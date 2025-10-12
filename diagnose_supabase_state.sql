-- ============================================================================
-- SUPABASE DIAGNOSTIC QUERIES
-- Run these step by step to understand the current database state
-- ============================================================================

-- =================================
-- STEP 1: Check what tables exist
-- =================================
SELECT 
    table_name,
    table_type,
    table_schema
FROM information_schema.tables 
WHERE table_schema = 'public'
AND table_name LIKE '%integration%'
ORDER BY table_name;

-- =================================
-- STEP 2: Check all public tables (to see what's actually there)
-- =================================
SELECT 
    table_name,
    table_type
FROM information_schema.tables 
WHERE table_schema = 'public'
ORDER BY table_name;

-- =================================
-- STEP 3: Check current user and roles
-- =================================
SELECT 
    current_user as current_user,
    session_user as session_user,
    current_role as current_role;

-- =================================
-- STEP 4: Check what roles exist in the database
-- =================================
SELECT 
    rolname as role_name,
    rolsuper as is_superuser,
    rolinherit as can_inherit,
    rolcreaterole as can_create_role,
    rolcreatedb as can_create_db,
    rolcanlogin as can_login
FROM pg_roles 
WHERE rolname IN ('authenticated', 'anon', 'service_role', 'postgres')
ORDER BY rolname;

-- =================================
-- STEP 5: Check table permissions (corrected column names)
-- =================================
SELECT 
    table_schema,
    table_name,
    grantee,
    privilege_type,
    is_grantable
FROM information_schema.table_privileges 
WHERE table_schema = 'public' 
AND table_name LIKE '%integration%'
ORDER BY table_name, grantee;

-- =================================
-- STEP 6: Check if integration tables exist and their structure
-- =================================
-- Check integrations table
SELECT 
    column_name,
    data_type,
    is_nullable,
    column_default
FROM information_schema.columns
WHERE table_schema = 'public' 
AND table_name = 'integrations'
ORDER BY ordinal_position;

-- =================================
-- STEP 7: Check if user_integrations table exists and its structure
-- =================================
SELECT 
    column_name,
    data_type,
    is_nullable,
    column_default
FROM information_schema.columns
WHERE table_schema = 'public' 
AND table_name = 'user_integrations'
ORDER BY ordinal_position;

-- =================================
-- STEP 8: Check RLS (Row Level Security) status
-- =================================
SELECT 
    t.schemaname,
    t.tablename,
    t.rowsecurity as rls_enabled,
    t.tableowner
FROM pg_tables t
WHERE t.schemaname = 'public'
AND t.tablename LIKE '%integration%'
ORDER BY t.tablename;

-- =================================
-- STEP 9: Check if data exists in the tables
-- =================================
-- Check integrations table (should have 6 default integrations)
SELECT 
    'integrations' as table_name,
    count(*) as record_count
FROM integrations
UNION ALL
-- Check user_integrations table (might be empty)
SELECT 
    'user_integrations' as table_name,
    count(*) as record_count
FROM user_integrations
UNION ALL
-- Check integration_logs table (might be empty)
SELECT 
    'integration_logs' as table_name,
    count(*) as record_count  
FROM integration_logs;

-- =================================
-- STEP 10: List available integrations (if table exists)
-- =================================
SELECT 
    id,
    name,
    category,
    status,
    created_at
FROM integrations 
ORDER BY name;

-- =================================
-- STEP 11: Check for any RLS policies
-- =================================
SELECT 
    schemaname,
    tablename,
    policyname,
    permissive,
    roles,
    cmd,
    qual
FROM pg_policies 
WHERE schemaname = 'public'
AND tablename LIKE '%integration%'
ORDER BY tablename, policyname;

-- =================================
-- STEP 12: Check sequence permissions (for UUID generation)
-- =================================
SELECT 
    sequence_schema,
    sequence_name,
    data_type,
    start_value,
    increment
FROM information_schema.sequences
WHERE sequence_schema = 'public'
ORDER BY sequence_name;

-- =================================
-- STEP 13: Test a simple SELECT on each integration table
-- =================================
-- This will help identify which specific table is causing the permission issue

-- Test integrations table
SELECT 'Testing integrations table...' as test;
SELECT count(*) as integrations_count FROM integrations;

-- Test user_integrations table  
SELECT 'Testing user_integrations table...' as test;
SELECT count(*) as user_integrations_count FROM user_integrations;

-- Test integration_logs table
SELECT 'Testing integration_logs table...' as test;
SELECT count(*) as integration_logs_count FROM integration_logs;

-- =================================
-- STEP 14: Check auth.users table access (to compare)
-- =================================
-- This should work since your app can authenticate
SELECT 'Testing auth.users access...' as test;
SELECT count(*) as users_count FROM auth.users;

-- =================================
-- STEP 15: Check your existing tables permissions (for comparison)
-- =================================
SELECT 
    table_schema,
    table_name,
    grantee,
    privilege_type
FROM information_schema.table_privileges 
WHERE table_schema = 'public' 
AND table_name IN ('projects', 'ad_analyses', 'user_profiles')
AND grantee IN ('authenticated', 'anon', 'service_role')
ORDER BY table_name, grantee;

-- =================================
-- DIAGNOSTIC COMPLETE
-- =================================
-- Run each section step by step and note any errors
-- This will help us understand exactly what's wrong