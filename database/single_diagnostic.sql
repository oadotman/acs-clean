-- SINGLE DIAGNOSTIC QUERY - Returns all results in one output
WITH diagnostic_results AS (
    -- User profiles check
    SELECT 
        '1_USERS' as check_type,
        id::text as item_id,
        email as description,
        subscription_tier as value1,
        CASE 
            WHEN agency_id IS NOT NULL THEN 'Has agency: ' || agency_id::text
            ELSE 'No agency'
        END as value2,
        CASE 
            WHEN subscription_tier = 'free' AND agency_id IS NOT NULL THEN '❌ Free user has agency!'
            WHEN subscription_tier LIKE 'agency%' AND agency_id IS NULL THEN '❌ Agency user no agency!'
            ELSE '✅'
        END as status
    FROM user_profiles
    
    UNION ALL
    
    -- Credits check
    SELECT 
        '2_CREDITS' as check_type,
        uc.user_id::text as item_id,
        up.email as description,
        'Credits: ' || uc.current_credits || '/' || uc.monthly_allowance as value1,
        'Tier: ' || uc.subscription_tier as value2,
        CASE 
            WHEN uc.subscription_tier != up.subscription_tier THEN '❌ Tier mismatch!'
            WHEN uc.current_credits IS NULL THEN '❌ No credits!'
            ELSE '✅'
        END as status
    FROM user_credits uc
    JOIN user_profiles up ON uc.user_id = up.id
    
    UNION ALL
    
    -- Agencies check
    SELECT 
        '3_AGENCIES' as check_type,
        a.id::text as item_id,
        a.name as description,
        'Owner: ' || up.email as value1,
        'Members: ' || (SELECT COUNT(*) FROM agency_team_members WHERE agency_id = a.id)::text as value2,
        '✅' as status
    FROM agencies a
    JOIN user_profiles up ON a.owner_id = up.id
    
    UNION ALL
    
    -- Team sync check
    SELECT 
        '4_TEAM_SYNC' as check_type,
        atm.user_id::text as item_id,
        up.email as description,
        'Role: ' || atm.role || ' Status: ' || atm.status as value1,
        'Profile agency: ' || COALESCE(up.agency_id::text, 'NULL') as value2,
        CASE 
            WHEN atm.agency_id != up.agency_id OR up.agency_id IS NULL THEN '❌ Not synced!'
            ELSE '✅'
        END as status
    FROM agency_team_members atm
    JOIN user_profiles up ON atm.user_id = up.id
    
    UNION ALL
    
    -- Realtime check
    SELECT 
        '5_REALTIME' as check_type,
        tablename as item_id,
        'Table: ' || tablename as description,
        'Realtime' as value1,
        'Enabled' as value2,
        '✅' as status
    FROM pg_publication_tables
    WHERE pubname = 'supabase_realtime'
      AND tablename IN ('user_credits', 'agency_team_members')
    
    UNION ALL
    
    -- Missing realtime check
    SELECT 
        '5_REALTIME' as check_type,
        'user_credits' as item_id,
        'Table: user_credits' as description,
        'Realtime' as value1,
        'MISSING' as value2,
        '❌ Not enabled!' as status
    WHERE NOT EXISTS (
        SELECT 1 FROM pg_publication_tables 
        WHERE pubname = 'supabase_realtime' AND tablename = 'user_credits'
    )
    
    UNION ALL
    
    -- Triggers check
    SELECT 
        '6_TRIGGERS' as check_type,
        trigger_name as item_id,
        'Trigger on ' || event_object_table as description,
        event_manipulation as value1,
        'Active' as value2,
        '✅' as status
    FROM information_schema.triggers
    WHERE trigger_name LIKE '%sync_agency%'
)
SELECT 
    check_type,
    item_id,
    description,
    value1,
    value2,
    status
FROM diagnostic_results
ORDER BY check_type, item_id;