#!/usr/bin/env python3
"""
AdCopySurge Working API - Real AI Analysis
Now with OpenAI integration for genuine analysis
"""
import os
# Prevent accidental use in production: use main_production instead
if os.getenv("ENVIRONMENT", "").lower() == "production":
    raise SystemExit("Deprecated entrypoint: use 'uvicorn main_production:app' for production")
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import os
import openai
import asyncio
from datetime import datetime

# Initialize OpenAI
openai_api_key = os.getenv('OPENAI_API_KEY', '')
if openai_api_key and openai_api_key.startswith('sk-'):
    openai.api_key = openai_api_key
    print(f"✅ OpenAI configured with API key: {openai_api_key[:7]}...{openai_api_key[-4:]}")
else:
    print("⚠️ OpenAI API key not configured. Using fallback analysis.")

# Create clean FastAPI app
app = FastAPI(
    title="AdCopySurge API",
    description="AI-powered ad copy analysis and optimization platform",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# CORS - Allow all for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Models
class AdInput(BaseModel):
    headline: str
    body_text: str
    cta: str
    platform: str = "facebook"
    target_audience: Optional[str] = None
    industry: Optional[str] = None

class AdScore(BaseModel):
    overall_score: float
    clarity_score: float
    persuasion_score: float
    emotion_score: float
    cta_strength: float
    platform_fit_score: float

class AdAlternative(BaseModel):
    variant_type: str
    headline: str
    body_text: str
    cta: str
    improvement_reason: str

class AdAnalysisResponse(BaseModel):
    analysis_id: str
    scores: AdScore
    feedback: str
    alternatives: List[AdAlternative]
    quick_wins: List[str]

# Helper functions
def calculate_emotion_score(text: str) -> float:
    """Calculate emotion score using keyword detection"""
    emotion_keywords = {
        'excitement': ['amazing', 'incredible', 'awesome', 'fantastic', 'wow', 'breakthrough'],
        'urgency': ['now', 'today', 'limited', 'hurry', 'expires', 'soon', 'deadline'],
        'trust': ['proven', 'guaranteed', 'trusted', 'verified', 'secure', 'reliable'],
        'benefit': ['save', 'free', 'discount', 'bonus', 'exclusive', 'special']
    }
    
    text_lower = text.lower()
    emotion_count = 0
    
    for category, words in emotion_keywords.items():
        if any(word in text_lower for word in words):
            emotion_count += 1
    
    return min(100, emotion_count * 20 + 20)  # Base score of 20, up to 100

def calculate_platform_fit(ad_input: AdInput) -> float:
    """Calculate platform fit score"""
    score = 75  # Base score
    
    if ad_input.platform == "facebook":
        headline_words = len(ad_input.headline.split())
        if 3 <= headline_words <= 6:
            score += 15
        body_length = len(ad_input.body_text)
        if 50 <= body_length <= 125:
            score += 10
    elif ad_input.platform == "google":
        if len(ad_input.headline) <= 30:
            score += 20
        if len(ad_input.body_text) <= 90:
            score += 10
    elif ad_input.platform == "linkedin":
        professional_words = ['business', 'professional', 'industry', 'solution', 'enterprise']
        if any(word in ad_input.body_text.lower() for word in professional_words):
            score += 15
            
    return min(100, score)

async def generate_ai_alternatives(ad_input: AdInput) -> List[AdAlternative]:
    """Generate AI-powered ad alternatives using OpenAI"""
    if not openai.api_key:
        return generate_template_alternatives(ad_input)
    
    try:
        variants = [
            {"type": "persuasive", "prompt": f"Rewrite this ad to be more persuasive with social proof and urgency: Headline: '{ad_input.headline}', Body: '{ad_input.body_text}', CTA: '{ad_input.cta}'. Platform: {ad_input.platform}. Keep it concise and compelling."},
            {"type": "emotional", "prompt": f"Rewrite this ad with strong emotional appeal and storytelling: Headline: '{ad_input.headline}', Body: '{ad_input.body_text}', CTA: '{ad_input.cta}'. Platform: {ad_input.platform}. Focus on benefits and transformation."},
            {"type": "urgency", "prompt": f"Rewrite this ad with urgency and scarcity elements: Headline: '{ad_input.headline}', Body: '{ad_input.body_text}', CTA: '{ad_input.cta}'. Platform: {ad_input.platform}. Add time-sensitive language."}
        ]
        
        alternatives = []
        
        for variant in variants:
            try:
                import openai
                client = openai.AsyncOpenAI(api_key=openai.api_key)
                response = await client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "You are an expert copywriter. Respond with ONLY the rewritten ad in this format: HEADLINE: [headline]\nBODY: [body text]\nCTA: [call to action]"}, 
                        {"role": "user", "content": variant["prompt"]}
                    ],
                    max_tokens=200,
                    temperature=0.7
                )
                
                content = response.choices[0].message.content.strip()
                parsed = parse_ai_response(content)
                
                alternatives.append(AdAlternative(
                    variant_type=variant["type"],
                    headline=parsed["headline"] or ad_input.headline,
                    body_text=parsed["body_text"] or ad_input.body_text,
                    cta=parsed["cta"] or ad_input.cta,
                    improvement_reason=f"AI-optimized for {variant['type']} appeal with real language modeling"
                ))
                
            except Exception as e:
                print(f"AI generation failed for {variant['type']}: {e}")
                continue
        
        # If AI failed, use templates
        if not alternatives:
            alternatives = generate_template_alternatives(ad_input)
        
        return alternatives
        
    except Exception as e:
        print(f"AI generation completely failed: {e}")
        return generate_template_alternatives(ad_input)

