-- AdCopySurge Database Schema Setup for Supabase
-- Run this script in your Supabase SQL Editor to set up the required tables

-- Enable necessary extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Check if tables exist and create them if they don't
DO $$
BEGIN
    -- Create users table if it doesn't exist
    IF NOT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'users') THEN
        CREATE TABLE users (
            id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
            supabase_user_id UUID UNIQUE REFERENCES auth.users(id) ON DELETE CASCADE,
            email VARCHAR(255) UNIQUE NOT NULL,
            full_name VARCHAR(255),
            subscription_tier VARCHAR(50) DEFAULT 'free',
            monthly_analyses INTEGER DEFAULT 0,
            total_analyses INTEGER DEFAULT 0,
            is_active BOOLEAN DEFAULT true,
            email_verified BOOLEAN DEFAULT false,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        );
        
        -- Create RLS policies for users table
        ALTER TABLE users ENABLE ROW LEVEL SECURITY;
        
        CREATE POLICY "Users can view own profile" ON users
            FOR SELECT USING (supabase_user_id = auth.uid());
            
        CREATE POLICY "Users can update own profile" ON users
            FOR UPDATE USING (supabase_user_id = auth.uid());
            
        RAISE NOTICE 'Created users table with RLS policies';
    ELSE
        RAISE NOTICE 'Users table already exists';
    END IF;

    -- Create ad_analyses table if it doesn't exist
    IF NOT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'ad_analyses') THEN
        CREATE TABLE ad_analyses (
            id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
            user_id UUID REFERENCES users(id) ON DELETE CASCADE,
            supabase_user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
            project_id UUID NULL,
            platform VARCHAR(50) NOT NULL DEFAULT 'facebook',
            industry VARCHAR(100),
            headline TEXT,
            body_text TEXT NOT NULL,
            cta TEXT,
            overall_score NUMERIC(5,2),
            clarity_score NUMERIC(5,2),
            persuasion_score NUMERIC(5,2),
            emotion_score NUMERIC(5,2),
            cta_strength NUMERIC(5,2),
            platform_fit_score NUMERIC(5,2),
            feedback TEXT,
            quick_wins JSONB,
            alternatives JSONB,
            analysis_metadata JSONB,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        );
        
        -- Create indexes for better performance
        CREATE INDEX idx_ad_analyses_user_id ON ad_analyses(user_id);
        CREATE INDEX idx_ad_analyses_supabase_user_id ON ad_analyses(supabase_user_id);
        CREATE INDEX idx_ad_analyses_platform ON ad_analyses(platform);
        CREATE INDEX idx_ad_analyses_created_at ON ad_analyses(created_at);
        CREATE INDEX idx_ad_analyses_overall_score ON ad_analyses(overall_score);
        
        -- Create RLS policies for ad_analyses table
        ALTER TABLE ad_analyses ENABLE ROW LEVEL SECURITY;
        
        CREATE POLICY "Users can view own analyses" ON ad_analyses
            FOR SELECT USING (supabase_user_id = auth.uid());
            
        CREATE POLICY "Users can create own analyses" ON ad_analyses
            FOR INSERT WITH CHECK (supabase_user_id = auth.uid());
            
        CREATE POLICY "Users can update own analyses" ON ad_analyses
            FOR UPDATE USING (supabase_user_id = auth.uid());
            
        CREATE POLICY "Users can delete own analyses" ON ad_analyses
            FOR DELETE USING (supabase_user_id = auth.uid());
            
        RAISE NOTICE 'Created ad_analyses table with indexes and RLS policies';
    ELSE
        RAISE NOTICE 'Ad_analyses table already exists';
    END IF;

    -- Create projects table if it doesn't exist (for future use)
    IF NOT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'projects') THEN
        CREATE TABLE projects (
            id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
            user_id UUID REFERENCES users(id) ON DELETE CASCADE,
            supabase_user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
            name VARCHAR(255) NOT NULL,
            description TEXT,
            platform VARCHAR(50),
            status VARCHAR(50) DEFAULT 'active',
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        );
        
        -- Create RLS policies for projects table
        ALTER TABLE projects ENABLE ROW LEVEL SECURITY;
        
        CREATE POLICY "Users can manage own projects" ON projects
            FOR ALL USING (supabase_user_id = auth.uid());
            
        RAISE NOTICE 'Created projects table with RLS policies';
    ELSE
        RAISE NOTICE 'Projects table already exists';
    END IF;


