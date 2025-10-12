-- ============================================================================
-- IMMEDIATE FIX for Authentication Issues
-- Run this in your Supabase SQL editor
-- ============================================================================

-- Check if user profile exists for current user
INSERT INTO user_profiles (id, email, subscription_tier, monthly_analyses)
SELECT 
  auth.uid() as id,
  auth.email() as email,
  'free' as subscription_tier,
  0 as monthly_analyses
WHERE auth.uid() IS NOT NULL
ON CONFLICT (id) DO NOTHING;

-- Ensure RLS is disabled (as per your setup script)
ALTER TABLE user_profiles DISABLE ROW LEVEL SECURITY;
ALTER TABLE projects DISABLE ROW LEVEL SECURITY;
ALTER TABLE ad_analyses DISABLE ROW LEVEL SECURITY;

-- Grant permissions to authenticated users
GRANT ALL ON user_profiles TO authenticated;
GRANT ALL ON projects TO authenticated;  
GRANT ALL ON ad_analyses TO authenticated;

-- Check current auth state
SELECT 
  'Current User:' as info,
  auth.uid() as user_id,
  auth.email() as email;

-- Check if projects exist
SELECT 
  'Projects Count:' as info,
  COUNT(*) as count
FROM projects;

-- Check if user_profiles exist
SELECT 
  'User Profiles Count:' as info,
  COUNT(*) as count
FROM user_profiles;

-- Create a test project if none exist (for debugging)
INSERT INTO projects (user_id, name, description, client_name)
SELECT 
  auth.uid(),
  'Test Project (Debug)',
  'Created to fix authentication issues',
  'Debug Client'
WHERE auth.uid() IS NOT NULL
  AND NOT EXISTS (SELECT 1 FROM projects WHERE user_id = auth.uid())
ON CONFLICT DO NOTHING;

-- Verify the fix
SELECT 
  'Verification:' as info,
  p.id,
  p.name,
  p.user_id
FROM projects p
WHERE p.user_id = auth.uid()
LIMIT 5;