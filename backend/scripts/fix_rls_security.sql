-- ============================================================================
-- FIX RLS (ROW LEVEL SECURITY) ISSUES
-- ============================================================================
-- Issue: 13 tables have RLS policies defined but RLS is not enabled
-- This means the policies are being IGNORED - SECURITY VULNERABILITY!
--
-- Affected tables:
-- - agency_invitations, agency_team_members, integrations, user_integrations
-- - integration_logs, competitor_benchmarks, ad_generations, ad_analyses
-- - projects, team_roles, team_members, team_invitations, project_team_access
--
-- INSTRUCTIONS:
-- 1. Copy this entire script
-- 2. Paste into Supabase SQL Editor
-- 3. Run STEP 1 to audit current state
-- 4. Run STEP 2 to enable RLS on affected tables
-- ============================================================================

-- ============================================================================
-- STEP 1: AUDIT CURRENT STATE (Read-only)
-- ============================================================================

-- Check which tables have RLS enabled
SELECT
    tablename,
    rowsecurity as rls_enabled,
    (SELECT COUNT(*)
     FROM pg_policies
     WHERE pg_policies.tablename = pg_tables.tablename
       AND pg_policies.schemaname = 'public') as policy_count
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY tablename;

-- Find tables with policies but RLS disabled (CRITICAL ISSUES)
SELECT
    t.tablename,
    t.rowsecurity as rls_enabled,
    COUNT(p.policyname) as policy_count,
    array_agg(p.policyname) as policy_names
FROM pg_tables t
INNER JOIN pg_policies p ON t.tablename = p.tablename AND p.schemaname = 'public'
WHERE t.schemaname = 'public'
    AND t.rowsecurity = false
GROUP BY t.tablename, t.rowsecurity
ORDER BY policy_count DESC, t.tablename;

-- Check the 13 specific tables from error report
SELECT
    table_name,
    (SELECT rowsecurity
     FROM pg_tables
     WHERE tablename = table_name AND schemaname = 'public') as rls_enabled,
    (SELECT COUNT(*)
     FROM pg_policies
     WHERE tablename = table_name AND schemaname = 'public') as policy_count
FROM (
    VALUES
        ('agency_invitations'),
        ('agency_team_members'),
        ('integrations'),
        ('user_integrations'),
        ('integration_logs'),
        ('competitor_benchmarks'),
        ('ad_generations'),
        ('ad_analyses'),
        ('projects'),
        ('team_roles'),
        ('team_members'),
        ('team_invitations'),
        ('project_team_access')
) AS reported_tables(table_name)
ORDER BY table_name;

-- ============================================================================
-- STEP 2: ENABLE RLS ON AFFECTED TABLES
-- ============================================================================

-- IMPORTANT: Review the audit results from STEP 1 first!
-- This will enable RLS enforcement on all affected tables.

BEGIN;

-- Enable RLS on tables that have policies but RLS disabled
-- (Based on Supabase error report)

-- Agency/Team tables
ALTER TABLE IF EXISTS public.agency_invitations ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS public.agency_team_members ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS public.team_roles ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS public.team_members ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS public.team_invitations ENABLE ROW LEVEL SECURITY;

-- Integration tables
ALTER TABLE IF EXISTS public.integrations ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS public.user_integrations ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS public.integration_logs ENABLE ROW LEVEL SECURITY;

-- Analysis/Content tables
ALTER TABLE IF EXISTS public.ad_analyses ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS public.ad_generations ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS public.competitor_benchmarks ENABLE ROW LEVEL SECURITY;

-- Project tables
ALTER TABLE IF EXISTS public.projects ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS public.project_team_access ENABLE ROW LEVEL SECURITY;

-- Verify changes
SELECT
    'VERIFICATION' as check_type,
    tablename,
    rowsecurity as rls_now_enabled,
    (SELECT COUNT(*)
     FROM pg_policies
     WHERE pg_policies.tablename = pg_tables.tablename
       AND pg_policies.schemaname = 'public') as policy_count
FROM pg_tables
WHERE schemaname = 'public'
    AND tablename IN (
        'agency_invitations', 'agency_team_members', 'integrations',
        'user_integrations', 'integration_logs', 'competitor_benchmarks',
        'ad_generations', 'ad_analyses', 'projects', 'team_roles',
        'team_members', 'team_invitations', 'project_team_access'
    )
ORDER BY tablename;

-- Review the verification results above
-- If all show rls_now_enabled = true, uncomment COMMIT
-- Otherwise, uncomment ROLLBACK

-- COMMIT;
-- ROLLBACK;

-- ============================================================================
-- STEP 3: VERIFY NO TABLES REMAIN WITH POLICY/RLS MISMATCH
-- ============================================================================

