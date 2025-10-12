"""
Enhanced Supabase Authentication Middleware
Centralized configuration, proper JWT verification, and anonymous fallback
"""

import jwt
import httpx
import json
from typing import Optional, Dict, Any, Tuple
from datetime import datetime, timezone
from functools import lru_cache
from contextlib import asynccontextmanager

from fastapi import HTTPException, Request, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

try:
    from app.core.config import settings
    from app.core.database_enhanced import get_db
    from app.models.user import User
    from app.core.logging import get_logger
except ImportError:
    # Fallback imports
    from app.core.config import settings
    from app.core.database import get_db
    from app.models.user import User
    from app.core.logging import get_logger

logger = get_logger(__name__)

class SupabaseConfig:
    """Centralized Supabase configuration"""
    
    def __init__(self):
        # Centralized environment variables
        self.supabase_url = getattr(settings, 'SUPABASE_URL', None) or getattr(settings, 'REACT_APP_SUPABASE_URL', None)
        self.supabase_anon_key = getattr(settings, 'SUPABASE_ANON_KEY', None) or getattr(settings, 'REACT_APP_SUPABASE_ANON_KEY', None) 
        self.supabase_service_role_key = getattr(settings, 'SUPABASE_SERVICE_ROLE_KEY', None)
        self.supabase_jwt_secret = getattr(settings, 'SUPABASE_JWT_SECRET', None)
        self.allow_anonymous = getattr(settings, 'ALLOW_ANON', False)
        
        # Configuration validation
        self.is_configured = bool(self.supabase_url)
        
        if not self.is_configured:
            logger.warning("Supabase not configured. Set SUPABASE_URL and keys in environment.")
        else:
            logger.info(f"Supabase configured: {self.supabase_url}")
            if not self.supabase_anon_key:
                logger.warning("SUPABASE_ANON_KEY not configured - some features may not work")
    
    @property
    def auth_url(self) -> Optional[str]:
        """Get Supabase auth URL"""
        return f"{self.supabase_url}/auth/v1" if self.supabase_url else None
    
    @property 
    def jwks_url(self) -> Optional[str]:
        """Get JWKS URL for token verification"""
        return f"{self.auth_url}/jwks" if self.auth_url else None
    
    def get_project_ref(self) -> Optional[str]:
        """Extract project reference from URL"""
        if not self.supabase_url:
            return None
        try:
            return self.supabase_url.split("//")[1].split(".")[0]
        except Exception:
            return None

