"""
Security Headers Middleware for AdCopySurge
Implements comprehensive HTTP security headers for defense in depth
"""

import logging
from typing import Dict, Optional
from urllib.parse import urlparse

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.config import settings

logger = logging.getLogger(__name__)

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """
    Security Headers Middleware that adds comprehensive HTTP security headers
    to protect against various web vulnerabilities
    """
    
    def __init__(self, app):
        super().__init__(app)
        
        # Content Security Policy for different environments
        self.csp_policies = {
            "production": {
                "default-src": "'self'",
                "script-src": "'self' 'unsafe-inline' https://cdn.paddle.com https://js.stripe.com https://checkout.stripe.com",
                "style-src": "'self' 'unsafe-inline' https://fonts.googleapis.com",
                "font-src": "'self' https://fonts.gstatic.com",
                "img-src": "'self' data: https: blob:",
                "connect-src": "'self' https://api.adcopysurge.com https://*.supabase.co https://api.openai.com wss://*.supabase.co",
                "object-src": "'none'",
                "base-uri": "'self'",
                "form-action": "'self'",
                "frame-ancestors": "'none'",
                "upgrade-insecure-requests": ""
            },
            "development": {
                "default-src": "'self'",
                "script-src": "'self' 'unsafe-inline' 'unsafe-eval' http://localhost:* ws://localhost:*",
                "style-src": "'self' 'unsafe-inline'",
                "font-src": "'self'",
                "img-src": "'self' data: blob:",
                "connect-src": "'self' http://localhost:* ws://localhost:* https://*.supabase.co https://api.openai.com wss://*.supabase.co",
                "object-src": "'none'",
                "base-uri": "'self'",
                "form-action": "'self'"
            }
        }
        
        # Security headers configuration
        self.security_headers = self._get_security_headers_config()

    def _get_security_headers_config(self) -> Dict[str, str]:
        """Get security headers configuration based on environment"""
        
        # Base security headers
        headers = {
            # Prevent clickjacking attacks
            "X-Frame-Options": "DENY",
            
            # Prevent MIME type sniffing
            "X-Content-Type-Options": "nosniff",
            
            # Enable XSS protection (legacy browsers)
            "X-XSS-Protection": "1; mode=block",
            
            # Control referrer information
            "Referrer-Policy": "strict-origin-when-cross-origin",
            
            # Prevent downloading of untrusted executables
            "X-Download-Options": "noopen",
            
            # Control DNS prefetching
            "X-DNS-Prefetch-Control": "off",
            
            # Disable Adobe Flash and PDF plugins
            "X-Permitted-Cross-Domain-Policies": "none",
            
            # Security.txt reference
            "X-Security-Contact": "security@adcopysurge.com",
            
            # Custom security headers
            "X-Content-Type-Options": "nosniff",
            "X-Robots-Tag": "noindex, nofollow" if settings.ENVIRONMENT == "development" else "index, follow"
        }
        
        # Environment-specific headers
        if settings.ENVIRONMENT == "production":
            headers.update({
                # Strict Transport Security (HTTPS only)
                "Strict-Transport-Security": "max-age=31536000; includeSubDomains; preload",
                
                # Expect-CT for certificate transparency
                "Expect-CT": f"max-age=86400, enforce, report-uri=https://api.adcopysurge.com/security/ct-report",
                
                # Feature Policy / Permissions Policy
                "Permissions-Policy": self._get_permissions_policy(),
                
                # Cross-Origin policies
                "Cross-Origin-Embedder-Policy": "require-corp",
                "Cross-Origin-Opener-Policy": "same-origin",
                "Cross-Origin-Resource-Policy": "cross-origin"
            })
        
        # Content Security Policy
        csp_policy = self._build_csp_header()
        if csp_policy:
            headers["Content-Security-Policy"] = csp_policy
        
        return headers

    def _get_permissions_policy(self) -> str:
        """Generate Permissions Policy header"""
        policies = [
            "accelerometer=()",
            "camera=()",
            "geolocation=()",
            "gyroscope=()",
            "magnetometer=()",
            "microphone=()",
            "payment=(self)",  # Allow payment APIs for Paddle/Stripe
            "usb=()",
            "bluetooth=()",
            "fullscreen=(self)",
            "autoplay=()",
            "encrypted-media=()",
            "picture-in-picture=()",
            "display-capture=()",
            "web-share=(self)"
        ]
        return ", ".join(policies)

    def _build_csp_header(self) -> str:
        """Build Content Security Policy header"""
        env = "production" if settings.ENVIRONMENT == "production" else "development"
        csp_directives = self.csp_policies.get(env, {})
        
        if not csp_directives:
            return ""
        
        # Build CSP string
        csp_parts = []
        for directive, sources in csp_directives.items():
            if sources:
                csp_parts.append(f"{directive} {sources}")
            else:
                csp_parts.append(directive)
        
        return "; ".join(csp_parts)

    async def dispatch(self, request: Request, call_next):
        """Add security headers to all responses"""
        
        # Process the request
        response = await call_next(request)
        
        # Add security headers
        self._add_security_headers(request, response)
        
        # Add additional headers based on response type
        self._add_response_type_headers(request, response)
        
        return response

    def _add_security_headers(self, request: Request, response: Response):
        """Add standard security headers to response"""
        
        for header_name, header_value in self.security_headers.items():
            # Don't override existing headers
            if header_name not in response.headers:
                response.headers[header_name] = header_value

    def _add_response_type_headers(self, request: Request, response: Response):
        """Add headers based on response content type and path"""
        
        content_type = response.headers.get("content-type", "")
        path = request.url.path
        
        # API responses
        if path.startswith("/api/") and "application/json" in content_type:
            # No caching for API responses
            response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
            response.headers["Pragma"] = "no-cache"
            response.headers["Expires"] = "0"
            
            # API-specific security headers
            response.headers["X-Content-Type-Options"] = "nosniff"
            response.headers["X-API-Version"] = "1.0.0"
        
        # Static assets
        elif self._is_static_asset(path):
            # Long cache for static assets
            response.headers["Cache-Control"] = "public, max-age=31536000, immutable"
        
        # HTML responses
        elif "text/html" in content_type:
            # Prevent caching of HTML pages
            response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
            response.headers["Pragma"] = "no-cache"
        
        # Health check endpoints
        elif path in ["/health", "/metrics"]:
            response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
            response.headers["X-Health-Check"] = "true"

    def _is_static_asset(self, path: str) -> bool:
        """Check if path is for a static asset"""
        static_extensions = {".js", ".css", ".png", ".jpg", ".jpeg", ".gif", ".ico", ".svg", ".woff", ".woff2", ".ttf"}
        return any(path.endswith(ext) for ext in static_extensions)