-- After committing, run this to ensure no issues remain
SELECT
    'FINAL CHECK' as status,
    COUNT(*) as tables_with_issues
FROM pg_tables t
INNER JOIN pg_policies p ON t.tablename = p.tablename AND p.schemaname = 'public'
WHERE t.schemaname = 'public'
    AND t.rowsecurity = false;

-- Expected result: tables_with_issues = 0

-- List any remaining problematic tables (should be empty)
SELECT
    t.tablename,
    COUNT(p.policyname) as policy_count,
    'RLS STILL DISABLED!' as issue
FROM pg_tables t
INNER JOIN pg_policies p ON t.tablename = p.tablename AND p.schemaname = 'public'
WHERE t.schemaname = 'public'
    AND t.rowsecurity = false
GROUP BY t.tablename;

-- ============================================================================
-- STEP 4: FIX FUNCTION SEARCH_PATH WARNINGS (Optional)
-- ============================================================================

-- The Supabase linter also warned about functions with mutable search_path
-- This is a security best practice - set search_path to empty string

-- List all functions with mutable search_path
SELECT
    n.nspname as schema_name,
    p.proname as function_name,
    pg_get_function_arguments(p.oid) as arguments,
    CASE
        WHEN p.proconfig IS NULL THEN 'MUTABLE (needs fix)'
        WHEN 'search_path' = ANY(
            SELECT split_part(unnest(p.proconfig), '=', 1)
        ) THEN 'FIXED'
        ELSE 'MUTABLE (needs fix)'
    END as search_path_status
FROM pg_proc p
INNER JOIN pg_namespace n ON p.pronamespace = n.oid
WHERE n.nspname = 'public'
    AND p.prokind = 'f'
ORDER BY p.proname;

-- Example: Fix a single function
-- (Repeat for each function shown above with MUTABLE status)
/*
ALTER FUNCTION public.get_dashboard_metrics()
SET search_path = '';

ALTER FUNCTION public.reset_monthly_credits()
SET search_path = '';

-- Add more ALTER FUNCTION statements for other functions...
*/

-- ============================================================================
-- STEP 5: COMPREHENSIVE SECURITY AUDIT
-- ============================================================================

-- Summary of all security settings
WITH table_security AS (
    SELECT
        t.tablename,
        t.rowsecurity as rls_enabled,
        COUNT(p.policyname) as policy_count
    FROM pg_tables t
    LEFT JOIN pg_policies p ON t.tablename = p.tablename AND p.schemaname = 'public'
    WHERE t.schemaname = 'public'
    GROUP BY t.tablename, t.rowsecurity
)
SELECT
    'SECURITY SUMMARY' as report_section,
    COUNT(*) FILTER (WHERE rls_enabled = true) as tables_with_rls,
    COUNT(*) FILTER (WHERE rls_enabled = false) as tables_without_rls,
    COUNT(*) FILTER (WHERE policy_count > 0 AND rls_enabled = false) as CRITICAL_issues,
    COUNT(*) FILTER (WHERE policy_count > 0 AND rls_enabled = true) as protected_tables,
    COUNT(*) FILTER (WHERE policy_count = 0) as unprotected_tables
FROM table_security;

-- ============================================================================
-- ROLLBACK COMMANDS (Emergency Use Only)
-- ============================================================================

-- If you need to revert RLS changes (NOT RECOMMENDED), uncomment below:
/*
BEGIN;

ALTER TABLE IF EXISTS public.agency_invitations DISABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS public.agency_team_members DISABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS public.team_roles DISABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS public.team_members DISABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS public.team_invitations DISABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS public.integrations DISABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS public.user_integrations DISABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS public.integration_logs DISABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS public.ad_analyses DISABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS public.ad_generations DISABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS public.competitor_benchmarks DISABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS public.projects DISABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS public.project_team_access DISABLE ROW LEVEL SECURITY;

COMMIT;
*/

-- ============================================================================
-- EXECUTION INSTRUCTIONS:
-- ============================================================================
-- 1. Run STEP 1 to see current state and identify issues
-- 2. Run STEP 2 BEGIN block and review verification results
-- 3. If verification looks good, uncomment and run COMMIT
-- 4. Run STEP 3 to confirm all issues resolved
-- 5. Optionally run STEP 4 to fix function search_path warnings
-- 6. Run STEP 5 to get final security summary
-- 7. Test your application to ensure RLS policies work correctly
-- 8. Monitor logs for any "permission denied" errors
--
-- NOTE: Enabling RLS enforces the policies. Make sure the policies are
-- correctly defined before enabling RLS, or some users may lose access!
-- ============================================================================
