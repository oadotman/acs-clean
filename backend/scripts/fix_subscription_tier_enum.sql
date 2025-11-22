-- Fix: Add missing subscription tier enum values
-- This adds agency_standard, agency_premium, agency_unlimited to the enum

-- First, check what values currently exist
SELECT enumlabel FROM pg_enum
WHERE enumtypid = 'subscriptiontier'::regtype
ORDER BY enumsortorder;

-- Add missing enum values if they don't exist
-- Note: ALTER TYPE ADD VALUE cannot be run inside a transaction block in older PostgreSQL
-- If this fails, run each ALTER TYPE command separately outside of BEGIN/COMMIT

DO $$
BEGIN
    -- Add agency_standard if it doesn't exist
    IF NOT EXISTS (
        SELECT 1 FROM pg_enum
        WHERE enumtypid = 'subscriptiontier'::regtype
        AND enumlabel = 'agency_standard'
    ) THEN
        ALTER TYPE subscriptiontier ADD VALUE 'agency_standard';
        RAISE NOTICE 'Added agency_standard to subscriptiontier enum';
    ELSE
        RAISE NOTICE 'agency_standard already exists';
    END IF;
END $$;

DO $$
BEGIN
    -- Add agency_premium if it doesn't exist
    IF NOT EXISTS (
        SELECT 1 FROM pg_enum
        WHERE enumtypid = 'subscriptiontier'::regtype
        AND enumlabel = 'agency_premium'
    ) THEN
        ALTER TYPE subscriptiontier ADD VALUE 'agency_premium';
        RAISE NOTICE 'Added agency_premium to subscriptiontier enum';
    ELSE
        RAISE NOTICE 'agency_premium already exists';
    END IF;
END $$;

DO $$
BEGIN
    -- Add agency_unlimited if it doesn't exist
    IF NOT EXISTS (
        SELECT 1 FROM pg_enum
        WHERE enumtypid = 'subscriptiontier'::regtype
        AND enumlabel = 'agency_unlimited'
    ) THEN
        ALTER TYPE subscriptiontier ADD VALUE 'agency_unlimited';
        RAISE NOTICE 'Added agency_unlimited to subscriptiontier enum';
    ELSE
        RAISE NOTICE 'agency_unlimited already exists';
    END IF;
END $$;

-- Verify all values exist now
SELECT enumlabel as tier FROM pg_enum
WHERE enumtypid = 'subscriptiontier'::regtype
ORDER BY enumsortorder;

-- Expected output:
-- tier
-- ----------------
-- free
-- basic
-- pro
-- growth
-- agency_standard
-- agency_premium
-- agency_unlimited
