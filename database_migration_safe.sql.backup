-- AdCopySurge Safe Database Migration Script
-- Purpose: Fix 401 errors by creating missing tables safely (handles existing tables)
-- Date: 2025-01-12
-- Version: 1.1 (Safe Mode)

-- Enable Row Level Security on public schema
SET search_path TO public;

-- ======================================================================================
-- SAFE TABLE CREATION - ONLY CREATE IF NOT EXISTS
-- ======================================================================================

DO $$ 
BEGIN
    RAISE NOTICE '🚀 Starting AdCopySurge safe database migration...';
    RAISE NOTICE '📋 This script will only create missing tables and policies';
END $$;

-- ======================================================================================
-- 1. USER PROFILES TABLE (CREATE ONLY IF NOT EXISTS)
-- ======================================================================================

DO $$ 
BEGIN
    -- Check if user_profiles table exists
    IF NOT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'user_profiles') THEN
        RAISE NOTICE '📝 Creating user_profiles table...';
        
        CREATE TABLE user_profiles (
            id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
            email VARCHAR(255) NOT NULL UNIQUE,
            full_name VARCHAR(255),
            company VARCHAR(255),
            industry VARCHAR(100),
            role VARCHAR(100),
            team_size VARCHAR(20),
            goals JSONB DEFAULT '[]'::JSONB,
            
            -- Subscription fields
            subscription_tier VARCHAR(50) DEFAULT 'free' NOT NULL,
            subscription_active BOOLEAN DEFAULT TRUE,
            subscription_expires_at TIMESTAMP WITH TIME ZONE,
            
            -- Usage tracking
            monthly_analyses INTEGER DEFAULT 0,
            total_analyses INTEGER DEFAULT 0,
            
            -- Onboarding
            has_completed_onboarding BOOLEAN DEFAULT FALSE,
            onboarding_completed_at TIMESTAMP WITH TIME ZONE,
            
            -- Timestamps
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        );
        
        RAISE NOTICE '✅ user_profiles table created successfully';
    ELSE
        RAISE NOTICE '⏭️ user_profiles table already exists, adding missing columns if needed...';
        
        -- Add missing columns to existing table
        BEGIN
            ALTER TABLE user_profiles ADD COLUMN IF NOT EXISTS has_completed_onboarding BOOLEAN DEFAULT FALSE;
            ALTER TABLE user_profiles ADD COLUMN IF NOT EXISTS onboarding_completed_at TIMESTAMP WITH TIME ZONE;
            ALTER TABLE user_profiles ADD COLUMN IF NOT EXISTS goals JSONB DEFAULT '[]'::JSONB;
            ALTER TABLE user_profiles ADD COLUMN IF NOT EXISTS industry VARCHAR(100);
            ALTER TABLE user_profiles ADD COLUMN IF NOT EXISTS role VARCHAR(100);
            ALTER TABLE user_profiles ADD COLUMN IF NOT EXISTS team_size VARCHAR(20);
            RAISE NOTICE '✅ user_profiles columns updated';
        EXCEPTION
            WHEN others THEN
                RAISE NOTICE '⚠️ Some user_profiles columns may already exist: %', SQLERRM;
        END;
    END IF;
END $$;

-- Enable RLS on user_profiles
ALTER TABLE user_profiles ENABLE ROW LEVEL SECURITY;

-- Create RLS policy for user_profiles (drop and recreate to avoid conflicts)
DROP POLICY IF EXISTS "Users can access their own profile" ON user_profiles;
CREATE POLICY "Users can access their own profile" ON user_profiles
    FOR ALL USING (auth.uid() = id);

-- ======================================================================================
-- 2. AD COPY PROJECTS TABLE (THE CRITICAL MISSING TABLE)
-- ======================================================================================

DO $$ 
BEGIN
    -- Check if ad_copy_projects table exists
    IF NOT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'ad_copy_projects') THEN
        RAISE NOTICE '🎯 Creating ad_copy_projects table (this fixes the main 401 error)...';
        
        CREATE TABLE ad_copy_projects (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
            project_name VARCHAR(255) NOT NULL,
            description TEXT,
            
            -- Ad copy content
            headline VARCHAR(500) NOT NULL,
            body_text TEXT NOT NULL,
            cta VARCHAR(100) NOT NULL,
            platform VARCHAR(50) NOT NULL DEFAULT 'facebook',
            industry VARCHAR(100),
            target_audience TEXT,
            
            -- Analysis configuration
            enabled_tools JSONB DEFAULT '["compliance", "legal_risk", "brand_voice", "psychology"]'::JSONB,
            auto_chain_analysis BOOLEAN DEFAULT TRUE,
            
            -- Project metadata
            tags JSONB DEFAULT '[]'::JSONB,
            status VARCHAR(50) DEFAULT 'draft',
            
            -- Timestamps
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        );
        
        RAISE NOTICE '✅ ad_copy_projects table created - this should fix 401 errors!';
    ELSE
        RAISE NOTICE '✅ ad_copy_projects table already exists';
    END IF;
