-- Fix RLS Policies and Create Missing Tables for AdCopySurge
-- Run this in your Supabase SQL Editor

-- First, let's create the missing tables that were showing errors

-- 1. Create user_profiles table if it doesn't exist
CREATE TABLE IF NOT EXISTS user_profiles (
    id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    email TEXT NOT NULL,
    full_name TEXT,
    company TEXT,
    subscription_tier TEXT DEFAULT 'free' CHECK (subscription_tier IN ('free', 'basic', 'pro')),
    monthly_analyses INTEGER DEFAULT 0,
    subscription_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    PRIMARY KEY (id)
);

-- 2. Create legacy ad_analyses table (for compatibility with existing code)
CREATE TABLE IF NOT EXISTS ad_analyses (
    id UUID DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES user_profiles(id) ON DELETE CASCADE,
    headline TEXT NOT NULL,
    body_text TEXT NOT NULL,
    cta TEXT NOT NULL,
    platform TEXT NOT NULL,
    target_audience TEXT,
    industry TEXT,
    overall_score DECIMAL(5,2) DEFAULT 0,
    clarity_score DECIMAL(5,2) DEFAULT 0,
    persuasion_score DECIMAL(5,2) DEFAULT 0,
    emotion_score DECIMAL(5,2) DEFAULT 0,
    cta_strength_score DECIMAL(5,2) DEFAULT 0,
    platform_fit_score DECIMAL(5,2) DEFAULT 0,
    analysis_data JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    PRIMARY KEY (id)
);

-- 3. Create competitor_benchmarks table
CREATE TABLE IF NOT EXISTS competitor_benchmarks (
    id UUID DEFAULT gen_random_uuid(),
    analysis_id UUID NOT NULL REFERENCES ad_analyses(id) ON DELETE CASCADE,
    competitor_headline TEXT NOT NULL,
    competitor_body_text TEXT NOT NULL,
    competitor_cta TEXT NOT NULL,
    competitor_platform TEXT NOT NULL,
    source_url TEXT,
    competitor_overall_score DECIMAL(5,2) DEFAULT 0,
    competitor_clarity_score DECIMAL(5,2) DEFAULT 0,
    competitor_emotion_score DECIMAL(5,2) DEFAULT 0,
    competitor_cta_score DECIMAL(5,2) DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    PRIMARY KEY (id)
);

-- 4. Create ad_generations table
CREATE TABLE IF NOT EXISTS ad_generations (
    id UUID DEFAULT gen_random_uuid(),
    analysis_id UUID NOT NULL REFERENCES ad_analyses(id) ON DELETE CASCADE,
    variant_type TEXT NOT NULL,
    generated_headline TEXT NOT NULL,
    generated_body_text TEXT NOT NULL,
    generated_cta TEXT NOT NULL,
    improvement_reason TEXT,
    predicted_score DECIMAL(5,2),
    user_rating INTEGER CHECK (user_rating BETWEEN 1 AND 5),
    user_selected BOOLEAN DEFAULT false,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    PRIMARY KEY (id)
);

-- Now enable RLS on all tables
ALTER TABLE user_profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE ad_analyses ENABLE ROW LEVEL SECURITY;
ALTER TABLE competitor_benchmarks ENABLE ROW LEVEL SECURITY;
ALTER TABLE ad_generations ENABLE ROW LEVEL SECURITY;

-- Create/Update RLS Policies

-- User Profiles Policies
DROP POLICY IF EXISTS "Users can view own profile" ON user_profiles;
CREATE POLICY "Users can view own profile" ON user_profiles
    FOR SELECT USING (auth.uid() = id);

DROP POLICY IF EXISTS "Users can insert own profile" ON user_profiles;
CREATE POLICY "Users can insert own profile" ON user_profiles
    FOR INSERT WITH CHECK (auth.uid() = id);

DROP POLICY IF EXISTS "Users can update own profile" ON user_profiles;
CREATE POLICY "Users can update own profile" ON user_profiles
    FOR UPDATE USING (auth.uid() = id);

-- Ad Analyses Policies
DROP POLICY IF EXISTS "Users can view own analyses" ON ad_analyses;
CREATE POLICY "Users can view own analyses" ON ad_analyses
    FOR SELECT USING (auth.uid() = user_id);

DROP POLICY IF EXISTS "Users can insert own analyses" ON ad_analyses;
CREATE POLICY "Users can insert own analyses" ON ad_analyses
    FOR INSERT WITH CHECK (auth.uid() = user_id);

DROP POLICY IF EXISTS "Users can update own analyses" ON ad_analyses;
CREATE POLICY "Users can update own analyses" ON ad_analyses
    FOR UPDATE USING (auth.uid() = user_id);

DROP POLICY IF EXISTS "Users can delete own analyses" ON ad_analyses;
CREATE POLICY "Users can delete own analyses" ON ad_analyses
    FOR DELETE USING (auth.uid() = user_id);

