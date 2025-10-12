"""
Enhanced Security Authentication Middleware for AdCopySurge
Implements secure Supabase-only authentication with comprehensive validation
"""

from typing import Optional, Dict, Any
from datetime import datetime, timedelta
import jwt
import httpx
from fastapi import HTTPException, Depends, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
import redis
import json
import hashlib
import logging

from app.core.database import get_db
from app.core.config import settings
from app.models.user import User

logger = logging.getLogger(__name__)

# Initialize Redis for session management (if available)
try:
    redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)
except Exception as e:
    logger.warning(f"Redis not available for session management: {e}")
    redis_client = None

class SecurityAuthMiddleware:
    """Enhanced security authentication middleware"""
    
    def __init__(self):
        self.security = HTTPBearer()
        self.session_timeout = 3600  # 1 hour
        self.max_failed_attempts = 5
        self.lockout_duration = 900  # 15 minutes
    
    async def verify_supabase_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Verify Supabase JWT token with enhanced security"""
        try:
            # Decode without verification first to get header
            unverified_header = jwt.get_unverified_header(token)
            unverified_payload = jwt.decode(token, options={"verify_signature": False})
            
            # Validate token structure
            required_fields = ['sub', 'aud', 'exp', 'iat', 'iss']
            for field in required_fields:
                if field not in unverified_payload:
                    logger.warning(f"Token missing required field: {field}")
                    return None
            
            # Validate issuer
            if unverified_payload.get('iss') != settings.SUPABASE_URL:
                logger.warning("Token issuer mismatch")
                return None
            
            # Validate audience
            if unverified_payload.get('aud') != 'authenticated':
                logger.warning("Token audience invalid")
                return None
            
            # Verify token signature
            payload = jwt.decode(
                token,
                settings.SUPABASE_JWT_SECRET,
                algorithms=['HS256'],
                audience='authenticated',
                issuer=settings.SUPABASE_URL
            )
            
            # Additional expiration check
            exp_timestamp = payload.get('exp')
            if exp_timestamp and datetime.utcnow().timestamp() > exp_timestamp:
                logger.warning("Token expired")
                return None
            
            # Check if token is blacklisted
            if await self._is_token_blacklisted(token):
                logger.warning("Token is blacklisted")
                return None
            
            return payload
            
        except jwt.ExpiredSignatureError:
            logger.warning("Token expired")
            return None
        except jwt.InvalidTokenError as e:
            logger.warning(f"Invalid token: {e}")
            return None
        except Exception as e:
            logger.error(f"Token verification error: {e}")
            return None
    
    async def _is_token_blacklisted(self, token: str) -> bool:
        """Check if token is blacklisted"""
        if not redis_client:
            return False
        
        try:
            token_hash = hashlib.sha256(token.encode()).hexdigest()[:16]
            return bool(await redis_client.get(f"blacklist:{token_hash}"))
        except Exception as e:
            logger.error(f"Error checking token blacklist: {e}")
            return False
    
    async def blacklist_token(self, token: str, expiry_seconds: int = 3600):
        """Add token to blacklist"""
        if not redis_client:
            logger.warning("Cannot blacklist token: Redis unavailable")
            return
        
        try:
            token_hash = hashlib.sha256(token.encode()).hexdigest()[:16]
            await redis_client.setex(f"blacklist:{token_hash}", expiry_seconds, "1")
            logger.info(f"Token blacklisted: {token_hash}")
        except Exception as e:
            logger.error(f"Error blacklisting token: {e}")
    
    async def get_or_create_user_from_payload(self, payload: Dict[str, Any], db: Session) -> Optional[User]:
        """Get or create user from Supabase payload with validation"""
        try:
            user_id = payload.get('sub')
            email = payload.get('email')
            
            if not user_id or not email:
                logger.warning("Token missing user ID or email")
                return None
            
            # Try to find existing user
            user = db.query(User).filter(User.supabase_id == user_id).first()
            
            if not user:
                # Create new user with secure defaults
                user = User(
                    id=user_id,
                    supabase_id=user_id,
                    email=email,
                    email_verified=payload.get('email_confirmed', False),
                    is_active=True,
                    subscription_tier="free",
                    monthly_analyses=0,
                    created_at=datetime.utcnow()
                )
                db.add(user)
                db.commit()
                db.refresh(user)
                logger.info(f"Created new user: {email}")
            
            # Update last login
            user.last_login = datetime.utcnow()
            db.commit()
            
            return user
            
        except Exception as e:
            logger.error(f"Error getting/creating user: {e}")
            db.rollback()
            return None
    
    async def validate_session(self, user_id: str, ip_address: str, user_agent: str) -> bool:
        """Validate user session with security checks"""
        if not redis_client:
            return True  # Skip session validation if Redis unavailable
        
        try:
            session_key = f"session:{user_id}"
            session_data = await redis_client.get(session_key)
            
            if not session_data:
                # Create new session
                session_info = {
                    "ip_address": ip_address,
                    "user_agent": user_agent,
                    "created_at": datetime.utcnow().isoformat(),
                    "last_activity": datetime.utcnow().isoformat()
                }
                await redis_client.setex(session_key, self.session_timeout, json.dumps(session_info))
                return True
            
            session_info = json.loads(session_data)
            
            # Check for suspicious activity (IP change)
            if session_info.get("ip_address") != ip_address:
                logger.warning(f"IP address change detected for user {user_id}: {session_info.get('ip_address')} -> {ip_address}")
                # Allow but log - could implement stricter controls here
            
            # Update session activity
            session_info["last_activity"] = datetime.utcnow().isoformat()
            await redis_client.setex(session_key, self.session_timeout, json.dumps(session_info))
            
            return True
            
        except Exception as e:
            logger.error(f"Session validation error: {e}")
            return True  # Fail open for availability
    
    async def log_failed_auth_attempt(self, ip_address: str, user_agent: str):
        """Log and track failed authentication attempts"""
        try:
            # Rate limiting for failed attempts
            if redis_client:
                attempt_key = f"auth_fails:{ip_address}"
                attempts = await redis_client.incr(attempt_key)
                await redis_client.expire(attempt_key, self.lockout_duration)
                
                if attempts >= self.max_failed_attempts:
                    logger.warning(f"IP {ip_address} locked out after {attempts} failed attempts")
                    # Could implement IP blocking here
            
            logger.warning(f"Failed authentication attempt from {ip_address}: {user_agent}")
            
        except Exception as e:
            logger.error(f"Error logging failed auth attempt: {e}")

# Create global instance
security_auth = SecurityAuthMiddleware()

async def get_current_user_secure(
    request: Request,
    credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer()),
    db: Session = Depends(get_db)
) -> User:
    """
    Secure authentication dependency with comprehensive validation
    """
    if not credentials:
        await security_auth.log_failed_auth_attempt(
            request.client.host, 
            request.headers.get("user-agent", "unknown")
        )
        raise HTTPException(
            status_code=401,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    token = credentials.credentials
    ip_address = request.client.host
    user_agent = request.headers.get("user-agent", "unknown")
    
    # Verify Supabase JWT token
    payload = await security_auth.verify_supabase_token(token)
    if not payload:
        await security_auth.log_failed_auth_attempt(ip_address, user_agent)
        raise HTTPException(
            status_code=401,
            detail="Invalid authentication token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Get or create user
    user = await security_auth.get_or_create_user_from_payload(payload, db)
    if not user:
        await security_auth.log_failed_auth_attempt(ip_address, user_agent)
        raise HTTPException(
            status_code=401,
            detail="User validation failed"
        )
    
    # Check if user is active
    if not user.is_active:
        logger.warning(f"Inactive user attempted login: {user.email}")
        raise HTTPException(
            status_code=403,
            detail="User account is disabled"
        )
    
    # Validate session
    session_valid = await security_auth.validate_session(user.id, ip_address, user_agent)
    if not session_valid:
        raise HTTPException(
            status_code=401,
            detail="Session validation failed"
        )
    
    return user

async def get_current_user_optional_secure(
    request: Request,
    db: Session = Depends(get_db)
) -> Optional[User]:
    """Optional authentication with security logging"""
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        return None
    
    try:
        token = auth_header.split(" ")[1]
        credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials=token)
        return await get_current_user_secure(request, credentials, db)
    except HTTPException:
        return None
    except Exception as e:
        logger.error(f"Optional auth error: {e}")
        return None

# Export the main authentication dependency
get_current_user = get_current_user_secure