class SecurityReportingMiddleware(BaseHTTPMiddleware):
    """
    Middleware for handling security reporting endpoints
    (CSP violations, Certificate Transparency, etc.)
    """
    
    def __init__(self, app):
        super().__init__(app)
        self.reporting_endpoints = {
            "/security/csp-report",
            "/security/ct-report", 
            "/security/hpkp-report"
        }

    async def dispatch(self, request: Request, call_next):
        """Handle security reporting"""
        
        if request.url.path in self.reporting_endpoints:
            return await self._handle_security_report(request)
        
        return await call_next(request)

    async def _handle_security_report(self, request: Request):
        """Process security violation reports"""
        try:
            if request.method != "POST":
                return Response(status_code=405)
            
            # Read report data
            body = await request.body()
            
            # Log security violation
            logger.warning(f"Security violation report from {request.client.host}: {body.decode()[:500]}")
            
            # In production, you might want to:
            # - Store in database for analysis
            # - Send to security monitoring service
            # - Alert security team for critical violations
            
            return Response(status_code=204)  # No Content
            
        except Exception as e:
            logger.error(f"Error processing security report: {e}")
            return Response(status_code=500)

class ContentSecurityMiddleware(BaseHTTPMiddleware):
    """
    Middleware for content security validation and sanitization
    """
    
    def __init__(self, app):
        super().__init__(app)
        self.max_request_size = 10 * 1024 * 1024  # 10MB
        self.suspicious_patterns = [
            b"<script",
            b"javascript:",
            b"vbscript:",
            b"onload=",
            b"onerror=",
            b"eval(",
            b"document.cookie",
            b"window.location"
        ]

    async def dispatch(self, request: Request, call_next):
        """Validate request content security"""
        
        # Check request size
        content_length = request.headers.get("content-length")
        if content_length and int(content_length) > self.max_request_size:
            logger.warning(f"Request too large: {content_length} bytes from {request.client.host}")
            return Response(
                status_code=413,
                content="Request entity too large"
            )
        
        # For POST/PUT requests, scan for suspicious content
        if request.method in ["POST", "PUT", "PATCH"]:
            if await self._has_suspicious_content(request):
                logger.warning(f"Suspicious content detected from {request.client.host}")
                return Response(
                    status_code=400,
                    content="Request contains suspicious content"
                )
        
        return await call_next(request)

    async def _has_suspicious_content(self, request: Request) -> bool:
        """Check if request contains suspicious patterns"""
        try:
            # Only check text content types
            content_type = request.headers.get("content-type", "")
            if not any(ct in content_type.lower() for ct in ["json", "text", "xml", "form"]):
                return False
            
            body = await request.body()
            if not body:
                return False
            
            # Check for suspicious patterns (case insensitive)
            body_lower = body.lower()
            for pattern in self.suspicious_patterns:
                if pattern in body_lower:
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error checking suspicious content: {e}")
            return False

# Functions to add middleware to FastAPI app
def add_security_headers_middleware(app):
    """Add security headers middleware to FastAPI application"""
    app.add_middleware(SecurityHeadersMiddleware)
    logger.info("Security headers middleware enabled")

def add_security_reporting_middleware(app):
    """Add security reporting middleware to FastAPI application"""
    if settings.ENVIRONMENT == "production":
        app.add_middleware(SecurityReportingMiddleware)
        logger.info("Security reporting middleware enabled")

def add_content_security_middleware(app):
    """Add content security middleware to FastAPI application"""
    app.add_middleware(ContentSecurityMiddleware)
    logger.info("Content security middleware enabled")