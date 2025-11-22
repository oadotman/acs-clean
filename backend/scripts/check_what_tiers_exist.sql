-- ============================================================================
-- CHECK WHAT TIER VALUES ACTUALLY EXIST IN YOUR DATABASE
-- ============================================================================
-- Run this first to see what you have
-- ============================================================================

SELECT '========================================' as message;
SELECT 'CURRENT SUBSCRIPTION TIERS IN DATABASE:' as message;
SELECT '========================================' as message;

SELECT enumlabel as tier_value
FROM pg_enum
WHERE enumtypid = 'subscriptiontier'::regtype
ORDER BY enumsortorder;

SELECT '========================================' as message;
