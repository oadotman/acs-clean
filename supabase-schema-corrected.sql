-- AdCopySurge Database Schema for Supabase (Corrected Version)
-- Run this in your Supabase SQL Editor
-- This schema fixes issues with the previous version and adds missing fields

-- Enable necessary extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create custom types
CREATE TYPE subscription_tier AS ENUM ('free', 'basic', 'pro');

-- Drop existing tables if they exist (for clean migration)
DROP TABLE IF EXISTS ad_generations CASCADE;
DROP TABLE IF EXISTS competitor_benchmarks CASCADE;
DROP TABLE IF EXISTS ad_analyses CASCADE;
DROP TABLE IF EXISTS user_profiles CASCADE;
DROP TYPE IF EXISTS subscription_tier CASCADE;

-- Recreate the enum type
CREATE TYPE subscription_tier AS ENUM ('free', 'basic', 'pro');

-- User profiles table (extends Supabase auth.users)
-- This maps to your SQLAlchemy User model
CREATE TABLE user_profiles (
    id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    email TEXT NOT NULL UNIQUE,
    hashed_password TEXT, -- For compatibility, but auth handled by Supabase
    full_name TEXT NOT NULL,
    company TEXT,
    
    -- Subscription info
    subscription_tier subscription_tier DEFAULT 'free',
    monthly_analyses INTEGER DEFAULT 0,
    subscription_active BOOLEAN DEFAULT true,
    
    -- Legacy Stripe fields (will be removed after migration)
    stripe_customer_id TEXT,
    
    -- Paddle billing fields (missing from original schema)
    paddle_subscription_id TEXT,
    paddle_plan_id TEXT,
    paddle_checkout_id TEXT,
    
    -- Account status
    is_active BOOLEAN DEFAULT true,
    email_verified BOOLEAN DEFAULT false,
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    PRIMARY KEY (id)
);

