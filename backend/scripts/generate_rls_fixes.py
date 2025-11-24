
#!/usr/bin/env python3
"""
Script: Generate RLS Fix SQL
============================

Purpose: Generate SQL commands to fix RLS configuration issues

This script generates (but does NOT execute):
1. ALTER TABLE commands to enable RLS on affected tables
2. Verification queries to check fix success
3. Rollback commands in case of issues
4. Alembic migration template

Output: SQL file that can be reviewed and applied manually

NO CHANGES ARE MADE - This generates SQL only.
"""

import sys
import os
from pathlib import Path
from datetime import datetime

# Add backend to path
backend_path = Path(__file__).parent.parent
sys.path.insert(0, str(backend_path))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

def generate_rls_fixes():
    """Generate SQL to fix RLS issues"""

    print("="*100)
    print("  RLS FIX SQL GENERATOR")
    print("="*100)
    print()

    # Create database connection
    engine = create_engine(settings.DATABASE_URL)
    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()

    output_file = backend_path / "scripts" / f"fix_rls_{datetime.now().strftime('%Y%m%d_%H%M%S')}.sql"

    try:
        # Query tables with policies but RLS disabled
        query = text("""
            SELECT DISTINCT
                t.tablename,
                COUNT(p.policyname) as policy_count
            FROM pg_tables t
            LEFT JOIN pg_policies p ON t.tablename = p.tablename AND p.schemaname = 'public'
            WHERE t.schemaname = 'public'
                AND t.rowsecurity = false
                AND p.policyname IS NOT NULL
            GROUP BY t.tablename
            ORDER BY t.tablename
        """)

        results = db.execute(query).fetchall()

        if not results:
            print("✅ No RLS issues found! All tables with policies have RLS enabled.")
            return

        tables_to_fix = [(row.tablename, row.policy_count) for row in results]

        print(f"Found {len(tables_to_fix)} tables that need RLS enabled:\n")
        for table, policy_count in tables_to_fix:
            print(f"   • {table} ({policy_count} policies)")

        print(f"\nGenerating fix SQL to: {output_file}")

        # Generate SQL file
        with open(output_file, 'w') as f:
            f.write("""-- RLS FIX SQL SCRIPT
-- Generated: {}
-- Purpose: Enable Row Level Security on tables with policies but RLS disabled
--
-- IMPORTANT: Review this SQL before executing!
-- Test in development environment first!
--
-- Usage:
--   psql $DATABASE_URL < {}
--
-- Or execute manually in Supabase SQL Editor

""".format(datetime.now().isoformat(), output_file.name))

            # Add header
            f.write("-- " + "="*90 + "\n")
            f.write("-- PART 1: BACKUP CURRENT STATE (Read-only checks)\n")
            f.write("-- " + "="*90 + "\n\n")

            # Backup queries
            f.write("""-- Check current RLS status BEFORE changes
SELECT
    tablename,
    rowsecurity as rls_enabled_before,
    (SELECT COUNT(*) FROM pg_policies WHERE pg_policies.tablename = pg_tables.tablename) as policy_count
FROM pg_tables
WHERE schemaname = 'public'
    AND tablename IN (
""")

            for i, (table, _) in enumerate(tables_to_fix):
                f.write(f"        '{table}'")
                if i < len(tables_to_fix) - 1:
                    f.write(",\n")
                else:
                    f.write("\n")

            f.write("""    )
ORDER BY tablename;

""")

            # Main fixes
            f.write("-- " + "="*90 + "\n")
            f.write("-- PART 2: ENABLE RLS ON AFFECTED TABLES\n")
            f.write("-- " + "="*90 + "\n\n")

            f.write("-- Begin transaction for atomic changes\n")
            f.write("BEGIN;\n\n")

            for table, policy_count in tables_to_fix:
                f.write(f"-- Enable RLS on {table} ({policy_count} policies defined)\n")
                f.write(f"ALTER TABLE public.{table} ENABLE ROW LEVEL SECURITY;\n\n")

            f.write("-- Commit transaction\n")
            f.write("COMMIT;\n\n")

            # Verification
            f.write("-- " + "="*90 + "\n")
            f.write("-- PART 3: VERIFY CHANGES\n")
            f.write("-- " + "="*90 + "\n\n")

            f.write("""-- Check RLS status AFTER changes
SELECT
    tablename,
    rowsecurity as rls_enabled_after,
    (SELECT COUNT(*) FROM pg_policies WHERE pg_policies.tablename = pg_tables.tablename) as policy_count
FROM pg_tables
WHERE schemaname = 'public'
    AND tablename IN (
""")

            for i, (table, _) in enumerate(tables_to_fix):
                f.write(f"        '{table}'")
                if i < len(tables_to_fix) - 1:
                    f.write(",\n")
                else:
                    f.write("\n")

            f.write("""    )
ORDER BY tablename;

-- Expected result: All tables should show rls_enabled_after = true

""")

            # Rollback section
            f.write("-- " + "="*90 + "\n")
            f.write("-- PART 4: ROLLBACK COMMANDS (If needed)\n")
            f.write("-- " + "="*90 + "\n\n")

            f.write("-- Uncomment and run ONLY if you need to revert changes\n")
            f.write("-- BEGIN;\n\n")

            for table, _ in tables_to_fix:
                f.write(f"-- ALTER TABLE public.{table} DISABLE ROW LEVEL SECURITY;\n")

            f.write("\n-- COMMIT;\n\n")

            # Testing section
            f.write("-- " + "="*90 + "\n")
            f.write("-- PART 5: TESTING RLS POLICIES\n")
            f.write("-- " + "="*90 + "\n\n")

            f.write("""-- Test if RLS policies work correctly
-- This should be done AFTER enabling RLS

-- Test 1: Check if anonymous users are blocked
SET ROLE anon;
-- Try to select from protected tables (should fail or return empty)
""")

            for table, _ in tables_to_fix[:3]:  # Test first 3 tables
                f.write(f"-- SELECT COUNT(*) FROM public.{table}; -- Should respect RLS\n")

            f.write("""
-- Reset role
RESET ROLE;

-- Test 2: Check if authenticated users can access their data
-- (This depends on your specific RLS policies)

""")

            # Migration template
            f.write("-- " + "="*90 + "\n")
            f.write("-- PART 6: ALEMBIC MIGRATION TEMPLATE\n")
            f.write("-- " + "="*90 + "\n\n")

            f.write("""-- Copy this into a new Alembic migration file
-- Command: alembic revision -m "enable_rls_on_policy_tables"

def upgrade():
    # Enable RLS on tables with policies
    op.execute('''
""")

            for table, _ in tables_to_fix:
                f.write(f"        ALTER TABLE public.{table} ENABLE ROW LEVEL SECURITY;\n")

            f.write("""    ''')

def downgrade():
    # Disable RLS (rollback)
    op.execute('''
""")

            for table, _ in tables_to_fix:
                f.write(f"        ALTER TABLE public.{table} DISABLE ROW LEVEL SECURITY;\n")

            f.write("""    ''')

""")

            # Summary
            f.write("-- " + "="*90 + "\n")
            f.write("-- SUMMARY\n")
            f.write("-- " + "="*90 + "\n\n")

            f.write(f"-- Tables to fix: {len(tables_to_fix)}\n")
            for table, policy_count in tables_to_fix:
                f.write(f"--   • {table} ({policy_count} policies)\n")

            f.write("""--
-- Execution checklist:
--   [ ] Review all SQL commands above
--   [ ] Backup production database
--   [ ] Test in development environment first
--   [ ] Execute PART 2 (BEGIN...COMMIT block)
--   [ ] Run PART 3 verification queries
--   [ ] Test application functionality
--   [ ] Monitor logs for access denied errors
--   [ ] Keep PART 4 rollback commands ready
--   [ ] Create Alembic migration using PART 6 template
--
-- END OF FIX SQL SCRIPT
""")

        print(f"\n✅ SQL fix script generated successfully!")
        print(f"\nFile location: {output_file}")
        print(f"\nNext steps:")
        print(f"   1. Review the SQL file: {output_file.name}")
        print(f"   2. Test in development: psql $DATABASE_URL < {output_file.name}")
        print(f"   3. Verify with PART 3 queries")
        print(f"   4. Apply to production during maintenance window")
        print(f"   5. Create Alembic migration using PART 6 template")

        # Also print table-specific analysis
        print(f"\n" + "="*100)
        print("  TABLE-SPECIFIC ANALYSIS")
        print("="*100 + "\n")

        for table, policy_count in tables_to_fix:
            # Get policy details for this table
            query = text("""
                SELECT
                    policyname,
                    cmd,
                    roles::text
                FROM pg_policies
                WHERE schemaname = 'public' AND tablename = :table
                ORDER BY policyname
            """)

            policies = db.execute(query, {"table": table}).fetchall()

            print(f"📋 {table} ({policy_count} policies):")
            for policy in policies:
                print(f"   • {policy.policyname}")
                print(f"      Command: {policy.cmd}")
                print(f"      Roles: {policy.roles}")
            print()

    except Exception as e:
        print(f"\n❌ ERROR generating fix SQL:")
        print(f"   {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    generate_rls_fixes()
