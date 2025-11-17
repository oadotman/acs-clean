"""
White-label configuration API endpoints
Handles agency white-label settings, logo uploads, and domain verification
"""
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import Optional
import base64
import logging

from app.core.database import get_db
from app.auth import get_current_user
from app.models.user import User
from app.schemas.whitelabel import (
    WhiteLabelSettingsUpdate,
    WhiteLabelSettingsResponse,
    LogoUploadResponse,
    AgencyCreateRequest,
    AgencyResponse,
    DomainVerificationRequest,
    DomainVerificationResponse
)
from app.services.whitelabel_service import whitelabel_service

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/agency", response_model=AgencyResponse)
async def create_agency(
    request: AgencyCreateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create a new agency for the current user
    """
    try:
        # Get user's supabase_user_id (used as owner_user_id)
        user_id = current_user.supabase_user_id or str(current_user.id)

        agency = whitelabel_service.create_agency_for_user(
            db=db,
            user_id=user_id,
            name=request.name,
            description=request.description
        )

        return AgencyResponse(
            id=str(agency.id),
            name=agency.name,
            description=agency.description,
            owner_user_id=str(agency.owner_user_id),
            subscription_tier=agency.subscription_tier,
            status=agency.status.value,
            whitelabel_enabled=agency.whitelabel_enabled,
            created_at=agency.created_at,
            updated_at=agency.updated_at
        )
    except Exception as e:
        logger.error(f"Error creating agency: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/settings", response_model=WhiteLabelSettingsResponse)
async def get_whitelabel_settings(
    agency_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get white-label settings for an agency
    """
    try:
        user_id = current_user.supabase_user_id or str(current_user.id)

        settings = whitelabel_service.get_agency_settings(
            db=db,
            agency_id=agency_id,
            user_id=user_id
        )

        return settings
    except Exception as e:
        logger.error(f"Error fetching settings: {e}")
        raise HTTPException(status_code=404, detail=str(e))


@router.put("/settings", response_model=WhiteLabelSettingsResponse)
async def update_whitelabel_settings(
    agency_id: str,
    settings: WhiteLabelSettingsUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update white-label settings for an agency
    """
    try:
        user_id = current_user.supabase_user_id or str(current_user.id)

        # Convert Pydantic model to dict, excluding None values
        settings_dict = settings.dict(exclude_none=True)

        updated_settings = whitelabel_service.update_agency_settings(
            db=db,
            agency_id=agency_id,
            user_id=user_id,
            settings=settings_dict
        )

        return updated_settings
    except Exception as e:
        logger.error(f"Error updating settings: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/logo/upload", response_model=LogoUploadResponse)
async def upload_logo(
    agency_id: str = Form(...),
    logo: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Upload a logo to Supabase Storage and update agency settings
    """
    try:
        user_id = current_user.supabase_user_id or str(current_user.id)

        # Validate file type
        allowed_types = ['image/png', 'image/jpeg', 'image/jpg', 'image/svg+xml', 'image/webp']
        if logo.content_type not in allowed_types:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid file type. Allowed: {', '.join(allowed_types)}"
            )

        # Validate file size (5MB limit)
        file_content = await logo.read()
        if len(file_content) > 5 * 1024 * 1024:
            raise HTTPException(
                status_code=400,
                detail="File size must be less than 5MB"
            )

        # Upload to Supabase Storage
        upload_result = whitelabel_service.upload_logo(
            agency_id=agency_id,
            file_content=file_content,
            filename=logo.filename,
            content_type=logo.content_type
        )

        # Update agency settings with new logo URL
        whitelabel_service.update_agency_settings(
            db=db,
            agency_id=agency_id,
            user_id=user_id,
            settings={"customLogo": upload_result["url"]}
        )

        return LogoUploadResponse(
            success=True,
            url=upload_result["url"],
            path=upload_result["path"]
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error uploading logo: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to upload logo: {str(e)}")


@router.post("/domain/verify", response_model=DomainVerificationResponse)
async def verify_domain(
    request: DomainVerificationRequest,
    agency_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Verify domain DNS configuration

    Note: This is a simplified implementation. For production, you should:
    1. Use dnspython to check actual DNS records
    2. Verify TXT records match your verification token
    3. Check CNAME points to your server
    4. Implement async DNS propagation checks
    """
    try:
        user_id = current_user.supabase_user_id or str(current_user.id)

        # Basic domain validation
        domain = request.domain.lower().strip()
        if not domain or '.' not in domain:
            raise HTTPException(status_code=400, detail="Invalid domain format")

        # TODO: Implement actual DNS verification using dnspython
        # For now, just update the domain in settings
        whitelabel_service.update_agency_settings(
            db=db,
            agency_id=agency_id,
            user_id=user_id,
            settings={
                "customDomain": domain,
                "domainVerified": False  # Set to True after real DNS check
            }
        )

        return DomainVerificationResponse(
            success=True,
            domain=domain,
            verified=False,  # Change to True after implementing real DNS check
            message="Domain saved. DNS verification pending implementation.",
            dns_records={
                "cname": {
                    "name": domain,
                    "value": "adcopysurge-app.adcopysurge.com",
                    "type": "CNAME"
                },
                "txt": {
                    "name": f"_adcopysurge-verification.{domain}",
                    "value": request.verification_token or "pending",
                    "type": "TXT"
                }
            }
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error verifying domain: {e}")
        raise HTTPException(status_code=500, detail=str(e))
