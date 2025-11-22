-- ============================================================================
-- ADD NEW SUBSCRIPTION TIERS TO DATABASE
-- ============================================================================
-- This script adds the new tier values to align with your pricing page
-- Run this in Supabase SQL Editor BEFORE running setup_test_user_final.sql
-- ============================================================================

BEGIN;

-- Display current tiers
SELECT '========================================' as message;
SELECT 'CURRENT TIER VALUES BEFORE MIGRATION:' as message;
SELECT '========================================' as message;

SELECT enumlabel as tier_value
FROM pg_enum
WHERE enumtypid = 'subscriptiontier'::regtype
ORDER BY enumsortorder;

SELECT '========================================' as message;
SELECT 'ADDING NEW TIER VALUES...' as message;
SELECT '========================================' as message;

-- Add new tier values
-- Note: PostgreSQL doesn't allow IF NOT EXISTS in ALTER TYPE ADD VALUE
-- So we'll use a DO block to check first

DO $$
BEGIN
    -- Add 'growth' if it doesn't exist
    IF NOT EXISTS (
        SELECT 1 FROM pg_enum
        WHERE enumtypid = 'subscriptiontier'::regtype
        AND enumlabel = 'growth'
    ) THEN
        ALTER TYPE subscriptiontier ADD VALUE 'growth';
        RAISE NOTICE '✓ Added tier: growth';
    ELSE
        RAISE NOTICE '→ Tier already exists: growth';
    END IF;

    -- Add 'agency_standard' if it doesn't exist
    IF NOT EXISTS (
        SELECT 1 FROM pg_enum
        WHERE enumtypid = 'subscriptiontier'::regtype
        AND enumlabel = 'agency_standard'
    ) THEN
        ALTER TYPE subscriptiontier ADD VALUE 'agency_standard';
        RAISE NOTICE '✓ Added tier: agency_standard';
    ELSE
        RAISE NOTICE '→ Tier already exists: agency_standard';
    END IF;

    -- Add 'agency_premium' if it doesn't exist
    IF NOT EXISTS (
        SELECT 1 FROM pg_enum
        WHERE enumtypid = 'subscriptiontier'::regtype
        AND enumlabel = 'agency_premium'
    ) THEN
        ALTER TYPE subscriptiontier ADD VALUE 'agency_premium';
        RAISE NOTICE '✓ Added tier: agency_premium';
    ELSE
        RAISE NOTICE '→ Tier already exists: agency_premium';
    END IF;

    -- Add 'agency_unlimited' if it doesn't exist
    IF NOT EXISTS (
        SELECT 1 FROM pg_enum
        WHERE enumtypid = 'subscriptiontier'::regtype
        AND enumlabel = 'agency_unlimited'
    ) THEN
        ALTER TYPE subscriptiontier ADD VALUE 'agency_unlimited';
        RAISE NOTICE '✓ Added tier: agency_unlimited';
    ELSE
        RAISE NOTICE '→ Tier already exists: agency_unlimited';
    END IF;
END $$;

-- Migrate existing users from legacy tiers to new tiers (if they exist)
SELECT '========================================' as message;
SELECT 'CHECKING FOR LEGACY USER DATA...' as message;
SELECT '========================================' as message;

-- Only migrate 'basic' → 'growth' if 'basic' enum value exists
DO $$
DECLARE
    v_basic_exists BOOLEAN;
    v_basic_count INTEGER := 0;
BEGIN
    -- Check if 'basic' enum value exists
    SELECT EXISTS (
        SELECT 1 FROM pg_enum
        WHERE enumtypid = 'subscriptiontier'::regtype
        AND enumlabel = 'basic'
    ) INTO v_basic_exists;

    IF v_basic_exists THEN
        -- Count users with basic tier
        SELECT COUNT(*) INTO v_basic_count
        FROM users
        WHERE subscription_tier = 'basic';

        IF v_basic_count > 0 THEN
            UPDATE users
            SET subscription_tier = 'growth',
                updated_at = NOW()
            WHERE subscription_tier = 'basic';

            UPDATE user_credits
            SET subscription_tier = 'growth',
                updated_at = NOW()
            WHERE subscription_tier = 'basic';

            RAISE NOTICE '✓ Migrated % users from "basic" → "growth"', v_basic_count;
        ELSE
            RAISE NOTICE '→ No users with "basic" tier to migrate';
        END IF;
    ELSE
        RAISE NOTICE '→ Legacy tier "basic" does not exist (already migrated or never used)';
    END IF;
END $$;

-- Only migrate 'pro' → 'agency_unlimited' if 'pro' enum value exists
DO $$
DECLARE
    v_pro_exists BOOLEAN;
    v_pro_count INTEGER := 0;
BEGIN
    -- Check if 'pro' enum value exists
    SELECT EXISTS (
        SELECT 1 FROM pg_enum
        WHERE enumtypid = 'subscriptiontier'::regtype
        AND enumlabel = 'pro'
    ) INTO v_pro_exists;

    IF v_pro_exists THEN
        -- Count users with pro tier
        SELECT COUNT(*) INTO v_pro_count
        FROM users
        WHERE subscription_tier = 'pro';

        IF v_pro_count > 0 THEN
            UPDATE users
            SET subscription_tier = 'agency_unlimited',
                updated_at = NOW()
            WHERE subscription_tier = 'pro';

            UPDATE user_credits
            SET subscription_tier = 'agency_unlimited',
                updated_at = NOW()
            WHERE subscription_tier = 'pro';

            RAISE NOTICE '✓ Migrated % users from "pro" → "agency_unlimited"', v_pro_count;
        ELSE
            RAISE NOTICE '→ No users with "pro" tier to migrate';
        END IF;
    ELSE
        RAISE NOTICE '→ Legacy tier "pro" does not exist (already migrated or never used)';
    END IF;
END $$;

-- Display final tier values
SELECT '========================================' as message;
SELECT 'FINAL TIER VALUES AFTER MIGRATION:' as message;
SELECT '========================================' as message;

SELECT enumlabel as tier_value
FROM pg_enum
WHERE enumtypid = 'subscriptiontier'::regtype
ORDER BY enumsortorder;

-- Verify alignment with pricing page
SELECT '========================================' as message;
SELECT 'PRICING PAGE ALIGNMENT CHECK:' as message;
SELECT '========================================' as message;

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
    END as pricing_info
FROM (
    VALUES
        ('free'),
        ('growth'),
        ('agency_standard'),
        ('agency_premium'),
        ('agency_unlimited')
) AS tiers(tier);

SELECT '========================================' as message;
SELECT 'MIGRATION COMPLETE!' as message;
SELECT '✓ Your database now matches your pricing page!' as message;
SELECT 'Next step: Run setup_test_user_final.sql' as message;
SELECT '========================================' as message;

COMMIT;

-- ============================================================================
-- EXPECTED OUTPUT:
-- ============================================================================
-- You should see:
-- ✓ Added tier: growth
-- ✓ Added tier: agency_standard
-- ✓ Added tier: agency_premium
-- ✓ Added tier: agency_unlimited
--
-- And the final alignment check should show exists_in_db = TRUE for all tiers
-- ============================================================================
