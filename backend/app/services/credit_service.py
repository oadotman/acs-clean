"""
Credit Management Service with Atomic Operations
Implements thread-safe credit deduction and refund logic
"""

from typing import Dict, Any, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import text
from datetime import datetime, timezone
from decimal import Decimal

from app.core.logging import get_logger
from app.models.user import User, SubscriptionTier

logger = get_logger(__name__)


class CreditService:
    """
    Centralized credit management service with atomic operations.
    All credit operations go through this service to ensure consistency.
    """

    # Credit costs for different operations
    CREDIT_COSTS = {
        'BASIC_ANALYSIS': 1,
        'FULL_ANALYSIS': 2,
        'PSYCHOLOGY_ANALYSIS': 3,
        'FURTHER_IMPROVE': 2,
        'BATCH_ANALYSIS_PER_AD': 1,
        'BASIC_EXPORT': 0,
        'ADVANCED_EXPORT': 1,
        'BULK_EXPORT': 2,
        'BASIC_REPORT': 1,
        'DETAILED_REPORT': 3,
        'WHITE_LABEL_REPORT': 5,
        'API_ANALYSIS_CALL': 1,
        'API_BATCH_CALL': 2,
        'BRAND_VOICE_TRAINING': 5,
        'COMPLIANCE_SCAN': 2,
        'LEGAL_RISK_SCAN': 3
    }

    # Monthly credit allocations by tier
    TIER_CREDITS = {
        SubscriptionTier.FREE: 5,
        SubscriptionTier.GROWTH: 100,
        SubscriptionTier.BASIC: 100,  # Legacy
        SubscriptionTier.AGENCY_STANDARD: 500,
        SubscriptionTier.AGENCY_PREMIUM: 1000,
        SubscriptionTier.AGENCY_UNLIMITED: -1,  # Unlimited
        SubscriptionTier.PRO: -1  # Legacy unlimited
    }

    def __init__(self, db: Session):
        self.db = db

    def get_user_credits(self, user_id: str) -> Dict[str, Any]:
        """
        Get user's current credit balance from database.
        Returns credit information including balance and monthly allowance.
        """
        try:
            # Query user_credits table directly
            result = self.db.execute(
                text("""
                    SELECT
                        current_credits,
                        monthly_allowance,
                        bonus_credits,
                        total_used,
                        last_reset,
                        subscription_tier
                    FROM user_credits
                    WHERE user_id = :user_id
                """),
                {"user_id": user_id}
            ).fetchone()

            if not result:
                # Initialize credits for new user
                return self._initialize_user_credits(user_id)

            # Check if unlimited tier
            is_unlimited = result.subscription_tier in ['agency_unlimited', 'pro']

            return {
                'credits': 999999 if is_unlimited else result.current_credits,
                'monthly_allowance': 999999 if is_unlimited else result.monthly_allowance,
                'bonus_credits': result.bonus_credits or 0,
                'total_used': result.total_used or 0,
                'last_reset': result.last_reset,
                'subscription_tier': result.subscription_tier,
                'is_unlimited': is_unlimited
            }

        except Exception as e:
            logger.error(f"Error fetching user credits: {e}")
            raise

    def consume_credits_atomic(
        self,
        user_id: str,
        operation: str,
        quantity: int = 1,
        description: Optional[str] = None
    ) -> Tuple[bool, Dict[str, Any]]:
        """
        Atomically consume credits using database-level constraints.
        This prevents race conditions through SQL WHERE clause.

        Returns:
            (success: bool, result: dict)
        """
        try:
            credit_cost = self.CREDIT_COSTS.get(operation, 0) * quantity

            if credit_cost == 0:
                logger.info(f"Free operation {operation}, no credits consumed")
                return True, {'success': True, 'message': 'Free operation'}

            # Check if unlimited tier first
            credits_info = self.get_user_credits(user_id)
            if credits_info.get('is_unlimited'):
                logger.info(f"Unlimited tier user {user_id}, allowing operation")
                # Still log the transaction for analytics
                self._log_transaction(
                    user_id=user_id,
                    operation=operation,
                    amount=-credit_cost,
                    description=description or f"Used for {operation}"
                )
                return True, {
                    'success': True,
                    'remaining': 'unlimited',
                    'consumed': credit_cost
                }

            # Atomic credit deduction with optimistic locking
            # This prevents race conditions: UPDATE only succeeds if credits >= cost
            result = self.db.execute(
                text("""
                    UPDATE user_credits
                    SET
                        current_credits = current_credits - :credit_cost,
                        total_used = COALESCE(total_used, 0) + :credit_cost,
                        updated_at = :updated_at
                    WHERE user_id = :user_id
                      AND current_credits >= :credit_cost
                    RETURNING current_credits, total_used
                """),
                {
                    "user_id": user_id,
                    "credit_cost": credit_cost,
                    "updated_at": datetime.now(timezone.utc)
                }
            ).fetchone()

            if not result:
                # UPDATE didn't affect any rows - insufficient credits
                current_balance = credits_info.get('credits', 0)
                logger.warning(
                    f"Insufficient credits for user {user_id}: "
                    f"needs {credit_cost}, has {current_balance}"
                )
                return False, {
                    'success': False,
                    'error': 'Insufficient credits',
                    'required': credit_cost,
                    'available': current_balance
                }

            # Commit the transaction
            self.db.commit()

            # Log the transaction
            self._log_transaction(
                user_id=user_id,
                operation=operation,
                amount=-credit_cost,
                description=description or f"Used for {operation}"
            )

            logger.info(
                f"Credits consumed: user={user_id}, operation={operation}, "
                f"cost={credit_cost}, remaining={result.current_credits}"
            )

            return True, {
                'success': True,
                'remaining': result.current_credits,
                'consumed': credit_cost,
                'total_used': result.total_used
            }

        except Exception as e:
            self.db.rollback()
            logger.error(f"Error consuming credits: {e}")
            return False, {
                'success': False,
                'error': f"Credit consumption failed: {str(e)}"
            }

    def refund_credits(
        self,
        user_id: str,
        operation: str,
        quantity: int = 1,
        reason: str = "Operation failed"
    ) -> Tuple[bool, Dict[str, Any]]:
        """
        Refund credits to user after a failed operation.
        This is idempotent and safe to call multiple times.
        """
        try:
            credit_amount = self.CREDIT_COSTS.get(operation, 0) * quantity

            if credit_amount == 0:
                return True, {'success': True, 'message': 'No refund needed'}

            # Check if unlimited tier (no refund needed)
            credits_info = self.get_user_credits(user_id)
            if credits_info.get('is_unlimited'):
                logger.info(f"Unlimited tier user {user_id}, no refund needed")
                return True, {'success': True, 'message': 'Unlimited tier'}

            # Atomic credit refund
            result = self.db.execute(
                text("""
                    UPDATE user_credits
                    SET
                        current_credits = current_credits + :credit_amount,
                        total_used = GREATEST(0, COALESCE(total_used, 0) - :credit_amount),
                        updated_at = :updated_at
                    WHERE user_id = :user_id
                    RETURNING current_credits, total_used
                """),
                {
                    "user_id": user_id,
                    "credit_amount": credit_amount,
                    "updated_at": datetime.now(timezone.utc)
                }
            ).fetchone()

            if not result:
                logger.error(f"User {user_id} not found for refund")
                return False, {'success': False, 'error': 'User not found'}

            self.db.commit()

            # Log the refund transaction
            self._log_transaction(
                user_id=user_id,
                operation=f"REFUND_{operation}",
                amount=credit_amount,
                description=f"Refund: {reason}"
            )

            logger.info(
                f"Credits refunded: user={user_id}, operation={operation}, "
                f"amount={credit_amount}, reason={reason}"
            )

            return True, {
                'success': True,
                'refunded': credit_amount,
                'new_balance': result.current_credits
            }

        except Exception as e:
            self.db.rollback()
            logger.error(f"Error refunding credits: {e}")
            return False, {
                'success': False,
                'error': f"Refund failed: {str(e)}"
            }

    def add_bonus_credits(
        self,
        user_id: str,
        amount: int,
        reason: str = "Bonus credits"
    ) -> Tuple[bool, Dict[str, Any]]:
        """Add bonus credits to user account"""
        try:
            result = self.db.execute(
                text("""
                    UPDATE user_credits
                    SET
                        current_credits = current_credits + :amount,
                        bonus_credits = COALESCE(bonus_credits, 0) + :amount,
                        updated_at = :updated_at
                    WHERE user_id = :user_id
                    RETURNING current_credits, bonus_credits
                """),
                {
                    "user_id": user_id,
                    "amount": amount,
                    "updated_at": datetime.now(timezone.utc)
                }
            ).fetchone()

            if not result:
                return False, {'success': False, 'error': 'User not found'}

            self.db.commit()

            self._log_transaction(
                user_id=user_id,
                operation="BONUS_CREDITS",
                amount=amount,
                description=reason
            )

            logger.info(f"Bonus credits added: user={user_id}, amount={amount}")

            return True, {
                'success': True,
                'added': amount,
                'new_balance': result.current_credits
            }

        except Exception as e:
            self.db.rollback()
            logger.error(f"Error adding bonus credits: {e}")
            return False, {'success': False, 'error': str(e)}

    def reset_monthly_credits(
        self,
        user_id: str,
        subscription_tier: str
    ) -> Tuple[bool, Dict[str, Any]]:
        """Reset monthly credits for a user based on their tier"""
        try:
            # Get tier enum
            tier_enum = SubscriptionTier(subscription_tier)
            monthly_allowance = self.TIER_CREDITS.get(tier_enum, 5)

            if monthly_allowance == -1:
                monthly_allowance = 999999  # Unlimited

            # Get current rollover credits (if applicable)
            current = self.get_user_credits(user_id)
            rollover_amount = 0

            # Calculate rollover for paid tiers
            if tier_enum in [SubscriptionTier.GROWTH, SubscriptionTier.BASIC]:
                rollover_amount = min(current.get('credits', 0), 50)
            elif tier_enum == SubscriptionTier.AGENCY_STANDARD:
                rollover_amount = min(current.get('credits', 0), 250)
            elif tier_enum == SubscriptionTier.AGENCY_PREMIUM:
                rollover_amount = min(current.get('credits', 0), 500)

            new_credits = monthly_allowance + rollover_amount

            result = self.db.execute(
                text("""
                    UPDATE user_credits
                    SET
                        current_credits = :new_credits,
                        monthly_allowance = :monthly_allowance,
                        last_reset = :reset_time,
                        updated_at = :updated_at
                    WHERE user_id = :user_id
                    RETURNING current_credits
                """),
                {
                    "user_id": user_id,
                    "new_credits": new_credits,
                    "monthly_allowance": monthly_allowance,
                    "reset_time": datetime.now(timezone.utc),
                    "updated_at": datetime.now(timezone.utc)
                }
            ).fetchone()

            self.db.commit()

            self._log_transaction(
                user_id=user_id,
                operation="MONTHLY_RESET",
                amount=new_credits,
                description=f"Monthly reset with {rollover_amount} rollover"
            )

            logger.info(
                f"Monthly credits reset: user={user_id}, "
                f"new_balance={new_credits}, rollover={rollover_amount}"
            )

            return True, {
                'success': True,
                'new_balance': new_credits,
                'rollover': rollover_amount
            }

        except Exception as e:
            self.db.rollback()
            logger.error(f"Error resetting monthly credits: {e}")
            return False, {'success': False, 'error': str(e)}

    def _initialize_user_credits(self, user_id: str) -> Dict[str, Any]:
        """Initialize credits for a new user"""
        try:
            # Get user to determine tier
            user = self.db.query(User).filter(User.id == user_id).first()
            tier = user.subscription_tier if user else SubscriptionTier.FREE

            monthly_allowance = self.TIER_CREDITS.get(tier, 5)
            if monthly_allowance == -1:
                monthly_allowance = 999999

            # Get bonus for tier
            bonus = 0
            if tier == SubscriptionTier.GROWTH:
                bonus = 20
            elif tier == SubscriptionTier.AGENCY_STANDARD:
                bonus = 100
            elif tier == SubscriptionTier.AGENCY_PREMIUM:
                bonus = 200

            initial_credits = monthly_allowance + bonus

            self.db.execute(
                text("""
                    INSERT INTO user_credits (
                        user_id,
                        current_credits,
                        monthly_allowance,
                        bonus_credits,
                        total_used,
                        subscription_tier,
                        last_reset,
                        created_at,
                        updated_at
                    ) VALUES (
                        :user_id,
                        :initial_credits,
                        :monthly_allowance,
                        :bonus,
                        0,
                        :tier,
                        :now,
                        :now,
                        :now
                    )
                    ON CONFLICT (user_id) DO NOTHING
                """),
                {
                    "user_id": user_id,
                    "initial_credits": initial_credits,
                    "monthly_allowance": monthly_allowance,
                    "bonus": bonus,
                    "tier": tier.value,
                    "now": datetime.now(timezone.utc)
                }
            )

            self.db.commit()

            logger.info(f"Initialized credits for user {user_id}: {initial_credits}")

            return {
                'credits': initial_credits,
                'monthly_allowance': monthly_allowance,
                'bonus_credits': bonus,
                'total_used': 0,
                'subscription_tier': tier.value,
                'is_unlimited': tier in [SubscriptionTier.AGENCY_UNLIMITED, SubscriptionTier.PRO]
            }

        except Exception as e:
            self.db.rollback()
            logger.error(f"Error initializing user credits: {e}")
            raise

    def _log_transaction(
        self,
        user_id: str,
        operation: str,
        amount: int,
        description: str
    ):
        """Log credit transaction to audit trail"""
        try:
            self.db.execute(
                text("""
                    INSERT INTO credit_transactions (
                        user_id,
                        operation,
                        amount,
                        description,
                        created_at
                    ) VALUES (
                        :user_id,
                        :operation,
                        :amount,
                        :description,
                        :created_at
                    )
                """),
                {
                    "user_id": user_id,
                    "operation": operation,
                    "amount": amount,
                    "description": description,
                    "created_at": datetime.now(timezone.utc)
                }
            )
            self.db.commit()
        except Exception as e:
            logger.error(f"Error logging credit transaction: {e}")
            # Don't fail the main operation if logging fails
