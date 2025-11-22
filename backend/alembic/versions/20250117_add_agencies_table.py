"""Add agencies table for white-label support

Revision ID: 20250117_agencies
Revises: 20250107_5tier
Create Date: 2025-01-17 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '20250117_agencies'
down_revision: Union[str, None] = '20250107_5tier'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create agencies table"""

    # Create AgencyStatus enum type for PostgreSQL
    op.execute("""
        CREATE TYPE agencystatus AS ENUM ('active', 'suspended', 'cancelled')
    """)

    # Create agencies table
    op.create_table(
        'agencies',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('owner_user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('subscription_tier', sa.String(), nullable=True),
        sa.Column('max_team_members', sa.Integer(), nullable=True),
        sa.Column('monthly_analysis_limit', sa.Integer(), nullable=True),
        sa.Column('settings', postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default='{}'),
        sa.Column('status', sa.Enum('active', 'suspended', 'cancelled', name='agencystatus'), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )

    # Create indexes
    op.create_index(op.f('ix_agencies_id'), 'agencies', ['id'], unique=False)
    op.create_index(op.f('ix_agencies_owner_user_id'), 'agencies', ['owner_user_id'], unique=False)


def downgrade() -> None:
    """Drop agencies table"""

    # Drop indexes
    op.drop_index(op.f('ix_agencies_owner_user_id'), table_name='agencies')
    op.drop_index(op.f('ix_agencies_id'), table_name='agencies')

    # Drop table
    op.drop_table('agencies')

    # Drop enum type
    op.execute('DROP TYPE agencystatus')
