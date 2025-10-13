"""
User Credits API endpoints for AdCopySurge
Handles credit balance queries, consumption, and management
"""

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, UUID4
from typing import Optional
import logging
from datetime import datetime

from ..auth.dependencies import get_current_user
from ..services.credits import CreditService
from ..models.user import User

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

class ConsumeCreditsRequest(BaseModel):
    operation: str
    quantity: int = 1

class ConsumeCreditsResponse(BaseModel):
    success: bool
    remaining: Optional[int]
    consumed: int
    error: Optional[str] = None

@router.get("/", response_model=CreditResponse)
async def get_user_credits(current_user: User = Depends(get_current_user)):
    """Get current user's credit balance and details"""
    try:
        logger.info(f"Getting credits for user {current_user.id}")
        
        credit_service = CreditService()
        credits_data = await credit_service.get_user_credits(current_user.id)
        
        # Check if unlimited plan
        is_unlimited = (
            credits_data.get('subscription_tier') == 'agency_unlimited' or
            credits_data.get('current_credits', 0) >= 999999 or
            credits_data.get('monthly_allowance', 0) == -1
        )
        
        return CreditResponse(
            credits=credits_data.get('current_credits', 0),
            monthly_allowance=credits_data.get('monthly_allowance', 0),
            bonus_credits=credits_data.get('bonus_credits', 0),
            total_used=credits_data.get('total_used', 0),
            subscription_tier=credits_data.get('subscription_tier', 'free'),
            last_reset=credits_data.get('last_reset'),
            is_unlimited=is_unlimited
        )
        
    except Exception as e:
        logger.error(f"Error fetching credits for user {current_user.id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch credit information"
        )

@router.post("/consume", response_model=ConsumeCreditsResponse)
async def consume_credits(
    request: ConsumeCreditsRequest,
    current_user: User = Depends(get_current_user)
):
    """Consume credits for an operation"""
    try:
        logger.info(f"User {current_user.id} consuming {request.quantity} credits for {request.operation}")
        
        credit_service = CreditService()
        result = await credit_service.consume_credits(
            user_id=current_user.id,
            operation=request.operation,
            quantity=request.quantity
        )
        
        return ConsumeCreditsResponse(
            success=result.get('success', False),
            remaining=result.get('remaining'),
            consumed=result.get('consumed', 0),
            error=result.get('error')
        )
        
    except Exception as e:
        logger.error(f"Error consuming credits for user {current_user.id}: {e}")
        return ConsumeCreditsResponse(
            success=False,
            remaining=None,
            consumed=0,
            error="Failed to consume credits"
        )

@router.get("/check/{operation}")
async def check_credits_for_operation(
    operation: str,
    quantity: int = 1,
    current_user: User = Depends(get_current_user)
):
    """Check if user has enough credits for an operation without consuming"""
    try:
        credit_service = CreditService()
        has_enough = await credit_service.check_credits(
            user_id=current_user.id,
            operation=operation,
            quantity=quantity
        )
        
        return {
            "has_enough": has_enough.get('has_enough', False),
            "required": has_enough.get('required', 0),
            "available": has_enough.get('available', 0),
            "shortage": has_enough.get('shortage', 0)
        }
        
    except Exception as e:
        logger.error(f"Error checking credits for user {current_user.id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to check credit requirements"
        )

@router.get("/history")
async def get_credit_history(
    limit: int = 50,
    current_user: User = Depends(get_current_user)
):
    """Get user's credit transaction history"""
    try:
        credit_service = CreditService()
        history = await credit_service.get_credit_history(current_user.id, limit)
        
        return {
            "transactions": history,
            "total": len(history)
        }
        
    except Exception as e:
        logger.error(f"Error fetching credit history for user {current_user.id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch credit history"
        )

# Development/testing endpoint - remove in production
@router.get("/debug/user/{user_id}")
async def debug_get_user_credits(user_id: str):
    """Debug endpoint to get any user's credits - REMOVE IN PRODUCTION"""
    try:
        credit_service = CreditService()
        credits_data = await credit_service.get_user_credits(user_id)
        
        return {
            "user_id": user_id,
            "credits": credits_data
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