class SupabaseJWTVerifier:
    """JWT token verification with JWKS support"""
    
    def __init__(self, config: SupabaseConfig):
        self.config = config
        self._jwks_cache = {}
        self._jwks_cache_time = None
        self._cache_duration = 3600  # 1 hour
    
    async def get_jwks(self) -> Optional[Dict]:
        """Fetch and cache JWKS data"""
        if not self.config.jwks_url:
            return None
        
        # Check cache
        if (self._jwks_cache and self._jwks_cache_time and 
            (datetime.now() - self._jwks_cache_time).seconds < self._cache_duration):
            return self._jwks_cache
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    self.config.jwks_url,
                    timeout=10.0,
                    headers={"apikey": self.config.supabase_anon_key} if self.config.supabase_anon_key else {}
                )
                response.raise_for_status()
                jwks_data = response.json()
                
                # Cache the JWKS data
                self._jwks_cache = jwks_data
                self._jwks_cache_time = datetime.now()
                logger.debug("JWKS data cached successfully")
                
                return jwks_data
                
        except Exception as e:
            logger.error(f"Failed to fetch JWKS: {e}")
            return None
    
    async def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Verify JWT token using JWKS or fallback methods"""
        try:
            # First, decode without verification to get header info
            unverified_header = jwt.get_unverified_header(token)
            unverified_payload = jwt.decode(token, options={"verify_signature": False})
            
            # Validate basic token structure
            if not self._validate_token_structure(unverified_payload):
                return None
            
            # Try JWKS verification first (production)
            if self.config.supabase_jwt_secret:
                try:
                    payload = jwt.decode(
                        token,
                        self.config.supabase_jwt_secret,
                        algorithms=["HS256"],
                        audience="authenticated",
                        issuer=self.config.auth_url
                    )
                    logger.debug("Token verified using JWT secret")
                    return payload
                except jwt.InvalidTokenError as e:
                    logger.warning(f"JWT secret verification failed: {e}")
            
            # Try JWKS verification
            jwks = await self.get_jwks()
            if jwks and "keys" in jwks:
                for key in jwks["keys"]:
                    try:
                        # Convert JWK to PEM for verification
                        public_key = jwt.algorithms.RSAAlgorithm.from_jwk(key)
                        payload = jwt.decode(
                            token,
                            public_key,
                            algorithms=["RS256"],
                            audience="authenticated",
                            issuer=self.config.auth_url
                        )
                        logger.debug("Token verified using JWKS")
                        return payload
                    except jwt.InvalidTokenError:
                        continue
            
            # Development fallback - use unverified payload with validation
            if getattr(settings, 'DEBUG', False) and self._validate_token_structure(unverified_payload):
                logger.warning("Using unverified token in development mode")
                return unverified_payload
            
            logger.warning("Token verification failed - no valid verification method")
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
    
    def _validate_token_structure(self, payload: Dict[str, Any]) -> bool:
        """Validate token structure and basic claims"""
        try:
            # Check required claims
            if not payload.get('sub'):
                logger.warning("Token missing 'sub' claim")
                return False
            
            if not payload.get('email'):
                logger.warning("Token missing 'email' claim")
                return False
            
            # Check issuer if configured
            if self.config.auth_url:
                expected_iss = self.config.auth_url
                if payload.get('iss') != expected_iss:
                    logger.warning(f"Invalid issuer: {payload.get('iss')} != {expected_iss}")
                    return False
            
            # Check expiration
            exp = payload.get('exp')
            if exp and datetime.fromtimestamp(exp, tz=timezone.utc) < datetime.now(timezone.utc):
                logger.warning("Token expired")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Token structure validation error: {e}")
            return False

class SupabaseUserManager:
    """User management for Supabase authentication"""
    
    def __init__(self, config: SupabaseConfig):
        self.config = config
    
    async def get_or_create_user(self, token_payload: Dict[str, Any], db: Session) -> Optional[User]:
        """Get or create user from Supabase token payload"""
        try:
            supabase_user_id = token_payload.get('sub')
            email = token_payload.get('email')
            
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
                user.email_verified = token_payload.get('email_confirmed', False)
                db.commit()
                logger.info(f"Linked existing user {email} to Supabase ID {supabase_user_id}")
                return user
            
            # Create new user
            full_name = self._extract_full_name(token_payload, email)
            
            user = User(
                supabase_user_id=supabase_user_id,
                email=email,
                full_name=full_name,
                email_verified=token_payload.get('email_confirmed', False),
                is_active=True,
                hashed_password=None  # Supabase handles auth
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
    
    def _extract_full_name(self, token_payload: Dict[str, Any], email: str) -> str:
        """Extract full name from token payload"""
        user_metadata = token_payload.get('user_metadata', {})
        app_metadata = token_payload.get('app_metadata', {})
        
        # Try various name fields
        name_candidates = [
            user_metadata.get('full_name'),
            user_metadata.get('name'),
            app_metadata.get('full_name'),
            app_metadata.get('name'),
            f"{user_metadata.get('first_name', '')} {user_metadata.get('last_name', '')}".strip(),
            email.split('@')[0]  # Fallback to username part of email
        ]
        
        for candidate in name_candidates:
            if candidate and candidate.strip():
                return candidate.strip()
        
        return email.split('@')[0]
    
    async def create_anonymous_user(self) -> Optional[User]:
        """Create an anonymous user for unauthenticated access"""
        try:
            # Create a minimal anonymous user object (not saved to DB)
            return User(
                id="anonymous",
                email="anonymous@localhost",
                full_name="Anonymous User",
                is_active=True,
                email_verified=False,
                supabase_user_id=None,
                hashed_password=None
            )
        except Exception as e:
            logger.error(f"Error creating anonymous user: {e}")
            return None

class EnhancedSupabaseAuth:
    """Main Supabase authentication class"""
    
    def __init__(self):
        self.config = SupabaseConfig()
        self.verifier = SupabaseJWTVerifier(self.config)
        self.user_manager = SupabaseUserManager(self.config)
        self.security = HTTPBearer(auto_error=False)
    
    async def authenticate_user(
        self, 
        credentials: Optional[HTTPAuthorizationCredentials], 
        db: Session,
        allow_anonymous: bool = True
    ) -> Optional[User]:
        """
        Main authentication method
        Returns User object or None based on credentials and configuration
        """
        # No credentials provided
        if not credentials:
            if allow_anonymous and self.config.allow_anonymous:
                logger.debug("No credentials, creating anonymous user")
                return await self.user_manager.create_anonymous_user()
            return None
        
        # Supabase not configured
        if not self.config.is_configured:
            logger.warning("Supabase not configured, cannot authenticate")
            if allow_anonymous and self.config.allow_anonymous:
                return await self.user_manager.create_anonymous_user()
            return None
        
        # Verify token
        token = credentials.credentials
        token_payload = await self.verifier.verify_token(token)
        
        if not token_payload:
            logger.debug("Token verification failed")
            if allow_anonymous and self.config.allow_anonymous:
                return await self.user_manager.create_anonymous_user()
            return None
        
        # Get or create user from token
        user = await self.user_manager.get_or_create_user(token_payload, db)
        
        if not user:
            logger.warning("Failed to get/create user from token")
            if allow_anonymous and self.config.allow_anonymous:
                return await self.user_manager.create_anonymous_user()
            return None
        
        # Check if user is active
        if not user.is_active:
            logger.warning(f"User {user.email} is not active")
            return None
        
        return user
    
    async def get_current_user(
        self,
        credentials: Optional[HTTPAuthorizationCredentials] = None,
        db: Session = None,
        allow_anonymous: bool = False
    ) -> User:
        """
        FastAPI dependency to get current authenticated user
        Raises HTTPException if authentication fails and anonymous not allowed
        """
        if not db:
            raise RuntimeError("Database session required")
        
        user = await self.authenticate_user(credentials, db, allow_anonymous)
        
        if not user:
            raise HTTPException(
                status_code=401,
                detail="Authentication required",
                headers={"WWW-Authenticate": "Bearer"}
            )
        
        return user
    
    async def get_optional_user(
        self,
        request: Request,
        db: Session = None
    ) -> Optional[User]:
        """
        Optional authentication - returns None if no valid auth provided
        """
        if not db:
            raise RuntimeError("Database session required")
        
        # Extract credentials from request
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            if self.config.allow_anonymous:
                return await self.user_manager.create_anonymous_user()
            return None
        
        try:
            token = auth_header.split(" ")[1]
            credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials=token)
            return await self.authenticate_user(credentials, db, allow_anonymous=True)
        except Exception as e:
            logger.debug(f"Optional auth failed: {e}")
            if self.config.allow_anonymous:
                return await self.user_manager.create_anonymous_user()
            return None

# Global instance
enhanced_supabase_auth = EnhancedSupabaseAuth()

# FastAPI Dependencies
async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(HTTPBearer(auto_error=False)),
    db: Session = Depends(get_db)
) -> User:
    """
    FastAPI dependency for required authentication
    """
    return await enhanced_supabase_auth.get_current_user(credentials, db, allow_anonymous=False)

async def get_current_user_or_anonymous(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(HTTPBearer(auto_error=False)),
    db: Session = Depends(get_db)
) -> User:
    """
    FastAPI dependency that allows anonymous users when configured
    """
    return await enhanced_supabase_auth.get_current_user(credentials, db, allow_anonymous=True)

async def get_optional_current_user(
    request: Request,
    db: Session = Depends(get_db)
) -> Optional[User]:
    """
    FastAPI dependency for optional authentication
    """
    return await enhanced_supabase_auth.get_optional_user(request, db)

# Configuration check function
def get_auth_status() -> Dict[str, Any]:
    """Get authentication configuration status"""
    config = enhanced_supabase_auth.config
    return {
        "supabase_configured": config.is_configured,
        "supabase_url": config.supabase_url,
        "has_anon_key": bool(config.supabase_anon_key),
        "has_service_role_key": bool(config.supabase_service_role_key),
        "has_jwt_secret": bool(config.supabase_jwt_secret),
        "allow_anonymous": config.allow_anonymous
    }