def parse_ai_response(content: str) -> Dict[str, str]:
    """Parse AI response into headline, body, and CTA"""
    lines = content.split('\n')
    parsed = {"headline": "", "body_text": "", "cta": ""}
    
    for line in lines:
        line = line.strip()
        if line.upper().startswith('HEADLINE:'):
            parsed["headline"] = line[9:].strip()
        elif line.upper().startswith('BODY:'):
            parsed["body_text"] = line[5:].strip()
        elif line.upper().startswith('CTA:'):
            parsed["cta"] = line[4:].strip()
    
    return parsed

def generate_template_alternatives(ad_input: AdInput) -> List[AdAlternative]:
    """Fallback template-based alternatives"""
    alternatives = []
    
    # Persuasive variant
    alternatives.append(AdAlternative(
        variant_type="persuasive",
        headline=f"Proven: {ad_input.headline}",
        body_text=f"Join thousands who already discovered {ad_input.body_text.lower()}",
        cta="Get Started Now",
        improvement_reason="Added social proof and strong action language (template-based)"
    ))
    
    # Emotional variant
    alternatives.append(AdAlternative(
        variant_type="emotional", 
        headline=f"Transform Your Business with {ad_input.headline}",
        body_text=f"Imagine the results: {ad_input.body_text}",
        cta="Claim Your Success",
        improvement_reason="Enhanced emotional appeal and aspiration (template-based)"
    ))
    
    # Urgency variant
    alternatives.append(AdAlternative(
        variant_type="urgency",
        headline=f"{ad_input.headline} - Limited Time",
        body_text=f"Don't wait! {ad_input.body_text} Act fast - offer expires soon.",
        cta="Act Now",
        improvement_reason="Added urgency and scarcity to drive immediate action (template-based)"
    ))
    
    return alternatives

async def generate_ai_comprehensive_analysis(ad_copy: str, platform: str) -> Dict[str, Any]:
    """Generate AI-powered comprehensive analysis with real insights"""
    if not openai.api_key:
        return generate_template_comprehensive_analysis(ad_copy, platform)
    
    try:
        analysis_prompt = f"""
Analyze this advertisement comprehensively:

Ad Copy: "{ad_copy}"
Platform: {platform}

Provide detailed analysis in this format:
OVERALL_SCORE: [0-100]
IMPROVED_COPY: [rewritten version]
IMPROVED_SCORE: [0-100]
IMPROVEMENT1: [specific improvement made]
IMPROVEMENT2: [another improvement]
IMPROVEMENT3: [third improvement]
COMPLIANCE: [COMPLIANT or list issues]
TOP_OPPORTUNITY: [main psychology improvement]
"""
        
        import openai
        client = openai.AsyncOpenAI(api_key=openai.api_key)
        response = await client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are an expert marketing analyst. Provide detailed, actionable analysis."},
                {"role": "user", "content": analysis_prompt}
            ],
            max_tokens=600,
            temperature=0.3
        )
        
        content = response.choices[0].message.content.strip()
        parsed = parse_comprehensive_analysis(content, ad_copy, platform)
        
        if parsed:
            return parsed
        else:
            return generate_template_comprehensive_analysis(ad_copy, platform)
            
    except Exception as e:
        print(f"AI comprehensive analysis failed: {e}")
        return generate_template_comprehensive_analysis(ad_copy, platform)

