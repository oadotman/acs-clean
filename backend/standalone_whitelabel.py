"""
Standalone White-label API server with no external app dependencies.
This version is completely self-contained for testing purposes.
"""

import os
import uuid
import json
from typing import Optional, Dict, Any
from fastapi import FastAPI, APIRouter, HTTPException, File, UploadFile, Form, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr, validator
import uvicorn

# Simple in-memory storage for testing
SETTINGS_STORAGE = {}
UPLOADED_FILES = {}

# Create FastAPI app
app = FastAPI(
    title="AdCopySurge White-Label API (Standalone)",
    description="Standalone server for testing white-label functionality",
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

# Pydantic models
class WhiteLabelSettings(BaseModel):
    """White-label settings model"""
    company_name: str
    custom_domain: Optional[str] = None
    custom_support_email: Optional[EmailStr] = None
    primary_color: str = "#1976d2"
    secondary_color: str = "#dc004e"
    accent_color: str = "#10b981"
    hide_original_branding: bool = False
    remove_powered_by: bool = False
    custom_login_page: bool = False
    ssl_enabled: bool = True
    
    @validator('custom_domain')
    def validate_domain(cls, v):
        if v and v.strip():
            domain = v.strip().lower()
            if domain.count('.') < 1:
                raise ValueError('Domain must contain at least one dot')
            if len(domain) < 4:
                raise ValueError('Domain too short')
            return domain
        return None

class DomainValidationRequest(BaseModel):
    domain: str

class TestEmailRequest(BaseModel):
    email: EmailStr

# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy", "message": "Standalone white-label API is running"}

@app.get("/api/whitelabel/health")
async def whitelabel_health():
    """White-label API health check"""
    return {
        "status": "healthy",
        "available": True,
        "endpoints": [
            "/api/whitelabel/settings",
            "/api/whitelabel/settings/{user_id}",
            "/api/whitelabel/validate-domain", 
            "/api/whitelabel/test-email"
        ]
    }

@app.post("/api/whitelabel/settings")
async def save_whitelabel_settings(
    settings_data: WhiteLabelSettings,
    user_id: str = "demo_user"
):
    """Save white-label settings"""
    try:
        user_settings = {
            "company_name": settings_data.company_name,
            "custom_domain": settings_data.custom_domain,
            "custom_support_email": settings_data.custom_support_email,
            "primary_color": settings_data.primary_color,
            "secondary_color": settings_data.secondary_color,
            "accent_color": settings_data.accent_color,
            "hide_original_branding": settings_data.hide_original_branding,
            "remove_powered_by": settings_data.remove_powered_by,
            "custom_login_page": settings_data.custom_login_page,
            "ssl_enabled": settings_data.ssl_enabled,
            "setup_completed": True,
            "enabled": True
        }
        
        SETTINGS_STORAGE[user_id] = user_settings
        
        return {
            "success": True,
            "message": "White-label settings saved successfully",
            "data": user_settings
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to save settings: {str(e)}"
        )

@app.get("/api/whitelabel/settings/{user_id}")
async def get_whitelabel_settings(user_id: str = "demo_user"):
    """Get white-label settings"""
    try:
        settings = SETTINGS_STORAGE.get(user_id, {})
        
        return {
            "success": True,
            "data": settings if settings else None,
            "message": "Settings loaded successfully" if settings else "No settings found"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to load settings: {str(e)}"
        )

@app.post("/api/whitelabel/validate-domain")
async def validate_domain(request: DomainValidationRequest):
    """Validate a custom domain"""
    try:
        domain = request.domain.strip().lower()
        
        if not domain:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Domain is required"
            )
        
        # Simple validation
        valid = domain.count('.') >= 1 and len(domain) >= 4
        available = domain not in ["google.com", "facebook.com", "twitter.com"]
        
        return {
            "success": True,
            "data": {
                "domain": domain,
                "available": available,
                "valid": valid,
                "suggestions": [f"my-{domain}", f"app-{domain}"] if not available else [],
                "ssl_available": True
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Domain validation failed: {str(e)}"
        )

@app.post("/api/whitelabel/test-email")
async def send_test_email(request: TestEmailRequest):
    """Send a test email"""
    try:
        print(f"🔧 Test email would be sent to: {request.email}")
        
        return {
            "success": True,
            "message": f"Test email sent successfully to {request.email}",
            "details": {
                "recipient": request.email,
                "subject": "White-label Platform Test Email",
                "provider": "mock-email-service"
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to send test email: {str(e)}"
        )

@app.get("/api/whitelabel/debug/storage")
async def debug_storage():
    """Debug endpoint to view storage"""
    return {
        "settings_count": len(SETTINGS_STORAGE),
        "settings": SETTINGS_STORAGE
    }

@app.get("/")
async def root():
    return {
        "message": "Standalone White-Label API",
        "docs": "/api/docs",
        "health": "/api/whitelabel/health"
    }

if __name__ == "__main__":
    print("🚀 Starting standalone white-label server...")
    print("📋 Available endpoints:")
    print("   - Health: http://localhost:8000/api/whitelabel/health")
    print("   - Docs: http://localhost:8000/api/docs")
    print("   - Settings: http://localhost:8000/api/whitelabel/settings")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )