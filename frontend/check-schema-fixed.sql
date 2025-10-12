-- AdCopySurge Database Schema Check
-- Run each query separately in Supabase SQL Editor

-- QUERY 1: Show all tables in your database
SELECT table_name FROM information_schema.tables WHERE table_schema = 'public' ORDER BY table_name;

-- QUERY 2: Check if critical tables exist
SELECT 
    'user_credits' as table_name,
    CASE WHEN EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'user_credits') 
         THEN '✅ EXISTS' ELSE '❌ MISSING' END as status;

-- QUERY 3: Check credit_transactions table
SELECT 
    'credit_transactions' as table_name,
    CASE WHEN EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'credit_transactions') 
         THEN '✅ EXISTS' ELSE '❌ MISSING' END as status;

-- QUERY 4: Check ad_analyses table
SELECT 
    'ad_analyses' as table_name,
    CASE WHEN EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'ad_analyses') 
         THEN '✅ EXISTS' ELSE '❌ MISSING' END as status;
