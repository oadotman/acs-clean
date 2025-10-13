"""
Simplified White-label API endpoints for testing without database dependencies.
This version uses in-memory storage for demonstration purposes.
"""

import os
import uuid
import base64
import json
from typing import Optional, Dict, Any
from fastapi import APIRouter, HTTPException, File, UploadFile, Form, status
from pydantic import BaseModel, EmailStr, validator
from PIL import Image
import io

# Simple in-memory storage for testing
SETTINGS_STORAGE = {}
UPLOADED_FILES = {}

router = APIRouter()

# Pydantic models for request/response
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
    custom_terms_url: Optional[str] = None
    custom_privacy_url: Optional[str] = None
    report_footer_text: Optional[str] = None
    
    @validator('custom_domain')
    def validate_domain(cls, v):
        if v and v.strip():
            # Basic domain validation
            domain = v.strip().lower()
            if not domain.replace('-', '').replace('.', '').replace('_', '').isalnum():
                raise ValueError('Domain contains invalid characters')
            if domain.count('.') < 1:
                raise ValueError('Domain must contain at least one dot')
            if len(domain) < 4:
                raise ValueError('Domain too short')
            return domain
        return None

class DomainValidationRequest(BaseModel):
    """Domain validation request"""
    domain: str

class TestEmailRequest(BaseModel):
    """Test email request"""
    email: EmailStr

class DomainValidationResponse(BaseModel):
    """Domain validation response"""
    domain: str
    available: bool
    valid: bool
    suggestions: list = []
    dns_records: Optional[Dict] = None
    ssl_available: bool = True

class LogoUploadResponse(BaseModel):
    """Logo upload response"""
    success: bool
    logo_url: Optional[str] = None
    thumbnail_url: Optional[str] = None
    file_size: Optional[int] = None
    dimensions: Optional[Dict] = None
    error: Optional[str] = None

# File storage configuration
UPLOAD_DIR = "uploads/whitelabel"
MAX_LOGO_SIZE = 5 * 1024 * 1024  # 5MB
ALLOWED_IMAGE_TYPES = ["image/jpeg", "image/png", "image/svg+xml", "image/webp"]

def ensure_upload_dir():
    """Ensure upload directory exists"""
    upload_path = os.path.join(os.getcwd(), UPLOAD_DIR)
    os.makedirs(upload_path, exist_ok=True)
    return upload_path

def process_logo_image(file_content: bytes, max_width: int = 400, max_height: int = 200) -> tuple:
    """Process and optimize logo image"""
    try:
        # Open image
        image = Image.open(io.BytesIO(file_content))
        
        # Get original dimensions
        original_width, original_height = image.size
        
        # Calculate new dimensions while maintaining aspect ratio
        if original_width > max_width or original_height > max_height:
            ratio = min(max_width / original_width, max_height / original_height)
            new_width = int(original_width * ratio)
            new_height = int(original_height * ratio)
            image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
        
        # Convert to RGB if necessary (for JPEG)
        if image.mode in ('RGBA', 'LA', 'P'):
            # Convert to RGB with white background
            rgb_image = Image.new('RGB', image.size, (255, 255, 255))
            if image.mode == 'P':
                image = image.convert('RGBA')
            rgb_image.paste(image, mask=image.split()[-1] if image.mode == 'RGBA' else None)
            image = rgb_image
        
        # Save processed image
        output = io.BytesIO()
        image.save(output, format='PNG', optimize=True, quality=85)
        processed_content = output.getvalue()
        
        return processed_content, image.size
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid image file: {str(e)}")

@router.get("/health")
async def whitelabel_health():
    """White-label API health check"""
    return {
        "status": "healthy",
        "available": True,
        "endpoints": [
            "/settings",
            "/settings/{user_id}",
            "/upload-logo",
            "/validate-domain", 
            "/test-email",
            "/preview-url/{user_id}",
            "/delete-logo/{filename}"
        ]
    }

@router.post("/settings")
async def save_whitelabel_settings(
    settings_data: WhiteLabelSettings,
    user_id: str = "demo_user"  # Simplified - normally from auth
):
    """Save white-label settings for the current user"""
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
            "custom_terms_url": settings_data.custom_terms_url,
            "custom_privacy_url": settings_data.custom_privacy_url,
            "report_footer_text": settings_data.report_footer_text,
            "setup_completed": True,
            "enabled": True
        }
        
        # Store in memory
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

@router.get("/settings/{user_id}")
async def get_whitelabel_settings(user_id: str = "demo_user"):
    """Get white-label settings for a user"""
    try:
        settings = SETTINGS_STORAGE.get(user_id, {})
        
        if not settings:
            return {
                "success": True,
                "data": None,
                "message": "No settings found for user"
            }
        
        return {
            "success": True,
            "data": settings
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to load settings: {str(e)}"
        )