-- Ad analyses table
-- This maps to your SQLAlchemy AdAnalysis model
CREATE TABLE ad_analyses (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES user_profiles(id) ON DELETE CASCADE,
    
    -- Ad content
    headline TEXT NOT NULL,
    body_text TEXT NOT NULL,
    cta TEXT NOT NULL,
    platform TEXT NOT NULL,
    target_audience TEXT,
    industry TEXT,
    
    -- Scores (using DECIMAL for precision)
    overall_score DECIMAL(5,2) NOT NULL CHECK (overall_score >= 0 AND overall_score <= 100),
    clarity_score DECIMAL(5,2) NOT NULL CHECK (clarity_score >= 0 AND clarity_score <= 100),
    persuasion_score DECIMAL(5,2) NOT NULL CHECK (persuasion_score >= 0 AND persuasion_score <= 100),
    emotion_score DECIMAL(5,2) NOT NULL CHECK (emotion_score >= 0 AND emotion_score <= 100),
    cta_strength_score DECIMAL(5,2) NOT NULL CHECK (cta_strength_score >= 0 AND cta_strength_score <= 100),
    platform_fit_score DECIMAL(5,2) NOT NULL CHECK (platform_fit_score >= 0 AND platform_fit_score <= 100),
    
    -- Detailed analysis data (stored as JSON)
    analysis_data JSONB,
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Competitor benchmarks table
-- This maps to your SQLAlchemy CompetitorBenchmark model
CREATE TABLE competitor_benchmarks (
    id SERIAL PRIMARY KEY,
    analysis_id UUID NOT NULL REFERENCES ad_analyses(id) ON DELETE CASCADE,
    
    -- Competitor ad content
    competitor_headline TEXT NOT NULL,
    competitor_body_text TEXT NOT NULL,
    competitor_cta TEXT NOT NULL,
    competitor_platform TEXT NOT NULL,
    source_url TEXT,
    
    -- Competitor scores
    competitor_overall_score DECIMAL(5,2) NOT NULL CHECK (competitor_overall_score >= 0 AND competitor_overall_score <= 100),
    competitor_clarity_score DECIMAL(5,2) NOT NULL CHECK (competitor_clarity_score >= 0 AND competitor_clarity_score <= 100),
    competitor_emotion_score DECIMAL(5,2) NOT NULL CHECK (competitor_emotion_score >= 0 AND competitor_emotion_score <= 100),
    competitor_cta_score DECIMAL(5,2) NOT NULL CHECK (competitor_cta_score >= 0 AND competitor_cta_score <= 100),
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Ad generation alternatives table
-- This maps to your SQLAlchemy AdGeneration model
CREATE TABLE ad_generations (
    id SERIAL PRIMARY KEY,
    analysis_id UUID NOT NULL REFERENCES ad_analyses(id) ON DELETE CASCADE,
    
    -- Generated content
    variant_type TEXT NOT NULL, -- persuasive, emotional, stats_heavy, etc.
    generated_headline TEXT NOT NULL,
    generated_body_text TEXT NOT NULL,
    generated_cta TEXT NOT NULL,
    improvement_reason TEXT,
    
    -- Performance prediction
    predicted_score DECIMAL(5,2) CHECK (predicted_score >= 0 AND predicted_score <= 100),
    
    -- User feedback
    user_rating INTEGER CHECK (user_rating >= 1 AND user_rating <= 5),
    user_selected BOOLEAN DEFAULT false,
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for better performance
CREATE INDEX idx_user_profiles_email ON user_profiles(email);
CREATE INDEX idx_user_profiles_subscription_tier ON user_profiles(subscription_tier);
CREATE INDEX idx_user_profiles_paddle_subscription_id ON user_profiles(paddle_subscription_id);

CREATE INDEX idx_ad_analyses_user_id ON ad_analyses(user_id);
CREATE INDEX idx_ad_analyses_created_at ON ad_analyses(created_at DESC);
CREATE INDEX idx_ad_analyses_platform ON ad_analyses(platform);
CREATE INDEX idx_ad_analyses_overall_score ON ad_analyses(overall_score);

-- GIN index for JSONB analysis_data for efficient queries
CREATE INDEX idx_ad_analyses_analysis_data_gin ON ad_analyses USING GIN (analysis_data);

CREATE INDEX idx_competitor_benchmarks_analysis_id ON competitor_benchmarks(analysis_id);
CREATE INDEX idx_ad_generations_analysis_id ON ad_generations(analysis_id);
CREATE INDEX idx_ad_generations_variant_type ON ad_generations(variant_type);

-- Function to automatically update updated_at timestamps
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Triggers to automatically update updated_at
CREATE TRIGGER update_user_profiles_updated_at
    BEFORE UPDATE ON user_profiles
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_ad_analyses_updated_at
    BEFORE UPDATE ON ad_analyses
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Enable Row Level Security (RLS)
ALTER TABLE user_profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE ad_analyses ENABLE ROW LEVEL SECURITY;
ALTER TABLE competitor_benchmarks ENABLE ROW LEVEL SECURITY;
ALTER TABLE ad_generations ENABLE ROW LEVEL SECURITY;

-- Helper functions for RLS
CREATE OR REPLACE FUNCTION is_authenticated()
RETURNS BOOLEAN AS $$
BEGIN
    RETURN auth.uid() IS NOT NULL;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

CREATE OR REPLACE FUNCTION is_owner(user_id UUID)
RETURNS BOOLEAN AS $$
BEGIN
    RETURN auth.uid() = user_id;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- RLS Policies

-- User profiles: Users can only see and modify their own profile
CREATE POLICY "Users can view own profile" ON user_profiles
    FOR SELECT USING (is_owner(id));

CREATE POLICY "Users can update own profile" ON user_profiles
    FOR UPDATE USING (is_owner(id));

CREATE POLICY "Users can insert own profile" ON user_profiles
    FOR INSERT WITH CHECK (is_owner(id));

-- Ad analyses: Users can only access their own analyses
CREATE POLICY "Users can view own analyses" ON ad_analyses
    FOR SELECT USING (is_owner(user_id));

CREATE POLICY "Users can insert own analyses" ON ad_analyses
    FOR INSERT WITH CHECK (is_owner(user_id) AND is_authenticated());

CREATE POLICY "Users can update own analyses" ON ad_analyses
    FOR UPDATE USING (is_owner(user_id));

CREATE POLICY "Users can delete own analyses" ON ad_analyses
    FOR DELETE USING (is_owner(user_id));

-- Competitor benchmarks: Users can access benchmarks for their analyses
CREATE POLICY "Users can view benchmarks for own analyses" ON competitor_benchmarks
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM ad_analyses 
            WHERE ad_analyses.id = competitor_benchmarks.analysis_id 
            AND is_owner(ad_analyses.user_id)
        )
    );

CREATE POLICY "Users can insert benchmarks for own analyses" ON competitor_benchmarks
    FOR INSERT WITH CHECK (
        EXISTS (
            SELECT 1 FROM ad_analyses 
            WHERE ad_analyses.id = competitor_benchmarks.analysis_id 
            AND is_owner(ad_analyses.user_id)
        )
    );

-- Ad generations: Users can access generations for their analyses
CREATE POLICY "Users can view generations for own analyses" ON ad_generations
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM ad_analyses 
            WHERE ad_analyses.id = ad_generations.analysis_id 
            AND is_owner(ad_analyses.user_id)
        )
    );

