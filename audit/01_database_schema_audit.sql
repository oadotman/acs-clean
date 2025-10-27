-- ============================================================================
-- DATABASE SCHEMA AUDIT
-- Run these queries in Supabase SQL Editor to understand the current database state
-- ============================================================================

-- ============================================================================
-- QUERY 1: Check if user_profiles table exists and get its complete schema
-- ============================================================================
SELECT 
    column_name,
    data_type,
    character_maximum_length,
    column_default,
    is_nullable,
    CASE 
        WHEN column_name = 'id' THEN '✓ PRIMARY KEY'
        ELSE ''
    END as key_info
FROM information_schema.columns
WHERE table_schema = 'public' 
    AND table_name = 'user_profiles'
ORDER BY ordinal_position;

-- Expected output: All columns in user_profiles including subscription_tier, agency_id, etc.

-- ============================================================================
-- QUERY 2: Check if user_credits table exists and get its complete schema
-- ============================================================================
SELECT 
    column_name,
    data_type,
    character_maximum_length,
    column_default,
    is_nullable,
    CASE 
        WHEN column_name = 'id' THEN '✓ PRIMARY KEY'
        WHEN column_name = 'user_id' THEN '✓ FOREIGN KEY → user_profiles(id)'
        ELSE ''
    END as key_info
FROM information_schema.columns
WHERE table_schema = 'public' 
    AND table_name = 'user_credits'
ORDER BY ordinal_position;

-- Expected output: All columns in user_credits including subscription_tier, current_credits, etc.

-- ============================================================================
-- QUERY 3: Check if subscription_tiers table exists and get its schema
-- ============================================================================
SELECT 
    column_name,
    data_type,
    character_maximum_length,
    column_default,
    is_nullable
FROM information_schema.columns
WHERE table_schema = 'public' 
    AND table_name = 'subscription_tiers'
ORDER BY ordinal_position;

-- Expected output: Columns in subscription_tiers reference table

-- ============================================================================
-- QUERY 4: Get all foreign key relationships for user_profiles and user_credits
-- ============================================================================
SELECT
    tc.table_name as source_table,
    kcu.column_name as source_column,
    ccu.table_name AS foreign_table,
    ccu.column_name AS foreign_column,
    tc.constraint_name
FROM information_schema.table_constraints AS tc
JOIN information_schema.key_column_usage AS kcu
    ON tc.constraint_name = kcu.constraint_name
    AND tc.table_schema = kcu.table_schema
JOIN information_schema.constraint_column_usage AS ccu
    ON ccu.constraint_name = tc.constraint_name
    AND ccu.table_schema = tc.table_schema
WHERE tc.constraint_type = 'FOREIGN KEY' 
    AND tc.table_schema = 'public'
    AND (tc.table_name IN ('user_profiles', 'user_credits'))
ORDER BY tc.table_name;

-- Expected output: Foreign key relationships (user_credits.user_id → user_profiles.id, etc.)

-- ============================================================================
-- QUERY 5: Get all constraints on user_profiles table
-- ============================================================================
SELECT
    tc.constraint_name,
    tc.constraint_type,
    kcu.column_name,
    cc.check_clause
FROM information_schema.table_constraints AS tc
LEFT JOIN information_schema.key_column_usage AS kcu
    ON tc.constraint_name = kcu.constraint_name
    AND tc.table_schema = kcu.table_schema
LEFT JOIN information_schema.check_constraints AS cc
    ON tc.constraint_name = cc.constraint_name
WHERE tc.table_schema = 'public'
    AND tc.table_name = 'user_profiles'
ORDER BY tc.constraint_type, tc.constraint_name;

-- Expected output: All constraints including CHECK constraints on subscription_tier

-- ============================================================================
-- QUERY 6: Get all constraints on user_credits table
-- ============================================================================
SELECT
    tc.constraint_name,
    tc.constraint_type,
    kcu.column_name,
    cc.check_clause
FROM information_schema.table_constraints AS tc
LEFT JOIN information_schema.key_column_usage AS kcu
    ON tc.constraint_name = kcu.constraint_name
    AND tc.table_schema = kcu.table_schema
LEFT JOIN information_schema.check_constraints AS cc
    ON tc.constraint_name = cc.constraint_name
WHERE tc.table_schema = 'public'
    AND tc.table_name = 'user_credits'
ORDER BY tc.constraint_type, tc.constraint_name;

-- Expected output: All constraints on user_credits

-- ============================================================================
-- QUERY 7: Check for database triggers on user_profiles
-- ============================================================================
SELECT
    trigger_name,
    event_manipulation as event,
    event_object_table as table_name,
    action_statement,
    action_timing as timing
FROM information_schema.triggers
WHERE event_object_schema = 'public'
    AND event_object_table = 'user_profiles'
ORDER BY trigger_name;

-- Expected output: Any triggers that fire on user_profiles changes

-- ============================================================================
-- QUERY 8: Check for database triggers on user_credits
-- ============================================================================
SELECT
    trigger_name,
    event_manipulation as event,
    event_object_table as table_name,
    action_statement,
    action_timing as timing
FROM information_schema.triggers
WHERE event_object_schema = 'public'
    AND event_object_table = 'user_credits'
ORDER BY trigger_name;

-- Expected output: Any triggers that fire on user_credits changes

