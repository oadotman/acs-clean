"""
Pydantic schemas for ad analysis API
"""
from pydantic import BaseModel
from typing import List, Optional


class BrandVoiceInput(BaseModel):
    """Structured brand voice and style preferences"""
    tone: Optional[str] = None  # professional, conversational, playful, authoritative, empathetic
    personality: Optional[str] = None  # friendly, confident, innovative, trustworthy, energetic
    formality: Optional[str] = None  # casual, semi-formal, formal
    brand_values: Optional[str] = None  # Core brand identity values
    past_ads: Optional[str] = None  # Past successful ads for learning
    emoji_preference: Optional[str] = "auto"  # auto, include, exclude


class AdInput(BaseModel):
    headline: str
    body_text: str
    cta: str
    platform: str = "facebook"  # facebook, google, linkedin, tiktok
    target_audience: Optional[str] = None  # Deprecated - use target_audience_detail instead
    industry: Optional[str] = None

    # 7 Strategic Context Inputs
    product_or_service: Optional[str] = None  # What is being advertised
    target_audience_detail: Optional[str] = None  # Detailed demographics + psychographics
    value_proposition: Optional[str] = None  # Why customers buy vs competitors
    audience_pain_points: Optional[str] = None  # Problems the audience faces
    desired_outcomes: Optional[str] = None  # What the audience wants to achieve
    trust_factors: Optional[str] = None  # Reviews, proof, guarantees, certifications
    offer_details: Optional[str] = None  # Discount, price, guarantee, terms, bundles

    # Brand Voice and Style
    brand_voice: Optional[BrandVoiceInput] = None


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
    variant_type: str = "improved"  # benefit_focused, problem_focused, story_driven, improved
    headline: str
    body_text: str
    cta: str
    improvement_reason: str
    expected_improvement: Optional[float] = None
    psychology_framework: Optional[str] = None  # Psychology principle used (e.g., "Outcome-Driven", "Pain-Aware")


class AdAnalysisResponse(BaseModel):
    analysis_id: str
    scores: AdScore
    feedback: str
    alternatives: List[AdAlternative]
    competitor_comparison: Optional[dict] = None
    quick_wins: List[str]
    tool_results: Optional[dict] = None  # Individual tool outputs (compliance, psychology, legal, ROI, etc.)
    missing_strategic_fields: Optional[List[str]] = None  # List of missing strategic context fields
