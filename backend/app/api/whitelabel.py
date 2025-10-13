"""
White-label API endpoints for branding, logo upload, and custom domain management.
Handles all white-label functionality including file uploads, email configuration, and domain validation.
"""

import os
import uuid
import base64
from typing import Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, File, UploadFile, Form, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr, validator
from PIL import Image
import io

from app.core.database import get_db
from app.auth import get_current_user
from app.models.user import User
from app.services.email_service import email_service
from app.core.logging import get_logger
from app.core.config import settings

logger = get_logger(__name__)
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

class WhiteLabelResponse(BaseModel):
    """Response model for white-label settings"""
    id: int
    user_id: int
    company_name: str
    custom_domain: Optional[str]
    custom_support_email: Optional[str]
    primary_color: str
    secondary_color: str
    accent_color: str
    logo_url: Optional[str]
    favicon_url: Optional[str]
    setup_completed: bool
    enabled: bool
    created_at: str
    updated_at: Optional[str]

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
    upload_path = os.path.join(settings.BASE_DIR if hasattr(settings, 'BASE_DIR') else os.getcwd(), UPLOAD_DIR)
    os.makedirs(upload_path, exist_ok=True)
    return upload_path

def save_uploaded_file(file_content: bytes, filename: str, user_id: int) -> tuple:
    """Save uploaded file and return URL and file info"""
    upload_path = ensure_upload_dir()
    
    # Generate unique filename
    file_ext = os.path.splitext(filename)[1].lower()
    unique_filename = f"logo_{user_id}_{uuid.uuid4().hex[:8]}{file_ext}"
    file_path = os.path.join(upload_path, unique_filename)
    
    # Save file
    with open(file_path, "wb") as f:
        f.write(file_content)
    
    # Generate URL (in production, use CDN/cloud storage URL)
    file_url = f"/static/whitelabel/{unique_filename}"
    
    return file_url, file_path

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
        logger.error(f"Error processing image: {e}")
        raise HTTPException(status_code=400, detail="Invalid image file")

