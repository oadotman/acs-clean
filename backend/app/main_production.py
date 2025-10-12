"""
Production FastAPI application configuration with error handling middleware

This demonstrates how to properly integrate the production error middleware
and ensure fail-fast behavior without mock data fallbacks.
"""

import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.core.exceptions import ConfigurationError, validate_production_environment
from app.middleware import ProductionErrorMiddleware
from app.core.logging import get_logger
from app.core.config import get_settings

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager for production"""
    
    logger.info("Starting adcopysurge API in production mode")
    
    try:
        # Validate production environment before startup
        validate_production_environment()
        
        # Validate required settings
        settings = get_settings()
        if not all([
            settings.openai_api_key,
            settings.gemini_api_key,
            settings.database_url,
            settings.tools_sdk_api_key
        ]):
            raise ConfigurationError(
                "missing_api_keys",
                "Required API keys or database configuration missing"
            )
        
        # Test database connection
        from app.core.database import test_database_connection
        await test_database_connection()
        
        # Test AI provider connectivity
        from app.services.production.production_ai_alternative_generator import ProductionAIAlternativeGenerator
        ai_generator = ProductionAIAlternativeGenerator()
        await ai_generator.health_check()
        
        logger.info("Production environment validation successful")
        
        yield
        
    except Exception as e:
        logger.error(f"Failed to start production application: {e}")
        raise ConfigurationError(
            "startup_failure",
            f"Application failed to start: {str(e)}"
        )
    
    finally:
        logger.info("Shutting down adcopysurge API")


def create_production_app() -> FastAPI:
    """Create production-ready FastAPI application"""
    
    # Create app with production settings
    app = FastAPI(
        title="AdCopySurge API",
        description="Production Ad Copy Analysis and Generation API",
        version="1.0.0",
        docs_url=None if os.getenv("ENVIRONMENT") == "production" else "/docs",
        redoc_url=None if os.getenv("ENVIRONMENT") == "production" else "/redoc",
        lifespan=lifespan
    )
    
    # Add production error handling middleware FIRST
    # This ensures all errors are caught and handled properly
    app.add_middleware(
        ProductionErrorMiddleware,
        include_debug=os.getenv("ENVIRONMENT") != "production"
    )
    
    # Add CORS middleware with production settings
    if os.getenv("ENVIRONMENT") == "production":
        # Strict CORS for production
        allowed_origins = os.getenv("ALLOWED_ORIGINS", "").split(",")
        if not allowed_origins or allowed_origins == [""]:
            raise ConfigurationError(
                "cors_configuration",
                "ALLOWED_ORIGINS must be configured for production"
            )
    else:
        # More permissive for development
        allowed_origins = ["http://localhost:3000", "http://localhost:8000"]
    
    app.add_middleware(
        CORSMiddleware,
        allow_origins=allowed_origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE"],
        allow_headers=["*"],
    )
    
    # Include API routes
    from app.api.v1 import api_router
    app.include_router(api_router, prefix="/api/v1")
    
    # Add health check endpoint
    @app.get("/health")
    async def health_check():
        """Health check endpoint for load balancers"""
        return {"status": "healthy", "service": "adcopysurge_api"}
    
    # Add metrics endpoint (for monitoring)
    @app.get("/metrics")
    async def metrics():
        """Basic metrics endpoint"""
        # This would integrate with your metrics collection system
        return {
            "service": "adcopysurge_api",
            "status": "active",
            "environment": os.getenv("ENVIRONMENT", "unknown")
        }
    
    return app


# Create the application instance
app = create_production_app()


if __name__ == "__main__":
    import uvicorn
    
    # Production server configuration
    uvicorn.run(
        "app.main_production:app",
        host="0.0.0.0",
        port=int(os.getenv("PORT", "8000")),
        workers=int(os.getenv("WORKERS", "4")),
        loop="uvloop",  # High-performance event loop
        http="httptools",  # High-performance HTTP parser
        log_config=None,  # Use our custom logging configuration
        access_log=False  # We handle access logging in middleware
    )