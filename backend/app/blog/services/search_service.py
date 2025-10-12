import re
from typing import List, Dict, Any
from datetime import datetime, timezone

from ..models.blog_models import (
    BlogPostList,
    BlogPostSearch,
    BlogPostResponse,
    PostStatus,
    PostCategory
)


class SearchService:
    def __init__(self):
        """Initialize search service"""
        pass
    
    def search(self, search_params: BlogPostSearch, all_posts: List[BlogPostList]) -> BlogPostResponse:
        """
        Search and filter blog posts
        
        Args:
            search_params: Search parameters
            all_posts: List of all available posts
            
        Returns:
            BlogPostResponse with filtered and paginated results
        """
        filtered_posts = self._filter_posts(all_posts, search_params)
        sorted_posts = self._sort_posts(filtered_posts, search_params)
        total = len(sorted_posts)
        
        # Apply pagination
        start_idx = search_params.offset
        end_idx = start_idx + search_params.limit
        paginated_posts = sorted_posts[start_idx:end_idx]
        
        return BlogPostResponse(
            posts=paginated_posts,
            total=total,
            limit=search_params.limit,
            offset=search_params.offset,
            has_more=end_idx < total
        )
    
    def _filter_posts(self, posts: List[BlogPostList], search_params: BlogPostSearch) -> List[BlogPostList]:
        """Filter posts based on search criteria"""
        filtered = []
        
        for post in posts:
            # Status filter
            if search_params.status and post.status != search_params.status:
                continue
            
            # Category filter
            if search_params.category and post.category != search_params.category:
                continue
            
            # Tags filter
            if search_params.tags:
                if not any(tag.lower() in [t.lower() for t in post.tags] for tag in search_params.tags):
                    continue
            
            # Text search
            if search_params.query:
                if not self._matches_query(post, search_params.query):
                    continue
            
            filtered.append(post)
        
        return filtered
    
    def _matches_query(self, post: BlogPostList, query: str) -> bool:
        """Check if post matches search query"""
        query_lower = query.lower()
        
        # Search in title (highest priority)
        if query_lower in post.title.lower():
            return True
        
        # Search in excerpt
        if query_lower in post.excerpt.lower():
            return True
        
        # Search in tags
        for tag in post.tags:
            if query_lower in tag.lower():
                return True
        
        # Search in author name
        if query_lower in post.author.name.lower():
            return True
        
        return False
    
    def _sort_posts(self, posts: List[BlogPostList], search_params: BlogPostSearch) -> List[BlogPostList]:
        """Sort posts based on search parameters"""
        reverse_order = search_params.sort_order == "desc"
        
        if search_params.sort_by == "published_at":
            return sorted(
                posts, 
                key=lambda p: p.published_at or p.created_at, 
                reverse=reverse_order
            )
        elif search_params.sort_by == "created_at":
            return sorted(
                posts, 
                key=lambda p: p.created_at, 
                reverse=reverse_order
            )
        elif search_params.sort_by == "title":
            return sorted(
                posts, 
                key=lambda p: p.title.lower(), 
                reverse=reverse_order
            )
        elif search_params.sort_by == "views":
            return sorted(
                posts, 
                key=lambda p: p.metadata.views, 
                reverse=reverse_order
            )
        else:
            # Default to published_at desc
            return sorted(
                posts, 
                key=lambda p: p.published_at or p.created_at, 
                reverse=True
            )
    
    def get_popular_posts(self, posts: List[BlogPostList], limit: int = 5) -> List[BlogPostList]:
        """Get most popular posts based on engagement metrics"""
        # Calculate engagement score
        scored_posts = []
        for post in posts:
            if post.status != PostStatus.PUBLISHED:
                continue
            
            score = (
                post.metadata.views * 1.0 +
                post.metadata.shares * 3.0 +
                post.metadata.likes * 2.0 +
                post.metadata.comments_count * 5.0
            )
            
            # Boost recent posts slightly
            post_date = post.published_at or post.created_at
            if post_date.tzinfo is None:
                post_date = post_date.replace(tzinfo=timezone.utc)
            days_since_publish = (datetime.now(timezone.utc) - post_date).days
            if days_since_publish <= 7:
                score *= 1.2
            elif days_since_publish <= 30:
                score *= 1.1
            
            scored_posts.append((post, score))
        
        # Sort by score and return top posts
        scored_posts.sort(key=lambda x: x[1], reverse=True)
        return [post for post, _ in scored_posts[:limit]]
    
    def get_trending_posts(self, posts: List[BlogPostList], limit: int = 5) -> List[BlogPostList]:
        """Get trending posts based on recent engagement"""
        trending = []
        
        for post in posts:
            if post.status != PostStatus.PUBLISHED:
                continue
            
            # Only consider posts from the last 30 days
            post_date = post.published_at or post.created_at
            if post_date.tzinfo is None:
                post_date = post_date.replace(tzinfo=timezone.utc)
            days_since_publish = (datetime.now(timezone.utc) - post_date).days
            if days_since_publish > 30:
                continue
            
            # Calculate trending score (higher for recent posts with good engagement)
            daily_views = post.metadata.views / max(1, days_since_publish)
            trending_score = daily_views + (post.metadata.shares * 2) + (post.metadata.likes * 1.5)
            
            trending.append((post, trending_score))
        
        # Sort by trending score
        trending.sort(key=lambda x: x[1], reverse=True)
        return [post for post, _ in trending[:limit]]
    
    def get_related_by_category(self, category: PostCategory, posts: List[BlogPostList], exclude_slug: str = None, limit: int = 4) -> List[BlogPostList]:
        """Get posts from the same category"""
        related = []
        
        for post in posts:
            if post.status != PostStatus.PUBLISHED:
                continue
            if post.category != category:
                continue
            if exclude_slug and post.slug == exclude_slug:
                continue
            
            related.append(post)
        
        # Sort by published date and return limited results
        related.sort(key=lambda p: p.published_at or p.created_at, reverse=True)
        return related[:limit]
    
    def get_related_by_tags(self, tags: List[str], posts: List[BlogPostList], exclude_slug: str = None, limit: int = 4) -> List[BlogPostList]:
        """Get posts with similar tags"""
        if not tags:
            return []
        
        scored_posts = []
        tag_set = set(tag.lower() for tag in tags)
        
        for post in posts:
            if post.status != PostStatus.PUBLISHED:
                continue
            if exclude_slug and post.slug == exclude_slug:
                continue
            
            post_tags = set(tag.lower() for tag in post.tags)
            shared_tags = tag_set & post_tags
            
            if shared_tags:
                score = len(shared_tags)
                scored_posts.append((post, score))
        
        # Sort by relevance score
        scored_posts.sort(key=lambda x: x[1], reverse=True)
        return [post for post, _ in scored_posts[:limit]]
    
    def suggest_search_terms(self, posts: List[BlogPostList]) -> Dict[str, List[str]]:
        """Generate search suggestions based on available content"""
        suggestions = {
            'categories': [],
            'tags': [],
            'popular_terms': []
        }
        
        # Get all categories
        categories = set()
        all_tags = set()
        title_words = []
        
        for post in posts:
            if post.status == PostStatus.PUBLISHED:
                categories.add(post.category.value.replace('_', ' ').title())
                all_tags.update(post.tags)
                
                # Extract words from title for popular terms
                title_words.extend([word.lower() for word in re.findall(r'\b\w+\b', post.title) if len(word) > 3])
        
        suggestions['categories'] = list(categories)
        suggestions['tags'] = list(all_tags)
        
        # Get most common title words as popular terms
        from collections import Counter
        word_counts = Counter(title_words)
        suggestions['popular_terms'] = [word for word, _ in word_counts.most_common(10)]
        
        return suggestions
