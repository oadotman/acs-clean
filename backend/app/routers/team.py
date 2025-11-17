"""
Team management API endpoints for invitations and team member operations.
Fixed version that uses code-based invitations for reliability.
"""

from fastapi import APIRouter, HTTPException, Depends, Request
from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional, List
from datetime import datetime, timedelta
import logging
import secrets
import string
import hashlib

from app.core.config import settings
from supabase import create_client, Client

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/team", tags=["team"])

# Initialize Supabase client
def get_supabase_client() -> Client:
    """Get Supabase client instance."""
    if not settings.REACT_APP_SUPABASE_URL or not settings.SUPABASE_SERVICE_ROLE_KEY:
        raise HTTPException(status_code=500, detail="Supabase configuration missing")
    return create_client(settings.REACT_APP_SUPABASE_URL, settings.SUPABASE_SERVICE_ROLE_KEY)


def generate_invitation_code(length: int = 6) -> str:
    """
    Generate a random invitation code using uppercase letters and digits.

    Args:
        length: Length of the code (default 6)

    Returns:
        A random code like 'A3B7K9'
    """
    characters = string.ascii_uppercase + string.digits
    # Avoid confusing characters
    characters = characters.replace('O', '').replace('0', '').replace('I', '').replace('1', '')
    return ''.join(secrets.choice(characters) for _ in range(length))


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
    invitation_code: Optional[str] = None  # Short code for manual sharing


class ResendInvitationRequest(BaseModel):
    """Resend invitation request model."""
    invitation_id: str = Field(..., description="Invitation ID to resend")
    inviter_user_id: str = Field(..., description="User ID of person resending")


@router.post("/invite", response_model=TeamInvitationResponse)
async def send_team_invitation(
    invitation: TeamInvitationRequest,
    request: Request
):
    """
    Create a team invitation with a shareable code.

    This endpoint:
    1. Validates that the user doesn't already exist in the agency
    2. Creates an invitation record with a 6-character code
    3. Returns the code for manual sharing (via Slack, email, etc.)

    The code-based approach is more reliable than email delivery and gives
    users flexibility in how they share invitations.
    """
    try:
        logger.info(f"Processing team invitation for {invitation.email} to agency {invitation.agency_id}")

        # Initialize Supabase client
        supabase = get_supabase_client()

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

        # 3. Generate a shareable invitation code
        invitation_code = generate_invitation_code(6)

        # Also generate a secure token for URL-based acceptance (backwards compatibility)
        invitation_token = secrets.token_urlsafe(32)

        # Use 7-day expiration for code-based invitations
        expires_at = datetime.utcnow() + timedelta(days=7)

        # 4. Get agency details for the invitation
        agency_result = supabase.table('agencies').select('name').eq('id', invitation.agency_id).execute()
        agency_name = agency_result.data[0]['name'] if agency_result.data else "the team"

        # 5. Create invitation record with both code and token
        invitation_data = {
            "agency_id": invitation.agency_id,
            "email": invitation.email.lower(),
            "role": invitation.role,
            "status": "pending",
            "invitation_token": invitation_token,  # For URL-based acceptance
            "invitation_code": invitation_code,     # For code-based acceptance
            "expires_at": expires_at.isoformat(),
            "invited_by": invitation.inviter_user_id,
            "project_access": invitation.project_access,
            "client_access": invitation.client_access
        }

        # Check if invitation_code column exists, if not use invitation_token field for the code
        try:
            result = supabase.table('agency_invitations').insert(invitation_data).execute()
        except Exception as e:
            # If invitation_code column doesn't exist, store code in invitation_token
            logger.warning(f"invitation_code column may not exist, using invitation_token field: {str(e)}")
            invitation_data.pop('invitation_code')
            invitation_data['invitation_token'] = invitation_code  # Use short code as token
            result = supabase.table('agency_invitations').insert(invitation_data).execute()

        if not result.data:
            logger.error("Failed to create invitation record")
            raise HTTPException(status_code=500, detail="Failed to create invitation")

        invitation_id = result.data[0]['id']
        logger.info(f"Created invitation record with ID: {invitation_id} and code: {invitation_code}")

        # Return success with the invitation code for manual sharing
        return TeamInvitationResponse(
            success=True,
            message=f"Invitation created for {invitation.email}. Share this code: {invitation_code}",
            invitation_id=str(invitation_id),
            invitation_code=invitation_code
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing team invitation: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process team invitation: {str(e)}"
        )


