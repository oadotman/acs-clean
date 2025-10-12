-- SUPABASE DATABASE AUDIT SCRIPT
-- Run this in your Supabase SQL Editor to see exactly what exists

-- ==============================================================================
-- 1. LIST ALL TABLES IN PUBLIC SCHEMA
-- ==============================================================================
SELECT 
    '=== PUBLIC SCHEMA TABLES ===' as info,
    table_name,
    table_type
FROM information_schema.tables 
WHERE table_schema = 'public'
ORDER BY table_name;

-- ==============================================================================
-- 2. DETAILED COLUMN INFO FOR ALL RELEVANT TABLES
-- ==============================================================================
SELECT 
    '=== TABLE COLUMNS DETAILS ===' as info,
    table_name,
    column_name,
    data_type,
    character_maximum_length,
    is_nullable,
    column_default
FROM information_schema.columns 
WHERE table_schema = 'public' 
    AND table_name IN ('users', 'ad_analyses', 'projects', 'agencies', 'agency_team_members')
ORDER BY table_name, ordinal_position;

-- ==============================================================================
-- 3. CHECK FOR FOREIGN KEY CONSTRAINTS
-- ==============================================================================
SELECT 
    '=== FOREIGN KEY CONSTRAINTS ===' as info,
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
    AND tc.table_schema = 'public';

-- ==============================================================================
-- 4. CHECK FOR INDEXES
-- ==============================================================================
SELECT 
    '=== INDEXES ===' as info,
    schemaname,
    tablename,
    indexname,
    indexdef
FROM pg_indexes 
WHERE schemaname = 'public'
ORDER BY tablename, indexname;

-- ==============================================================================
-- 5. CHECK FOR ROW LEVEL SECURITY (RLS) POLICIES
-- ==============================================================================
SELECT 
    '=== RLS POLICIES ===' as info,
    schemaname,
    tablename,
    policyname,
    permissive,
    roles,
    cmd,
    qual,
    with_check
FROM pg_policies 
WHERE schemaname = 'public';

-- ==============================================================================
-- 6. CHECK FOR STORED FUNCTIONS/PROCEDURES
-- ==============================================================================
SELECT 
    '=== STORED FUNCTIONS ===' as info,
    routine_name,
    routine_type,
    data_type as return_type,
    routine_definition
FROM information_schema.routines 
WHERE routine_schema = 'public'
    AND (routine_name LIKE '%metric%' 
    OR routine_name LIKE '%dashboard%'
    OR routine_name LIKE '%analys%');

-- ==============================================================================
-- 7. CHECK RLS STATUS ON TABLES
-- ==============================================================================
SELECT 
    '=== RLS STATUS ===' as info,
    schemaname,
    tablename,
    rowsecurity as rls_enabled
FROM pg_tables 
WHERE schemaname = 'public'
ORDER BY tablename;

-- ==============================================================================
-- 8. CHECK FOR TRIGGERS
-- ==============================================================================
SELECT 
    '=== TRIGGERS ===' as info,
    event_object_schema,
    event_object_table,
    trigger_name,
    event_manipulation,
    action_timing,
    action_statement
FROM information_schema.triggers
WHERE event_object_schema = 'public';

-- ==============================================================================
-- 9. COUNT RECORDS IN EACH TABLE (to see if there's existing data)
-- ==============================================================================
DO $$
DECLARE
    table_record RECORD;
    row_count INTEGER;
BEGIN
    RAISE NOTICE '=== RECORD COUNTS ===';
    
    FOR table_record IN 
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public' 
        AND table_type = 'BASE TABLE'
    LOOP
        EXECUTE 'SELECT COUNT(*) FROM ' || quote_ident(table_record.table_name) INTO row_count;
        RAISE NOTICE 'Table: % has % records', table_record.table_name, row_count;
    END LOOP;
END $$;

-- ==============================================================================
-- 10. CHECK AUTH SCHEMA (to understand user authentication setup)
-- ==============================================================================
SELECT 
    '=== AUTH SCHEMA TABLES ===' as info,
    table_name
FROM information_schema.tables 
WHERE table_schema = 'auth'
ORDER BY table_name;

-- ==============================================================================
-- 11. CHECK IF THERE'S A CONNECTION BETWEEN PUBLIC.USERS AND AUTH.USERS
-- ==============================================================================
-- This will show the structure of the users table to see how it relates to auth
SELECT 
    '=== USERS TABLE STRUCTURE ===' as info,
    column_name,
    data_type,
    is_nullable,
    column_default
FROM information_schema.columns 
WHERE table_schema = 'public' 
    AND table_name = 'users'
ORDER BY ordinal_position;

-- ==============================================================================
-- 12. SAMPLE DATA FROM KEY TABLES (first 3 records, no sensitive data)
-- ==============================================================================
DO $$
BEGIN
    -- Check if users table exists and has data
    IF EXISTS (SELECT FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'users') THEN
        RAISE NOTICE '=== SAMPLE USERS DATA (PUBLIC SCHEMA) ===';
        PERFORM 1; -- This is just to make the block valid
        -- Note: We'll handle actual data display separately since RAISE NOTICE can't show query results
    ELSE
        RAISE NOTICE '=== USERS TABLE === Not found in public schema';
    END IF;
    
    -- Check if ad_analyses table exists and has data
    IF EXISTS (SELECT FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'ad_analyses') THEN
        RAISE NOTICE '=== AD_ANALYSES TABLE === Found in public schema';
    ELSE
        RAISE NOTICE '=== AD_ANALYSES TABLE === Not found in public schema';
    END IF;
    
    -- Check auth.users table (Supabase default)
    IF EXISTS (SELECT FROM information_schema.tables WHERE table_schema = 'auth' AND table_name = 'users') THEN
        RAISE NOTICE '=== AUTH.USERS TABLE === Found (this is normal for Supabase)';
    ELSE
        RAISE NOTICE '=== AUTH.USERS TABLE === Not found';
    END IF;
END $$;

-- ==============================================================================
-- FINAL SUMMARY
-- ==============================================================================
SELECT 
    '=== AUDIT COMPLETE ===' as info,
    'Check the results above to understand your current database structure' as next_step;