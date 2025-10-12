-- AdCopySurge Database Schema for Supabase
-- Run this in your Supabase SQL Editor

-- Enable RLS (Row Level Security)

-- Create custom types
CREATE TYPE subscription_tier AS ENUM ('free', 'basic', 'pro');

-- User profiles table (extends Supabase auth.users)
CREATE TABLE IF NOT EXISTS user_profiles (
    id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    email TEXT NOT NULL,
    full_name TEXT NOT NULL,
    company TEXT,
    subscription_tier subscription_tier DEFAULT 'free',
    monthly_analyses INTEGER DEFAULT 0,
    subscription_active BOOLEAN DEFAULT true,
    stripe_customer_id TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    PRIMARY KEY (id)
);

-- Ad analyses table
CREATE TABLE IF NOT EXISTS ad_analyses (
    id UUID DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES user_profiles(id) ON DELETE CASCADE,
    headline TEXT NOT NULL,
    body_text TEXT NOT NULL,
    cta TEXT NOT NULL,
    platform TEXT NOT NULL,
    target_audience TEXT,
    industry TEXT,
    overall_score DECIMAL(5,2) NOT NULL,
    clarity_score DECIMAL(5,2) NOT NULL,
    persuasion_score DECIMAL(5,2) NOT NULL,
    emotion_score DECIMAL(5,2) NOT NULL,
    cta_strength_score DECIMAL(5,2) NOT NULL,
    platform_fit_score DECIMAL(5,2) NOT NULL,
    analysis_data JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    PRIMARY KEY (id)
);

-- Competitor benchmarks table
CREATE TABLE IF NOT EXISTS competitor_benchmarks (
    id SERIAL PRIMARY KEY,
    analysis_id UUID NOT NULL REFERENCES ad_analyses(id) ON DELETE CASCADE,
    competitor_headline TEXT NOT NULL,
    competitor_body_text TEXT NOT NULL,
    competitor_cta TEXT NOT NULL,
    competitor_platform TEXT NOT NULL,
    source_url TEXT,
    competitor_overall_score DECIMAL(5,2) NOT NULL,
    competitor_clarity_score DECIMAL(5,2) NOT NULL,
    competitor_emotion_score DECIMAL(5,2) NOT NULL,
    competitor_cta_score DECIMAL(5,2) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Ad generation alternatives table
CREATE TABLE IF NOT EXISTS ad_generations (
    id SERIAL PRIMARY KEY,
    analysis_id UUID NOT NULL REFERENCES ad_analyses(id) ON DELETE CASCADE,
    variant_type TEXT NOT NULL,
    generated_headline TEXT NOT NULL,
    generated_body_text TEXT NOT NULL,
    generated_cta TEXT NOT NULL,
    improvement_reason TEXT,
    predicted_score DECIMAL(5,2),
    user_rating INTEGER CHECK (user_rating >= 1 AND user_rating <= 5),
    user_selected BOOLEAN DEFAULT false,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_ad_analyses_user_id ON ad_analyses(user_id);
CREATE INDEX IF NOT EXISTS idx_ad_analyses_created_at ON ad_analyses(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_ad_analyses_platform ON ad_analyses(platform);
CREATE INDEX IF NOT EXISTS idx_competitor_benchmarks_analysis_id ON competitor_benchmarks(analysis_id);
CREATE INDEX IF NOT EXISTS idx_ad_generations_analysis_id ON ad_generations(analysis_id);
CREATE INDEX IF NOT EXISTS idx_user_profiles_subscription_tier ON user_profiles(subscription_tier);

-- Enable Row Level Security (RLS)
ALTER TABLE user_profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE ad_analyses ENABLE ROW LEVEL SECURITY;
ALTER TABLE competitor_benchmarks ENABLE ROW LEVEL SECURITY;
ALTER TABLE ad_generations ENABLE ROW LEVEL SECURITY;

-- RLS Policies

-- User profiles: Users can only see and modify their own profile
CREATE POLICY "Users can view own profile" ON user_profiles
    FOR SELECT USING (auth.uid() = id);

CREATE POLICY "Users can update own profile" ON user_profiles
    FOR UPDATE USING (auth.uid() = id);

CREATE POLICY "Users can insert own profile" ON user_profiles
    FOR INSERT WITH CHECK (auth.uid() = id);

-- Ad analyses: Users can only access their own analyses
CREATE POLICY "Users can view own analyses" ON ad_analyses
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own analyses" ON ad_analyses
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own analyses" ON ad_analyses
    FOR UPDATE USING (auth.uid() = user_id);

CREATE POLICY "Users can delete own analyses" ON ad_analyses
    FOR DELETE USING (auth.uid() = user_id);

-- Competitor benchmarks: Users can access benchmarks for their analyses
CREATE POLICY "Users can view benchmarks for own analyses" ON competitor_benchmarks
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM ad_analyses 
            WHERE ad_analyses.id = competitor_benchmarks.analysis_id 
            AND ad_analyses.user_id = auth.uid()
        )
    );

CREATE POLICY "Users can insert benchmarks for own analyses" ON competitor_benchmarks
    FOR INSERT WITH CHECK (
        EXISTS (
            SELECT 1 FROM ad_analyses 
            WHERE ad_analyses.id = competitor_benchmarks.analysis_id 
            AND ad_analyses.user_id = auth.uid()
        )
    );

-- Ad generations: Users can access generations for their analyses
CREATE POLICY "Users can view generations for own analyses" ON ad_generations
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM ad_analyses 
            WHERE ad_analyses.id = ad_generations.analysis_id 
            AND ad_analyses.user_id = auth.uid()
        )
    );

