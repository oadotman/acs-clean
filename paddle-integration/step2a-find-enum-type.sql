-- Find the actual enum type name for subscription tiers
-- Run this first to see what enum type your database uses

-- Query 1: Find all enum types in your database
SELECT 
    t.typname AS enum_name,
    e.enumlabel AS enum_value
FROM pg_type t 
JOIN pg_enum e ON t.oid = e.enumtypid  
WHERE t.typname LIKE '%subscription%' OR t.typname LIKE '%tier%'
ORDER BY t.typname, e.enumsortorder;

-- Query 2: Check the column definition for subscription_tier
SELECT 
    column_name,
    udt_name,
    data_type
FROM information_schema.columns
WHERE table_name = 'user_profiles' 
AND column_name = 'subscription_tier';

-- Query 3: Get all enum types
SELECT typname 
FROM pg_type 
WHERE typtype = 'e'
ORDER BY typname;