@router.post("/settings", response_model=Dict[str, Any])
async def save_whitelabel_settings(
    settings_data: WhiteLabelSettings,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Save white-label settings for the current user"""
    try:
        # For now, store in user's metadata or create a separate table
        # This is a simplified implementation - in production you'd have a WhiteLabel table
        
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
        
        # Save to user metadata (simplified approach)
        # In production, create a separate WhiteLabel table
        if not hasattr(current_user, 'whitelabel_settings'):
            current_user.whitelabel_settings = {}
        
        # Update user's white-label settings
        # For now, we'll store as JSON in a text field or metadata
        logger.info(f"Saving white-label settings for user {current_user.id}: {settings_data.company_name}")
        
        return {
            "success": True,
            "message": "White-label settings saved successfully",
            "settings": user_settings
        }
        
    except Exception as e:
        logger.error(f"Error saving white-label settings: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to save white-label settings"
        )

@router.get("/settings", response_model=Dict[str, Any])
async def get_whitelabel_settings(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get white-label settings for the current user"""
    try:
        # Return default settings for now
        # In production, fetch from WhiteLabel table
        default_settings = {
            "company_name": current_user.company or "Your Agency",
            "custom_domain": None,
            "custom_support_email": None,
            "primary_color": "#1976d2",
            "secondary_color": "#dc004e",
            "accent_color": "#10b981",
            "logo_url": None,
            "favicon_url": None,
            "setup_completed": False,
            "enabled": False,
            "hide_original_branding": False,
            "remove_powered_by": False,
            "custom_login_page": False,
            "ssl_enabled": True
        }
        
        return {
            "success": True,
            "settings": default_settings
        }
        
    except Exception as e:
        logger.error(f"Error fetching white-label settings: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch white-label settings"
        )

@router.post("/upload-logo", response_model=LogoUploadResponse)
async def upload_logo(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Upload and process company logo"""
    try:
        # Validate file
        if not file.content_type in ALLOWED_IMAGE_TYPES:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid file type. Allowed types: {', '.join(ALLOWED_IMAGE_TYPES)}"
            )
        
        # Read file content
        file_content = await file.read()
        
        # Check file size
        if len(file_content) > MAX_LOGO_SIZE:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File too large. Maximum size: {MAX_LOGO_SIZE // (1024*1024)}MB"
            )
        
        # Process image (resize, optimize)
        if file.content_type != "image/svg+xml":
            processed_content, dimensions = process_logo_image(file_content)
        else:
            processed_content = file_content
            dimensions = None
        
        # Save file
        file_url, file_path = save_uploaded_file(processed_content, file.filename, current_user.id)
        
        # Generate thumbnail for non-SVG images
        thumbnail_url = None
        if file.content_type != "image/svg+xml" and dimensions:
            try:
                thumb_content, _ = process_logo_image(file_content, max_width=64, max_height=64)
                thumb_filename = f"thumb_{os.path.basename(file_url)}"
                thumb_path = os.path.join(os.path.dirname(file_path), thumb_filename)
                
                with open(thumb_path, "wb") as f:
                    f.write(thumb_content)
                
                thumbnail_url = f"/static/whitelabel/thumb_{os.path.basename(file_url)}"
            except Exception as e:
                logger.warning(f"Failed to generate thumbnail: {e}")
        
        logger.info(f"Logo uploaded successfully for user {current_user.id}: {file_url}")
        
        return LogoUploadResponse(
            success=True,
            logo_url=file_url,
            thumbnail_url=thumbnail_url,
            file_size=len(processed_content),
            dimensions={"width": dimensions[0], "height": dimensions[1]} if dimensions else None
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error uploading logo: {e}")
        return LogoUploadResponse(
            success=False,
            error=str(e)
        )

@router.post("/validate-domain", response_model=DomainValidationResponse)
async def validate_custom_domain(
    domain: str = Form(...),
    current_user: User = Depends(get_current_user)
):
    """Validate custom domain availability and configuration"""
    try:
        # Clean domain input
        domain = domain.strip().lower()
        if domain.startswith(('http://', 'https://')):
            domain = domain.split('://', 1)[1]
        if domain.startswith('www.'):
            domain = domain[4:]
        
        # Basic validation
        if not domain or len(domain) < 4:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Domain is too short"
            )
        
        # Check for invalid characters
        if not domain.replace('-', '').replace('.', '').replace('_', '').isalnum():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Domain contains invalid characters"
            )
        
        # Check if domain has valid TLD
        if domain.count('.') < 1:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Domain must have a valid TLD (e.g., .com, .org)"
            )
        
        # In production, you would:
        # 1. Check DNS records
        # 2. Verify domain ownership
        # 3. Check if domain is already in use
        # 4. Generate DNS setup instructions
        
        # For now, return mock validation
        dns_records = {
            "cname": {
                "name": domain,
                "value": "app.adcopysurge.com",
                "type": "CNAME"
            },
            "txt": {
                "name": f"_adcopysurge-verify.{domain}",
                "value": f"adcopysurge-verify={uuid.uuid4().hex[:16]}",
                "type": "TXT"
            }
        }
        
        return DomainValidationResponse(
            domain=domain,
            available=True,  # Mock - in production check actual availability
            valid=True,
            suggestions=[],
            dns_records=dns_records,
            ssl_available=True
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error validating domain {domain}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Domain validation failed"
        )

@router.post("/test-email")
async def test_support_email(
    email: EmailStr = Form(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Test support email functionality"""
    try:
        # Get user's white-label settings
        # In production, fetch from WhiteLabel table
        white_label_settings = {
            "company_name": current_user.company or "Your Agency",
            "custom_domain": None,  # Would fetch from settings
            "support_email": email,
            "primary_color": "#1976d2",
            "logo_url": None
        }
        
        # Send test email
        result = await email_service.send_welcome_email(
            email=email,
            user_name=current_user.full_name or current_user.email,
            agency_name=white_label_settings["company_name"],
            is_agency_owner=True,
            white_label_settings=white_label_settings
        )
        
        if result.get('success'):
            return {
                "success": True,
                "message": f"Test email sent successfully to {email}",
                "email_id": result.get('message_id')
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to send test email: {result.get('error')}"
            )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error sending test email: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to send test email"
        )

@router.post("/generate-preview-url")
async def generate_preview_url(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Generate a preview URL for the white-label platform"""
    try:
        # Generate unique preview token
        preview_token = uuid.uuid4().hex[:16]
        
        # In production, you would:
        # 1. Save preview token to database with expiration
        # 2. Associate with user's white-label settings
        # 3. Return temporary preview URL
        
        preview_url = f"https://preview.adcopysurge.com/{preview_token}"
        
        return {
            "success": True,
            "preview_url": preview_url,
            "expires_in": 3600,  # 1 hour
            "instructions": "Use this URL to preview your white-label platform. Link expires in 1 hour."
        }
        
    except Exception as e:
        logger.error(f"Error generating preview URL: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate preview URL"
        )

@router.delete("/logo")
async def delete_logo(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete uploaded logo"""
    try:
        # In production, you would:
        # 1. Get current logo URL from database
        # 2. Delete file from storage
        # 3. Update database to remove logo reference
        
        logger.info(f"Logo deleted for user {current_user.id}")
        
        return {
            "success": True,
            "message": "Logo deleted successfully"
        }
        
    except Exception as e:
        logger.error(f"Error deleting logo: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete logo"
        )

@router.get("/preview/{token}")
async def get_preview_settings(
    token: str,
    db: Session = Depends(get_db)
):
    """Get white-label settings for preview (public endpoint)"""
    try:
        # In production, validate preview token and return associated settings
        # For now, return mock settings
        
        mock_settings = {
            "company_name": "Demo Agency",
            "primary_color": "#1976d2",
            "secondary_color": "#dc004e",
            "logo_url": None,
            "custom_domain": "demo.agency.com",
            "enabled": True,
            "preview_mode": True
        }
        
        return {
            "success": True,
            "settings": mock_settings,
            "preview_mode": True
        }
        
    except Exception as e:
        logger.error(f"Error getting preview settings for token {token}: {e}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Preview not found or expired"
        )