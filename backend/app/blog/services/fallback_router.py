"""
Smart Fallback Router - The 404 Eliminator
Creative emergency response system for blog routing failures
"""
import logging
import re
import json
from typing import Dict, List, Optional, Any, Union
from pathlib import Path
from datetime import datetime, timedelta
from difflib import SequenceMatcher
from urllib.parse import unquote

from fastapi import HTTPException
from fastapi.responses import JSONResponse, RedirectResponse

logger = logging.getLogger(__name__)


class SmartFallbackRouter:
    """Intelligent fallback system for handling blog routing failures"""
    
    def __init__(self, blog_service=None):
        self.blog_service = blog_service
        self.redirect_cache = {}  # slug -> redirect_url
        self.search_cache = {}    # query -> results (with TTL)
        self.popularity_cache = {} # slug -> view_count
        
        # Load any existing redirect mappings
        self._load_redirect_mappings()
        
        # Track 404 patterns for analysis
        self.missing_slug_patterns = {}
        self.last_cache_clear = datetime.now()
    
    def _load_redirect_mappings(self):
        """Load known slug redirects from file"""
        try:
            redirect_file = Path("app/blog/data/slug_redirects.json")
            if redirect_file.exists():
                with open(redirect_file, 'r') as f:
                    self.redirect_cache = json.load(f)
                logger.info(f"Loaded {len(self.redirect_cache)} redirect mappings")
        except Exception as e:
            logger.warning(f"Could not load redirect mappings: {e}")
    
    def _save_redirect_mappings(self):
        """Save redirect mappings to file"""
        try:
            redirect_file = Path("app/blog/data/slug_redirects.json")
            redirect_file.parent.mkdir(exist_ok=True)
            
            with open(redirect_file, 'w') as f:
                json.dump(self.redirect_cache, f, indent=2)
            logger.info(f"Saved {len(self.redirect_cache)} redirect mappings")
        except Exception as e:
            logger.error(f"Could not save redirect mappings: {e}")
    
    async def handle_missing_slug(self, requested_slug: str, request_info: Dict = None) -> Union[JSONResponse, RedirectResponse]:
        """
        Creative 404 handler that tries multiple recovery strategies
        Returns appropriate response or raises HTTPException
        """
        request_info = request_info or {}
        
        logger.info(f"🔍 Handling missing slug: '{requested_slug}'")
        
        # Track this miss for pattern analysis
        self._track_missing_slug(requested_slug, request_info)
        
        # Strategy 1: Check redirect cache first
        if requested_slug in self.redirect_cache:
            redirect_url = self.redirect_cache[requested_slug]
            logger.info(f"📍 Found cached redirect: {requested_slug} -> {redirect_url}")
            return RedirectResponse(url=redirect_url, status_code=301)
        
        # Strategy 2: Intelligent slug matching and suggestions
        suggestions = await self._find_similar_slugs(requested_slug)
        
        if suggestions:
            best_match = suggestions[0]
            confidence = best_match.get('confidence', 0)
            
            # Auto-redirect for high confidence matches
            if confidence > 0.8:
                redirect_url = f"/blog/{best_match['slug']}"
                logger.info(f"🎯 High confidence redirect: {requested_slug} -> {redirect_url} (confidence: {confidence})")
                
                # Cache this redirect for future
                self.redirect_cache[requested_slug] = redirect_url
                self._save_redirect_mappings()
                
                return RedirectResponse(url=redirect_url, status_code=301)
        
        # Strategy 3: Return intelligent 404 with suggestions
        return await self._create_smart_404_response(requested_slug, suggestions, request_info)
    
    async def _find_similar_slugs(self, requested_slug: str) -> List[Dict[str, Any]]:
        """Find similar slugs using multiple matching algorithms"""
        if not self.blog_service:
            return []
        
        try:
            # Get all available posts
            all_posts = self.blog_service.get_all_posts(status=None)
            suggestions = []
            
            # Clean the requested slug
            clean_requested = self._clean_slug(requested_slug)
            
            for post in all_posts:
                post_slug = post.slug
                clean_post_slug = self._clean_slug(post_slug)
                
                # Multiple similarity algorithms
                similarities = {
                    'exact': self._exact_similarity(clean_requested, clean_post_slug),
                    'sequence': self._sequence_similarity(clean_requested, clean_post_slug),
                    'fuzzy': self._fuzzy_similarity(clean_requested, clean_post_slug),
                    'keyword': self._keyword_similarity(clean_requested, clean_post_slug),
                    'date_pattern': self._date_pattern_similarity(requested_slug, post_slug)
                }
                
                # Weighted confidence score
                confidence = (
                    similarities['exact'] * 0.4 +
                    similarities['sequence'] * 0.25 +
                    similarities['fuzzy'] * 0.15 +
                    similarities['keyword'] * 0.15 +
                    similarities['date_pattern'] * 0.05
                )
                
                if confidence > 0.3:  # Minimum threshold
                    suggestions.append({
                        'slug': post_slug,
                        'title': post.title,
                        'confidence': confidence,
                        'category': post.category.value if post.category else 'uncategorized',
                        'similarities': similarities
                    })
            
            # Sort by confidence and return top matches
            suggestions.sort(key=lambda x: x['confidence'], reverse=True)
            return suggestions[:5]  # Top 5 matches
            
        except Exception as e:
            logger.error(f"Error finding similar slugs: {e}")
            return []
    
    def _clean_slug(self, slug: str) -> str:
        """Clean and normalize slug for comparison"""
        if not slug:
            return ""
        
        # Remove URL encoding, dates, special chars
        clean = unquote(slug.lower())
        clean = re.sub(r'^\d{4}-\d{2}-\d{2}-', '', clean)  # Remove date prefix
        clean = re.sub(r'[^a-z0-9-]', '-', clean)          # Replace non-alphanumeric with dash
        clean = re.sub(r'-+', '-', clean)                   # Collapse multiple dashes
        clean = clean.strip('-')                            # Remove leading/trailing dashes
        return clean
    
    def _exact_similarity(self, slug1: str, slug2: str) -> float:
        """Exact match similarity"""
        return 1.0 if slug1 == slug2 else 0.0
    
    def _sequence_similarity(self, slug1: str, slug2: str) -> float:
        """Sequence-based similarity using SequenceMatcher"""
        return SequenceMatcher(None, slug1, slug2).ratio()
    
    def _fuzzy_similarity(self, slug1: str, slug2: str) -> float:
        """Fuzzy matching for common variations"""
        # Check if one is contained in the other
        if slug1 in slug2 or slug2 in slug1:
            shorter = min(len(slug1), len(slug2))
            longer = max(len(slug1), len(slug2))
            return shorter / longer if longer > 0 else 0
        
        # Check for common word overlaps
        words1 = set(slug1.split('-'))
        words2 = set(slug2.split('-'))
        
        if words1 and words2:
            intersection = words1.intersection(words2)
            union = words1.union(words2)
            return len(intersection) / len(union) if union else 0
        
        return 0.0
    
    def _keyword_similarity(self, slug1: str, slug2: str) -> float:
        """Keyword-based similarity"""
        # Extract meaningful words (length > 2)
        words1 = [w for w in slug1.split('-') if len(w) > 2]
        words2 = [w for w in slug2.split('-') if len(w) > 2]
        
        if not words1 or not words2:
            return 0.0
        
        matches = 0
        for word1 in words1:
            for word2 in words2:
                if word1 in word2 or word2 in word1:
                    matches += 1
                    break
        
        return matches / max(len(words1), len(words2))
    
    def _date_pattern_similarity(self, slug1: str, slug2: str) -> float:
        """Check if slugs follow similar date patterns"""
        date_pattern = r'\\d{4}-\\d{2}-\\d{2}'
        has_date1 = bool(re.match(date_pattern, slug1))
        has_date2 = bool(re.match(date_pattern, slug2))
        
        if has_date1 and has_date2:
            return 0.2  # Small bonus for both having dates
        elif has_date1 or has_date2:
            return 0.1  # Smaller bonus for one having date
        
        return 0.0
    
    async def _create_smart_404_response(self, requested_slug: str, suggestions: List[Dict], request_info: Dict) -> JSONResponse:
        """Create intelligent 404 response with suggestions"""
        
        # Get popular/recent posts as fallback
        popular_posts = await self._get_popular_posts()
        recent_posts = await self._get_recent_posts()
        
        response_data = {
            "error": "Blog post not found",
            "requested_slug": requested_slug,
            "message": f"The blog post '{requested_slug}' could not be found.",
            "suggestions": {
                "similar_posts": suggestions,
                "popular_posts": popular_posts[:3],
                "recent_posts": recent_posts[:3]
            },
            "search_suggestion": f"Try searching for: {self._generate_search_query(requested_slug)}",
            "help_links": {
                "blog_home": "/blog",
                "all_categories": "/blog/categories",
                "search": f"/blog/search?q={self._generate_search_query(requested_slug)}"
            },
            "debug_info": {
                "timestamp": datetime.now().isoformat(),
                "user_agent": request_info.get("user_agent"),
                "referer": request_info.get("referer"),
                "patterns_found": len(suggestions)
            } if request_info.get("debug") else None
        }
        
        return JSONResponse(
            status_code=404,
            content=response_data,
            headers={
                "X-Content-Type": "blog-404-enhanced",
                "Cache-Control": "no-cache"
            }
        )
    
    def _generate_search_query(self, slug: str) -> str:
        """Generate helpful search query from slug"""
        clean_slug = self._clean_slug(slug)
        words = [w for w in clean_slug.split('-') if len(w) > 2]
        return ' '.join(words[:3])  # Use top 3 meaningful words
    
    async def _get_popular_posts(self) -> List[Dict[str, str]]:
        """Get popular posts for suggestions"""
        try:
            if self.blog_service and hasattr(self.blog_service, 'search_service'):
                all_posts = self.blog_service.get_all_posts(status='published')
                popular = self.blog_service.search_service.get_popular_posts(all_posts, 5)
                return [{"slug": p.slug, "title": p.title, "category": p.category.value} for p in popular]
        except Exception as e:
            logger.error(f"Could not get popular posts: {e}")
        
        return []
    
    async def _get_recent_posts(self) -> List[Dict[str, str]]:
        """Get recent posts for suggestions"""
        try:
            if self.blog_service:
                all_posts = self.blog_service.get_all_posts(status='published')
                # Sort by published_at or created_at
                recent = sorted(all_posts, key=lambda p: p.published_at or p.created_at, reverse=True)[:5]
                return [{"slug": p.slug, "title": p.title, "category": p.category.value} for p in recent]
        except Exception as e:
            logger.error(f"Could not get recent posts: {e}")
        
        return []
    
    def _track_missing_slug(self, slug: str, request_info: Dict):
        """Track missing slug patterns for analysis"""
        pattern_key = self._clean_slug(slug)
        
        if pattern_key not in self.missing_slug_patterns:
            self.missing_slug_patterns[pattern_key] = {
                'count': 0,
                'first_seen': datetime.now().isoformat(),
                'last_seen': None,
                'variations': [],
                'user_agents': set(),
                'referers': set()
            }
        
        pattern = self.missing_slug_patterns[pattern_key]
        pattern['count'] += 1
        pattern['last_seen'] = datetime.now().isoformat()
        
        if slug not in pattern['variations']:
            pattern['variations'].append(slug)
        
        if request_info.get('user_agent'):
            pattern['user_agents'].add(request_info['user_agent'])
        
        if request_info.get('referer'):
            pattern['referers'].add(request_info['referer'])
        
        # Keep user_agents and referers as lists in JSON
        pattern['user_agents'] = list(pattern['user_agents'])
        pattern['referers'] = list(pattern['referers'])
    
    def get_analytics_report(self) -> Dict[str, Any]:
        """Get analytics report of 404 patterns"""
        total_misses = sum(p['count'] for p in self.missing_slug_patterns.values())
        
        top_missing = sorted(
            self.missing_slug_patterns.items(),
            key=lambda x: x[1]['count'],
            reverse=True
        )[:10]
        
        return {
            "total_404_count": total_misses,
            "unique_patterns": len(self.missing_slug_patterns),
            "redirect_cache_size": len(self.redirect_cache),
            "top_missing_slugs": [
                {
                    "pattern": pattern,
                    "count": data['count'],
                    "variations": data['variations'][:5],  # Top 5 variations
                    "last_seen": data['last_seen']
                }
                for pattern, data in top_missing
            ],
            "cache_stats": {
                "search_cache_size": len(self.search_cache),
                "last_cache_clear": self.last_cache_clear.isoformat()
            }
        }
    
    def add_redirect(self, old_slug: str, new_slug: str):
        """Manually add a redirect mapping"""
        self.redirect_cache[old_slug] = f"/blog/{new_slug}"
        self._save_redirect_mappings()
        logger.info(f"Added redirect: {old_slug} -> {new_slug}")
    
    def clear_caches(self):
        """Clear all caches"""
        self.search_cache.clear()
        self.popularity_cache.clear()
        self.last_cache_clear = datetime.now()
        logger.info("Cleared all caches")


# Global fallback router instance
_fallback_router: Optional[SmartFallbackRouter] = None


def get_fallback_router(blog_service=None) -> SmartFallbackRouter:
    """Get or create global fallback router instance"""
    global _fallback_router
    
    if _fallback_router is None:
        _fallback_router = SmartFallbackRouter(blog_service)
    
    return _fallback_router