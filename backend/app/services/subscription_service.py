from sqlalchemy.orm import Session
from typing import Dict, Any, Optional
from app.models.user import User, SubscriptionTier
from app.core.config import settings
# import stripe  # Temporarily disabled for MVP

class SubscriptionService:
    """Handles subscription management and payments"""
    
    def __init__(self, db: Session):
        self.db = db
        # Temporarily disabled for MVP - will add payment processing back
        # if settings.STRIPE_SECRET_KEY:
        #     stripe.api_key = settings.STRIPE_SECRET_KEY
    
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
            'stripe_customer_id': user.stripe_customer_id
        }
    
    async def upgrade_subscription(self, user_id: int, new_tier: str, 
                                 payment_method_id: Optional[str] = None) -> Dict[str, Any]:
        """Upgrade user subscription"""
        user = self.db.query(User).filter(User.id == user_id).first()
        
        if not user:
            raise ValueError("User not found")
        
        # Convert string to enum
        tier_enum = SubscriptionTier(new_tier)
        
        # If upgrading to paid tier, handle Stripe payment
        if tier_enum != SubscriptionTier.FREE and settings.STRIPE_SECRET_KEY:
            try:
                # Create or update Stripe customer
                if not user.stripe_customer_id:
                    customer = stripe.Customer.create(
                        email=user.email,
                        name=user.full_name,
                        payment_method=payment_method_id
                    )
                    user.stripe_customer_id = customer.id
                
                # Create subscription
                price_id = self._get_stripe_price_id(tier_enum)
                subscription = stripe.Subscription.create(
                    customer=user.stripe_customer_id,
                    items=[{'price': price_id}],
                    payment_behavior='default_incomplete',
                    expand=['latest_invoice.payment_intent'],
                )
                
                # Update user subscription
                user.subscription_tier = tier_enum
                user.subscription_active = True
                user.monthly_analyses = 0  # Reset count on upgrade
                
                self.db.commit()
                
                return {
                    'success': True,
                    'subscription_id': subscription.id,
                    'client_secret': subscription.latest_invoice.payment_intent.client_secret
                }
            
            except stripe.error.StripeError as e:
                return {
                    'success': False,
                    'error': str(e)
                }
        else:
            # Free tier or no Stripe configured
            user.subscription_tier = tier_enum
            user.monthly_analyses = 0
            self.db.commit()
            
            return {
                'success': True,
                'message': f'Subscription updated to {tier_enum.value}'
            }
    
    async def cancel_subscription(self, user_id: int) -> Dict[str, Any]:
        """Cancel user subscription"""
        user = self.db.query(User).filter(User.id == user_id).first()
        
        if not user:
            raise ValueError("User not found")
        
        # Cancel Stripe subscription if exists
        if user.stripe_customer_id and settings.STRIPE_SECRET_KEY:
            try:
                # List and cancel active subscriptions
                subscriptions = stripe.Subscription.list(
                    customer=user.stripe_customer_id,
                    status='active'
                )
                
                for subscription in subscriptions.data:
                    stripe.Subscription.cancel(subscription.id)
                
            except stripe.error.StripeError as e:
                return {
                    'success': False,
                    'error': str(e)
                }
        
        # Update user to free tier
        user.subscription_tier = SubscriptionTier.FREE
        user.subscription_active = False
        self.db.commit()
        
        return {
            'success': True,
            'message': 'Subscription cancelled successfully'
        }
    
    def _get_subscription_limits(self, tier: SubscriptionTier) -> Dict[str, Any]:
        """Get subscription limits and features"""
        if tier == SubscriptionTier.FREE:
            return {
                'monthly_limit': 5,
                'price': 0,
                'features': [
                    '5 ad analyses per month',
                    'Basic scoring',
                    'Limited alternatives'
                ]
            }
        elif tier == SubscriptionTier.BASIC:
            return {
                'monthly_limit': 100,
                'price': settings.BASIC_PLAN_PRICE,
                'features': [
                    '100 ad analyses per month',
                    'Full AI analysis',
                    'Unlimited alternatives',
                    'Competitor benchmarking',
                    'PDF reports'
                ]
            }
        elif tier == SubscriptionTier.PRO:
            return {
                'monthly_limit': 500,
                'price': settings.PRO_PLAN_PRICE,
                'features': [
                    '500 ad analyses per month',
                    'Premium AI models',
                    'Advanced competitor analysis',
                    'White-label reports',
                    'API access',
                    'Priority support'
                ]
            }
    
    def _get_stripe_price_id(self, tier: SubscriptionTier) -> str:
        """Get Stripe price ID for subscription tier"""
        # These would be configured in Stripe dashboard
        price_ids = {
            SubscriptionTier.BASIC: 'price_basic_monthly',
            SubscriptionTier.PRO: 'price_pro_monthly'
        }
        return price_ids.get(tier, '')
    
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
