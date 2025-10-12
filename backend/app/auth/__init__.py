"""
Authentication package for AdCopySurge
Provides unified authentication supporting both legacy JWT and Supabase
"""

from .dependencies import (
    get_current_user,
    get_optional_current_user,
    require_active_user,
    require_verified_email,
    require_subscription_limit,
    require_admin,
    # Backward compatibility aliases
    get_current_user_dep,
    get_optional_current_user_dep,
)

__all__ = [
    "get_current_user",
    "get_optional_current_user", 
    "require_active_user",
    "require_verified_email",
    "require_subscription_limit",
    "require_admin",
    "get_current_user_dep",
    "get_optional_current_user_dep",
]
