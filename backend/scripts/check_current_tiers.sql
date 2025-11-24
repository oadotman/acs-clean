-- ============================================================================
-- CHECK CURRENT TIER VALUES IN DATABASE
-- ============================================================================
-- This script shows you exactly what tier values exist in your database right now
-- ============================================================================

SELECT '=' || repeat('=', 78) || '=' as separator;
SELECT 'CURRENT SUBSCRIPTION TIER VALUES IN DATABASE' as title;
SELECT '=' || repeat('=', 78) || '=' as separator;

-- Show all enum values
SELECT
    enumlabel as tier_value,
    enumsortorder as sort_order
FROM pg_enum
WHERE enumtypid = 'subscriptiontier'::regtype
ORDER BY enumsortorder;

SELECT '=' || repeat('=', 78) || '=' as separator;

-- Check for required tiers
SELECT
    tier as required_tier,
    EXISTS (
        SELECT 1 FROM pg_enum
        WHERE enumtypid = 'subscriptiontier'::regtype
        AND enumlabel = tier
    ) as exists_in_database,
    CASE
        WHEN tier = 'free' THEN '$0 - 5 analyses/mo'
        WHEN tier = 'growth' THEN '$39/mo - 100 analyses/mo'
        WHEN tier = 'agency_standard' THEN '$99/mo - 500 analyses/mo'
        WHEN tier = 'agency_premium' THEN '$199/mo - 1000 analyses/mo'
        WHEN tier = 'agency_unlimited' THEN '$249/mo - unlimited'
    END as pricing_page_info
FROM (
    VALUES
        ('free'),
        ('growth'),
        ('agency_standard'),
        ('agency_premium'),
        ('agency_unlimited')
) AS tiers(tier);

SELECT '=' || repeat('=', 78) || '=' as separator;
SELECT 'DIAGNOSIS:' as section;
SELECT '=' || repeat('=', 78) || '=' as separator;

-- Diagnosis
SELECT
    CASE
        WHEN COUNT(*) FILTER (WHERE tier IN ('growth', 'agency_standard', 'agency_premium', 'agency_unlimited')) = 0 THEN
            '❌ NEW TIERS MISSING - Run migration: alembic upgrade head'
        WHEN COUNT(*) FILTER (WHERE tier IN ('growth', 'agency_standard', 'agency_premium', 'agency_unlimited')) < 4 THEN
            '⚠️  PARTIAL MIGRATION - Some tiers missing. Run: alembic upgrade head'
        ELSE
            '✅ ALL TIERS PRESENT - You can setup test user!'
    END as status
FROM (
    SELECT enumlabel as tier
    FROM pg_enum
    WHERE enumtypid = 'subscriptiontier'::regtype
) as current_tiers;

SELECT '=' || repeat('=', 78) || '=' as separator;

-- Show current user distribution
SELECT 'CURRENT USER DISTRIBUTION:' as section;
SELECT '=' || repeat('=', 78) || '=' as separator;

SELECT
    subscription_tier,
    COUNT(*) as user_count,
    CASE
        WHEN subscription_tier IN ('basic', 'pro') THEN '⚠️  Legacy tier (will be migrated)'
        ELSE '✓ Current tier'
    END as status
FROM users
GROUP BY subscription_tier
ORDER BY user_count DESC;

SELECT '=' || repeat('=', 78) || '=' as separator;
SELECT 'NEXT STEPS:' as section;
SELECT '=' || repeat('=', 78) || '=' as separator;

SELECT
    CASE
        WHEN (SELECT COUNT(*) FROM pg_enum WHERE enumtypid = 'subscriptiontier'::regtype AND enumlabel = 'agency_standard') = 0 THEN
            E'1. Run migration:\n   cd backend\n   alembic upgrade head\n\n2. Then run test user setup:\n   psql < scripts/setup_test_user_final.sql'
        ELSE
            E'✓ Migration complete!\n\nRun test user setup:\n   psql < scripts/setup_test_user_final.sql'
    END as instructions;

SELECT '=' || repeat('=', 78) || '=' as separator;
