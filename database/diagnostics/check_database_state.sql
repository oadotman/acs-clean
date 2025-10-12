-- ============================================================================
-- Database State Check - Run this in Supabase SQL Editor
-- ============================================================================

-- 1. Check if tables exist
SELECT 
  'Tables Check' as check_type,
  tablename,
  tableowner,
  hasindexes,
  hastriggers
FROM pg_tables
WHERE schemaname = 'public' 
  AND tablename IN ('projects', 'ad_analyses')
ORDER BY tablename;

-- 2. Check RLS status
SELECT 
  'RLS Status' as check_type,
  tablename,
  rowsecurity as rls_enabled
FROM pg_tables
WHERE schemaname = 'public' 
  AND tablename IN ('projects', 'ad_analyses');

-- 3. Check columns in projects table
SELECT 
  'Projects Columns' as check_type,
  column_name,
  data_type,
  is_nullable,
  column_default
FROM information_schema.columns
WHERE table_name = 'projects'
  AND table_schema = 'public'
ORDER BY ordinal_position;

-- 4. Check constraints on projects table
SELECT 
  'Constraints' as check_type,
  conname as constraint_name,
  contype as constraint_type,
  CASE contype
    WHEN 'p' THEN 'PRIMARY KEY'
    WHEN 'f' THEN 'FOREIGN KEY'
    WHEN 'u' THEN 'UNIQUE'
    WHEN 'c' THEN 'CHECK'
  END as type_description
FROM pg_constraint
WHERE conrelid = 'projects'::regclass;

-- 5. Check triggers on projects table
SELECT 
  'Triggers' as check_type,
  tgname as trigger_name,
  tgtype,
  tgenabled
FROM pg_trigger
WHERE tgrelid = 'projects'::regclass
  AND tgname NOT LIKE 'RI_ConstraintTrigger%';

-- 6. Check permissions
SELECT 
  'Permissions' as check_type,
  grantee,
  table_name,
  privilege_type
FROM information_schema.table_privileges
WHERE table_name = 'projects'
  AND table_schema = 'public'
ORDER BY grantee, privilege_type;

-- 7. Check if any projects exist
SELECT 
  'Data Check' as check_type,
  COUNT(*) as total_projects,
  MIN(created_at) as first_project_date,
  MAX(created_at) as last_project_date
FROM projects;

-- 8. Test direct insert (this will create a test project)
DO $$
BEGIN
  -- Try to insert a test project
  INSERT INTO projects (user_id, name, description)
  VALUES (
    '00000000-0000-0000-0000-000000000000'::uuid, 
    'SQL Test Project ' || NOW()::text, 
    'Created by diagnostic SQL'
  );
  RAISE NOTICE 'Insert successful!';
EXCEPTION
  WHEN OTHERS THEN
    RAISE NOTICE 'Insert failed: % %', SQLERRM, SQLSTATE;
END $$;

-- 9. Final status
SELECT 
  'Final Status' as check_type,
  CASE 
    WHEN EXISTS (SELECT 1 FROM pg_tables WHERE tablename = 'projects' AND schemaname = 'public')
    THEN '✅ Table exists'
    ELSE '❌ Table missing'
  END as projects_table,
  CASE 
    WHEN EXISTS (SELECT 1 FROM pg_tables WHERE tablename = 'projects' AND rowsecurity = false)
    THEN '✅ RLS disabled'
    ELSE '❌ RLS enabled'
  END as rls_status,
  (SELECT COUNT(*) FROM projects) as project_count;