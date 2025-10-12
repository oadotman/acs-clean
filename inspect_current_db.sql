-- Run these queries one by one in Supabase SQL Editor
-- Copy and paste the results back to me

-- QUERY 1: Check if team management tables exist
SELECT 
  schemaname,
  tablename,
  'TABLE' as object_type
FROM pg_tables 
WHERE schemaname = 'public' 
  AND tablename IN (
    'agencies', 'agency_team_members', 'agency_invitations', 
    'agency_team_member_analytics', 'team_members', 'team_invitations',
    'team_roles', 'project_team_access', 'subscription_tiers'
  )
ORDER BY tablename;

-- QUERY 2: Check user_profiles columns in detail
SELECT column_name, data_type, is_nullable, column_default 
FROM information_schema.columns 
WHERE table_schema = 'public' AND table_name = 'user_profiles'
ORDER BY ordinal_position;

-- QUERY 3: Check projects columns in detail
SELECT column_name, data_type, is_nullable, column_default 
FROM information_schema.columns 
WHERE table_schema = 'public' AND table_name = 'projects'  
ORDER BY ordinal_position;

-- QUERY 4: Check if tables exist at all
SELECT tablename
FROM pg_tables 
WHERE schemaname = 'public'
ORDER BY tablename;
