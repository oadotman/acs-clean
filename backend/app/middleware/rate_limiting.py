"""
Rate Limiting Middleware for AdCopySurge
Implements comprehensive rate limiting with different tiers and endpoint-specific limits
"""

import time
import json
import hashlib
from typing import Dict, Tuple, Optional
from datetime import datetime, timedelta
import redis
from fastapi import HTTPException, Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
import logging

from app.core.config import settings

logger = logging.getLogger(__name__)

# Initialize Redis for rate limiting
try:
    redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)
    # Test connection
    redis_client.ping()
    logger.info("Redis connected for rate limiting")
except Exception as e:
    logger.warning(f"Redis not available for rate limiting: {e}")
    redis_client = None

class RateLimitingMiddleware(BaseHTTPMiddleware):
    """
    Advanced rate limiting middleware with multiple strategies:
    - IP-based rate limiting
    - User-based rate limiting (authenticated)
    - Endpoint-specific limits
    - Subscription tier-based limits
    """
    
    def __init__(self, app):
        super().__init__(app)
        
        # Default rate limits (requests per window)
        self.default_limits = {
            "anonymous": {
                "per_minute": 20,
                "per_hour": 100,
                "per_day": 500
            },
            "authenticated": {
                "per_minute": 60,
                "per_hour": 1000,
                "per_day": 5000
            },
            "free": {
                "per_minute": 60,
                "per_hour": 1000,
                "per_day": 5000
            },
            "basic": {
                "per_minute": 100,
                "per_hour": 2000,
                "per_day": 10000
            },
            "pro": {
                "per_minute": 200,
                "per_hour": 5000,
                "per_day": 25000
            }
        }
        
        # Endpoint-specific limits (more restrictive for expensive operations)
        self.endpoint_limits = {
            "/api/ads/analyze": {
                "free": {"per_minute": 5, "per_hour": 20, "per_day": 100},
                "basic": {"per_minute": 10, "per_hour": 60, "per_day": 500},
                "pro": {"per_minute": 20, "per_hour": 120, "per_day": 1000}
            },
            "/api/ads/generate-alternatives": {
                "free": {"per_minute": 3, "per_hour": 15, "per_day": 50},
                "basic": {"per_minute": 8, "per_hour": 40, "per_day": 200},
                "pro": {"per_minute": 15, "per_hour": 80, "per_day": 500}
            },
            "/api/auth/login": {
                "anonymous": {"per_minute": 5, "per_hour": 20, "per_day": 50}
            },
            "/api/auth/register": {
                "anonymous": {"per_minute": 2, "per_hour": 10, "per_day": 20}
            }
        }
        
        # Window sizes in seconds
        self.windows = {
            "per_minute": 60,
            "per_hour": 3600,
            "per_day": 86400
        }
    
    async def dispatch(self, request: Request, call_next):
        """Process rate limiting for incoming requests"""
        
        # Skip rate limiting for health checks and static files
        if request.url.path in ["/health", "/metrics", "/favicon.ico"]:
            return await call_next(request)
        
        # Skip if Redis unavailable (fail open)
        if not redis_client:
            return await call_next(request)
        
        try:
            # Extract client information
            client_ip = self._get_client_ip(request)
            user_id = await self._get_user_id_from_request(request)
            subscription_tier = await self._get_subscription_tier(request)
            
            # Check rate limits
            rate_limit_key = self._generate_rate_limit_key(client_ip, user_id, request.url.path)
            is_allowed, limit_info = await self._check_rate_limit(
                rate_limit_key, 
                request.url.path, 
                subscription_tier
            )
            
            if not is_allowed:
                # Log rate limit violation
                logger.warning(f"Rate limit exceeded: {client_ip} (user: {user_id}) on {request.url.path}")
                
                return self._create_rate_limit_response(limit_info)
            
            # Process request
            response = await call_next(request)
            
            # Add rate limit headers to response
            response.headers.update(self._generate_rate_limit_headers(limit_info))
            
            return response
            
        except Exception as e:
            logger.error(f"Rate limiting middleware error: {e}")
            # Fail open - allow request if rate limiting fails
            return await call_next(request)
    
    def _get_client_ip(self, request: Request) -> str:
        """Extract client IP address with proxy support"""
        # Check for forwarded headers (Nginx, Cloudflare, etc.)
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip.strip()
        
        # Fallback to direct connection IP
        return request.client.host
    
    async def _get_user_id_from_request(self, request: Request) -> Optional[str]:
        """Extract user ID from JWT token if available"""
        try:
            auth_header = request.headers.get("Authorization")
            if not auth_header or not auth_header.startswith("Bearer "):
                return None
            
            token = auth_header.split(" ")[1]
            
            # Simple JWT decode without verification (for rate limiting only)
            import jwt
            payload = jwt.decode(token, options={"verify_signature": False})
            return payload.get("sub")
            
        except Exception:
            return None
    
    async def _get_subscription_tier(self, request: Request) -> str:
        """Get user subscription tier or default to anonymous"""
        try:
            user_id = await self._get_user_id_from_request(request)
            if not user_id:
                return "anonymous"
            
            # Try to get from Redis cache first
            tier_key = f"user_tier:{user_id}"
            cached_tier = await redis_client.get(tier_key)
            if cached_tier:
                return cached_tier
            
            # Default to authenticated if we have user ID but no tier info
            return "authenticated"
            
        except Exception:
            return "anonymous"
    
    def _generate_rate_limit_key(self, client_ip: str, user_id: Optional[str], endpoint: str) -> str:
        """Generate unique rate limit key"""
        if user_id:
            base_key = f"rate_limit:user:{user_id}"
        else:
            base_key = f"rate_limit:ip:{client_ip}"
        
        # Add endpoint specificity for certain endpoints
        endpoint_hash = hashlib.md5(endpoint.encode()).hexdigest()[:8]
        return f"{base_key}:{endpoint_hash}"
    
    async def _check_rate_limit(self, key: str, endpoint: str, tier: str) -> Tuple[bool, Dict]:
        """Check if request is within rate limits"""
        try:
            # Get applicable limits
            limits = self._get_applicable_limits(endpoint, tier)
            current_time = int(time.time())
            
            limit_info = {
                "limits": limits,
                "remaining": {},
                "reset_times": {}
            }
            
            # Check each time window
            for window_name, limit in limits.items():
                window_size = self.windows[window_name]
                window_key = f"{key}:{window_name}"
                
                # Get current count for this window
                current_count = await self._get_window_count(window_key, window_size, current_time)
                
                limit_info["remaining"][window_name] = max(0, limit - current_count)
                limit_info["reset_times"][window_name] = current_time + window_size
                
                # Check if limit exceeded
                if current_count >= limit:
                    return False, limit_info
            
            # Increment counters for allowed request
            await self._increment_counters(key, current_time)
            
            return True, limit_info
            
        except Exception as e:
            logger.error(f"Rate limit check error: {e}")
            # Fail open
            return True, {}
    
    def _get_applicable_limits(self, endpoint: str, tier: str) -> Dict[str, int]:
        """Get rate limits for endpoint and tier"""
        # Check endpoint-specific limits first
        if endpoint in self.endpoint_limits:
            endpoint_rules = self.endpoint_limits[endpoint]
            if tier in endpoint_rules:
                return endpoint_rules[tier]
        
        # Fall back to default limits
        if tier in self.default_limits:
            return self.default_limits[tier]
        
        # Ultimate fallback
        return self.default_limits["anonymous"]
    
    async def _get_window_count(self, window_key: str, window_size: int, current_time: int) -> int:
        """Get current request count for time window"""
        try:
            # Use Redis sorted set for sliding window
            set_key = f"{window_key}:requests"
            
            # Remove old entries
            cutoff_time = current_time - window_size
            await redis_client.zremrangebyscore(set_key, 0, cutoff_time)
            
            # Get current count
            count = await redis_client.zcard(set_key)
            return count
            
        except Exception as e:
            logger.error(f"Window count error: {e}")
            return 0
    
    async def _increment_counters(self, key: str, current_time: int):
        """Increment request counters for all windows"""
        try:
            # Increment for each window type
            for window_name, window_size in self.windows.items():
                set_key = f"{key}:{window_name}:requests"
                
                # Add current request with timestamp
                request_id = f"{current_time}:{hash(key) % 10000}"
                await redis_client.zadd(set_key, {request_id: current_time})
                
                # Set expiration to window size + buffer
                await redis_client.expire(set_key, window_size + 60)
                
        except Exception as e:
            logger.error(f"Counter increment error: {e}")
    
    def _create_rate_limit_response(self, limit_info: Dict) -> Response:
        """Create rate limit exceeded response"""
        # Find which limit was exceeded and when it resets
        reset_time = min(limit_info.get("reset_times", {}).values()) if limit_info.get("reset_times") else int(time.time()) + 60
        
        headers = {
            "X-RateLimit-Limit": str(min(limit_info.get("limits", {}).values()) if limit_info.get("limits") else 100),
            "X-RateLimit-Remaining": "0",
            "X-RateLimit-Reset": str(reset_time),
            "Retry-After": str(reset_time - int(time.time()))
        }
        
        error_response = {
            "error": "Rate limit exceeded",
            "message": "Too many requests. Please try again later.",
            "retry_after": reset_time - int(time.time())
        }
        
        return Response(
            content=json.dumps(error_response),
            status_code=429,
            headers=headers,
            media_type="application/json"
        )
    
    def _generate_rate_limit_headers(self, limit_info: Dict) -> Dict[str, str]:
        """Generate rate limit headers for successful responses"""
        headers = {}
        
        if limit_info.get("limits"):
            # Use the most restrictive limit for headers
            min_limit = min(limit_info["limits"].values())
            min_remaining = min(limit_info["remaining"].values()) if limit_info.get("remaining") else 0
            min_reset = min(limit_info["reset_times"].values()) if limit_info.get("reset_times") else int(time.time()) + 60
            
            headers.update({
                "X-RateLimit-Limit": str(min_limit),
                "X-RateLimit-Remaining": str(min_remaining),
                "X-RateLimit-Reset": str(min_reset)
            })
        
        return headers

# Function to add middleware to FastAPI app
def add_rate_limiting_middleware(app):
    """Add rate limiting middleware to FastAPI application"""
    if settings.ENABLE_RATE_LIMITING:
        app.add_middleware(RateLimitingMiddleware)
        logger.info("Rate limiting middleware enabled")
    else:
        logger.info("Rate limiting middleware disabled")