-- Competitor Benchmarks Policies
DROP POLICY IF EXISTS "Users can view benchmarks for own analyses" ON competitor_benchmarks;
CREATE POLICY "Users can view benchmarks for own analyses" ON competitor_benchmarks
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM ad_analyses 
            WHERE id = competitor_benchmarks.analysis_id 
            AND user_id = auth.uid()
        )
    );

DROP POLICY IF EXISTS "Users can insert benchmarks for own analyses" ON competitor_benchmarks;
CREATE POLICY "Users can insert benchmarks for own analyses" ON competitor_benchmarks
    FOR INSERT WITH CHECK (
        EXISTS (
            SELECT 1 FROM ad_analyses 
            WHERE id = competitor_benchmarks.analysis_id 
            AND user_id = auth.uid()
        )
    );

-- Ad Generations Policies
DROP POLICY IF EXISTS "Users can view generations for own analyses" ON ad_generations;
CREATE POLICY "Users can view generations for own analyses" ON ad_generations
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM ad_analyses 
            WHERE id = ad_generations.analysis_id 
            AND user_id = auth.uid()
        )
    );

DROP POLICY IF EXISTS "Users can insert generations for own analyses" ON ad_generations;
CREATE POLICY "Users can insert generations for own analyses" ON ad_generations
    FOR INSERT WITH CHECK (
        EXISTS (
            SELECT 1 FROM ad_analyses 
            WHERE id = ad_generations.analysis_id 
            AND user_id = auth.uid()
        )
    );

DROP POLICY IF EXISTS "Users can update generations for own analyses" ON ad_generations;
CREATE POLICY "Users can update generations for own analyses" ON ad_generations
    FOR UPDATE USING (
        EXISTS (
            SELECT 1 FROM ad_analyses 
            WHERE id = ad_generations.analysis_id 
            AND user_id = auth.uid()
        )
    );

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_user_profiles_email ON user_profiles(email);
CREATE INDEX IF NOT EXISTS idx_ad_analyses_user_id ON ad_analyses(user_id);
CREATE INDEX IF NOT EXISTS idx_ad_analyses_created_at ON ad_analyses(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_competitor_benchmarks_analysis_id ON competitor_benchmarks(analysis_id);
CREATE INDEX IF NOT EXISTS idx_ad_generations_analysis_id ON ad_generations(analysis_id);

-- Insert a function to automatically create user profiles when users sign up
CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO public.user_profiles (id, email, full_name, created_at)
    VALUES (
        NEW.id,
        NEW.email,
        COALESCE(NEW.raw_user_meta_data->>'full_name', NEW.email),
        NOW()
    );
    RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Create trigger to automatically create user profile
DROP TRIGGER IF EXISTS on_auth_user_created ON auth.users;
CREATE TRIGGER on_auth_user_created
    AFTER INSERT ON auth.users
    FOR EACH ROW EXECUTE FUNCTION public.handle_new_user();

-- Create a function to check user quota (used by the app)
CREATE OR REPLACE FUNCTION public.check_user_quota(user_uuid UUID)
RETURNS JSON AS $$
DECLARE
    user_profile RECORD;
    monthly_count INTEGER;
    max_analyses INTEGER;
BEGIN
    -- Get user profile
    SELECT * INTO user_profile FROM user_profiles WHERE id = user_uuid;
    
    IF NOT FOUND THEN
        RETURN json_build_object('canAnalyze', false, 'remaining', 0, 'reason', 'Profile not found');
    END IF;
    
    -- Set limits based on subscription tier
    CASE user_profile.subscription_tier
        WHEN 'free' THEN max_analyses := 3;
        WHEN 'basic' THEN max_analyses := 50;
        WHEN 'pro' THEN max_analyses := 500;
        ELSE max_analyses := 3;
    END CASE;
    
    -- Count analyses this month
    SELECT COUNT(*) INTO monthly_count 
    FROM ad_analyses 
    WHERE user_id = user_uuid 
    AND created_at >= date_trunc('month', CURRENT_DATE);
    
    RETURN json_build_object(
        'canAnalyze', monthly_count < max_analyses,
        'remaining', GREATEST(0, max_analyses - monthly_count),
        'used', monthly_count,
        'limit', max_analyses,
        'tier', user_profile.subscription_tier
    );
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

COMMENT ON TABLE user_profiles IS 'User profile information and subscription details';
COMMENT ON TABLE ad_analyses IS 'Ad copy analysis results and scores';
COMMENT ON TABLE competitor_benchmarks IS 'Competitor ad copy benchmarks for comparison';
COMMENT ON TABLE ad_generations IS 'AI-generated ad copy alternatives and improvements';

-- Grant necessary permissions
GRANT USAGE ON SCHEMA public TO postgres, anon, authenticated;
GRANT ALL ON ALL TABLES IN SCHEMA public TO postgres;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO authenticated;
GRANT USAGE ON ALL SEQUENCES IN SCHEMA public TO authenticated;

COMMIT;
