"""
Pydantic schemas for white-label API
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class WhiteLabelSettingsUpdate(BaseModel):
    """Request schema for updating white-label settings"""
    companyName: Optional[str] = None
    customLogo: Optional[str] = None  # Base64 or URL
    primaryColor: Optional[str] = Field(None, pattern=r'^#[0-9A-Fa-f]{6}$')
    secondaryColor: Optional[str] = Field(None, pattern=r'^#[0-9A-Fa-f]{6}$')
    customDomain: Optional[str] = None
    domainVerified: Optional[bool] = None
    customSupportEmail: Optional[str] = None
    sslEnabled: Optional[bool] = None
    favicon: Optional[str] = None
    reportHeaderLogo: Optional[str] = None
    reportFooterText: Optional[str] = None


class WhiteLabelSettingsResponse(BaseModel):
    """Response schema for white-label settings"""
    enabled: bool
    companyName: str
    customLogo: Optional[str] = None
    primaryColor: str
    secondaryColor: str
    customDomain: str
    domainVerified: bool
    customSupportEmail: str
    sslEnabled: bool
    favicon: Optional[str] = None
    reportHeaderLogo: Optional[str] = None
    reportFooterText: str

    class Config:
        from_attributes = True


class LogoUploadResponse(BaseModel):
    """Response schema for logo upload"""
    success: bool
    url: str
    path: str
    message: str = "Logo uploaded successfully"


class AgencyCreateRequest(BaseModel):
    """Request schema for creating an agency"""
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None


class AgencyResponse(BaseModel):
    """Response schema for agency data"""
    id: str
    name: str
    description: Optional[str]
    owner_user_id: str
    subscription_tier: str
    status: str
    whitelabel_enabled: bool
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


class DomainVerificationRequest(BaseModel):
    """Request schema for domain verification"""
    domain: str
    verification_token: Optional[str] = None


class DomainVerificationResponse(BaseModel):
    """Response schema for domain verification"""
    success: bool
    domain: str
    verified: bool
    message: str
    dns_records: Optional[dict] = None
    errors: Optional[list] = None
