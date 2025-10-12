-- ============================================================================
-- AdCopySurge Production Data Purging Scripts
-- Removes all test, demo, and development data before production deployment
-- RUN THESE SCRIPTS IN ORDER - STAGING FIRST, THEN PRODUCTION
-- ============================================================================

-- ============================================================================
-- PART 1: BACKUP VERIFICATION
-- ============================================================================

-- First, verify we have a recent backup
-- IMPORTANT: CREATE A FULL DATABASE BACKUP BEFORE RUNNING THESE SCRIPTS

SELECT 
    'BACKUP CHECK' as script_phase,
    'CRITICAL: Ensure you have created a full database backup before proceeding' as warning,
    NOW() as current_time,
    'Run: pg_dump your_database > backup_' || TO_CHAR(NOW(), 'YYYY_MM_DD_HH24_MI') || '.sql' as backup_command;

-- ============================================================================
-- PART 2: IDENTIFY TEST DATA (DRY RUN)
-- ============================================================================

-- Check for test/demo users (common patterns)
SELECT 
    'TEST DATA DETECTION' as check_type,
    'user_profiles' as table_name,
    id,
    email,
    subscription_tier,
    monthly_analyses,
    created_at,
    'TEST USER CANDIDATE' as reason
FROM user_profiles 
WHERE 
    email ILIKE '%test%' 
    OR email ILIKE '%demo%' 
    OR email ILIKE '%example.com%' 
    OR email ILIKE '%sample%'
    OR email ILIKE '%placeholder%'
    OR email = 'user@example.com'
    OR id = '00000000-0000-0000-0000-000000000000'
ORDER BY created_at;

-- Check for projects with test/demo names
SELECT 
    'TEST DATA DETECTION' as check_type,
    'projects' as table_name,
    p.id,
    p.user_id,
    p.name,
    p.description,
    p.client_name,
    p.created_at,
    CASE 
        WHEN p.name ILIKE '%test%' THEN 'TEST PROJECT NAME'
        WHEN p.name ILIKE '%demo%' THEN 'DEMO PROJECT NAME'
        WHEN p.name ILIKE '%sample%' THEN 'SAMPLE PROJECT NAME'
        WHEN p.description ILIKE '%debug%' THEN 'DEBUG PROJECT'
        WHEN p.client_name ILIKE '%debug%' THEN 'DEBUG CLIENT'
        WHEN up.email ILIKE '%test%' THEN 'BELONGS TO TEST USER'
        ELSE 'OTHER TEST INDICATOR'
    END as reason
FROM projects p
LEFT JOIN user_profiles up ON p.user_id = up.id
WHERE 
    p.name ILIKE '%test%' 
    OR p.name ILIKE '%demo%' 
    OR p.name ILIKE '%sample%'
    OR p.description ILIKE '%debug%'
    OR p.client_name ILIKE '%debug%'
    OR up.email ILIKE '%test%'
    OR up.email ILIKE '%demo%'
    OR up.email ILIKE '%example.com%'
    OR p.user_id = '00000000-0000-0000-0000-000000000000'
ORDER BY p.created_at;

-- Check for ad analyses with test/demo content
SELECT 
    'TEST DATA DETECTION' as check_type,
    'ad_analyses' as table_name,
    aa.id,
    aa.user_id,
    aa.headline,
    LEFT(aa.body_text, 100) || '...' as body_preview,
    aa.platform,
    aa.created_at,
    CASE 
        WHEN aa.headline ILIKE '%test%' THEN 'TEST HEADLINE'
        WHEN aa.headline ILIKE '%demo%' THEN 'DEMO HEADLINE'
        WHEN aa.headline ILIKE '%sample%' THEN 'SAMPLE HEADLINE'
        WHEN aa.body_text ILIKE '%test%' THEN 'TEST BODY'
        WHEN aa.body_text ILIKE '%debug%' THEN 'DEBUG CONTENT'
        WHEN aa.headline = 'Amazing Product Launch' THEN 'DEFAULT SAMPLE'
        WHEN up.email ILIKE '%test%' THEN 'BELONGS TO TEST USER'
        ELSE 'OTHER TEST INDICATOR'
    END as reason
FROM ad_analyses aa
LEFT JOIN user_profiles up ON aa.user_id = up.id
WHERE 
    aa.headline ILIKE '%test%' 
    OR aa.headline ILIKE '%demo%' 
    OR aa.headline ILIKE '%sample%'
    OR aa.body_text ILIKE '%test%'
    OR aa.body_text ILIKE '%debug%'
    OR aa.body_text ILIKE '%lorem ipsum%'
    OR aa.headline = 'Amazing Product Launch'
    OR aa.headline = '50% Off Everything - Limited Time Only!'
    OR up.email ILIKE '%test%'
    OR up.email ILIKE '%demo%'
    OR up.email ILIKE '%example.com%'
    OR aa.user_id = '00000000-0000-0000-0000-000000000000'
ORDER BY aa.created_at;

-- Check for old/stale data (potentially test data from development)
SELECT 
    'STALE DATA DETECTION' as check_type,
    table_name,
    count,
    age_days,
    'POTENTIALLY OLD TEST DATA' as reason
