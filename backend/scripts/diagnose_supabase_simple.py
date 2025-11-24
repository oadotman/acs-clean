#!/usr/bin/env python3
"""
Diagnostic Script: Unlimited Credit Bug - Simple HTTP API Version
=================================================================

Uses direct HTTP requests to Supabase PostgREST API
No external dependencies beyond requests (which is usually available)
"""

import sys
import os
from pathlib import Path
import json

# Add backend to path
backend_path = Path(__file__).parent.parent
sys.path.insert(0, str(backend_path))

from dotenv import load_dotenv
import requests

# Load environment
load_dotenv(backend_path / '.env')

def print_section(title):
    """Print formatted section header"""
    print("\n" + "="*80)
    print(f"  {title}")
    print("="*80 + "\n")

def diagnose():
    """Diagnose credit issue using Supabase REST API"""

    # Get credentials
    supabase_url = os.getenv('SUPABASE_URL')
    supabase_key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')

    if not supabase_url or not supabase_key:
        print("ERROR: SUPABASE_URL or SUPABASE_SERVICE_ROLE_KEY not found in .env")
        return

    # User to investigate
    USER_EMAIL = "oadatascientist@gmail.com"
    USER_UID = "92f3f140-ddb5-4e21-a6d7-814982b55ebc"

    api_url = f"{supabase_url}/rest/v1"
    headers = {
        "apikey": supabase_key,
        "Authorization": f"Bearer {supabase_key}",
        "Content-Type": "application/json"
    }

    print_section("UNLIMITED CREDIT BUG DIAGNOSTIC")
    print(f"Target User: {USER_EMAIL}")
    print(f"User UID: {USER_UID}")
    print(f"Supabase URL: {supabase_url}")

    # ========================================================================
    # CHECK 1: Query users table
    # ========================================================================
    print_section("CHECK 1: Users Table")

    try:
        response = requests.get(
            f"{api_url}/users",
            headers=headers,
            params={"email": f"eq.{USER_EMAIL}"}
        )

        if response.status_code != 200:
            print(f"ERROR: API request failed with status {response.status_code}")
            print(f"Response: {response.text}")
            return

        users = response.json()

        if not users:
            print(f"ERROR: User not found with email {USER_EMAIL}")
            return

        user_data = users[0]
        print("User found:")
        for key, value in user_data.items():
            print(f"   {key:30} = {value}")

        user_id = str(user_data['id'])

    except Exception as e:
        print(f"ERROR querying users table: {e}")
        import traceback
        traceback.print_exc()
        return

    # ========================================================================
    # CHECK 2: Query user_credits table
    # ========================================================================
    print_section("CHECK 2: User Credits Table")

    try:
        response = requests.get(
            f"{api_url}/user_credits",
            headers=headers,
            params={"user_id": f"eq.{user_id}"}
        )

        if response.status_code != 200:
            print(f"ERROR: API request failed with status {response.status_code}")
            print(f"Response: {response.text}")
            credit_data = None
        else:
            credits = response.json()

            if not credits:
                print(f"ERROR: No credit record found for user!")
                credit_data = None
            else:
                credit_data = credits[0]
                print("Credit record found:")
                for key, value in credit_data.items():
                    print(f"   {key:30} = {value}")

    except Exception as e:
        print(f"ERROR querying user_credits table: {e}")
        import traceback
        traceback.print_exc()
        credit_data = None

    # ========================================================================
    # ANALYSIS
    # ========================================================================
    print_section("ANALYSIS")

    user_tier = user_data.get('subscription_tier')
    print(f"User subscription tier: {user_tier}")

    if credit_data:
        credit_tier = credit_data.get('subscription_tier')
        is_unlimited = credit_data.get('is_unlimited')
        current_credits = credit_data.get('current_credits')

        print(f"Credit table tier:      {credit_tier}")
        print(f"is_unlimited flag:      {is_unlimited}")
        print(f"current_credits value:  {current_credits}")

        # Identify issues
        issues = []

        if user_tier != credit_tier:
            issues.append(f"Tier mismatch: users={user_tier}, credits={credit_tier}")

        if user_tier in ['agency_unlimited', 'pro', 'AGENCY_UNLIMITED', 'PRO']:
            if not is_unlimited:
                issues.append(f"User has unlimited tier '{user_tier}' but is_unlimited=False")
            if current_credits == 0:
                issues.append(f"Unlimited user shows 0 credits (should be 999999 for display)")

        if issues:
            print("\n*** ISSUES FOUND ***")
            for i, issue in enumerate(issues, 1):
                print(f"   {i}. {issue}")

            print_section("FIX SQL")
            print("Run this SQL in Supabase SQL Editor:")
            print()
            print("UPDATE user_credits")
            print(f"SET is_unlimited = true,")
            print(f"    current_credits = 999999,")
            print(f"    subscription_tier = '{user_tier}'")
            print(f"WHERE user_id = '{user_id}';")
            print()
            print("Or use the Supabase REST API:")
            print(f"PATCH {api_url}/user_credits?user_id=eq.{user_id}")
            print(json.dumps({
                "is_unlimited": True,
                "current_credits": 999999,
                "subscription_tier": user_tier
            }, indent=2))

        else:
            print("\n*** NO DATABASE ISSUES FOUND ***")
            print("\nDatabase records look correct!")
            print("The issue is likely in the application code:")
            print("  1. Frontend validation in useCredits.js")
            print("  2. Credit service logic in credit_service.py")
            print("  3. API credit check in ads.py")
            print("\nCheck application logs for errors.")

    else:
        print("\n*** CRITICAL: NO CREDIT RECORD EXISTS ***")
        print("\nThe user has no entry in user_credits table!")
        print("This will cause all credit checks to fail.")

        print_section("FIX SQL")
        print("Run this SQL in Supabase SQL Editor:")
        print()
        print("INSERT INTO user_credits (")
        print("    user_id,")
        print("    current_credits,")
        print("    monthly_allowance,")
        print("    subscription_tier,")
        print("    is_unlimited,")
        print("    last_reset")
        print(") VALUES (")
        print(f"    '{user_id}',")
        print(f"    999999,")
        print(f"    -1,")
        print(f"    '{user_tier}',")
        print(f"    true,")
        print(f"    NOW()")
        print(");")

    # ========================================================================
    # CHECK 3: Compare with other unlimited users
    # ========================================================================
    print_section("CHECK 3: Other Unlimited Users (Sample)")

    try:
        response = requests.get(
            f"{api_url}/users",
            headers=headers,
            params={
                "subscription_tier": "in.(agency_unlimited,pro,AGENCY_UNLIMITED,PRO)",
                "limit": "5",
                "order": "created_at.desc"
            }
        )

        if response.status_code == 200:
            users = response.json()
            print(f"Found {len(users)} other unlimited tier users:")
            print(f"\n{'Email':<35} {'Tier':<20} {'Active'}")
            print("-" * 80)

            for user in users:
                email = user.get('email', 'N/A')[:34]
                tier = user.get('subscription_tier', 'N/A')
                active = user.get('subscription_active', 'N/A')
                flag = "***" if email == USER_EMAIL[:34] else "   "
                print(f"{flag} {email:<35} {tier:<20} {active}")

    except Exception as e:
        print(f"Could not fetch other users: {e}")

    print_section("DIAGNOSTIC COMPLETE")
    print("Review the analysis above to determine the fix needed.")
    print("="*80)

if __name__ == "__main__":
    try:
        diagnose()
    except KeyboardInterrupt:
        print("\n\nDiagnostic cancelled by user.")
    except Exception as e:
        print(f"\nFATAL ERROR: {e}")
        import traceback
        traceback.print_exc()
