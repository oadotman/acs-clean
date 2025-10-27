-- ============================================================================
-- FULL SYSTEM DIAGNOSTIC - Run all sections and paste results
-- ============================================================================

-- 1. CHECK ALL USERS AND THEIR TIERS
SELECT 
    '=== USER PROFILES ===' as section,
    id,
    email,
    subscription_tier,
    agency_id,
    can_create_agency,
    CASE 
        WHEN subscription_tier = 'free' THEN '🆓 Free user'
        WHEN subscription_tier LIKE 'agency%' THEN '🏢 Agency user'
        ELSE '💎 Pro user'
    END as user_type
FROM user_profiles
ORDER BY email;

-- 2. CHECK USER CREDITS
SELECT 
    '=== USER CREDITS ===' as section,
    uc.user_id,
    up.email,
    uc.current_credits,
    uc.monthly_allowance,
    uc.subscription_tier as credit_tier,
    up.subscription_tier as profile_tier,
    CASE 
        WHEN uc.subscription_tier = up.subscription_tier THEN '✅ Tiers match'
        ELSE '❌ TIER MISMATCH'
    END as tier_status
FROM user_credits uc
JOIN user_profiles up ON uc.user_id = up.id
ORDER BY up.email;

-- 3. CHECK AGENCIES AND MEMBERS
SELECT 
    '=== AGENCIES ===' as section,
    a.id as agency_id,
    a.name,
    a.owner_id,
    up.email as owner_email,
    a.subscription_tier as agency_tier,
    (SELECT COUNT(*) FROM agency_team_members WHERE agency_id = a.id) as member_count
FROM agencies a
JOIN user_profiles up ON a.owner_id = up.id;

-- 4. CHECK TEAM MEMBERS
SELECT 
    '=== TEAM MEMBERS ===' as section,
    atm.id,
    atm.agency_id,
    atm.user_id,
    up.email,
    atm.role,
    atm.status,
    up.agency_id as profile_agency_id,
    CASE 
        WHEN atm.agency_id = up.agency_id THEN '✅ Synced'
        ELSE '❌ NOT SYNCED'
    END as sync_status
FROM agency_team_members atm
JOIN user_profiles up ON atm.user_id = up.id;

-- 5. CHECK REALTIME STATUS
SELECT 
    '=== REALTIME STATUS ===' as section,
    tablename,
    CASE 
        WHEN tablename IS NOT NULL THEN '✅ Real-time enabled'
        ELSE '❌ Real-time NOT enabled'
    END as status
FROM pg_publication_tables
WHERE pubname = 'supabase_realtime'
  AND tablename IN ('user_credits', 'agency_team_members');

-- 6. CHECK TRIGGERS
SELECT 
    '=== TRIGGERS ===' as section,
    trigger_name,
    event_object_table,
    CASE 
        WHEN trigger_name LIKE '%sync_agency%' THEN '✅ Sync trigger'
        ELSE 'ℹ️ Other trigger'
    END as trigger_type
FROM information_schema.triggers
WHERE trigger_name LIKE '%sync%' OR trigger_name LIKE '%credit%';

-- 7. IDENTIFY PROBLEMS
SELECT 
    '=== PROBLEMS DETECTED ===' as section,
    'Check the results above for:' as instructions,
    '1. Any ❌ marks indicate problems' as check1,
    '2. Free users should NOT have agency_id' as check2,
    '3. All agency users should have matching tiers' as check3,
    '4. Real-time should be enabled for credits' as check4;