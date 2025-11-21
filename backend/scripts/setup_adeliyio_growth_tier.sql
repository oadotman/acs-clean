-- Setup adeliyio@yahoo.com as GROWTH tier user for testing
-- This uses 'growth' tier which should already exist in your database
-- UUID: 5ee6a8be-6739-41d5-85d8-b735c61b31f0

BEGIN;

-- Step 1: Update or create user in backend database with GROWTH tier
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
    'Test User - Growth Tier',
    '5ee6a8be-6739-41d5-85d8-b735c61b31f0',
    'growth',  -- Using 'growth' instead of 'agency_standard'
    TRUE,
    TRUE,
    TRUE,
    NOW(),
    NOW()
)
ON CONFLICT (email)
DO UPDATE SET
    subscription_tier = 'growth',
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
    RAISE NOTICE 'Tier: GROWTH (100 credits/month + 20 bonus)';
    RAISE NOTICE '============================================';

    -- Initialize credits for Growth tier
    -- Growth: 100 credits/month + 20 bonus = 120 total
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
        120,  -- 100 monthly + 20 bonus
        100,
        20,
        0,
        'growth',
        NOW(),
        NOW(),
        NOW()
    )
    ON CONFLICT (user_id)
    DO UPDATE SET
        current_credits = 120,
        monthly_allowance = 100,
        bonus_credits = 20,
        total_used = 0,
        subscription_tier = 'growth',
        last_reset = NOW(),
        updated_at = NOW();

    RAISE NOTICE 'Credits initialized: 120 credits (100 monthly + 20 bonus)';

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
        120,
        'Test user setup: Growth tier with 120 credits',
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
-- NOTICE:  User ID: 123
-- NOTICE:  Supabase UUID: 5ee6a8be-6739-41d5-85d8-b735c61b31f0
-- NOTICE:  Tier: GROWTH (100 credits/month + 20 bonus)
-- NOTICE:  ============================================
-- NOTICE:  Credits initialized: 120 credits (100 monthly + 20 bonus)
-- NOTICE:  Transaction logged successfully
-- NOTICE:  ============================================
--
-- Query Result:
-- id  | email              | subscription_tier | current_credits | monthly_allowance
-- ----|--------------------|--------------------|-----------------|------------------
-- 123 | adeliyio@yahoo.com | growth            | 120             | 100
-- ============================================================================

-- ============================================================================
-- TESTING:
-- ============================================================================
-- 1. Login as adeliyio@yahoo.com
-- 2. Start analysis (costs 2 credits)
-- 3. Expected: 120 → 118 credits
--
-- You'll have 60 analyses available (120 credits / 2 per analysis)
-- ============================================================================

-- ============================================================================
-- TO UPGRADE TO AGENCY TIER LATER:
-- ============================================================================
-- First run: backend/scripts/fix_subscription_tier_enum.sql
-- Then run: backend/scripts/setup_adeliyio_test_user.sql
-- ============================================================================