-- ============================================================================
-- QUERY 9: List all custom functions related to user profiles or credits
-- ============================================================================
SELECT
    routine_name as function_name,
    routine_type,
    data_type as return_type,
    routine_definition as definition_preview
FROM information_schema.routines
WHERE routine_schema = 'public'
    AND (
        routine_name ILIKE '%user%'
        OR routine_name ILIKE '%credit%'
        OR routine_name ILIKE '%subscription%'
        OR routine_name ILIKE '%tier%'
    )
ORDER BY routine_name;

-- Expected output: Functions like initialize_user_credits, update_subscription_tier, etc.

-- ============================================================================
-- QUERY 10: Check subscription_tiers configuration (if table exists)
-- ============================================================================
SELECT 
    id,
    name,
    price_monthly,
    analysis_limit,
    can_create_agency,
    max_team_members,
    features,
    is_active
FROM subscription_tiers
WHERE is_active = true
ORDER BY price_monthly;

-- Expected output: All active subscription tier configurations

-- ============================================================================
-- QUERY 11: Sample user_profiles data (showing tier information)
-- ============================================================================
SELECT 
    id,
    email,
    subscription_tier,
    monthly_analysis_limit,
    monthly_analyses_used,
    can_create_agency,
    agency_id,
    created_at
FROM user_profiles
ORDER BY created_at DESC
LIMIT 5;

-- Expected output: Sample of actual user records with their tier information

-- ============================================================================
-- QUERY 12: Sample user_credits data
-- ============================================================================
SELECT 
    id,
    user_id,
    current_credits,
    monthly_allowance,
    subscription_tier,
    bonus_credits,
    total_used,
    last_reset,
    created_at
FROM user_credits
ORDER BY created_at DESC
LIMIT 5;

-- Expected output: Sample of actual user credit records

-- ============================================================================
-- QUERY 13: Check for tier mismatches between user_profiles and user_credits
-- ============================================================================
SELECT 
    up.id as user_id,
    up.email,
    up.subscription_tier as profile_tier,
    uc.subscription_tier as credits_tier,
    CASE 
        WHEN up.subscription_tier = uc.subscription_tier THEN '✓ MATCH'
        ELSE '✗ MISMATCH'
    END as sync_status,
    up.monthly_analysis_limit as profile_limit,
    uc.monthly_allowance as credits_allowance
FROM user_profiles up
LEFT JOIN user_credits uc ON up.id = uc.user_id
WHERE up.subscription_tier IS NOT NULL
ORDER BY 
    CASE WHEN up.subscription_tier != uc.subscription_tier THEN 0 ELSE 1 END,
    up.created_at DESC
LIMIT 20;

-- Expected output: Shows which users have mismatched tier data between tables

-- ============================================================================
-- QUERY 14: Find users with missing credit records
-- ============================================================================
SELECT 
    up.id,
    up.email,
    up.subscription_tier,
    up.created_at
FROM user_profiles up
LEFT JOIN user_credits uc ON up.id = uc.user_id
WHERE uc.id IS NULL
ORDER BY up.created_at DESC
LIMIT 10;

-- Expected output: Users who don't have corresponding user_credits records

-- ============================================================================
-- QUERY 15: Check Row Level Security (RLS) policies on user_profiles
-- ============================================================================
SELECT 
    schemaname,
    tablename,
    policyname,
    permissive,
    roles,
    cmd,
    qual as using_expression,
    with_check as with_check_expression
FROM pg_policies
WHERE schemaname = 'public'
    AND tablename = 'user_profiles'
ORDER BY policyname;

-- Expected output: All RLS policies protecting user_profiles table

-- ============================================================================
-- QUERY 16: Check Row Level Security (RLS) policies on user_credits
-- ============================================================================
SELECT 
    schemaname,
    tablename,
    policyname,
    permissive,
    roles,
    cmd,
    qual as using_expression,
    with_check as with_check_expression
FROM pg_policies
WHERE schemaname = 'public'
    AND tablename = 'user_credits'
ORDER BY policyname;

-- Expected output: All RLS policies protecting user_credits table

-- ============================================================================
-- QUERY 17: Check if RLS is enabled on these tables
-- ============================================================================
SELECT 
    schemaname,
    tablename,
    rowsecurity as rls_enabled
FROM pg_tables
WHERE schemaname = 'public'
    AND tablename IN ('user_profiles', 'user_credits', 'subscription_tiers')
ORDER BY tablename;

-- Expected output: Whether RLS is enabled (true/false) for each table

-- ============================================================================
-- QUERY 18: Get index information for performance analysis
-- ============================================================================
SELECT
    schemaname,
    tablename,
    indexname,
    indexdef
FROM pg_indexes
WHERE schemaname = 'public'
    AND tablename IN ('user_profiles', 'user_credits')
ORDER BY tablename, indexname;

-- Expected output: All indexes on user_profiles and user_credits tables

-- ============================================================================
-- INSTRUCTIONS FOR RUNNING THESE QUERIES
-- ============================================================================
-- 
-- 1. Copy each query section individually into Supabase SQL Editor
-- 2. Run each query and save the output
-- 3. Some queries might return empty results if tables don't exist - that's OK
-- 4. Pay special attention to QUERY 13 (mismatches) and QUERY 14 (missing records)
-- 5. The results will show the actual state of your database schema
--
-- ============================================================================
