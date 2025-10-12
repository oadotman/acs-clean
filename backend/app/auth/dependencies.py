"""
Unified Authentication Dependencies for AdCopySurge
Supports both legacy JWT authentication and new Supabase authentication
"""

from typing import Optional
from fastapi import Depends, HTTPException, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.user import User
from app.services.auth_service import AuthService
from app.middleware.supabase_auth import (
    get_current_user_from_token as get_supabase_user,
    supabase_auth
)
from app.core.logging import get_logger

logger = get_logger(__name__)

# Create HTTPBearer instance for token extraction
security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """
    Unified authentication dependency that supports both legacy JWT and Supabase tokens.
    Tries Supabase first, falls back to legacy JWT if needed.
    """
    if not credentials:
        raise HTTPException(
            status_code=401,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    token = credentials.credentials
    
    # Try Supabase authentication first
    try:
        supabase_payload = await supabase_auth.verify_supabase_token(token)
        if supabase_payload:
            user = await supabase_auth.get_or_create_user(supabase_payload, db)
            if user and user.is_active:
                logger.debug(f"User authenticated via Supabase: {user.email}")
                return user
    except Exception as e:
        logger.debug(f"Supabase auth failed, trying legacy JWT: {e}")
    
    # Fall back to legacy JWT authentication
    try:
        auth_service = AuthService(db)
        user = auth_service.get_current_user(token)
        if user and user.is_active:
            logger.debug(f"User authenticated via legacy JWT: {user.email}")
            return user
    except Exception as e:
        logger.debug(f"Legacy JWT auth failed: {e}")
    
    # Both authentication methods failed
    raise HTTPException(
        status_code=401,
        detail="Invalid authentication token",
        headers={"WWW-Authenticate": "Bearer"},
    )


async def get_optional_current_user(
    request: Request,
    db: Session = Depends(get_db)
) -> Optional[User]:
    """
    Optional authentication dependency that returns None if no valid auth is provided.
    Supports both Supabase and legacy JWT tokens.
    """
    # Check for Authorization header
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        return None
    
    try:
        token = auth_header.split(" ")[1]
        credentials = HTTPAuthorizationCredentials(
            scheme="Bearer",
            credentials=token
        )
        return await get_current_user(credentials, db)
    except HTTPException:
        # Invalid token, but this is optional auth
        return None
    except Exception as e:
        logger.error(f"Optional auth error: {e}")
        return None


async def require_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Dependency that requires an active user account.
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=403,
            detail="User account is disabled"
        )
    return current_user


async def require_verified_email(
    current_user: User = Depends(require_active_user)
) -> User:
    """
    Dependency that requires email verification.
    """
    if not current_user.email_verified:
        raise HTTPException(
            status_code=403,
            detail="Email verification required"
        )
    return current_user


async def check_subscription_limits(user: User, db: Session) -> bool:
    """Check if user can perform an action based on subscription limits"""
    try:
        # Import here to avoid circular imports
        from app.services.paddle_service import PaddleService
        
        paddle_service = PaddleService(db)
        usage_info = paddle_service.check_usage_limit(user.id)
        return usage_info.get('can_analyze', False)
    except Exception as e:
        logger.error(f"Error checking subscription limits: {e}")
        # Default to basic limits check if Paddle service fails
        if user.subscription_tier.value == "free":
            return user.monthly_analyses < 5
        elif user.subscription_tier.value == "basic":
            return user.monthly_analyses < 100
        else:  # pro
            return user.monthly_analyses < 500


async def require_subscription_limit(
    current_user: User = Depends(require_active_user),
    db: Session = Depends(get_db)
) -> User:
    """
    Dependency that enforces subscription limits.
    """
    if not await check_subscription_limits(current_user, db):
        raise HTTPException(
            status_code=403,
            detail="Subscription limit exceeded. Please upgrade your plan."
        )
    return current_user


async def require_admin(
    current_user: User = Depends(require_active_user)
) -> User:
    """
    Dependency that requires admin privileges.
    For now, uses email-based admin check.
    """
    admin_emails = [
        "admin@adcopysurge.com",
        "blog@adcopysurge.com",
        # Add more admin emails as needed
    ]
    
    if current_user.email not in admin_emails:
        raise HTTPException(
            status_code=403,
            detail="Admin access required"
        )
    
    return current_user


# Backward compatibility aliases
get_current_user_dep = get_current_user
get_optional_current_user_dep = get_optional_current_user
