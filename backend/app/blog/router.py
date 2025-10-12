from fastapi import APIRouter, Depends, HTTPException, Response, Query, Request
from fastapi.responses import Response, PlainTextResponse
from typing import List, Optional
import os
import logging
from datetime import datetime

from .models.blog_models import (
    BlogPostCreate,
    BlogPostUpdate,
    BlogPostList,
    BlogPostDetail,
    BlogPostResponse,
    BlogPostSearch,
    PostStatus,
    PostCategory
)
from .services.blog_service import BlogService, BlogServiceError
from .services.seo_service import SEOService
from .services.health_monitor import get_health_monitor
from .services.fallback_router import get_fallback_router
from ..auth.dependencies import require_admin
from ..models.user import User
from ..core.config import settings

logger = logging.getLogger(__name__)

# Initialize router
router = APIRouter()

# Initialize services with settings
try:
    blog_service = BlogService(
        content_dir=settings.BLOG_CONTENT_DIR,
        graceful_degradation=settings.BLOG_GRACEFUL_DEGRADATION
    )
    seo_service = SEOService()
    
    # Initialize enhanced monitoring and fallback systems
    health_monitor = get_health_monitor(blog_service)
    fallback_router = get_fallback_router(blog_service)
    
    logger.info("✅ Blog services initialized successfully with enhanced monitoring")
except Exception as e:
    logger.error(f"Failed to initialize blog services: {e}")
    # Create a placeholder service that will return empty responses
    blog_service = BlogService(
        content_dir="C:/tmp/empty_blog",
        graceful_degradation=True
    )
    seo_service = SEOService()  # Still initialize SEO service with defaults
    
    # Initialize fallback systems even with placeholder service
    health_monitor = get_health_monitor(blog_service)
    fallback_router = get_fallback_router(blog_service)


@router.get("/", response_model=BlogPostResponse)
async def get_blog_posts(
    status: Optional[PostStatus] = Query(PostStatus.PUBLISHED, description="Filter by post status"),
    category: Optional[PostCategory] = Query(None, description="Filter by category"),
    limit: int = Query(20, ge=1, le=100, description="Number of posts to return"),
    offset: int = Query(0, ge=0, description="Number of posts to skip"),
    sort_by: str = Query("published_at", pattern="^(published_at|created_at|title|views)$"),
    sort_order: str = Query("desc", pattern="^(asc|desc)$")
):
    """Get list of blog posts with filtering and pagination"""
    
    try:
        search_params = BlogPostSearch(
            query="",  # Empty query for listing
            category=category,
            status=status,
            limit=limit,
            offset=offset,
            sort_by=sort_by,
            sort_order=sort_order
        )
        
        return blog_service.search_posts(search_params)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch posts: {str(e)}")


@router.get("/search", response_model=BlogPostResponse)
async def search_blog_posts(
    q: str = Query(..., min_length=1, description="Search query"),
    category: Optional[PostCategory] = Query(None, description="Filter by category"),
    tags: Optional[List[str]] = Query(None, description="Filter by tags"),
    status: Optional[PostStatus] = Query(PostStatus.PUBLISHED, description="Filter by post status"),
    limit: int = Query(20, ge=1, le=100, description="Number of posts to return"),
    offset: int = Query(0, ge=0, description="Number of posts to skip"),
    sort_by: str = Query("published_at", pattern="^(published_at|created_at|title|views)$"),
    sort_order: str = Query("desc", pattern="^(asc|desc)$")
):
    """Search blog posts"""
    
    try:
        search_params = BlogPostSearch(
            query=q,
            category=category,
            tags=tags or [],
            status=status,
            limit=limit,
            offset=offset,
            sort_by=sort_by,
            sort_order=sort_order
        )
        
        return blog_service.search_posts(search_params)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")


@router.get("/categories/{category}", response_model=BlogPostResponse)
async def get_posts_by_category(
    category: PostCategory,
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0)
):
    """Get posts by category"""
    
    try:
        search_params = BlogPostSearch(
            query="",
            category=category,
            status=PostStatus.PUBLISHED,
            limit=limit,
            offset=offset
        )
        
        return blog_service.search_posts(search_params)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch posts by category: {str(e)}")


@router.get("/tags/{tag}", response_model=BlogPostResponse)
async def get_posts_by_tag(
    tag: str,
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0)
):
    """Get posts by tag"""
    
    try:
        search_params = BlogPostSearch(
            query="",
            tags=[tag],
            status=PostStatus.PUBLISHED,
            limit=limit,
            offset=offset
        )
        
        return blog_service.search_posts(search_params)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch posts by tag: {str(e)}")


# Utility endpoints (must be before /{slug} to avoid conflicts)
@router.get("/categories", response_model=List[str])
async def get_categories():
    """Get all available categories"""
    return [category.value for category in PostCategory]


