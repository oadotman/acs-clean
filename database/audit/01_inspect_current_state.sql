-- ============================================================================
-- DATABASE STATE AUDIT SCRIPT
-- Run this in Supabase SQL Editor to understand current state
-- BEFORE making any changes
-- ============================================================================

-- ============================================================================
-- 1. INSPECT EXISTING TABLES
-- ============================================================================

SELECT 
    '=== EXISTING TABLES ===' as section,
    table_name,
    table_type
FROM information_schema.tables
WHERE table_schema = 'public'
    AND table_name IN (
        'agencies',
        'agency_team_members',
        'agency_invitations',
        'user_profiles',
        'user_credits',
        'credit_transactions',
        'projects',
        'team_roles'
    )
ORDER BY table_name;

-- ============================================================================
-- 2. INSPECT AGENCY TEAM MEMBERS TABLE STRUCTURE
-- ============================================================================

SELECT 
    '=== AGENCY_TEAM_MEMBERS COLUMNS ===' as section,
    column_name,
    data_type,
    is_nullable,
    column_default
FROM information_schema.columns
WHERE table_schema = 'public'
    AND table_name = 'agency_team_members'
ORDER BY ordinal_position;

-- ============================================================================
-- 3. INSPECT EXISTING RLS POLICIES (THE PROBLEM AREA)
-- ============================================================================

SELECT 
    '=== CURRENT RLS POLICIES ===' as section,
    schemaname,
    tablename,
    policyname,
    permissive,
    roles,
    cmd,
    qual as using_expression,
    with_check as check_expression
FROM pg_policies
WHERE schemaname = 'public'
    AND tablename IN (
        'agencies',
        'agency_team_members',
        'agency_invitations',
        'user_credits',
        'credit_transactions'
    )
ORDER BY tablename, policyname;

-- ============================================================================
-- 4. CHECK FOR RECURSIVE POLICY PATTERNS (LIKELY CULPRIT)
-- ============================================================================

SELECT 
    '=== POTENTIALLY RECURSIVE POLICIES ===' as section,
    tablename,
    policyname,
    qual as policy_definition
FROM pg_policies
WHERE schemaname = 'public'
    AND tablename = 'agency_team_members'
    AND (
        qual LIKE '%agency_team_members%' -- Self-referencing in USING clause
        OR with_check LIKE '%agency_team_members%' -- Self-referencing in CHECK clause
    );

-- ============================================================================
-- 5. INSPECT EXISTING HELPER FUNCTIONS
-- ============================================================================

SELECT 
    '=== EXISTING HELPER FUNCTIONS ===' as section,
    routine_name as function_name,
    routine_type,
    security_type,
    data_type as return_type
FROM information_schema.routines
WHERE routine_schema = 'public'
    AND (
        routine_name LIKE '%agency%'
        OR routine_name LIKE '%team%'
        OR routine_name LIKE '%member%'
    )
ORDER BY routine_name;

-- ============================================================================
-- 6. CHECK FOREIGN KEY RELATIONSHIPS
-- ============================================================================

SELECT 
    '=== FOREIGN KEY CONSTRAINTS ===' as section,
    tc.table_name,
    kcu.column_name,
    ccu.table_name AS foreign_table_name,
    ccu.column_name AS foreign_column_name,
    tc.constraint_name
FROM information_schema.table_constraints AS tc
JOIN information_schema.key_column_usage AS kcu
    ON tc.constraint_name = kcu.constraint_name
JOIN information_schema.constraint_column_usage AS ccu
    ON ccu.constraint_name = tc.constraint_name
WHERE tc.constraint_type = 'FOREIGN KEY'
    AND tc.table_name IN (
        'agencies',
        'agency_team_members',
        'agency_invitations',
        'user_credits'
    )
ORDER BY tc.table_name, kcu.column_name;

-- ============================================================================
-- 7. CHECK CURRENT DATA IN CRITICAL TABLES
-- ============================================================================

-- Count agencies
SELECT 
    '=== DATA COUNT: AGENCIES ===' as section,
    COUNT(*) as total_agencies,
    COUNT(DISTINCT owner_id) as unique_owners
FROM agencies;

-- Count team members
SELECT 
    '=== DATA COUNT: TEAM MEMBERS ===' as section,
    COUNT(*) as total_team_members,
    COUNT(DISTINCT agency_id) as agencies_with_members,
    COUNT(CASE WHEN status = 'active' THEN 1 END) as active_members,
    COUNT(CASE WHEN status = 'pending' THEN 1 END) as pending_members
FROM agency_team_members;

-- Count invitations
SELECT 
    '=== DATA COUNT: INVITATIONS ===' as section,
    COUNT(*) as total_invitations,
    COUNT(CASE WHEN status = 'pending' THEN 1 END) as pending_invitations,
    COUNT(CASE WHEN status = 'accepted' THEN 1 END) as accepted_invitations,
    COUNT(CASE WHEN status = 'expired' THEN 1 END) as expired_invitations
FROM agency_invitations;

-- Check user credits
SELECT 
    '=== DATA COUNT: USER CREDITS ===' as section,
    COUNT(*) as total_users_with_credits,
    COUNT(CASE WHEN subscription_tier = 'free' THEN 1 END) as free_tier_users,
    COUNT(CASE WHEN subscription_tier LIKE 'agency%' THEN 1 END) as agency_tier_users,
    SUM(current_credits) as total_credits_in_system
FROM user_credits;

-- ============================================================================
-- 8. CHECK FOR TRIGGERS
-- ============================================================================

SELECT 
    '=== TRIGGERS ON TEAM TABLES ===' as section,
    trigger_name,
    event_manipulation,
    event_object_table,
    action_statement,
    action_timing
FROM information_schema.triggers
WHERE event_object_schema = 'public'
    AND event_object_table IN (
        'agencies',
        'agency_team_members',
        'agency_invitations',
        'user_credits'
    )
ORDER BY event_object_table, trigger_name;

-- ============================================================================
-- 9. TEST SIMPLE QUERY TO DETECT RECURSION ERROR
-- ============================================================================

-- This query will show if we have the recursion problem
-- If you get error 42P17, we confirmed the issue
SELECT 
    '=== RECURSION TEST ===' as section,
    'Attempting to query agency_team_members...' as test_status;

-- Try to select from agency_team_members
-- If this fails with "infinite recursion detected" -> RLS policy problem confirmed
SELECT 
    id,
    agency_id,
    user_id,
    role,
    status
FROM agency_team_members
LIMIT 5;

-- ============================================================================
-- 10. CHECK USER PROFILES STRUCTURE
-- ============================================================================

SELECT 
    '=== USER_PROFILES COLUMNS ===' as section,
    column_name,
    data_type,
    is_nullable
FROM information_schema.columns
WHERE table_schema = 'public'
    AND table_name = 'user_profiles'
    AND column_name IN (
        'id',
        'subscription_tier',
        'tier',
        'agency_id',
        'can_create_agency',
        'monthly_analysis_limit'
    )
ORDER BY ordinal_position;

-- ============================================================================
-- SUMMARY INSTRUCTIONS
-- ============================================================================

SELECT 
    '=== AUDIT COMPLETE ===' as section,
    'Review the output above to understand:
    1. Which tables exist
    2. Current RLS policies (especially recursive ones)
    3. Existing helper functions
    4. Data volumes in each table
    5. Any recursion errors from the test query
    
    Save this output before proceeding with fixes!' as next_steps;
