"""
User Tier Service - Handles effective subscription tier calculation for users.

This service determines a user's effective subscription tier by checking:
1. If the user is a member of an agency team -> Use agency's subscription tier
2. If not -> Use user's personal subscription tier

This ensures team members inherit their agency's subscription benefits.
"""

from typing import Optional, Dict, Any
from supabase import create_client, Client
from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


def get_supabase_client() -> Client:
    """Get Supabase client instance."""
    if not settings.REACT_APP_SUPABASE_URL or not settings.SUPABASE_SERVICE_ROLE_KEY:
        raise Exception("Supabase configuration missing")
    return create_client(settings.REACT_APP_SUPABASE_URL, settings.SUPABASE_SERVICE_ROLE_KEY)


def get_user_effective_subscription(user_id: str) -> Dict[str, Any]:
    """
    Get the effective subscription tier for a user.

    Logic:
    1. Check if user is a member of an agency team
    2. If yes, return the agency's subscription tier and agency info
    3. If no, return the user's personal subscription tier

    Args:
        user_id: The Supabase user ID (UUID string)

    Returns:
        Dict containing:
        - subscription_tier: The effective subscription tier
        - is_team_member: Boolean indicating if user is part of a team
        - agency_id: Agency ID if user is a team member, None otherwise
        - agency_name: Agency name if user is a team member, None otherwise
        - role: User's role in the agency if team member, None otherwise
        - personal_tier: User's personal subscription tier (for reference)
    """
    try:
        supabase = get_supabase_client()

        # First, get user's personal subscription tier
        user_result = supabase.table('user_profiles').select('subscription_tier').eq('id', user_id).maybeSingle().execute()

        personal_tier = 'free'
        if user_result.data:
            personal_tier = user_result.data.get('subscription_tier', 'free')

        # Check if user is a member of an agency team
        team_member_result = supabase.table('agency_team_members').select(
            'agency_id, role, agencies(id, name, subscription_tier, status)'
        ).eq('user_id', user_id).maybeSingle().execute()

        if team_member_result.data and team_member_result.data.get('agencies'):
            # User is a team member - use agency's subscription tier
            agency_data = team_member_result.data['agencies']
            agency_status = agency_data.get('status', 'active')

            # Only inherit tier if agency is active
            if agency_status == 'active':
                effective_tier = agency_data.get('subscription_tier', 'free')

                logger.info(
                    f"User {user_id} is team member of agency {agency_data['id']} "
                    f"- inheriting tier: {effective_tier}"
                )

                return {
                    'subscription_tier': effective_tier,
                    'is_team_member': True,
                    'agency_id': str(agency_data['id']),
                    'agency_name': agency_data.get('name', ''),
                    'role': team_member_result.data.get('role', 'viewer'),
                    'personal_tier': personal_tier,
                }

        # User is not a team member or agency is not active - use personal tier
        logger.info(f"User {user_id} using personal subscription tier: {personal_tier}")

        return {
            'subscription_tier': personal_tier,
            'is_team_member': False,
            'agency_id': None,
            'agency_name': None,
            'role': None,
            'personal_tier': personal_tier,
        }

    except Exception as e:
        logger.error(f"Error getting effective subscription for user {user_id}: {str(e)}", exc_info=True)
        # On error, return free tier to be safe
        return {
            'subscription_tier': 'free',
            'is_team_member': False,
            'agency_id': None,
            'agency_name': None,
            'role': None,
            'personal_tier': 'free',
            'error': str(e)
        }
