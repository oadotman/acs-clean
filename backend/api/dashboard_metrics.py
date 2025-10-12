# Dashboard Metrics API
# Provides real-time dashboard metrics based on actual user data

from fastapi import APIRouter, Depends, HTTPException
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
import asyncpg
from dataclasses import dataclass
from ..database import get_db_connection
from ..auth import get_current_user

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])

@dataclass
class DashboardMetrics:
    """Dashboard metrics data structure"""
    ads_analyzed: int
    ads_analyzed_change: float
    avg_improvement: float
    avg_improvement_change: float
    avg_score: float
    avg_score_change: float
    top_performing: int
    top_performing_change: float
    period_start: datetime
    period_end: datetime

@router.get("/metrics")
async def get_dashboard_metrics(
    user_id: str = Depends(get_current_user),
    period_days: int = 30,
    db: asyncpg.Connection = Depends(get_db_connection)
) -> Dict[str, Any]:
    """
    Get dashboard metrics for the current user
    
    Returns:
    - ads_analyzed: Number of analyses performed in the period
    - avg_improvement: Average score improvement across all analyses
    - avg_score: Average overall score across all analyses  
    - top_performing: Highest score achieved in the period
    - Change percentages compared to previous period
    """
    
    try:
        # Calculate date ranges
        current_end = datetime.utcnow()
        current_start = current_end - timedelta(days=period_days)
        previous_start = current_start - timedelta(days=period_days)
        previous_end = current_start
        
        # Query current period metrics
        current_metrics = await get_period_metrics(
            db, user_id, current_start, current_end
        )
        
        # Query previous period metrics for comparison
        previous_metrics = await get_period_metrics(
            db, user_id, previous_start, previous_end
        )
        
        # Calculate changes
        def calculate_change(current: float, previous: float) -> float:
            if previous == 0:
                return 100.0 if current > 0 else 0.0
            return ((current - previous) / previous) * 100
        
        # Build response
        response = {
            "adsAnalyzed": current_metrics["ads_analyzed"],
            "adsAnalyzedChange": calculate_change(
                current_metrics["ads_analyzed"], 
                previous_metrics["ads_analyzed"]
            ),
            "avgImprovement": round(current_metrics["avg_improvement"], 1),
            "avgImprovementChange": calculate_change(
                current_metrics["avg_improvement"],
                previous_metrics["avg_improvement"]
            ),
            "avgScore": round(current_metrics["avg_score"], 0),
            "avgScoreChange": calculate_change(
                current_metrics["avg_score"],
                previous_metrics["avg_score"]
            ),
            "topPerforming": current_metrics["top_performing"],
            "topPerformingChange": calculate_change(
                current_metrics["top_performing"],
                previous_metrics["top_performing"]
            ),
            "periodStart": current_start.isoformat(),
            "periodEnd": current_end.isoformat(),
            "periodDays": period_days
        }
        
        return response
        
    except Exception as e:
        print(f"Error fetching dashboard metrics: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch dashboard metrics")

async def get_period_metrics(
    db: asyncpg.Connection,
    user_id: str, 
    start_date: datetime, 
    end_date: datetime
) -> Dict[str, Any]:
    """Get metrics for a specific time period"""
    
    query = """
    WITH period_analyses AS (
        SELECT 
            id,
            overall_score,
            created_at,
            -- Calculate improvement based on difference between overall_score and baseline
            -- Using 50 as baseline "before improvement" score
            CASE 
                WHEN overall_score IS NOT NULL AND overall_score > 50 
                THEN overall_score - 50 
                ELSE 0 
            END as score_improvement
        FROM ad_analyses 
        WHERE user_id = $1 
            AND created_at >= $2 
            AND created_at <= $3
            AND overall_score IS NOT NULL
    )
    SELECT 
        COUNT(*) as ads_analyzed,
        COALESCE(AVG(score_improvement), 0) as avg_improvement,
        COALESCE(AVG(overall_score), 0) as avg_score,
        COALESCE(MAX(overall_score), 0) as top_performing
    FROM period_analyses;
    """
    
    row = await db.fetchrow(query, user_id, start_date, end_date)
    
    return {
        "ads_analyzed": int(row["ads_analyzed"]) if row["ads_analyzed"] else 0,
        "avg_improvement": float(row["avg_improvement"]) if row["avg_improvement"] else 0.0,
        "avg_score": float(row["avg_score"]) if row["avg_score"] else 0.0,
        "top_performing": int(row["top_performing"]) if row["top_performing"] else 0,
    }

