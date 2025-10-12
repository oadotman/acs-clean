from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from app.core.database import get_db
from app.services.analytics_service import AnalyticsService
from app.auth import get_current_user
from app.models.user import User

router = APIRouter()

class AnalyticsResponse(BaseModel):
    total_analyses: int
    avg_score_improvement: float
    top_performing_platforms: List[dict]
    monthly_usage: dict
    subscription_analytics: dict

@router.get("/dashboard", response_model=AnalyticsResponse)
async def get_dashboard_analytics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get user dashboard analytics"""
    analytics_service = AnalyticsService(db)
    analytics = analytics_service.get_user_analytics(current_user.id)
    
    return analytics

@router.get("/export/pdf")
async def export_analytics_pdf(
    analysis_ids: List[str],
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Export analysis results as PDF report"""
    analytics_service = AnalyticsService(db)
    pdf_data = await analytics_service.generate_pdf_report(current_user.id, analysis_ids)
    
    return {"pdf_url": pdf_data["url"], "download_link": pdf_data["download_link"]}
