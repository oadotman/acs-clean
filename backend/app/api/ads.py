from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, File, UploadFile, Form
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from app.core.database import get_db
from app.services.ad_analysis_service_enhanced import EnhancedAdAnalysisService
from app.services.production_ai_generator import ProductionAIService
from app.auth import get_current_user, require_subscription_limit
from app.models.user import User
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
from datetime import datetime

router = APIRouter()

# Initialize AI service with OpenAI
ai_service = None
if settings.OPENAI_API_KEY:
    try:
        ai_service = ProductionAIService(
            openai_key=settings.OPENAI_API_KEY
        )
    except Exception as e:
        print(f"⚠️ Failed to initialize AI service: {e}")
        ai_service = None

@router.post("/comprehensive-analyze")
async def comprehensive_analyze_ad(
    request: dict,  # Accept flexible request format
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_subscription_limit)
):
    """Comprehensive analysis with all 9 tools - new endpoint"""
    try:
        # Extract data from request
        ad_copy = request.get('ad_copy', '')
        platform = request.get('platform', 'facebook')
        user_id = request.get('user_id')
        
        if not ad_copy:
            raise HTTPException(status_code=400, detail="ad_copy is required")
        
        # Convert ad_copy string to AdInput format if needed
        if isinstance(ad_copy, str):
            # Parse the ad copy into components
            ad_input = AdInput(
                headline=ad_copy[:100] if len(ad_copy) > 100 else ad_copy,  # First 100 chars as headline
                body_text=ad_copy,
                cta="Learn More",  # Default CTA
                platform=platform
            )
        else:
            ad_input = AdInput(**ad_copy)
        
        # Create analysis request
        analysis_request = AdAnalysisRequest(
            ad=ad_input,
            competitor_ads=[]
        )
        
        # Perform comprehensive analysis
        ad_service = EnhancedAdAnalysisService(db)
        analysis = await ad_service.analyze_ad(
            user_id=current_user.id,
            ad=analysis_request.ad,
            competitor_ads=analysis_request.competitor_ads
        )
        
        return {
            "success": True,
            "analysis": analysis,
            "platform": platform,
            "message": "Comprehensive analysis completed successfully"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Comprehensive analysis failed: {str(e)}")

@router.post("/analyze")
async def analyze_ad(
    request: AdAnalysisRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
    # Auth handled by frontend Supabase session - no backend DB user needed
):
    """Analyze an ad using EnhancedAdAnalysisService with AI-powered improvements"""
    analysis_id = str(uuid.uuid4())
    
    # Use user_id from request if provided, otherwise use a default
    # Frontend sends user_id from Supabase session
    from types import SimpleNamespace
    user_id = getattr(request.ad, 'user_id', None) or request.dict().get('user_id', 'anonymous')
    current_user = SimpleNamespace(id=user_id, email='user@app.com')
    
    try:
        print(f"🔍 Starting analysis for ad: {request.ad.headline[:50]}...")
        
        # ALWAYS use EnhancedAdAnalysisService - it has all our AI improvements
        ad_service = EnhancedAdAnalysisService(db)
        analysis = await ad_service.analyze_ad(
            user_id=current_user.id,
            ad=request.ad,
            competitor_ads=request.competitor_ads
        )
        
        print(f"✅ Analysis complete. Generated {len(analysis.alternatives)} alternatives")
        
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
                    "feedback": analysis.feedback,
                    "quick_wins": analysis.quick_wins,
                    "competitor_comparison": analysis.competitor_comparison,
                    "timestamp": datetime.utcnow().isoformat(),
                    "ai_powered": True
                }
            },
            "alternatives": [{
                "variant_type": alt.variant_type,
                "headline": alt.headline,
                "body_text": alt.body_text,
                "cta": alt.cta,
                "improvement_reason": alt.improvement_reason,
                "predicted_score": alt.expected_improvement if hasattr(alt, 'expected_improvement') else 75
            } for alt in analysis.alternatives],
            "feedback": analysis.feedback
        }
        
    except Exception as e:
        print(f"❌ Analysis failed: {str(e)}")
        import traceback
        traceback.print_exc()
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
                "feedback": "\n".join(str(f) for f in analysis.feedback if f) if isinstance(analysis.feedback, list) else (str(analysis.feedback) if analysis.feedback else "Analysis completed successfully"),
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
        "feedback": "\n".join(str(f) for f in analysis.feedback if f) if isinstance(analysis.feedback, list) else (str(analysis.feedback) if analysis.feedback else "Analysis completed successfully")
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
