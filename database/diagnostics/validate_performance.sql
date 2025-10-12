-- ============================================================================
-- AdCopySurge Database Performance Validation
-- Tests database performance and validates indexes for production workload
-- Run this after schema validation to ensure production-ready performance
-- ============================================================================

-- ============================================================================
-- PART 1: Query Performance Tests
-- ============================================================================

-- Test 1: User dashboard analytics query (most critical)
EXPLAIN (ANALYZE, BUFFERS, FORMAT TEXT) 
SELECT 
    COUNT(*) as total_analyses,
    AVG(overall_score) as avg_score,
    MAX(created_at) as last_analysis
FROM ad_analyses 
WHERE user_id = '11111111-1111-1111-1111-111111111111'  -- Replace with real UUID
    AND created_at >= NOW() - INTERVAL '30 days';

-- Test 2: Recent analyses for user (dashboard)
EXPLAIN (ANALYZE, BUFFERS, FORMAT TEXT)
SELECT 
    id,
    headline,
    platform,
    overall_score,
    created_at
FROM ad_analyses 
WHERE user_id = '11111111-1111-1111-1111-111111111111'  -- Replace with real UUID
ORDER BY created_at DESC 
LIMIT 10;

-- Test 3: Platform filtering (common filter)
EXPLAIN (ANALYZE, BUFFERS, FORMAT TEXT)
SELECT 
    COUNT(*) as count,
    AVG(overall_score) as avg_score
FROM ad_analyses 
WHERE platform = 'facebook' 
    AND created_at >= NOW() - INTERVAL '7 days';

-- Test 4: Project analytics query
EXPLAIN (ANALYZE, BUFFERS, FORMAT TEXT)
SELECT 
    p.id,
    p.name,
    COUNT(aa.id) as analysis_count,
    AVG(aa.overall_score) as avg_score
FROM projects p
LEFT JOIN ad_analyses aa ON p.id = aa.project_id
WHERE p.user_id = '11111111-1111-1111-1111-111111111111'  -- Replace with real UUID
GROUP BY p.id, p.name
ORDER BY p.updated_at DESC
LIMIT 20;

-- Test 5: Score range filtering (search functionality)
EXPLAIN (ANALYZE, BUFFERS, FORMAT TEXT)
SELECT 
    id,
    headline,
    overall_score,
    platform
FROM ad_analyses 
WHERE overall_score >= 80 
    AND created_at >= NOW() - INTERVAL '30 days'
ORDER BY overall_score DESC
LIMIT 50;

-- ============================================================================
-- PART 2: Index Usage Analysis
-- ============================================================================

-- Check index usage statistics
SELECT 
    schemaname,
    tablename,
    indexname,
    idx_scan as times_used,
    idx_tup_read as tuples_read,
    idx_tup_fetch as tuples_fetched,
    CASE 
        WHEN idx_scan = 0 THEN '❌ UNUSED INDEX'
        WHEN idx_scan < 100 THEN '⚠️ LOW USAGE'
        ELSE '✅ ACTIVE INDEX'
    END as usage_status
FROM pg_stat_user_indexes 
WHERE schemaname = 'public'
    AND tablename IN ('user_profiles', 'projects', 'ad_analyses', 'competitor_benchmarks', 'ad_generations')
ORDER BY tablename, idx_scan DESC;

-- Check for missing indexes (table scans)
SELECT 
    schemaname,
    tablename,
    seq_scan as sequential_scans,
    seq_tup_read as rows_read_sequentially,
    CASE 
        WHEN seq_scan > idx_scan AND seq_tup_read > 1000 THEN '❌ NEEDS INDEX'
        WHEN seq_scan > idx_scan THEN '⚠️ CONSIDER INDEX'
        ELSE '✅ GOOD'
    END as recommendation
FROM pg_stat_user_tables 
WHERE schemaname = 'public'
    AND tablename IN ('user_profiles', 'projects', 'ad_analyses', 'competitor_benchmarks', 'ad_generations')
ORDER BY seq_tup_read DESC;

-- ============================================================================
-- PART 3: Table Statistics and Maintenance
-- ============================================================================

-- Table sizes and row counts
SELECT 
    schemaname,
    tablename,
    n_tup_ins as inserts,
    n_tup_upd as updates,
    n_tup_del as deletes,
    n_live_tup as live_rows,
    n_dead_tup as dead_rows,
    CASE 
        WHEN n_dead_tup > n_live_tup * 0.1 THEN '⚠️ NEEDS VACUUM'
        ELSE '✅ CLEAN'
    END as maintenance_needed,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as total_size
FROM pg_stat_user_tables 
WHERE schemaname = 'public'
    AND tablename IN ('user_profiles', 'projects', 'ad_analyses', 'competitor_benchmarks', 'ad_generations')
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;

