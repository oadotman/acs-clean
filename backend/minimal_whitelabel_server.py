import os
import sys
import time
import logging
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn

# Add the backend directory to the path so we can import our modules
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

# Import simplified white-label API
from app.api.whitelabel_simple import router as whitelabel_router

# Setup basic logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="AdCopySurge White-Label API (Minimal)",
    description="Minimal server for testing white-label functionality",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json"
)

# CORS middleware - Allow all origins for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Health check endpoint
@app.get("/health")
async def health_check():
    """Basic health check"""
    return {
        "status": "healthy", 
        "timestamp": time.time(),
        "message": "White-label API is running (minimal mode)"
    }

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "AdCopySurge White-Label API (Minimal Mode)",
        "version": "1.0.0",
        "docs": "/api/docs",
        "health": "/health",
        "white_label_endpoints": "/api/whitelabel"
    }

# Include white-label API routes
app.include_router(whitelabel_router, prefix="/api/whitelabel", tags=["white-label"])

if __name__ == "__main__":
    print("🚀 Starting minimal white-label server...")
    print("📋 Available endpoints:")
    print("   - Health: http://localhost:8000/health")
    print("   - Docs: http://localhost:8000/api/docs")
    print("   - White-label API: http://localhost:8000/api/whitelabel")
    
    uvicorn.run(
        "minimal_whitelabel_server:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )