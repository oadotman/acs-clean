from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import UUID, JSONB
from app.core.database import Base
import enum
import uuid

class AgencyStatus(enum.Enum):
    ACTIVE = "active"
    SUSPENDED = "suspended"
    CANCELLED = "cancelled"

class Agency(Base):
    __tablename__ = "agencies"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)

    # Owner reference (user who created the agency)
    owner_user_id = Column(UUID(as_uuid=True), nullable=False, index=True)

    # Subscription tier
    subscription_tier = Column(String, default='agency_standard')

    # Team limits
    max_team_members = Column(Integer, default=10)
    monthly_analysis_limit = Column(Integer, default=500)

    # White-label settings (JSONB)
    settings = Column(JSONB, default={}, nullable=False)

    # Status
    status = Column(Enum(AgencyStatus), default=AgencyStatus.ACTIVE)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def __repr__(self):
        return f"<Agency(name='{self.name}', owner='{self.owner_user_id}')>"

    @property
    def whitelabel_enabled(self):
        """Check if white-label is enabled"""
        return self.settings.get('white_label_enabled', False)

    @property
    def whitelabel_settings(self):
        """Get white-label settings"""
        return {
            'enabled': self.settings.get('white_label_enabled', False),
            'companyName': self.settings.get('company_name', ''),
            'customLogo': self.settings.get('logo_url', None),
            'primaryColor': self.settings.get('primary_color', '#7C3AED'),
            'secondaryColor': self.settings.get('secondary_color', '#A855F7'),
            'customDomain': self.settings.get('custom_domain', ''),
            'domainVerified': self.settings.get('domain_verified', False),
            'customSupportEmail': self.settings.get('support_email', ''),
            'sslEnabled': self.settings.get('ssl_enabled', True),
            'favicon': self.settings.get('favicon_url', None),
            'reportHeaderLogo': self.settings.get('report_logo_url', None),
            'reportFooterText': self.settings.get('report_footer_text', ''),
        }

    def update_whitelabel_settings(self, settings_dict):
        """Update white-label settings"""
        if not self.settings:
            self.settings = {}

        # Map frontend field names to backend field names
        field_mapping = {
            'companyName': 'company_name',
            'customLogo': 'logo_url',
            'primaryColor': 'primary_color',
            'secondaryColor': 'secondary_color',
            'customDomain': 'custom_domain',
            'domainVerified': 'domain_verified',
            'customSupportEmail': 'support_email',
            'sslEnabled': 'ssl_enabled',
            'favicon': 'favicon_url',
            'reportHeaderLogo': 'report_logo_url',
            'reportFooterText': 'report_footer_text',
        }

        for frontend_key, backend_key in field_mapping.items():
            if frontend_key in settings_dict:
                self.settings[backend_key] = settings_dict[frontend_key]

        # Enable white-label if settings are provided
        if settings_dict:
            self.settings['white_label_enabled'] = True