-- Check for bloated tables
WITH table_stats AS (
    SELECT 
        schemaname,
        tablename,
        n_dead_tup,
        n_live_tup,
        CASE 
            WHEN n_live_tup > 0 THEN (n_dead_tup::float / n_live_tup::float) * 100
            ELSE 0
        END as dead_tuple_percentage
    FROM pg_stat_user_tables 
    WHERE schemaname = 'public'
)
SELECT 
    schemaname,
    tablename,
    dead_tuple_percentage,
    CASE 
        WHEN dead_tuple_percentage > 20 THEN '❌ URGENT: Run VACUUM'
        WHEN dead_tuple_percentage > 10 THEN '⚠️ Run VACUUM soon'
        ELSE '✅ No action needed'
    END as recommendation
FROM table_stats
WHERE tablename IN ('user_profiles', 'projects', 'ad_analyses', 'competitor_benchmarks', 'ad_generations')
ORDER BY dead_tuple_percentage DESC;

-- ============================================================================
-- PART 4: Connection and Resource Usage
-- ============================================================================

-- Current database connections
SELECT 
    state,
    COUNT(*) as connection_count
FROM pg_stat_activity 
WHERE datname = current_database()
GROUP BY state
ORDER BY connection_count DESC;

-- Long running queries (potential performance issues)
SELECT 
    pid,
    now() - pg_stat_activity.query_start AS duration,
    query,
    state
FROM pg_stat_activity 
WHERE (now() - pg_stat_activity.query_start) > interval '5 minutes'
    AND state != 'idle'
ORDER BY duration DESC;

-- Database size information
SELECT 
    pg_database.datname as database_name,
    pg_size_pretty(pg_database_size(pg_database.datname)) as size
FROM pg_database
WHERE datname = current_database();

-- ============================================================================
-- PART 5: Performance Recommendations
-- ============================================================================

-- Generate performance recommendations based on analysis
WITH performance_analysis AS (
    -- Analyze most queried tables
    SELECT 
        tablename,
        seq_scan,
        idx_scan,
        n_live_tup,
        CASE 
            WHEN seq_scan > idx_scan AND n_live_tup > 1000 THEN 'add_index'
            WHEN n_dead_tup > n_live_tup * 0.1 THEN 'vacuum_needed'
            ELSE 'ok'
        END as recommendation_type
    FROM pg_stat_user_tables 
    WHERE schemaname = 'public'
        AND tablename IN ('ad_analyses', 'projects', 'user_profiles')
),
missing_indexes AS (
    -- Check for commonly filtered columns without indexes
    SELECT 
        'ad_analyses' as table_name,
        'industry' as column_name,
        'Consider adding index on industry for filtering' as recommendation
    WHERE NOT EXISTS (
        SELECT 1 FROM pg_indexes 
        WHERE tablename = 'ad_analyses' AND indexdef LIKE '%industry%'
    )
    
    UNION ALL
    
    SELECT 
        'ad_analyses' as table_name,
        'target_audience' as column_name,
        'Consider adding index on target_audience for filtering' as recommendation
    WHERE NOT EXISTS (
        SELECT 1 FROM pg_indexes 
        WHERE tablename = 'ad_analyses' AND indexdef LIKE '%target_audience%'
    )
)
SELECT 
    'PERFORMANCE RECOMMENDATIONS' as category,
    table_name,
    column_name,
    recommendation,
    'HIGH' as priority
FROM missing_indexes

UNION ALL

SELECT 
    'MAINTENANCE RECOMMENDATIONS' as category,
    tablename as table_name,
    'N/A' as column_name,
    'Run VACUUM ANALYZE on this table' as recommendation,
    'MEDIUM' as priority
FROM performance_analysis 
WHERE recommendation_type = 'vacuum_needed'

UNION ALL

SELECT 
    'INDEX RECOMMENDATIONS' as category,
    tablename as table_name,
    'N/A' as column_name,
    'Consider adding selective indexes based on query patterns' as recommendation,
    'LOW' as priority
FROM performance_analysis 
WHERE recommendation_type = 'add_index';

-- ============================================================================
-- PART 6: Suggested Performance Optimizations
-- ============================================================================

-- Additional indexes for production performance (run if needed)
/*
-- Uncomment and run these if the performance analysis recommends them:

-- Index for industry filtering
CREATE INDEX CONCURRENTLY idx_ad_analyses_industry_created 
ON ad_analyses(industry, created_at DESC) 
WHERE industry IS NOT NULL;

-- Index for target audience filtering  
CREATE INDEX CONCURRENTLY idx_ad_analyses_target_audience_created
ON ad_analyses(target_audience, created_at DESC)
WHERE target_audience IS NOT NULL;

-- Composite index for dashboard queries
CREATE INDEX CONCURRENTLY idx_ad_analyses_user_score_created
ON ad_analyses(user_id, overall_score DESC, created_at DESC)
WHERE overall_score IS NOT NULL;

-- Index for platform analytics
CREATE INDEX CONCURRENTLY idx_ad_analyses_platform_score_created
ON ad_analyses(platform, overall_score, created_at DESC)
WHERE overall_score IS NOT NULL;

-- Partial index for recent high-scoring analyses
CREATE INDEX CONCURRENTLY idx_ad_analyses_recent_high_scores
ON ad_analyses(overall_score DESC, created_at DESC)
WHERE overall_score >= 80 AND created_at >= NOW() - INTERVAL '90 days';
*/