END $$;

-- Enable RLS on ad_copy_projects
ALTER TABLE ad_copy_projects ENABLE ROW LEVEL SECURITY;

-- Create RLS policy for ad_copy_projects
DROP POLICY IF EXISTS "Users can access their own projects" ON ad_copy_projects;
CREATE POLICY "Users can access their own projects" ON ad_copy_projects
    FOR ALL USING (auth.uid() = user_id);

-- ======================================================================================
-- 3. TOOL ANALYSIS RESULTS TABLE
-- ======================================================================================

DO $$ 
BEGIN
    IF NOT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'tool_analysis_results') THEN
        RAISE NOTICE '📊 Creating tool_analysis_results table...';
        
        CREATE TABLE tool_analysis_results (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            project_id UUID NOT NULL REFERENCES ad_copy_projects(id) ON DELETE CASCADE,
            user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
            tool_id VARCHAR(50) NOT NULL,
            
            -- Analysis results
            overall_score INTEGER CHECK (overall_score >= 0 AND overall_score <= 100),
            detailed_scores JSONB DEFAULT '{}'::JSONB,
            suggestions JSONB DEFAULT '[]'::JSONB,
            warnings JSONB DEFAULT '[]'::JSONB,
            raw_analysis_data JSONB DEFAULT '{}'::JSONB,
            
            -- Processing status
            status VARCHAR(50) DEFAULT 'pending',
            error_message TEXT,
            processing_time_ms INTEGER,
            
            -- Timestamps
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        );
        
        RAISE NOTICE '✅ tool_analysis_results table created';
    ELSE
        RAISE NOTICE '✅ tool_analysis_results table already exists';
    END IF;
END $$;

-- Enable RLS and create policy
ALTER TABLE tool_analysis_results ENABLE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS "Users can access their own analysis results" ON tool_analysis_results;
CREATE POLICY "Users can access their own analysis results" ON tool_analysis_results
    FOR ALL USING (auth.uid() = user_id);

-- ======================================================================================
-- 4. ANALYSIS PIPELINE RUNS TABLE  
-- ======================================================================================

DO $$ 
BEGIN
    IF NOT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'analysis_pipeline_runs') THEN
        RAISE NOTICE '⚙️ Creating analysis_pipeline_runs table...';
        
        CREATE TABLE analysis_pipeline_runs (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            project_id UUID NOT NULL REFERENCES ad_copy_projects(id) ON DELETE CASCADE,
            user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
            
            -- Pipeline configuration
            tools_requested JSONB NOT NULL,
            tools_completed JSONB DEFAULT '[]'::JSONB,
            
            -- Overall status
            status VARCHAR(50) DEFAULT 'pending',
            progress_percentage INTEGER DEFAULT 0 CHECK (progress_percentage >= 0 AND progress_percentage <= 100),
            
            -- Summary results
            overall_score INTEGER CHECK (overall_score >= 0 AND overall_score <= 100),
            total_suggestions INTEGER DEFAULT 0,
            total_warnings INTEGER DEFAULT 0,
            
            -- Performance metrics
            started_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            completed_at TIMESTAMP WITH TIME ZONE,
            total_processing_time_ms INTEGER,
            
            -- Timestamps
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        );
        
        RAISE NOTICE '✅ analysis_pipeline_runs table created';
    ELSE
        RAISE NOTICE '✅ analysis_pipeline_runs table already exists';
    END IF;
END $$;

-- Enable RLS and create policy
ALTER TABLE analysis_pipeline_runs ENABLE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS "Users can access their own pipeline runs" ON analysis_pipeline_runs;
CREATE POLICY "Users can access their own pipeline runs" ON analysis_pipeline_runs
    FOR ALL USING (auth.uid() = user_id);

-- ======================================================================================
-- 5. HANDLE EXISTING TABLES (ad_analyses, competitor_benchmarks, ad_generations)
-- ======================================================================================

-- These tables already exist, so just ensure RLS is enabled and policies exist

-- Fix ad_analyses table
DO $$
BEGIN
    RAISE NOTICE '🔧 Ensuring ad_analyses table has proper RLS policies...';
    
    -- Enable RLS if not already enabled
    ALTER TABLE ad_analyses ENABLE ROW LEVEL SECURITY;
    
    -- Recreate policy to ensure it exists
    DROP POLICY IF EXISTS "Users can access their own legacy analyses" ON ad_analyses;
    CREATE POLICY "Users can access their own legacy analyses" ON ad_analyses
        FOR ALL USING (auth.uid() = user_id);
    
    RAISE NOTICE '✅ ad_analyses RLS policies updated';
