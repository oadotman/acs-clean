-- ============================================================================
-- AdCopySurge Production Database Constraints
-- Adds NOT NULL, CHECK constraints, and data validation for production safety
-- Run AFTER data purging and BEFORE production deployment
-- ============================================================================

-- ============================================================================
-- PART 1: Add NOT NULL Constraints to Critical Fields
-- ============================================================================

-- These constraints prevent invalid/empty data from being inserted
-- Run these AFTER cleaning existing data

-- user_profiles table constraints
ALTER TABLE user_profiles 
    ALTER COLUMN id SET NOT NULL,
    ALTER COLUMN subscription_tier SET NOT NULL,
    ALTER COLUMN monthly_analyses SET NOT NULL,
    ALTER COLUMN created_at SET NOT NULL,
    ALTER COLUMN updated_at SET NOT NULL;

-- projects table constraints  
ALTER TABLE projects
    ALTER COLUMN id SET NOT NULL,
    ALTER COLUMN user_id SET NOT NULL,
    ALTER COLUMN name SET NOT NULL,
    ALTER COLUMN created_at SET NOT NULL,
    ALTER COLUMN updated_at SET NOT NULL;

-- ad_analyses table constraints (most critical)
ALTER TABLE ad_analyses
    ALTER COLUMN id SET NOT NULL,
    ALTER COLUMN user_id SET NOT NULL,
    ALTER COLUMN headline SET NOT NULL,
    ALTER COLUMN body_text SET NOT NULL,
    ALTER COLUMN platform SET NOT NULL,
    ALTER COLUMN created_at SET NOT NULL,
    ALTER COLUMN updated_at SET NOT NULL;

-- Supporting tables
ALTER TABLE competitor_benchmarks
    ALTER COLUMN id SET NOT NULL,
    ALTER COLUMN analysis_id SET NOT NULL,
    ALTER COLUMN created_at SET NOT NULL;

ALTER TABLE ad_generations
    ALTER COLUMN id SET NOT NULL,
    ALTER COLUMN analysis_id SET NOT NULL,
    ALTER COLUMN user_selected SET NOT NULL,
    ALTER COLUMN created_at SET NOT NULL;

-- ============================================================================
-- PART 2: Add CHECK Constraints for Data Validation
-- ============================================================================

-- user_profiles validation
ALTER TABLE user_profiles 
    ADD CONSTRAINT check_subscription_tier 
    CHECK (subscription_tier IN ('free', 'basic', 'pro', 'enterprise'));

ALTER TABLE user_profiles 
    ADD CONSTRAINT check_monthly_analyses_positive 
    CHECK (monthly_analyses >= 0);

