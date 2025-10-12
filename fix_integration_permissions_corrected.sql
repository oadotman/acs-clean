-- ============================================================================
-- SUPABASE PERMISSIONS FIX FOR INTEGRATION TABLES (CORRECTED)
-- Run this in Supabase SQL Editor to fix permission issues
-- ============================================================================

-- =================================
-- CORE PERMISSION FIXES
-- =================================

-- Grant basic schema permissions
GRANT USAGE ON SCHEMA public TO authenticated;
GRANT USAGE ON SCHEMA public TO anon;

-- Grant table permissions to authenticated users
GRANT ALL ON TABLE public.integrations TO authenticated;
GRANT ALL ON TABLE public.user_integrations TO authenticated;
GRANT ALL ON TABLE public.integration_logs TO authenticated;

-- Grant read permissions to anonymous users (for public integrations catalog)
GRANT SELECT ON TABLE public.integrations TO anon;

-- Grant sequence permissions (needed for UUID generation)
GRANT USAGE ON ALL SEQUENCES IN SCHEMA public TO authenticated;
GRANT SELECT ON ALL SEQUENCES IN SCHEMA public TO authenticated;

-- Ensure RLS is disabled (matching your existing database pattern)
ALTER TABLE public.integrations DISABLE ROW LEVEL SECURITY;
ALTER TABLE public.user_integrations DISABLE ROW LEVEL SECURITY;
ALTER TABLE public.integration_logs DISABLE ROW LEVEL SECURITY;

-- Grant permissions to service role (for admin operations)
GRANT ALL ON TABLE public.integrations TO service_role;
GRANT ALL ON TABLE public.user_integrations TO service_role;
GRANT ALL ON TABLE public.integration_logs TO service_role;

-- Grant schema creation permissions (if needed)
GRANT CREATE ON SCHEMA public TO authenticated;

-- Grant execute permissions on custom functions
GRANT EXECUTE ON FUNCTION public.update_updated_at_column() TO authenticated;
GRANT EXECUTE ON FUNCTION public.update_updated_at_column() TO service_role;

-- Fix any missing default privileges
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO authenticated;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT USAGE ON SEQUENCES TO authenticated;

-- =================================
-- BROADER PERMISSIONS (if specific grants don't work)
-- =================================

-- Grant ALL permissions on all existing tables to authenticated
-- (This matches how your other tables like projects, ad_analyses are configured)
GRANT ALL ON ALL TABLES IN SCHEMA public TO authenticated;
GRANT ALL ON ALL SEQUENCES IN SCHEMA public TO authenticated;
GRANT ALL ON ALL FUNCTIONS IN SCHEMA public TO authenticated;

-- =================================
-- SIMPLE VERIFICATION (safe queries)
-- =================================

-- Test table access and count records
SELECT 'integrations' as table_name, count(*) as record_count FROM integrations;

SELECT 'user_integrations' as table_name, count(*) as record_count FROM user_integrations;

SELECT 'integration_logs' as table_name, count(*) as record_count FROM integration_logs;

-- Check RLS status (should all show 'f' for false/disabled)
SELECT 
    t.tablename,
    t.rowsecurity as rls_enabled
FROM pg_tables t
WHERE t.schemaname = 'public'
AND t.tablename IN ('integrations', 'user_integrations', 'integration_logs')
ORDER BY t.tablename;

-- =================================
-- SUCCESS MESSAGE
-- =================================
SELECT 'Permissions fix completed! Check your frontend console for errors.' as status;