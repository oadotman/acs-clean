"""align_subscription_tiers_with_pricing

Revision ID: 20250120_tier_alignment
Revises: 20250120_security_fixes
Create Date: 2025-01-20

CRITICAL: Aligns database enum with frontend pricing page
Ensures consistency across the entire application

FRONTEND TIERS (from frontend/src/constants/plans.js):
- free
- growth ($39/mo)
- agency_standard ($99/mo)
- agency_premium ($199/mo)
- agency_unlimited ($249/mo)

LEGACY TIERS (being deprecated):
- basic → maps to growth
- pro → maps to agency_unlimited
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers
revision = '20250120_tier_alignment'
down_revision = '20250120_security_fixes'
branch_labels = None
depends_on = None


def upgrade():
    """
    Add missing subscription tier enum values to align with pricing page
    """

    print("=" * 80)
    print("ALIGNING SUBSCRIPTION TIERS WITH PRICING PAGE")
    print("=" * 80)

    # PostgreSQL enum modification strategy:
    # 1. Add new values to existing enum
    # 2. Migrate existing data
    # 3. Keep legacy values for backward compatibility

    connection = op.get_bind()

    # Step 1: Check what enum values currently exist
    print("\n1. Checking current enum values...")
    result = connection.execute(sa.text("""
        SELECT enumlabel FROM pg_enum
        WHERE enumtypid = 'subscriptiontier'::regtype
        ORDER BY enumsortorder
    """))

    existing_values = [row[0] for row in result.fetchall()]
    print(f"   Current values: {existing_values}")

    # Step 2: Add new enum values if they don't exist
    print("\n2. Adding new tier values...")

    new_tiers = ['growth', 'agency_standard', 'agency_premium', 'agency_unlimited']

    for tier in new_tiers:
        if tier not in existing_values:
            print(f"   Adding '{tier}'...")
            connection.execute(sa.text(f"ALTER TYPE subscriptiontier ADD VALUE '{tier}'"))
            connection.commit()
        else:
            print(f"   '{tier}' already exists ✓")

    # Step 3: Migrate legacy data to new tiers
    print("\n3. Migrating legacy tier data...")

    # Migrate 'basic' → 'growth'
    result = connection.execute(sa.text("""
        SELECT COUNT(*) FROM users WHERE subscription_tier = 'basic'
    """))
    basic_count = result.scalar()

    if basic_count > 0:
        print(f"   Migrating {basic_count} users from 'basic' → 'growth'...")
        connection.execute(sa.text("""
            UPDATE users
            SET subscription_tier = 'growth'
            WHERE subscription_tier = 'basic'
        """))
        connection.commit()
    else:
        print("   No 'basic' tier users to migrate ✓")

    # Migrate 'pro' → 'agency_unlimited'
    result = connection.execute(sa.text("""
        SELECT COUNT(*) FROM users WHERE subscription_tier = 'pro'
    """))
    pro_count = result.scalar()

    if pro_count > 0:
        print(f"   Migrating {pro_count} users from 'pro' → 'agency_unlimited'...")
        connection.execute(sa.text("""
            UPDATE users
            SET subscription_tier = 'agency_unlimited'
            WHERE subscription_tier = 'pro'
        """))
        connection.commit()
    else:
        print("   No 'pro' tier users to migrate ✓")

    # Step 4: Migrate user_credits table tiers
    print("\n4. Migrating user_credits subscription tiers...")

    # Check if user_credits table exists
    result = connection.execute(sa.text("""
        SELECT EXISTS (
            SELECT FROM information_schema.tables
            WHERE table_name = 'user_credits'
        )
    """))

    if result.scalar():
        # Migrate basic → growth
        connection.execute(sa.text("""
            UPDATE user_credits
            SET subscription_tier = 'growth'
            WHERE subscription_tier = 'basic'
        """))

        # Migrate pro → agency_unlimited
        connection.execute(sa.text("""
            UPDATE user_credits
            SET subscription_tier = 'agency_unlimited'
            WHERE subscription_tier = 'pro'
        """))

        connection.commit()
        print("   user_credits tiers migrated ✓")
    else:
        print("   user_credits table not found (OK if not created yet)")

    # Step 5: Verify final state
    print("\n5. Verifying migration...")
    result = connection.execute(sa.text("""
        SELECT enumlabel FROM pg_enum
        WHERE enumtypid = 'subscriptiontier'::regtype
        ORDER BY enumsortorder
    """))

    final_values = [row[0] for row in result.fetchall()]
    print(f"   Final enum values: {final_values}")

    # Check for required values
    required = ['free', 'growth', 'agency_standard', 'agency_premium', 'agency_unlimited']
    missing = [t for t in required if t not in final_values]

    if missing:
        print(f"   ⚠️  WARNING: Missing required tiers: {missing}")
    else:
        print("   ✓ All required tiers present!")

    # Display tier distribution
    result = connection.execute(sa.text("""
        SELECT subscription_tier, COUNT(*) as count
        FROM users
        GROUP BY subscription_tier
        ORDER BY count DESC
    """))

    print("\n6. Current tier distribution:")
    for row in result.fetchall():
        print(f"   {row[0]}: {row[1]} users")

    print("\n" + "=" * 80)
    print("MIGRATION COMPLETE")
    print("=" * 80)
    print("\nSUMMARY:")
    print("✓ Added: growth, agency_standard, agency_premium, agency_unlimited")
    print("✓ Migrated: basic → growth")
    print("✓ Migrated: pro → agency_unlimited")
    print("✓ Kept: basic, pro (for backward compatibility)")
    print("\nYour database now matches your pricing page! 🎉")
    print("=" * 80)


def downgrade():
    """
    Rollback tier alignment (migrate back to legacy tiers)
    """
    connection = op.get_bind()

    print("Rolling back tier alignment...")

    # Migrate growth → basic
    connection.execute(sa.text("""
        UPDATE users
        SET subscription_tier = 'basic'
        WHERE subscription_tier = 'growth'
    """))

    # Migrate agency_unlimited → pro
    connection.execute(sa.text("""
        UPDATE users
        SET subscription_tier = 'pro'
        WHERE subscription_tier = 'agency_unlimited'
    """))

    # Migrate other agency tiers to pro (best approximation)
    connection.execute(sa.text("""
        UPDATE users
        SET subscription_tier = 'pro'
        WHERE subscription_tier IN ('agency_standard', 'agency_premium')
    """))

    connection.commit()

    print("Rollback complete")
    print("Note: Cannot remove enum values in PostgreSQL without recreating the type")
