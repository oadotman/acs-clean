#!/usr/bin/env python3
"""
Diagnostic Script: Unlimited Credit Bug - Supabase Direct Connection
====================================================================

This version connects directly to Supabase PostgreSQL instead of using
the configured DATABASE_URL (which may be SQLite in development).
"""

import sys
import os
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent.parent
sys.path.insert(0, str(backend_path))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

# Load environment
load_dotenv(backend_path / '.env')

def print_section(title):
    """Print formatted section header"""
    print("\n" + "="*80)
    print(f"  {title}")
    print("="*80 + "\n")

def get_supabase_connection():
    """Build Supabase PostgreSQL connection string"""
    supabase_url = os.getenv('SUPABASE_URL', '')

    if not supabase_url:
        print("ERROR: SUPABASE_URL not found in .env")
        sys.exit(1)

    # Extract project ref from Supabase URL
    # Format: https://PROJECT_REF.supabase.co
    project_ref = supabase_url.replace('https://', '').replace('.supabase.co', '')

    print(f"Connecting to Supabase project: {project_ref}")
    print(f"Host: db.{project_ref}.supabase.co")

    # Ask user for database password
    print("\nTo connect to Supabase PostgreSQL, we need the database password.")
    print("This is different from the API keys - it's the 'Database password'")
    print("from your Supabase project settings > Database > Connection string")
    print("\nAlternatively, you can check your Supabase connection string which")
    print("looks like: postgresql://postgres:[YOUR-PASSWORD]@...")
    print()

    db_password = input("Enter Supabase database password (or press Enter to check via Supabase API): ").strip()

    if not db_password:
        print("\nAlternative: Use Supabase REST API to query data...")
        return None

    # Build PostgreSQL connection string
    # Format: postgresql://postgres.PROJECT_REF:[PASSWORD]@aws-0-us-west-1.pooler.supabase.com:6543/postgres
    db_url = f"postgresql://postgres.{project_ref}:{db_password}@aws-0-us-west-1.pooler.supabase.com:6543/postgres"

    return db_url

def diagnose_with_api():
    """Use Supabase REST API as fallback"""
    from supabase import create_client

    supabase_url = os.getenv('SUPABASE_URL')
    supabase_key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')

    if not supabase_url or not supabase_key:
        print("ERROR: Supabase credentials not found")
        return

    print_section("Using Supabase REST API")

    supabase = create_client(supabase_url, supabase_key)

    # User to investigate
    USER_EMAIL = "oadatascientist@gmail.com"
    USER_UID = "92f3f140-ddb5-4e21-a6d7-814982b55ebc"

    print(f"Target User: {USER_EMAIL}")
    print(f"User UID: {USER_UID}")

    try:
        # Check users table
        print_section("CHECK 1: Users Table")
        response = supabase.table('users').select('*').eq('email', USER_EMAIL).execute()

        if response.data:
            user_data = response.data[0]
            print("User found:")
            for key, value in user_data.items():
                print(f"   {key:25} = {value}")

            user_id = str(user_data['id'])

            # Check user_credits table
            print_section("CHECK 2: User Credits Table")
            response = supabase.table('user_credits').select('*').eq('user_id', user_id).execute()

            if response.data:
                credit_data = response.data[0]
                print("Credit record found:")
                for key, value in credit_data.items():
                    print(f"   {key:25} = {value}")

                # Analysis
                print_section("ANALYSIS")
                user_tier = user_data.get('subscription_tier')
                credit_tier = credit_data.get('subscription_tier')
                is_unlimited = credit_data.get('is_unlimited')
                current_credits = credit_data.get('current_credits')

                print(f"Users table tier:        {user_tier}")
                print(f"User_credits tier:       {credit_tier}")
                print(f"is_unlimited:            {is_unlimited}")
                print(f"current_credits:         {current_credits}")

                if user_tier != credit_tier:
                    print("\nISSUE FOUND: Tier mismatch between tables!")

                if user_tier in ['agency_unlimited', 'pro'] and not is_unlimited:
                    print("\nISSUE FOUND: Unlimited tier but is_unlimited=False!")

                print_section("RECOMMENDATION")
                if not is_unlimited and user_tier in ['agency_unlimited', 'pro']:
                    print("Run this SQL to fix:")
                    print(f"UPDATE user_credits")
                    print(f"SET is_unlimited = true,")
                    print(f"    current_credits = 999999,")
                    print(f"    subscription_tier = '{user_tier}'")
                    print(f"WHERE user_id = '{user_id}';")

            else:
                print("ERROR: No credit record found for user!")
                print("\nRun this SQL to initialize:")
                print(f"INSERT INTO user_credits (user_id, current_credits, monthly_allowance, subscription_tier, is_unlimited)")
                print(f"VALUES ('{user_id}', 999999, -1, '{user_data.get('subscription_tier')}', true);")
        else:
            print("ERROR: User not found!")

    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()

