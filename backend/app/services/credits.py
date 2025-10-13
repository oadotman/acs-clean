"""
Credit Service for AdCopySurge Backend
Handles all credit-related operations using Supabase with service role permissions
"""

import os
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
from supabase import create_client, Client

logger = logging.getLogger(__name__)

# Credit costs for various operations
CREDIT_COSTS = {
    # Analysis operations
    'BASIC_ANALYSIS': 1,
    'FULL_ANALYSIS': 2,
    'PSYCHOLOGY_ANALYSIS': 3,
    'FURTHER_IMPROVE': 2,
    'BATCH_ANALYSIS_PER_AD': 1,
    
    # Export operations
    'BASIC_EXPORT': 0,  # Free for all users
    'ADVANCED_EXPORT': 1,
    'BULK_EXPORT': 2,
    
    # Report generation
    'BASIC_REPORT': 1,
    'DETAILED_REPORT': 3,
    'WHITE_LABEL_REPORT': 5,
    
    # Logo upload (should be free for unlimited plans)
    'LOGO_UPLOAD': 0,
    
    # API calls
    'API_ANALYSIS_CALL': 1,
    'API_BATCH_CALL': 2,
    
    # Premium features
    'BRAND_VOICE_TRAINING': 5,
    'COMPLIANCE_SCAN': 2,
    'LEGAL_RISK_SCAN': 3
}

