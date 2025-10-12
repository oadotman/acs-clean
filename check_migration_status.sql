-- QUERY 1: Check if migration tables were created
SELECT 
    'Migration Status' as check_type,
    CASE 
        WHEN EXISTS(SELECT 1 FROM pg_tables WHERE schemaname='public' AND tablename='subscription_tiers') THEN '✅'
        ELSE '❌ subscription_tiers missing'
    END as subscription_tiers_table,
    CASE 
        WHEN EXISTS(SELECT 1 FROM pg_tables WHERE schemaname='public' AND tablename='agency_team_members') THEN '✅'
        ELSE '❌ agency_team_members missing'
    END as team_members_table,
    CASE 
        WHEN EXISTS(SELECT 1 FROM pg_tables WHERE schemaname='public' AND tablename='agency_invitations') THEN '✅'
        ELSE '❌ agency_invitations missing'
    END as invitations_table;

-- QUERY 2: Check if user_profiles has required columns
SELECT 
    'User Profiles Columns' as check_type,
    CASE 
        WHEN EXISTS(SELECT 1 FROM information_schema.columns WHERE table_name='user_profiles' AND column_name='can_create_agency') THEN '✅'
        ELSE '❌ can_create_agency missing'
    END as can_create_agency_column,
    CASE 
        WHEN EXISTS(SELECT 1 FROM information_schema.columns WHERE table_name='user_profiles' AND column_name='monthly_analysis_limit') THEN '✅'
        ELSE '❌ monthly_analysis_limit missing'
    END as analysis_limit_column,
    CASE 
        WHEN EXISTS(SELECT 1 FROM information_schema.columns WHERE table_name='user_profiles' AND column_name='full_name') THEN '✅'
        ELSE '❌ full_name missing'
    END as full_name_column;

-- QUERY 3: Check current user_profiles structure
SELECT column_name, data_type, is_nullable, column_default 
FROM information_schema.columns 
WHERE table_schema = 'public' AND table_name = 'user_profiles'
ORDER BY ordinal_position;

-- QUERY 4: Check if your user exists and current status
SELECT 
    id,
    email,
    subscription_tier,
    COALESCE(can_create_agency, false) as can_create_agency,
    COALESCE(monthly_analysis_limit, 0) as monthly_analysis_limit,
    'Current Status' as note
FROM user_profiles 
WHERE email = 'oadatascientist@gmail.com';

-- QUERY 5: Count how many pricing tiers exist
SELECT COUNT(*) as tier_count, 'Should be 5 tiers' as expected
FROM subscription_tiers;