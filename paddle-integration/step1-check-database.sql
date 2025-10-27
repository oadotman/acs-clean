-- =====================================================
-- STEP 1: Check Current Database Structure
-- =====================================================
-- Run these queries in your Supabase SQL Editor to understand current state
-- Copy and paste each query separately

-- Query 1: Check if user_profiles table exists and see its structure
SELECT 
    column_name, 
    data_type, 
    is_nullable,
    column_default
FROM information_schema.columns
WHERE table_name = 'user_profiles'
ORDER BY ordinal_position;

-- Query 2: Check current subscription_tier enum values
SELECT 
    e.enumlabel as tier_value
FROM pg_type t 
JOIN pg_enum e ON t.oid = e.enumtypid  
WHERE t.typname = 'subscription_tier'
ORDER BY e.enumsortorder;

-- Query 3: Check if any Paddle columns already exist
SELECT 
    column_name
FROM information_schema.columns
WHERE table_name = 'user_profiles'
AND column_name LIKE '%paddle%';

-- Query 4: Check existing indexes on user_profiles
SELECT
    indexname,
    indexdef
FROM pg_indexes
WHERE tablename = 'user_profiles';

-- Query 5: Check sample of current users to understand data
-- First, let's see what columns actually exist
SELECT column_name 
FROM information_schema.columns 
WHERE table_name = 'user_profiles';

-- Query 6: Check sample data with only confirmed columns
SELECT 
    id,
    email,
    subscription_tier,
    created_at
FROM user_profiles
LIMIT 5;

-- =====================================================
-- INSTRUCTIONS:
-- 1. Run each query above in Supabase SQL Editor
-- 2. Save the results - we need to know:
--    - Does user_profiles table exist?
--    - What subscription_tier values are currently available?
--    - Do any Paddle columns already exist?
--    - What does the current data look like?
-- 3. Share the results so we can proceed to Step 2
-- =====================================================