END $$;

-- Create function to automatically create user profile on signup
CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO public.users (supabase_user_id, email, full_name, email_verified)
    VALUES (
        new.id,
        new.email,
        COALESCE(new.raw_user_meta_data->>'full_name', new.raw_user_meta_data->>'name', split_part(new.email, '@', 1)),
        COALESCE((new.email_confirmed_at IS NOT NULL), false)
    );
    RETURN new;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Create trigger to automatically create user profile
DROP TRIGGER IF EXISTS on_auth_user_created ON auth.users;
CREATE TRIGGER on_auth_user_created
    AFTER INSERT ON auth.users
    FOR EACH ROW EXECUTE FUNCTION public.handle_new_user();

-- Create a function to get dashboard metrics (this will be called by your API)
CREATE OR REPLACE FUNCTION get_dashboard_metrics(
    p_user_id UUID,
    p_period_days INTEGER DEFAULT 30
)
RETURNS JSON AS $$
DECLARE
    current_period_start TIMESTAMP;
    current_period_end TIMESTAMP;
    previous_period_start TIMESTAMP;
    previous_period_end TIMESTAMP;
    current_metrics JSON;
    previous_metrics JSON;
    result JSON;
BEGIN
    -- Calculate date ranges
    current_period_end := NOW();
    current_period_start := current_period_end - (p_period_days || ' days')::INTERVAL;
    previous_period_start := current_period_start - (p_period_days || ' days')::INTERVAL;
    previous_period_end := current_period_start;
    
    -- Get current period metrics
    WITH current_stats AS (
        SELECT 
            COUNT(*) as ads_analyzed,
            COALESCE(AVG(CASE 
                WHEN overall_score IS NOT NULL AND overall_score > 50 
                THEN overall_score - 50 
                ELSE 0 
            END), 0) as avg_improvement,
            COALESCE(AVG(overall_score), 0) as avg_score,
            COALESCE(MAX(overall_score), 0) as top_performing
        FROM ad_analyses 
        WHERE supabase_user_id = p_user_id 
            AND created_at >= current_period_start 
            AND created_at <= current_period_end
            AND overall_score IS NOT NULL
    )
    SELECT json_build_object(
        'ads_analyzed', ads_analyzed,
        'avg_improvement', avg_improvement,
        'avg_score', avg_score,
        'top_performing', top_performing
    ) INTO current_metrics
    FROM current_stats;
    
    -- Get previous period metrics
    WITH previous_stats AS (
        SELECT 
            COUNT(*) as ads_analyzed,
            COALESCE(AVG(CASE 
                WHEN overall_score IS NOT NULL AND overall_score > 50 
                THEN overall_score - 50 
                ELSE 0 
            END), 0) as avg_improvement,
            COALESCE(AVG(overall_score), 0) as avg_score,
            COALESCE(MAX(overall_score), 0) as top_performing
        FROM ad_analyses 
        WHERE supabase_user_id = p_user_id 
            AND created_at >= previous_period_start 
            AND created_at <= previous_period_end
            AND overall_score IS NOT NULL
    )
    SELECT json_build_object(
        'ads_analyzed', ads_analyzed,
        'avg_improvement', avg_improvement,
        'avg_score', avg_score,
        'top_performing', top_performing
    ) INTO previous_metrics
    FROM previous_stats;
    
    -- Calculate changes and build final result
    SELECT json_build_object(
        'adsAnalyzed', (current_metrics->>'ads_analyzed')::INTEGER,
        'adsAnalyzedChange', CASE 
            WHEN (previous_metrics->>'ads_analyzed')::NUMERIC = 0 THEN
                CASE WHEN (current_metrics->>'ads_analyzed')::INTEGER > 0 THEN 100.0 ELSE 0.0 END
            ELSE
                ROUND((((current_metrics->>'ads_analyzed')::NUMERIC - (previous_metrics->>'ads_analyzed')::NUMERIC) / (previous_metrics->>'ads_analyzed')::NUMERIC) * 100, 1)
        END,
        'avgImprovement', ROUND((current_metrics->>'avg_improvement')::NUMERIC, 1),
        'avgImprovementChange', CASE 
            WHEN (previous_metrics->>'avg_improvement')::NUMERIC = 0 THEN
                CASE WHEN (current_metrics->>'avg_improvement')::NUMERIC > 0 THEN 100.0 ELSE 0.0 END
            ELSE
                ROUND((((current_metrics->>'avg_improvement')::NUMERIC - (previous_metrics->>'avg_improvement')::NUMERIC) / (previous_metrics->>'avg_improvement')::NUMERIC) * 100, 1)
        END,
        'avgScore', ROUND((current_metrics->>'avg_score')::NUMERIC, 0),
        'avgScoreChange', CASE 
            WHEN (previous_metrics->>'avg_score')::NUMERIC = 0 THEN
                CASE WHEN (current_metrics->>'avg_score')::NUMERIC > 0 THEN 100.0 ELSE 0.0 END
            ELSE
                ROUND((((current_metrics->>'avg_score')::NUMERIC - (previous_metrics->>'avg_score')::NUMERIC) / (previous_metrics->>'avg_score')::NUMERIC) * 100, 1)
        END,
        'topPerforming', (current_metrics->>'top_performing')::INTEGER,
        'topPerformingChange', CASE 
            WHEN (previous_metrics->>'top_performing')::NUMERIC = 0 THEN
                CASE WHEN (current_metrics->>'top_performing')::INTEGER > 0 THEN 100.0 ELSE 0.0 END
            ELSE
                ROUND((((current_metrics->>'top_performing')::NUMERIC - (previous_metrics->>'top_performing')::NUMERIC) / (previous_metrics->>'top_performing')::NUMERIC) * 100, 1)
        END,
        'periodStart', current_period_start,
        'periodEnd', current_period_end,
        'periodDays', p_period_days
    ) INTO result;
    
    RETURN result;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Create function to get summary metrics
