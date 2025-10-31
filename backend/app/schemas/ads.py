"""
Pydantic schemas for ad analysis API
"""
from pydantic import BaseModel
from typing import List, Optional


class AdInput(BaseModel):
    headline: str
    body_text: str
    cta: str
    platform: str = "facebook"  # facebook, google, linkedin, tiktok
    target_audience: Optional[str] = None
    industry: Optional[str] = None


class CompetitorAd(BaseModel):
    headline: str
    body_text: str
    cta: str
    platform: str
    source_url: Optional[str] = None


class AdAnalysisRequest(BaseModel):
    ad: AdInput
    competitor_ads: Optional[List[CompetitorAd]] = []


class AdScore(BaseModel):
    overall_score: float
    clarity_score: float
    persuasion_score: float
    emotion_score: float
    cta_strength: float
    platform_fit_score: float


class AdAlternative(BaseModel):
    variant_type: str = "improved"  # persuasive, emotional, stats_heavy, platform_optimized
    headline: str
    body_text: str
    cta: str
    improvement_reason: str
    expected_improvement: Optional[float] = None


class AdAnalysisResponse(BaseModel):
    analysis_id: str
    scores: AdScore
    feedback: str
    alternatives: List[AdAlternative]
    competitor_comparison: Optional[dict] = None
    quick_wins: List[str]
    tool_results: Optional[dict] = None  # Individual tool outputs (compliance, psychology, legal, ROI, etc.)
