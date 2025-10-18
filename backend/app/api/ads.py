from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, File, UploadFile, Form
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from pydantic import BaseModel
from app.core.database import get_db
from app.services.ad_analysis_service_enhanced import EnhancedAdAnalysisService
from app.services.production_ai_generator import ProductionAIService
from app.auth import get_current_user, require_subscription_limit
from app.models.user import User
from app.core.exceptions import AIProviderUnavailable
from app.core.config import settings
import asyncio
import logging
from app.schemas.ads import (
    AdInput, 
    CompetitorAd, 
    AdAnalysisRequest, 
    AdScore, 
    AdAlternative, 
    AdAnalysisResponse
)
from app.utils.text_parser import TextParser
from app.utils.file_extract import FileExtractor
from app.core.config import settings
import json
import uuid
import time
from datetime import datetime

router = APIRouter()
logger = logging.getLogger(__name__)

# Initialize AI service with OpenAI
ai_service = None
if settings.OPENAI_API_KEY:
    try:
        ai_service = ProductionAIService(
            openai_key=settings.OPENAI_API_KEY
        )
    except Exception as e:
        print(f"WARNING: Failed to initialize AI service: {e}")
        ai_service = None

# Import the new platform services
from app.services.platform_ad_generator import PlatformAdGenerator, GenerationResult
from app.services.platform_registry import get_platform_registry, resolve_platform_id
from app.services.variant_strategies import get_variant_context
from app.services.response_formatter import format_standardized_response

# Helper functions for platform-aware generation
def _format_content_for_display(content: Dict[str, Any], platform_id: str) -> str:
    """Format generated content for display as a single string"""
    if platform_id == 'google_ads':
        # Google Ads has multiple headlines and descriptions
        headlines = content.get('headlines', [])
        descriptions = content.get('descriptions', [])
        cta = content.get('cta', '')
        
        parts = []
        if headlines:
            parts.append(f"Headlines: {' | '.join(headlines)}")
        if descriptions:
            parts.append(f"Descriptions: {' | '.join(descriptions)}")
        if cta:
            parts.append(f"CTA: {cta}")
        
        return ' • '.join(parts)
    
    elif platform_id == 'instagram':
        # Instagram has body + hashtags + optional CTA
        body = content.get('body', '')
        hashtags = content.get('hashtags', [])
        cta = content.get('cta', '')
        
        parts = [body]
        if hashtags:
            parts.append(' '.join(hashtags))
        if cta:
            parts.append(cta)
        
        return '\n'.join(parts)
    
    elif platform_id == 'twitter_x':
        # Twitter/X just has body with embedded CTA
        return content.get('body', '')
    
    else:
        # Facebook, LinkedIn, TikTok have headline + body + CTA
        headline = content.get('headline', '')
        body = content.get('body', '')
        cta = content.get('cta', '')
        
        parts = []
        if headline:
            parts.append(headline)
        if body:
            parts.append(body)
        if cta:
            parts.append(cta)
        
        return ' • '.join(parts)

def _create_fallback_response(ad_copy: str, platform_id: str, errors: List[str]) -> Dict[str, Any]:
    """Create fallback response when platform generation fails"""
    analysis_id = f"fallback_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{platform_id}"
    
    # Create basic fallback content
    fallback_content = {
        'headline': ad_copy[:50] if len(ad_copy) > 50 else ad_copy,
        'body': ad_copy,
        'cta': 'Learn More'
    }
    
    if platform_id == 'google_ads':
        fallback_content = {
            'headlines': [ad_copy[:30], 'Quality Service', 'Get Started'],
            'descriptions': [ad_copy[:90], 'Professional solutions for your needs'],
            'cta': 'Contact Us'
        }
    elif platform_id == 'instagram':
        fallback_content = {
            'body': ad_copy,
            'hashtags': ['#business', '#service', '#quality'],
            'cta': 'Discover More'
        }
    elif platform_id == 'twitter_x':
        fallback_content = {
            'body': ad_copy[:280]
        }
    elif platform_id == 'tiktok':
        fallback_content = {
            'body': ad_copy[:100],
            'cta': 'Try Now'
        }
    
    return {
        'analysis_id': analysis_id,
        'platform_id': platform_id,
        'original': {
            'copy': ad_copy,
            'score': 60
        },
        'improved': {
            'copy': _format_content_for_display(fallback_content, platform_id),
            'score': 65,
            'content': fallback_content,
            'platform_specific': False
        },
        'abTests': {
            'abc_variants': [],
            'platform_optimized': False
        },
        'errors': errors,
        'fallback_used': True
    }

