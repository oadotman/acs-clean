from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer
from fastapi.staticfiles import StaticFiles
from pathlib import Path
import uvicorn
from app.api import auth, ads, analytics, subscriptions
from app.api.creative import router as creative_router
from app.api.health_fixed import router as health_router
from app.api.v1.auth_status import router as auth_status_router
from api.integrations import router as integrations_router
from app.routers.team import router as team_router
from app.routers.support import router as support_router
from app.routers.whitelabel import router as whitelabel_router
from app.core.config import settings
from app.core.logging import setup_logging, get_logger

# SECURITY: Import security middleware
from app.middleware.rate_limiting import add_rate_limiting_middleware
from app.middleware.csrf_protection import add_csrf_protection_middleware
from app.middleware.security_headers import (
    add_security_headers_middleware,
    add_security_reporting_middleware,
    add_content_security_middleware
)

# Import enhanced components
try:
    from app.core.database_enhanced import create_all_tables
except ImportError:
    # Fallback to original database
    from app.core.database import engine, Base
    def create_all_tables():
        if engine:
            Base.metadata.create_all(bind=engine)

try:
    from app.core.error_handlers import setup_error_handling
except ImportError:
    setup_error_handling = None

# Setup logging first
setup_logging()
logger = get_logger(__name__)

# Import blog router conditionally
blog_router = None
if settings.ENABLE_BLOG:
    try:
        from app.blog import router as blog_module
        blog_router = blog_module.router
        logger.info("Blog router imported successfully")
    except ImportError as e:
        logger.warning(f"Blog router import failed: {e}")
else:
    logger.info("Blog functionality disabled via settings")

# Logging is now set up above

# Create database tables (enhanced version)
try:
    create_all_tables()
except Exception as e:
    logger.warning(f"Database table creation skipped: {e}")

# SECURITY: Conditionally disable API documentation in production
docs_url = None if settings.ENVIRONMENT == "production" else "/api/docs"
redoc_url = None if settings.ENVIRONMENT == "production" else "/api/redoc"

app = FastAPI(
    title="AdCopySurge API",
    description="AI-powered ad copy analysis and optimization platform",
    version="1.0.0",
    docs_url=docs_url,
    redoc_url=redoc_url
)

# Setup global error handling
if setup_error_handling:
    setup_error_handling(app, enable_debug=settings.DEBUG)
    logger.info("Global error handling enabled")

# SECURITY: Add comprehensive security middleware (order matters)
add_content_security_middleware(app)        # First - validate incoming content
add_security_headers_middleware(app)         # Add security headers to all responses
add_security_reporting_middleware(app)       # Handle security violation reports
add_csrf_protection_middleware(app)          # CSRF protection for state-changing requests
add_rate_limiting_middleware(app)            # Rate limiting (after auth to get user context)

# CORS middleware with proper origin handling
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,  # Use CORS_ORIGINS instead of ALLOWED_HOSTS
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["*"],
    expose_headers=["*"]
)

# Include routers
app.include_router(health_router, tags=["monitoring"])  # Health checks at root level
app.include_router(auth_status_router, prefix="/api", tags=["authentication"])  # Enhanced auth status
app.include_router(auth.router, prefix="/api/auth", tags=["authentication"])
app.include_router(ads.router, prefix="/api/ads", tags=["ad-analysis"])
app.include_router(creative_router, prefix="/api/creative", tags=["creative-controls"])  # Phase 4-7 Creative Controls
app.include_router(analytics.router, prefix="/api/analytics", tags=["analytics"])
app.include_router(subscriptions.router, prefix="/api/subscriptions", tags=["subscriptions"])
app.include_router(integrations_router, prefix="/api", tags=["integrations"])
app.include_router(team_router, prefix="/api", tags=["team"])  # Team invitation and management
app.include_router(support_router, prefix="/api", tags=["support"])  # Support tickets
app.include_router(whitelabel_router, prefix="/api/whitelabel", tags=["whitelabel"])  # White-label configuration

# Include blog router if enabled and available
if blog_router is not None:
    app.include_router(blog_router, prefix="/api/blog", tags=["blog"])
    logger.info("Blog router included with prefix /api/blog")
else:
    logger.info("Blog router not included - disabled or import failed")

@app.get("/")
async def root():
    return {"message": "AdCopySurge API is running", "version": "1.0.0"}

# Health endpoints now handled by health.router

# Static files are served by Netlify in production
# Keep this for local development only
if settings.DEBUG and not settings.is_vps:
    static_files_path = Path(__file__).parent / "../frontend/build"
    if static_files_path.exists():
        app.mount("/static", StaticFiles(directory=str(static_files_path)), name="static")
        logger.info("Static file serving enabled for local development")
    else:
        logger.info("Frontend build directory not found - static serving disabled")
else:
    logger.info("Static file serving disabled - frontend served by Netlify")

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )
