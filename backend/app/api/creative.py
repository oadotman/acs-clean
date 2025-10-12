"""
Creative Controls API - Phase 4 & 5 Integration

This module provides API endpoints for advanced creative controls,
variant generation, A/B/C testing, and creative analytics.
Integrates with ProductionAIService and VariantGenerator.
"""

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from pydantic import BaseModel
from app.core.database import get_db
from app.services.production_ai_generator import ProductionAIService
from app.services.variant_generator import VariantGenerator, VariantStrategy
from app.services.cliche_filter import ClicheFilter
from app.auth import get_current_user, require_subscription_limit
from app.models.user import User
from app.core.config import settings
from app.core.exceptions import AIProviderUnavailable, ProductionError
from app.constants.creative_controls import EmotionType
import logging
from datetime import datetime
import json
import uuid

logger = logging.getLogger(__name__)
router = APIRouter()

# Initialize AI services
ai_service = None
variant_generator = None
cliche_filter = None

if settings.OPENAI_API_KEY:
    try:
        ai_service = ProductionAIService(
            openai_key=settings.OPENAI_API_KEY
        )
        variant_generator = VariantGenerator(ai_service)
        cliche_filter = ClicheFilter()
        logger.info("Creative Controls API initialized with AI services")
    except Exception as e:
        logger.error(f"Failed to initialize AI services: {e}")
        ai_service = None
        variant_generator = None
        cliche_filter = None

# Pydantic models for request/response validation
class AdData(BaseModel):
    headline: str
    body_text: str
    cta: str
    platform: str = "facebook"
    industry: Optional[str] = None
    target_audience: Optional[str] = None

class CreativeControls(BaseModel):
    creativity_level: int = 5
    urgency_level: int = 5
    emotion_type: str = "inspiring"
    filter_cliches: bool = True
    num_variants: int = 1
    variant_strategy: str = "diverse"

class GenerationOptions(BaseModel):
    emoji_level: str = "moderate"
    human_tone: str = "conversational"
    brand_tone: str = "casual"
    formality_level: int = 5
    target_audience_description: Optional[str] = None
    brand_voice_description: Optional[str] = None
    include_cta: bool = True
    cta_style: str = "medium"

class VariantGenerationRequest(BaseModel):
    ad_data: AdData
    creative_controls: CreativeControls
    generation_options: GenerationOptions

class PresetRequest(BaseModel):
    name: str
    settings: Dict[str, Any]
    user_id: Optional[str] = None

class ClicheAnalysisRequest(BaseModel):
    text: str

class PlatformOptimizationRequest(BaseModel):
    platform: str
    ad_data: AdData

# API Endpoints

@router.post("/generate-variants")
async def generate_creative_variants(
    request: VariantGenerationRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_subscription_limit)
):
    """
    Generate creative variants using advanced controls - Phase 4 & 5
    """
    if not variant_generator:
        raise HTTPException(
            status_code=503, 
            detail="AI services not available. Please check OpenAI configuration."
        )
    
    try:
        # Convert Pydantic models to dict format expected by services
        ad_data = {
            "headline": request.ad_data.headline,
            "body_text": request.ad_data.body_text,
            "cta": request.ad_data.cta,
            "platform": request.ad_data.platform,
            "industry": request.ad_data.industry,
            "target_audience": request.ad_data.target_audience
        }
        
        # Map string emotion type to enum
        try:
            emotion_type = EmotionType(request.creative_controls.emotion_type)
        except ValueError:
            emotion_type = EmotionType.INSPIRING
        
        # Map string strategy to enum
        try:
            strategy = VariantStrategy(request.creative_controls.variant_strategy)
        except ValueError:
            strategy = VariantStrategy.DIVERSE
        
        logger.info(f"Generating {request.creative_controls.num_variants} variants for user {current_user.id}")
        
        # Generate variants using the variant generator
        variant_set = await variant_generator.generate_variant_set(
            ad_data=ad_data,
            strategy=strategy,
            num_variants=request.creative_controls.num_variants,
            base_creativity=request.creative_controls.creativity_level,
            base_urgency=request.creative_controls.urgency_level,
            base_emotion=emotion_type,
            variant_type="creative_controlled",
            # Pass generation options
            emoji_level=request.generation_options.emoji_level,
            human_tone=request.generation_options.human_tone,
            brand_tone=request.generation_options.brand_tone,
            formality_level=request.generation_options.formality_level,
            target_audience_description=request.generation_options.target_audience_description,
            brand_voice_description=request.generation_options.brand_voice_description,
            include_cta=request.generation_options.include_cta,
            cta_style=request.generation_options.cta_style,
            filter_cliches=request.creative_controls.filter_cliches
        )
        
        # Log successful generation for analytics
        background_tasks.add_task(
            _log_variant_generation,
            user_id=current_user.id,
            platform=request.ad_data.platform,
            num_variants=request.creative_controls.num_variants,
            strategy=request.creative_controls.variant_strategy,
            db=db
        )
        
        return {
            "success": True,
            "variants": variant_set.get("variants", []),
            "comparison": variant_set.get("comparison", {}),
            "recommendations": variant_set.get("recommendations", []),
            "generation_id": str(uuid.uuid4()),
            "timestamp": datetime.utcnow().isoformat(),
            "ai_powered": True
        }
        
    except AIProviderUnavailable as e:
        logger.error(f"AI provider unavailable: {e}")
        raise HTTPException(
            status_code=503,
            detail=f"AI generation service unavailable: {str(e)}"
        )
    except ProductionError as e:
        logger.error(f"Production error: {e}")
        raise HTTPException(
            status_code=400,
            detail=f"Generation failed: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Unexpected error in variant generation: {e}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error during variant generation"
        )

