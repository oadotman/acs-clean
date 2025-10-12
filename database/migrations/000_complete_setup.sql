-- ============================================================================
-- AdCopySurge Complete Database Setup
-- This script creates all tables from scratch with proper structure
-- RLS is DISABLED to avoid authentication issues with frontend
-- ============================================================================

-- ============================================================================
-- STEP 1: Drop existing tables (in correct order to handle foreign keys)
-- ============================================================================

-- New supporting tables (drop first due to FKs)
DROP TABLE IF EXISTS ad_generations CASCADE;
DROP TABLE IF EXISTS competitor_benchmarks CASCADE;

-- Core tables
DROP TABLE IF EXISTS ad_analyses CASCADE;
DROP TABLE IF EXISTS projects CASCADE;
DROP TABLE IF EXISTS user_profiles CASCADE;

-- ============================================================================
-- STEP 2: Create user_profiles table (for quotas and subscriptions)
-- ============================================================================

CREATE TABLE user_profiles (
  id UUID PRIMARY KEY, -- Matches auth.users.id
  email TEXT,
  subscription_tier TEXT NOT NULL DEFAULT 'free', -- free | basic | pro
  monthly_analyses INTEGER NOT NULL DEFAULT 0,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

COMMENT ON TABLE user_profiles IS 'Per-user profile for subscription and quotas';
COMMENT ON COLUMN user_profiles.subscription_tier IS 'free | basic | pro';
COMMENT ON COLUMN user_profiles.monthly_analyses IS 'Number of analyses performed in the current month';

-- Backfill profiles for existing users so quota checks work immediately
INSERT INTO user_profiles (id, email)
SELECT id, email FROM auth.users
ON CONFLICT (id) DO NOTHING;

-- ============================================================================
-- STEP 3: Create projects table
-- ============================================================================

CREATE TABLE projects (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL,
  name TEXT NOT NULL,
  description TEXT,
  client_name TEXT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Add comments for documentation
COMMENT ON TABLE projects IS 'Projects for organizing ad analyses by client, campaign, or category';
COMMENT ON COLUMN projects.id IS 'Unique project identifier';
COMMENT ON COLUMN projects.user_id IS 'ID of the user who owns this project';
COMMENT ON COLUMN projects.name IS 'Project name (required)';
COMMENT ON COLUMN projects.description IS 'Optional project description';
COMMENT ON COLUMN projects.client_name IS 'Optional client name for the project';

-- ============================================================================
-- STEP 4: Create ad_analyses table
-- ============================================================================

CREATE TABLE ad_analyses (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL,
  project_id UUID,
  headline TEXT NOT NULL,
  body_text TEXT NOT NULL,
  cta TEXT,
  platform TEXT NOT NULL,
  target_audience TEXT, -- NEW
  industry TEXT,        -- NEW
  overall_score INTEGER,
  clarity_score INTEGER,
  persuasion_score INTEGER,
  emotion_score INTEGER,
  cta_strength_score INTEGER,
  platform_fit_score INTEGER,
  feedback TEXT,
  suggestions TEXT,
  analysis_data JSONB,  -- NEW: store AI result payloads
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  
  -- Foreign key to projects (nullable - analyses can exist without a project)
  CONSTRAINT fk_ad_analyses_project 
    FOREIGN KEY (project_id) 
    REFERENCES projects(id) 
    ON DELETE SET NULL
);

-- Add comments for documentation
COMMENT ON TABLE ad_analyses IS 'Ad copy analyses with scores and feedback';
COMMENT ON COLUMN ad_analyses.id IS 'Unique analysis identifier';
COMMENT ON COLUMN ad_analyses.user_id IS 'ID of the user who owns this analysis';
COMMENT ON COLUMN ad_analyses.project_id IS 'Optional project this analysis belongs to';
COMMENT ON COLUMN ad_analyses.platform IS 'Ad platform (facebook, instagram, google, linkedin, twitter, tiktok)';
COMMENT ON COLUMN ad_analyses.overall_score IS 'Overall ad quality score (0-100)';

-- ============================================================================
-- STEP 4: Create indexes for performance
-- ============================================================================

-- Projects indexes
CREATE INDEX idx_projects_user_id ON projects(user_id);
CREATE INDEX idx_projects_created_at ON projects(created_at DESC);
CREATE INDEX idx_projects_name ON projects(name);

-- Ad analyses indexes
CREATE INDEX idx_ad_analyses_user_id ON ad_analyses(user_id);
CREATE INDEX idx_ad_analyses_project_id ON ad_analyses(project_id);
CREATE INDEX idx_ad_analyses_created_at ON ad_analyses(created_at DESC);
CREATE INDEX idx_ad_analyses_platform ON ad_analyses(platform);
CREATE INDEX idx_ad_analyses_industry ON ad_analyses(industry);

-- ============================================================================
-- STEP 5: Supporting tables for competitor benchmarks and generations
-- ============================================================================

CREATE TABLE competitor_benchmarks (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  analysis_id UUID NOT NULL REFERENCES ad_analyses(id) ON DELETE CASCADE,
  competitor_headline TEXT,
  competitor_body_text TEXT,
  competitor_cta TEXT,
  competitor_platform TEXT,
  source_url TEXT,
  competitor_overall_score INTEGER,
  competitor_clarity_score INTEGER,
  competitor_emotion_score INTEGER,
  competitor_cta_score INTEGER,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_competitor_benchmarks_analysis_id ON competitor_benchmarks(analysis_id);

CREATE TABLE ad_generations (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  analysis_id UUID NOT NULL REFERENCES ad_analyses(id) ON DELETE CASCADE,
  variant_type TEXT,
  generated_headline TEXT,
  generated_body_text TEXT,
  generated_cta TEXT,
  improvement_reason TEXT,
  predicted_score INTEGER,
  user_rating INTEGER,
  user_selected BOOLEAN NOT NULL DEFAULT FALSE,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_ad_generations_analysis_id ON ad_generations(analysis_id);

-- ============================================================================
-- STEP 5: Create updated_at trigger function
-- ============================================================================

CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Apply trigger to projects table
CREATE TRIGGER update_projects_updated_at
  BEFORE UPDATE ON projects
  FOR EACH ROW
  EXECUTE FUNCTION update_updated_at_column();

-- Apply trigger to ad_analyses table
CREATE TRIGGER update_ad_analyses_updated_at
  BEFORE UPDATE ON ad_analyses
  FOR EACH ROW
  EXECUTE FUNCTION update_updated_at_column();

-- Apply trigger to user_profiles table
CREATE TRIGGER update_user_profiles_updated_at
  BEFORE UPDATE ON user_profiles
  FOR EACH ROW
  EXECUTE FUNCTION update_updated_at_column();

-- ============================================================================
-- STEP 6: Disable RLS (to avoid auth.uid() issues with frontend)
-- ============================================================================

ALTER TABLE projects DISABLE ROW LEVEL SECURITY;
ALTER TABLE ad_analyses DISABLE ROW LEVEL SECURITY;
ALTER TABLE user_profiles DISABLE ROW LEVEL SECURITY;
ALTER TABLE competitor_benchmarks DISABLE ROW LEVEL SECURITY;
ALTER TABLE ad_generations DISABLE ROW LEVEL SECURITY;

-- ============================================================================
-- STEP 7: Grant permissions to all roles
-- ============================================================================

-- Projects permissions
GRANT ALL ON projects TO anon;
GRANT ALL ON projects TO authenticated;
GRANT ALL ON projects TO service_role;

-- Ad analyses permissions
GRANT ALL ON ad_analyses TO anon;
GRANT ALL ON ad_analyses TO authenticated;
GRANT ALL ON ad_analyses TO service_role;

-- User profiles permissions
GRANT ALL ON user_profiles TO anon;
GRANT ALL ON user_profiles TO authenticated;
GRANT ALL ON user_profiles TO service_role;

-- Supporting tables permissions
GRANT ALL ON competitor_benchmarks TO anon;
GRANT ALL ON competitor_benchmarks TO authenticated;
GRANT ALL ON competitor_benchmarks TO service_role;

GRANT ALL ON ad_generations TO anon;
GRANT ALL ON ad_generations TO authenticated;
GRANT ALL ON ad_generations TO service_role;

-- ============================================================================
-- STEP 8: Utility functions (RPC)
-- ============================================================================

-- Increment analysis count for a user (creates profile if missing)
CREATE OR REPLACE FUNCTION increment_user_analysis_count(p_user_id UUID)
RETURNS VOID AS $$
BEGIN
  INSERT INTO user_profiles (id, monthly_analyses, created_at, updated_at)
  VALUES (p_user_id, 1, NOW(), NOW())
  ON CONFLICT (id) DO UPDATE SET
    monthly_analyses = user_profiles.monthly_analyses + 1,
    updated_at = NOW();
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

GRANT EXECUTE ON FUNCTION increment_user_analysis_count(UUID) TO anon, authenticated, service_role;

-- ============================================================================
-- STEP 9: Insert sample data (optional - for testing)
-- ============================================================================

-- You can uncomment this section to add sample data for testing
/*
-- Sample project
INSERT INTO projects (user_id, name, description, client_name)
VALUES (
  '00000000-0000-0000-0000-000000000000', -- Replace with your actual user ID
  'Sample Campaign 2024',
  'Q1 Marketing Campaign',
  'Acme Corp'
);

-- Sample analysis (without project)
INSERT INTO ad_analyses (user_id, headline, body_text, cta, platform, overall_score)
VALUES (
  '00000000-0000-0000-0000-000000000000', -- Replace with your actual user ID
  'Amazing Product Launch',
  'Discover the future of innovation',
  'Learn More',
  'facebook',
  85
);
*/

-- ============================================================================
-- STEP 9: Verification queries
-- ============================================================================

-- Check tables exist
SELECT 
  table_name,
  (SELECT COUNT(*) FROM information_schema.columns WHERE table_name = t.table_name) as column_count
FROM information_schema.tables t
WHERE table_schema = 'public' 
  AND table_name IN ('projects', 'ad_analyses', 'user_profiles', 'competitor_benchmarks', 'ad_generations')
ORDER BY table_name;

-- Check RLS status (should be false/disabled)
SELECT 
  schemaname,
  tablename,
  rowsecurity as rls_enabled
FROM pg_tables
WHERE tablename IN ('projects', 'ad_analyses', 'user_profiles', 'competitor_benchmarks', 'ad_generations')
ORDER BY tablename;

-- Check indexes
SELECT 
  tablename,
  indexname,
  indexdef
FROM pg_indexes
WHERE tablename IN ('projects', 'ad_analyses', 'competitor_benchmarks', 'ad_generations')
ORDER BY tablename, indexname;

-- Check foreign keys
SELECT
  tc.table_name,
  tc.constraint_name,
  kcu.column_name,
  ccu.table_name AS foreign_table_name,
  ccu.column_name AS foreign_column_name
FROM information_schema.table_constraints AS tc
JOIN information_schema.key_column_usage AS kcu
  ON tc.constraint_name = kcu.constraint_name
JOIN information_schema.constraint_column_usage AS ccu
  ON ccu.constraint_name = tc.constraint_name
WHERE tc.constraint_type = 'FOREIGN KEY'
  AND tc.table_name IN ('projects', 'ad_analyses');

-- Summary
SELECT 
  '✅ Setup Complete!' as status,
  'Tables created (projects, ad_analyses, user_profiles, competitor_benchmarks, ad_generations), indexes added, RLS disabled, permissions granted' as details;

-- ============================================================================
-- NOTES:
-- ============================================================================
-- 1. RLS is DISABLED on both tables to avoid authentication issues
-- 2. Your frontend should handle user filtering (filter by user_id in queries)
-- 3. Foreign key constraint uses ON DELETE SET NULL (analyses persist when project deleted)
-- 4. All timestamps use TIMESTAMPTZ for proper timezone handling
-- 5. updated_at triggers automatically update the timestamp on record changes
-- ============================================================================
