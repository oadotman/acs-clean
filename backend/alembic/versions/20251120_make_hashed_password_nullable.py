"""make_hashed_password_nullable_for_supabase_auth

Revision ID: 20251120_hashed_password
Revises: 20250120_align_subscription_tiers_with_pricing
Create Date: 2025-11-20

CRITICAL FIX: Makes hashed_password nullable for Supabase authentication

Context:
- App uses Supabase for authentication (OAuth, magic links)
- Users created via Supabase have no password (hashed_password=None)
- Current schema has hashed_password as NOT NULL
- This causes 100% failure rate for new user registrations

Impact:
- Without this migration, all new user signups fail with database constraint violation
- This is a complete blocker for user acquisition
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '20251120_hashed_password'
down_revision = '20250120_align_subscription_tiers_with_pricing'
branch_labels = None
depends_on = None


def upgrade():
    """Make hashed_password nullable to support Supabase auth"""

    print("=" * 80)
    print("CRITICAL SCHEMA FIX: Making hashed_password nullable")
    print("=" * 80)
    print()
    print("This fixes a critical bug where new user registration fails because:")
    print("1. Supabase auth creates users without passwords (OAuth, magic links)")
    print("2. Database schema currently requires hashed_password (NOT NULL)")
    print("3. INSERT fails with constraint violation")
    print()
    print("After this migration:")
    print("✓ Supabase users can register successfully (hashed_password=NULL)")
    print("✓ Legacy users with passwords continue to work")
    print("✓ New user acquisition unblocked")
    print()

    # Make hashed_password nullable
    op.alter_column(
        'users',
        'hashed_password',
        existing_type=sa.String(),
        nullable=True,
        existing_nullable=False
    )

    print("✓ hashed_password column is now nullable")
    print("=" * 80)
    print("MIGRATION COMPLETE")
    print("=" * 80)


def downgrade():
    """Revert hashed_password to NOT NULL (WARNING: may fail if NULL values exist)"""

    print("WARNING: Reverting hashed_password to NOT NULL")
    print("This may fail if any users have NULL hashed_password (Supabase users)")
    print()

    # Check if any users have NULL hashed_password
    connection = op.get_bind()
    result = connection.execute(
        sa.text("SELECT COUNT(*) FROM users WHERE hashed_password IS NULL")
    )
    null_count = result.scalar()

    if null_count > 0:
        print(f"ERROR: Cannot revert - {null_count} users have NULL hashed_password")
        print("These are Supabase authenticated users.")
        print("Reverting would break their accounts!")
        print()
        raise Exception(
            f"Cannot make hashed_password NOT NULL - {null_count} users have NULL values. "
            "Delete these users or set dummy passwords before reverting this migration."
        )

    # Safe to revert
    op.alter_column(
        'users',
        'hashed_password',
        existing_type=sa.String(),
        nullable=False,
        existing_nullable=True
    )

    print("✓ Reverted hashed_password to NOT NULL")
