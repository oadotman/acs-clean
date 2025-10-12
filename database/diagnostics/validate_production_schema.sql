-- ============================================================================
-- AdCopySurge Production Schema Validation
-- Validates current database schema against production requirements
-- Run this in Supabase SQL Editor to check production readiness
-- ============================================================================

-- ============================================================================
-- PART 1: Core Tables Validation
-- ============================================================================

-- Check if all required tables exist
SELECT 
    'Table Existence Check' as check_type,
    table_name,
    CASE 
        WHEN table_name IS NOT NULL THEN '✅ EXISTS'
        ELSE '❌ MISSING'
    END as status
FROM (VALUES 
    ('user_profiles'),
    ('projects'), 
    ('ad_analyses'),
    ('competitor_benchmarks'),
    ('ad_generations')
) as required_tables(table_name)
LEFT JOIN information_schema.tables t 
    ON t.table_name = required_tables.table_name 
    AND t.table_schema = 'public'
ORDER BY required_tables.table_name;

-- ============================================================================
-- PART 2: Column Validation
-- ============================================================================

-- Check user_profiles columns
SELECT 
    'user_profiles columns' as check_type,
    column_name,
    data_type,
    is_nullable,
    column_default,
    CASE 
        WHEN column_name IN ('id', 'email', 'subscription_tier', 'monthly_analyses', 'created_at', 'updated_at') THEN '✅ REQUIRED'
        ELSE '🔄 OPTIONAL'
    END as requirement_status
FROM information_schema.columns 
WHERE table_name = 'user_profiles' AND table_schema = 'public'
ORDER BY ordinal_position;

-- Check projects columns  
SELECT 
    'projects columns' as check_type,
    column_name,
    data_type,
    is_nullable,
    column_default,
    CASE 
        WHEN column_name IN ('id', 'user_id', 'name', 'created_at', 'updated_at') THEN '✅ REQUIRED'
        ELSE '🔄 OPTIONAL'
    END as requirement_status
FROM information_schema.columns 
WHERE table_name = 'projects' AND table_schema = 'public'
ORDER BY ordinal_position;

-- Check ad_analyses columns (critical for production)
SELECT 
    'ad_analyses columns' as check_type,
    column_name,
    data_type,
    is_nullable,
    column_default,
    CASE 
        WHEN column_name IN ('id', 'user_id', 'headline', 'body_text', 'platform', 'created_at', 'updated_at') THEN '✅ REQUIRED'
        WHEN column_name IN ('cta_strength_score', 'target_audience', 'industry', 'analysis_data') THEN '⚠️ PRODUCTION CRITICAL'
        ELSE '🔄 OPTIONAL'
    END as requirement_status
FROM information_schema.columns 
WHERE table_name = 'ad_analyses' AND table_schema = 'public'
ORDER BY ordinal_position;

-- ============================================================================
-- PART 3: Index Validation (Performance Critical)
-- ============================================================================

-- Check for required indexes
SELECT 
    'Index Check' as check_type,
    tablename,
    indexname,
    indexdef,
    CASE 
        WHEN indexname LIKE '%user_id%' THEN '✅ USER FILTERING'
        WHEN indexname LIKE '%created_at%' THEN '✅ TIME SORTING'
        WHEN indexname LIKE '%platform%' OR indexname LIKE '%industry%' THEN '✅ CATEGORY FILTERING'
        ELSE '🔄 GENERAL'
    END as performance_impact
FROM pg_indexes 
WHERE tablename IN ('user_profiles', 'projects', 'ad_analyses', 'competitor_benchmarks', 'ad_generations')
    AND schemaname = 'public'
ORDER BY tablename, indexname;

-- ============================================================================
-- PART 4: Constraint Validation
-- ============================================================================

-- Check foreign key constraints
SELECT 
    'Foreign Key Constraints' as check_type,
    tc.table_name,
    tc.constraint_name,
    kcu.column_name,
    ccu.table_name AS foreign_table_name,
    ccu.column_name AS foreign_column_name,
    '✅ REFERENTIAL INTEGRITY' as status