def diagnose_with_sql(db_url):
    """Use direct SQL connection"""
    print_section("Connecting to Supabase PostgreSQL")

    try:
        engine = create_engine(db_url)
        SessionLocal = sessionmaker(bind=engine)
        db = SessionLocal()

        # Test connection
        result = db.execute(text("SELECT version();")).fetchone()
        print(f"Connected successfully!")
        print(f"PostgreSQL version: {result[0][:50]}...")

        # User to investigate
        USER_EMAIL = "oadatascientist@gmail.com"
        USER_UID = "92f3f140-ddb5-4e21-a6d7-814982b55ebc"

        print_section("CHECK 1: Users Table")

        query = text("""
            SELECT
                id,
                email,
                subscription_tier,
                subscription_active,
                paddle_subscription_id,
                created_at
            FROM users
            WHERE email = :email OR id::text = :user_id
        """)

        result = db.execute(query, {"email": USER_EMAIL, "user_id": USER_UID}).fetchone()

        if not result:
            print(f"ERROR: User not found!")
            return

        print("User found:")
        user_data = dict(result._mapping)
        for key, value in user_data.items():
            print(f"   {key:25} = {value}")

        user_id = str(user_data['id'])

        print_section("CHECK 2: User Credits Table")

        query = text("""
            SELECT *
            FROM user_credits
            WHERE user_id = :user_id
        """)

        result = db.execute(query, {"user_id": user_id}).fetchone()

        if not result:
            print(f"ERROR: No credit record found!")
            print(f"\nFIX: Run this SQL:")
            print(f"INSERT INTO user_credits (user_id, current_credits, monthly_allowance, subscription_tier, is_unlimited)")
            print(f"VALUES ('{user_id}', 999999, -1, '{user_data['subscription_tier']}', true);")
            return

        print("Credit record found:")
        credit_data = dict(result._mapping)
        for key, value in credit_data.items():
            print(f"   {key:25} = {value}")

        print_section("ANALYSIS")
        user_tier = user_data.get('subscription_tier')
        credit_tier = credit_data.get('subscription_tier')
        is_unlimited = credit_data.get('is_unlimited')
        current_credits = credit_data.get('current_credits')

        print(f"Users table tier:        {user_tier}")
        print(f"User_credits tier:       {credit_tier}")
        print(f"is_unlimited:            {is_unlimited}")
        print(f"current_credits:         {current_credits}")

        issues = []
        if user_tier != credit_tier:
            issues.append("Tier mismatch between tables")

        if user_tier in ['agency_unlimited', 'pro'] and not is_unlimited:
            issues.append("Unlimited tier but is_unlimited=False")

        if is_unlimited and current_credits == 0:
            issues.append("Unlimited but shows 0 credits (should be 999999)")

        if issues:
            print("\nISSUES FOUND:")
            for i, issue in enumerate(issues, 1):
                print(f"   {i}. {issue}")

            print_section("FIX SQL")
            print("UPDATE user_credits")
            print(f"SET is_unlimited = true,")
            print(f"    current_credits = 999999,")
            print(f"    subscription_tier = '{user_tier}'")
            print(f"WHERE user_id = '{user_id}';")
        else:
            print("\nNo database issues found!")
            print("Issue may be in frontend validation logic.")
            print("Check frontend/src/hooks/useCredits.js")

        db.close()

    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("="*80)
    print("  UNLIMITED CREDIT BUG DIAGNOSTIC - SUPABASE CONNECTION")
    print("="*80)

    print("\nConnection method:")
    print("  1. Direct PostgreSQL connection (requires database password)")
    print("  2. Supabase REST API (uses service role key from .env)")

    choice = input("\nChoose method (1 or 2, default=2): ").strip()

    if choice == "1":
        db_url = get_supabase_connection()
        if db_url:
            diagnose_with_sql(db_url)
        else:
            print("\nFalling back to REST API...")
            diagnose_with_api()
    else:
        diagnose_with_api()
