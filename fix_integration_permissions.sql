-- ============================================================================
-- SUPABASE PERMISSIONS FIX FOR INTEGRATION TABLES
-- Run this in Supabase SQL Editor to fix permission issues
-- 
-- Problem: user_integrations table returns "permission denied" (42501)
-- Solution: Grant proper permissions to authenticated users
-- ============================================================================

-- Step 1: Grant basic schema permissions
GRANT USAGE ON SCHEMA public TO authenticated;
GRANT USAGE ON SCHEMA public TO anon;

-- Step 2: Grant table permissions to authenticated users
GRANT ALL ON TABLE public.integrations TO authenticated;
GRANT ALL ON TABLE public.user_integrations TO authenticated;
GRANT ALL ON TABLE public.integration_logs TO authenticated;

-- Step 3: Grant read permissions to anonymous users (for public integrations catalog)
GRANT SELECT ON TABLE public.integrations TO anon;

-- Step 4: Grant sequence permissions (needed for UUID generation)
GRANT USAGE ON ALL SEQUENCES IN SCHEMA public TO authenticated;
GRANT SELECT ON ALL SEQUENCES IN SCHEMA public TO authenticated;

-- Step 5: Ensure RLS is disabled (matching your existing database pattern)
ALTER TABLE public.integrations DISABLE ROW LEVEL SECURITY;
ALTER TABLE public.user_integrations DISABLE ROW LEVEL SECURITY;
ALTER TABLE public.integration_logs DISABLE ROW LEVEL SECURITY;

-- Step 6: Grant permissions to service role (for admin operations)
GRANT ALL ON TABLE public.integrations TO service_role;
GRANT ALL ON TABLE public.user_integrations TO service_role;
GRANT ALL ON TABLE public.integration_logs TO service_role;

-- Step 7: Grant schema creation permissions (if needed)
GRANT CREATE ON SCHEMA public TO authenticated;

-- Step 8: Grant execute permissions on custom functions
GRANT EXECUTE ON FUNCTION public.update_updated_at_column() TO authenticated;
GRANT EXECUTE ON FUNCTION public.update_updated_at_column() TO service_role;

-- Step 9: Fix any missing default privileges
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO authenticated;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT USAGE ON SEQUENCES TO authenticated;

-- ============================================================================
-- VERIFICATION QUERIES - Run these to confirm the fix worked
-- ============================================================================

-- Check if permissions were granted correctly
SELECT 
    schemaname,
    tablename,
    usename,
    privilege_type
FROM information_schema.table_privileges 
WHERE schemaname = 'public' 
AND tablename IN ('integrations', 'user_integrations', 'integration_logs')
AND usename IN ('authenticated', 'anon', 'service_role')
ORDER BY tablename, usename;

-- Check RLS status (should all be 'f' for false/disabled)
SELECT 
    schemaname,
    tablename,
    rowsecurity
FROM pg_tables 
WHERE schemaname = 'public' 
AND tablename IN ('integrations', 'user_integrations', 'integration_logs');

-- Test table access and count records
SELECT 'integrations' as table_name, count(*) as record_count FROM integrations
UNION ALL
SELECT 'user_integrations' as table_name, count(*) as record_count FROM user_integrations
UNION ALL  
SELECT 'integration_logs' as table_name, count(*) as record_count FROM integration_logs;

-- ============================================================================
-- ADDITIONAL FIXES IF NEEDED
-- ============================================================================

-- If you still get permission errors, also run these:

-- Grant ALL permissions on all existing tables to authenticated
-- (This is a broader fix that matches how your other tables are configured)
GRANT ALL ON ALL TABLES IN SCHEMA public TO authenticated;
GRANT ALL ON ALL SEQUENCES IN SCHEMA public TO authenticated;
GRANT ALL ON ALL FUNCTIONS IN SCHEMA public TO authenticated;

-- Ensure the postgres user has permissions (fallback)
GRANT ALL ON TABLE public.integrations TO postgres;
GRANT ALL ON TABLE public.user_integrations TO postgres;
GRANT ALL ON TABLE public.integration_logs TO postgres;

-- ============================================================================
-- TROUBLESHOOTING
-- ============================================================================

-- If you still get errors after running this, check:
-- 1. Are you using the correct Supabase anon key in your frontend?
-- 2. Is the user properly authenticated (check browser dev tools > Application > Local Storage)
-- 3. Are there any RLS policies that might be interfering?

-- To check current user and role:
SELECT current_user, current_role;

-- To check if user is authenticated:
SELECT auth.uid() as authenticated_user_id;