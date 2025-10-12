import os
import re
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional, Dict, Any

try:
    import frontmatter
except ImportError:
    frontmatter = None

try:
    from slugify import slugify
except ImportError:
    def slugify(text: str) -> str:
        """Fallback slugify function"""
        return re.sub(r'[^a-zA-Z0-9-]', '-', text.lower()).strip('-')

from ..models.blog_models import (
    BlogPost,
    BlogPostCreate,
    BlogPostUpdate,
    BlogPostList,
    BlogPostDetail,
    BlogPostResponse,
    BlogPostSearch,
    PostStatus,
    PostCategory,
    Author,
    SEOData,
    ContentStats,
    BlogMetadata
)

try:
    from .markdown_processor import MarkdownProcessor
except ImportError:
    MarkdownProcessor = None

try:
    from .search_service import SearchService
except ImportError:
    SearchService = None

logger = logging.getLogger(__name__)


class BlogServiceError(Exception):
    """Blog service specific exception"""
    pass


class BlogService:
    def __init__(self, content_dir: str = "content/blog", graceful_degradation: bool = True):
        self.graceful_degradation = graceful_degradation
        self.is_healthy = True
        self.error_message = None
        
        try:
            # Initialize content directory
            self.content_dir = Path(content_dir)
            try:
                self.content_dir.mkdir(parents=True, exist_ok=True)
                logger.info(f"Blog content directory initialized: {self.content_dir}")
            except PermissionError as e:
                raise BlogServiceError(f"Permission denied creating content directory {self.content_dir}: {e}")
            except OSError as e:
                raise BlogServiceError(f"OS error creating content directory {self.content_dir}: {e}")
            
            # Initialize markdown processor
            if MarkdownProcessor is None:
                raise BlogServiceError("MarkdownProcessor not available - missing markdown dependencies")
            
            try:
                self.markdown_processor = MarkdownProcessor()
                logger.info("Markdown processor initialized successfully")
            except Exception as e:
                raise BlogServiceError(f"Failed to initialize MarkdownProcessor: {e}")
            
            # Initialize search service
            if SearchService is None:
                raise BlogServiceError("SearchService not available")
            
            try:
                self.search_service = SearchService()
                logger.info("Search service initialized successfully")
            except Exception as e:
                raise BlogServiceError(f"Failed to initialize SearchService: {e}")
            
            # Check for frontmatter dependency
            if frontmatter is None:
                raise BlogServiceError("python-frontmatter package not available")
            
            logger.info("BlogService initialized successfully")
            
        except BlogServiceError as e:
            self.is_healthy = False
            self.error_message = str(e)
            
            if self.graceful_degradation:
                logger.warning(f"BlogService initialization failed, running in degraded mode: {e}")
                # Set fallback services
                self.content_dir = Path(content_dir)  # Still set the path
                self.markdown_processor = None
                self.search_service = None
            else:
                logger.error(f"BlogService initialization failed: {e}")
                raise
        
    def _get_post_path(self, slug: str) -> Path:
        """Get the file path for a blog post by slug"""
        # Look for existing file with this slug
        for file_path in self.content_dir.glob("*.md"):
            if file_path.stem.endswith(f"-{slug}"):
                return file_path
        
        # If not found, create new filename with current date
        date_str = datetime.now().strftime("%Y-%m-%d")
        return self.content_dir / f"{date_str}-{slug}.md"
    
    def _parse_markdown_file(self, file_path: Path) -> Optional[BlogPost]:
        """Parse a markdown file and return BlogPost object"""
        if not file_path.exists():
            return None
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                post = frontmatter.load(f)
            
            # Extract metadata from frontmatter
            metadata = post.metadata
            content = post.content
            
            # Get file stats
            file_stats = file_path.stat()
            created_at = datetime.fromtimestamp(file_stats.st_ctime, tz=timezone.utc)
            updated_at = datetime.fromtimestamp(file_stats.st_mtime, tz=timezone.utc)
            
            # Parse filename for ID (remove date prefix and .md extension)
            file_id = re.sub(r'^\d{4}-\d{2}-\d{2}-', '', file_path.stem)
            
            # Calculate content stats
            content_stats = self._calculate_content_stats(content, metadata)
            
            # Parse published date
            published_at = None
            if metadata.get('status') == 'published' and metadata.get('published_at'):
                published_at = datetime.fromisoformat(metadata['published_at'])
            elif metadata.get('status') == 'published':
                published_at = created_at
            
            # Build blog post object
            blog_post = BlogPost(
                id=file_id,
                title=metadata.get('title', ''),
                slug=metadata.get('slug', file_id),
                excerpt=metadata.get('excerpt', ''),
                content=content,
                status=PostStatus(metadata.get('status', 'draft')),
                category=PostCategory(metadata.get('category', 'educational')),
                tags=metadata.get('tags', []),
                featured_image=metadata.get('featured_image'),
                hero_image=metadata.get('hero_image'),
                author=Author(**metadata.get('author', {'name': 'AdCopySurge Team'})),
                seo=SEOData(**metadata.get('seo', {
                    'title': metadata.get('title', '')[:60],
                    'meta_description': metadata.get('excerpt', '')[:160],
                    'primary_keyword': metadata.get('primary_keyword', '')
                })),
                scheduled_at=datetime.fromisoformat(metadata['scheduled_at']) if metadata.get('scheduled_at') else None,
                created_at=created_at,
                updated_at=updated_at,
                published_at=published_at,
                content_stats=content_stats,
                metadata=BlogMetadata(**metadata.get('blog_metadata', {}))
            )
            
            return blog_post
            
        except Exception as e:
            print(f"Error parsing {file_path}: {e}")
            return None
    
    def _calculate_content_stats(self, content: str, metadata: Dict) -> ContentStats:
        """Calculate content statistics"""
        words = len(content.split())
        read_time = max(1, words // 200)  # Average reading speed
        
        # Count headings
        heading_count = len(re.findall(r'^#{1,6}\s', content, re.MULTILINE))
        
        # Count images
        image_count = len(re.findall(r'!\[.*?\]\(.*?\)', content))
        
        # Extract links
        links = re.findall(r'\[.*?\]\((.*?)\)', content)
        internal_links = [link for link in links if not link.startswith(('http', 'mailto:', 'tel:'))]
        external_links = [link for link in links if link.startswith('http')]
        
        return ContentStats(
            word_count=words,
            read_time=read_time,
            heading_count=heading_count,
            image_count=image_count,
            link_count=len(links),
            internal_links=internal_links,
            external_links=external_links
        )
    
    def _save_markdown_file(self, blog_post: BlogPostCreate, file_path: Path) -> bool:
        """Save blog post to markdown file"""
        try:
            # Prepare frontmatter data
            frontmatter_data = {
                'title': blog_post.title,
                'slug': blog_post.slug,
                'excerpt': blog_post.excerpt,
                'status': blog_post.status.value,
                'category': blog_post.category.value,
                'tags': blog_post.tags,
                'featured_image': str(blog_post.featured_image) if blog_post.featured_image else None,
                'hero_image': str(blog_post.hero_image) if blog_post.hero_image else None,
                'author': blog_post.author.dict(),
                'seo': blog_post.seo.dict(),
                'scheduled_at': blog_post.scheduled_at.isoformat() if blog_post.scheduled_at else None,
                'created_at': datetime.now(timezone.utc).isoformat(),
                'updated_at': datetime.now(timezone.utc).isoformat()
            }
            
            if blog_post.status == PostStatus.PUBLISHED:
                frontmatter_data['published_at'] = datetime.now(timezone.utc).isoformat()
            
            # Create frontmatter post
            post = frontmatter.Post(blog_post.content, **frontmatter_data)
            
            # Write to file
            with open(file_path, 'w', encoding='utf-8') as f:
                frontmatter.dump(post, f)
            
            return True
            
        except Exception as e:
            print(f"Error saving {file_path}: {e}")
            return False
    
    def get_all_posts(self, status: Optional[PostStatus] = None, category: Optional[PostCategory] = None) -> List[BlogPostList]:
        """Get all blog posts with optional filtering"""
        if not self.is_healthy and self.graceful_degradation:
            logger.warning("BlogService unhealthy, returning empty posts list")
            return self._get_empty_posts_list()
        
        if not self.is_healthy:
            raise BlogServiceError(f"BlogService is unhealthy: {self.error_message}")
        
        posts = []
        
        for file_path in self.content_dir.glob("*.md"):
            blog_post = self._parse_markdown_file(file_path)
            if blog_post:
                # Apply filters
                if status and blog_post.status != status:
                    continue
                if category and blog_post.category != category:
                    continue
                
                # Convert to list format
                post_list = BlogPostList(
                    id=blog_post.id,
                    title=blog_post.title,
                    slug=blog_post.slug,
                    excerpt=blog_post.excerpt,
                    status=blog_post.status,
                    category=blog_post.category,
                    tags=blog_post.tags,
                    featured_image=blog_post.featured_image,
                    author=blog_post.author,
                    created_at=blog_post.created_at,
                    updated_at=blog_post.updated_at,
                    published_at=blog_post.published_at,
                    content_stats=blog_post.content_stats,
                    metadata=blog_post.metadata
                )
                posts.append(post_list)
        
        # Sort by published date (newest first)
        posts.sort(key=lambda x: x.published_at or x.created_at, reverse=True)
        return posts
    
    def get_post_by_slug(self, slug: str) -> Optional[BlogPostDetail]:
        """Get a single blog post by slug with full details"""
        if not self.is_healthy:
            if self.graceful_degradation:
                logger.warning(f"BlogService unhealthy, cannot retrieve post {slug}")
                return None
            else:
                raise BlogServiceError(f"BlogService is unhealthy: {self.error_message}")
        
        file_path = self._get_post_path(slug)
        blog_post = self._parse_markdown_file(file_path)
        
        if not blog_post:
            return None
        
        # Process markdown content to HTML
        content_html, toc = self.markdown_processor.process(blog_post.content)
        
        # Get related posts
        related_posts = self._get_related_posts(blog_post, limit=3)
        
        # Build breadcrumbs
        breadcrumbs = [
            {"name": "Home", "url": "/"},
            {"name": "Blog", "url": "/blog"},
            {"name": blog_post.category.value.replace('_', ' ').title(), "url": f"/blog/category/{blog_post.category.value}"},
            {"name": blog_post.title, "url": f"/blog/{blog_post.slug}"}
        ]
        
        return BlogPostDetail(
            **blog_post.dict(),
            related_posts=related_posts,
            table_of_contents=toc,
            content_html=content_html,
            breadcrumbs=breadcrumbs,
            cta_variations=self._get_cta_variations(),
            lead_magnets=self._get_lead_magnets(blog_post.category),
            social_snippets=self._get_social_snippets(blog_post)
        )
    
    def create_post(self, blog_post: BlogPostCreate) -> Optional[str]:
        """Create a new blog post"""
        # Generate slug if not provided
        if not blog_post.slug:
            blog_post.slug = slugify(blog_post.title)
        
        file_path = self._get_post_path(blog_post.slug)
        
        # Check if file already exists
        if file_path.exists():
            return None
        
        if self._save_markdown_file(blog_post, file_path):
            return blog_post.slug
        return None
    
    def update_post(self, slug: str, blog_post: BlogPostUpdate) -> bool:
        """Update an existing blog post"""
        file_path = self._get_post_path(slug)
        existing_post = self._parse_markdown_file(file_path)
        
        if not existing_post:
            return False
        
        # Update only provided fields
        update_data = blog_post.dict(exclude_unset=True)
        
        # Create updated post
        updated_post = BlogPostCreate(
            **{**existing_post.dict(exclude={'id', 'created_at', 'updated_at', 'published_at', 'content_stats', 'metadata'}), 
               **update_data}
        )
        
        # Handle slug change (rename file)
        if blog_post.slug and blog_post.slug != existing_post.slug:
            new_file_path = self._get_post_path(blog_post.slug)
            file_path.unlink()  # Delete old file
            file_path = new_file_path
        
        return self._save_markdown_file(updated_post, file_path)
    
    def delete_post(self, slug: str) -> bool:
        """Delete a blog post"""
        file_path = self._get_post_path(slug)
        
        if file_path.exists():
            file_path.unlink()
            return True
        return False
    
    def search_posts(self, search_params: BlogPostSearch) -> BlogPostResponse:
        """Search blog posts"""
        if not self.is_healthy and self.graceful_degradation:
            logger.warning("BlogService unhealthy, returning empty search results")
            return self._get_empty_response()
        
        if not self.is_healthy:
            raise BlogServiceError(f"BlogService is unhealthy: {self.error_message}")
        
        if self.search_service is None:
            logger.warning("SearchService not available, returning empty results")
            return self._get_empty_response()
            
        return self.search_service.search(search_params, self.get_all_posts())
    
    def _get_related_posts(self, current_post: BlogPost, limit: int = 3) -> List[BlogPostList]:
        """Get related posts based on tags and category"""
        all_posts = self.get_all_posts(status=PostStatus.PUBLISHED)
        related = []
        
        for post in all_posts:
            if post.slug == current_post.slug:
                continue
            
            score = 0
            # Same category gets higher score
            if post.category == current_post.category:
                score += 3
            
            # Shared tags
            shared_tags = set(post.tags) & set(current_post.tags)
            score += len(shared_tags)
            
            if score > 0:
                related.append((post, score))
        
        # Sort by score and return top posts
        related.sort(key=lambda x: x[1], reverse=True)
        return [post for post, _ in related[:limit]]
    
    def _get_cta_variations(self) -> List[Dict[str, str]]:
        """Get CTA variations for A/B testing"""
        return [
            {"text": "Start Your Free Trial", "url": "/register", "type": "primary"},
            {"text": "Try AdCopySurge Free", "url": "/register", "type": "secondary"},
            {"text": "Get Started Today", "url": "/register", "type": "tertiary"},
            {"text": "Optimize Your Ads Now", "url": "/analyze", "type": "primary"},
            {"text": "See How It Works", "url": "/demo", "type": "secondary"}
        ]
    
    def _get_lead_magnets(self, category: PostCategory) -> List[Dict[str, str]]:
        """Get relevant lead magnets based on category"""
        base_magnets = [
            {"title": "Free Ad Copy Analysis Checklist", "url": "/resources/checklist", "type": "pdf"},
            {"title": "25 High-Converting Ad Copy Templates", "url": "/resources/templates", "type": "swipe_file"}
        ]
        
        if category == PostCategory.EDUCATIONAL:
            base_magnets.extend([
                {"title": "Ad Copy Psychology Guide", "url": "/resources/psychology-guide", "type": "guide"},
                {"title": "Facebook Ads Compliance Checklist", "url": "/resources/compliance", "type": "checklist"}
            ])
        elif category == PostCategory.CASE_STUDY:
            base_magnets.extend([
                {"title": "Case Study Template Pack", "url": "/resources/case-study-templates", "type": "templates"},
                {"title": "ROI Calculator Spreadsheet", "url": "/resources/roi-calculator", "type": "tool"}
            ])
        
        return base_magnets
    
    def _get_social_snippets(self, post: BlogPost) -> Dict[str, str]:
        """Generate social media snippets for sharing"""
        return {
            "linkedin": f"📈 {post.title}\n\n{post.excerpt}\n\nRead more: [LINK]\n\n#AdCopy #Marketing #DigitalAdvertising",
            "twitter": f"🔥 {post.title}\n\n{post.excerpt[:100]}...\n\n[LINK]\n\n#AdCopy #MarketingTips",
            "tiktok_script": f"Hook: Did you know {post.seo.primary_keyword} can increase your CTR by 300%?\n\nBody: {post.excerpt[:150]}\n\nCTA: Link in bio for the full guide!"
        }
    
    def _get_empty_response(self) -> BlogPostResponse:
        """Return empty blog response for degraded mode"""
        return BlogPostResponse(
            posts=[],
            total=0,
            limit=20,
            offset=0,
            has_more=False
        )
    
    def _get_empty_posts_list(self) -> List[BlogPostList]:
        """Return empty posts list for degraded mode"""
        return []
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get health status of the blog service"""
        return {
            "healthy": self.is_healthy,
            "error_message": self.error_message,
            "graceful_degradation": self.graceful_degradation,
            "content_dir_exists": self.content_dir.exists() if hasattr(self, 'content_dir') else False,
            "dependencies": {
                "frontmatter": frontmatter is not None,
                "markdown_processor": MarkdownProcessor is not None,
                "search_service": SearchService is not None
            }
        }
