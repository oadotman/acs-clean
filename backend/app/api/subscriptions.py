from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List
from app.core.database import get_db
from app.services.subscription_service import SubscriptionService  # Legacy Stripe service
try:
    from app.services.paddle_service import PaddleService
except ImportError:
    PaddleService = None  # Graceful fallback if Paddle service isn't available yet
from app.auth import get_current_user
from app.models.user import User
from app.core.logging import get_logger

logger = get_logger(__name__)

router = APIRouter()

class SubscriptionPlan(BaseModel):
    tier: str  # free, basic, pro
    price: int
    features: List[str]
    monthly_analysis_limit: int

class SubscriptionUpdate(BaseModel):
    tier: str
    payment_method_id: Optional[str] = None
    billing_period: Optional[str] = 'monthly'  # 'monthly' or 'yearly'

@router.get("/plans")
async def get_subscription_plans():
    """Get available subscription plans"""
    return {
        "plans": [
            {
                "tier": "free",
                "name": "Free",
                "price": 0,
                "period": "forever",
                "monthly_analysis_limit": 5,
                "features": [
                    "5 ad analyses per month",
                    "Basic scoring",
                    "Limited alternatives",
                    "Community support"
                ],
                "popular": False
            },
            {
                "tier": "growth",
                "name": "Growth",
                "price": 39,
                "period": "month",
                "monthly_analysis_limit": 100,
                "features": [
                    "100 analyses/month",
                    "All core features",
                    "Advanced compliance + legal scanning",
                    "47-point psychology analysis",
                    "Competitor benchmarking",
                    "ROI-optimized positioning",
                    "A/B test generator",
                    "Email support"
                ],
                "popular": True
            },
            {
                "tier": "agency_standard",
                "name": "Agency Standard",
                "price": 99,
                "period": "month",
                "monthly_analysis_limit": 500,
                "features": [
                    "500 analyses per month",
                    "50 reports per month",
                    "All core features",
                    "Up to 5 team members",
                    "White-label branding",
                    "Integration with 5000+ tools",
                    "47-point psychology analysis",
                    "Competitor benchmarking",
                    "ROI-optimized positioning",
                    "A/B test generator",
                    "Priority support"
                ],
                "popular": False
            },
            {
                "tier": "agency_premium",
                "name": "Agency Premium",
                "price": 199,
                "period": "month",
                "monthly_analysis_limit": 1000,
                "features": [
                    "1000 analyses per month",
                    "100 reports per month",
                    "All core features",
                    "Up to 10 team members",
                    "White-label branding",
                    "Custom integrations",
                    "Advanced analytics dashboard",
                    "Priority support",
                    "Account manager access",
                    "Custom training sessions",
                    "API access"
                ],
                "popular": False
            },
            {
                "tier": "agency_unlimited",
                "name": "Agency Unlimited",
                "price": 249,
                "period": "month",
                "monthly_analysis_limit": -1,  # -1 indicates unlimited
                "features": [
                    "Unlimited analyses",
                    "Unlimited reports",
                    "All core features",
                    "Up to 20 team members",
                    "White-label branding",
                    "Integration with 5000+ tools",
                    "47-point psychology analysis",
                    "Competitor benchmarking",
                    "ROI-optimized positioning",
                    "A/B test generator",
                    "Priority support",
                    "Dedicated account manager",
                    "Custom onboarding",
                    "Phone support"
                ],
                "popular": False
            }
        ]
    }

