"""
Team management API endpoints for invitations and team member operations.
"""

from fastapi import APIRouter, HTTPException, Depends, Request
from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional, List
from datetime import datetime, timedelta
import logging
import secrets
import hashlib

from app.core.config import settings
from app.services.email_service import EmailService
from supabase import create_client, Client

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/team", tags=["team"])

# Initialize Supabase client
def get_supabase_client() -> Client:
    """Get Supabase client instance."""
    if not settings.REACT_APP_SUPABASE_URL or not settings.SUPABASE_SERVICE_ROLE_KEY:
        raise HTTPException(status_code=500, detail="Supabase configuration missing")
    return create_client(settings.REACT_APP_SUPABASE_URL, settings.SUPABASE_SERVICE_ROLE_KEY)


class TeamInvitationRequest(BaseModel):
    """Team invitation request model."""
    email: EmailStr = Field(..., description="Email of person to invite")
    agency_id: str = Field(..., description="Agency ID sending the invitation")
    inviter_user_id: str = Field(..., description="User ID of person sending invitation")
    role: str = Field(default="viewer", description="Role to assign: admin, editor, viewer, client")
    project_access: Optional[List[str]] = Field(default=[], description="List of project IDs for access")
    client_access: Optional[List[str]] = Field(default=[], description="List of client IDs for access")
    personal_message: Optional[str] = Field(None, max_length=500, description="Optional personal message")
    
    @validator('role')
    def validate_role(cls, v):
        allowed_roles = ['admin', 'editor', 'viewer', 'client']
        if v not in allowed_roles:
            raise ValueError(f'Role must be one of: {", ".join(allowed_roles)}')
        return v


class TeamInvitationResponse(BaseModel):
    """Team invitation response model."""
    success: bool
    message: str
    invitation_id: Optional[str] = None
    email_sent: bool = False


def generate_invitation_token() -> str:
    """Generate a secure invitation token."""
    return secrets.token_hex(32)


@router.post("/invite", response_model=TeamInvitationResponse)
async def send_team_invitation(
    invitation: TeamInvitationRequest,
    request: Request
):
    """
    Send a team invitation email and create invitation record.
    
    This endpoint:
    1. Validates that the user doesn't already exist in the agency
    2. Creates an invitation record in the database
    3. Sends an invitation email with a secure link
    """
    try:
        logger.info(f"Processing team invitation for {invitation.email} to agency {invitation.agency_id}")
        
        # Initialize services
        supabase = get_supabase_client()
        email_service = EmailService()
        
        # 1. Check if user already exists and is a member
        user_check = supabase.table('user_profiles').select('id').eq('email', invitation.email).execute()
        
        if user_check.data:
            user_id = user_check.data[0]['id']
            # Check if already a member
            member_check = supabase.table('agency_team_members').select('id').eq('agency_id', invitation.agency_id).eq('user_id', user_id).execute()
            
            if member_check.data:
                raise HTTPException(
                    status_code=400,
                    detail="User is already a member of this agency"
                )
        
        # 2. Check for existing pending invitation and delete it
        existing_invitation = supabase.table('agency_invitations').select('id').eq('agency_id', invitation.agency_id).eq('email', invitation.email.lower()).execute()
        
        if existing_invitation.data:
            logger.info(f"Deleting existing invitation for {invitation.email}")
            supabase.table('agency_invitations').delete().eq('id', existing_invitation.data[0]['id']).execute()
        
        # 3. Generate invitation token and expiration
        invitation_token = generate_invitation_token()
        expires_at = datetime.utcnow() + timedelta(days=7)
        
        # 4. Create invitation record
        invitation_data = {
            "agency_id": invitation.agency_id,
            "email": invitation.email.lower(),
            "role": invitation.role,
            "status": "pending",
            "invitation_token": invitation_token,
            "expires_at": expires_at.isoformat(),
            "invited_by": invitation.inviter_user_id,
            "project_access": invitation.project_access,
            "client_access": invitation.client_access
        }
        
        result = supabase.table('agency_invitations').insert(invitation_data).execute()
        
        if not result.data:
            logger.error("Failed to create invitation record")
            raise HTTPException(status_code=500, detail="Failed to create invitation")
        
        invitation_id = result.data[0]['id']
        logger.info(f"Created invitation record with ID: {invitation_id}")
        
        # 5. Get agency details for email
        agency_result = supabase.table('agencies').select('name').eq('id', invitation.agency_id).execute()
        agency_name = agency_result.data[0]['name'] if agency_result.data else "the team"
        
        # 6. Get inviter details
        inviter_result = supabase.table('user_profiles').select('full_name, email').eq('id', invitation.inviter_user_id).execute()
        invited_by_name = inviter_result.data[0]['full_name'] if inviter_result.data and inviter_result.data[0].get('full_name') else inviter_result.data[0]['email'] if inviter_result.data else "A team member"
        
        # 7. Send invitation email
        role_names = {
            'admin': 'Administrator',
            'editor': 'Editor',
            'viewer': 'Viewer',
            'client': 'Client'
        }
        
        email_result = await email_service.send_team_invitation(
            email=invitation.email,
            agency_name=agency_name,
            invitation_token=invitation_token,
            invited_by=invited_by_name,
            role_name=role_names.get(invitation.role, 'Team Member'),
            personal_message=invitation.personal_message
        )
        
        email_sent = email_result.get('success', False)
        
        if not email_sent:
            logger.warning(f"Email sending failed: {email_result.get('error')}")
            # Don't fail the request - invitation is still created
            return TeamInvitationResponse(
                success=True,
                message=f"Invitation created but email notification failed. The invitation link can be shared manually.",
                invitation_id=str(invitation_id),
                email_sent=False
            )
        
        logger.info(f"Successfully sent invitation email to {invitation.email}")
        
        return TeamInvitationResponse(
            success=True,
            message=f"Invitation sent successfully to {invitation.email}",
            invitation_id=str(invitation_id),
            email_sent=True
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing team invitation: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process team invitation: {str(e)}"
        )


