#!/usr/bin/env python3
"""
Diagnostic Script: Unlimited Credit Bug Investigation
======================================================

Purpose: Investigate why user on UNLIMITED plan gets "Not enough credits" error

Affected User:
- Name: Olutomiwa Adeliyi
- Email: oadatascientist@gmail.com
- UID: 92f3f140-ddb5-4e21-a6d7-814982b55ebc

What This Script Does (READ-ONLY):
1. Checks user's subscription tier in users table
2. Checks user's credit record in user_credits table
3. Verifies is_unlimited flag status
4. Compares tier consistency between tables
5. Tests credit service logic with this user's data
6. Identifies exact point of failure

NO CHANGES ARE MADE - This is diagnostic only.
"""

import sys
import os
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent.parent
sys.path.insert(0, str(backend_path))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
from app.services.credit_service import CreditService
from app.models.user import SubscriptionTier
import json

def print_section(title):
    """Print formatted section header"""
    print("\n" + "="*80)
    print(f"  {title}")
    print("="*80 + "\n")

def diagnose_user_credits():
    """Main diagnostic function"""

    # User to investigate
    USER_EMAIL = "oadatascientist@gmail.com"
    USER_UID = "92f3f140-ddb5-4e21-a6d7-814982b55ebc"

    print_section("UNLIMITED CREDIT BUG DIAGNOSTIC REPORT")
    print(f"Target User: {USER_EMAIL}")
    print(f"User UID: {USER_UID}")
    print(f"Timestamp: {__import__('datetime').datetime.now().isoformat()}")

    # Create database connection
    engine = create_engine(settings.DATABASE_URL)
    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()

    try:
        # ===================================================================
        # CHECK 1: User's subscription tier in users table
        # ===================================================================
        print_section("CHECK 1: Users Table - Subscription Tier")

        query = text("""
            SELECT
                id,
                email,
                subscription_tier,
                subscription_active,
                paddle_subscription_id,
                paddle_customer_id,
                created_at,
                updated_at
            FROM users
            WHERE email = :email OR id = :user_id
        """)

        result = db.execute(query, {"email": USER_EMAIL, "user_id": USER_UID}).fetchone()

        if not result:
            print(f"❌ ERROR: User not found in database!")
            print(f"   Searched for email: {USER_EMAIL}")
            print(f"   Searched for ID: {USER_UID}")
            return

        user_data = dict(result._mapping)
        print("✅ User found in users table:")
        for key, value in user_data.items():
            print(f"   {key:25} = {value}")

        user_id_from_db = str(user_data['id'])
        user_tier = user_data['subscription_tier']

        # ===================================================================
        # CHECK 2: User's credit record in user_credits table
        # ===================================================================
        print_section("CHECK 2: User_Credits Table - Credit Balance")

        query = text("""
            SELECT
                user_id,
                current_credits,
                monthly_allowance,
                subscription_tier,
                is_unlimited,
                last_reset,
                created_at,
                updated_at
            FROM user_credits
            WHERE user_id = :user_id
        """)

        result = db.execute(query, {"user_id": user_id_from_db}).fetchone()

        if not result:
            print(f"❌ ERROR: No credit record found for user!")
            print(f"   User ID: {user_id_from_db}")
            print(f"   This is a CRITICAL issue - user_credits record missing!")
            print(f"\n   Possible causes:")
            print(f"   - User was created before credit system initialization")
            print(f"   - Credit record was accidentally deleted")
            print(f"   - Database migration didn't run properly")
        else:
            credit_data = dict(result._mapping)
            print("✅ Credit record found:")
            for key, value in credit_data.items():
                print(f"   {key:25} = {value}")

            # ===================================================================
            # CHECK 3: Tier consistency validation
            # ===================================================================
            print_section("CHECK 3: Tier Consistency Analysis")

            credit_tier = credit_data['subscription_tier']
            is_unlimited = credit_data['is_unlimited']
            current_credits = credit_data['current_credits']

            print(f"Users table tier:        {user_tier}")
            print(f"User_credits table tier: {credit_tier}")
            print(f"is_unlimited flag:       {is_unlimited}")
            print(f"current_credits value:   {current_credits}")

            if user_tier != credit_tier:
                print(f"\n❌ TIER MISMATCH DETECTED!")
                print(f"   Users table shows:        {user_tier}")
                print(f"   User_credits shows:       {credit_tier}")
                print(f"   This is likely the root cause of the bug!")
            else:
                print(f"\n✅ Tiers match in both tables")

            # Check if unlimited tier has correct is_unlimited flag
            unlimited_tiers = ['agency_unlimited', 'pro']
            should_be_unlimited = user_tier in unlimited_tiers

            if should_be_unlimited and not is_unlimited:
                print(f"\n❌ UNLIMITED FLAG MISMATCH!")
                print(f"   Tier '{user_tier}' should have is_unlimited=True")
                print(f"   But is_unlimited={is_unlimited}")
                print(f"   This is a CRITICAL bug!")
            elif should_be_unlimited and is_unlimited:
                print(f"\n✅ Unlimited flag correctly set for tier '{user_tier}'")

        # ===================================================================
        # CHECK 4: Test CreditService logic with this user
        # ===================================================================
        print_section("CHECK 4: Credit Service Logic Test")

        credit_service = CreditService(db)

        try:
            # Test get_balance
            balance = credit_service.get_balance(user_id_from_db)
            print(f"✅ CreditService.get_balance() returned:")
            print(f"   Current credits: {balance.get('current_credits')}")
            print(f"   Monthly allowance: {balance.get('monthly_allowance')}")
            print(f"   Subscription tier: {balance.get('subscription_tier')}")
            print(f"   Is unlimited: {balance.get('is_unlimited')}")

            # Test has_sufficient_credits
            has_credits = credit_service.has_sufficient_credits(user_id_from_db, 1)
            print(f"\n✅ CreditService.has_sufficient_credits(1) returned: {has_credits}")

            if not has_credits:
                print(f"   ❌ Backend thinks user DOES NOT have credits!")
                print(f"   This confirms backend-side logic failure")
            else:
                print(f"   ✅ Backend correctly recognizes unlimited credits")
                print(f"   Bug must be in frontend validation!")

        except Exception as e:
            print(f"❌ ERROR testing CreditService: {e}")
            import traceback
            traceback.print_exc()

        # ===================================================================
        # CHECK 5: Verify SubscriptionTier enum values
        # ===================================================================
        print_section("CHECK 5: SubscriptionTier Enum Validation")

        print("Available SubscriptionTier enum values:")
        for tier in SubscriptionTier:
            print(f"   - {tier.value}")

        if user_tier in [t.value for t in SubscriptionTier]:
            print(f"\n✅ User's tier '{user_tier}' exists in enum")
        else:
            print(f"\n❌ User's tier '{user_tier}' NOT in enum!")
            print(f"   This is a CRITICAL issue!")

        # ===================================================================
        # CHECK 6: Database-level unlimited check
        # ===================================================================
        print_section("CHECK 6: Database-Level Credit Queries")

        # Simulate the atomic credit check query
        query = text("""
            SELECT
                current_credits,
                is_unlimited,
                (CASE
                    WHEN is_unlimited = true THEN true
                    WHEN current_credits >= :credit_cost THEN true
                    ELSE false
                END) as has_credits
            FROM user_credits
            WHERE user_id = :user_id
        """)

        result = db.execute(query, {"user_id": user_id_from_db, "credit_cost": 1}).fetchone()

        if result:
            print(f"Database-level credit check:")
            print(f"   current_credits:  {result.current_credits}")
            print(f"   is_unlimited:     {result.is_unlimited}")
            print(f"   has_credits:      {result.has_credits}")

            if not result.has_credits:
                print(f"\n❌ Database query says user DOES NOT have credits!")
                if not result.is_unlimited and result.current_credits < 1:
                    print(f"   Root cause: is_unlimited=False AND current_credits=0")
            else:
                print(f"\n✅ Database query correctly recognizes user has credits")

        # ===================================================================
        # CHECK 7: Compare with other unlimited users
        # ===================================================================
        print_section("CHECK 7: Compare with Other Unlimited Users")

        query = text("""
            SELECT
                u.email,
                u.subscription_tier as user_tier,
                uc.subscription_tier as credit_tier,
                uc.is_unlimited,
                uc.current_credits
            FROM users u
            LEFT JOIN user_credits uc ON CAST(u.id AS VARCHAR) = uc.user_id
            WHERE u.subscription_tier IN ('agency_unlimited', 'pro')
            ORDER BY u.created_at DESC
            LIMIT 5
        """)

        results = db.execute(query).fetchall()

        print(f"Found {len(results)} users with unlimited tiers:")
        print(f"\n{'Email':<35} {'User Tier':<20} {'Credit Tier':<20} {'Unlimited':<12} {'Credits'}")
        print("-" * 110)

        for row in results:
            email = row.email[:34]
            user_tier_val = row.user_tier or 'NULL'
            credit_tier_val = row.credit_tier or 'NULL'
            unlimited = str(row.is_unlimited) if row.is_unlimited is not None else 'NULL'
            credits = str(row.current_credits) if row.current_credits is not None else 'NULL'

            flag = "⚠️ " if row.email == USER_EMAIL else "   "
            print(f"{flag}{email:<35} {user_tier_val:<20} {credit_tier_val:<20} {unlimited:<12} {credits}")

        # ===================================================================
        # SUMMARY & RECOMMENDATIONS
        # ===================================================================
        print_section("DIAGNOSTIC SUMMARY & RECOMMENDATIONS")

        print("📊 FINDINGS:")
        print(f"   1. User tier in users table: {user_tier}")

        if result:
            print(f"   2. Credit record exists: YES")
            print(f"   3. is_unlimited flag: {credit_data.get('is_unlimited', 'N/A')}")
            print(f"   4. current_credits: {credit_data.get('current_credits', 'N/A')}")

            # Determine root cause
            print("\n🔍 ROOT CAUSE ANALYSIS:")

            if credit_data.get('is_unlimited') == False:
                print("   ❌ PRIMARY ISSUE: is_unlimited flag is False for unlimited tier")
                print("      The user_credits.is_unlimited should be True")
                print("      Likely cause: Subscription upgrade didn't update credit record")

            elif credit_data.get('current_credits', 0) == 0:
                print("   ⚠️  SECONDARY ISSUE: current_credits is 0")
                print("      Even with is_unlimited, credits show 0 instead of 999999")
                print("      This might confuse frontend validation")

            else:
                print("   ⚠️  Backend data looks correct!")
                print("      Issue is likely in frontend useCredits.js validation")
                print("      Check hasEnoughCredits() function logic")
        else:
            print(f"   2. Credit record exists: NO")
            print("\n🔍 ROOT CAUSE ANALYSIS:")
            print("   ❌ PRIMARY ISSUE: Missing user_credits record")
            print("      User has no entry in user_credits table")
            print("      This causes all credit checks to fail")

        print("\n💡 RECOMMENDED FIXES:")

        if not result:
            print("   1. Run initialize_user_credits() for this user")
            print("   2. Verify all users have credit records (run audit script)")
            print("   3. Add database constraint to ensure credit records exist")
        elif credit_data.get('is_unlimited') == False:
            print("   1. Update user_credits set is_unlimited=true where user_id='...'")
            print("   2. Update current_credits to 999999 for display purposes")
            print("   3. Investigate Paddle webhook subscription.updated handler")
            print("   4. Add validation in subscription upgrade flow")
        else:
            print("   1. Debug frontend useCredits.js hasEnoughCredits() function")
            print("   2. Check if API /api/credits/balance returns correct data")
            print("   3. Verify React state updates when tier changes")
            print("   4. Add frontend logging to trace validation failure")

        print("\n" + "="*80)
        print("  END OF DIAGNOSTIC REPORT")
        print("="*80 + "\n")

    except Exception as e:
        print(f"\n❌ FATAL ERROR during diagnosis:")
        print(f"   {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    diagnose_user_credits()