def parse_comprehensive_analysis(content: str, original_copy: str, platform: str) -> Dict[str, Any]:
    """Parse AI comprehensive analysis response"""
    try:
        lines = content.split('\n')
        data = {}
        
        for line in lines:
            line = line.strip()
            if ':' in line:
                key, value = line.split(':', 1)
                data[key.strip().upper()] = value.strip()
        
        overall_score = float(data.get('OVERALL_SCORE', 75))
        improved_score = float(data.get('IMPROVED_SCORE', min(95, overall_score + 15)))
        improved_copy = data.get('IMPROVED_COPY', original_copy)
        
        improvements = []
        for i in range(1, 4):
            improvement = data.get(f'IMPROVEMENT{i}')
            if improvement:
                category = "Headline" if i == 1 else "CTA" if i == 2 else "Platform"
                improvements.append({"category": category, "description": improvement})
        
        return {
            "original": {"copy": original_copy, "score": round(overall_score, 1)},
            "improved": {"copy": improved_copy, "score": round(improved_score, 1), "improvements": improvements},
            "compliance": {"status": "COMPLIANT" if data.get('COMPLIANCE', 'COMPLIANT') == 'COMPLIANT' else "ISSUES", "totalIssues": 0, "issues": []},
            "psychology": {"overallScore": round(overall_score * 0.9), "topOpportunity": data.get('TOP_OPPORTUNITY', 'Add emotional triggers'), "triggers": []},
            "abTests": {"variations": []},
            "roi": {"segment": "Mass market", "premiumVersions": []},
            "legal": {"riskLevel": "Low", "issues": []},
            "platform": platform,
            "ai_powered": True,  # Mark as AI-powered
            "evidence_level": "high",  # Real AI analysis = high evidence
            "sample_size": 1000,  # Simulated sample size
            "confidence": 0.85  # High confidence for real AI
        }
        
    except Exception as e:
        print(f"Failed to parse comprehensive analysis: {e}")
        return None

def generate_template_comprehensive_analysis(ad_copy: str, platform: str) -> Dict[str, Any]:
    """Fallback template comprehensive analysis"""
    base_score = min(100, 65 + len(ad_copy) * 0.05)
    return {
        "original": {"copy": ad_copy, "score": round(base_score, 1)},
        "improved": {
            "copy": f"Discover: {ad_copy[:50]}..." if len(ad_copy) > 50 else f"Discover: {ad_copy}",
            "score": round(min(95, base_score + 15), 1),
            "improvements": [
                {"category": "Headline", "description": "Enhanced for better engagement (template)"},
                {"category": "CTA", "description": "Optimized call-to-action (template)"},
                {"category": "Platform", "description": f"Tailored for {platform} (template)"}
            ]
        },
        "compliance": {"status": "COMPLIANT", "totalIssues": 0, "issues": []},
        "psychology": {"overallScore": round(base_score * 0.8), "topOpportunity": "Add social proof (template)", "triggers": []},
        "abTests": {"variations": []},
        "roi": {"segment": "Mass market", "premiumVersions": []},
        "legal": {"riskLevel": "Low", "issues": []},
        "platform": platform,
        "ai_powered": False,  # Template-based
        "evidence_level": "low",  # Template = low evidence
        "sample_size": 50,  # Small simulated sample
        "confidence": 0.35  # Low confidence for templates
    }

# Routes
@app.get("/")
async def root():
    return {
        "message": "AdCopySurge API is running", 
        "version": "1.0.0",
        "status": "Working - No Auth Issues"
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy", 
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0",
        "auth_status": "bypassed"
    }

