-- QUERY 1: Upgrade oadatascientist@gmail.com to Agency Unlimited
UPDATE user_profiles SET 
    subscription_tier = 'agency_unlimited',
    can_create_agency = TRUE,
    monthly_analysis_limit = 999999,
    full_name = COALESCE(full_name, 'Data Scientist')
WHERE email = 'oadatascientist@gmail.com';

-- QUERY 2: Verify the user was upgraded
SELECT 
    id,
    email,
    full_name,
    subscription_tier,
    can_create_agency,
    monthly_analysis_limit,
    monthly_analyses_used,
    CASE 
        WHEN can_create_agency = TRUE THEN '✅ Can create agency'
        ELSE '❌ Cannot create agency'
    END as agency_status,
    created_at,
    updated_at
FROM user_profiles 
WHERE email = 'oadatascientist@gmail.com';

-- QUERY 3: Verify all pricing tiers are correct
SELECT 
    id,
    name,
    price_monthly / 100.0 as price_monthly_dollars,
    CASE 
        WHEN price_yearly IS NOT NULL THEN price_yearly / 100.0 
        ELSE NULL 
    END as price_yearly_dollars,
    analysis_limit,
    can_create_agency,
    max_team_members,
    features,
    is_active
FROM subscription_tiers
ORDER BY price_monthly;

-- QUERY 4: Check if pricing matches your requirements
SELECT 
    'Pricing Verification' as check_type,
    CASE 
        WHEN EXISTS(SELECT 1 FROM subscription_tiers WHERE id='free' AND price_monthly=0 AND analysis_limit=10) THEN '✅'
        ELSE '❌'
    END as free_tier,
    CASE 
        WHEN EXISTS(SELECT 1 FROM subscription_tiers WHERE id='growth' AND price_monthly=3900 AND analysis_limit=100) THEN '✅'
        ELSE '❌'
    END as growth_39,
    CASE 
        WHEN EXISTS(SELECT 1 FROM subscription_tiers WHERE id='agency_standard' AND price_monthly=9900 AND analysis_limit=500) THEN '✅'
        ELSE '❌'
    END as agency_standard_99,
    CASE 
        WHEN EXISTS(SELECT 1 FROM subscription_tiers WHERE id='agency_premium' AND price_monthly=19900 AND analysis_limit=2000) THEN '✅'
        ELSE '❌'
    END as agency_premium_199,
    CASE 
        WHEN EXISTS(SELECT 1 FROM subscription_tiers WHERE id='agency_unlimited' AND price_monthly=24900 AND analysis_limit=999999) THEN '✅'
        ELSE '❌'
    END as agency_unlimited_249;