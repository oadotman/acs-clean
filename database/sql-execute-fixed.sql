-- ============================================================================
-- Fixed SQL Scripts - Safe to Execute in SQL Editor
-- This version removes CONCURRENTLY to avoid transaction block issues
-- ============================================================================

-- ============================================================================
-- 1. Essential Indexes for Dashboard Metrics (REQUIRED)
-- ============================================================================

-- Index for dashboard metrics queries (user + created_at + score)
CREATE INDEX IF NOT EXISTS idx_ad_analyses_user_created_score 
ON ad_analyses(user_id, created_at DESC, overall_score) 
WHERE overall_score IS NOT NULL;

-- Index for platform/industry breakdowns
CREATE INDEX IF NOT EXISTS idx_ad_analyses_platform_industry 
ON ad_analyses(user_id, platform, industry, created_at) 
WHERE overall_score IS NOT NULL;

-- ============================================================================
-- 2. Brand Voice Tables (OPTIONAL - only if you want brand voice features)
-- ============================================================================

-- Brand voice profiles table
CREATE TABLE IF NOT EXISTS brand_voice_profiles (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL,
  profile_name TEXT NOT NULL,
  
  -- Tone characteristics
  primary_tone TEXT,
  secondary_tone TEXT,
  formality_level TEXT,
  
  -- Personality traits
  personality_traits TEXT[],
  
  -- Voice attributes
  voice_attributes JSONB,
  
  -- Brand lexicon
  preferred_words TEXT[],
  prohibited_words TEXT[],
  brand_specific_terms TEXT[],
  
  -- Sample content
  brand_samples TEXT[],
  
  -- Messaging hierarchy
  messaging_hierarchy TEXT[],
  
  -- Brand values and context
  brand_values TEXT[],
  industry_context TEXT,
  target_audience_description TEXT,
  
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  
  -- Constraints
  CONSTRAINT fk_brand_voice_user FOREIGN KEY (user_id) REFERENCES user_profiles(id) ON DELETE CASCADE
);

-- Project-specific brand voice overrides
CREATE TABLE IF NOT EXISTS project_brand_voice_overrides (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  project_id UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
  brand_voice_profile_id UUID NOT NULL REFERENCES brand_voice_profiles(id) ON DELETE CASCADE,
  
  -- Override-specific adjustments
  tone_adjustments JSONB,
  vocabulary_additions TEXT[],
  context_specific_rules TEXT[],
  
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  
  UNIQUE(project_id, brand_voice_profile_id)
);

-- Brand voice analysis results
CREATE TABLE IF NOT EXISTS brand_voice_analysis_results (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  analysis_id UUID NOT NULL REFERENCES ad_analyses(id) ON DELETE CASCADE,
  brand_voice_profile_id UUID REFERENCES brand_voice_profiles(id) ON DELETE SET NULL,
  
  -- Analysis scores
  tone_consistency_score INTEGER,
  vocabulary_alignment_score INTEGER,
  personality_consistency_score INTEGER,
  overall_brand_alignment_score INTEGER,
  
  -- Detailed results
  analysis_data JSONB,
  
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Brand Voice Indexes
CREATE INDEX IF NOT EXISTS idx_brand_voice_profiles_user_id ON brand_voice_profiles(user_id);
CREATE INDEX IF NOT EXISTS idx_brand_voice_overrides_project_id ON project_brand_voice_overrides(project_id);
CREATE INDEX IF NOT EXISTS idx_brand_voice_results_analysis_id ON brand_voice_analysis_results(analysis_id);

-- Brand voice updated_at trigger (only if the trigger function exists)
DO $$
BEGIN
  IF EXISTS (SELECT 1 FROM pg_proc WHERE proname = 'update_updated_at_column') THEN
    CREATE TRIGGER update_brand_voice_profiles_updated_at
      BEFORE UPDATE ON brand_voice_profiles
      FOR EACH ROW
      EXECUTE FUNCTION update_updated_at_column();
  END IF;
EXCEPTION
  WHEN duplicate_object THEN
    -- Trigger already exists, ignore
    NULL;
END
$$;

-- ============================================================================
-- 3. VERIFICATION QUERIES (Run these to check success)
-- ============================================================================

-- Check if essential indexes were created
SELECT 
  indexname,
  tablename,
  indexdef
FROM pg_indexes 
WHERE indexname IN (
  'idx_ad_analyses_user_created_score',
  'idx_ad_analyses_platform_industry'
);

-- Check if brand voice tables were created (if you ran that section)
SELECT 
  schemaname,
  tablename,
  tableowner
FROM pg_tables 
WHERE tablename IN (
  'brand_voice_profiles',
  'project_brand_voice_overrides', 
  'brand_voice_analysis_results'
)
ORDER BY tablename;

-- Check ad_analyses table structure (ensure it has the columns we need)
SELECT column_name, data_type, is_nullable
FROM information_schema.columns
WHERE table_name = 'ad_analyses'
AND column_name IN ('user_id', 'created_at', 'overall_score', 'platform', 'industry')
ORDER BY column_name;