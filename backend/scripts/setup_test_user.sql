-- Setup adeliyio@yahoo.com as Agency Standard user for testing
-- Run this script after deployment to test credit deduction

-- ============================================================================
-- IMPORTANT: Replace 'SUPABASE_USER_UUID' with actual UUID from Supabase Auth
-- ============================================================================
-- To find the UUID:
-- 1. Go to Supabase Dashboard → Authentication → Users
-- 2. Find adeliyio@yahoo.com
-- 3. Copy the UUID (looks like: 12345678-1234-1234-1234-123456789abc)
-- ============================================================================

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
    'REPLACE_WITH_SUPABASE_UUID',  -- ⚠️ REPLACE THIS
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
    updated_at = NOW();

-- Step 2: Get the user ID (works for both insert and update)
DO $$
DECLARE
    v_user_id INTEGER;
BEGIN
    -- Get user ID
    SELECT id INTO v_user_id
    FROM users
    WHERE email = 'adeliyio@yahoo.com';

    RAISE NOTICE 'User ID: %', v_user_id;

    -- Step 3: Initialize or reset credits for Agency Standard tier
    -- Agency Standard gets 500 credits/month + 100 bonus
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
        v_user_id::TEXT,  -- Convert to text for user_credits table
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

    -- Step 4: Log the credit initialization
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

    RAISE NOTICE 'Transaction logged';
END $$;

-- Step 5: Verify setup
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
-- id  | email                  | subscription_tier   | current_credits
-- ----|------------------------|---------------------|----------------
-- 123 | adeliyio@yahoo.com     | agency_standard     | 600
-- ============================================================================

-- ============================================================================
-- Testing Credit Deduction:
-- ============================================================================
-- After setup, test with:
--
-- 1. Login as adeliyio@yahoo.com in the frontend
-- 2. Start a new analysis
-- 3. Watch backend logs for:
--    "✅ Credits deducted: 2 credits, remaining: 598"
-- 4. Verify in database:
--    SELECT current_credits FROM user_credits WHERE user_id = '123';
--    -- Should show: 598
-- ============================================================================

-- ============================================================================
-- Manual Credit Operations (if needed):
-- ============================================================================

-- Add bonus credits
-- UPDATE user_credits
-- SET current_credits = current_credits + 100,
--     bonus_credits = bonus_credits + 100
-- WHERE user_id = (SELECT id::TEXT FROM users WHERE email = 'adeliyio@yahoo.com');

-- Reset to full balance
-- UPDATE user_credits
-- SET current_credits = 600,
--     total_used = 0
-- WHERE user_id = (SELECT id::TEXT FROM users WHERE email = 'adeliyio@yahoo.com');

-- Check transaction history
-- SELECT * FROM credit_transactions
-- WHERE user_id = (SELECT id::TEXT FROM users WHERE email = 'adeliyio@yahoo.com')
-- ORDER BY created_at DESC
-- LIMIT 20;
-- ============================================================================