FROM information_schema.table_constraints AS tc
JOIN information_schema.key_column_usage AS kcu
    ON tc.constraint_name = kcu.constraint_name
JOIN information_schema.constraint_column_usage AS ccu
    ON ccu.constraint_name = tc.constraint_name
WHERE tc.constraint_type = 'FOREIGN KEY'
    AND tc.table_name IN ('projects', 'ad_analyses', 'competitor_benchmarks', 'ad_generations');

-- Check for NOT NULL constraints on critical columns
SELECT 
    'NOT NULL Constraints' as check_type,
    table_name,
    column_name,
    CASE 
        WHEN is_nullable = 'NO' THEN '✅ NOT NULL'
        ELSE '⚠️ NULLABLE'
    END as constraint_status,
    CASE 
        WHEN table_name = 'ad_analyses' AND column_name IN ('headline', 'body_text', 'platform', 'user_id') AND is_nullable = 'YES' 
            THEN '❌ CRITICAL: Should be NOT NULL'
        WHEN table_name = 'projects' AND column_name IN ('name', 'user_id') AND is_nullable = 'YES' 
            THEN '❌ CRITICAL: Should be NOT NULL'
        WHEN table_name = 'user_profiles' AND column_name IN ('id', 'subscription_tier') AND is_nullable = 'YES' 
            THEN '❌ CRITICAL: Should be NOT NULL'
        ELSE '✅ OK'
    END as production_readiness
FROM information_schema.columns 
WHERE table_name IN ('user_profiles', 'projects', 'ad_analyses')
    AND table_schema = 'public'
    AND column_name IN ('id', 'user_id', 'name', 'headline', 'body_text', 'platform', 'subscription_tier')
ORDER BY table_name, column_name;

-- ============================================================================
-- PART 5: RLS and Permissions Check
-- ============================================================================

-- Check Row Level Security status (should be DISABLED for current setup)
SELECT 
    'Row Level Security' as check_type,
    schemaname,
    tablename,
    rowsecurity as rls_enabled,
    CASE 
        WHEN rowsecurity = false THEN '✅ DISABLED (As expected)'
        ELSE '⚠️ ENABLED (Check if needed)'
    END as status
FROM pg_tables 
WHERE tablename IN ('user_profiles', 'projects', 'ad_analyses', 'competitor_benchmarks', 'ad_generations')
ORDER BY tablename;

-- Check table permissions
SELECT 
    'Table Permissions' as check_type,
    grantee,
    table_name,
    privilege_type,
    CASE 
        WHEN grantee = 'authenticated' AND privilege_type = 'SELECT' THEN '✅ READ ACCESS'
        WHEN grantee = 'authenticated' AND privilege_type = 'INSERT' THEN '✅ WRITE ACCESS' 
        WHEN grantee = 'authenticated' AND privilege_type = 'UPDATE' THEN '✅ UPDATE ACCESS'
        WHEN grantee = 'authenticated' AND privilege_type = 'DELETE' THEN '✅ DELETE ACCESS'
        ELSE '🔄 OTHER'
    END as access_level
FROM information_schema.role_table_grants 
WHERE table_name IN ('user_profiles', 'projects', 'ad_analyses', 'competitor_benchmarks', 'ad_generations')
    AND grantee IN ('anon', 'authenticated', 'service_role')
ORDER BY table_name, grantee, privilege_type;

-- ============================================================================
-- PART 6: Data Integrity Check
-- ============================================================================

-- Check for data without required fields (potential production issues)
SELECT 
    'Data Integrity Issues' as check_type,
    'ad_analyses' as table_name,
    'Missing Headlines' as issue_type,
    COUNT(*) as count,
    CASE WHEN COUNT(*) = 0 THEN '✅ CLEAN' ELSE '⚠️ NEEDS FIXING' END as status
FROM ad_analyses 
WHERE headline IS NULL OR headline = '';