@router.post("/analyze-cliches")
async def analyze_cliches(
    request: ClicheAnalysisRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Analyze cliché usage in ad copy
    """
    if not cliche_filter:
        raise HTTPException(
            status_code=503, 
            detail="Cliché analysis service not available"
        )
    
    try:
        analysis_result = await cliche_filter.analyze_text(request.text)
        
        return {
            "success": True,
            "cliches_found": analysis_result.get("cliches_found", []),
            "cliche_count": analysis_result.get("cliche_count", 0),
            "severity_score": analysis_result.get("severity_score", 0),
            "suggestions": analysis_result.get("suggestions", []),
            "filtered_text": analysis_result.get("filtered_text", request.text)
        }
        
    except Exception as e:
        logger.error(f"Cliché analysis failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Cliché analysis failed: {str(e)}"
        )

@router.get("/analytics")
async def get_creative_analytics(
    time_range: str = "30d",
    platform: str = "all",
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get creative analytics data for user
    """
    try:
        # This would typically query the database for user's creative analytics
        # For now, return a placeholder structure
        analytics_data = {
            "time_range": time_range,
            "platform": platform,
            "total_variants_generated": 0,
            "most_used_emotion_types": [],
            "average_creativity_level": 5.0,
            "platform_performance": {},
            "improvement_trends": [],
            "best_performing_variants": []
        }
        
        return {
            "success": True,
            "data": analytics_data
        }
        
    except Exception as e:
        logger.error(f"Analytics fetch failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch analytics: {str(e)}"
        )

@router.post("/platform-optimizations")
async def get_platform_optimizations(
    request: PlatformOptimizationRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Get platform-specific creative optimization recommendations
    """
    if not ai_service:
        raise HTTPException(
            status_code=503, 
            detail="AI optimization service not available"
        )
    
    try:
        ad_data = {
            "headline": request.ad_data.headline,
            "body_text": request.ad_data.body_text,
            "cta": request.ad_data.cta,
            "platform": request.platform,
            "industry": request.ad_data.industry,
            "target_audience": request.ad_data.target_audience
        }
        
        # Generate platform-specific optimization
        optimization_result = await ai_service.generate_ad_alternative(
            ad_data=ad_data,
            variant_type=f"platform_optimization_{request.platform}"
        )
        
        return {
            "success": True,
            "platform": request.platform,
            "optimizations": optimization_result.get("alternatives", []),
            "recommendations": optimization_result.get("feedback", []),
            "platform_score": optimization_result.get("scores", {}).get("platform_fit_score", 75)
        }
        
    except Exception as e:
        logger.error(f"Platform optimization failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Platform optimization failed: {str(e)}"
        )

# Phase 6: Preset System
@router.get("/presets")
async def get_presets(
    current_user: User = Depends(get_current_user)
):
    """
    Get available presets for different industries/use cases
    """
    try:
        # Return built-in presets + user's custom presets
        builtin_presets = [
            {
                "id": "ecommerce_high_urgency",
                "name": "E-commerce - High Urgency",
                "description": "High-converting settings for e-commerce sales",
                "settings": {
                    "creativity_level": 7,
                    "urgency_level": 8,
                    "emotion_type": "urgency",
                    "emoji_level": "moderate",
                    "human_tone": "persuasive"
                },
                "industry": "ecommerce",
                "type": "builtin"
            },
            {
                "id": "saas_trust_building",
                "name": "SaaS - Trust Building",
                "description": "Professional tone for B2B SaaS products",
                "settings": {
                    "creativity_level": 5,
                    "urgency_level": 4,
                    "emotion_type": "trust_building",
                    "emoji_level": "minimal",
                    "human_tone": "professional"
                },
                "industry": "saas",
                "type": "builtin"
            },
            {
                "id": "social_viral",
                "name": "Social Media - Viral",
                "description": "Engaging content for social media virality",
                "settings": {
                    "creativity_level": 9,
                    "urgency_level": 6,
                    "emotion_type": "excitement",
                    "emoji_level": "high",
                    "human_tone": "casual"
                },
                "industry": "social",
                "type": "builtin"
            }
        ]
        
        return {
            "success": True,
            "data": {
                "builtin_presets": builtin_presets,
                "custom_presets": []  # TODO: Fetch user's custom presets from database
            }
        }
        
    except Exception as e:
        logger.error(f"Preset fetch failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch presets: {str(e)}"
        )

@router.post("/presets")
async def save_preset(
    request: PresetRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Save a custom preset configuration
    """
    try:
        # TODO: Save to database
        preset_id = str(uuid.uuid4())
        
        saved_preset = {
            "id": preset_id,
            "name": request.name,
            "settings": request.settings,
            "user_id": current_user.id,
            "created_at": datetime.utcnow().isoformat(),
            "type": "custom"
        }
        
        return {
            "success": True,
            "data": saved_preset
        }
        
    except Exception as e:
        logger.error(f"Preset save failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to save preset: {str(e)}"
        )

# Helper functions
async def _log_variant_generation(user_id: str, platform: str, num_variants: int, strategy: str, db: Session):
    """Log variant generation for analytics"""
    try:
        # TODO: Save generation log to database for analytics
        logger.info(f"User {user_id} generated {num_variants} variants for {platform} using {strategy} strategy")
    except Exception as e:
        logger.error(f"Failed to log variant generation: {e}")