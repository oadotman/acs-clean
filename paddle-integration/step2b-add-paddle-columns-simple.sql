-- =====================================================
-- STEP 2B: Add Paddle Fields (Simplified - No Enum)
-- =====================================================
-- This version works when subscription_tier is TEXT, not an enum

-- =====================================================
-- PART A: Add Paddle subscription columns
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
-- PART B: Create indexes for performance
-- =====================================================

-- Create index on paddle_subscription_id for fast webhook lookups
CREATE INDEX IF NOT EXISTS idx_user_profiles_paddle_subscription_id 
ON user_profiles(paddle_subscription_id);

-- Create index on paddle_customer_id for customer lookups
CREATE INDEX IF NOT EXISTS idx_user_profiles_paddle_customer_id 
ON user_profiles(paddle_customer_id);

-- Create index on subscription_tier for faster tier queries
CREATE INDEX IF NOT EXISTS idx_user_profiles_subscription_tier 
ON user_profiles(subscription_tier);

-- =====================================================
-- PART C: Verify the changes
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

-- Check sample of user data with new columns
SELECT 
    id,
    email,
    subscription_tier,
    paddle_subscription_id,
    paddle_customer_id,
    created_at
FROM user_profiles
LIMIT 5;

-- =====================================================
-- SUCCESS MESSAGE
-- =====================================================
-- If you see the columns and indexes above, you're done!
-- The subscription_tier column is TEXT type, which is fine.
-- It can accept any values: 'free', 'growth', 'agency_standard', 
-- 'agency_premium', 'agency_unlimited'
-- =====================================================
