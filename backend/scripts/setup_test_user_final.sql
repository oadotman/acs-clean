-- ============================================================================
-- SETUP TEST USER: adeliyio@yahoo.com
-- ============================================================================
-- This script sets up a test user with Agency Standard tier (500 credits)
-- UUID: 5ee6a8be-6739-41d5-85d8-b735c61b31f0
--
-- IMPORTANT: Run the migration first!
--   alembic upgrade head
--
-- This ensures all tier enum values exist in your database.
-- ============================================================================

BEGIN;

-- Step 1: Check if required enum value exists
DO $$
DECLARE
    v_tier_exists BOOLEAN;
BEGIN
    SELECT EXISTS (
        SELECT 1 FROM pg_enum
        WHERE enumtypid = 'subscriptiontier'::regtype
        AND enumlabel = 'agency_standard'
    ) INTO v_tier_exists;

    IF NOT v_tier_exists THEN
        RAISE EXCEPTION '
============================================================================
ERROR: Subscription tier "agency_standard" does not exist in database!

SOLUTION: Run the migration first:
    cd backend
    alembic upgrade head

This will add all required tier values: growth, agency_standard,
agency_premium, agency_unlimited to match your pricing page.

After running migration, run this script again.
============================================================================';
    END IF;

    RAISE NOTICE '============================================';
    RAISE NOTICE 'Tier check passed: agency_standard exists ✓';
    RAISE NOTICE '============================================';
END $$;

-- Step 2: Insert/update user with Agency Standard tier
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

-- Step 3: Initialize credits
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
    RAISE NOTICE 'Tier: AGENCY STANDARD';
    RAISE NOTICE 'Credits: 600 (500 monthly + 100 bonus)';
    RAISE NOTICE 'Price: $99/month';
    RAISE NOTICE '============================================';

    -- Initialize credits for Agency Standard tier
    -- Matches frontend: PLAN_LIMITS[SUBSCRIPTION_TIERS.AGENCY_STANDARD]
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

    RAISE NOTICE 'Credits initialized successfully ✓';

    -- Log transaction
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
        'Test user setup: Agency Standard tier ($99/mo) with 600 credits',
        NOW()
    );

    RAISE NOTICE 'Transaction logged ✓';
    RAISE NOTICE '============================================';
END $$;

-- Step 4: Verify setup matches pricing page
SELECT
    u.id,
    u.email,
    u.subscription_tier,
    uc.current_credits,
    uc.monthly_allowance,
    uc.bonus_credits,
    CASE
        WHEN u.subscription_tier = 'free' THEN '$0 - 5 analyses/mo'
        WHEN u.subscription_tier = 'growth' THEN '$39/mo - 100 analyses/mo'
        WHEN u.subscription_tier = 'agency_standard' THEN '$99/mo - 500 analyses/mo'
        WHEN u.subscription_tier = 'agency_premium' THEN '$199/mo - 1000 analyses/mo'
        WHEN u.subscription_tier = 'agency_unlimited' THEN '$249/mo - unlimited'
        ELSE 'Unknown tier'
    END as pricing_info
FROM users u
LEFT JOIN user_credits uc ON u.id::TEXT = uc.user_id
WHERE u.email = 'adeliyio@yahoo.com';

COMMIT;

-- ============================================================================
-- EXPECTED OUTPUT:
-- ============================================================================
-- id  | email              | subscription_tier | current_credits | pricing_info
-- ----|--------------------|--------------------|-----------------|------------------
-- 123 | adeliyio@yahoo.com | agency_standard   | 600             | $99/mo - 500 analyses/mo
-- ============================================================================

-- ============================================================================
-- TESTING CHECKLIST:
-- ============================================================================
-- [ ] Run migration: alembic upgrade head
-- [ ] Run this script: psql < setup_test_user_final.sql
-- [ ] Verify: subscription_tier = 'agency_standard'
-- [ ] Verify: current_credits = 600
-- [ ] Login as adeliyio@yahoo.com
-- [ ] Start analysis (should deduct 2 credits: 600 → 598)
-- [ ] Check logs: "✅ Credits deducted: 2 credits, remaining: 598"
-- [ ] Verify in database: SELECT current_credits FROM user_credits...
-- ============================================================================

-- ============================================================================
-- PRICING PAGE ALIGNMENT VERIFICATION:
-- ============================================================================
-- This query shows if your database tiers match the pricing page
-- ============================================================================
SELECT
    tier,
    EXISTS (
        SELECT 1 FROM pg_enum
        WHERE enumtypid = 'subscriptiontier'::regtype
        AND enumlabel = tier
    ) as exists_in_db,
    CASE
        WHEN tier = 'free' THEN '$0 - 5 analyses/mo'
        WHEN tier = 'growth' THEN '$39/mo - 100 analyses/mo'
        WHEN tier = 'agency_standard' THEN '$99/mo - 500 analyses/mo'
        WHEN tier = 'agency_premium' THEN '$199/mo - 1000 analyses/mo'
        WHEN tier = 'agency_unlimited' THEN '$249/mo - unlimited'
    END as pricing
FROM (
    VALUES
        ('free'),
        ('growth'),
        ('agency_standard'),
        ('agency_premium'),
        ('agency_unlimited')
) AS tiers(tier);

-- All should show exists_in_db = true after migration!
-- ============================================================================