END $$;

-- Fix competitor_benchmarks table (if it exists)
DO $$
BEGIN
    IF EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'competitor_benchmarks') THEN
        RAISE NOTICE '🔧 Ensuring competitor_benchmarks table has proper RLS policies...';
        
        ALTER TABLE competitor_benchmarks ENABLE ROW LEVEL SECURITY;
        
        DROP POLICY IF EXISTS "Users can access benchmarks for their analyses" ON competitor_benchmarks;
        CREATE POLICY "Users can access benchmarks for their analyses" ON competitor_benchmarks
            FOR ALL USING (
                analysis_id IN (
                    SELECT id FROM ad_analyses WHERE user_id = auth.uid()
                )
            );
        
        RAISE NOTICE '✅ competitor_benchmarks RLS policies updated';
    END IF;
END $$;

-- Fix ad_generations table (if it exists)
DO $$
BEGIN
    IF EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'ad_generations') THEN
        RAISE NOTICE '🔧 Ensuring ad_generations table has proper RLS policies...';
        
        ALTER TABLE ad_generations ENABLE ROW LEVEL SECURITY;
        
        DROP POLICY IF EXISTS "Users can access generations for their analyses" ON ad_generations;
        CREATE POLICY "Users can access generations for their analyses" ON ad_generations
            FOR ALL USING (
                analysis_id IN (
                    SELECT id FROM ad_analyses WHERE user_id = auth.uid()
                )
            );
        
        RAISE NOTICE '✅ ad_generations RLS policies updated';
    END IF;
END $$;

-- ======================================================================================
-- 6. CREATE INDEXES (ONLY IF NOT EXISTS)
-- ======================================================================================

DO $$
BEGIN
    RAISE NOTICE '📈 Creating performance indexes...';
END $$;

-- Create indexes safely
CREATE INDEX IF NOT EXISTS idx_user_profiles_email ON user_profiles(email);
CREATE INDEX IF NOT EXISTS idx_ad_copy_projects_user_id ON ad_copy_projects(user_id);
CREATE INDEX IF NOT EXISTS idx_ad_copy_projects_created_at ON ad_copy_projects(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_tool_analysis_results_project_id ON tool_analysis_results(project_id);
CREATE INDEX IF NOT EXISTS idx_tool_analysis_results_user_id ON tool_analysis_results(user_id);
CREATE INDEX IF NOT EXISTS idx_tool_analysis_results_tool_id ON tool_analysis_results(tool_id);
CREATE INDEX IF NOT EXISTS idx_analysis_pipeline_runs_project_id ON analysis_pipeline_runs(project_id);
CREATE INDEX IF NOT EXISTS idx_analysis_pipeline_runs_user_id ON analysis_pipeline_runs(user_id);
CREATE INDEX IF NOT EXISTS idx_ad_analyses_user_id ON ad_analyses(user_id);
CREATE INDEX IF NOT EXISTS idx_ad_analyses_created_at ON ad_analyses(created_at DESC);

-- ======================================================================================
-- 7. CREATE/UPDATE UTILITY FUNCTIONS
-- ======================================================================================

-- Function to update updated_at timestamps
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create triggers safely (drop first to avoid conflicts)
DROP TRIGGER IF EXISTS update_user_profiles_updated_at ON user_profiles;
CREATE TRIGGER update_user_profiles_updated_at BEFORE UPDATE ON user_profiles
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_ad_copy_projects_updated_at ON ad_copy_projects;
CREATE TRIGGER update_ad_copy_projects_updated_at BEFORE UPDATE ON ad_copy_projects
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Only create triggers for tables that exist
DO $$
BEGIN
    IF EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'tool_analysis_results') THEN
        DROP TRIGGER IF EXISTS update_tool_analysis_results_updated_at ON tool_analysis_results;
        CREATE TRIGGER update_tool_analysis_results_updated_at BEFORE UPDATE ON tool_analysis_results
            FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
    END IF;
    
    IF EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'analysis_pipeline_runs') THEN
        DROP TRIGGER IF EXISTS update_analysis_pipeline_runs_updated_at ON analysis_pipeline_runs;
        CREATE TRIGGER update_analysis_pipeline_runs_updated_at BEFORE UPDATE ON analysis_pipeline_runs
            FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
    END IF;
    
    DROP TRIGGER IF EXISTS update_ad_analyses_updated_at ON ad_analyses;
    CREATE TRIGGER update_ad_analyses_updated_at BEFORE UPDATE ON ad_analyses
        FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
END $$;

-- User quota checking function
CREATE OR REPLACE FUNCTION check_user_quota(user_id UUID)
RETURNS JSONB AS $$
DECLARE
    user_profile user_profiles;
    monthly_count INTEGER;
    quota_limit INTEGER;
    result JSONB;