@router.get("/popular", response_model=List[BlogPostList])
async def get_popular_posts(limit: int = Query(5, ge=1, le=10)):
    """Get popular blog posts"""
    
    try:
        all_posts = blog_service.get_all_posts(status=PostStatus.PUBLISHED)
        popular = blog_service.search_service.get_popular_posts(all_posts, limit)
        
        return popular
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch popular posts: {str(e)}")


@router.get("/trending", response_model=List[BlogPostList])
async def get_trending_posts(limit: int = Query(5, ge=1, le=10)):
    """Get trending blog posts"""
    
    try:
        all_posts = blog_service.get_all_posts(status=PostStatus.PUBLISHED)
        trending = blog_service.search_service.get_trending_posts(all_posts, limit)
        
        return trending
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch trending posts: {str(e)}")


# SEO endpoints (must be before /{slug} to avoid conflicts)
@router.get("/sitemap.xml")
async def get_sitemap():
    """Generate XML sitemap for blog posts"""
    
    try:
        posts = blog_service.get_all_posts(status=PostStatus.PUBLISHED)
        if seo_service:
            additional_urls = seo_service.get_default_sitemap_entries()
            sitemap_xml = seo_service.generate_sitemap(posts, additional_urls)
        else:
            # Fallback basic sitemap
            sitemap_xml = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n</urlset>'
        
        return Response(
            content=sitemap_xml,
            media_type="application/xml; charset=utf-8"
        )
        
    except Exception as e:
        logger.warning(f"Sitemap generation failed: {e}")
        # Return minimal sitemap instead of 500
        minimal_sitemap = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n</urlset>'
        return Response(
            content=minimal_sitemap,
            media_type="application/xml; charset=utf-8"
        )


@router.get("/rss.xml")
async def get_rss_feed():
    """Generate RSS feed for blog posts"""
    
    try:
        posts = blog_service.get_all_posts(status=PostStatus.PUBLISHED)
        
        if seo_service:
            rss_xml = seo_service.generate_rss_feed(posts)
        else:
            # Fallback basic RSS
            rss_xml = '<?xml version="1.0" encoding="UTF-8"?>\n<rss version="2.0">\n<channel>\n<title>AdCopySurge Blog</title>\n<description>Blog posts</description>\n</channel>\n</rss>'
        
        return Response(
            content=rss_xml,
            media_type="application/rss+xml; charset=utf-8",
            headers={
                "Cache-Control": "public, max-age=3600"  # Cache for 1 hour
            }
        )
        
    except Exception as e:
        logger.warning(f"RSS generation failed: {e}")
        # Return minimal RSS instead of 500
        minimal_rss = '<?xml version="1.0" encoding="UTF-8"?>\n<rss version="2.0">\n<channel>\n<title>AdCopySurge Blog</title>\n<description>Blog temporarily unavailable</description>\n</channel>\n</rss>'
        return Response(
            content=minimal_rss,
            media_type="application/rss+xml; charset=utf-8"
        )


@router.get("/robots.txt", response_class=PlainTextResponse)
async def get_robots_txt():
    """Generate robots.txt for blog"""
    
    try:
        if seo_service:
            robots_content = seo_service.generate_robots_txt()
        else:
            # Fallback basic robots.txt
            robots_content = "User-agent: *\nAllow: /"
        
        return PlainTextResponse(
            content=robots_content,
            headers={"Content-Type": "text/plain; charset=utf-8"}
        )
        
    except Exception as e:
        logger.warning(f"Robots.txt generation failed: {e}")
        # Return minimal robots.txt instead of 500
        return PlainTextResponse(
            content="User-agent: *\nAllow: /",
            headers={"Content-Type": "text/plain; charset=utf-8"}
        )


@router.get("/{slug}", response_model=BlogPostDetail)
async def get_blog_post(slug: str, request: Request = None):
    """Get a single blog post by slug with intelligent fallback"""
    
    try:
        if not blog_service.is_healthy:
            if blog_service.graceful_degradation:
                logger.warning(f"Blog service unhealthy, cannot retrieve post {slug}")
                # Use fallback system instead of immediate 404
                request_info = {
                    'user_agent': request.headers.get('user-agent', '') if request else '',
                    'referer': request.headers.get('referer', '') if request else '',
                    'debug': settings.DEBUG
                }
                return await fallback_router.handle_missing_slug(slug, request_info)
        
        post = blog_service.get_post_by_slug(slug)
        
        if not post:
            # Use intelligent fallback instead of immediate 404
            request_info = {
                'user_agent': request.headers.get('user-agent', '') if request else '',
                'referer': request.headers.get('referer', '') if request else '',
                'debug': settings.DEBUG
            }
            return await fallback_router.handle_missing_slug(slug, request_info)
        
        # Only allow published posts for non-admin users
        if post.status != PostStatus.PUBLISHED:
            request_info = {
                'user_agent': request.headers.get('user-agent', '') if request else '',
                'referer': request.headers.get('referer', '') if request else '',
                'debug': settings.DEBUG,
                'reason': 'unpublished_post'
            }
            return await fallback_router.handle_missing_slug(slug, request_info)
        
        return post
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching blog post {slug}: {e}")
        # Use intelligent fallback instead of immediate 404
        request_info = {
            'user_agent': request.headers.get('user-agent', '') if request else '',
            'referer': request.headers.get('referer', '') if request else '',
            'debug': settings.DEBUG,
            'error': str(e)
        }
        return await fallback_router.handle_missing_slug(slug, request_info)