@router.get("/metrics/detailed")
async def get_detailed_dashboard_metrics(
    user_id: str = Depends(get_current_user),
    period_days: int = 30,
    db: asyncpg.Connection = Depends(get_db_connection)
) -> Dict[str, Any]:
    """Get detailed dashboard metrics including breakdowns"""
    
    try:
        current_end = datetime.utcnow()
        current_start = current_end - timedelta(days=period_days)
        
        # Platform breakdown
        platform_query = """
        SELECT 
            platform,
            COUNT(*) as count,
            AVG(overall_score) as avg_score
        FROM ad_analyses 
        WHERE user_id = $1 
            AND created_at >= $2 
            AND created_at <= $3
            AND overall_score IS NOT NULL
        GROUP BY platform
        ORDER BY count DESC;
        """
        
        platform_rows = await db.fetch(platform_query, user_id, current_start, current_end)
        
        # Industry breakdown  
        industry_query = """
        SELECT 
            COALESCE(industry, 'Unknown') as industry,
            COUNT(*) as count,
            AVG(overall_score) as avg_score
        FROM ad_analyses 
        WHERE user_id = $1 
            AND created_at >= $2 
            AND created_at <= $3
            AND overall_score IS NOT NULL
        GROUP BY industry
        ORDER BY count DESC
        LIMIT 10;
        """
        
        industry_rows = await db.fetch(industry_query, user_id, current_start, current_end)
        
        # Score distribution
        score_distribution_query = """
        SELECT 
            CASE 
                WHEN overall_score >= 90 THEN 'Excellent (90-100)'
                WHEN overall_score >= 80 THEN 'Good (80-89)'
                WHEN overall_score >= 70 THEN 'Fair (70-79)'
                WHEN overall_score >= 60 THEN 'Poor (60-69)'
                ELSE 'Needs Improvement (<60)'
            END as score_range,
            COUNT(*) as count
        FROM ad_analyses 
        WHERE user_id = $1 
            AND created_at >= $2 
            AND created_at <= $3
            AND overall_score IS NOT NULL
        GROUP BY score_range
        ORDER BY 
            CASE score_range
                WHEN 'Excellent (90-100)' THEN 1
                WHEN 'Good (80-89)' THEN 2
                WHEN 'Fair (70-79)' THEN 3
                WHEN 'Poor (60-69)' THEN 4
                ELSE 5
            END;
        """
        
        score_rows = await db.fetch(score_distribution_query, user_id, current_start, current_end)
        
        # Recent activity (last 7 days daily breakdown)
        activity_query = """
        SELECT 
            DATE(created_at) as analysis_date,
            COUNT(*) as daily_count,
            AVG(overall_score) as daily_avg_score
        FROM ad_analyses 
        WHERE user_id = $1 
            AND created_at >= $2
            AND overall_score IS NOT NULL
        GROUP BY DATE(created_at)
        ORDER BY analysis_date DESC
        LIMIT 7;
        """
        
        recent_start = current_end - timedelta(days=7)
        activity_rows = await db.fetch(activity_query, user_id, recent_start)
        
        return {
            "platformBreakdown": [
                {
                    "platform": row["platform"] or "Unknown",
                    "count": int(row["count"]),
                    "avgScore": round(float(row["avg_score"]), 1)
                }
                for row in platform_rows
            ],
            "industryBreakdown": [
                {
                    "industry": row["industry"],
                    "count": int(row["count"]),
                    "avgScore": round(float(row["avg_score"]), 1)
                }
                for row in industry_rows
            ],
            "scoreDistribution": [
                {
                    "range": row["score_range"],
                    "count": int(row["count"])
                }
                for row in score_rows
            ],
            "recentActivity": [
                {
                    "date": row["analysis_date"].isoformat(),
                    "count": int(row["daily_count"]),
                    "avgScore": round(float(row["daily_avg_score"]), 1)
                }
                for row in activity_rows
            ]
        }
        
    except Exception as e:
        print(f"Error fetching detailed dashboard metrics: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch detailed metrics")

@router.get("/metrics/summary")
async def get_metrics_summary(
    user_id: str = Depends(get_current_user),
    db: asyncpg.Connection = Depends(get_db_connection)
) -> Dict[str, Any]:
    """Get high-level summary metrics for the user"""
    
    try:
        summary_query = """
        WITH user_stats AS (
            SELECT 
                COUNT(*) as total_analyses,
                AVG(overall_score) as lifetime_avg_score,
                MAX(overall_score) as best_score,
                MIN(created_at) as first_analysis_date,
                MAX(created_at) as last_analysis_date,
                COUNT(DISTINCT platform) as platforms_used,
                COUNT(DISTINCT project_id) as projects_count
            FROM ad_analyses 
            WHERE user_id = $1 AND overall_score IS NOT NULL
        ),
        recent_stats AS (
            SELECT 
                COUNT(*) as analyses_last_30_days
            FROM ad_analyses 
            WHERE user_id = $1 
                AND created_at >= NOW() - INTERVAL '30 days'
                AND overall_score IS NOT NULL
        )
        SELECT 
            us.*,
            rs.analyses_last_30_days
        FROM user_stats us
        CROSS JOIN recent_stats rs;
        """
        
        row = await db.fetchrow(summary_query, user_id)
        
        if not row:
            return {
                "totalAnalyses": 0,
                "lifetimeAvgScore": 0,
                "bestScore": 0,
                "analysesLast30Days": 0,
                "platformsUsed": 0,
                "projectsCount": 0,
                "firstAnalysisDate": None,
                "lastAnalysisDate": None,
                "isNewUser": True
            }
        
        return {
            "totalAnalyses": int(row["total_analyses"]),
            "lifetimeAvgScore": round(float(row["lifetime_avg_score"]), 1),
            "bestScore": int(row["best_score"]),
            "analysesLast30Days": int(row["analyses_last_30_days"]),
            "platformsUsed": int(row["platforms_used"]),
            "projectsCount": int(row["projects_count"] or 0),
            "firstAnalysisDate": row["first_analysis_date"].isoformat() if row["first_analysis_date"] else None,
            "lastAnalysisDate": row["last_analysis_date"].isoformat() if row["last_analysis_date"] else None,
            "isNewUser": row["total_analyses"] == 0
        }
        
    except Exception as e:
        print(f"Error fetching metrics summary: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch metrics summary")