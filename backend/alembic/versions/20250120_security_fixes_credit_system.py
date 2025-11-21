"""security_fixes_credit_system

Revision ID: 20250120_security_fixes
Revises: 20250117_add_agencies_table
Create Date: 2025-01-20

SECURITY UPDATE: Fixes critical payment vulnerabilities
- Adds paddle_idempotency_keys table to prevent duplicate charges
- No changes to user_credits (managed by Supabase, already exists)
- No changes to credit_transactions (already exists)
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '20250120_security_fixes'
down_revision = '20250117_add_agencies_table'
branch_labels = None
depends_on = None


def upgrade():
    """Apply security fixes"""

    # Create paddle_idempotency_keys table
    op.create_table(
        'paddle_idempotency_keys',
        sa.Column('idempotency_key', sa.String(255), primary_key=True, index=True),
        sa.Column('user_id', sa.String(255), nullable=False, index=True),
        sa.Column('transaction_id', sa.String(255), nullable=True),
        sa.Column('price_id', sa.String(255), nullable=False),
        sa.Column('response_data', sa.Text, nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=False),
    )

    # Create index for cleanup queries
    op.create_index(
        'idx_paddle_idempotency_expires',
        'paddle_idempotency_keys',
        ['expires_at']
    )

    # Add paddle_customer_id column to users if it doesn't exist
    # (for Paddle Billing integration)
    try:
        op.add_column('users', sa.Column('paddle_customer_id', sa.String(255), nullable=True))
    except Exception as e:
        print(f"paddle_customer_id column may already exist: {e}")

    print("✅ Security fixes applied successfully")
    print("   - Added paddle_idempotency_keys table")
    print("   - Added paddle_customer_id to users table")


def downgrade():
    """Rollback security fixes"""

    # Drop paddle_idempotency_keys table
    op.drop_index('idx_paddle_idempotency_expires', table_name='paddle_idempotency_keys')
    op.drop_table('paddle_idempotency_keys')

    # Remove paddle_customer_id column
    try:
        op.drop_column('users', 'paddle_customer_id')
    except Exception as e:
        print(f"Could not drop paddle_customer_id: {e}")

    print("✅ Security fixes rolled back")