@router.post("/invite/resend", response_model=TeamInvitationResponse)
async def resend_team_invitation(
    resend_request: ResendInvitationRequest
):
    """
    Generate a new invitation code for an existing invitation.
    """
    try:
        supabase = get_supabase_client()

        # Get invitation details
        invitation_result = supabase.table('agency_invitations').select('*').eq('id', resend_request.invitation_id).execute()

        if not invitation_result.data:
            raise HTTPException(status_code=404, detail="Invitation not found")

        invitation_data = invitation_result.data[0]

        # Generate new code and extend expiration
        new_code = generate_invitation_code(6)
        new_token = secrets.token_urlsafe(32)
        new_expiration = datetime.utcnow() + timedelta(days=7)

        # Update invitation with new code
        update_data = {
            'invitation_token': new_code,  # Store code in token field for compatibility
            'expires_at': new_expiration.isoformat(),
            'status': 'pending'
        }

        # Try to update invitation_code if column exists
        try:
            update_data['invitation_code'] = new_code
            update_result = supabase.table('agency_invitations').update(update_data).eq('id', resend_request.invitation_id).execute()
        except:
            # Column doesn't exist, just use invitation_token
            update_result = supabase.table('agency_invitations').update(update_data).eq('id', resend_request.invitation_id).execute()

        logger.info(f"Regenerated invitation code for {invitation_data['email']}: {new_code}")

        return TeamInvitationResponse(
            success=True,
            message=f"New invitation code generated. Share this code: {new_code}",
            invitation_id=resend_request.invitation_id,
            invitation_code=new_code
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error resending team invitation: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to resend invitation: {str(e)}"
        )


@router.post("/invite/accept-code")
async def accept_invitation_by_code(
    code: str = Field(..., description="6-character invitation code"),
    user_id: str = Field(..., description="User ID accepting the invitation")
):
    """
    Accept an invitation using a 6-character code.

    This endpoint allows users to join a team by entering the invitation code
    they received from the team owner.
    """
    try:
        supabase = get_supabase_client()

        # Normalize code (uppercase, no spaces)
        code = code.strip().upper()

        # Find invitation by code
        # Try invitation_code column first, fall back to invitation_token
        invitation_result = supabase.table('agency_invitations').select('*').eq('invitation_code', code).eq('status', 'pending').execute()

        if not invitation_result.data:
            # Try invitation_token field (for backwards compatibility)
            invitation_result = supabase.table('agency_invitations').select('*').eq('invitation_token', code).eq('status', 'pending').execute()

        if not invitation_result.data:
            raise HTTPException(status_code=404, detail="Invalid or expired invitation code")

        invitation = invitation_result.data[0]

        # Check if invitation has expired
        expires_at = datetime.fromisoformat(invitation['expires_at'].replace('Z', '+00:00'))
        if expires_at < datetime.utcnow():
            raise HTTPException(status_code=400, detail="Invitation has expired")

        # Add user to agency team
        team_member_data = {
            'agency_id': invitation['agency_id'],
            'user_id': user_id,
            'role': invitation['role'],
            'joined_at': datetime.utcnow().isoformat()
        }

        if invitation.get('project_access'):
            team_member_data['project_access'] = invitation['project_access']
        if invitation.get('client_access'):
            team_member_data['client_access'] = invitation['client_access']

        # Insert team member
        member_result = supabase.table('agency_team_members').insert(team_member_data).execute()

        if not member_result.data:
            raise HTTPException(status_code=500, detail="Failed to add user to team")

        # Mark invitation as accepted
        supabase.table('agency_invitations').update({
            'status': 'accepted',
            'accepted_at': datetime.utcnow().isoformat(),
            'accepted_by': user_id
        }).eq('id', invitation['id']).execute()

        logger.info(f"User {user_id} successfully joined agency {invitation['agency_id']} using code {code}")

        return {
            'success': True,
            'message': 'Successfully joined the team',
            'agency_id': invitation['agency_id'],
            'role': invitation['role']
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error accepting invitation by code: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to accept invitation: {str(e)}"
        )