FROM (
    SELECT 
        'user_profiles' as table_name,
        COUNT(*) as count,
        EXTRACT(DAY FROM NOW() - MIN(created_at)) as age_days
    FROM user_profiles 
    WHERE created_at < NOW() - INTERVAL '90 days'
    
    UNION ALL
    
    SELECT 
        'projects' as table_name,
        COUNT(*) as count,
        EXTRACT(DAY FROM NOW() - MIN(created_at)) as age_days
    FROM projects 
    WHERE created_at < NOW() - INTERVAL '90 days'
    
    UNION ALL
    
    SELECT 
        'ad_analyses' as table_name,
        COUNT(*) as count,
        EXTRACT(DAY FROM NOW() - MIN(created_at)) as age_days
    FROM ad_analyses 
    WHERE created_at < NOW() - INTERVAL '90 days'
) old_data
WHERE count > 0;

-- ============================================================================
-- PART 3: DATA PURGING SUMMARY (Before Deletion)
-- ============================================================================

-- Show summary of what will be deleted
WITH deletion_summary AS (
    SELECT 'Test Users' as category, COUNT(*) as count FROM user_profiles 
    WHERE email ILIKE '%test%' OR email ILIKE '%demo%' OR email ILIKE '%example.com%' 
       OR id = '00000000-0000-0000-0000-000000000000'
    
    UNION ALL
    
    SELECT 'Test Projects' as category, COUNT(*) as count FROM projects p
    LEFT JOIN user_profiles up ON p.user_id = up.id
    WHERE p.name ILIKE '%test%' OR p.name ILIKE '%demo%' OR p.name ILIKE '%sample%'
       OR up.email ILIKE '%test%' OR up.email ILIKE '%demo%' OR up.email ILIKE '%example.com%'
       OR p.user_id = '00000000-0000-0000-0000-000000000000'
    
    UNION ALL
    
    SELECT 'Test Analyses' as category, COUNT(*) as count FROM ad_analyses aa
    LEFT JOIN user_profiles up ON aa.user_id = up.id
    WHERE aa.headline ILIKE '%test%' OR aa.body_text ILIKE '%test%' OR aa.body_text ILIKE '%debug%'
       OR up.email ILIKE '%test%' OR up.email ILIKE '%demo%' OR up.email ILIKE '%example.com%'
       OR aa.user_id = '00000000-0000-0000-0000-000000000000'
    
    UNION ALL
    
    SELECT 'Test Competitor Data' as category, COUNT(*) as count FROM competitor_benchmarks cb
    JOIN ad_analyses aa ON cb.analysis_id = aa.id
    LEFT JOIN user_profiles up ON aa.user_id = up.id
    WHERE up.email ILIKE '%test%' OR up.email ILIKE '%demo%' OR up.email ILIKE '%example.com%'
       OR aa.user_id = '00000000-0000-0000-0000-000000000000'
    
    UNION ALL
    
    SELECT 'Test Generations' as category, COUNT(*) as count FROM ad_generations ag
    JOIN ad_analyses aa ON ag.analysis_id = aa.id
    LEFT JOIN user_profiles up ON aa.user_id = up.id
    WHERE up.email ILIKE '%test%' OR up.email ILIKE '%demo%' OR up.email ILIKE '%example.com%'
       OR aa.user_id = '00000000-0000-0000-0000-000000000000'
)
SELECT 
    'DELETION SUMMARY' as phase,
    category,
    count,
    CASE WHEN count > 0 THEN '⚠️ WILL BE DELETED' ELSE '✅ CLEAN' END as status
FROM deletion_summary
ORDER BY count DESC;

-- ============================================================================
-- PART 4: ACTUAL DATA PURGING (IRREVERSIBLE - BE CAREFUL!)
-- ============================================================================

-- UNCOMMENT THESE SECTIONS ONLY WHEN READY TO PURGE
-- RUN IN STAGING ENVIRONMENT FIRST TO TEST

