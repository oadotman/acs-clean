"""
Monthly Credit Reset Background Task
Runs on the 1st of each month to reset user credits
"""

from datetime import datetime, timezone
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.core.database import SessionLocal
from app.core.logging import get_logger
from app.services.credit_service import CreditService

logger = get_logger(__name__)


def reset_all_user_credits():
    """
    Reset monthly credits for all users based on their subscription tier.
    This should be run on the 1st of each month via cron or Celery beat.

    Usage with cron:
        0 0 1 * * /usr/bin/python /path/to/backend/run_credit_reset.py

    Usage with Celery:
        @periodic_task(run_every=crontab(day_of_month='1', hour='0', minute='0'))
        def monthly_credit_reset():
            reset_all_user_credits()
    """
    db = SessionLocal()
    success_count = 0
    failure_count = 0

    try:
        logger.info("=" * 80)
        logger.info("Starting monthly credit reset for all users")
        logger.info("=" * 80)

        # Get all users who have credit records
        result = db.execute(
            text("""
                SELECT user_id, subscription_tier
                FROM user_credits
                WHERE subscription_tier IS NOT NULL
                ORDER BY user_id
            """)
        )

        users = result.fetchall()
        total_users = len(users)

        logger.info(f"Found {total_users} users to process")

        credit_service = CreditService(db)

        for user_data in users:
            user_id = user_data.user_id
            subscription_tier = user_data.subscription_tier

            try:
                logger.info(f"Processing user {user_id} (tier: {subscription_tier})")

                success, result = credit_service.reset_monthly_credits(
                    user_id=user_id,
                    subscription_tier=subscription_tier
                )

                if success:
                    logger.info(
                        f"✅ Reset successful for user {user_id}: "
                        f"new_balance={result.get('new_balance')}, "
                        f"rollover={result.get('rollover')}"
                    )
                    success_count += 1
                else:
                    logger.error(
                        f"❌ Reset failed for user {user_id}: {result.get('error')}"
                    )
                    failure_count += 1

            except Exception as e:
                logger.error(f"❌ Exception processing user {user_id}: {e}")
                failure_count += 1
                continue

        logger.info("=" * 80)
        logger.info(f"Monthly credit reset complete!")
        logger.info(f"Total users: {total_users}")
        logger.info(f"Successful: {success_count}")
        logger.info(f"Failed: {failure_count}")
        logger.info("=" * 80)

        return {
            'success': True,
            'total': total_users,
            'successful': success_count,
            'failed': failure_count
        }

    except Exception as e:
        logger.error(f"Fatal error in monthly credit reset: {e}")
        return {
            'success': False,
            'error': str(e)
        }
    finally:
        db.close()


def cleanup_expired_idempotency_keys():
    """
    Clean up expired idempotency keys (older than 24 hours).
    This should run daily to keep the table clean.
    """
    db = SessionLocal()

    try:
        logger.info("Cleaning up expired idempotency keys...")

        result = db.execute(
            text("""
                DELETE FROM paddle_idempotency_keys
                WHERE expires_at < NOW()
            """)
        )

        deleted_count = result.rowcount
        db.commit()

        logger.info(f"✅ Deleted {deleted_count} expired idempotency keys")

        return {'success': True, 'deleted': deleted_count}

    except Exception as e:
        logger.error(f"Error cleaning up idempotency keys: {e}")
        db.rollback()
        return {'success': False, 'error': str(e)}
    finally:
        db.close()


if __name__ == "__main__":
    # Allow running directly from command line
    print("Running monthly credit reset...")
    result = reset_all_user_credits()
    print(f"Result: {result}")

    print("\nCleaning up expired idempotency keys...")
    cleanup_result = cleanup_expired_idempotency_keys()
    print(f"Cleanup result: {cleanup_result}")
