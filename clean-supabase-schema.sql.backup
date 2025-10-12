-- AdCopySurge - Clean Supabase Schema
-- Copy and paste this entire script into your Supabase SQL Editor

-- Enable necessary extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create custom types
CREATE TYPE subscription_tier AS ENUM ('free', 'basic', 'pro');
CREATE TYPE project_status AS ENUM ('draft', 'analyzing', 'completed', 'archived');
CREATE TYPE analysis_status AS ENUM ('pending', 'running', 'completed', 'failed');

-- ============================================================================
-- USER PROFILES TABLE (extends Supabase auth.users)
-- ============================================================================
CREATE TABLE IF NOT EXISTS user_profiles (
    id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    email TEXT NOT NULL,
    full_name TEXT NOT NULL,
    company TEXT,
    
    -- Subscription management
    subscription_tier subscription_tier DEFAULT 'free',
    monthly_analyses INTEGER DEFAULT 0,
    subscription_active BOOLEAN DEFAULT true,
    
    -- Billing integration (Stripe/Paddle)
    stripe_customer_id TEXT,
    paddle_subscription_id TEXT,
    
    -- Account status
    is_active BOOLEAN DEFAULT true,
    email_verified BOOLEAN DEFAULT false,
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    PRIMARY KEY (id)
);

-- ============================================================================
-- AD COPY PROJECTS TABLE (main projects users work with)
-- ============================================================================
CREATE TABLE IF NOT EXISTS ad_copy_projects (
    id UUID DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES user_profiles(id) ON DELETE CASCADE,
    
    -- Project details
    project_name TEXT NOT NULL DEFAULT 'Untitled Project',
    description TEXT,
    status project_status DEFAULT 'draft',
    
    -- Ad copy content (the core data)
    headline TEXT NOT NULL,
    body_text TEXT NOT NULL,
    cta TEXT NOT NULL,
    platform TEXT NOT NULL, -- Facebook, Google, LinkedIn, TikTok, etc.
    industry TEXT,
    target_audience TEXT,
    
    -- Project metadata
    tags TEXT[], -- For organization and search
    
    -- Analysis tracking
    last_analyzed_at TIMESTAMP WITH TIME ZONE,
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    PRIMARY KEY (id)
);

-- ============================================================================
-- AD ANALYSES TABLE (stores AI analysis results)
-- ============================================================================
CREATE TABLE IF NOT EXISTS ad_analyses (
    id UUID DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES user_profiles(id) ON DELETE CASCADE,
    project_id UUID REFERENCES ad_copy_projects(id) ON DELETE CASCADE,
    
    -- Ad content analyzed (snapshot at time of analysis)
    headline TEXT NOT NULL,
    body_text TEXT NOT NULL,
    cta TEXT NOT NULL,
    platform TEXT NOT NULL,
    target_audience TEXT,
    industry TEXT,
    
    -- Analysis scores (0-100)
    overall_score DECIMAL(5,2) NOT NULL DEFAULT 0,
    clarity_score DECIMAL(5,2) NOT NULL DEFAULT 0,
    persuasion_score DECIMAL(5,2) NOT NULL DEFAULT 0,
    emotion_score DECIMAL(5,2) NOT NULL DEFAULT 0,
    cta_strength_score DECIMAL(5,2) NOT NULL DEFAULT 0,
    platform_fit_score DECIMAL(5,2) NOT NULL DEFAULT 0,
    
    -- Detailed analysis data (JSON)
    analysis_data JSONB DEFAULT '{}',
    feedback TEXT, -- Human-readable feedback
    
    -- Status
    status analysis_status DEFAULT 'pending',
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    PRIMARY KEY (id)
);

-- ============================================================================
-- COMPETITOR BENCHMARKS TABLE (competitor ad comparisons)
-- ============================================================================
CREATE TABLE IF NOT EXISTS competitor_benchmarks (
    id UUID DEFAULT gen_random_uuid(),
    analysis_id UUID NOT NULL REFERENCES ad_analyses(id) ON DELETE CASCADE,
    
    -- Competitor ad content
    competitor_headline TEXT NOT NULL,
    competitor_body_text TEXT NOT NULL,
    competitor_cta TEXT NOT NULL,
    competitor_platform TEXT NOT NULL,
    source_url TEXT,
    
    -- Competitor scores
    competitor_overall_score DECIMAL(5,2) NOT NULL,
    competitor_clarity_score DECIMAL(5,2) NOT NULL,
    competitor_emotion_score DECIMAL(5,2) NOT NULL,
    competitor_cta_score DECIMAL(5,2) NOT NULL,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    PRIMARY KEY (id)
);

-- ============================================================================
-- AD GENERATIONS TABLE (AI-generated alternatives)
-- ============================================================================
CREATE TABLE IF NOT EXISTS ad_generations (
    id UUID DEFAULT gen_random_uuid(),
    analysis_id UUID NOT NULL REFERENCES ad_analyses(id) ON DELETE CASCADE,
    
    -- Generated alternative
    variant_type TEXT NOT NULL, -- 'persuasive', 'emotional', 'stats_heavy', etc.
    generated_headline TEXT NOT NULL,
    generated_body_text TEXT NOT NULL,
    generated_cta TEXT NOT NULL,
    improvement_reason TEXT,
    
    -- Performance prediction
    predicted_score DECIMAL(5,2),
    
    -- User feedback
    user_rating INTEGER CHECK (user_rating >= 1 AND user_rating <= 5),
    user_selected BOOLEAN DEFAULT false,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    PRIMARY KEY (id)
);

