"""
Supabase JWT Authentication Middleware for AdCopySurge
Validates Supabase JWT tokens and maps them to internal User records
"""

import jwt
from typing import Optional, Tuple
from fastapi import HTTPException, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
import httpx
import json
from datetime import datetime, timezone
import asyncio
from functools import lru_cache

from app.core.config import settings
from app.core.database import get_db
from app.models.user import User
from app.core.logging import get_logger

logger = get_logger(__name__)

# Create HTTPBearer instance for token extraction
security = HTTPBearer()


class SupabaseAuth:
    """Supabase JWT authentication handler"""
    
    def __init__(self):
        self.supabase_url = settings.REACT_APP_SUPABASE_URL if hasattr(settings, 'REACT_APP_SUPABASE_URL') else None
        self.supabase_jwt_secret = None
        self._jwks_cache = {}
        self._jwks_cache_time = None
        self._cache_duration = 3600  # 1 hour
        
        if not self.supabase_url:
            logger.warning("Supabase URL not configured. Authentication will not work.")
    
    @lru_cache(maxsize=100)
    async def get_supabase_jwt_secret(self) -> Optional[str]:
        """Get Supabase JWT secret from the project's JWT settings"""
        if not self.supabase_url:
            return None
            
        try:
            # Extract project ref from URL
            project_ref = self.supabase_url.split("//")[1].split(".")[0]
            jwks_url = f"{self.supabase_url}/auth/v1/jwks"
            
            async with httpx.AsyncClient() as client:
                response = await client.get(jwks_url, timeout=10.0)
                response.raise_for_status()
                jwks_data = response.json()
                
                # Cache the JWKS data
                self._jwks_cache = jwks_data
                self._jwks_cache_time = datetime.now()
                
                return jwks_data
                
        except Exception as e:
            logger.error(f"Failed to fetch Supabase JWKS: {e}")
            return None
    
    async def verify_supabase_token(self, token: str) -> Optional[dict]:
        """Verify and decode Supabase JWT token"""
        try:
            # For development, we can use the anon key as secret
            # In production, this should use proper JWKS verification
            if hasattr(settings, 'REACT_APP_SUPABASE_ANON_KEY'):
                # Decode without verification first to get header info
                unverified_header = jwt.get_unverified_header(token)
                unverified_payload = jwt.decode(token, options={"verify_signature": False})
                
                # Basic validation
                if unverified_payload.get('iss') != self.supabase_url + '/auth/v1':
                    logger.warning("Invalid token issuer")
                    return None
                
                # Check if token is expired
                exp = unverified_payload.get('exp')
                if exp and datetime.fromtimestamp(exp, tz=timezone.utc) < datetime.now(timezone.utc):
                    logger.warning("Token expired")
                    return None
                
                # For now, return the unverified payload for development
                # TODO: Implement proper JWKS verification for production
                return unverified_payload
            
            return None
            
        except jwt.ExpiredSignatureError:
            logger.warning("Token expired")
            return None
        except jwt.InvalidTokenError as e:
            logger.warning(f"Invalid token: {e}")
            return None
        except Exception as e:
            logger.error(f"Token verification error: {e}")
            return None
    
    async def get_or_create_user(self, supabase_payload: dict, db: Session) -> Optional[User]:
        """Get or create user from Supabase token payload"""
        try:
            supabase_user_id = supabase_payload.get('sub')
            email = supabase_payload.get('email')
            
            if not supabase_user_id or not email:
                logger.warning("Missing required user data in token")
                return None
            
            # Try to find existing user by Supabase ID
            user = db.query(User).filter(User.supabase_user_id == supabase_user_id).first()
            
            if user:
                # Update email if changed
                if user.email != email:
                    user.email = email
                    db.commit()
                return user
            
            # Try to find by email (for migration of existing users)
            user = db.query(User).filter(User.email == email).first()
            if user and not user.supabase_user_id:
                # Link existing user to Supabase
                user.supabase_user_id = supabase_user_id
                user.email_verified = supabase_payload.get('email_confirmed', False)
                db.commit()
                logger.info(f"Linked existing user {email} to Supabase ID {supabase_user_id}")
                return user
            
            # Create new user
            full_name = (
                supabase_payload.get('user_metadata', {}).get('full_name') or
                supabase_payload.get('user_metadata', {}).get('name') or
                email.split('@')[0]  # Fallback to username part of email
            )
            
            user = User(
                supabase_user_id=supabase_user_id,
                email=email,
                full_name=full_name,
                email_verified=supabase_payload.get('email_confirmed', False),
                is_active=True,
                # Note: hashed_password is None since Supabase handles auth
                hashed_password=None
            )
            
            db.add(user)
            db.commit()
            db.refresh(user)
            
            logger.info(f"Created new user from Supabase: {email}")
            return user
            
        except Exception as e:
            logger.error(f"Error getting/creating user: {e}")
            db.rollback()
            return None


