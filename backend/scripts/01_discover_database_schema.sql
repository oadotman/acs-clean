-- ============================================================================
-- DISCOVERY SCRIPT: What Actually Exists in the Database
-- ============================================================================
-- Purpose: Find out the actual structure before attempting fixes
-- Run this FIRST to understand your database schema
-- ============================================================================

-- ============================================================================
-- PART 1: List ALL tables in public schema
-- ============================================================================

SELECT
    'ALL TABLES' as info,
    schemaname,
    tablename,
    tableowner
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY tablename;

-- ============================================================================
-- PART 2: Check if specific tables exist
-- ============================================================================

-- Check for users table
SELECT
    'USERS TABLE EXISTS' as info,
    EXISTS (
        SELECT FROM pg_tables
        WHERE schemaname = 'public'
        AND tablename = 'users'
    ) as table_exists;

-- Check for user_credits table
SELECT
    'USER_CREDITS TABLE EXISTS' as info,
    EXISTS (
        SELECT FROM pg_tables
        WHERE schemaname = 'public'
        AND tablename = 'user_credits'
    ) as table_exists;

-- ============================================================================
-- PART 3: Get column structure of users table
-- ============================================================================

SELECT
    'USERS TABLE COLUMNS' as info,
    column_name,
    data_type,
    character_maximum_length,
    is_nullable,
    column_default
FROM information_schema.columns
WHERE table_schema = 'public'
    AND table_name = 'users'
ORDER BY ordinal_position;

-- ============================================================================
-- PART 4: Get column structure of user_credits table (if it exists)
-- ============================================================================

SELECT
    'USER_CREDITS TABLE COLUMNS' as info,
    column_name,
    data_type,
    character_maximum_length,
    is_nullable,
    column_default
FROM information_schema.columns
WHERE table_schema = 'public'
    AND table_name = 'user_credits'
ORDER BY ordinal_position;

-- ============================================================================
-- PART 5: Find the specific user by email
-- ============================================================================

-- First, let's see what columns actually exist in users table
-- Then we can safely query it
SELECT * FROM users WHERE email = 'oadatascientist@gmail.com' LIMIT 1;

-- ============================================================================
-- PART 6: Check for any credit-related tables
-- ============================================================================

SELECT
    'CREDIT RELATED TABLES' as info,
    tablename
FROM pg_tables
WHERE schemaname = 'public'
    AND (
        tablename LIKE '%credit%'
        OR tablename LIKE '%subscription%'
        OR tablename LIKE '%plan%'
        OR tablename LIKE '%tier%'
    )
ORDER BY tablename;

-- ============================================================================
-- PART 7: Check for any transaction/audit tables
-- ============================================================================

SELECT
    'TRANSACTION TABLES' as info,
    tablename
FROM pg_tables
WHERE schemaname = 'public'
    AND (
        tablename LIKE '%transaction%'
        OR tablename LIKE '%history%'
        OR tablename LIKE '%log%'
        OR tablename LIKE '%audit%'
    )
ORDER BY tablename;

-- ============================================================================
-- PART 8: Look at the actual data structure for this user
-- ============================================================================

-- Get the user's record (all columns, whatever they are)
SELECT
    'USER RECORD' as info,
    *
FROM users
WHERE email = 'oadatascientist@gmail.com';

-- ============================================================================
-- PART 9: Find related records in other tables
-- ============================================================================

-- Try to find credit-related records using the user's ID
-- First, let's get the user's ID
WITH user_info AS (
    SELECT id, email FROM users WHERE email = 'oadatascientist@gmail.com'
)
SELECT
    'USER ID' as info,
    id,
    id::text as id_as_text,
    email
FROM user_info;

-- ============================================================================
-- PART 10: Check subscriptions table structure (if it exists)
-- ============================================================================

SELECT
    'SUBSCRIPTIONS TABLE COLUMNS' as info,
    column_name,
    data_type,
    is_nullable
FROM information_schema.columns
WHERE table_schema = 'public'
    AND table_name = 'subscriptions'
ORDER BY ordinal_position;

-- Check user's subscription records
SELECT
    'USER SUBSCRIPTIONS' as info,
    *
FROM subscriptions
WHERE user_id IN (
    SELECT id FROM users WHERE email = 'oadatascientist@gmail.com'
) OR user_id IN (
    SELECT id::text FROM users WHERE email = 'oadatascientist@gmail.com'
);

-- ============================================================================
-- PART 11: Check Paddle-related tables
-- ============================================================================

SELECT
    'PADDLE RELATED TABLES' as info,
    tablename
FROM pg_tables
WHERE schemaname = 'public'
    AND tablename LIKE '%paddle%'
ORDER BY tablename;

-- ============================================================================
-- PART 12: Search for ANY table that might contain user credits/balance
-- ============================================================================

-- Get list of all columns named 'credits' or 'balance' across all tables
SELECT
    'COLUMNS RELATED TO CREDITS' as info,
    table_name,
    column_name,
    data_type
FROM information_schema.columns
WHERE table_schema = 'public'
    AND (
        column_name LIKE '%credit%'
        OR column_name LIKE '%balance%'
        OR column_name LIKE '%unlimited%'
        OR column_name LIKE '%allowance%'
    )
ORDER BY table_name, column_name;

-- ============================================================================
-- PART 13: Check for any enum types (like SubscriptionTier)
-- ============================================================================

SELECT
    'ENUM TYPES' as info,
    t.typname as enum_name,
    e.enumlabel as enum_value,
    e.enumsortorder
FROM pg_type t
JOIN pg_enum e ON t.oid = e.enumtypid
WHERE t.typname LIKE '%subscription%'
    OR t.typname LIKE '%tier%'
    OR t.typname LIKE '%plan%'
ORDER BY t.typname, e.enumsortorder;

-- ============================================================================
-- PART 14: Summary of findings
-- ============================================================================

-- Count total tables
SELECT
    'SUMMARY' as info,
    COUNT(*) as total_public_tables
FROM pg_tables
WHERE schemaname = 'public';

-- List all table names (compact view)
SELECT
    'ALL TABLE NAMES' as info,
    string_agg(tablename, ', ' ORDER BY tablename) as tables
FROM pg_tables
WHERE schemaname = 'public';

-- ============================================================================
-- EXECUTION NOTES:
-- ============================================================================
--
-- This script will tell us:
-- 1. What tables actually exist
-- 2. What columns each table has
-- 3. What data types are used
-- 4. Where the user's data is stored
-- 5. How credits/subscriptions are structured
--
-- After running this, we'll know exactly how to write the fix script!
-- ============================================================================
