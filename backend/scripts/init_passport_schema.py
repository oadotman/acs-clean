#!/usr/bin/env python3
"""
Database initialization script for AdCopySurge Passport System
Run this script to set up the database schema for the cohesive architecture.

Usage:
    python scripts/init_passport_schema.py [--environment=production|development]
"""

import os
import sys
import argparse
from pathlib import Path

# Add the backend directory to Python path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from alembic.config import Config
from alembic import command
from sqlalchemy import create_engine, text
from app.core.config import settings
from app.core.database import get_db, engine

def run_alembic_upgrade(alembic_cfg_path: str, revision: str = "head"):
    """Run Alembic upgrade to specified revision"""
    print(f"🔄 Running Alembic upgrade to {revision}...")
    
    alembic_cfg = Config(alembic_cfg_path)
    command.upgrade(alembic_cfg, revision)
    
    print("✅ Database schema updated successfully!")

def check_database_connection():
    """Test database connectivity"""
    print("🔍 Checking database connection...")
    
    try:
        with engine.connect() as connection:
            result = connection.execute(text("SELECT 1"))
            row = result.fetchone()
            if row and row[0] == 1:
                print("✅ Database connection successful!")
                return True
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False
    
    return False

def check_existing_tables():
    """Check what tables already exist"""
    print("📋 Checking existing database schema...")
    
    try:
        with engine.connect() as connection:
            # Check for existing tables
            result = connection.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_type = 'BASE TABLE'
                ORDER BY table_name
            """))
            
            existing_tables = [row[0] for row in result.fetchall()]
            
            if existing_tables:
                print(f"📊 Found {len(existing_tables)} existing tables:")
                for table in existing_tables:
                    print(f"   - {table}")
            else:
                print("📭 No existing tables found.")
                
            # Check for passport system tables specifically
            passport_tables = [
                'data_passports',
                'passport_insights', 
                'passport_conflicts',
                'passport_events',
                'organizational_rules',
                'user_preferences',
                'conflict_resolution_history'
            ]
            
            existing_passport_tables = [t for t in passport_tables if t in existing_tables]
            
            if existing_passport_tables:
                print(f"🛂 Passport system tables already exist: {existing_passport_tables}")
                return True
            else:
                print("🆕 Passport system tables need to be created.")
                return False
                
    except Exception as e:
        print(f"❌ Error checking tables: {e}")
        return False

def seed_default_data():
    """Insert default organizational rules and preferences"""
    print("🌱 Seeding default data...")
    
    try:
        with engine.connect() as connection:
            # Insert default organizational rules
            connection.execute(text("""
                INSERT INTO organizational_rules (
                    rule_id, organization_id, rule_name, rule_type, rule_data, 
                    priority, is_active, created_at, created_by, updated_at
                ) VALUES 
                (
                    gen_random_uuid()::text, 
                    NULL, 
                    'Default Compliance Priority', 
                    'compliance_priority', 
                    '{"always_prioritize_compliance": true, "max_risk_tolerance": 0.3}',
                    10,
                    true,
                    NOW(),
                    'system',
                    NOW()
                ),
                (
                    gen_random_uuid()::text,
                    NULL,
                    'Default Engagement Balance',
                    'engagement_priority',
                    '{"engagement_weight": 0.7, "compliance_weight": 0.3}',
                    20,
                    true,
                    NOW(),
                    'system', 
                    NOW()
                ),
                (
                    gen_random_uuid()::text,
                    NULL,
                    'Conservative Risk Tolerance',
                    'risk_tolerance',
                    '{"max_risk_score": 0.4, "require_legal_review_above": 0.6}',
                    15,
                    true,
                    NOW(),
                    'system',
                    NOW()
                )
            """))
            
            connection.commit()
            print("✅ Default organizational rules created!")
            
    except Exception as e:
        print(f"⚠️  Warning: Could not seed default data: {e}")
        print("   This is normal if the migration hasn't been run yet.")

def main():
    parser = argparse.ArgumentParser(description="Initialize AdCopySurge Passport System Database")
    parser.add_argument(
        '--environment', 
        choices=['development', 'production'], 
        default='development',
        help='Target environment'
    )
    parser.add_argument(
        '--force', 
        action='store_true',
        help='Force migration even if tables exist'
    )
    parser.add_argument(
        '--seed-data',
        action='store_true', 
        default=True,
        help='Seed default organizational rules and data'
    )
    
    args = parser.parse_args()
    
    print("🚀 AdCopySurge Passport System Database Initialization")
    print("=" * 60)
    print(f"Environment: {args.environment}")
    print(f"Database URL: {settings.DATABASE_URL[:50]}...")
    print("")
    
    # Step 1: Check database connection
    if not check_database_connection():
        print("❌ Cannot proceed without database connection.")
        sys.exit(1)
    
    # Step 2: Check existing schema
    passport_tables_exist = check_existing_tables()
    
    if passport_tables_exist and not args.force:
        print("⚠️  Passport system tables already exist!")
        response = input("Do you want to continue with migration anyway? (y/N): ")
        if response.lower() != 'y':
            print("🛑 Migration cancelled.")
            sys.exit(0)
    
    # Step 3: Run Alembic migration
    try:
        alembic_cfg_path = backend_dir / "alembic.ini"
        run_alembic_upgrade(str(alembic_cfg_path))
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        sys.exit(1)
    
    # Step 4: Seed default data
    if args.seed_data:
        seed_default_data()
    
    print("")
    print("🎉 Database initialization completed successfully!")
    print("")
    print("Next steps:")
    print("1. Restart your backend server")
    print("2. Test the passport system endpoints")
    print("3. Check the frontend integration")
    print("")
    print("For monitoring:")
    print(f"- Check logs: tail -f logs/adcopysurge.log")
    print(f"- Database health: python scripts/check_db_health.py")

if __name__ == "__main__":
    main()