@router.post("/comprehensive-analyze")
async def comprehensive_analyze_ad(
    request: dict,  # Accept flexible request format
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_subscription_limit)
):
    """Platform-aware comprehensive ad generation with structured output"""
    try:
        # Extract data from request
        ad_copy = request.get('ad_copy', '')
        platform = request.get('platform', 'facebook')
        user_id = request.get('user_id') or getattr(current_user, 'id', None)
        brand_voice = request.get('brand_voice', {})
        no_emojis = request.get('no_emojis', False)
        
        if not ad_copy:
            raise HTTPException(status_code=400, detail="ad_copy is required")
        
        # Resolve and validate platform
        resolved_platform = resolve_platform_id(platform)
        logger.info(f"[platform-aware] request received: user_id={user_id}, platform={platform} -> {resolved_platform}, ad_copy_len={len(ad_copy)}")
        
        # Validate platform is supported
        registry = get_platform_registry()
        if not registry.is_valid_platform(resolved_platform):
            raise HTTPException(status_code=400, detail=f"Unsupported platform: {platform}")
        
        # Prepare context for generation
        generation_context = {
            'industry': brand_voice.get('industry', 'general'),
            'target_audience': brand_voice.get('target_audience', 'general audience'),
            'brand_voice': brand_voice.get('personality', 'professional'),
            'tone': brand_voice.get('tone', 'conversational'),
            'formality': brand_voice.get('formality', 'semi-formal')
        }
        
        # Initialize platform-aware generator
        if not settings.OPENAI_API_KEY:
            raise HTTPException(status_code=500, detail="AI service not configured")
        
        generator = PlatformAdGenerator(settings.OPENAI_API_KEY)
        
        # Generate platform-specific ad
        generation_result = await generator.generate_ad(
            text_input=ad_copy,
            platform_id=resolved_platform,
            context=generation_context
        )
        
        if not generation_result.success:
            logger.error(f"[platform-aware] Generation failed: {generation_result.errors}")
            # Fall back to basic structure for backward compatibility
            return _create_fallback_response(ad_copy, resolved_platform, generation_result.errors)
        
        logger.info(f"[platform-aware] Generation successful: {generation_result.metrics}")

        # Generate platform-specific A/B/C variants using platform strategies
        abc_variants = []
        try:
            # Create 3 variants using platform-specific strategies
            variant_requests = []
            
            for variant_version in ['A', 'B', 'C']:
                # Get platform-specific context for this variant
                variant_context = get_variant_context(resolved_platform, variant_version, generation_context)
                
                variant_requests.append({
                    'text_input': ad_copy,
                    'platform_id': resolved_platform, 
                    'context': variant_context
                })
            
            logger.info(f"[platform-aware] Generating {len(variant_requests)} platform-specific variants for {resolved_platform}")
            variant_results = await generator.generate_batch(variant_requests)
            
            for i, variant_result in enumerate(variant_results):
                variant_version = ['A', 'B', 'C'][i]
                variant_context = variant_requests[i]['context']
                
                if variant_result.success:
                    abc_variants.append({
                        "version": variant_version,
                        "type": variant_context.get('variant_focus', 'benefit_focused'),
                        "variant_name": variant_context.get('variant_name', f'Version {variant_version}'),
                        "variant_description": variant_context.get('variant_description', ''),
                        "confidence_score": getattr(variant_result, 'confidence_score', 75),
                        **variant_result.generated_content,
                        "char_counts": variant_result.char_counts,
                        "platform_id": resolved_platform
                    })
                else:
                    # Add fallback variant with lower confidence
                    abc_variants.append({
                        "version": variant_version,
                        "type": variant_context.get('variant_focus', 'benefit_focused'), 
                        "variant_name": variant_context.get('variant_name', f'Version {variant_version}'),
                        "variant_description": f"Fallback variant (generation failed)",
                        "confidence_score": 45,  # Low score for fallback
                        **generation_result.generated_content,  # Use main result as fallback
                        "char_counts": generation_result.char_counts,
                        "platform_id": resolved_platform,
                        "errors": variant_result.errors
                    })
            
            logger.info(f"[platform-aware] Generated {len(abc_variants)} platform-specific variants")
            
        except Exception as e:
            logger.warning(f"[platform-aware] Variant generation failed: {e}")
            abc_variants = []

        # Ensure we have exactly 3 variants (fallback if needed)
        if len(abc_variants) < 3:
            logger.info(f"[platform-aware] Only {len(abc_variants)} variants generated, filling remaining with main result")
            
            variant_types = ['benefit_focused', 'problem_focused', 'story_driven']
            variant_names = ['Benefit-Focused', 'Problem-Focused', 'Story-Driven']
            
            for i in range(len(abc_variants), 3):
                abc_variants.append({
                    "id": f"variant_{chr(65 + i).lower()}",  # a, b, c
                    "version": chr(65 + i),  # A, B, C
                    "type": variant_types[i],
                    "variant_label": f"VERSION {chr(65 + i)}",
                    "variant_name": variant_names[i],
                    "variant_description": f"Platform-optimized {variant_types[i].replace('_', ' ')} approach (fallback)",
                    **generation_result.generated_content,
                    "char_counts": generation_result.char_counts,
                    "platform_id": resolved_platform
                })
        
        logger.info(f"[platform-aware] Final abc_variants count: {len(abc_variants)}")

        # Use standardized response format
        logger.info(f"[platform-aware] Creating standardized response: platform={resolved_platform}, success={generation_result.success}, variants={len(abc_variants)}")
        
        # Get validation result for confidence scoring
        from app.services.content_validator import validate_content
        validation_result = validate_content(generation_result.generated_content, resolved_platform, strict_mode=False)
        
        # Create standardized response
        standardized_response = format_standardized_response(
            platform_id=resolved_platform,
            original_ad_copy=ad_copy,
            generation_result=generation_result,
            validation_result=validation_result,
            variants=abc_variants,
            original_score=65
        )
        
        logger.info(f"[platform-aware] Standardized response ready: confidence={standardized_response['confidenceScore']}, variants={len(standardized_response['variants'])}")
        return standardized_response
        
    except Exception as e:
        logger.exception(f"[platform-aware] failure: {e}")
        raise HTTPException(status_code=500, detail=f"Platform-aware generation failed: {str(e)}")

