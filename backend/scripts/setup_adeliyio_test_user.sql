-- Setup adeliyio@yahoo.com as Agency Standard user for testing
-- UUID: 5ee6a8be-6739-41d5-85d8-b735c61b31f0
-- Ready to run - no modifications needed!

BEGIN;

-- Step 1: Update or create user in backend database
INSERT INTO users (
    email,
    full_name,
    supabase_user_id,
    subscription_tier,
    subscription_active,
    is_active,
    email_verified,
    created_at,
    updated_at
) VALUES (
    'adeliyio@yahoo.com',
    'Test User - Agency Standard',
    '5ee6a8be-6739-41d5-85d8-b735c61b31f0',
    'agency_standard',
    TRUE,
    TRUE,
    TRUE,
    NOW(),
    NOW()
)
ON CONFLICT (email)
DO UPDATE SET
    subscription_tier = 'agency_standard',
    subscription_active = TRUE,
    is_active = TRUE,
    email_verified = TRUE,
    supabase_user_id = '5ee6a8be-6739-41d5-85d8-b735c61b31f0',
    updated_at = NOW();

-- Step 2: Get the user ID and initialize credits
DO $$
DECLARE
    v_user_id INTEGER;
BEGIN
    -- Get user ID
    SELECT id INTO v_user_id
    FROM users
    WHERE email = 'adeliyio@yahoo.com';

    RAISE NOTICE '============================================';
    RAISE NOTICE 'User ID: %', v_user_id;
    RAISE NOTICE 'Supabase UUID: 5ee6a8be-6739-41d5-85d8-b735c61b31f0';
    RAISE NOTICE '============================================';

    -- Initialize credits for Agency Standard tier
    -- Agency Standard: 500 credits/month + 100 bonus = 600 total
    INSERT INTO user_credits (
        user_id,
        current_credits,
        monthly_allowance,
        bonus_credits,
        total_used,
        subscription_tier,
        last_reset,
        created_at,
        updated_at
    ) VALUES (
        v_user_id::TEXT,
        600,  -- 500 monthly + 100 bonus
        500,
        100,
        0,
        'agency_standard',
        NOW(),
        NOW(),
        NOW()
    )
    ON CONFLICT (user_id)
    DO UPDATE SET
        current_credits = 600,
        monthly_allowance = 500,
        bonus_credits = 100,
        total_used = 0,
        subscription_tier = 'agency_standard',
        last_reset = NOW(),
        updated_at = NOW();

    RAISE NOTICE 'Credits initialized: 600 credits (500 monthly + 100 bonus)';

    -- Log the credit initialization
    INSERT INTO credit_transactions (
        user_id,
        operation,
        amount,
        description,
        created_at
    ) VALUES (
        v_user_id::TEXT,
        'MANUAL_RESET',
        600,
        'Test user setup: Agency Standard tier with 600 credits',
        NOW()
    );

    RAISE NOTICE 'Transaction logged successfully';
    RAISE NOTICE '============================================';
END $$;

-- Step 3: Verify setup
SELECT
    u.id,
    u.email,
    u.full_name,
    u.subscription_tier,
    u.subscription_active,
    u.supabase_user_id,
    uc.current_credits,
    uc.monthly_allowance,
    uc.bonus_credits,
    uc.subscription_tier as credit_tier
FROM users u
LEFT JOIN user_credits uc ON u.id::TEXT = uc.user_id
WHERE u.email = 'adeliyio@yahoo.com';

COMMIT;

-- ============================================================================
-- Expected Output:
-- ============================================================================
-- NOTICE:  ============================================
-- NOTICE:  User ID: 123 (or whatever your user ID is)
-- NOTICE:  Supabase UUID: 5ee6a8be-6739-41d5-85d8-b735c61b31f0
-- NOTICE:  ============================================
-- NOTICE:  Credits initialized: 600 credits (500 monthly + 100 bonus)
-- NOTICE:  Transaction logged successfully
-- NOTICE:  ============================================
--
-- Query Result:
-- id  | email              | subscription_tier   | current_credits | monthly_allowance
-- ----|--------------------|--------------------|-----------------|------------------
-- 123 | adeliyio@yahoo.com | agency_standard    | 600             | 500
-- ============================================================================

-- ============================================================================
-- NEXT STEPS:
-- ============================================================================
-- 1. Login to your app as adeliyio@yahoo.com
-- 2. Start a new analysis
-- 3. Watch backend logs:
--    sudo journalctl -u adcopysurge -f | grep -i credit
--
-- 4. Expected log output:
--    ✅ Credits deducted: 2 credits, remaining: 598
--
-- 5. Verify in database:
--    SELECT current_credits FROM user_credits
--    WHERE user_id = (SELECT id::TEXT FROM users WHERE email = 'adeliyio@yahoo.com');
--    -- Should show: 598
-- ============================================================================

-- ============================================================================
-- TROUBLESHOOTING:
-- ============================================================================
-- If you see "User not found" errors:
--   SELECT * FROM users WHERE email = 'adeliyio@yahoo.com';
--   -- If empty, the user doesn't exist in Supabase Auth
--
-- If credits don't deduct:
--   -- Check backend logs for errors
--   sudo journalctl -u adcopysurge -n 50
--
--   -- Verify credit service is working
--   SELECT * FROM credit_transactions
--   WHERE user_id = (SELECT id::TEXT FROM users WHERE email = 'adeliyio@yahoo.com')
--   ORDER BY created_at DESC LIMIT 5;
-- ============================================================================

-- ============================================================================
-- RESET CREDITS (if needed for testing):
-- ============================================================================
-- UPDATE user_credits
-- SET current_credits = 600,
--     total_used = 0
-- WHERE user_id = (SELECT id::TEXT FROM users WHERE email = 'adeliyio@yahoo.com');
-- ============================================================================