/*
-- Step 1: Delete supporting data first (to avoid FK constraint issues)
DELETE FROM ad_generations 
WHERE analysis_id IN (
    SELECT aa.id FROM ad_analyses aa
    LEFT JOIN user_profiles up ON aa.user_id = up.id
    WHERE aa.headline ILIKE '%test%' OR aa.body_text ILIKE '%test%' OR aa.body_text ILIKE '%debug%'
       OR up.email ILIKE '%test%' OR up.email ILIKE '%demo%' OR up.email ILIKE '%example.com%'
       OR aa.user_id = '00000000-0000-0000-0000-000000000000'
);

DELETE FROM competitor_benchmarks 
WHERE analysis_id IN (
    SELECT aa.id FROM ad_analyses aa
    LEFT JOIN user_profiles up ON aa.user_id = up.id
    WHERE aa.headline ILIKE '%test%' OR aa.body_text ILIKE '%test%' OR aa.body_text ILIKE '%debug%'
       OR up.email ILIKE '%test%' OR up.email ILIKE '%demo%' OR up.email ILIKE '%example.com%'
       OR aa.user_id = '00000000-0000-0000-0000-000000000000'
);

-- Step 2: Delete test ad analyses
DELETE FROM ad_analyses 
WHERE id IN (
    SELECT aa.id FROM ad_analyses aa
    LEFT JOIN user_profiles up ON aa.user_id = up.id
    WHERE aa.headline ILIKE '%test%' OR aa.body_text ILIKE '%test%' OR aa.body_text ILIKE '%debug%'
       OR aa.headline = 'Amazing Product Launch'
       OR aa.headline = '50% Off Everything - Limited Time Only!'
       OR up.email ILIKE '%test%' OR up.email ILIKE '%demo%' OR up.email ILIKE '%example.com%'
       OR aa.user_id = '00000000-0000-0000-0000-000000000000'
);

-- Step 3: Delete test projects
DELETE FROM projects 
WHERE id IN (
    SELECT p.id FROM projects p
    LEFT JOIN user_profiles up ON p.user_id = up.id
    WHERE p.name ILIKE '%test%' OR p.name ILIKE '%demo%' OR p.name ILIKE '%sample%'
       OR p.description ILIKE '%debug%' OR p.client_name ILIKE '%debug%'
       OR up.email ILIKE '%test%' OR up.email ILIKE '%demo%' OR up.email ILIKE '%example.com%'
       OR p.user_id = '00000000-0000-0000-0000-000000000000'
);

-- Step 4: Delete test user profiles (LAST - this will cascade)
DELETE FROM user_profiles 
WHERE email ILIKE '%test%' 
   OR email ILIKE '%demo%' 
   OR email ILIKE '%example.com%' 
   OR email ILIKE '%sample%'
   OR email = 'user@example.com'
   OR id = '00000000-0000-0000-0000-000000000000';
*/

-- ============================================================================
-- PART 5: POST-PURGE VERIFICATION
-- ============================================================================

-- After running purge scripts, verify clean state
SELECT 
    'POST-PURGE VERIFICATION' as check_type,
    'user_profiles' as table_name,
    COUNT(*) as remaining_records,
    COUNT(*) FILTER (WHERE email ILIKE '%test%' OR email ILIKE '%demo%' OR email ILIKE '%example.com%') as test_records_remaining
FROM user_profiles

UNION ALL

SELECT 
    'POST-PURGE VERIFICATION' as check_type,
    'projects' as table_name,
    COUNT(*) as remaining_records,
    COUNT(*) FILTER (WHERE name ILIKE '%test%' OR name ILIKE '%demo%' OR name ILIKE '%sample%') as test_records_remaining
FROM projects

UNION ALL

SELECT 
    'POST-PURGE VERIFICATION' as check_type,
    'ad_analyses' as table_name,
    COUNT(*) as remaining_records,
    COUNT(*) FILTER (WHERE headline ILIKE '%test%' OR body_text ILIKE '%test%') as test_records_remaining
FROM ad_analyses;

-- ============================================================================
-- PART 6: PRODUCTION READINESS FINAL CHECK
-- ============================================================================

-- Verify database is clean and ready for production
WITH clean_check AS (
    SELECT 
        'Clean Data Check' as check_category,
        COUNT(*) FILTER (WHERE email NOT ILIKE '%test%' AND email NOT ILIKE '%demo%' AND email NOT ILIKE '%example.com%') as clean_users,
        COUNT(*) FILTER (WHERE email ILIKE '%test%' OR email ILIKE '%demo%' OR email ILIKE '%example.com%') as test_users,
        COUNT(*) as total_users
    FROM user_profiles
),
size_check AS (
    SELECT 
        (SELECT COUNT(*) FROM user_profiles) as user_count,
        (SELECT COUNT(*) FROM projects) as project_count,
        (SELECT COUNT(*) FROM ad_analyses) as analysis_count
)
SELECT 
    'PRODUCTION READINESS' as final_status,
    CASE 
        WHEN cc.test_users = 0 AND sc.user_count > 0 THEN '🎉 READY FOR PRODUCTION'
        WHEN cc.test_users > 0 THEN '❌ STILL HAS TEST DATA'
        WHEN sc.user_count = 0 THEN '⚠️ NO USERS (Empty database)'
        ELSE '⚠️ NEEDS REVIEW'
    END as status,
    cc.clean_users as production_users,
    cc.test_users as test_users_remaining,
    sc.project_count as total_projects,
    sc.analysis_count as total_analyses
FROM clean_check cc, size_check sc;

-- ============================================================================
-- USAGE INSTRUCTIONS:
-- ============================================================================
/*
1. BACKUP FIRST: 
   - Create full database backup before running any deletion scripts
   - Test in staging environment first

2. RUN VALIDATION:
   - Execute Parts 1-3 to identify test data
   - Review the results carefully

3. PURGE DATA:
   - Uncomment Part 4 scripts
   - Run in staging first to verify
   - Then run in production during maintenance window

4. VERIFY RESULTS:
   - Execute Parts 5-6 to confirm clean state
   - Check that real user data remains intact

5. FINAL CHECK:
   - Ensure the database is ready for production traffic
   - Verify no test/demo data remains
*/