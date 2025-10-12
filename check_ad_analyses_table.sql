-- Quick check of ad_analyses table structure and recent data
-- Run this in your Supabase SQL Editor

-- 1. Check if ad_analyses table exists and show structure
SELECT 
    '=== AD_ANALYSES TABLE STRUCTURE ===' as info,
    column_name,
    data_type,
    is_nullable,
    column_default
FROM information_schema.columns 
WHERE table_schema = 'public' 
    AND table_name = 'ad_analyses'
ORDER BY ordinal_position;

-- 2. Count total records
SELECT 
    '=== RECORD COUNT ===' as info,
    COUNT(*) as total_analyses
FROM ad_analyses;

-- 3. Show recent analyses (last 5, without sensitive data)
SELECT 
    '=== RECENT ANALYSES ===' as info,
    id,
    platform,
    overall_score,
    clarity_score,
    persuasion_score,
    emotion_score,
    cta_strength_score,
    platform_fit_score,
    created_at
FROM ad_analyses
ORDER BY created_at DESC
LIMIT 5;

-- 4. Check for any null analysis_data fields (these might be failing updates)
SELECT 
    '=== ANALYSES WITH NULL ANALYSIS_DATA ===' as info,
    COUNT(*) as null_analysis_data_count
FROM ad_analyses
WHERE analysis_data IS NULL;

-- 5. Check for analyses created recently but with 0 scores (might indicate update failures)
SELECT 
    '=== RECENT ANALYSES WITH ZERO SCORES ===' as info,
    COUNT(*) as zero_score_count
FROM ad_analyses
WHERE created_at >= NOW() - INTERVAL '1 hour'
    AND (overall_score = 0 OR overall_score IS NULL);