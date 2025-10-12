"""Add passport system tables

Revision ID: 20250917_passport_system
Revises: 9776a61f9e9d
Create Date: 2025-09-17 15:24:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '20250917_passport_system'
down_revision = '9776a61f9e9d'
branch_labels = None
depends_on = None


def upgrade():
    # Create data_passports table
    op.create_table('data_passports',
        sa.Column('passport_id', sa.String(36), primary_key=True),
        sa.Column('schema_version', sa.String(20), nullable=False),
        sa.Column('project_id', sa.String(36), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('origin_tool', sa.String(100), nullable=False),
        sa.Column('origin_user', sa.String(36), nullable=False),
        
        # Payload data (JSONB for PostgreSQL, JSON for others)
        sa.Column('ad_copy_data', sa.JSON(), nullable=False),
        sa.Column('metadata', sa.JSON(), nullable=False),
        
        # Workflow state
        sa.Column('current_step', sa.String(100), nullable=False),
        sa.Column('completed_steps', sa.JSON(), nullable=False, default=list),
        sa.Column('next_suggested_steps', sa.JSON(), nullable=False, default=list),
        sa.Column('fast_track_completed', sa.Boolean(), nullable=False, default=False),
        sa.Column('deep_track_completed', sa.Boolean(), nullable=False, default=False),
        
        # Performance and routing metadata
        sa.Column('priority', sa.Enum('low', 'medium', 'high', 'critical', name='priority_enum'), nullable=False, default='medium'),
        sa.Column('routing_hints', sa.JSON(), nullable=False, default=list),
        sa.Column('processing_time', sa.Integer(), nullable=False, default=0),
        sa.Column('retry_count', sa.Integer(), nullable=False, default=0),
        sa.Column('last_error', sa.Text(), nullable=True),
        
        # Indexes
        sa.Index('idx_passport_project_id', 'project_id'),
        sa.Index('idx_passport_origin_user', 'origin_user'),
        sa.Index('idx_passport_created_at', 'created_at'),
        sa.Index('idx_passport_priority', 'priority'),
        sa.Index('idx_passport_workflow_step', 'current_step'),
    )
    
    # Create passport_insights table
    op.create_table('passport_insights',
        sa.Column('insight_id', sa.String(36), primary_key=True),
        sa.Column('passport_id', sa.String(36), sa.ForeignKey('data_passports.passport_id', ondelete='CASCADE'), nullable=False),
        sa.Column('tool_id', sa.String(100), nullable=False),
        sa.Column('tool_version', sa.String(20), nullable=False),
        sa.Column('timestamp', sa.DateTime(timezone=True), nullable=False),
        sa.Column('confidence', sa.Float(), nullable=False),
        sa.Column('category', sa.Enum('analysis', 'suggestion', 'warning', 'error', name='insight_category_enum'), nullable=False),
        sa.Column('schema_version', sa.String(20), nullable=False),
        sa.Column('deprecation_notice', sa.Text(), nullable=True),
        
        # Insight data (scores, flags, recommendations, alternatives)
        sa.Column('insight_data', sa.JSON(), nullable=False),
        
        # Indexes
        sa.Index('idx_insight_passport_id', 'passport_id'),
        sa.Index('idx_insight_tool_id', 'tool_id'),
        sa.Index('idx_insight_timestamp', 'timestamp'),
        sa.Index('idx_insight_confidence', 'confidence'),
        sa.Index('idx_insight_category', 'category'),
    )
    
    # Create passport_conflicts table
    op.create_table('passport_conflicts',
        sa.Column('conflict_id', sa.String(36), primary_key=True),
        sa.Column('passport_id', sa.String(36), sa.ForeignKey('data_passports.passport_id', ondelete='CASCADE'), nullable=False),
        sa.Column('timestamp', sa.DateTime(timezone=True), nullable=False),
        sa.Column('conflict_type', sa.Enum('tool_disagreement', 'policy_violation', 'user_preference', 'business_rule', name='conflict_type_enum'), nullable=False),
        sa.Column('severity', sa.Enum('low', 'medium', 'high', 'critical', name='conflict_severity_enum'), nullable=False),
        
        # Conflicting parties and data
        sa.Column('tools_involved', sa.JSON(), nullable=False),
        sa.Column('conflict_data', sa.JSON(), nullable=False),
        
        # Resolution data (nullable until resolved)
        sa.Column('resolution_strategy', sa.Enum('auto', 'user_decision', 'escalated', 'deferred', name='resolution_strategy_enum'), nullable=True),
        sa.Column('resolution_decision', sa.Text(), nullable=True),
        sa.Column('resolution_reasoning', sa.Text(), nullable=True),
        sa.Column('resolved_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('resolved_by', sa.String(36), nullable=True),
        
        # Indexes
        sa.Index('idx_conflict_passport_id', 'passport_id'),
        sa.Index('idx_conflict_type', 'conflict_type'),
        sa.Index('idx_conflict_severity', 'severity'),
        sa.Index('idx_conflict_resolved', 'resolved_at'),
        sa.Index('idx_conflict_timestamp', 'timestamp'),
    )
    
    # Create passport_events table for audit trail
    op.create_table('passport_events',
        sa.Column('event_id', sa.String(36), primary_key=True),
        sa.Column('passport_id', sa.String(36), sa.ForeignKey('data_passports.passport_id', ondelete='CASCADE'), nullable=False),
        sa.Column('timestamp', sa.DateTime(timezone=True), nullable=False),
        sa.Column('event_type', sa.Enum('created', 'processed', 'conflicted', 'resolved', 'completed', 'error', name='event_type_enum'), nullable=False),
        sa.Column('tool_id', sa.String(100), nullable=False),
        sa.Column('event_data', sa.JSON(), nullable=True),
        sa.Column('metadata', sa.JSON(), nullable=True),
        
        # Performance metrics
        sa.Column('duration', sa.Integer(), nullable=True),
        sa.Column('memory_usage', sa.Integer(), nullable=True),
        sa.Column('cpu_usage', sa.Float(), nullable=True),
        
        # Indexes
        sa.Index('idx_event_passport_id', 'passport_id'),
        sa.Index('idx_event_timestamp', 'timestamp'),
        sa.Index('idx_event_type', 'event_type'),
        sa.Index('idx_event_tool_id', 'tool_id'),
    )
    
    # Create organizational_rules table for conflict resolution
    op.create_table('organizational_rules',
        sa.Column('rule_id', sa.String(36), primary_key=True),
        sa.Column('organization_id', sa.String(36), nullable=True),  # NULL for global rules
        sa.Column('rule_name', sa.String(200), nullable=False),
        sa.Column('rule_type', sa.Enum('compliance_priority', 'engagement_priority', 'risk_tolerance', 'tool_preference', name='org_rule_type_enum'), nullable=False),
        sa.Column('rule_data', sa.JSON(), nullable=False),
        sa.Column('priority', sa.Integer(), nullable=False, default=100),
        sa.Column('is_active', sa.Boolean(), nullable=False, default=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('created_by', sa.String(36), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        
        # Indexes
        sa.Index('idx_org_rules_organization', 'organization_id'),
        sa.Index('idx_org_rules_type', 'rule_type'),
        sa.Index('idx_org_rules_priority', 'priority'),
        sa.Index('idx_org_rules_active', 'is_active'),
    )
    
    # Create user_preferences table for personal conflict resolution
    op.create_table('user_preferences',
        sa.Column('user_id', sa.String(36), primary_key=True),
        sa.Column('experience_level', sa.Enum('new', 'power', name='experience_level_enum'), nullable=False, default='new'),
        sa.Column('conflict_resolution_preferences', sa.JSON(), nullable=False, default=dict),
        sa.Column('tool_preferences', sa.JSON(), nullable=False, default=dict),
        sa.Column('workflow_preferences', sa.JSON(), nullable=False, default=dict),
        sa.Column('ui_preferences', sa.JSON(), nullable=False, default=dict),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        
        # Feature flags for progressive experience
        sa.Column('show_advanced_features', sa.Boolean(), nullable=False, default=False),
        sa.Column('enable_power_shortcuts', sa.Boolean(), nullable=False, default=False),
        sa.Column('skip_tutorials', sa.Boolean(), nullable=False, default=False),
        
        # Indexes
        sa.Index('idx_user_pref_experience', 'experience_level'),
        sa.Index('idx_user_pref_advanced', 'show_advanced_features'),
    )
    
    # Create conflict_resolution_history table for ML learning
    op.create_table('conflict_resolution_history',
        sa.Column('resolution_id', sa.String(36), primary_key=True),
        sa.Column('conflict_id', sa.String(36), sa.ForeignKey('passport_conflicts.conflict_id'), nullable=False),
        sa.Column('user_id', sa.String(36), nullable=False),
        sa.Column('resolution_time_seconds', sa.Integer(), nullable=False),
        sa.Column('user_satisfaction_score', sa.Integer(), nullable=True),  # 1-5 rating
        sa.Column('outcome_success', sa.Boolean(), nullable=True),  # Did this resolution work well?
        sa.Column('learning_data', sa.JSON(), nullable=True),  # For ML model training
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        
        # Indexes
        sa.Index('idx_resolution_history_conflict', 'conflict_id'),
        sa.Index('idx_resolution_history_user', 'user_id'),
        sa.Index('idx_resolution_history_success', 'outcome_success'),
        sa.Index('idx_resolution_history_created', 'created_at'),
    )
    
    # Add foreign key constraints to existing tables if needed
    # Note: We might need to add passport_id to existing analysis tables for integration
    
    # Add passport_id column to ad_analysis table (optional - for linking)
    op.add_column('ad_analysis', 
        sa.Column('passport_id', sa.String(36), nullable=True)
    )
    op.create_index('idx_ad_analysis_passport_id', 'ad_analysis', ['passport_id'])


def downgrade():
    # Drop tables in reverse order (respecting foreign key constraints)
    op.drop_table('conflict_resolution_history')
    op.drop_table('user_preferences')
    op.drop_table('organizational_rules')
    op.drop_table('passport_events')
    op.drop_table('passport_conflicts')
    op.drop_table('passport_insights')
    op.drop_table('data_passports')
    
    # Drop the enums
    op.execute('DROP TYPE IF EXISTS priority_enum')
    op.execute('DROP TYPE IF EXISTS insight_category_enum')
    op.execute('DROP TYPE IF EXISTS conflict_type_enum')
    op.execute('DROP TYPE IF EXISTS conflict_severity_enum')
    op.execute('DROP TYPE IF EXISTS resolution_strategy_enum')
    op.execute('DROP TYPE IF EXISTS event_type_enum')
    op.execute('DROP TYPE IF EXISTS org_rule_type_enum')
    op.execute('DROP TYPE IF EXISTS experience_level_enum')
    
    # Remove added column from existing table
    op.drop_index('idx_ad_analysis_passport_id', 'ad_analysis')
    op.drop_column('ad_analysis', 'passport_id')