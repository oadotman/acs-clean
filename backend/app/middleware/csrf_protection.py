"""
CSRF Protection Middleware for AdCopySurge
Implements comprehensive CSRF protection with token-based validation
"""

import secrets
import hashlib
import hmac
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
import json
import redis
import logging

from fastapi import Request, Response, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

from app.core.config import settings

logger = logging.getLogger(__name__)

# Initialize Redis for CSRF token storage
try:
    redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)
    logger.info("Redis connected for CSRF protection")
except Exception as e:
    logger.warning(f"Redis not available for CSRF protection: {e}")
    redis_client = None

class CSRFProtectionMiddleware(BaseHTTPMiddleware):
    """
    CSRF Protection Middleware implementing double-submit cookie pattern
    with additional server-side validation
    """
    
    def __init__(self, app):
        super().__init__(app)
        self.token_lifetime = 3600  # 1 hour
        self.cookie_name = "csrftoken"
        self.header_name = "X-CSRFToken"
        self.form_field_name = "csrf_token"
        
        # Methods that require CSRF protection
        self.protected_methods = {"POST", "PUT", "DELETE", "PATCH"}
        
        # Paths that don't need CSRF protection
        self.exempt_paths = {
            "/health",
            "/metrics",
            "/api/docs",
            "/api/redoc",
            "/api/openapi.json",
            "/api/auth/login",     # Initial login doesn't have CSRF token yet
            "/api/auth/register",  # Initial registration doesn't have CSRF token yet
            "/api/team/invite",    # Team invitations (authenticated via session)
            "/api/support/send",   # Support tickets (rate-limited separately)
        }
        
        # Paths that need CSRF protection (all others by default)
        self.protected_paths = {
            "/api/ads/analyze",
            "/api/ads/generate-alternatives",
            "/api/auth/logout",
            "/api/subscriptions/",
            "/api/analytics/",
        }

    async def dispatch(self, request: Request, call_next):
        """Main CSRF protection logic"""
        
        # Skip CSRF protection for exempt paths
        if self._is_exempt_path(request.url.path):
            response = await call_next(request)
            # Still add CSRF token for future requests
            if request.method == "GET":
                await self._add_csrf_token(request, response)
            return response
        
        # Skip for safe methods (GET, HEAD, OPTIONS)
        if request.method not in self.protected_methods:
            response = await call_next(request)
            # Add CSRF token to GET responses
            if request.method == "GET":
                await self._add_csrf_token(request, response)
            return response
        
        try:
            # Validate CSRF token for protected methods
            is_valid = await self._validate_csrf_token(request)
            if not is_valid:
                logger.warning(f"CSRF validation failed for {request.url.path} from {request.client.host}")
                return self._create_csrf_error_response()
            
            # Process the request
            response = await call_next(request)
            
            # Refresh CSRF token in response
            await self._add_csrf_token(request, response)
            
            return response
            
        except Exception as e:
            logger.error(f"CSRF middleware error: {e}")
            # Fail secure - block the request
            return self._create_csrf_error_response()

    def _is_exempt_path(self, path: str) -> bool:
        """Check if path is exempt from CSRF protection"""
        # Exact match
        if path in self.exempt_paths:
            return True
        
        # Prefix match for API docs and similar
        exempt_prefixes = ["/docs", "/redoc", "/openapi", "/favicon"]
        for prefix in exempt_prefixes:
            if path.startswith(prefix):
                return True
        
        return False

    async def _validate_csrf_token(self, request: Request) -> bool:
        """Validate CSRF token from header, form, or cookie"""
        
        # Get CSRF token from various sources
        csrf_token = self._extract_csrf_token(request)
        if not csrf_token:
            return False
        
        # Get expected token from cookie
        cookie_token = request.cookies.get(self.cookie_name)
        if not cookie_token:
            return False
        
        # Basic double-submit validation
        if not self._tokens_match(csrf_token, cookie_token):
            return False
        
        # Additional server-side validation if Redis available
        if redis_client:
            return await self._validate_server_side_token(csrf_token, request)
        
        return True

    def _extract_csrf_token(self, request: Request) -> Optional[str]:
        """Extract CSRF token from request headers or form data"""
        
        # Check X-CSRFToken header (preferred for AJAX)
        token = request.headers.get(self.header_name)
        if token:
            return token
        
        # Check X-CSRF-TOKEN header (alternative)
        token = request.headers.get("X-CSRF-TOKEN")
        if token:
            return token
        
        # For form submissions, would check form data
        # This requires parsing request body which is tricky in middleware
        # Better handled in individual endpoints if needed
        
        return None

    def _tokens_match(self, token1: str, token2: str) -> bool:
        """Secure token comparison to prevent timing attacks"""
        if not token1 or not token2:
            return False
        
        # Use hmac.compare_digest for constant-time comparison
        return hmac.compare_digest(token1.encode(), token2.encode())

    async def _validate_server_side_token(self, token: str, request: Request) -> bool:
        """Server-side token validation using Redis"""
        try:
            # Create token key with IP and User-Agent for additional security
            client_ip = request.client.host
            user_agent = request.headers.get("User-Agent", "")
            token_key = f"csrf:{hashlib.sha256((token + client_ip + user_agent).encode()).hexdigest()[:16]}"
            
            # Check if token exists and is valid
            token_data = await redis_client.get(token_key)
            if not token_data:
                return False
            
            token_info = json.loads(token_data)
            
            # Check expiration
            expires_at = datetime.fromisoformat(token_info.get("expires_at", ""))
            if datetime.utcnow() > expires_at:
                # Clean up expired token
                await redis_client.delete(token_key)
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Server-side CSRF validation error: {e}")
            return False

    async def _add_csrf_token(self, request: Request, response: Response):
        """Add CSRF token to response"""
        try:
            # Generate new CSRF token
            csrf_token = secrets.token_urlsafe(32)
            
            # Set CSRF cookie with secure attributes
            response.set_cookie(
                key=self.cookie_name,
                value=csrf_token,
                max_age=self.token_lifetime,
                httponly=False,  # JavaScript needs to read this for AJAX
                secure=settings.ENVIRONMENT == "production",
                samesite="lax"  # Balance between security and functionality
            )
            
            # Add token to response headers for JavaScript access
            response.headers["X-CSRFToken"] = csrf_token
            
            # Store server-side token if Redis available
            if redis_client:
                await self._store_server_side_token(csrf_token, request)
                
        except Exception as e:
            logger.error(f"Error adding CSRF token: {e}")

    async def _store_server_side_token(self, token: str, request: Request):
        """Store CSRF token server-side for additional validation"""
        try:
            client_ip = request.client.host
            user_agent = request.headers.get("User-Agent", "")
            token_key = f"csrf:{hashlib.sha256((token + client_ip + user_agent).encode()).hexdigest()[:16]}"
            
            token_data = {
                "token": token,
                "ip": client_ip,
                "user_agent": user_agent[:200],  # Limit length
                "created_at": datetime.utcnow().isoformat(),
                "expires_at": (datetime.utcnow() + timedelta(seconds=self.token_lifetime)).isoformat()
            }
            
            await redis_client.setex(token_key, self.token_lifetime, json.dumps(token_data))
            
        except Exception as e:
            logger.error(f"Error storing server-side CSRF token: {e}")

    def _create_csrf_error_response(self) -> JSONResponse:
        """Create standardized CSRF error response"""
        return JSONResponse(
            status_code=403,
            content={
                "error": "CSRF_TOKEN_MISSING_OR_INVALID",
                "message": "CSRF token missing or invalid. Please refresh the page and try again.",
                "code": "CSRF_VALIDATION_FAILED"
            },
            headers={
                "X-Content-Type-Options": "nosniff",
                "X-Frame-Options": "DENY"
            }
        )

class CSRFHelper:
    """Helper class for CSRF token operations in endpoints"""
    
    @staticmethod
    def get_csrf_token_from_request(request: Request) -> Optional[str]:
        """Extract CSRF token from request for manual validation"""
        return request.headers.get("X-CSRFToken") or request.headers.get("X-CSRF-TOKEN")
    
    @staticmethod
    def generate_csrf_token() -> str:
        """Generate a new CSRF token"""
        return secrets.token_urlsafe(32)
    
    @staticmethod
    async def validate_csrf_manually(request: Request, token: str) -> bool:
        """Manual CSRF validation for special cases"""
        cookie_token = request.cookies.get("csrftoken")
        if not cookie_token or not token:
            return False
        return hmac.compare_digest(token.encode(), cookie_token.encode())

# Function to add CSRF middleware to FastAPI app
def add_csrf_protection_middleware(app):
    """Add CSRF protection middleware to FastAPI application"""
    if settings.ENVIRONMENT == "production":
        app.add_middleware(CSRFProtectionMiddleware)
        logger.info("CSRF protection middleware enabled for production")
    else:
        logger.info("CSRF protection middleware disabled for development")

# Export helper for use in endpoints
csrf_helper = CSRFHelper()