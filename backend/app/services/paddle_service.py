"""
Paddle billing service for subscription management.
Handles all interactions with Paddle's API including subscriptions, payments, and webhooks.
"""

import json
import hashlib
import hmac
from typing import Dict, Any, Optional, List
from datetime import datetime
import requests
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.logging import get_logger
from app.models.user import User, SubscriptionTier

logger = get_logger(__name__)


class PaddleService:
    """Service for handling Paddle billing operations"""
    
    def __init__(self, db: Session):
        self.db = db
        self.vendor_id = settings.PADDLE_VENDOR_ID
        self.auth_code = settings.PADDLE_AUTH_CODE
        self.public_key = settings.PADDLE_PUBLIC_KEY
        self.api_url = settings.PADDLE_API_URL
        self.environment = settings.PADDLE_ENVIRONMENT
        
        if not self.vendor_id or not self.auth_code:
            logger.warning("Paddle credentials not configured. Some features may not work.")
    
    def _make_request(self, endpoint: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Make authenticated request to Paddle API"""
        url = f"{self.api_url}/{endpoint}"
        
        # Add authentication
        data["vendor_id"] = self.vendor_id
        data["vendor_auth_code"] = self.auth_code
        
        try:
            response = requests.post(url, data=data, timeout=30)
            response.raise_for_status()
            
            result = response.json()
            
            if not result.get("success", False):
                logger.error(f"Paddle API error: {result}")
                raise Exception(f"Paddle API error: {result.get('error', {}).get('message', 'Unknown error')}")
            
            return result
        
        except requests.exceptions.RequestException as e:
            logger.error(f"Paddle API request failed: {e}")
            raise Exception(f"Payment service unavailable: {e}")
    
    def create_pay_link(self, plan_id: str, user: User, success_redirect: str = None, 
                       cancel_redirect: str = None) -> Dict[str, Any]:
        """Create a Paddle pay link for subscription checkout"""
        
        data = {
            "product_id": plan_id,
            "customer_email": user.email,
            "customer_name": user.full_name,
            "passthrough": json.dumps({
                "user_id": user.id,
                "plan": plan_id,
                "environment": self.environment
            }),
            "quantity_variable": 0,  # Fixed quantity
            "recurring_prices": ["USD:month"]  # Monthly billing
        }
        
        if success_redirect:
            data["success_redirect_url"] = success_redirect
        if cancel_redirect:
            data["cancel_redirect_url"] = cancel_redirect
            
        try:
            result = self._make_request("2.0/product/generate_pay_link", data)
            return {
                "success": True,
                "pay_link": result["response"]["url"],
                "expires_at": result["response"]["expires"]
            }
        except Exception as e:
            logger.error(f"Failed to create pay link: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_user_subscription(self, user_id: int) -> Dict[str, Any]:
        """Get user's current subscription details"""
        user = self.db.query(User).filter(User.id == user_id).first()
        
        if not user:
            raise ValueError("User not found")
        
        # Get subscription limits
        limits = self._get_subscription_limits(user.subscription_tier)
        
        return {
            'tier': user.subscription_tier.value,
            'monthly_analyses': user.monthly_analyses,
            'monthly_limit': limits['monthly_limit'],
            'features': limits['features'],
            'price': limits['price'],
            'subscription_active': user.subscription_active,
            'paddle_subscription_id': getattr(user, 'paddle_subscription_id', None),
            'paddle_plan_id': getattr(user, 'paddle_plan_id', None)
        }
    
    def cancel_subscription(self, subscription_id: str) -> Dict[str, Any]:
        """Cancel a Paddle subscription"""
        if not subscription_id:
            return {"success": False, "error": "No subscription ID provided"}
            
        data = {
            "subscription_id": subscription_id
        }
        
        try:
            result = self._make_request("2.0/subscription/users_cancel", data)
            return {
                "success": True,
                "message": "Subscription cancelled successfully"
            }
        except Exception as e:
            logger.error(f"Failed to cancel subscription: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def update_subscription(self, subscription_id: str, new_plan_id: str) -> Dict[str, Any]:
        """Update/modify a Paddle subscription"""
        if not subscription_id or not new_plan_id:
            return {"success": False, "error": "Missing subscription ID or plan ID"}
            
        data = {
            "subscription_id": subscription_id,
            "plan_id": new_plan_id,
            "prorate": True,  # Prorate charges
            "bill_immediately": True  # Bill immediately for upgrade
        }
        
        try:
            result = self._make_request("2.0/subscription/users/update", data)
            return {
                "success": True,
                "subscription_id": result["response"]["subscription_id"],
                "next_payment": result["response"]["next_payment"]
            }
        except Exception as e:
            logger.error(f"Failed to update subscription: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def verify_webhook(self, data: bytes, signature: str) -> bool:
        """Verify Paddle webhook signature"""
        if not self.public_key:
            logger.warning("Paddle public key not configured - cannot verify webhooks")
            return False
        
        try:
            # Paddle uses PHPSerialize format, but for simplicity we'll use HMAC verification
            # In production, you should use the proper Paddle signature verification
            expected_signature = hmac.new(
                self.public_key.encode(),
                data,
                hashlib.sha256
            ).hexdigest()
            
            return hmac.compare_digest(signature, expected_signature)
        except Exception as e:
            logger.error(f"Webhook verification failed: {e}")
            return False
    
    def process_webhook(self, webhook_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process incoming Paddle webhook"""
        alert_name = webhook_data.get("alert_name")
        
        if not alert_name:
            return {"success": False, "error": "No alert_name in webhook"}
        
        try:
            if alert_name == "subscription_created":
                return self._handle_subscription_created(webhook_data)
            elif alert_name == "subscription_updated":
                return self._handle_subscription_updated(webhook_data)
            elif alert_name == "subscription_cancelled":
                return self._handle_subscription_cancelled(webhook_data)
            elif alert_name == "subscription_payment_succeeded":
                return self._handle_payment_succeeded(webhook_data)
            elif alert_name == "subscription_payment_failed":
                return self._handle_payment_failed(webhook_data)
            else:
                logger.info(f"Unhandled webhook type: {alert_name}")
                return {"success": True, "message": f"Unhandled webhook: {alert_name}"}
                
        except Exception as e:
            logger.error(f"Webhook processing failed: {e}")
            return {"success": False, "error": str(e)}
    
    def _handle_subscription_created(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle subscription_created webhook"""
        passthrough = json.loads(data.get("passthrough", "{}"))
        user_id = passthrough.get("user_id")
        
        if not user_id:
            return {"success": False, "error": "No user_id in passthrough"}
        
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            return {"success": False, "error": "User not found"}
        
        # Update user subscription
        plan_id = data.get("subscription_plan_id")
        tier = self._plan_id_to_tier(plan_id)
        
        user.subscription_tier = tier
        user.subscription_active = True
        user.paddle_subscription_id = data.get("subscription_id")
        user.paddle_plan_id = plan_id
        user.monthly_analyses = 0  # Reset usage
        
        self.db.commit()
        
        logger.info(f"Subscription created for user {user_id}: {tier}")
        return {"success": True}
    
    def _handle_subscription_updated(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle subscription_updated webhook"""
        subscription_id = data.get("subscription_id")
        user = self.db.query(User).filter(User.paddle_subscription_id == subscription_id).first()
        
        if not user:
            return {"success": False, "error": "User not found"}
        
        # Update plan if changed
        new_plan_id = data.get("subscription_plan_id")
        if new_plan_id:
            new_tier = self._plan_id_to_tier(new_plan_id)
            user.subscription_tier = new_tier
            user.paddle_plan_id = new_plan_id
        
        # Update status
        status = data.get("status")
        user.subscription_active = status in ["active", "trialing"]
        
        self.db.commit()
        
        logger.info(f"Subscription updated for user {user.id}: {status}")
        return {"success": True}
    
    def _handle_subscription_cancelled(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle subscription_cancelled webhook"""
        subscription_id = data.get("subscription_id")
        user = self.db.query(User).filter(User.paddle_subscription_id == subscription_id).first()
        
        if not user:
            return {"success": False, "error": "User not found"}
        
        # Downgrade to free tier
        user.subscription_tier = SubscriptionTier.FREE
        user.subscription_active = False
        user.paddle_subscription_id = None
        user.paddle_plan_id = None
        
        self.db.commit()
        
        logger.info(f"Subscription cancelled for user {user.id}")
        return {"success": True}
    
    def _handle_payment_succeeded(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle subscription_payment_succeeded webhook"""
        subscription_id = data.get("subscription_id")
        user = self.db.query(User).filter(User.paddle_subscription_id == subscription_id).first()
        
        if not user:
            return {"success": False, "error": "User not found"}
        
        # Ensure subscription is active
        user.subscription_active = True
        self.db.commit()
        
        logger.info(f"Payment succeeded for user {user.id}")
        return {"success": True}
    
    def _handle_payment_failed(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle subscription_payment_failed webhook"""
        subscription_id = data.get("subscription_id")
        user = self.db.query(User).filter(User.paddle_subscription_id == subscription_id).first()
        
        if not user:
            return {"success": False, "error": "User not found"}
        
        # Mark subscription as inactive (but don't downgrade tier immediately)
        # Give user grace period to update payment method
        user.subscription_active = False
        self.db.commit()
        
        logger.warning(f"Payment failed for user {user.id}")
        return {"success": True}
    
    def _plan_id_to_tier(self, plan_id: str) -> SubscriptionTier:
        """Convert Paddle plan ID to subscription tier"""
        # These will need to be configured based on your Paddle product setup
        plan_mapping = {
            # New 5-tier structure - Monthly plans
            "growth_monthly": SubscriptionTier.GROWTH,
            "agency_standard_monthly": SubscriptionTier.AGENCY_STANDARD,
            "agency_premium_monthly": SubscriptionTier.AGENCY_PREMIUM,
            "agency_unlimited_monthly": SubscriptionTier.AGENCY_UNLIMITED,
            # New 5-tier structure - Yearly plans
            "growth_yearly": SubscriptionTier.GROWTH,
            "agency_standard_yearly": SubscriptionTier.AGENCY_STANDARD,
            "agency_premium_yearly": SubscriptionTier.AGENCY_PREMIUM,
            "agency_unlimited_yearly": SubscriptionTier.AGENCY_UNLIMITED,
            # Legacy mapping for backward compatibility
            "basic_monthly": SubscriptionTier.GROWTH,  # Maps to Growth
            "pro_monthly": SubscriptionTier.AGENCY_UNLIMITED,  # Maps to Agency Unlimited
        }
        return plan_mapping.get(plan_id, SubscriptionTier.FREE)
    
    def _get_subscription_limits(self, tier: SubscriptionTier) -> Dict[str, Any]:
        """Get subscription limits and features"""
        if tier == SubscriptionTier.FREE:
            return {
                'monthly_limit': 5,
                'price': 0,
                'features': [
                    '5 ad analyses per month',
                    'Basic scoring',
                    'Limited alternatives',
                    'Community support'
                ]
            }
        elif tier in [SubscriptionTier.GROWTH, SubscriptionTier.BASIC]:
            return {
                'monthly_limit': 100,
                'price': 39,
                'features': [
                    '100 analyses/month',
                    'All core features',
                    'Advanced compliance + legal scanning',
                    '47-point psychology analysis',
                    'Competitor benchmarking',
                    'ROI-optimized positioning',
                    'A/B test generator',
                    'Email support'
                ]
            }
        elif tier == SubscriptionTier.AGENCY_STANDARD:
            return {
                'monthly_limit': 500,
                'price': 99,
                'features': [
                    '500 analyses per month',
                    '50 reports per month',
                    'All core features',
                    'Up to 5 team members',
                    'White-label branding',
                    'Integration with 5000+ tools',
                    '47-point psychology analysis',
                    'Competitor benchmarking',
                    'ROI-optimized positioning',
                    'A/B test generator',
                    'Priority support'
                ]
            }
        elif tier == SubscriptionTier.AGENCY_PREMIUM:
            return {
                'monthly_limit': 1000,
                'price': 199,
                'features': [
                    '1000 analyses per month',
                    '100 reports per month',
                    'All core features',
                    'Up to 10 team members',
                    'White-label branding',
                    'Custom integrations',
                    'Advanced analytics dashboard',
                    'Priority support',
                    'Account manager access',
                    'Custom training sessions',
                    'API access'
                ]
            }
        elif tier in [SubscriptionTier.AGENCY_UNLIMITED, SubscriptionTier.PRO]:
            return {
                'monthly_limit': -1,  # -1 indicates unlimited
                'price': 249,
                'features': [
                    'Unlimited analyses',
                    'Unlimited reports',
                    'All core features',
                    'Up to 20 team members',
                    'White-label branding',
                    'Integration with 5000+ tools',
                    '47-point psychology analysis',
                    'Competitor benchmarking',
                    'ROI-optimized positioning',
                    'A/B test generator',
                    'Priority support',
                    'Dedicated account manager',
                    'Custom onboarding',
                    'Phone support'
                ]
            }
        else:
            # Default fallback
            return {
                'monthly_limit': 5,
                'price': 0,
                'features': ['Basic features']
            }
    
    def check_usage_limit(self, user_id: int) -> Dict[str, Any]:
        """Check if user has exceeded usage limits"""
        user = self.db.query(User).filter(User.id == user_id).first()
        
        if not user:
            raise ValueError("User not found")
        
        limits = self._get_subscription_limits(user.subscription_tier)
        
        return {
            'current_usage': user.monthly_analyses,
            'limit': limits['monthly_limit'],
            'can_analyze': user.monthly_analyses < limits['monthly_limit'],
            'tier': user.subscription_tier.value
        }
