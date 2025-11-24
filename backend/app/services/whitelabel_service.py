"""
WhitelabelService - Handles white-label configuration and asset storage.
Uses Supabase Storage for logo/favicon uploads with CDN delivery.
"""
import os
import uuid
import logging
from typing import Dict, Optional, BinaryIO
from pathlib import Path
from supabase import create_client, Client
from sqlalchemy.orm import Session

from app.models.agency import Agency
from app.core.config import settings

logger = logging.getLogger(__name__)

class WhitelabelService:
    """Service for managing white-label settings and asset uploads"""

    def __init__(self):
        """Initialize Supabase client for storage operations"""
        self.supabase_url = settings.SUPABASE_URL or settings.REACT_APP_SUPABASE_URL
        self.supabase_key = settings.SUPABASE_SERVICE_ROLE_KEY

        if not self.supabase_url or not self.supabase_key:
            logger.warning("Supabase credentials not configured - storage features will be disabled")
            self.supabase: Optional[Client] = None
        else:
            self.supabase: Client = create_client(self.supabase_url, self.supabase_key)

        # Storage bucket name for whitelabel assets
        self.bucket_name = "whitelabel-assets"

    def _ensure_bucket_exists(self):
        """Ensure the whitelabel assets bucket exists"""
        if not self.supabase:
            raise Exception("Supabase client not initialized")

        try:
            # Try to get bucket
            buckets = self.supabase.storage.list_buckets()
            bucket_names = [b['name'] for b in buckets]

            if self.bucket_name not in bucket_names:
                # Create bucket with public access
                self.supabase.storage.create_bucket(
                    self.bucket_name,
                    options={"public": True}
                )
                logger.info(f"Created Supabase storage bucket: {self.bucket_name}")
        except Exception as e:
            logger.error(f"Error ensuring bucket exists: {e}")
            # Bucket might already exist, continue anyway

    def upload_logo(
        self,
        agency_id: str,
        file_content: bytes,
        filename: str,
        content_type: str = "image/png"
    ) -> Dict[str, str]:
        """
        Upload a logo to Supabase Storage

        Args:
            agency_id: UUID of the agency
            file_content: Binary content of the file
            filename: Original filename
            content_type: MIME type of the file

        Returns:
            Dict with 'url' and 'path' keys
        """
        if not self.supabase:
            raise Exception("Supabase storage not configured")

        try:
            self._ensure_bucket_exists()

            # Generate unique filename
            file_ext = Path(filename).suffix
            unique_filename = f"{agency_id}/logo-{uuid.uuid4()}{file_ext}"

            # Upload to Supabase Storage
            response = self.supabase.storage.from_(self.bucket_name).upload(
                path=unique_filename,
                file=file_content,
                file_options={
                    "content-type": content_type,
                    "cache-control": "3600",
                    "upsert": "true"
                }
            )

            # Get public URL
            public_url = self.supabase.storage.from_(self.bucket_name).get_public_url(unique_filename)

            logger.info(f"Uploaded logo for agency {agency_id}: {public_url}")

            return {
                "url": public_url,
                "path": unique_filename,
                "bucket": self.bucket_name
            }

        except Exception as e:
            logger.error(f"Error uploading logo: {e}")
            raise Exception(f"Failed to upload logo: {str(e)}")

    def delete_logo(self, file_path: str) -> bool:
        """
        Delete a logo from Supabase Storage

        Args:
            file_path: Path to the file in storage (e.g., "agency-id/logo-uuid.png")

        Returns:
            True if deleted successfully
        """
        if not self.supabase:
            raise Exception("Supabase storage not configured")

        try:
            self.supabase.storage.from_(self.bucket_name).remove([file_path])
            logger.info(f"Deleted logo: {file_path}")
            return True
        except Exception as e:
            logger.error(f"Error deleting logo: {e}")
            return False

    def get_agency_settings(
        self,
        db: Session,
        agency_id: str,
        user_id: str
    ) -> Dict:
        """
        Get white-label settings for an agency

        Args:
            db: Database session
            agency_id: UUID of the agency
            user_id: UUID of the requesting user (for authorization)

        Returns:
            White-label settings dict
        """
        # Get agency from database
        agency = db.query(Agency).filter(Agency.id == agency_id).first()

        if not agency:
            raise Exception(f"Agency not found: {agency_id}")

        # Verify user has access (owner or team member)
        if str(agency.owner_user_id) != user_id:
            # TODO: Check if user is team member
            raise Exception("Unauthorized: User does not have access to this agency")

        return agency.whitelabel_settings

    def update_agency_settings(
        self,
        db: Session,
        agency_id: str,
        user_id: str,
        settings: Dict
    ) -> Dict:
        """
        Update white-label settings for an agency

        Args:
            db: Database session
            agency_id: UUID of the agency
            user_id: UUID of the requesting user
            settings: New settings to apply

        Returns:
            Updated settings
        """
        # Get agency from database
        agency = db.query(Agency).filter(Agency.id == agency_id).first()

        if not agency:
            raise Exception(f"Agency not found: {agency_id}")

        # Verify user has access
        if str(agency.owner_user_id) != user_id:
            raise Exception("Unauthorized: User does not have access to this agency")

        # Update settings
        agency.update_whitelabel_settings(settings)
        db.commit()
        db.refresh(agency)

        logger.info(f"Updated white-label settings for agency {agency_id}")

        return agency.whitelabel_settings

    def create_agency_for_user(
        self,
        db: Session,
        user_id: str,
        name: str,
        description: Optional[str] = None
    ) -> Agency:
        """
        Create a new agency for a user

        Args:
            db: Database session
            user_id: UUID of the user creating the agency
            name: Agency name
            description: Optional agency description

        Returns:
            Created Agency model
        """
        # Check if user already has an agency
        existing = db.query(Agency).filter(Agency.owner_user_id == user_id).first()
        if existing:
            logger.info(f"User {user_id} already has agency {existing.id}, returning existing")
            return existing

        # Create new agency
        agency = Agency(
            owner_user_id=user_id,
            name=name,
            description=description,
            settings={}
        )

        db.add(agency)
        db.commit()
        db.refresh(agency)

        logger.info(f"Created new agency {agency.id} for user {user_id}")

        return agency


# Singleton instance
whitelabel_service = WhitelabelService()