@router.get("/current")
async def get_current_subscription(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get user's current subscription details"""
    # Use legacy service temporarily (will switch to Paddle after MVP)
    subscription_service = SubscriptionService(db)
    subscription = subscription_service.get_user_subscription(current_user.id)
    
    return subscription

@router.post("/upgrade")
async def upgrade_subscription(
    subscription_data: SubscriptionUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Upgrade user subscription"""
    subscription_service = SubscriptionService(db)
    result = await subscription_service.upgrade_subscription(
        current_user.id, 
        subscription_data.tier,
        subscription_data.payment_method_id
    )
    
    return result

@router.post("/cancel")
async def cancel_subscription(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Cancel user subscription"""
    subscription_service = SubscriptionService(db)
    result = await subscription_service.cancel_subscription(current_user.id)
    
    return result

# NEW PADDLE ENDPOINTS

@router.post("/paddle/checkout")
async def create_paddle_checkout(
    subscription_data: SubscriptionUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create Paddle checkout link for subscription upgrade"""
    if PaddleService is None:
        raise HTTPException(status_code=503, detail="Paddle service not available")
    
    paddle_service = PaddleService(db)
    
    # Map tier to Paddle plan ID (you'll need to configure these in Paddle dashboard)
    # Support both monthly and yearly billing
    billing_period = subscription_data.billing_period or 'monthly'
    
    plan_mapping = {
        # New 5-tier structure
        "growth": f"growth_{billing_period}",
        "agency_standard": f"agency_standard_{billing_period}",
        "agency_premium": f"agency_premium_{billing_period}",
        "agency_unlimited": f"agency_unlimited_{billing_period}",
        # Legacy support (monthly only for backward compatibility)
        "basic": "growth_monthly",  # Maps to Growth
        "pro": "agency_unlimited_monthly"  # Maps to Agency Unlimited
    }
    
    plan_id = plan_mapping.get(subscription_data.tier)
    if not plan_id:
        raise HTTPException(status_code=400, detail="Invalid subscription tier")
    
    # Create pay link with production URLs
    result = paddle_service.create_pay_link(
        plan_id=plan_id,
        user=current_user,
        success_redirect="https://adcopysurge.com/analysis/new?success=true",
        cancel_redirect="https://adcopysurge.com/pricing"
    )
    
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("error", "Failed to create checkout"))
    
    return {
        "checkout_url": result["pay_link"],
        "expires_at": result["expires_at"]
    }

@router.post("/paddle/webhook")
async def paddle_webhook(
    request: Request,
    db: Session = Depends(get_db)
):
    """Handle Paddle webhooks (New Paddle Billing API)"""
    if PaddleService is None:
        raise HTTPException(status_code=503, detail="Paddle service not available")
        
    try:
        # Get raw body and headers
        body = await request.body()
        signature = request.headers.get("Paddle-Signature", "")  # Note: New Paddle uses "Paddle-Signature" header
        
        paddle_service = PaddleService(db)
        
        # ✅ FIXED: Always verify webhook signature (CRITICAL FOR SECURITY)
        if not signature:
            logger.error("Webhook received without Paddle-Signature header")
            raise HTTPException(status_code=401, detail="Missing webhook signature")

        if not paddle_service.webhook_secret:
            logger.error("PADDLE_WEBHOOK_SECRET not configured - cannot verify webhooks")
            raise HTTPException(status_code=500, detail="Webhook secret not configured")

        if not paddle_service.verify_webhook_signature(body, signature):
            logger.warning("Webhook signature verification failed")
            raise HTTPException(status_code=401, detail="Invalid webhook signature")

        logger.info("✅ Webhook signature verified successfully")
        
        # Parse JSON body (New Paddle API sends JSON)
        import json
        webhook_data = json.loads(body)
        
        # Process the webhook
        result = paddle_service.process_webhook(webhook_data)
        
        if result.get("success"):
            return {"status": "ok"}
        else:
            logger.error(f"Webhook processing failed: {result}")
            return {"status": "error", "message": result.get("error")}
            
    except json.JSONDecodeError as e:
        logger.error(f"Webhook JSON parsing error: {e}")
        raise HTTPException(status_code=400, detail="Invalid JSON in webhook payload")
    except Exception as e:
        logger.error(f"Webhook error: {e}")
        raise HTTPException(status_code=500, detail="Webhook processing failed")

@router.post("/paddle/cancel")
async def cancel_paddle_subscription(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Cancel Paddle subscription"""
    if PaddleService is None:
        raise HTTPException(status_code=503, detail="Paddle service not available")
        
    if not getattr(current_user, 'paddle_subscription_id', None):
        raise HTTPException(status_code=400, detail="No active subscription found")
    
    paddle_service = PaddleService(db)
    result = paddle_service.cancel_subscription(current_user.paddle_subscription_id)
    
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("error", "Failed to cancel subscription"))
    
    return result