ALTER TABLE user_profiles 
    ADD CONSTRAINT check_email_format 
    CHECK (email IS NULL OR email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$');

-- projects validation
ALTER TABLE projects 
    ADD CONSTRAINT check_project_name_not_empty 
    CHECK (LENGTH(TRIM(name)) > 0);

ALTER TABLE projects 
    ADD CONSTRAINT check_project_name_length 
    CHECK (LENGTH(name) <= 255);

-- ad_analyses validation (critical for production)
ALTER TABLE ad_analyses 
    ADD CONSTRAINT check_headline_not_empty 
    CHECK (LENGTH(TRIM(headline)) > 0);

ALTER TABLE ad_analyses 
    ADD CONSTRAINT check_body_text_not_empty 
    CHECK (LENGTH(TRIM(body_text)) > 0);

ALTER TABLE ad_analyses 
    ADD CONSTRAINT check_platform_valid 
    CHECK (platform IN ('facebook', 'instagram', 'google', 'linkedin', 'twitter', 'tiktok', 'youtube'));

ALTER TABLE ad_analyses 
    ADD CONSTRAINT check_scores_range 
    CHECK (
        (overall_score IS NULL OR (overall_score >= 0 AND overall_score <= 100)) AND
        (clarity_score IS NULL OR (clarity_score >= 0 AND clarity_score <= 100)) AND
        (persuasion_score IS NULL OR (persuasion_score >= 0 AND persuasion_score <= 100)) AND
        (emotion_score IS NULL OR (emotion_score >= 0 AND emotion_score <= 100)) AND
        (cta_strength_score IS NULL OR (cta_strength_score >= 0 AND cta_strength_score <= 100)) AND
        (platform_fit_score IS NULL OR (platform_fit_score >= 0 AND platform_fit_score <= 100))
    );

ALTER TABLE ad_analyses 
    ADD CONSTRAINT check_headline_length 
    CHECK (LENGTH(headline) <= 500);

ALTER TABLE ad_analyses 
    ADD CONSTRAINT check_body_text_length 
    CHECK (LENGTH(body_text) <= 5000);

-- competitor_benchmarks validation
ALTER TABLE competitor_benchmarks 
    ADD CONSTRAINT check_competitor_scores_range 
    CHECK (
        (competitor_overall_score IS NULL OR (competitor_overall_score >= 0 AND competitor_overall_score <= 100)) AND
        (competitor_clarity_score IS NULL OR (competitor_clarity_score >= 0 AND competitor_clarity_score <= 100)) AND
        (competitor_emotion_score IS NULL OR (competitor_emotion_score >= 0 AND competitor_emotion_score <= 100)) AND
        (competitor_cta_score IS NULL OR (competitor_cta_score >= 0 AND competitor_cta_score <= 100))
    );

-- ad_generations validation
ALTER TABLE ad_generations 
    ADD CONSTRAINT check_predicted_score_range 
    CHECK (predicted_score IS NULL OR (predicted_score >= 0 AND predicted_score <= 100));

ALTER TABLE ad_generations 
    ADD CONSTRAINT check_user_rating_range 
    CHECK (user_rating IS NULL OR (user_rating >= 1 AND user_rating <= 5));

-- ============================================================================
-- PART 3: Add Performance Indexes (if missing)
-- ============================================================================

-- Additional indexes for production performance
CREATE INDEX IF NOT EXISTS idx_user_profiles_email ON user_profiles(email);
CREATE INDEX IF NOT EXISTS idx_user_profiles_subscription_tier ON user_profiles(subscription_tier);

CREATE INDEX IF NOT EXISTS idx_ad_analyses_overall_score ON ad_analyses(overall_score) WHERE overall_score IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_ad_analyses_user_platform ON ad_analyses(user_id, platform);
CREATE INDEX IF NOT EXISTS idx_ad_analyses_target_audience ON ad_analyses(target_audience) WHERE target_audience IS NOT NULL;

-- Composite indexes for common query patterns
CREATE INDEX IF NOT EXISTS idx_ad_analyses_user_created ON ad_analyses(user_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_projects_user_updated ON projects(user_id, updated_at DESC);

-- ============================================================================
-- PART 4: Create Database Functions for Production
-- ============================================================================

-- Function to validate ad content before insert/update
CREATE OR REPLACE FUNCTION validate_ad_content()
RETURNS TRIGGER AS $$
BEGIN
    -- Prevent test/demo content in production
    IF NEW.headline ILIKE '%test%' OR NEW.headline ILIKE '%demo%' OR NEW.headline ILIKE '%sample%' THEN
        RAISE EXCEPTION 'Test/demo content not allowed in production: %', NEW.headline;
    END IF;
    
    IF NEW.body_text ILIKE '%test%' OR NEW.body_text ILIKE '%debug%' OR NEW.body_text ILIKE '%lorem ipsum%' THEN
        RAISE EXCEPTION 'Test/demo content not allowed in production: %', LEFT(NEW.body_text, 50);
    END IF;
    
    -- Ensure valid platform
    IF NEW.platform NOT IN ('facebook', 'instagram', 'google', 'linkedin', 'twitter', 'tiktok', 'youtube') THEN
        RAISE EXCEPTION 'Invalid platform: %. Must be one of: facebook, instagram, google, linkedin, twitter, tiktok, youtube', NEW.platform;
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Apply the validation trigger to ad_analyses
DROP TRIGGER IF EXISTS trigger_validate_ad_content ON ad_analyses;
CREATE TRIGGER trigger_validate_ad_content
    BEFORE INSERT OR UPDATE ON ad_analyses
    FOR EACH ROW EXECUTE FUNCTION validate_ad_content();

-- Function to prevent test user creation
CREATE OR REPLACE FUNCTION validate_user_profile()
RETURNS TRIGGER AS $$
BEGIN
    -- Prevent test/demo emails in production
    IF NEW.email ILIKE '%test%' OR NEW.email ILIKE '%demo%' OR NEW.email ILIKE '%example.com%' THEN
        RAISE EXCEPTION 'Test/demo email not allowed in production: %', NEW.email;
    END IF;
    
    -- Ensure valid subscription tier
    IF NEW.subscription_tier NOT IN ('free', 'basic', 'pro', 'enterprise') THEN
        RAISE EXCEPTION 'Invalid subscription tier: %. Must be one of: free, basic, pro, enterprise', NEW.subscription_tier;
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Apply the validation trigger to user_profiles
DROP TRIGGER IF EXISTS trigger_validate_user_profile ON user_profiles;
CREATE TRIGGER trigger_validate_user_profile
    BEFORE INSERT OR UPDATE ON user_profiles
    FOR EACH ROW EXECUTE FUNCTION validate_user_profile();

-- ============================================================================
-- PART 5: Create Production Monitoring Views
-- ============================================================================

-- View for monitoring analysis quality
CREATE OR REPLACE VIEW v_analysis_quality_metrics AS
SELECT 
    platform,
    COUNT(*) as total_analyses,
    ROUND(AVG(overall_score), 2) as avg_overall_score,
    ROUND(AVG(clarity_score), 2) as avg_clarity_score,
    ROUND(AVG(persuasion_score), 2) as avg_persuasion_score,
    ROUND(AVG(emotion_score), 2) as avg_emotion_score,
    COUNT(*) FILTER (WHERE overall_score >= 80) as high_quality_count,
    ROUND(100.0 * COUNT(*) FILTER (WHERE overall_score >= 80) / COUNT(*), 2) as high_quality_percentage
FROM ad_analyses 
WHERE overall_score IS NOT NULL
GROUP BY platform
ORDER BY total_analyses DESC;

-- View for user activity monitoring
CREATE OR REPLACE VIEW v_user_activity_metrics AS
SELECT 
    subscription_tier,
    COUNT(*) as user_count,
    SUM(monthly_analyses) as total_analyses,
    ROUND(AVG(monthly_analyses), 2) as avg_analyses_per_user,
    COUNT(*) FILTER (WHERE monthly_analyses > 0) as active_users,
    ROUND(100.0 * COUNT(*) FILTER (WHERE monthly_analyses > 0) / COUNT(*), 2) as active_user_percentage
FROM user_profiles
GROUP BY subscription_tier
ORDER BY user_count DESC;

-- View for recent system health
CREATE OR REPLACE VIEW v_system_health AS
WITH recent_stats AS (
    SELECT 
        COUNT(*) as analyses_last_24h
    FROM ad_analyses 
    WHERE created_at >= NOW() - INTERVAL '24 hours'
),
error_stats AS (
    SELECT 
        COUNT(*) as analyses_with_no_score
    FROM ad_analyses 
    WHERE overall_score IS NULL AND created_at >= NOW() - INTERVAL '24 hours'
)
SELECT 
    rs.analyses_last_24h,
    es.analyses_with_no_score,
    CASE 
        WHEN rs.analyses_last_24h = 0 THEN 'NO_ACTIVITY'
        WHEN es.analyses_with_no_score > rs.analyses_last_24h * 0.1 THEN 'HIGH_ERROR_RATE'
        ELSE 'HEALTHY'
    END as system_status,
    ROUND(100.0 * es.analyses_with_no_score / GREATEST(rs.analyses_last_24h, 1), 2) as error_percentage
FROM recent_stats rs, error_stats es;

-- ============================================================================
-- PART 6: Grant Permissions for Production Views
-- ============================================================================

GRANT SELECT ON v_analysis_quality_metrics TO authenticated, service_role;
GRANT SELECT ON v_user_activity_metrics TO authenticated, service_role;
GRANT SELECT ON v_system_health TO authenticated, service_role;

-- ============================================================================
-- PART 7: Verification and Testing
-- ============================================================================

-- Test that constraints work by attempting invalid inserts
-- (These should fail with helpful error messages)

-- Test 1: Try to insert empty headline (should fail)
/*
INSERT INTO ad_analyses (user_id, headline, body_text, platform) 
VALUES ('11111111-1111-1111-1111-111111111111', '', 'body', 'facebook');
*/

-- Test 2: Try to insert invalid platform (should fail)
/*
INSERT INTO ad_analyses (user_id, headline, body_text, platform) 
VALUES ('11111111-1111-1111-1111-111111111111', 'headline', 'body', 'invalid');
*/

-- Test 3: Try to insert invalid score (should fail)
/*
INSERT INTO ad_analyses (user_id, headline, body_text, platform, overall_score) 
VALUES ('11111111-1111-1111-1111-111111111111', 'headline', 'body', 'facebook', 150);
*/

-- Test 4: Try to insert test content (should fail)
/*
INSERT INTO ad_analyses (user_id, headline, body_text, platform) 
VALUES ('11111111-1111-1111-1111-111111111111', 'Test headline', 'body', 'facebook');
*/

-- ============================================================================
-- PART 8: Constraint Summary Report
-- ============================================================================

-- Show all constraints that were added
SELECT 
    'PRODUCTION CONSTRAINTS SUMMARY' as report_type,
    tc.table_name,
    tc.constraint_name,
    tc.constraint_type,
    CASE 
        WHEN tc.constraint_type = 'CHECK' THEN '✅ DATA VALIDATION'
        WHEN tc.constraint_type = 'NOT NULL' THEN '✅ REQUIRED FIELD'
        WHEN tc.constraint_type = 'FOREIGN KEY' THEN '✅ REFERENTIAL INTEGRITY'
        ELSE '🔄 OTHER'
    END as purpose
FROM information_schema.table_constraints tc
WHERE tc.table_schema = 'public' 
    AND tc.table_name IN ('user_profiles', 'projects', 'ad_analyses', 'competitor_benchmarks', 'ad_generations')
    AND tc.constraint_type IN ('CHECK', 'FOREIGN KEY')
ORDER BY tc.table_name, tc.constraint_type, tc.constraint_name;

-- Show all triggers that were added
SELECT 
    'PRODUCTION TRIGGERS SUMMARY' as report_type,
    trigger_name,
    event_object_table as table_name,
    action_timing,
    event_manipulation,
    '✅ CONTENT VALIDATION' as purpose
FROM information_schema.triggers
WHERE trigger_schema = 'public'
    AND trigger_name LIKE 'trigger_validate_%'
ORDER BY event_object_table, trigger_name;

-- Show production views created
SELECT 
    'PRODUCTION VIEWS SUMMARY' as report_type,
    table_name as view_name,
    '✅ MONITORING' as purpose
FROM information_schema.views
WHERE table_schema = 'public'
    AND table_name LIKE 'v_%'
ORDER BY table_name;

-- Final production readiness check
SELECT 
    'PRODUCTION READINESS FINAL' as final_check,
    CASE 
        WHEN EXISTS(SELECT 1 FROM information_schema.table_constraints WHERE constraint_name = 'check_platform_valid')
            AND EXISTS(SELECT 1 FROM information_schema.triggers WHERE trigger_name = 'trigger_validate_ad_content')
            THEN '🎉 PRODUCTION CONSTRAINTS ACTIVE'
        ELSE '❌ CONSTRAINTS NOT PROPERLY APPLIED'
    END as status,
    NOW() as applied_at;