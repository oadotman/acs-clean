# Database Migrations - Projects Feature

## Overview

This directory contains SQL migration scripts for the AdCopySurge Projects feature.

## Running the Migration

### Step 1: Access Supabase SQL Editor

1. Go to your Supabase project dashboard: https://app.supabase.com
2. Navigate to **SQL Editor** in the left sidebar
3. Click **New Query**

### Step 2: Run the Migration Script

1. Open the file: `001_add_projects_table.sql`
2. Copy the entire contents
3. Paste into the Supabase SQL Editor
4. Click **Run** (or press Ctrl+Enter / Cmd+Enter)

### Step 3: Verify Migration Success

After running the migration, you should see success messages for:
- ✅ Projects table created
- ✅ Indexes created
- ✅ project_id column added to ad_analyses
- ✅ RLS policies created
- ✅ Triggers created

Run the verification queries at the bottom of the migration file to confirm:

```sql
-- Check if projects table exists
SELECT EXISTS (
  SELECT FROM information_schema.tables 
  WHERE table_schema = 'public' 
  AND table_name = 'projects'
) AS projects_table_exists;
-- Should return: true

-- Check if project_id column exists in ad_analyses
SELECT EXISTS (
  SELECT FROM information_schema.columns 
  WHERE table_schema = 'public' 
  AND table_name = 'ad_analyses' 
  AND column_name = 'project_id'
) AS project_id_column_exists;
-- Should return: true

-- Check RLS is enabled on projects
SELECT relname, relrowsecurity 
FROM pg_class 
WHERE relname = 'projects';
-- Should return: projects | true

-- List all policies on projects table
SELECT policyname FROM pg_policies WHERE tablename = 'projects';
-- Should return 4 policies:
--   - Users can view own projects
--   - Users can insert own projects
--   - Users can update own projects
--   - Users can delete own projects
```

### Step 4: Test with Sample Data (Optional)

Uncomment and run the sample insert at the bottom of the migration file:

```sql
INSERT INTO projects (user_id, name, description, client_name)
VALUES (
  auth.uid(), -- Will use your current authenticated user
  'Q1 2025 Campaign',
  'All ads for Q1 product launch',
  'Nike'
);
```

Then verify:
```sql
SELECT * FROM projects WHERE user_id = auth.uid();
```

## Rollback

If you need to undo the migration, uncomment and run the rollback script at the bottom of `001_add_projects_table.sql`.

⚠️ **WARNING**: This will delete ALL project data. Only use in development/testing!

## Troubleshooting

### Error: "relation auth.users does not exist"

**Solution**: Your Supabase project is using a different auth schema. Update line 14:
```sql
-- Change from:
user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,

-- To:
user_id UUID NOT NULL, -- No foreign key constraint
```

### Error: "table ad_analyses does not exist"

**Solution**: Make sure you have the `ad_analyses` table created first. Check your Supabase tables in the Table Editor.

### Error: "permission denied for schema auth"

**Solution**: Run the query as the `postgres` role or service_role in Supabase SQL Editor.

## Migration History

| Version | Date | Description |
|---------|------|-------------|
| 001 | 2025-01-05 | Initial projects table, project_id column, indexes, RLS policies |

## Next Steps

After successful migration, proceed to:
1. Build `projectsService.js` (frontend service layer)
2. Create React Query hooks (`useProjectsNew.js`)
3. Build UI components (ProjectsListNew, ProjectDetailNew)

See the main implementation guide for details.