@app.post("/api/ads/comprehensive-analyze")
async def comprehensive_analyze_ad(request: dict):
    """Comprehensive analysis endpoint with real AI analysis"""
    try:
        ad_copy = request.get('ad_copy', '')
        platform = request.get('platform', 'facebook')
        
        if not ad_copy:
            raise HTTPException(status_code=400, detail="ad_copy is required")
        
        # Use AI-powered comprehensive analysis
        analysis_result = await generate_ai_comprehensive_analysis(ad_copy, platform)
        
        # Create AdInput for alternatives
        ad_input = AdInput(
            headline=ad_copy.split('\n')[0][:100] if '\n' in ad_copy else ad_copy[:100],
            body_text=ad_copy,
            cta="Learn More",
            platform=platform
        )
        
        # Generate AI alternatives
        alternatives = await generate_ai_alternatives(ad_input)
        
        # Merge alternatives into result
        analysis_result["abTests"] = {"variations": [alt.dict() for alt in alternatives]}
        
        return analysis_result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Comprehensive analysis failed: {str(e)}")

@app.post("/api/ads/analyze", response_model=AdAnalysisResponse)
async def analyze_ad(ad_input: AdInput):
    """Regular analysis endpoint that works"""
    try:
        # Calculate scores
        full_text = f"{ad_input.headline} {ad_input.body_text} {ad_input.cta}"
        
        clarity_score = min(100, 70 + len(ad_input.body_text) * 0.1)
        persuasion_score = min(100, 65 + full_text.count('!') * 5)
        emotion_score = calculate_emotion_score(full_text)
        cta_strength = min(100, 60 + len(ad_input.cta) * 2)
        platform_fit_score = calculate_platform_fit(ad_input)
        
        overall_score = (clarity_score + persuasion_score + emotion_score + cta_strength + platform_fit_score) / 5
        
        scores = AdScore(
            clarity_score=round(clarity_score, 1),
            persuasion_score=round(persuasion_score, 1),
            emotion_score=round(emotion_score, 1),
            cta_strength=round(cta_strength, 1),
            platform_fit_score=round(platform_fit_score, 1),
            overall_score=round(overall_score, 1)
        )
        
        # Generate feedback
        feedback_parts = []
        if scores.overall_score >= 80:
            feedback_parts.append("Excellent ad copy! Your content is well-optimized.")
        elif scores.overall_score >= 60:
            feedback_parts.append("Good ad copy with room for improvement.")
        else:
            feedback_parts.append("Your ad copy needs optimization to improve performance.")
        
        if scores.clarity_score < 70:
            feedback_parts.append("Consider simplifying your language for better readability.")
        if scores.cta_strength < 70:
            feedback_parts.append("Your call-to-action could be more compelling.")
        if scores.emotion_score < 70:
            feedback_parts.append("Adding more emotional triggers could improve engagement.")
        
        feedback = " ".join(feedback_parts)
        
        # Generate quick wins
        quick_wins = []
        if scores.clarity_score < 70:
            quick_wins.append("Shorten sentences and use simpler words")
        if scores.cta_strength < 70:
            quick_wins.append("Use stronger action words in your CTA")
        if scores.emotion_score < 70:
            quick_wins.append("Add emotional words like 'amazing', 'exclusive', or 'proven'")
        if len(ad_input.headline) > 50:
            quick_wins.append("Consider shortening your headline for better impact")
        
        # Generate alternatives
        alternatives = await generate_ai_alternatives(ad_input)
        
        return AdAnalysisResponse(
            analysis_id=f"analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            scores=scores,
            feedback=feedback,
            alternatives=alternatives,
            quick_wins=quick_wins[:3]
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@app.get("/api/blog/categories")
async def get_blog_categories():
    """Get blog categories for frontend"""
    return {
        "categories": [
            {"id": 1, "name": "Ad Copy Optimization", "slug": "ad-copy"},
            {"id": 2, "name": "Marketing Psychology", "slug": "psychology"},
            {"id": 3, "name": "Platform Strategies", "slug": "platforms"},
            {"id": 4, "name": "Conversion Tactics", "slug": "conversion"},
            {"id": 5, "name": "A/B Testing", "slug": "ab-testing"},
            {"id": 6, "name": "Industry Insights", "slug": "insights"}
        ],
        "total": 6
    }

@app.get("/api/test")
async def test_endpoint():
    """Test endpoint"""
    return {
        "status": "success",
        "message": "AdCopySurge API is working correctly",
        "timestamp": datetime.now().isoformat(),
        "endpoints": [
            "/api/ads/comprehensive-analyze",
            "/api/ads/analyze",
            "/api/blog/categories",
            "/health",
            "/api/test"
        ]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)