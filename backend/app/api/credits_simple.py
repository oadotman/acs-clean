"""
Simplified User Credits API endpoints for AdCopySurge (No Auth Required - For Testing)
Handles credit balance queries, consumption, and management without authentication
"""

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from typing import Optional
import logging
from datetime import datetime

from ..services.credits import CreditService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/credits", tags=["credits"])

# Pydantic models
class CreditResponse(BaseModel):
    credits: int
    monthly_allowance: int
    bonus_credits: int
    total_used: int
    subscription_tier: str
    last_reset: Optional[datetime]
    is_unlimited: bool

@router.get("/debug/user/{user_id}")
async def debug_get_user_credits(user_id: str):
    """Debug endpoint to get any user's credits - REMOVE IN PRODUCTION"""
    try:
        credit_service = CreditService()
        credits_data = await credit_service.get_user_credits(user_id)
        
        # Check if unlimited plan
        is_unlimited = (
            credits_data.get('subscription_tier') == 'agency_unlimited' or
            credits_data.get('current_credits', 0) >= 999999 or
            credits_data.get('monthly_allowance', 0) == -1
        )
        
        return {
            "user_id": user_id,
            "credits": credits_data.get('current_credits', 0),
            "monthly_allowance": credits_data.get('monthly_allowance', 0),
            "bonus_credits": credits_data.get('bonus_credits', 0),
            "total_used": credits_data.get('total_used', 0),
            "subscription_tier": credits_data.get('subscription_tier', 'free'),
            "last_reset": credits_data.get('last_reset'),
            "is_unlimited": is_unlimited
        }
        
    except Exception as e:
        logger.error(f"Error in debug endpoint for user {user_id}: {e}")
        return {"error": str(e)}

@router.post("/debug/upgrade/{user_id}")
async def debug_upgrade_user_to_unlimited(user_id: str):
    """Debug endpoint to upgrade user to unlimited plan - REMOVE IN PRODUCTION"""
    try:
        credit_service = CreditService()
        result = await credit_service.upgrade_user_subscription(
            user_id=user_id,
            new_tier='agency_unlimited'
        )
        
        return {
            "success": True,
            "message": f"User {user_id} upgraded to unlimited plan",
            "credits": result
        }
        
    except Exception as e:
        logger.error(f"Error upgrading user {user_id}: {e}")
        return {"success": False, "error": str(e)}

@router.post("/debug/check/{user_id}/{operation}")
async def debug_check_credits(user_id: str, operation: str, quantity: int = 1):
    """Debug endpoint to check if user has credits for an operation"""
    try:
        credit_service = CreditService()
        result = await credit_service.check_credits(user_id, operation, quantity)
        
        return {
            "user_id": user_id,
            "operation": operation,
            "quantity": quantity,
            "result": result
        }
        
    except Exception as e:
        logger.error(f"Error checking credits for user {user_id}: {e}")
        return {"error": str(e)}