@router.post("/upload-logo", response_model=LogoUploadResponse)
async def upload_logo(
    logo: UploadFile = File(...),
    user_id: str = Form("demo_user")
):
    """Upload and process a logo file"""
    try:
        # Validate file type
        if logo.content_type not in ALLOWED_IMAGE_TYPES:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid file type. Allowed types: {', '.join(ALLOWED_IMAGE_TYPES)}"
            )
        
        # Read file content
        file_content = await logo.read()
        
        # Validate file size
        if len(file_content) > MAX_LOGO_SIZE:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File too large. Maximum size: {MAX_LOGO_SIZE / 1024 / 1024:.1f}MB"
            )
        
        # Process image
        processed_content, dimensions = process_logo_image(file_content)
        
        # Generate unique filename
        file_ext = os.path.splitext(logo.filename)[1].lower() if logo.filename else '.png'
        unique_filename = f"logo_{user_id}_{uuid.uuid4().hex[:8]}{file_ext}"
        
        # Ensure upload directory exists
        upload_path = ensure_upload_dir()
        file_path = os.path.join(upload_path, unique_filename)
        
        # Save processed file
        with open(file_path, "wb") as f:
            f.write(processed_content)
        
        # Generate URL
        logo_url = f"/static/whitelabel/{unique_filename}"
        
        # Store file info
        UPLOADED_FILES[unique_filename] = {
            "user_id": user_id,
            "original_filename": logo.filename,
            "file_path": file_path,
            "url": logo_url,
            "size": len(processed_content),
            "dimensions": {"width": dimensions[0], "height": dimensions[1]}
        }
        
        return LogoUploadResponse(
            success=True,
            logo_url=logo_url,
            file_size=len(processed_content),
            dimensions={"width": dimensions[0], "height": dimensions[1]}
        )
        
    except HTTPException:
        raise
    except Exception as e:
        return LogoUploadResponse(
            success=False,
            error=f"Upload failed: {str(e)}"
        )

@router.post("/validate-domain")
async def validate_domain(request: DomainValidationRequest):
    """Validate a custom domain"""
    try:
        domain = request.domain.strip().lower()
        
        # Basic domain validation
        if not domain:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Domain is required"
            )
        
        # Simple validation checks
        valid = True
        available = True
        suggestions = []
        
        # Check basic format
        if domain.count('.') < 1:
            valid = False
        
        if len(domain) < 4:
            valid = False
            
        # Mock DNS checks (in production, use actual DNS lookup)
        dns_records = {
            "A": "192.0.2.1",
            "CNAME": f"{domain}",
            "MX": f"mail.{domain}",
            "TXT": f"v=spf1 include:{domain} ~all"
        }
        
        # Generate suggestions if domain is taken
        if domain in ["google.com", "facebook.com", "twitter.com"]:
            available = False
            suggestions = [
                f"my-{domain}",
                f"{domain.split('.')[0]}-app.com",
                f"get-{domain.split('.')[0]}.com"
            ]
        
        return {
            "success": True,
            "data": DomainValidationResponse(
                domain=domain,
                available=available,
                valid=valid,
                suggestions=suggestions,
                dns_records=dns_records if valid and available else None,
                ssl_available=True
            )
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Domain validation failed: {str(e)}"
        )

@router.post("/test-email")
async def send_test_email(request: TestEmailRequest):
    """Send a test email to verify email configuration"""
    try:
        # Mock email sending (in production, use actual email service)
        print(f"🔧 Test email would be sent to: {request.email}")
        print(f"📧 Email content: Welcome to your white-label platform!")
        
        return {
            "success": True,
            "message": f"Test email sent successfully to {request.email}",
            "details": {
                "recipient": request.email,
                "subject": "White-label Platform Test Email",
                "sent_at": "2025-10-13T15:30:00Z",
                "provider": "mock-email-service"
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to send test email: {str(e)}"
        )

@router.get("/preview-url/{user_id}")
async def generate_preview_url(user_id: str):
    """Generate a preview URL for white-label branding"""
    try:
        settings = SETTINGS_STORAGE.get(user_id, {})
        
        if not settings:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No white-label settings found for user"
            )
        
        # Generate preview URL
        preview_url = f"http://localhost:3000/preview/{user_id}"
        
        return {
            "success": True,
            "data": {
                "preview_url": preview_url,
                "settings": settings,
                "expires_at": "2025-10-13T16:30:00Z"
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate preview URL: {str(e)}"
        )

@router.delete("/delete-logo/{filename}")
async def delete_uploaded_logo(filename: str):
    """Delete an uploaded logo file"""
    try:
        file_info = UPLOADED_FILES.get(filename)
        
        if not file_info:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Logo file not found"
            )
        
        # Delete file from storage
        if os.path.exists(file_info["file_path"]):
            os.remove(file_info["file_path"])
        
        # Remove from storage
        del UPLOADED_FILES[filename]
        
        return {
            "success": True,
            "message": f"Logo {filename} deleted successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete logo: {str(e)}"
        )

# Additional debugging endpoints for development
@router.get("/debug/storage")
async def debug_storage():
    """Debug endpoint to view current storage state"""
    return {
        "settings_count": len(SETTINGS_STORAGE),
        "files_count": len(UPLOADED_FILES),
        "settings": SETTINGS_STORAGE,
        "files": {k: {**v, "file_path": "hidden"} for k, v in UPLOADED_FILES.items()}
    }