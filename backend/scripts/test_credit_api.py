#!/usr/bin/env python3
"""
Test what the credit API returns for the unlimited user
"""

import sys
from pathlib import Path

backend_path = Path(__file__).parent.parent
sys.path.insert(0, str(backend_path))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
from app.services.credit_service import CreditService

# User to test
USER_UUID = "92f3f140-ddb5-4e21-a6d7-814982b55ebc"

print("="*80)
print("Testing Credit API Response")
print("="*80)
print(f"\nUser UUID: {USER_UUID}")

# Create database session
engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
db = SessionLocal()

try:
    # Test the credit service
    credit_service = CreditService(db)

    print("\n1. Testing get_user_credits()...")
    credits_info = credit_service.get_user_credits(USER_UUID)

    print("\nResult:")
    for key, value in credits_info.items():
        print(f"   {key}: {value}")

    print("\n2. Testing consume_credits_atomic()...")
    success, result = credit_service.consume_credits_atomic(
        user_id=USER_UUID,
        operation='FULL_ANALYSIS',
        quantity=1,
        description="Test analysis"
    )

    print(f"\nSuccess: {success}")
    print(f"Result: {result}")

    if success:
        print("\n✅ Credit consumption succeeded!")
        print("   User can analyze!")
    else:
        print("\n❌ Credit consumption failed!")
        print("   This is the bug!")

except Exception as e:
    print(f"\n❌ ERROR: {e}")
    import traceback
    traceback.print_exc()
finally:
    db.close()

print("\n" + "="*80)
