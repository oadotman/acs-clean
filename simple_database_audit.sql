-- SIMPLE SUPABASE DATABASE AUDIT
-- Run each section separately in Supabase SQL Editor

-- ==========================================
-- STEP 1: What tables exist in public schema?
-- ==========================================
SELECT 
    table_name,
    table_type
FROM information_schema.tables 
WHERE table_schema = 'public'
ORDER BY table_name;