"""
Security Tests for Credit Service
Tests race conditions, refund logic, and atomic operations
"""

import pytest
import asyncio
from concurrent.futures import ThreadPoolExecutor
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from app.services.credit_service import CreditService
from app.models.user import User, SubscriptionTier


# Test database setup
TEST_DATABASE_URL = "sqlite:///./test_credits.db"
engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture
def db_session():
    """Create a test database session"""
    session = TestingSessionLocal()

    # Create tables
    session.execute(text("""
        CREATE TABLE IF NOT EXISTS user_credits (
            user_id TEXT PRIMARY KEY,
            current_credits INTEGER DEFAULT 0,
            monthly_allowance INTEGER DEFAULT 0,
            bonus_credits INTEGER DEFAULT 0,
            total_used INTEGER DEFAULT 0,
            subscription_tier TEXT DEFAULT 'free',
            last_reset TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """))

    session.execute(text("""
        CREATE TABLE IF NOT EXISTS credit_transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            operation TEXT NOT NULL,
            amount INTEGER NOT NULL,
            description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """))

    session.commit()

    yield session

    # Cleanup
    session.execute(text("DROP TABLE IF EXISTS user_credits"))
    session.execute(text("DROP TABLE IF EXISTS credit_transactions"))
    session.commit()
    session.close()


def test_atomic_credit_deduction_prevents_race_condition(db_session):
    """
    CRITICAL TEST: Verify atomic operations prevent race conditions
    Simulates 10 concurrent requests with only 5 credits available
    """
    user_id = "test_user_race"
    credit_service = CreditService(db_session)

    # Initialize user with 5 credits
    db_session.execute(text("""
        INSERT INTO user_credits (user_id, current_credits, monthly_allowance, subscription_tier)
        VALUES (:user_id, 5, 100, 'free')
    """), {"user_id": user_id})
    db_session.commit()

    # Simulate 10 concurrent credit deduction attempts
    successful_deductions = 0
    failed_deductions = 0

    def attempt_deduction():
        nonlocal successful_deductions, failed_deductions
        session = TestingSessionLocal()
        service = CreditService(session)

        success, result = service.consume_credits_atomic(
            user_id=user_id,
            operation='FULL_ANALYSIS',
            quantity=1
        )

        session.close()

        if success:
            successful_deductions += 1
        else:
            failed_deductions += 1

        return success

    # Execute 10 concurrent attempts
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(attempt_deduction) for _ in range(10)]
        results = [f.result() for f in futures]

    # Verify atomicity: Only 2 should succeed (5 credits / 2 per analysis = 2)
    # FULL_ANALYSIS costs 2 credits
    assert successful_deductions == 2, f"Expected 2 successful, got {successful_deductions}"
    assert failed_deductions == 8, f"Expected 8 failed, got {failed_deductions}"

    # Verify final balance
    final_credits = db_session.execute(
        text("SELECT current_credits FROM user_credits WHERE user_id = :user_id"),
        {"user_id": user_id}
    ).fetchone()

    assert final_credits[0] == 1, f"Expected 1 credit remaining, got {final_credits[0]}"
    print("✅ Race condition test passed: Atomic operations work correctly")


def test_credit_refund_on_failure(db_session):
    """
    CRITICAL TEST: Verify credits are refunded when analysis fails
    """
    user_id = "test_user_refund"
    credit_service = CreditService(db_session)

    # Initialize user with 10 credits
    db_session.execute(text("""
        INSERT INTO user_credits (user_id, current_credits, monthly_allowance, subscription_tier)
        VALUES (:user_id, 10, 100, 'growth')
    """), {"user_id": user_id})
    db_session.commit()

    # Consume credits
    success, result = credit_service.consume_credits_atomic(
        user_id=user_id,
        operation='FULL_ANALYSIS',
        quantity=1
    )

    assert success == True
    assert result['remaining'] == 8  # 10 - 2 = 8

    # Simulate failure and refund
    refund_success, refund_result = credit_service.refund_credits(
        user_id=user_id,
        operation='FULL_ANALYSIS',
        quantity=1,
        reason="Analysis failed due to API error"
    )

    assert refund_success == True
    assert refund_result['refunded'] == 2
    assert refund_result['new_balance'] == 10  # Back to original

    print("✅ Refund test passed: Credits properly restored on failure")


def test_unlimited_tier_bypass(db_session):
    """
    Test that unlimited tier users don't consume credits
    """
    user_id = "test_user_unlimited"
    credit_service = CreditService(db_session)

    # Initialize unlimited user
    db_session.execute(text("""
        INSERT INTO user_credits (user_id, current_credits, monthly_allowance, subscription_tier)
        VALUES (:user_id, 999999, 999999, 'agency_unlimited')
    """), {"user_id": user_id})
    db_session.commit()

    # Attempt multiple operations
    for _ in range(50):
        success, result = credit_service.consume_credits_atomic(
            user_id=user_id,
            operation='FULL_ANALYSIS',
            quantity=1
        )
        assert success == True
        assert result['remaining'] == 'unlimited'

    print("✅ Unlimited tier test passed: No credits consumed")


def test_insufficient_credits_rejection(db_session):
    """
    Test that operations are rejected when credits are insufficient
    """
    user_id = "test_user_insufficient"
    credit_service = CreditService(db_session)

    # Initialize user with only 1 credit
    db_session.execute(text("""
        INSERT INTO user_credits (user_id, current_credits, monthly_allowance, subscription_tier)
        VALUES (:user_id, 1, 100, 'free')
    """), {"user_id": user_id})
    db_session.commit()

    # Try to consume 2 credits
    success, result = credit_service.consume_credits_atomic(
        user_id=user_id,
        operation='FULL_ANALYSIS',  # Costs 2 credits
        quantity=1
    )

    assert success == False
    assert result['error'] == 'Insufficient credits'
    assert result['required'] == 2
    assert result['available'] == 1

    # Verify credits unchanged
    final_credits = db_session.execute(
        text("SELECT current_credits FROM user_credits WHERE user_id = :user_id"),
        {"user_id": user_id}
    ).fetchone()
    assert final_credits[0] == 1

    print("✅ Insufficient credits test passed: Operation correctly rejected")


def test_credit_transaction_logging(db_session):
    """
    Test that all credit operations are logged for audit trail
    """
    user_id = "test_user_logging"
    credit_service = CreditService(db_session)

    # Initialize user
    db_session.execute(text("""
        INSERT INTO user_credits (user_id, current_credits, monthly_allowance, subscription_tier)
        VALUES (:user_id, 20, 100, 'growth')
    """), {"user_id": user_id})
    db_session.commit()

    # Perform multiple operations
    credit_service.consume_credits_atomic(user_id, 'FULL_ANALYSIS', 1)
    credit_service.consume_credits_atomic(user_id, 'BASIC_ANALYSIS', 1)
    credit_service.refund_credits(user_id, 'FULL_ANALYSIS', 1, "Test refund")
    credit_service.add_bonus_credits(user_id, 10, "Promotional bonus")

    # Verify all transactions logged
    transactions = db_session.execute(
        text("SELECT operation, amount FROM credit_transactions WHERE user_id = :user_id"),
        {"user_id": user_id}
    ).fetchall()

    assert len(transactions) >= 4
    operations = [t[0] for t in transactions]
    assert 'FULL_ANALYSIS' in operations
    assert 'BASIC_ANALYSIS' in operations
    assert 'REFUND_FULL_ANALYSIS' in operations
    assert 'BONUS_CREDITS' in operations

    print("✅ Transaction logging test passed: All operations logged")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