CREATE POLICY "Users can insert generations for own analyses" ON ad_generations
    FOR INSERT WITH CHECK (
        EXISTS (
            SELECT 1 FROM ad_analyses 
            WHERE ad_analyses.id = ad_generations.analysis_id 
            AND is_owner(ad_analyses.user_id)
        )
    );

CREATE POLICY "Users can update generations for own analyses" ON ad_generations
    FOR UPDATE USING (
        EXISTS (
            SELECT 1 FROM ad_analyses 
            WHERE ad_analyses.id = ad_generations.analysis_id 
            AND is_owner(ad_analyses.user_id)
        )
    );

-- Function to automatically create user profile when user signs up
CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO public.user_profiles (id, email, full_name)
    VALUES (
        NEW.id,
        NEW.email,
        COALESCE(NEW.raw_user_meta_data->>'full_name', 'User')
    );
    RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Trigger to create profile on user signup
DROP TRIGGER IF EXISTS on_auth_user_created ON auth.users;
CREATE TRIGGER on_auth_user_created
    AFTER INSERT ON auth.users
    FOR EACH ROW EXECUTE FUNCTION public.handle_new_user();

-- Function to update monthly analysis count
CREATE OR REPLACE FUNCTION increment_user_analysis_count()
RETURNS TRIGGER AS $$
BEGIN
    UPDATE user_profiles 
    SET monthly_analyses = monthly_analyses + 1,
        updated_at = NOW()
    WHERE id = NEW.user_id;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger to increment analysis count when new analysis is created
DROP TRIGGER IF EXISTS on_new_analysis ON ad_analyses;
CREATE TRIGGER on_new_analysis
    AFTER INSERT ON ad_analyses
    FOR EACH ROW EXECUTE FUNCTION increment_user_analysis_count();

-- Function to reset monthly counts (run this monthly via cron or Edge Function)
CREATE OR REPLACE FUNCTION reset_monthly_analysis_counts()
RETURNS void AS $$
BEGIN
    UPDATE user_profiles SET monthly_analyses = 0, updated_at = NOW();
END;
$$ LANGUAGE plpgsql;

-- Function to check user subscription limits
CREATE OR REPLACE FUNCTION check_user_analysis_limit(p_user_id UUID)
RETURNS BOOLEAN AS $$
DECLARE
    user_tier subscription_tier;
    current_count INTEGER;
    max_analyses INTEGER;
BEGIN
    -- Get user's current tier and monthly count
    SELECT subscription_tier, monthly_analyses 
    INTO user_tier, current_count
    FROM user_profiles 
    WHERE id = p_user_id;
    
    -- Determine max analyses based on tier
    CASE user_tier
        WHEN 'free' THEN max_analyses := 5;
        WHEN 'basic' THEN max_analyses := 100;
        WHEN 'pro' THEN max_analyses := 500;
        ELSE max_analyses := 0;
    END CASE;
    
    -- Return true if under limit
    RETURN current_count < max_analyses;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Create views for analytics and reporting
CREATE OR REPLACE VIEW user_analytics AS
SELECT 
    up.id,
    up.full_name,
    up.email,
    up.company,
    up.subscription_tier,
    up.monthly_analyses,
    up.subscription_active,
    COUNT(aa.id) as total_analyses,
    AVG(aa.overall_score) as avg_score,
    MAX(aa.created_at) as last_analysis,
    up.created_at as user_created_at
