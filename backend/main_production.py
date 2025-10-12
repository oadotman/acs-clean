import os
import sys
import time
import logging
from contextlib import asynccontextmanager
from pathlib import Path
from tenacity import retry, wait_fixed, stop_after_attempt

from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware
from fastapi.responses import JSONResponse, Response
import uvicorn

# Import application modules
from app.api import auth, ads, analytics, subscriptions
from app.blog import router as blog_router
from app.core.config import settings
from app.core.database import engine, Base
from app.core.logging import setup_logging, get_logger

# Setup logging first
setup_logging()
logger = get_logger(__name__)


@retry(
    wait=wait_fixed(3),
    stop=stop_after_attempt(5),
    reraise=True
)
def initialize_database():
    """Initialize database with retry logic for Railway"""
    try:
        logger.info("Creating/verifying database tables...")
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created/verified successfully")
        return True
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        # Test basic connection
        try:
            with engine.connect() as conn:
                from sqlalchemy import text
                result = conn.execute(text("SELECT version()"))
                logger.info(f"Database connection test successful: {result.scalar()}")
        except Exception as conn_e:
            logger.error(f"Database connection test failed: {conn_e}")
        raise

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handle startup and shutdown events with retry logic for Railway"""
    # Startup
    logger.info("Starting AdCopySurge API...")
    
    startup_errors = []
    
    # Initialize database with retries
    try:
        logger.info("Initializing database connection...")
        initialize_database()
        logger.info("Database initialization completed")
    except Exception as e:
        error_msg = f"Critical: Database initialization failed after retries: {e}"
        logger.error(error_msg)
        startup_errors.append(error_msg)
        # Database is critical - fail fast
        sys.exit(1)
    
    # Download NLTK data (non-critical)
    try:
        import nltk
        nltk.download('punkt', quiet=True)
        nltk.download('stopwords', quiet=True)
        logger.info("NLTK data initialized")
    except Exception as e:
        logger.warning(f"NLTK data download failed (non-critical): {e}")
        startup_errors.append(f"NLTK warning: {e}")
    
    # Initialize Redis connection if configured (non-critical)
    if settings.REDIS_URL and settings.REDIS_URL != "redis://localhost:6379":
        try:
            import redis
            redis_client = redis.from_url(settings.REDIS_URL)
            redis_client.ping()
            logger.info("Redis connection verified")
        except Exception as e:
            logger.warning(f"Redis connection failed (non-critical): {e}")
            startup_errors.append(f"Redis warning: {e}")
    
    if startup_errors:
        logger.warning(f"Startup completed with {len(startup_errors)} warnings")
        for error in startup_errors:
            logger.warning(f"  - {error}")
    else:
        logger.info("Application startup completed successfully")
    
    yield
    
    # Shutdown
    logger.info("Shutting down AdCopySurge API...")


# Create FastAPI app with lifespan
app = FastAPI(
    title="AdCopySurge API",
    description="AI-powered ad copy analysis and optimization platform",
    version=settings.APP_VERSION,
    docs_url="/api/docs" if settings.DEBUG else None,
    redoc_url="/api/redoc" if settings.DEBUG else None,
    openapi_url="/api/openapi.json" if settings.DEBUG else None,
    lifespan=lifespan
)

# Security Middleware (in production)
if not settings.DEBUG:
    # Force HTTPS in production
    app.add_middleware(HTTPSRedirectMiddleware)
    
    # Trusted hosts
    app.add_middleware(
        TrustedHostMiddleware, 
        allowed_hosts=["api.adcopysurge.com", "*.adcopysurge.com"]
    )

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_HOSTS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["X-Total-Count", "X-Request-ID"],
)


# Security headers middleware
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    start_time = time.time()
    
    response = await call_next(request)
    
    # Add security headers
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    
    if not settings.DEBUG:
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline'; "
            "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
            "font-src 'self' https://fonts.gstatic.com; "
            "img-src 'self' data: https:; "
            "connect-src 'self' https://api.openai.com"
        )
    
    # Add request timing
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    
    return response


# Health check endpoints
@app.get("/health")
async def health_check():
    """Basic health check"""
    return {"status": "healthy", "timestamp": time.time()}


@app.get("/healthz")
async def kubernetes_health_check():
    """Kubernetes-style health check with dependencies"""
    health_status = {
        "status": "healthy",
        "timestamp": time.time(),
        "version": settings.APP_VERSION,
        "checks": {}
    }
    
    # Check database
    try:
        # Simple database check with proper SQL syntax
        from sqlalchemy import text
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1 as test"))
            test_value = result.scalar()
            if test_value == 1:
                health_status["checks"]["database"] = "healthy"
            else:
                health_status["checks"]["database"] = f"unexpected_result: {test_value}"
                health_status["status"] = "unhealthy"
    except Exception as e:
        health_status["checks"]["database"] = f"unhealthy: {str(e)}"
        health_status["status"] = "unhealthy"
    
    # Check Redis (if configured)
    if settings.REDIS_URL and settings.REDIS_URL != "redis://localhost:6379":
        try:
            import redis
            redis_client = redis.from_url(settings.REDIS_URL)
            redis_client.ping()
            health_status["checks"]["redis"] = "healthy"
        except Exception as e:
            health_status["checks"]["redis"] = f"unhealthy: {str(e)}"
            # Redis is not critical, don't mark as unhealthy
    
    # Check OpenAI API (if configured)
    if settings.OPENAI_API_KEY:
        health_status["checks"]["openai"] = "configured"
    else:
        health_status["checks"]["openai"] = "not_configured"
    
    # Check Blog service (if enabled)
    if settings.ENABLE_BLOG:
        try:
            from app.blog import router as blog_router
            blog_health = blog_router.blog_service.get_health_status()
            if blog_health["healthy"]:
                health_status["checks"]["blog_service"] = "healthy"
            else:
                health_status["checks"]["blog_service"] = f"degraded: {blog_health['error_message']}"
                # Blog degradation doesn't mark overall status as unhealthy
        except Exception as e:
            health_status["checks"]["blog_service"] = f"unhealthy: {str(e)}"
            # Blog issues don't mark overall status as unhealthy
    else:
        health_status["checks"]["blog_service"] = "disabled"
    
    status_code = 200 if health_status["status"] == "healthy" else 503
    return JSONResponse(content=health_status, status_code=status_code)


@app.get("/metrics")
async def prometheus_metrics():
    """Prometheus metrics endpoint"""
    try:
        from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
        return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)
    except ImportError:
        return {"error": "Prometheus client not installed"}


# Include API routes
app.include_router(auth.router, prefix="/api/auth", tags=["authentication"])
app.include_router(ads.router, prefix="/api/ads", tags=["ad-analysis"])
app.include_router(analytics.router, prefix="/api/analytics", tags=["analytics"])
app.include_router(subscriptions.router, prefix="/api/subscriptions", tags=["subscriptions"])

# Include blog router if enabled
if settings.ENABLE_BLOG:
    try:
        app.include_router(blog_router.router, prefix="/api/blog", tags=["blog"])
        logger.info("Blog router included successfully")
    except Exception as e:
        logger.error(f"Failed to include blog router: {e}")
        if not settings.BLOG_GRACEFUL_DEGRADATION:
            raise
else:
    logger.info("Blog functionality disabled via settings")


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "AdCopySurge API is running",
        "version": settings.VERSION,
        "docs": "/api/docs" if settings.DEBUG else None,
        "health": "/health"
    }


# Custom exception handlers
@app.exception_handler(404)
async def not_found_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=404,
        content={
            "error": "Resource not found",
            "path": str(request.url.path),
            "method": request.method
        }
    )


@app.exception_handler(500)
async def internal_error_handler(request: Request, exc: Exception):
    logger.error(f"Internal server error: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "request_id": getattr(request.state, "request_id", None)
        }
    )


if __name__ == "__main__":
    # This is for development only
    # In production, use gunicorn/uvicorn with proper configuration
    uvicorn.run(
        "main_production:app",
        host="0.0.0.0",
        port=8000,
        reload=False,
        log_level="info",
        access_log=True,
        server_header=False,
        date_header=False
    )
