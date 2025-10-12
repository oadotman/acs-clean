"""
Authentication status endpoints for health monitoring and configuration verification
"""

from typing import Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

try:
    from app.auth.supabase_enhanced import (
        enhanced_supabase_auth,
        get_auth_status,
        get_optional_current_user,
        get_current_user_or_anonymous
    )
    from app.core.database_enhanced import get_db
    from app.models.user import User
    from app.core.logging import get_logger
except ImportError:
    from app.auth.supabase_enhanced import (
        enhanced_supabase_auth,
        get_auth_status,
        get_optional_current_user,
        get_current_user_or_anonymous
    )
    from app.core.database import get_db
    from app.models.user import User
    from app.core.logging import get_logger

router = APIRouter()
logger = get_logger(__name__)

@router.get("/auth/status", response_model=Dict[str, Any])
async def get_authentication_status():
    """
    Get authentication system status and configuration
    Public endpoint for health checks
    """
    try:
        status = get_auth_status()
        
        # Add additional runtime status
        status.update({
            "authentication_system": "supabase_enhanced",
            "version": "2.0",
            "available_auth_methods": [],
            "status": "healthy"
        })
        
        # Determine available auth methods
        if status["supabase_configured"]:
            status["available_auth_methods"].append("supabase_jwt")
        
        if status["allow_anonymous"]:
            status["available_auth_methods"].append("anonymous")
            
        if not status["available_auth_methods"]:
            status["available_auth_methods"].append("none")
            status["status"] = "degraded"
            
        return status
        
    except Exception as e:
        logger.error(f"Error getting auth status: {e}")
        return {
            "authentication_system": "supabase_enhanced",
            "version": "2.0",
            "status": "error",
            "error": str(e),
            "supabase_configured": False,
            "available_auth_methods": ["none"]
        }

@router.get("/auth/user", response_model=Dict[str, Any])
async def get_current_user_info(
    user: Optional[User] = Depends(get_optional_current_user)
):
    """
    Get current user information
    Returns user info if authenticated, anonymous user info if allowed, or null
    """
    try:
        if not user:
            return {
                "authenticated": False,
                "user": None,
                "auth_method": "none"
            }
        
        # Determine auth method
        auth_method = "anonymous" if user.id == "anonymous" else "supabase"
        
        # Return safe user info
        user_info = {
            "id": user.id,
            "email": user.email,
            "full_name": user.full_name,
            "is_active": user.is_active,
            "email_verified": getattr(user, 'email_verified', False)
        }
        
        # Don't include sensitive info for anonymous users
        if auth_method == "anonymous":
            user_info = {
                "id": "anonymous",
                "email": "anonymous@localhost",
                "full_name": "Anonymous User",
                "is_active": True,
                "email_verified": False
            }
        
        return {
            "authenticated": auth_method != "anonymous",
            "user": user_info,
            "auth_method": auth_method
        }
        
    except Exception as e:
        logger.error(f"Error getting user info: {e}")
        return {
            "authenticated": False,
            "user": None,
            "auth_method": "error",
            "error": str(e)
        }

@router.post("/auth/test", response_model=Dict[str, Any])
async def test_authentication(
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Test authentication functionality
    Returns detailed information about the authentication attempt
    """
    try:
        # Get authentication status
        auth_status = get_auth_status()
        
        # Extract auth header
        auth_header = request.headers.get("Authorization")
        has_auth_header = bool(auth_header and auth_header.startswith("Bearer "))
        
        result = {
            "config": auth_status,
            "request_has_auth_header": has_auth_header,
            "auth_header_preview": f"{auth_header[:20]}..." if auth_header else None,
            "authentication_attempts": []
        }
        
        # Test optional authentication
        try:
            optional_user = await enhanced_supabase_auth.get_optional_user(request, db)
            result["authentication_attempts"].append({
                "method": "optional",
                "success": optional_user is not None,
                "user_type": "anonymous" if optional_user and optional_user.id == "anonymous" else "authenticated",
                "user_id": optional_user.id if optional_user else None,
                "user_email": optional_user.email if optional_user else None
            })
        except Exception as e:
            result["authentication_attempts"].append({
                "method": "optional",
                "success": False,
                "error": str(e)
            })
        
        # Test required authentication with anonymous fallback
        try:
            required_user = await get_current_user_or_anonymous(
                request=request,
                db=db
            )
            result["authentication_attempts"].append({
                "method": "required_with_anonymous",
                "success": required_user is not None,
                "user_type": "anonymous" if required_user and required_user.id == "anonymous" else "authenticated",
                "user_id": required_user.id if required_user else None,
                "user_email": required_user.email if required_user else None
            })
        except Exception as e:
            result["authentication_attempts"].append({
                "method": "required_with_anonymous",
                "success": False,
                "error": str(e)
            })
        
        return result
        
    except Exception as e:
        logger.error(f"Error in auth test: {e}")
        return {
            "error": str(e),
            "config": get_auth_status(),
            "request_has_auth_header": False,
            "authentication_attempts": []
        }

@router.get("/auth/health", response_model=Dict[str, Any])
async def auth_health_check(
    db: Session = Depends(get_db)
):
    """
    Authentication system health check
    Used by the main health endpoint
    """
    try:
        config = enhanced_supabase_auth.config
        
        # Basic configuration check
        health_status = {
            "status": "healthy",
            "checks": {
                "config_loaded": True,
                "supabase_configured": config.is_configured,
                "database_available": True,  # If we got this far, DB is working
                "anonymous_fallback": config.allow_anonymous
            },
            "details": {
                "has_supabase_url": bool(config.supabase_url),
                "has_anon_key": bool(config.supabase_anon_key),
                "has_jwt_secret": bool(config.supabase_jwt_secret),
                "auth_url": config.auth_url,
                "jwks_url": config.jwks_url
            }
        }
        
        # Test JWKS endpoint if configured
        if config.jwks_url:
            try:
                jwks = await enhanced_supabase_auth.verifier.get_jwks()
                health_status["checks"]["jwks_accessible"] = jwks is not None
                health_status["details"]["jwks_keys_count"] = len(jwks.get("keys", [])) if jwks else 0
            except Exception as e:
                health_status["checks"]["jwks_accessible"] = False
                health_status["details"]["jwks_error"] = str(e)
                logger.warning(f"JWKS check failed: {e}")
        
        # Test anonymous user creation if allowed
        if config.allow_anonymous:
            try:
                anon_user = await enhanced_supabase_auth.user_manager.create_anonymous_user()
                health_status["checks"]["anonymous_user_creation"] = anon_user is not None
            except Exception as e:
                health_status["checks"]["anonymous_user_creation"] = False
                health_status["details"]["anonymous_error"] = str(e)
                logger.warning(f"Anonymous user creation failed: {e}")
        
        # Determine overall status
        failed_checks = [k for k, v in health_status["checks"].items() if v is False]
        if failed_checks:
            if config.allow_anonymous and len(failed_checks) <= 2:  # Allow some failures if we have fallback
                health_status["status"] = "degraded"
            else:
                health_status["status"] = "unhealthy"
            
            health_status["failed_checks"] = failed_checks
        
        return health_status
        
    except Exception as e:
        logger.error(f"Auth health check failed: {e}")
        return {
            "status": "error",
            "error": str(e),
            "checks": {
                "config_loaded": False,
                "database_available": False
            }
        }