# Admin-only endpoints
@router.post("/", response_model=dict)
async def create_blog_post(
    post_data: BlogPostCreate,
    current_user: User = Depends(require_admin)
):
    """Create a new blog post (Admin only)"""
    
    try:
        slug = blog_service.create_post(post_data)
        
        if not slug:
            raise HTTPException(status_code=400, detail="Failed to create post - slug may already exist")
        
        return {"slug": slug, "message": "Post created successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create post: {str(e)}")


@router.put("/{slug}", response_model=dict)
async def update_blog_post(
    slug: str,
    post_data: BlogPostUpdate,
    current_user: User = Depends(require_admin)
):
    """Update an existing blog post (Admin only)"""
    
    try:
        success = blog_service.update_post(slug, post_data)
        
        if not success:
            raise HTTPException(status_code=404, detail="Post not found")
        
        return {"message": "Post updated successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update post: {str(e)}")


@router.delete("/{slug}", response_model=dict)
async def delete_blog_post(
    slug: str,
    current_user: User = Depends(require_admin)
):
    """Delete a blog post (Admin only)"""
    
    try:
        success = blog_service.delete_post(slug)
        
        if not success:
            raise HTTPException(status_code=404, detail="Post not found")
        
        return {"message": "Post deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete post: {str(e)}")


@router.get("/admin/all", response_model=BlogPostResponse)
async def get_all_posts_admin(
    status: Optional[PostStatus] = Query(None, description="Filter by post status"),
    category: Optional[PostCategory] = Query(None, description="Filter by category"),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(require_admin)
):
    """Get all posts including drafts (Admin only)"""
    
    try:
        search_params = BlogPostSearch(
            query="",
            category=category,
            status=status,  # Allow all statuses for admin
            limit=limit,
            offset=offset
        )
        
        return blog_service.search_posts(search_params)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch posts: {str(e)}")


# SEO endpoints moved above to avoid route conflicts


# Analytics and engagement endpoints
@router.post("/{slug}/view")
async def track_post_view(slug: str):
    """Track a post view (for analytics)"""
    
    # TODO: Implement view tracking
    # This would typically update the post's view count
    # and send analytics events
    
    return {"message": "View tracked"}


@router.post("/{slug}/share")
async def track_post_share(
    slug: str,
    platform: str = Query(..., description="Social platform (twitter, linkedin, facebook, etc.)")
):
    """Track a post share (for analytics)"""
    
    # TODO: Implement share tracking
    # This would typically update the post's share count
    # and send analytics events
    
    return {"message": "Share tracked"}


# Health and diagnostic endpoints
@router.get("/health", response_model=dict)
async def blog_health_check():
    """Get detailed blog service health report"""
    try:
        health_report = health_monitor.get_health_report()
        fallback_analytics = fallback_router.get_analytics_report()
        
        return {
            "status": "healthy" if health_report.get('service_status', {}).get('is_healthy') else "degraded",
            "timestamp": datetime.now().isoformat(),
            "service_health": health_report,
            "fallback_analytics": fallback_analytics,
            "blog_service_healthy": blog_service.is_healthy if hasattr(blog_service, 'is_healthy') else False,
            "version": "2.0.0-enhanced"
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }


@router.post("/admin/recovery", response_model=dict)
async def trigger_blog_recovery(current_user: User = Depends(require_admin)):
    """Manually trigger blog service recovery (Admin only)"""
    try:
        success = await health_monitor.force_recovery()
        return {
            "recovery_triggered": True,
            "success": success,
            "message": "Recovery successful" if success else "Recovery failed - check logs",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {
            "recovery_triggered": False,
            "success": False,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }


@router.post("/admin/redirect/{old_slug}/{new_slug}", response_model=dict)
async def add_slug_redirect(
    old_slug: str,
    new_slug: str,
    current_user: User = Depends(require_admin)
):
    """Add a manual slug redirect (Admin only)"""
    try:
        fallback_router.add_redirect(old_slug, new_slug)
        return {
            "redirect_added": True,
            "old_slug": old_slug,
            "new_slug": new_slug,
            "message": f"Redirect added: {old_slug} -> {new_slug}"
        }
    except Exception as e:
        return {
            "redirect_added": False,
            "error": str(e)
        }


@router.get("/admin/analytics", response_model=dict)
async def get_blog_analytics(current_user: User = Depends(require_admin)):
    """Get comprehensive blog analytics (Admin only)"""
    try:
        return fallback_router.get_analytics_report()
    except Exception as e:
        return {"error": str(e)}


# Utility endpoints have been moved above /{slug} to avoid conflicts
