"""
User Profile API - Returns user profile with effective subscription tier.

This endpoint considers team membership when returning subscription information.
Team members inherit their agency's subscription tier instead of using their personal tier.
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional
from app.auth.dependencies import get_current_user_id
from app.services.user_tier_service import get_user_effective_subscription
from app.core.logging import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/user", tags=["user"])


class UserProfileResponse(BaseModel):
    """User profile with effective subscription tier"""
    user_id: str
    subscription_tier: str
    is_team_member: bool
    agency_id: Optional[str] = None
    agency_name: Optional[str] = None
    role: Optional[str] = None
    personal_tier: str


@router.get("/profile", response_model=UserProfileResponse)
async def get_user_profile(user_id: str = Depends(get_current_user_id)):
    """
    Get user profile with effective subscription tier.

    This endpoint returns the user's effective subscription tier:
    - If user is a team member: Returns agency's subscription tier
    - If user is not a team member: Returns personal subscription tier

    This ensures team members have access to their agency's features.
    """
    try:
        logger.info(f"Fetching profile for user: {user_id}")

        subscription_data = get_user_effective_subscription(user_id)

        if 'error' in subscription_data:
            logger.error(f"Error in subscription data: {subscription_data['error']}")
            # Continue anyway, will return free tier

        return UserProfileResponse(
            user_id=user_id,
            subscription_tier=subscription_data['subscription_tier'],
            is_team_member=subscription_data['is_team_member'],
            agency_id=subscription_data.get('agency_id'),
            agency_name=subscription_data.get('agency_name'),
            role=subscription_data.get('role'),
            personal_tier=subscription_data['personal_tier']
        )

    except Exception as e:
        logger.error(f"Error fetching user profile: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch user profile: {str(e)}"
        )


@router.get("/effective-tier")
async def get_effective_tier(user_id: str = Depends(get_current_user_id)):
    """
    Get just the effective subscription tier for the current user.

    Quick endpoint for checking subscription level.
    """
    try:
        subscription_data = get_user_effective_subscription(user_id)

        return {
            'subscription_tier': subscription_data['subscription_tier'],
            'is_team_member': subscription_data['is_team_member']
        }

    except Exception as e:
        logger.error(f"Error fetching effective tier: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch subscription tier: {str(e)}"
        )
