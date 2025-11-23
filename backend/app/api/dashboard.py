# Dashboard Metrics API
# Provides real-time dashboard metrics based on actual user data

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func, case
from datetime import datetime, timedelta
from typing import Dict, Any
from app.core.database import get_db
from app.auth import get_current_user
from app.models.user import User
from app.models.ad_analysis import AdAnalysis

router = APIRouter()


@router.get("/metrics")
async def get_dashboard_metrics(
    period_days: int = 30,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Get dashboard metrics for the current user

    Returns:
    - adsAnalyzed: Number of analyses performed in the period
    - avgImprovement: Average score improvement across all analyses
    - avgScore: Average overall score across all analyses
    - topPerforming: Highest score achieved in the period
    - Change percentages compared to previous period
    """

    try:
        # Calculate date ranges
        current_end = datetime.utcnow()
        current_start = current_end - timedelta(days=period_days)
        previous_start = current_start - timedelta(days=period_days)
        previous_end = current_start

        # Query current period metrics
        current_metrics = get_period_metrics(
            db, current_user.id, current_start, current_end
        )

        # Query previous period metrics for comparison
        previous_metrics = get_period_metrics(
            db, current_user.id, previous_start, previous_end
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
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Failed to fetch dashboard metrics: {str(e)}")


def get_period_metrics(
    db: Session,
    user_id: int,
    start_date: datetime,
    end_date: datetime
) -> Dict[str, Any]:
    """Get metrics for a specific time period"""

    # Calculate improvement as (overall_score - 50) where 50 is baseline
    score_improvement = case(
        (AdAnalysis.overall_score > 50, AdAnalysis.overall_score - 50),
        else_=0
    )

    # Query metrics
    result = db.query(
        func.count(AdAnalysis.id).label('ads_analyzed'),
        func.coalesce(func.avg(score_improvement), 0).label('avg_improvement'),
        func.coalesce(func.avg(AdAnalysis.overall_score), 0).label('avg_score'),
        func.coalesce(func.max(AdAnalysis.overall_score), 0).label('top_performing')
    ).filter(
        AdAnalysis.user_id == user_id,
        AdAnalysis.created_at >= start_date,
        AdAnalysis.created_at <= end_date,
        AdAnalysis.overall_score.isnot(None)
    ).first()

    return {
        "ads_analyzed": int(result.ads_analyzed) if result.ads_analyzed else 0,
        "avg_improvement": float(result.avg_improvement) if result.avg_improvement else 0.0,
        "avg_score": float(result.avg_score) if result.avg_score else 0.0,
        "top_performing": int(result.top_performing) if result.top_performing else 0,
    }
