-- ============================================================================
-- CRITICAL FIX: Make hashed_password nullable for Supabase authentication
-- ============================================================================
-- Run this in Supabase SQL Editor FIRST before any other scripts
-- ============================================================================

-- Make hashed_password nullable
ALTER TABLE users
ALTER COLUMN hashed_password DROP NOT NULL;

-- Verify the fix
SELECT
    column_name,
    is_nullable,
    data_type,
    CASE
        WHEN is_nullable = 'YES' THEN '✅ SUCCESS! Column is now nullable'
        ELSE '❌ ERROR: Column is still NOT NULL'
    END as status
FROM information_schema.columns
WHERE table_name = 'users'
AND column_name = 'hashed_password';

-- ============================================================================
-- NEXT STEPS:
-- ============================================================================
-- 1. Run this script in Supabase SQL Editor
-- 2. Verify you see "✅ SUCCESS!"
-- 3. Test user registration (create new account)
-- 4. Then run other setup scripts if needed
-- ============================================================================