-- ============================================================================
-- INDEXES FOR PERFORMANCE
-- ============================================================================
-- User profiles
CREATE INDEX IF NOT EXISTS idx_user_profiles_email ON user_profiles(email);
CREATE INDEX IF NOT EXISTS idx_user_profiles_subscription ON user_profiles(subscription_tier);

-- Projects  
CREATE INDEX IF NOT EXISTS idx_projects_user_id ON ad_copy_projects(user_id);
CREATE INDEX IF NOT EXISTS idx_projects_status ON ad_copy_projects(status);
CREATE INDEX IF NOT EXISTS idx_projects_created_at ON ad_copy_projects(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_projects_updated_at ON ad_copy_projects(updated_at DESC);
CREATE INDEX IF NOT EXISTS idx_projects_tags ON ad_copy_projects USING GIN(tags);

-- Analyses
CREATE INDEX IF NOT EXISTS idx_analyses_user_id ON ad_analyses(user_id);
CREATE INDEX IF NOT EXISTS idx_analyses_project_id ON ad_analyses(project_id);
CREATE INDEX IF NOT EXISTS idx_analyses_created_at ON ad_analyses(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_analyses_platform ON ad_analyses(platform);
CREATE INDEX IF NOT EXISTS idx_analyses_overall_score ON ad_analyses(overall_score);

-- Competitor benchmarks
CREATE INDEX IF NOT EXISTS idx_competitor_analysis_id ON competitor_benchmarks(analysis_id);

-- Ad generations
CREATE INDEX IF NOT EXISTS idx_generations_analysis_id ON ad_generations(analysis_id);
CREATE INDEX IF NOT EXISTS idx_generations_variant_type ON ad_generations(variant_type);

-- ============================================================================
-- ROW LEVEL SECURITY (RLS)
-- ============================================================================
-- Enable RLS on all tables
ALTER TABLE user_profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE ad_copy_projects ENABLE ROW LEVEL SECURITY;
ALTER TABLE ad_analyses ENABLE ROW LEVEL SECURITY;
ALTER TABLE competitor_benchmarks ENABLE ROW LEVEL SECURITY;
ALTER TABLE ad_generations ENABLE ROW LEVEL SECURITY;

-- ============================================================================
-- RLS POLICIES
-- ============================================================================

-- User profiles: Users can only see and modify their own profile
CREATE POLICY "Users can view own profile" ON user_profiles
    FOR SELECT USING (auth.uid() = id);

CREATE POLICY "Users can update own profile" ON user_profiles
    FOR UPDATE USING (auth.uid() = id);

CREATE POLICY "Users can insert own profile" ON user_profiles
    FOR INSERT WITH CHECK (auth.uid() = id);

-- Projects: Users can only access their own projects
CREATE POLICY "Users can view own projects" ON ad_copy_projects
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can create own projects" ON ad_copy_projects
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own projects" ON ad_copy_projects
    FOR UPDATE USING (auth.uid() = user_id);

CREATE POLICY "Users can delete own projects" ON ad_copy_projects
    FOR DELETE USING (auth.uid() = user_id);

-- Analyses: Users can only access analyses for their projects
CREATE POLICY "Users can view own analyses" ON ad_analyses
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can create own analyses" ON ad_analyses
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

CREATE POLICY "Users can create benchmarks for own analyses" ON competitor_benchmarks
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

CREATE POLICY "Users can create generations for own analyses" ON ad_generations
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

-- ============================================================================
-- FUNCTIONS AND TRIGGERS
-- ============================================================================

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

-- Function to update project's last_analyzed_at when analysis is created
CREATE OR REPLACE FUNCTION update_project_analyzed_at()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.project_id IS NOT NULL THEN
        UPDATE ad_copy_projects 
        SET last_analyzed_at = NOW(),
            updated_at = NOW()
        WHERE id = NEW.project_id;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger to update project when analysis is created
DROP TRIGGER IF EXISTS on_analysis_created ON ad_analyses;
CREATE TRIGGER on_analysis_created
    AFTER INSERT ON ad_analyses
    FOR EACH ROW EXECUTE FUNCTION update_project_analyzed_at();

-- ============================================================================
-- SAMPLE DATA (Optional - for testing)
-- ============================================================================
-- Uncomment the lines below if you want some sample data for testing

/*
-- Insert sample project (will only work after you have a user)
INSERT INTO ad_copy_projects (
    user_id, 
    project_name, 
    description, 
    headline, 
    body_text, 
    cta, 
    platform, 
    industry, 
    target_audience,
    status
) 
SELECT 
    id as user_id,
    'Sample Holiday Campaign' as project_name,
    'Test project for holiday promotions' as description,
    'Get 50% Off This Holiday Season!' as headline,
    'Limited time offer on all our premium products. Don''t miss out on incredible savings!' as body_text,
    'Shop Now' as cta,
    'Facebook' as platform,
    'E-commerce' as industry,
    'Holiday shoppers aged 25-45' as target_audience,
    'draft' as status
FROM user_profiles 
WHERE NOT EXISTS (
    SELECT 1 FROM ad_copy_projects 
    WHERE user_id = user_profiles.id
)
LIMIT 1;
*/

-- Success message
SELECT 'AdCopySurge database schema created successfully! 🚀' as message;