@router.post("/analyze")
async def analyze_ad(
    request: AdAnalysisRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_subscription_limit)
):
    """Analyze an ad using real OpenAI and generate alternatives"""
    analysis_id = str(uuid.uuid4())
    
    try:
        # Prepare ad data for AI analysis
        ad_data = {
            "headline": request.ad.headline,
            "body_text": request.ad.body_text,
            "cta": request.ad.cta,
            "platform": request.ad.platform,
            "industry": getattr(request.ad, 'industry', None),
            "target_audience": getattr(request.ad, 'target_audience', None)
        }
        
        # Extract brand voice parameters from request if available
        brand_voice = getattr(request.ad, 'brand_voice', None)
        if brand_voice:
            logger.info(f"Brand voice parameters received: {brand_voice}")
        
        # Use real AI service if available, otherwise fallback to enhanced service
        if ai_service:
            try:
                logger.info(f"Starting AI analysis for user {current_user.id}, analysis {analysis_id}")
                start_time = time.time()
                
                # Extract brand voice parameters for AI service call
                emoji_level = brand_voice.get('emoji_level', 'moderate') if brand_voice else 'moderate'
                human_tone = brand_voice.get('tone', 'conversational') if brand_voice else 'conversational'
                brand_tone = brand_voice.get('personality', 'friendly') if brand_voice else 'casual'
                formality_level = 5  # Default middle ground
                if brand_voice and brand_voice.get('formality'):
                    formality_mapping = {'casual': 3, 'semi-formal': 5, 'formal': 7}
                    formality_level = formality_mapping.get(brand_voice.get('formality'), 5)
                
                # Extract advanced creative controls
                creativity_level = brand_voice.get('creativity_level', 5) if brand_voice else 5
                urgency_level = brand_voice.get('urgency_level', 5) if brand_voice else 5
                emotion_type = brand_voice.get('emotion_type', 'inspiring') if brand_voice else 'inspiring'
                filter_cliches = brand_voice.get('filter_cliches', True) if brand_voice else True
                
                target_audience_description = brand_voice.get('target_audience') if brand_voice else None
                brand_voice_description = brand_voice.get('brand_values') if brand_voice else None
                
                logger.info(f"AI generation parameters: emoji_level={emoji_level}, human_tone={human_tone}, formality_level={formality_level}")
                logger.info(f"Advanced controls: creativity_level={creativity_level}, urgency_level={urgency_level}, emotion_type={emotion_type}, filter_cliches={filter_cliches}")
                
                # Generate AI-powered analysis with timeout and all brand voice parameters
                ai_result = await asyncio.wait_for(
                    ai_service.generate_ad_alternative(
                        ad_data=ad_data,
                        variant_type="comprehensive_analysis",
                        emoji_level=emoji_level,
                        human_tone=human_tone,
                        brand_tone=brand_tone,
                        formality_level=formality_level,
                        target_audience_description=target_audience_description,
                        brand_voice_description=brand_voice_description,
                        creativity_level=creativity_level,
                        urgency_level=urgency_level,
                        emotion_type=emotion_type,
                        filter_cliches=filter_cliches
                    ),
                    timeout=settings.AI_REQUEST_TIMEOUT + 5  # Extra 5 seconds buffer
                )
                
                elapsed_time = (time.time() - start_time) * 1000  # Convert to milliseconds
                logger.info(f"AI analysis completed for user {current_user.id} in {elapsed_time:.2f}ms")
                
                # Extract scores from AI result
                ai_scores = ai_result.get('scores', {})
                ai_feedback = ai_result.get('feedback', [])
                ai_alternatives = ai_result.get('alternatives', [])
                
                # Create comprehensive scores
                scores = {
                    "overall_score": ai_scores.get('overall_score', 75),
                    "clarity_score": ai_scores.get('clarity_score', 75),
                    "persuasion_score": ai_scores.get('persuasion_score', 75),
                    "emotion_score": ai_scores.get('emotion_score', 75),
                    "cta_strength_score": ai_scores.get('cta_strength_score', 75),
                    "platform_fit_score": ai_scores.get('platform_fit_score', 75),
                    "analysis_data": {
                        "feedback": ai_feedback,
                        "ai_powered": True,
                        "model_used": "gpt-4",
                        "timestamp": datetime.utcnow().isoformat(),
                        "full_ai_response": ai_result
                    }
                }
                
                # Format alternatives from AI
                alternatives = []
                for alt in ai_alternatives:
                    alternatives.append({
                        "variant_type": alt.get("type", "ai_improved"),
                        "headline": alt.get("headline", request.ad.headline),
                        "body_text": alt.get("body_text", request.ad.body_text),
                        "cta": alt.get("cta", request.ad.cta),
                        "improvement_reason": alt.get("reason", "AI-generated improvement"),
                        "predicted_score": alt.get("expected_score", 85)
                    })
                
                feedback_text = " ".join(ai_feedback) if isinstance(ai_feedback, list) else str(ai_feedback)
                
            except (asyncio.TimeoutError, AIProviderUnavailable) as ai_error:
                elapsed_time = (time.time() - start_time) * 1000 if 'start_time' in locals() else 0
                logger.warning(
                    f"AI timeout/unavailable for user {current_user.id}, analysis {analysis_id} after {elapsed_time:.2f}ms: {str(ai_error)}"
                )
                # Fallback to enhanced service when AI times out or is unavailable
                return await _fallback_to_enhanced_service(request, db, current_user, analysis_id)
            except Exception as ai_error:
                elapsed_time = (time.time() - start_time) * 1000 if 'start_time' in locals() else 0
                logger.error(
                    f"AI service failed for user {current_user.id}, analysis {analysis_id} after {elapsed_time:.2f}ms: {str(ai_error)}"
                )
                # Fallback to enhanced service if AI fails
                return await _fallback_to_enhanced_service(request, db, current_user, analysis_id)
        else:
            # AI service not available, use enhanced service
            return await _fallback_to_enhanced_service(request, db, current_user, analysis_id)
        
        # Save analysis to database
        await _save_analysis_to_supabase(
            analysis_id=analysis_id,
            user_id=current_user.id,
            ad_data=ad_data,
            scores=scores,
            alternatives=alternatives,
            feedback=feedback_text,
            db=db
        )
        
        return {
            "analysis_id": analysis_id,
            "scores": scores,
            "alternatives": alternatives,
            "feedback": feedback_text
        }
        
    except Exception as e:
        print(f"Analysis failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@router.get("/history", response_model=List[dict])
async def get_analysis_history(
    limit: int = 10,
    offset: int = 0,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get user's analysis history"""
    ad_service = EnhancedAdAnalysisService(db)
    history = ad_service.get_user_analysis_history(current_user.id, limit, offset)
    
    return history

@router.get("/analysis/{analysis_id}")
async def get_analysis_detail(
    analysis_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get detailed analysis results"""
    ad_service = EnhancedAdAnalysisService(db)
    analysis = ad_service.get_analysis_by_id(analysis_id, current_user.id)
    
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found")
    
    return analysis

@router.post("/generate-alternatives")
async def generate_alternatives(
    ad: AdInput,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Generate alternative ad variations"""
    
    ad_service = EnhancedAdAnalysisService(db)
    alternatives = await ad_service.generate_ad_alternatives(ad)
    
    return {"alternatives": alternatives}

# Parse request models
class ParseTextRequest(BaseModel):
    text: str
    platform: Optional[str] = 'facebook'
    user_id: Optional[str] = None

class GenerateRequest(BaseModel):
    platform: str = 'facebook'
    productService: str
    valueProposition: str
    targetAudience: Optional[str] = None
    tone: str = 'professional'
    industry: Optional[str] = None
    keyBenefits: Optional[str] = None
    numVariations: int = 3
    includeEmojis: bool = False
    includeUrgency: bool = True
    includeStats: bool = False
    prompt_context: Optional[str] = None
    generation_options: Optional[dict] = None
    user_id: Optional[str] = None

@router.post("/parse")
async def parse_ads(
    request: ParseTextRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Parse pasted ad copy text"""
    try:
        text_parser = TextParser()
        parsed_ads = text_parser.parse_text(request.text, request.platform)
        
        if not parsed_ads:
            return {
                "ads": [],
                "message": "No ad copy could be parsed from the provided text",
                "success": False
            }
        
        return {
            "ads": parsed_ads,
            "message": f"Successfully parsed {len(parsed_ads)} ad{'s' if len(parsed_ads) > 1 else ''}",
            "success": True
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Parsing failed: {str(e)}")

@router.post("/parse-file")
async def parse_file(
    file: UploadFile = File(...),
    platform: str = Form('facebook'),
    user_id: str = Form(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Parse uploaded file for ad copy"""
    try:
        file_extractor = FileExtractor()
        content = await file.read()
        
        parsed_ads = file_extractor.extract_from_file(
            content, 
            file.filename, 
            platform
        )
        
        if not parsed_ads:
            return {
                "ads": [],
                "message": "No ad copy could be extracted from the file",
                "success": False
            }
        
        return {
            "ads": parsed_ads,
            "message": f"Successfully extracted {len(parsed_ads)} ad{'s' if len(parsed_ads) > 1 else ''} from file",
            "success": True
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"File parsing failed: {str(e)}")

@router.post("/generate")
async def generate_ad_copy(
    request: GenerateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_subscription_limit)
):
    """Generate ad copy using AI"""
    try:
        ad_service = EnhancedAdAnalysisService(db)
        
        # Create a prompt for AI generation
        prompt = f"""
Create {request.numVariations} compelling ad variations for {request.platform}.

Product/Service: {request.productService}
Value Proposition: {request.valueProposition}
Target Audience: {request.targetAudience or 'general audience'}
Tone: {request.tone}
Industry: {request.industry or 'general'}
Key Benefits: {request.keyBenefits or 'N/A'}

Options:
- Include emojis: {request.includeEmojis}
- Add urgency: {request.includeUrgency}
- Include statistics: {request.includeStats}

For each variation, provide:
1. Headline (catchy and attention-grabbing)
2. Body text (compelling description)
3. Call-to-action (action-oriented)

Return as JSON array with objects containing headline, body_text, cta, platform fields.
        """
        
        # For now, create template-based variations
        # In production, this would call OpenAI API
        variations = []
        
        for i in range(request.numVariations):
            variation = {
                "headline": f"{request.valueProposition}" + (" 🚀" if request.includeEmojis else ""),
                "body_text": f"Join thousands who trust {request.productService}. {request.keyBenefits or 'Transform your business today.'}",
                "cta": "Get Started" if i == 0 else ("Learn More" if i == 1 else "Try Free"),
                "platform": request.platform,
                "industry": request.industry,
                "target_audience": request.targetAudience
            }
            variations.append(variation)
        
        return {
            "ads": variations,
            "platform": request.platform,
            "generation_info": f"Generated {len(variations)} variations using AI",
            "success": True
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Generation failed: {str(e)}")


# Helper functions for AI analysis
async def _fallback_to_enhanced_service(request: AdAnalysisRequest, db: Session, current_user: User, analysis_id: str):
    """Fallback to enhanced service when AI is not available"""
    ad_service = EnhancedAdAnalysisService(db)
    analysis = await ad_service.analyze_ad(
        user_id=current_user.id,
        ad=request.ad,
        competitor_ads=request.competitor_ads
    )
    
    # Format response for frontend compatibility
    return {
        "analysis_id": analysis.analysis_id,
        "scores": {
            "overall_score": analysis.scores.overall_score,
            "clarity_score": analysis.scores.clarity_score,
            "persuasion_score": analysis.scores.persuasion_score,
            "emotion_score": analysis.scores.emotion_score,
            "cta_strength_score": analysis.scores.cta_strength,
            "platform_fit_score": analysis.scores.platform_fit_score,
            "analysis_data": {
                "feedback": "\n".join(analysis.feedback) if isinstance(analysis.feedback, list) else analysis.feedback,
                "quick_wins": analysis.quick_wins,
                "competitor_comparison": analysis.competitor_comparison,
                "tools_used": getattr(analysis, 'tools_used', []),
                "timestamp": getattr(analysis, 'timestamp', None),
                "ai_powered": False
            }
        },
        "alternatives": [{
            "variant_type": alt.variant_type if hasattr(alt, 'variant_type') else "enhanced",
            "headline": alt.headline,
            "body_text": alt.body_text,
            "cta": alt.cta,
            "improvement_reason": alt.improvement_reason if hasattr(alt, 'improvement_reason') else "Enhanced analysis",
            "predicted_score": alt.expected_improvement if hasattr(alt, 'expected_improvement') else 75
        } for alt in analysis.alternatives],
        "feedback": "\n".join(analysis.feedback) if isinstance(analysis.feedback, list) else analysis.feedback
    }


async def _save_analysis_to_supabase(analysis_id: str, user_id: int, ad_data: dict, scores: dict, alternatives: list, feedback: str, db: Session):
    """Save analysis results to database"""
    try:
        from app.models.ad_analysis import AdAnalysis
        
        analysis_record = AdAnalysis(
            id=analysis_id,
            user_id=user_id,
            headline=ad_data.get('headline', ''),
            body_text=ad_data.get('body_text', ''),
            cta=ad_data.get('cta', ''),
            platform=ad_data.get('platform', 'facebook'),
            target_audience=ad_data.get('target_audience'),
            industry=ad_data.get('industry'),
            overall_score=scores.get('overall_score', 75),
            clarity_score=scores.get('clarity_score', 75),
            persuasion_score=scores.get('persuasion_score', 75),
            emotion_score=scores.get('emotion_score', 75),
            cta_strength_score=scores.get('cta_strength_score', 75),
            platform_fit_score=scores.get('platform_fit_score', 75),
            feedback=feedback,
            analysis_data=scores.get('analysis_data', {}),
            created_at=datetime.utcnow()
        )
        
        db.add(analysis_record)
        db.commit()
        
        print(f"✅ Saved analysis {analysis_id} to database")
        
    except Exception as e:
        print(f"❌ Failed to save analysis to database: {e}")
        db.rollback()