CREATE POLICY "Users can insert generations for own analyses" ON ad_generations
    FOR INSERT WITH CHECK (
        EXISTS (
            SELECT 1 FROM ad_analyses 
            WHERE ad_analyses.id = ad_generations.analysis_id 
            AND ad_analyses.user_id = auth.uid()
        )
    );

CREATE POLICY "Users can update generations for own analyses" ON ad_generations
    FOR UPDATE USING (
        EXISTS (
            SELECT 1 FROM ad_analyses 
            WHERE ad_analyses.id = ad_generations.analysis_id 
            AND ad_analyses.user_id = auth.uid()
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
CREATE TRIGGER on_new_analysis
    AFTER INSERT ON ad_analyses
    FOR EACH ROW EXECUTE FUNCTION increment_user_analysis_count();

-- Function to reset monthly counts (run this monthly via cron or Edge Function)
CREATE OR REPLACE FUNCTION reset_monthly_analysis_counts()
RETURNS void AS $$
BEGIN
    UPDATE user_profiles SET monthly_analyses = 0;
END;
$$ LANGUAGE plpgsql;

-- Create views for analytics (optional)
CREATE OR REPLACE VIEW user_analytics AS
SELECT 
    up.id,
    up.full_name,
    up.subscription_tier,
    up.monthly_analyses,
    COUNT(aa.id) as total_analyses,
    AVG(aa.overall_score) as avg_score,
    MAX(aa.created_at) as last_analysis
FROM user_profiles up
LEFT JOIN ad_analyses aa ON up.id = aa.user_id
GROUP BY up.id, up.full_name, up.subscription_tier, up.monthly_analyses;

-- Sample data (optional - for testing)
-- Don't run this in production
/*
INSERT INTO user_profiles (id, email, full_name, company, subscription_tier) VALUES
('550e8400-e29b-41d4-a716-446655440000', 'demo@example.com', 'Demo User', 'Demo Company', 'free');

INSERT INTO ad_analyses (id, user_id, headline, body_text, cta, platform, overall_score, clarity_score, persuasion_score, emotion_score, cta_strength_score, platform_fit_score) VALUES
('550e8400-e29b-41d4-a716-446655440001', '550e8400-e29b-41d4-a716-446655440000', 'Amazing Product Launch!', 'Discover the future of productivity with our revolutionary new app.', 'Get Started Now', 'facebook', 85.5, 88.0, 83.0, 87.0, 85.0, 82.5);
*/