CREATE OR REPLACE FUNCTION get_summary_metrics(p_user_id UUID)
RETURNS JSON AS $$
DECLARE
    result JSON;
BEGIN
    WITH user_stats AS (
        SELECT 
            COUNT(*) as total_analyses,
            COALESCE(AVG(overall_score), 0) as lifetime_avg_score,
            COALESCE(MAX(overall_score), 0) as best_score,
            MIN(created_at) as first_analysis_date,
            MAX(created_at) as last_analysis_date,
            COUNT(DISTINCT platform) as platforms_used,
            COUNT(DISTINCT project_id) as projects_count
        FROM ad_analyses 
        WHERE supabase_user_id = p_user_id 
            AND overall_score IS NOT NULL
    ),
    recent_stats AS (
        SELECT 
            COUNT(*) as analyses_last_30_days
        FROM ad_analyses 
        WHERE supabase_user_id = p_user_id 
            AND created_at >= NOW() - INTERVAL '30 days'
            AND overall_score IS NOT NULL
    )
    SELECT json_build_object(
        'totalAnalyses', COALESCE(us.total_analyses, 0),
        'lifetimeAvgScore', ROUND(COALESCE(us.lifetime_avg_score, 0), 1),
        'bestScore', COALESCE(us.best_score, 0),
        'analysesLast30Days', COALESCE(rs.analyses_last_30_days, 0),
        'platformsUsed', COALESCE(us.platforms_used, 0),
        'projectsCount', COALESCE(us.projects_count, 0),
        'firstAnalysisDate', us.first_analysis_date,
        'lastAnalysisDate', us.last_analysis_date,
        'isNewUser', COALESCE(us.total_analyses, 0) = 0
    ) INTO result
    FROM user_stats us
    CROSS JOIN recent_stats rs;
    
    RETURN result;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Test the setup by checking if everything was created
SELECT 
    'Setup completed successfully!' as message,
    (SELECT COUNT(*) FROM information_schema.tables WHERE table_name IN ('users', 'ad_analyses', 'projects')) as tables_created,
    (SELECT COUNT(*) FROM information_schema.routines WHERE routine_name IN ('get_dashboard_metrics', 'get_summary_metrics')) as functions_created;

-- Show current database structure
SELECT 
    table_name,
    column_name,
    data_type,
    is_nullable
FROM information_schema.columns 
WHERE table_name IN ('users', 'ad_analyses', 'projects')
ORDER BY table_name, ordinal_position;