FROM user_profiles up
LEFT JOIN ad_analyses aa ON up.id = aa.user_id
GROUP BY up.id, up.full_name, up.email, up.company, up.subscription_tier, 
         up.monthly_analyses, up.subscription_active, up.created_at;

-- Create view for platform performance analytics
CREATE OR REPLACE VIEW platform_analytics AS
SELECT 
    platform,
    COUNT(*) as total_analyses,
    AVG(overall_score) as avg_overall_score,
    AVG(clarity_score) as avg_clarity_score,
    AVG(persuasion_score) as avg_persuasion_score,
    AVG(emotion_score) as avg_emotion_score,
    AVG(cta_strength_score) as avg_cta_score,
    AVG(platform_fit_score) as avg_platform_fit_score
FROM ad_analyses
GROUP BY platform
ORDER BY total_analyses DESC;

-- Comments for documentation
COMMENT ON TABLE user_profiles IS 'User account information and subscription details';
COMMENT ON TABLE ad_analyses IS 'Ad copy analysis results with AI-generated scores';
COMMENT ON TABLE competitor_benchmarks IS 'Competitor ad comparisons for benchmarking';
COMMENT ON TABLE ad_generations IS 'AI-generated alternative ad copy variations';

COMMENT ON COLUMN user_profiles.paddle_subscription_id IS 'Paddle billing subscription ID';
COMMENT ON COLUMN user_profiles.paddle_plan_id IS 'Paddle billing plan ID';
COMMENT ON COLUMN user_profiles.monthly_analyses IS 'Current month analysis count for usage tracking';
COMMENT ON COLUMN ad_analyses.analysis_data IS 'Detailed JSON analysis results from AI engines';

-- Sample data for testing (commented out for production)
/*
-- Test user profile
INSERT INTO user_profiles (id, email, full_name, company, subscription_tier) VALUES
('550e8400-e29b-41d4-a716-446655440000', 'demo@adcopysurge.com', 'Demo User', 'Demo Company', 'pro');

-- Test ad analysis
INSERT INTO ad_analyses (id, user_id, headline, body_text, cta, platform, overall_score, clarity_score, persuasion_score, emotion_score, cta_strength_score, platform_fit_score, analysis_data) VALUES
('550e8400-e29b-41d4-a716-446655440001', 
 '550e8400-e29b-41d4-a716-446655440000', 
 'Revolutionary AI-Powered Ad Analysis', 
 'Transform your marketing campaigns with our cutting-edge AI analysis platform. Get detailed insights, competitor benchmarks, and AI-generated alternatives that convert better.', 
 'Start Free Trial', 
 'facebook', 
 92.5, 95.0, 89.0, 94.0, 91.0, 93.5,
 '{"readability_score": 78, "sentiment": "positive", "keywords": ["AI", "analysis", "marketing"], "suggestions": ["Add urgency", "Include social proof"]}'::jsonb);

-- Test competitor benchmark
INSERT INTO competitor_benchmarks (analysis_id, competitor_headline, competitor_body_text, competitor_cta, competitor_platform, competitor_overall_score, competitor_clarity_score, competitor_emotion_score, competitor_cta_score) VALUES
('550e8400-e29b-41d4-a716-446655440001', 
 'Basic Ad Copy Tool', 
 'Simple ad copy generation for your business needs.', 
 'Try Now', 
 'facebook', 
 68.5, 72.0, 65.0, 69.0);

-- Test ad generation
INSERT INTO ad_generations (analysis_id, variant_type, generated_headline, generated_body_text, generated_cta, improvement_reason, predicted_score) VALUES
('550e8400-e29b-41d4-a716-446655440001', 
 'emotional', 
 'Don\'t Let Your Competitors Win With Better Ads', 
 'While your competitors are getting ahead with AI-powered ad analysis, you\'re still guessing. Join thousands of marketers who\'ve transformed their campaigns with our advanced AI platform.', 
 'Beat Your Competition Today', 
 'Uses emotional triggers (fear of missing out) and social proof to increase conversion potential', 
 94.2);
*/