# Global instance
supabase_auth = SupabaseAuth()


async def get_current_user_from_token(
    credentials: HTTPAuthorizationCredentials,
    db: Session
) -> User:
    """
    Extract and validate Supabase JWT token, return corresponding User
    This is the main function to be used as a FastAPI dependency
    """
    if not credentials:
        raise HTTPException(
            status_code=401,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    token = credentials.credentials
    
    # Verify the Supabase token
    supabase_payload = await supabase_auth.verify_supabase_token(token)
    if not supabase_payload:
        raise HTTPException(
            status_code=401,
            detail="Invalid authentication token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Get or create user
    user = await supabase_auth.get_or_create_user(supabase_payload, db)
    if not user:
        raise HTTPException(
            status_code=401,
            detail="Failed to authenticate user"
        )
    
    # Check if user is active
    if not user.is_active:
        raise HTTPException(
            status_code=403,
            detail="User account is disabled"
        )
    
    return user


# Dependency function for FastAPI routes
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = security,
    db: Session = None
) -> User:
    """
    FastAPI dependency to get current authenticated user
    Usage: def my_route(current_user: User = Depends(get_current_user))
    """
    if db is None:
        # This is a bit of a hack, but needed for dependency injection
        # In practice, this should be injected properly
        from app.core.database import SessionLocal
        db = SessionLocal()
        try:
            return await get_current_user_from_token(credentials, db)
        finally:
            db.close()
    else:
        return await get_current_user_from_token(credentials, db)


def get_optional_current_user():
    """
    Optional authentication dependency - returns None if no auth provided
    Usage: def my_route(current_user: Optional[User] = Depends(get_optional_current_user))
    """
    async def optional_auth(
        request: Request,
        db: Session = None
    ) -> Optional[User]:
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
            
            if db is None:
                from app.core.database import SessionLocal
                db = SessionLocal()
                try:
                    return await get_current_user_from_token(credentials, db)
                finally:
                    db.close()
            else:
                return await get_current_user_from_token(credentials, db)
        except HTTPException:
            # Invalid token, but this is optional auth
            return None
        except Exception as e:
            logger.error(f"Optional auth error: {e}")
            return None
    
    return optional_auth


# Subscription limit middleware
async def check_subscription_limits(user: User, db: Session) -> bool:
    """Check if user can perform an action based on subscription limits"""
    from app.services.paddle_service import PaddleService
    
    try:
        paddle_service = PaddleService(db)
        usage_info = paddle_service.check_usage_limit(user.id)
        return usage_info.get('can_analyze', False)
    except Exception as e:
        logger.error(f"Error checking subscription limits: {e}")
        # Default to allowing if there's an error checking limits
        return True


def require_subscription_limit():
    """
    Dependency to enforce subscription limits
    Usage: def my_route(user: User = Depends(require_subscription_limit()))
    """
    async def check_limits(
        user: User = security,
        db: Session = None
    ) -> User:
        if db is None:
            from app.core.database import SessionLocal
            db = SessionLocal()
            try:
                if not await check_subscription_limits(user, db):
                    raise HTTPException(
                        status_code=403,
                        detail="Subscription limit exceeded. Please upgrade your plan."
                    )
                return user
            finally:
                db.close()
        else:
            if not await check_subscription_limits(user, db):
                raise HTTPException(
                    status_code=403,
                    detail="Subscription limit exceeded. Please upgrade your plan."
                )
            return user
    
    return check_limits