class CreditService:
    def __init__(self):
        """Initialize credit service with Supabase client using service role"""
        self.supabase_url = os.getenv('SUPABASE_URL')
        self.supabase_service_key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
        
        if not self.supabase_url or not self.supabase_service_key:
            raise ValueError("Missing Supabase configuration")
            
        # Use service role key to bypass RLS
        self.supabase: Client = create_client(self.supabase_url, self.supabase_service_key)
        logger.info("Credit service initialized with Supabase service role")
    
    async def get_user_credits(self, user_id: str) -> Dict[str, Any]:
        """Get user's current credit information"""
        try:
            logger.info(f"Fetching credits for user: {user_id}")
            
            # Query user_credits table directly with service role (bypasses RLS)
            result = self.supabase.table('user_credits').select('*').eq('user_id', user_id).execute()
            
            if not result.data:
                logger.info(f"No credit record found for user {user_id}, initializing...")
                return await self._initialize_user_credits(user_id)
                
            credits = result.data[0]
            logger.info(f"Retrieved credits for user {user_id}: {credits['current_credits']} credits")
            
            return {
                'current_credits': credits.get('current_credits', 0),
                'monthly_allowance': credits.get('monthly_allowance', 0),
                'bonus_credits': credits.get('bonus_credits', 0),
                'total_used': credits.get('total_used', 0),
                'subscription_tier': credits.get('subscription_tier', 'free'),
                'last_reset': credits.get('last_reset'),
                'created_at': credits.get('created_at'),
                'updated_at': credits.get('updated_at')
            }
            
        except Exception as e:
            logger.error(f"Error fetching credits for user {user_id}: {e}")
            # Return fallback credits
            return {
                'current_credits': 5,
                'monthly_allowance': 5,
                'bonus_credits': 0,
                'total_used': 0,
                'subscription_tier': 'free',
                'last_reset': datetime.utcnow().isoformat(),
                'created_at': datetime.utcnow().isoformat(),
                'updated_at': datetime.utcnow().isoformat()
            }
    
    async def _initialize_user_credits(self, user_id: str, subscription_tier: str = 'free') -> Dict[str, Any]:
        """Initialize credits for a new user"""
        try:
            credit_data = {
                'user_id': user_id,
                'current_credits': 10 if subscription_tier == 'free' else 999999,
                'monthly_allowance': 10 if subscription_tier == 'free' else 999999,
                'bonus_credits': 0,
                'total_used': 0,
                'subscription_tier': subscription_tier,
                'last_reset': datetime.utcnow().isoformat()
            }
            
            result = self.supabase.table('user_credits').insert(credit_data).execute()
            
            if result.data:
                logger.info(f"Initialized credits for new user {user_id}")
                return await self.get_user_credits(user_id)
            else:
                raise Exception("Failed to initialize user credits")
                
        except Exception as e:
            logger.error(f"Error initializing credits for user {user_id}: {e}")
            raise
    
    async def consume_credits(self, user_id: str, operation: str, quantity: int = 1) -> Dict[str, Any]:
        """Consume credits for an operation"""
        try:
            credit_cost = CREDIT_COSTS.get(operation, 0) * quantity
            
            logger.info(f"User {user_id} attempting to consume {credit_cost} credits for {operation}")
            
            if credit_cost == 0:
                logger.info(f"Operation {operation} is free, no credits consumed")
                return {'success': True, 'remaining': None, 'consumed': 0}
            
            # Get current credits
            current_credits = await self.get_user_credits(user_id)
            
            # Check if unlimited plan
            is_unlimited = (
                current_credits['subscription_tier'] == 'agency_unlimited' or
                current_credits['current_credits'] >= 999999 or
                current_credits['monthly_allowance'] == -1
            )
            
            if is_unlimited:
                logger.info(f"User {user_id} has unlimited plan, allowing operation")
                return {'success': True, 'remaining': 'unlimited', 'consumed': 0}
            
            # Check if sufficient credits
            if current_credits['current_credits'] < credit_cost:
                logger.warning(f"User {user_id} has insufficient credits: need {credit_cost}, have {current_credits['current_credits']}")
                return {
                    'success': False,
                    'error': 'Insufficient credits',
                    'required': credit_cost,
                    'available': current_credits['current_credits'],
                    'consumed': 0
                }
            
            # Consume credits
            new_credits = current_credits['current_credits'] - credit_cost
            new_total_used = current_credits['total_used'] + credit_cost
            
            update_result = self.supabase.table('user_credits').update({
                'current_credits': new_credits,
                'total_used': new_total_used,
                'updated_at': datetime.utcnow().isoformat()
            }).eq('user_id', user_id).execute()
            
            if update_result.data:
                # Log the transaction
                await self._log_credit_transaction(user_id, operation, -credit_cost, f"Consumed for {operation}")
                
                logger.info(f"Credits consumed for user {user_id}: -{credit_cost}, remaining: {new_credits}")
                return {
                    'success': True,
                    'remaining': new_credits,
                    'consumed': credit_cost
                }
            else:
                raise Exception("Failed to update credits in database")
                
        except Exception as e:
            logger.error(f"Error consuming credits for user {user_id}: {e}")
            return {'success': False, 'error': str(e), 'consumed': 0}
    
    async def check_credits(self, user_id: str, operation: str, quantity: int = 1) -> Dict[str, Any]:
        """Check if user has enough credits for an operation without consuming"""
        try:
            required = CREDIT_COSTS.get(operation, 0) * quantity
            
            if required == 0:
                return {'has_enough': True, 'required': 0}
            
            current_credits = await self.get_user_credits(user_id)
            
            # Check if unlimited plan
            is_unlimited = (
                current_credits['subscription_tier'] == 'agency_unlimited' or
                current_credits['current_credits'] >= 999999 or
                current_credits['monthly_allowance'] == -1
            )
            
            if is_unlimited:
                return {'has_enough': True, 'required': required, 'remaining': 'unlimited'}
            
            available = current_credits['current_credits']
            has_enough = available >= required
            
            return {
                'has_enough': has_enough,
                'required': required,
                'available': available,
                'shortage': max(0, required - available)
            }
            
        except Exception as e:
            logger.error(f"Error checking credits for user {user_id}: {e}")
            return {'has_enough': False, 'required': 0, 'available': 0, 'shortage': 0}
    
    async def get_credit_history(self, user_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Get user's credit transaction history"""
        try:
            result = self.supabase.table('credit_transactions').select('*').eq('user_id', user_id).order('created_at', desc=True).limit(limit).execute()
            
            return result.data if result.data else []
            
        except Exception as e:
            logger.error(f"Error fetching credit history for user {user_id}: {e}")
            return []
    
    async def _log_credit_transaction(self, user_id: str, operation: str, amount: int, description: str):
        """Log a credit transaction for history tracking"""
        try:
            transaction_data = {
                'user_id': user_id,
                'operation': operation,
                'amount': amount,
                'description': description,
                'created_at': datetime.utcnow().isoformat()
            }
            
            self.supabase.table('credit_transactions').insert(transaction_data).execute()
            
        except Exception as e:
            logger.error(f"Error logging credit transaction: {e}")
            # Don't raise - transaction logging should not fail the main operation
    
    async def upgrade_user_subscription(self, user_id: str, new_tier: str) -> Dict[str, Any]:
        """Upgrade user's subscription tier and adjust credits accordingly"""
        try:
            tier_credits = {
                'free': 10,
                'growth': 100,
                'agency_standard': 500,
                'agency_premium': 1000,
                'agency_unlimited': 999999
            }
            
            new_credits = tier_credits.get(new_tier, 10)
            
            update_result = self.supabase.table('user_credits').update({
                'subscription_tier': new_tier,
                'current_credits': new_credits,
                'monthly_allowance': new_credits,
                'updated_at': datetime.utcnow().isoformat()
            }).eq('user_id', user_id).execute()
            
            if update_result.data:
                await self._log_credit_transaction(
                    user_id, 
                    'SUBSCRIPTION_UPGRADE', 
                    new_credits, 
                    f"Upgraded to {new_tier} plan"
                )
                
                logger.info(f"User {user_id} upgraded to {new_tier} with {new_credits} credits")
                return await self.get_user_credits(user_id)
            else:
                raise Exception("Failed to upgrade user subscription")
                
        except Exception as e:
            logger.error(f"Error upgrading user {user_id} to {new_tier}: {e}")
            raise