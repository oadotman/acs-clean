-- =====================================================
-- STEP 2: Add Missing Paddle Fields to Database
-- =====================================================
-- Run this AFTER you've confirmed results from Step 1
-- This adds Paddle columns and new subscription tiers

-- =====================================================
-- PART A: Add new subscription tier values
-- =====================================================

-- Add the 4 new agency tier values to the subscription_tier enum
-- Note: In PostgreSQL, you can only ADD values to an enum, not remove them
-- The old 'basic' and 'pro' tiers will remain for backward compatibility

ALTER TYPE subscription_tier ADD VALUE IF NOT EXISTS 'growth';
ALTER TYPE subscription_tier ADD VALUE IF NOT EXISTS 'agency_standard';
ALTER TYPE subscription_tier ADD VALUE IF NOT EXISTS 'agency_premium';
ALTER TYPE subscription_tier ADD VALUE IF NOT EXISTS 'agency_unlimited';

-- Verify the new values were added
SELECT 
    e.enumlabel as tier_value
FROM pg_type t 
JOIN pg_enum e ON t.oid = e.enumtypid  
WHERE t.typname = 'subscription_tier'
ORDER BY e.enumsortorder;

-- =====================================================
-- PART B: Add Paddle subscription columns
-- =====================================================

-- Add paddle_subscription_id column (stores Paddle's subscription ID)
ALTER TABLE user_profiles 
ADD COLUMN IF NOT EXISTS paddle_subscription_id TEXT;

-- Add paddle_plan_id column (stores which Paddle price/plan the user is on)
ALTER TABLE user_profiles 
ADD COLUMN IF NOT EXISTS paddle_plan_id TEXT;

-- Add paddle_checkout_id column (stores the checkout session ID)
ALTER TABLE user_profiles 
ADD COLUMN IF NOT EXISTS paddle_checkout_id TEXT;

-- Add paddle_customer_id column (stores Paddle's customer ID)
ALTER TABLE user_profiles 
ADD COLUMN IF NOT EXISTS paddle_customer_id TEXT;

-- =====================================================
-- PART C: Create indexes for performance
-- =====================================================

-- Create index on paddle_subscription_id for fast webhook lookups
CREATE INDEX IF NOT EXISTS idx_user_profiles_paddle_subscription_id 
ON user_profiles(paddle_subscription_id);

-- Create index on paddle_customer_id for customer lookups
CREATE INDEX IF NOT EXISTS idx_user_profiles_paddle_customer_id 
ON user_profiles(paddle_customer_id);

-- =====================================================
-- PART D: Verify the changes
-- =====================================================

-- Check that all columns were added successfully
SELECT 
    column_name, 
    data_type, 
    is_nullable
FROM information_schema.columns
WHERE table_name = 'user_profiles'
AND column_name LIKE '%paddle%';

-- Check that indexes were created
SELECT
    indexname,
    indexdef
FROM pg_indexes
WHERE tablename = 'user_profiles'
AND indexname LIKE '%paddle%';

-- =====================================================
-- PART E: Update existing users (optional migration)
-- =====================================================

-- If you have existing test users that need migration, you can:
-- 1. Map 'basic' tier to 'growth' tier
-- 2. Map 'pro' tier to 'agency_unlimited' tier

-- UNCOMMENT ONLY IF YOU WANT TO MIGRATE EXISTING USERS:
-- UPDATE user_profiles 
-- SET subscription_tier = 'growth' 
-- WHERE subscription_tier = 'basic';

-- UPDATE user_profiles 
-- SET subscription_tier = 'agency_unlimited' 
-- WHERE subscription_tier = 'pro';

-- =====================================================
-- INSTRUCTIONS:
-- 1. Run this entire script in Supabase SQL Editor
-- 2. Check the verification queries at the end
-- 3. Confirm all columns and indexes were created
-- 4. If you see any errors, share them so we can fix
-- =====================================================