-- ============================================================================
-- PART 7: Production Performance Benchmarks
-- ============================================================================

-- Benchmark typical queries with timing
\timing on

-- Benchmark 1: User dashboard load
SELECT 
    COUNT(*) as total_analyses,
    COUNT(*) FILTER (WHERE created_at >= NOW() - INTERVAL '30 days') as recent_analyses,
    ROUND(AVG(overall_score), 1) as avg_score,
    COUNT(DISTINCT platform) as platforms_used
FROM ad_analyses 
WHERE user_id = (SELECT id FROM user_profiles LIMIT 1);

-- Benchmark 2: Analysis history page
SELECT 
    id,
    headline,
    platform,
    overall_score,
    created_at
FROM ad_analyses 
WHERE user_id = (SELECT id FROM user_profiles LIMIT 1)
ORDER BY created_at DESC 
LIMIT 20;

-- Benchmark 3: Platform filter
SELECT 
    platform,
    COUNT(*) as count,
    ROUND(AVG(overall_score), 1) as avg_score
FROM ad_analyses 
WHERE created_at >= NOW() - INTERVAL '7 days'
GROUP BY platform
ORDER BY count DESC;

-- Benchmark 4: Project summary
SELECT 
    p.name,
    COUNT(aa.id) as analysis_count,
    ROUND(AVG(aa.overall_score), 1) as avg_score
FROM projects p
LEFT JOIN ad_analyses aa ON p.id = aa.project_id
WHERE p.user_id = (SELECT id FROM user_profiles LIMIT 1)
GROUP BY p.id, p.name
ORDER BY p.updated_at DESC;

\timing off

-- ============================================================================
-- PART 8: Performance Summary Report
-- ============================================================================

-- Generate final performance report
WITH performance_summary AS (
    SELECT 
        COUNT(*) FILTER (WHERE tablename = 'ad_analyses') as core_tables,
        COUNT(*) FILTER (WHERE idx_scan > 0) as active_indexes,
        COUNT(*) FILTER (WHERE seq_scan > idx_scan AND seq_tup_read > 1000) as tables_needing_indexes,
        COUNT(*) FILTER (WHERE n_dead_tup > n_live_tup * 0.1) as tables_needing_vacuum
    FROM pg_stat_user_indexes psi
    JOIN pg_stat_user_tables pst ON psi.relid = pst.relid
    WHERE psi.schemaname = 'public'
        AND psi.tablename IN ('user_profiles', 'projects', 'ad_analyses', 'competitor_benchmarks', 'ad_generations')
),
size_summary AS (
    SELECT 
        pg_size_pretty(SUM(pg_total_relation_size(schemaname||'.'||tablename))) as total_db_size,
        COUNT(*) as total_tables
    FROM pg_stat_user_tables 
    WHERE schemaname = 'public'
        AND tablename IN ('user_profiles', 'projects', 'ad_analyses', 'competitor_benchmarks', 'ad_generations')
)
SELECT 
    'DATABASE PERFORMANCE SUMMARY' as report_type,
    CASE 
        WHEN ps.tables_needing_indexes = 0 AND ps.tables_needing_vacuum = 0 AND ps.active_indexes > 5
            THEN '🎉 EXCELLENT PERFORMANCE'
        WHEN ps.tables_needing_indexes <= 1 AND ps.tables_needing_vacuum <= 1
            THEN '✅ GOOD PERFORMANCE'
        WHEN ps.tables_needing_indexes <= 2 OR ps.tables_needing_vacuum <= 2
            THEN '⚠️ NEEDS OPTIMIZATION'
        ELSE '❌ POOR PERFORMANCE'
    END as performance_status,
    ps.active_indexes as active_indexes,
    ps.tables_needing_indexes as tables_needing_indexes,
    ps.tables_needing_vacuum as tables_needing_vacuum,
    ss.total_db_size as database_size,
    NOW() as analysis_time
FROM performance_summary ps, size_summary ss;

-- Final recommendations
SELECT 
    'FINAL PERFORMANCE RECOMMENDATIONS' as section,
    CASE 
        WHEN EXISTS(SELECT 1 FROM pg_stat_user_tables WHERE n_dead_tup > n_live_tup * 0.1)
            THEN 'Run VACUUM ANALYZE on tables with high dead tuple ratio'
        WHEN EXISTS(SELECT 1 FROM pg_stat_user_tables WHERE seq_scan > idx_scan AND n_live_tup > 1000)
            THEN 'Add missing indexes for frequently queried tables'
        ELSE 'Database performance is optimized for production'
    END as recommendation,
    CASE 
        WHEN EXISTS(SELECT 1 FROM pg_stat_user_tables WHERE n_dead_tup > n_live_tup * 0.1) THEN 'HIGH'
        WHEN EXISTS(SELECT 1 FROM pg_stat_user_tables WHERE seq_scan > idx_scan AND n_live_tup > 1000) THEN 'MEDIUM' 
        ELSE 'NONE'
    END as priority;