SELECT 
    'Data Integrity Issues' as check_type,
    'ad_analyses' as table_name,
    'Missing Body Text' as issue_type,
    COUNT(*) as count,
    CASE WHEN COUNT(*) = 0 THEN '✅ CLEAN' ELSE '⚠️ NEEDS FIXING' END as status
FROM ad_analyses 
WHERE body_text IS NULL OR body_text = '';

SELECT 
    'Data Integrity Issues' as check_type,
    'ad_analyses' as table_name,
    'Missing Platform' as issue_type,
    COUNT(*) as count,
    CASE WHEN COUNT(*) = 0 THEN '✅ CLEAN' ELSE '⚠️ NEEDS FIXING' END as status
FROM ad_analyses 
WHERE platform IS NULL OR platform = '';

-- ============================================================================
-- PART 7: Production Readiness Summary
-- ============================================================================

-- Overall production readiness check
WITH schema_health AS (
    SELECT 
        COUNT(*) as total_tables,
        COUNT(*) FILTER (WHERE table_name IN ('user_profiles', 'projects', 'ad_analyses')) as core_tables
    FROM information_schema.tables 
    WHERE table_schema = 'public' 
        AND table_name IN ('user_profiles', 'projects', 'ad_analyses', 'competitor_benchmarks', 'ad_generations')
),
index_health AS (
    SELECT 
        COUNT(*) as total_indexes,
        COUNT(*) FILTER (WHERE indexname LIKE '%user_id%') as user_indexes,
        COUNT(*) FILTER (WHERE indexname LIKE '%created_at%') as time_indexes
    FROM pg_indexes 
    WHERE tablename IN ('user_profiles', 'projects', 'ad_analyses')
),
constraint_health AS (
    SELECT 
        COUNT(*) as total_fks
    FROM information_schema.table_constraints 
    WHERE constraint_type = 'FOREIGN KEY' 
        AND table_name IN ('projects', 'ad_analyses', 'competitor_benchmarks', 'ad_generations')
)
SELECT 
    'PRODUCTION READINESS SUMMARY' as check_type,
    CASE 
        WHEN sh.core_tables = 3 AND ih.user_indexes > 0 AND ih.time_indexes > 0 AND ch.total_fks > 0 
            THEN '🎉 READY FOR PRODUCTION'
        WHEN sh.core_tables = 3 AND ih.user_indexes > 0 
            THEN '⚠️ MOSTLY READY (Minor issues)'
        ELSE '❌ NOT READY (Critical issues)'
    END as status,
    sh.total_tables as tables_created,
    ih.total_indexes as indexes_created,
    ch.total_fks as foreign_keys_created
FROM schema_health sh, index_health ih, constraint_health ch;

-- ============================================================================
-- PART 8: Recommended Actions
-- ============================================================================

-- Show recommended actions based on current state
SELECT 
    'RECOMMENDED ACTIONS' as action_type,
    'Add missing indexes for performance' as action,
    '⚠️ PERFORMANCE' as priority
WHERE NOT EXISTS (
    SELECT 1 FROM pg_indexes 
    WHERE tablename = 'ad_analyses' AND indexname LIKE '%platform%'
)

UNION ALL

SELECT 
    'RECOMMENDED ACTIONS' as action_type,
    'Add NOT NULL constraints to critical columns' as action,
    '❌ CRITICAL' as priority
WHERE EXISTS (
    SELECT 1 FROM information_schema.columns 
    WHERE table_name = 'ad_analyses' 
        AND column_name IN ('headline', 'body_text', 'platform')
        AND is_nullable = 'YES'
)

UNION ALL

SELECT 
    'RECOMMENDED ACTIONS' as action_type,
    'Remove test/demo data before production' as action,
    '⚠️ DATA CLEANLINESS' as priority

UNION ALL

SELECT 
    'RECOMMENDED ACTIONS' as action_type,
    'Verify all backend model fields exist in database' as action,
    '⚠️ API COMPATIBILITY' as priority;