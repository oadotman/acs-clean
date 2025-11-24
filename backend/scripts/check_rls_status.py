#!/usr/bin/env python3
"""
Diagnostic Script: Supabase RLS Status Check
============================================

Purpose: Audit Row Level Security (RLS) configuration across all tables

Supabase Errors Reported:
- 13 tables have RLS policies but RLS not enabled
- Tables include: agency_invitations, agency_team_members, integrations,
  user_integrations, integration_logs, competitor_benchmarks, ad_generations,
  ad_analyses, projects, team_roles, team_members, team_invitations,
  project_team_access

What This Script Does (READ-ONLY):
1. Lists all tables in public schema
2. Checks RLS enabled status for each table
3. Counts RLS policies per table
4. Identifies tables with policies but RLS disabled
5. Checks which tables are actively used in codebase
6. Generates audit report with recommendations

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
import json
from collections import defaultdict

def print_section(title):
    """Print formatted section header"""
    print("\n" + "="*100)
    print(f"  {title}")
    print("="*100 + "\n")

def check_rls_status():
    """Main diagnostic function"""

    print_section("SUPABASE RLS SECURITY AUDIT REPORT")
    print(f"Timestamp: {__import__('datetime').datetime.now().isoformat()}")

    # Create database connection
    engine = create_engine(settings.DATABASE_URL)
    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()

    try:
        # ===================================================================
        # CHECK 1: List all tables with RLS status
        # ===================================================================
        print_section("CHECK 1: All Tables - RLS Status")

        query = text("""
            SELECT
                schemaname,
                tablename,
                rowsecurity as rls_enabled,
                tableowner
            FROM pg_tables
            WHERE schemaname = 'public'
            ORDER BY tablename
        """)

        results = db.execute(query).fetchall()

        print(f"Found {len(results)} tables in public schema:\n")
        print(f"{'Table Name':<35} {'RLS Enabled':<15} {'Owner'}")
        print("-" * 100)

        all_tables = {}
        rls_enabled_count = 0
        rls_disabled_count = 0

        for row in results:
            table = row.tablename
            rls_status = "✅ YES" if row.rls_enabled else "❌ NO"
            all_tables[table] = row.rls_enabled

            if row.rls_enabled:
                rls_enabled_count += 1
            else:
                rls_disabled_count += 1

            print(f"{table:<35} {rls_status:<15} {row.tableowner}")

        print(f"\nSummary:")
        print(f"  ✅ RLS Enabled:  {rls_enabled_count} tables")
        print(f"  ❌ RLS Disabled: {rls_disabled_count} tables")

        # ===================================================================
        # CHECK 2: Count RLS policies per table
        # ===================================================================
        print_section("CHECK 2: RLS Policies Per Table")

        query = text("""
            SELECT
                tablename,
                COUNT(*) as policy_count
            FROM pg_policies
            WHERE schemaname = 'public'
            GROUP BY tablename
            ORDER BY policy_count DESC, tablename
        """)

        results = db.execute(query).fetchall()

        print(f"Found {len(results)} tables with RLS policies:\n")
        print(f"{'Table Name':<35} {'Policy Count':<15} {'RLS Enabled'}")
        print("-" * 100)

        policy_counts = {}
        for row in results:
            table = row.tablename
            count = row.policy_count
            policy_counts[table] = count

            rls_enabled = all_tables.get(table, False)
            rls_status = "✅ YES" if rls_enabled else "❌ NO"

            flag = "⚠️ " if not rls_enabled else "   "
            print(f"{flag}{table:<35} {count:<15} {rls_status}")

        # ===================================================================
        # CHECK 3: Identify critical issues - Policies but RLS disabled
        # ===================================================================
        print_section("CHECK 3: CRITICAL - Tables with Policies but RLS Disabled")

        problematic_tables = [
            table for table in policy_counts.keys()
            if not all_tables.get(table, False)
        ]

        if problematic_tables:
            print(f"❌ Found {len(problematic_tables)} tables with RLS policies but RLS DISABLED:\n")

            for table in problematic_tables:
                policy_count = policy_counts[table]
                print(f"   ⚠️  {table:<35} ({policy_count} policies defined)")

            print("\n🔴 SECURITY RISK:")
            print("   These tables have access control policies defined but RLS is not enforced.")
            print("   This means the policies are being IGNORED and all users can access all rows!")
            print("   This is a CRITICAL security vulnerability.")

        else:
            print("✅ No issues found - All tables with policies have RLS enabled")

        # ===================================================================
        # CHECK 4: List all RLS policies in detail
        # ===================================================================
        print_section("CHECK 4: Detailed RLS Policy Information")

        query = text("""
            SELECT
                tablename,
                policyname,
                permissive,
                roles::text,
                cmd,
                qual,
                with_check
            FROM pg_policies
            WHERE schemaname = 'public'
            ORDER BY tablename, policyname
        """)

        results = db.execute(query).fetchall()

        current_table = None
        for row in results:
            if row.tablename != current_table:
                current_table = row.tablename
                rls_status = "✅ ENABLED" if all_tables.get(current_table, False) else "❌ DISABLED"
                print(f"\n📋 Table: {current_table} (RLS {rls_status})")
                print("-" * 100)

            print(f"   Policy: {row.policyname}")
            print(f"      Type: {row.permissive}")
            print(f"      Command: {row.cmd}")
            print(f"      Roles: {row.roles}")
            if row.qual:
                print(f"      Using: {row.qual[:100]}{'...' if len(row.qual) > 100 else ''}")
            if row.with_check:
                print(f"      With Check: {row.with_check[:100]}{'...' if len(row.with_check) > 100 else ''}")
            print()

        # ===================================================================
        # CHECK 5: Tables without any RLS configuration
        # ===================================================================
        print_section("CHECK 5: Tables Without RLS Configuration")

        tables_without_policies = [
            table for table in all_tables.keys()
            if table not in policy_counts
        ]

        if tables_without_policies:
            print(f"Found {len(tables_without_policies)} tables with NO RLS policies:\n")

            for table in tables_without_policies:
                rls_enabled = all_tables[table]
                status = "✅ Enabled (no policies)" if rls_enabled else "⚠️  Disabled (no policies)"
                print(f"   {table:<35} {status}")

            print("\n⚠️  NOTE:")
            print("   Tables without policies are effectively PUBLIC (if RLS enabled)")
            print("   or UNPROTECTED (if RLS disabled).")
            print("   Consider if these tables need access control.")

        # ===================================================================
        # CHECK 6: Check SQLAlchemy model coverage
        # ===================================================================
        print_section("CHECK 6: SQLAlchemy Model Coverage")

        models_dir = backend_path / "app" / "models"
        models_found = set()

        if models_dir.exists():
            for model_file in models_dir.glob("*.py"):
                if model_file.name != "__init__.py":
                    content = model_file.read_text()
                    # Extract __tablename__ definitions
                    import re
                    tablenames = re.findall(r'__tablename__\s*=\s*["\'](\w+)["\']', content)
                    models_found.update(tablenames)

        print(f"Found {len(models_found)} tables with SQLAlchemy models:")
        for table in sorted(models_found):
            print(f"   ✅ {table}")

        tables_without_models = set(all_tables.keys()) - models_found
        if tables_without_models:
            print(f"\n⚠️  Found {len(tables_without_models)} tables WITHOUT SQLAlchemy models:")
            for table in sorted(tables_without_models):
                print(f"   ❌ {table}")

            print("\n   These tables may be:")
            print("   - Supabase-native tables (managed outside backend)")
            print("   - Legacy tables no longer used")
            print("   - Manually created without migrations")

        # ===================================================================
        # CHECK 7: Specific tables from error report
        # ===================================================================
        print_section("CHECK 7: Validation Against Error Report")

        error_reported_tables = [
            'agency_invitations',
            'agency_team_members',
            'integrations',
            'user_integrations',
            'integration_logs',
            'competitor_benchmarks',
            'ad_generations',
            'ad_analyses',
            'projects',
            'team_roles',
            'team_members',
            'team_invitations',
            'project_team_access'
        ]

        print("Checking tables reported in Supabase error:\n")
        print(f"{'Table Name':<35} {'Exists':<10} {'RLS':<10} {'Policies':<10} {'Has Model'}")
        print("-" * 100)

        for table in error_reported_tables:
            exists = "✅ YES" if table in all_tables else "❌ NO"
            rls = "✅ ON" if all_tables.get(table, False) else "❌ OFF"
            policies = f"{policy_counts.get(table, 0)} policies"
            has_model = "✅ YES" if table in models_found else "❌ NO"

            flag = "⚠️ " if table in problematic_tables else "   "
            print(f"{flag}{table:<35} {exists:<10} {rls:<10} {policies:<10} {has_model}")

        # ===================================================================
        # CHECK 8: Database user permissions check
        # ===================================================================
        print_section("CHECK 8: Current Database User Permissions")

        query = text("""
            SELECT
                current_user as username,
                current_database() as database,
                session_user,
                inet_server_addr() as server_ip
        """)

        result = db.execute(query).fetchone()

        print(f"Current connection info:")
        print(f"   User: {result.username}")
        print(f"   Database: {result.database}")
        print(f"   Session User: {result.session_user}")
        print(f"   Server: {result.server_ip}")

        # Check if user has permission to enable RLS
        query = text("""
            SELECT
                has_database_privilege(current_user, current_database(), 'CREATE') as can_create,
                has_database_privilege(current_user, current_database(), 'CONNECT') as can_connect
        """)

        result = db.execute(query).fetchone()

        print(f"\nPermissions:")
        print(f"   Can CREATE: {'✅ YES' if result.can_create else '❌ NO'}")
        print(f"   Can CONNECT: {'✅ YES' if result.can_connect else '❌ NO'}")

        # ===================================================================
        # SUMMARY & RECOMMENDATIONS
        # ===================================================================
        print_section("AUDIT SUMMARY & RECOMMENDATIONS")

        print("📊 KEY FINDINGS:")
        print(f"   • Total tables in public schema: {len(all_tables)}")
        print(f"   • Tables with RLS enabled: {rls_enabled_count}")
        print(f"   • Tables with RLS disabled: {rls_disabled_count}")
        print(f"   • Tables with policies defined: {len(policy_counts)}")
        print(f"   • Critical issues (policies but RLS off): {len(problematic_tables)}")
        print(f"   • Tables without SQLAlchemy models: {len(tables_without_models)}")

        print("\n🔍 RISK ASSESSMENT:")

        if problematic_tables:
            print(f"   🔴 HIGH RISK: {len(problematic_tables)} tables have policies but RLS disabled")
            print(f"      These tables are VULNERABLE to unauthorized access!")
            print(f"      Policies are defined but NOT ENFORCED")

        if len(tables_without_models) > 5:
            print(f"   🟡 MEDIUM RISK: Many tables ({len(tables_without_models)}) not in backend models")
            print(f"      These may be orphaned or managed outside version control")

        print("\n💡 RECOMMENDED ACTIONS:")

        print("\n   Priority 1 - CRITICAL (Do First):")
        if problematic_tables:
            print(f"   ✓ Enable RLS on {len(problematic_tables)} tables with policies:")
            for table in problematic_tables[:5]:
                print(f"      • ALTER TABLE {table} ENABLE ROW LEVEL SECURITY;")
            if len(problematic_tables) > 5:
                print(f"      • ... and {len(problematic_tables) - 5} more tables")

        print("\n   Priority 2 - Audit & Clean:")
        print("   ✓ Identify which tables are actively used vs orphaned")
        print("   ✓ Review tables without models - add to backend or mark as Supabase-only")
        print("   ✓ Consider dropping unused tables to reduce attack surface")

        print("\n   Priority 3 - Security Functions:")
        print("   ✓ Fix function search_path warnings (set search_path to empty)")
        print("   ✓ Review RLS policies for correctness")
        print("   ✓ Test RLS policies with different user roles")

        print("\n   Priority 4 - Long-term:")
        print("   ✓ Create Alembic migration to version control RLS changes")
        print("   ✓ Add RLS status check to CI/CD pipeline")
        print("   ✓ Document which tables should have RLS vs public access")

        print("\n📝 NEXT STEPS:")
        print("   1. Review this audit report with team")
        print("   2. Run generate_rls_fixes.sql script to create fix SQL")
        print("   3. Test RLS fixes in development environment")
        print("   4. Apply fixes to production during maintenance window")
        print("   5. Monitor application logs for access denied errors")

        print("\n" + "="*100)
        print("  END OF RLS AUDIT REPORT")
        print("="*100 + "\n")

    except Exception as e:
        print(f"\n❌ FATAL ERROR during audit:")
        print(f"   {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    check_rls_status()
