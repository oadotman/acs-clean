"""
Paddle Billing Service for subscription management using NEW Paddle Billing API.
This replaces the old Paddle Classic API implementation.

Documentation: https://developer.paddle.com/api-reference/overview
"""

import json
import hmac
import hashlib
from typing import Dict, Any, Optional
from datetime import datetime
import requests
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.logging import get_logger
from app.models.user import User, SubscriptionTier

logger = get_logger(__name__)


class PaddleService:
    """Service for handling Paddle Billing API operations"""
    
    def __init__(self, db: Session):
        self.db = db
        self.api_key = settings.PADDLE_API_KEY
        self.vendor_id = settings.PADDLE_VENDOR_ID
        self.webhook_secret = settings.PADDLE_WEBHOOK_SECRET
        self.api_url = settings.PADDLE_API_URL
        self.environment = settings.PADDLE_ENVIRONMENT
        
        # Price ID mapping for all subscription tiers and billing periods
        self.price_id_map = {
            # Growth Plan
            'growth_monthly': settings.PADDLE_GROWTH_MONTHLY_PRICE_ID,
            'growth_yearly': settings.PADDLE_GROWTH_YEARLY_PRICE_ID,
            
            # Agency Standard Plan
            'agency_standard_monthly': settings.PADDLE_AGENCY_STANDARD_MONTHLY_PRICE_ID,
            'agency_standard_yearly': settings.PADDLE_AGENCY_STANDARD_YEARLY_PRICE_ID,
            
            # Agency Premium Plan
            'agency_premium_monthly': settings.PADDLE_AGENCY_PREMIUM_MONTHLY_PRICE_ID,
            'agency_premium_yearly': settings.PADDLE_AGENCY_PREMIUM_YEARLY_PRICE_ID,
            
            # Agency Unlimited Plan
            'agency_unlimited_monthly': settings.PADDLE_AGENCY_UNLIMITED_MONTHLY_PRICE_ID,
            'agency_unlimited_yearly': settings.PADDLE_AGENCY_UNLIMITED_YEARLY_PRICE_ID,
        }
        
        # Reverse mapping: Price ID -> Tier
        self.tier_from_price_id = {v: k for k, v in self.price_id_map.items() if v}
        
        if not self.api_key or not self.vendor_id:
            logger.warning("Paddle credentials not configured. Payment features will not work.")
    
    def _make_request(
        self, 
        method: str, 
        endpoint: str, 
        data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Make authenticated request to Paddle Billing API
        
        Args:
            method: HTTP method (GET, POST, PATCH, DELETE)
            endpoint: API endpoint path (e.g., '/transactions')
            data: Request payload for POST/PATCH requests
            
        Returns:
            API response data
        """
        url = f"{self.api_url}{endpoint}"
        
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, timeout=30)
            elif method == 'POST':
                response = requests.post(url, headers=headers, json=data, timeout=30)
            elif method == 'PATCH':
                response = requests.patch(url, headers=headers, json=data, timeout=30)
            elif method == 'DELETE':
                response = requests.delete(url, headers=headers, timeout=30)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
            
            response.raise_for_status()
            
            result = response.json()
            logger.info(f"Paddle API {method} {endpoint} successful")
            return result
            
        except requests.exceptions.HTTPError as e:
            error_detail = e.response.text if e.response else str(e)
            logger.error(f"Paddle API HTTP error: {error_detail}")
            raise Exception(f"Paddle API error: {error_detail}")
        except requests.exceptions.RequestException as e:
            logger.error(f"Paddle API request failed: {e}")
            raise Exception(f"Payment service unavailable: {e}")
    
    def create_transaction(
        self, 
        price_id: str, 
        user: User,
        billing_period: str = 'monthly',
        success_url: str = None,
        cancel_url: str = None
    ) -> Dict[str, Any]:
        """
        Create a Paddle transaction (checkout session)
        
        Args:
            price_id: Paddle price ID for the subscription
            user: User object
            billing_period: 'monthly' or 'yearly'
            success_url: URL to redirect after successful payment
            cancel_url: URL to redirect if user cancels
            
        Returns:
            Dict with checkout URL and transaction details
        """
        
        # Build transaction payload
        payload = {
            "items": [
                {
                    "price_id": price_id,
                    "quantity": 1
                }
            ],
            "customer": {
                "email": user.email,
                "name": user.full_name if hasattr(user, 'full_name') else user.email
            },
            "custom_data": {
                "user_id": str(user.id),
                "environment": self.environment,
                "billing_period": billing_period
            },
            "checkout": {
                "url": success_url or "https://adcopysurge.com/analysis/new",
                "allowed_payment_methods": ["card", "paypal"]
            }
        }
        
        try:
            result = self._make_request('POST', '/transactions', payload)
            
            # Extract checkout URL from response
            checkout_url = result.get('data', {}).get('checkout', {}).get('url')
            transaction_id = result.get('data', {}).get('id')
            
            if not checkout_url:
                raise Exception("No checkout URL in Paddle response")
            
            return {
                "success": True,
                "checkout_url": checkout_url,
                "transaction_id": transaction_id,
                "data": result.get('data', {})
            }
            
        except Exception as e:
            logger.error(f"Failed to create Paddle transaction: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def create_pay_link(
        self, 
        plan_id: str, 
        user: User, 
        success_redirect: str = None,
        cancel_redirect: str = None
    ) -> Dict[str, Any]:
        """
        Legacy method name for backward compatibility.
        Creates a checkout transaction using the new API.
        """
        # Extract billing period from plan_id
        billing_period = 'yearly' if 'yearly' in plan_id else 'monthly'
        
        # Get actual price ID
        price_id = self.price_id_map.get(plan_id)
        
        if not price_id:
            return {
                "success": False,
                "error": f"Invalid plan ID: {plan_id}"
            }
        
        return self.create_transaction(
            price_id=price_id,
            user=user,
            billing_period=billing_period,
            success_url=success_redirect,
            cancel_url=cancel_redirect
        )
    
    def get_subscription(self, subscription_id: str) -> Dict[str, Any]:
        """
        Get subscription details from Paddle
        
        Args:
            subscription_id: Paddle subscription ID
            
        Returns:
            Subscription data
        """
        try:
            result = self._make_request('GET', f'/subscriptions/{subscription_id}')
            return {
                "success": True,
                "data": result.get('data', {})
            }
        except Exception as e:
            logger.error(f"Failed to get subscription: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def cancel_subscription(self, subscription_id: str) -> Dict[str, Any]:
        """
        Cancel a Paddle subscription
        
        Args:
            subscription_id: Paddle subscription ID
            
        Returns:
            Cancellation result
        """
        if not subscription_id:
            return {"success": False, "error": "No subscription ID provided"}
        
        # In new Paddle API, we cancel by updating the subscription
        payload = {
            "scheduled_change": {
                "action": "cancel",
                "effective_at": "next_billing_period"  # Cancel at end of current period
            }
        }
        
        try:
            result = self._make_request('PATCH', f'/subscriptions/{subscription_id}', payload)
            return {
                "success": True,
                "message": "Subscription will be cancelled at end of billing period",
                "data": result.get('data', {})
            }
        except Exception as e:
            logger.error(f"Failed to cancel subscription: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def update_subscription(
        self, 
        subscription_id: str, 
        new_price_id: str,
        prorate: bool = True
    ) -> Dict[str, Any]:
        """
        Update/modify a Paddle subscription (e.g., upgrade/downgrade)
        
        Args:
            subscription_id: Paddle subscription ID
            new_price_id: New price ID to switch to
            prorate: Whether to prorate the charges
            
        Returns:
            Update result
        """
        if not subscription_id or not new_price_id:
            return {"success": False, "error": "Missing subscription ID or price ID"}
        
        payload = {
            "items": [
                {
                    "price_id": new_price_id,
                    "quantity": 1
                }
            ],
            "proration_billing_mode": "prorated_immediately" if prorate else "full_immediately"
        }
        
        try:
            result = self._make_request('PATCH', f'/subscriptions/{subscription_id}', payload)
            return {
                "success": True,
                "message": "Subscription updated successfully",
                "data": result.get('data', {})
            }
        except Exception as e:
            logger.error(f"Failed to update subscription: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def verify_webhook_signature(self, body: bytes, signature: str) -> bool:
        """
        Verify Paddle webhook signature
        
        Args:
            body: Raw request body bytes
            signature: Signature from Paddle-Signature header
            
        Returns:
            True if signature is valid
        """
        if not self.webhook_secret:
            logger.warning("Paddle webhook secret not configured - cannot verify webhooks")
            return False
        
        try:
            # Paddle signature format: ts=timestamp;h1=signature
            parts = dict(part.split('=') for part in signature.split(';'))
            timestamp = parts.get('ts', '')
            received_signature = parts.get('h1', '')
            
            # Construct signed payload
            signed_payload = f"{timestamp}:{body.decode('utf-8')}"
            
            # Calculate expected signature
            expected_signature = hmac.new(
                self.webhook_secret.encode('utf-8'),
                signed_payload.encode('utf-8'),
                hashlib.sha256
            ).hexdigest()
            
            # Compare signatures
            is_valid = hmac.compare_digest(received_signature, expected_signature)
            
            if not is_valid:
                logger.warning("Webhook signature verification failed")
            
            return is_valid
            
        except Exception as e:
            logger.error(f"Webhook verification error: {e}")
            return False
    
    def process_webhook(self, webhook_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process incoming Paddle webhook event
        
        Args:
            webhook_data: Webhook payload
            
        Returns:
            Processing result
        """
        event_type = webhook_data.get("event_type")
        event_data = webhook_data.get("data", {})
        
        if not event_type:
            return {"success": False, "error": "No event_type in webhook"}
        
        logger.info(f"Processing Paddle webhook: {event_type}")
        
        try:
            # Route to appropriate handler based on event type
            if event_type == "subscription.created":
                return self._handle_subscription_created(event_data)
            elif event_type == "subscription.updated":
                return self._handle_subscription_updated(event_data)
            elif event_type == "subscription.canceled":
                return self._handle_subscription_canceled(event_data)
            elif event_type == "subscription.paused":
                return self._handle_subscription_paused(event_data)
            elif event_type == "subscription.resumed":
                return self._handle_subscription_resumed(event_data)
            elif event_type == "transaction.completed":
                return self._handle_transaction_completed(event_data)
            elif event_type == "transaction.payment_failed":
                return self._handle_payment_failed(event_data)
            else:
                logger.info(f"Unhandled webhook type: {event_type}")
                return {"success": True, "message": f"Webhook received: {event_type}"}
                
        except Exception as e:
            logger.error(f"Webhook processing failed: {e}")
            return {"success": False, "error": str(e)}
    
    def _handle_subscription_created(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle subscription.created webhook"""
        custom_data = data.get("custom_data", {})
        user_id = custom_data.get("user_id")
        
        if not user_id:
            return {"success": False, "error": "No user_id in custom_data"}
        
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            return {"success": False, "error": "User not found"}
        
        # Get subscription details
        subscription_id = data.get("id")
        price_id = data.get("items", [{}])[0].get("price", {}).get("id")
        customer_id = data.get("customer_id")
        
        # Determine tier from price ID
        plan_key = self.tier_from_price_id.get(price_id, 'growth_monthly')
        tier = self._plan_key_to_tier(plan_key)
        
        # Update user
        user.subscription_tier = tier
        user.subscription_active = True
        user.paddle_subscription_id = subscription_id
        user.paddle_plan_id = price_id
        user.paddle_customer_id = customer_id
        user.monthly_analyses = 0  # Reset usage
        
        self.db.commit()
        
        logger.info(f"Subscription created for user {user_id}: {tier}")
        return {"success": True}
    
    def _handle_subscription_updated(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle subscription.updated webhook"""
        subscription_id = data.get("id")
        user = self.db.query(User).filter(User.paddle_subscription_id == subscription_id).first()
        
        if not user:
            return {"success": False, "error": "User not found"}
        
        # Get new plan details
        price_id = data.get("items", [{}])[0].get("price", {}).get("id")
        status = data.get("status")
        
        if price_id:
            plan_key = self.tier_from_price_id.get(price_id, 'growth_monthly')
            new_tier = self._plan_key_to_tier(plan_key)
            user.subscription_tier = new_tier
            user.paddle_plan_id = price_id
        
        # Update subscription status
        user.subscription_active = status in ["active", "trialing"]
        
        self.db.commit()
        
        logger.info(f"Subscription updated for user {user.id}: {status}")
        return {"success": True}
    
    def _handle_subscription_canceled(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle subscription.canceled webhook"""
        subscription_id = data.get("id")
        user = self.db.query(User).filter(User.paddle_subscription_id == subscription_id).first()
        
        if not user:
            return {"success": False, "error": "User not found"}
        
        # Downgrade to free tier
        user.subscription_tier = SubscriptionTier.FREE
        user.subscription_active = False
        user.paddle_subscription_id = None
        user.paddle_plan_id = None
        
        self.db.commit()
        
        logger.info(f"Subscription canceled for user {user.id}")
        return {"success": True}
    
    def _handle_subscription_paused(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle subscription.paused webhook"""
        subscription_id = data.get("id")
        user = self.db.query(User).filter(User.paddle_subscription_id == subscription_id).first()
        
        if not user:
            return {"success": False, "error": "User not found"}
        
        user.subscription_active = False
        self.db.commit()
        
        logger.info(f"Subscription paused for user {user.id}")
        return {"success": True}
    
    def _handle_subscription_resumed(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle subscription.resumed webhook"""
        subscription_id = data.get("id")
        user = self.db.query(User).filter(User.paddle_subscription_id == subscription_id).first()
        
        if not user:
            return {"success": False, "error": "User not found"}
        
        user.subscription_active = True
        self.db.commit()
        
        logger.info(f"Subscription resumed for user {user.id}")
        return {"success": True}
    
    def _handle_transaction_completed(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle transaction.completed webhook"""
        # This is fired when a payment is successful
        custom_data = data.get("custom_data", {})
        user_id = custom_data.get("user_id")
        
        if not user_id:
            # Try to find user by subscription_id if it exists
            subscription_id = data.get("subscription_id")
            if subscription_id:
                user = self.db.query(User).filter(User.paddle_subscription_id == subscription_id).first()
                if user:
                    user.subscription_active = True
                    self.db.commit()
                    logger.info(f"Payment succeeded for user {user.id}")
                    return {"success": True}
            return {"success": False, "error": "No user identifier in transaction"}
        
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            return {"success": False, "error": "User not found"}
        
        # Ensure subscription is active
        user.subscription_active = True
        self.db.commit()
        
        logger.info(f"Transaction completed for user {user_id}")
        return {"success": True}
    
    def _handle_payment_failed(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle transaction.payment_failed webhook"""
        subscription_id = data.get("subscription_id")
        
        if not subscription_id:
            return {"success": True, "message": "No subscription_id in payment failure"}
        
        user = self.db.query(User).filter(User.paddle_subscription_id == subscription_id).first()
        
        if not user:
            return {"success": False, "error": "User not found"}
        
        # Mark subscription as inactive but don't downgrade tier immediately
        # Give user grace period to update payment method
        user.subscription_active = False
        self.db.commit()
        
        logger.warning(f"Payment failed for user {user.id}")
        return {"success": True}
    
    def _plan_key_to_tier(self, plan_key: str) -> SubscriptionTier:
        """
        Convert plan key (e.g., 'growth_monthly') to SubscriptionTier enum
        
        Args:
            plan_key: Plan identifier (tier_period format)
            
        Returns:
            SubscriptionTier enum value
        """
        # Extract tier name from plan_key (remove '_monthly' or '_yearly')
        tier_name = plan_key.replace('_monthly', '').replace('_yearly', '')
        
        tier_mapping = {
            'growth': SubscriptionTier.GROWTH,
            'agency_standard': SubscriptionTier.AGENCY_STANDARD,
            'agency_premium': SubscriptionTier.AGENCY_PREMIUM,
            'agency_unlimited': SubscriptionTier.AGENCY_UNLIMITED,
            # Legacy support
            'basic': SubscriptionTier.GROWTH,
            'pro': SubscriptionTier.AGENCY_UNLIMITED,
        }
        
        return tier_mapping.get(tier_name, SubscriptionTier.FREE)
    
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
            'paddle_plan_id': getattr(user, 'paddle_plan_id', None),
            'paddle_customer_id': getattr(user, 'paddle_customer_id', None)
        }
    
    def _get_subscription_limits(self, tier: SubscriptionTier) -> Dict[str, Any]:
        """Get subscription limits and features for a tier"""
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
        monthly_limit = limits['monthly_limit']
        
        # -1 means unlimited
        can_analyze = (monthly_limit == -1) or (user.monthly_analyses < monthly_limit)
        
        return {
            'current_usage': user.monthly_analyses,
            'limit': monthly_limit,
            'can_analyze': can_analyze,
            'tier': user.subscription_tier.value
        }
