"""
Credit Management API Endpoints
Provides frontend access to backend credit service
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional

from app.core.database import get_db
from app.auth import get_current_user, require_active_user
from app.models.user import User
from app.services.credit_service import CreditService
from app.core.logging import get_logger

logger = get_logger(__name__)

router = APIRouter()


class CreditBalanceResponse(BaseModel):
    """User credit balance information"""
    credits: int | str  # Can be int or "unlimited"
    monthly_allowance: int | str
    bonus_credits: int
    total_used: int
    subscription_tier: str
    is_unlimited: bool
    last_reset: str


class ConsumeCreditsRequest(BaseModel):
    """Request to consume credits"""
    operation: str
    quantity: int = 1
    description: Optional[str] = None


class ConsumeCreditsResponse(BaseModel):
    """Response from consuming credits"""
    success: bool
    remaining: int | str
    consumed: int
    total_used: Optional[int] = None
    error: Optional[str] = None


@router.get("/balance", response_model=CreditBalanceResponse)
async def get_credit_balance(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_active_user)
):
    """
    Get user's current credit balance.

    ✅ Frontend should call this instead of directly querying Supabase.
    """
    try:
        credit_service = CreditService(db)
        credits_info = credit_service.get_user_credits(current_user.supabase_user_id)

        return CreditBalanceResponse(
            credits=credits_info['credits'],
            monthly_allowance=credits_info['monthly_allowance'],
            bonus_credits=credits_info.get('bonus_credits', 0),
            total_used=credits_info.get('total_used', 0),
            subscription_tier=credits_info.get('subscription_tier', 'free'),
            is_unlimited=credits_info.get('is_unlimited', False),
            last_reset=credits_info.get('last_reset', '').isoformat() if credits_info.get('last_reset') else ''
        )

    except Exception as e:
        logger.error(f"Error fetching credit balance for user {current_user.id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch credit balance: {str(e)}")


@router.post("/consume", response_model=ConsumeCreditsResponse)
async def consume_credits(
    request: ConsumeCreditsRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_active_user)
):
    """
    Consume credits for an operation.

    ⚠️ NOTE: This endpoint is for special cases only.
    Regular analysis operations should use /api/ads/analyze which handles
    credit deduction automatically.
    """
    try:
        credit_service = CreditService(db)

        success, result = credit_service.consume_credits_atomic(
            user_id=current_user.supabase_user_id,
            operation=request.operation,
            quantity=request.quantity,
            description=request.description
        )

        if not success:
            return ConsumeCreditsResponse(
                success=False,
                remaining=result.get('available', 0),
                consumed=0,
                error=result.get('error', 'Failed to consume credits')
            )

        return ConsumeCreditsResponse(
            success=True,
            remaining=result.get('remaining', 0),
            consumed=result.get('consumed', 0),
            total_used=result.get('total_used')
        )

    except Exception as e:
        logger.error(f"Error consuming credits for user {current_user.id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to consume credits: {str(e)}")


@router.get("/history")
async def get_credit_history(
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_active_user)
):
    """
    Get user's credit transaction history.
    """
    try:
        from sqlalchemy import text

        result = db.execute(
            text("""
                SELECT
                    operation,
                    amount,
                    description,
                    created_at
                FROM credit_transactions
                WHERE user_id = :user_id
                ORDER BY created_at DESC
                LIMIT :limit
            """),
            {"user_id": current_user.supabase_user_id, "limit": limit}
        )

        transactions = []
        for row in result:
            transactions.append({
                'operation': row.operation,
                'amount': row.amount,
                'description': row.description,
                'created_at': row.created_at.isoformat() if row.created_at else None
            })

        return {
            'success': True,
            'transactions': transactions,
            'count': len(transactions)
        }

    except Exception as e:
        logger.error(f"Error fetching credit history for user {current_user.id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch credit history: {str(e)}")


@router.get("/costs")
async def get_credit_costs():
    """
    Get credit costs for all operations.
    Public endpoint - no auth required.
    """
    credit_service = CreditService(None)  # Don't need DB for static costs

    return {
        'success': True,
        'costs': credit_service.CREDIT_COSTS,
        'tiers': {
            'free': credit_service.TIER_CREDITS.get('free', 5),
            'growth': credit_service.TIER_CREDITS.get('growth', 100),
            'agency_standard': credit_service.TIER_CREDITS.get('agency_standard', 500),
            'agency_premium': credit_service.TIER_CREDITS.get('agency_premium', 1000),
            'agency_unlimited': 'unlimited'
        }
    }


@router.post("/refund")
async def refund_credits(
    operation: str,
    quantity: int = 1,
    reason: str = "Manual refund",
    db: Session = Depends(get_db),
    current_user: User = Depends(require_active_user)
):
    """
    Refund credits to user.

    ⚠️ This should only be called internally or by admins.
    Regular refunds happen automatically on analysis failure.
    """
    try:
        credit_service = CreditService(db)

        success, result = credit_service.refund_credits(
            user_id=current_user.supabase_user_id,
            operation=operation,
            quantity=quantity,
            reason=reason
        )

        if not success:
            raise HTTPException(status_code=400, detail=result.get('error', 'Refund failed'))

        return {
            'success': True,
            'refunded': result.get('refunded', 0),
            'new_balance': result.get('new_balance', 0),
            'message': f"Refunded {result.get('refunded', 0)} credits"
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error refunding credits for user {current_user.id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to refund credits: {str(e)}")