@router.post("/invite/resend")
async def resend_team_invitation(
    invitation_id: str = Field(..., description="Invitation ID to resend"),
    inviter_user_id: str = Field(..., description="User ID of person resending")
):
    """
    Resend a team invitation email.
    """
    try:
        supabase = get_supabase_client()
        email_service = EmailService()
        
        # Get invitation details
        invitation_result = supabase.table('agency_invitations').select('*').eq('id', invitation_id).execute()
        
        if not invitation_result.data:
            raise HTTPException(status_code=404, detail="Invitation not found")
        
        invitation_data = invitation_result.data[0]
        
        # Generate new token and extend expiration
        new_token = generate_invitation_token()
        new_expiration = datetime.utcnow() + timedelta(days=7)
        
        # Update invitation
        update_result = supabase.table('agency_invitations').update({
            'invitation_token': new_token,
            'expires_at': new_expiration.isoformat(),
            'status': 'pending'
        }).eq('id', invitation_id).execute()
        
        # Get agency details
        agency_result = supabase.table('agencies').select('name').eq('id', invitation_data['agency_id']).execute()
        agency_name = agency_result.data[0]['name'] if agency_result.data else "the team"
        
        # Get inviter details
        inviter_result = supabase.table('user_profiles').select('full_name, email').eq('id', inviter_user_id).execute()
        invited_by_name = inviter_result.data[0]['full_name'] if inviter_result.data and inviter_result.data[0].get('full_name') else inviter_result.data[0]['email'] if inviter_result.data else "A team member"
        
        # Send email
        role_names = {
            'admin': 'Administrator',
            'editor': 'Editor',
            'viewer': 'Viewer',
            'client': 'Client'
        }
        
        email_result = await email_service.send_team_invitation(
            email=invitation_data['email'],
            agency_name=agency_name,
            invitation_token=new_token,
            invited_by=invited_by_name,
            role_name=role_names.get(invitation_data['role'], 'Team Member')
        )
        
        return TeamInvitationResponse(
            success=True,
            message="Invitation resent successfully",
            invitation_id=invitation_id,
            email_sent=email_result.get('success', False)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error resending team invitation: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to resend invitation: {str(e)}"
        )