BEGIN
    -- Get user profile
    SELECT * INTO user_profile FROM user_profiles WHERE id = user_id;
    
    IF NOT FOUND THEN
        RETURN jsonb_build_object(
            'can_analyze', false,
            'reason', 'User profile not found',
            'monthly_analyses', 0,
            'quota_limit', 0
        );
    END IF;
    
    -- Set quota limit based on subscription tier
    CASE user_profile.subscription_tier
        WHEN 'free' THEN quota_limit := 5;
        WHEN 'basic' THEN quota_limit := 50;
        WHEN 'pro' THEN quota_limit := 500;
        WHEN 'enterprise' THEN quota_limit := 999999;
        ELSE quota_limit := 5;
    END CASE;
    
    -- Get current month's analysis count (use either table that exists)
    IF EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'analysis_pipeline_runs') THEN
        SELECT COUNT(*) INTO monthly_count
        FROM analysis_pipeline_runs
        WHERE user_id = check_user_quota.user_id
        AND created_at >= date_trunc('month', CURRENT_DATE);
    ELSE
        SELECT COUNT(*) INTO monthly_count
        FROM ad_analyses  
        WHERE user_id = check_user_quota.user_id
        AND created_at >= date_trunc('month', CURRENT_DATE);
    END IF;
    
    -- Build result
    result := jsonb_build_object(
        'can_analyze', monthly_count < quota_limit AND user_profile.subscription_active,
        'monthly_analyses', monthly_count,
        'quota_limit', quota_limit,
        'subscription_tier', user_profile.subscription_tier,
        'subscription_active', user_profile.subscription_active
    );
    
    IF monthly_count >= quota_limit THEN
        result := result || jsonb_build_object('reason', 'Monthly quota exceeded');
    END IF;
    
    IF NOT user_profile.subscription_active THEN
        result := result || jsonb_build_object('reason', 'Subscription inactive');
    END IF;
    
    RETURN result;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- ======================================================================================
-- 8. GRANT PERMISSIONS
-- ======================================================================================

-- Grant permissions on all tables to authenticated users
DO $$
DECLARE
    table_record RECORD;
BEGIN
    -- Grant permissions on existing tables
    FOR table_record IN 
        SELECT tablename FROM pg_tables 
        WHERE schemaname = 'public' 
        AND tablename IN ('user_profiles', 'ad_copy_projects', 'tool_analysis_results', 
                         'analysis_pipeline_runs', 'ad_analyses', 'competitor_benchmarks', 'ad_generations')
    LOOP
        EXECUTE 'GRANT ALL ON ' || table_record.tablename || ' TO authenticated';
    END LOOP;
    
    RAISE NOTICE '✅ Permissions granted to authenticated users';
END $$;

-- Grant usage on sequences
GRANT USAGE ON ALL SEQUENCES IN SCHEMA public TO authenticated;

-- ======================================================================================
-- MIGRATION COMPLETION
-- ======================================================================================

DO $$ 
DECLARE
    table_count INTEGER;
BEGIN
    -- Count tables we care about
    SELECT COUNT(*) INTO table_count 
    FROM information_schema.tables 
    WHERE table_schema = 'public' 
    AND table_name IN ('user_profiles', 'ad_copy_projects', 'tool_analysis_results', 
                       'analysis_pipeline_runs', 'ad_analyses', 'competitor_benchmarks', 'ad_generations');
                       
    RAISE NOTICE '';
    RAISE NOTICE '🎉 ===== MIGRATION COMPLETED SUCCESSFULLY! =====';
    RAISE NOTICE '';
    RAISE NOTICE '📊 Database Status:';
    RAISE NOTICE '   • Total relevant tables: %', table_count;
    RAISE NOTICE '   • RLS policies: ✅ Updated for all tables';
    RAISE NOTICE '   • Indexes: ✅ Created for performance';
    RAISE NOTICE '   • Functions: ✅ User quota checking available';
    RAISE NOTICE '   • Permissions: ✅ Granted to authenticated users';
    RAISE NOTICE '';
    RAISE NOTICE '🎯 Critical Fix Applied:';
    
    IF EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'ad_copy_projects') THEN
        RAISE NOTICE '   • ad_copy_projects table: ✅ NOW AVAILABLE';
        RAISE NOTICE '   • This should fix the 401 errors you were experiencing!';
    END IF;
    
    RAISE NOTICE '';
    RAISE NOTICE '📋 Next Steps:';
    RAISE NOTICE '   1. Restart your development server';
    RAISE NOTICE '   2. Try creating a new project';
    RAISE NOTICE '   3. Check browser console for any remaining errors';
    RAISE NOTICE '   4. Use window.debugAuthState() to verify authentication';
    RAISE NOTICE '';
    RAISE NOTICE '🚀 Your AdCopySurge app should now work without 401 errors!';
    RAISE NOTICE '';
END $$;
