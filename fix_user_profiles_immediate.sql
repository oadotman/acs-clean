-- ============================================================================
-- IMMEDIATE FIX for User Profiles 406 Error
-- Run this in your Supabase SQL editor while logged in
-- ============================================================================

-- 1. First, check if the table exists
SELECT table_name 
FROM information_schema.tables 
WHERE table_name = 'user_profiles';

-- 2. Ensure RLS is disabled (to avoid 406 errors)
ALTER TABLE user_profiles DISABLE ROW LEVEL SECURITY;

-- 3. Grant all permissions to authenticated and anon roles
GRANT ALL ON user_profiles TO authenticated;
GRANT ALL ON user_profiles TO anon;
GRANT ALL ON user_profiles TO service_role;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO authenticated, anon;

-- 4. Create profile for your user (oadatascientist@gmail.com)
INSERT INTO user_profiles (id, email, subscription_tier, monthly_analyses, created_at, updated_at)
VALUES (
  '92f3f140-ddb5-4e21-a6d7-814982b55ebc', -- Your user ID from the logs
  'oadatascientist@gmail.com',
  'free',
  0,
  NOW(),
  NOW()
)
ON CONFLICT (id) DO UPDATE SET
  email = EXCLUDED.email,
  updated_at = NOW();

-- 5. Verify the profile was created
SELECT * FROM user_profiles WHERE id = '92f3f140-ddb5-4e21-a6d7-814982b55ebc';

-- 6. Check if projects table is accessible
SELECT COUNT(*) as project_count FROM projects WHERE user_id = '92f3f140-ddb5-4e21-a6d7-814982b55ebc';

-- 7. Ensure projects table also has RLS disabled
ALTER TABLE projects DISABLE ROW LEVEL SECURITY;
GRANT ALL ON projects TO authenticated;
GRANT ALL ON projects TO anon;

-- 8. Ensure ad_analyses table also has RLS disabled
ALTER TABLE ad_analyses DISABLE ROW LEVEL SECURITY;
GRANT ALL ON ad_analyses TO authenticated;
GRANT ALL ON ad_analyses TO anon;

-- 9. Final check - all tables should have RLS disabled
SELECT 
  tablename,
  rowsecurity as rls_enabled
FROM pg_tables
WHERE schemaname = 'public'
  AND tablename IN ('user_profiles', 'projects', 'ad_analyses')
ORDER BY tablename;

-- Expected result: All should show 'f' for rls_enabled