-- ============================================================================
-- FIX RLS SECURITY ISSUES - Simple & Safe
-- ============================================================================
-- Issue: 13 tables have RLS policies but RLS is not enabled
-- This means policies are being IGNORED - security vulnerability!
-- ============================================================================

-- STEP 1: Check current RLS status (read-only)
-- ============================================================================
SELECT
    tablename,
    rowsecurity as rls_enabled,
    (SELECT COUNT(*) FROM pg_policies
     WHERE pg_policies.tablename = pg_tables.tablename
     AND pg_policies.schemaname = 'public') as policy_count
FROM pg_tables
WHERE schemaname = 'public'
    AND tablename IN (
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
    )
ORDER BY tablename;

-- ============================================================================
-- STEP 2: Enable RLS on all affected tables
-- ============================================================================
-- Run this after reviewing STEP 1 results

BEGIN;

-- Agency/Team tables
ALTER TABLE IF EXISTS agency_invitations ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS agency_team_members ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS team_roles ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS team_members ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS team_invitations ENABLE ROW LEVEL SECURITY;

-- Integration tables
ALTER TABLE IF EXISTS integrations ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS user_integrations ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS integration_logs ENABLE ROW LEVEL SECURITY;

-- Analysis/Content tables
ALTER TABLE IF EXISTS ad_analyses ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS ad_generations ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS competitor_benchmarks ENABLE ROW LEVEL SECURITY;

-- Project tables
ALTER TABLE IF EXISTS projects ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS project_team_access ENABLE ROW LEVEL SECURITY;

-- Verify the changes
SELECT
    'AFTER ENABLING RLS' as status,
    tablename,
    rowsecurity as rls_now_enabled
FROM pg_tables
WHERE schemaname = 'public'
    AND tablename IN (
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
    )
ORDER BY tablename;

-- Review the results above
-- If all show rls_now_enabled = true, uncomment COMMIT below
-- If any issues, uncomment ROLLBACK instead

-- COMMIT;
-- ROLLBACK;

-- ============================================================================
-- STEP 3: Final verification (run after COMMIT)
-- ============================================================================

-- Check no tables remain with policy/RLS mismatch
SELECT
    'FINAL CHECK' as status,
    COUNT(*) as tables_still_with_issues
FROM pg_tables t
INNER JOIN pg_policies p ON t.tablename = p.tablename AND p.schemaname = 'public'
WHERE t.schemaname = 'public'
    AND t.rowsecurity = false;

-- Expected result: tables_still_with_issues = 0

-- ============================================================================
-- ROLLBACK COMMANDS (Emergency use only - NOT RECOMMENDED)
-- ============================================================================
/*
BEGIN;

ALTER TABLE IF EXISTS agency_invitations DISABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS agency_team_members DISABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS team_roles DISABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS team_members DISABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS team_invitations DISABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS integrations DISABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS user_integrations DISABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS integration_logs DISABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS ad_analyses DISABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS ad_generations DISABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS competitor_benchmarks DISABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS projects DISABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS project_team_access DISABLE ROW LEVEL SECURITY;

COMMIT;
*/

-- ============================================================================
-- INSTRUCTIONS:
-- ============================================================================
-- 1. Copy this entire script
-- 2. Paste into Supabase SQL Editor
-- 3. Run STEP 1 to see current state
-- 4. Run STEP 2 BEGIN block and review results
-- 5. If results look good, uncomment and run: COMMIT;
-- 6. If issues, uncomment and run: ROLLBACK;
-- 7. Run STEP 3 to verify all issues resolved
-- 8. Test application to ensure access control works
-- ============================================================================
