-- CHECK AUTH USER MAPPING
-- This checks if auth.users matches user_profiles correctly

-- 1. Check what auth.users email is linked to which user_profiles ID
SELECT 
    '=== AUTH TO PROFILE MAPPING ===' as check,
    au.id as auth_id,
    au.email as auth_email,
    up.id as profile_id,
    up.email as profile_email,
    up.subscription_tier,
    up.agency_id,
    CASE 
        WHEN au.id != up.id THEN '❌ ID MISMATCH!'
        WHEN au.email != up.email THEN '❌ EMAIL MISMATCH!'
        ELSE '✅ Matched'
    END as status
FROM auth.users au
LEFT JOIN user_profiles up ON au.id = up.id
WHERE au.email IN ('oadatascientist@gmail.com', 'evelyn.etaifo@protonmail.com')
ORDER BY au.email;

-- 2. Check user_credits mapping
SELECT 
    '=== CREDITS MAPPING ===' as check,
    au.id as auth_id,
    au.email as auth_email,
    uc.user_id as credit_user_id,
    uc.subscription_tier as credit_tier,
    uc.current_credits,
    CASE 
        WHEN au.id != uc.user_id THEN '❌ ID MISMATCH!'
        ELSE '✅ Matched'
    END as status
FROM auth.users au
LEFT JOIN user_credits uc ON au.id = uc.user_id
WHERE au.email IN ('oadatascientist@gmail.com', 'evelyn.etaifo@protonmail.com')
ORDER BY au.email;

-- 3. IF THERE'S A MISMATCH, THIS WILL FIX IT:
-- Update user_profiles to match auth.users
UPDATE user_profiles SET 
    subscription_tier = 'agency_unlimited',
    agency_id = '505ed26d-d111-4070-abc2-281a345ac4f8',
    can_create_agency = true
WHERE email = 'oadatascientist@gmail.com';

-- Update user_credits to match
UPDATE user_credits SET 
    subscription_tier = 'agency_unlimited',
    current_credits = 999999,
    monthly_allowance = 999999
WHERE user_id = (SELECT id FROM auth.users WHERE email = 'oadatascientist@gmail.com');

-- Verify the fix
SELECT 
    '=== AFTER FIX ===' as status,
    up.email,
    up.subscription_tier as profile_tier,
    uc.subscription_tier as credit_tier,
    uc.current_credits,
    up.agency_id
FROM user_profiles up
JOIN user_credits uc ON up.id = uc.user_id
WHERE up.email = 'oadatascientist@gmail.com';