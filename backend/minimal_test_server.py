#!/usr/bin/env python3
"""
Minimal test server to isolate the 404/403 issue
"""
import os
# Prevent accidental use in production: use main_production instead
if os.getenv("ENVIRONMENT", "").lower() == "production":
    raise SystemExit("Deprecated entrypoint: use 'uvicorn main_production:app' for production")
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import os
from datetime import datetime

# Create minimal FastAPI app
app = FastAPI(
    title="AdCopySurge API Test",
    description="Minimal test server",
    version="1.0.0"
)

# Simple CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all for testing
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

class AdScore(BaseModel):
    overall_score: float
    clarity_score: float
    persuasion_score: float
    emotion_score: float
    cta_strength: float
    platform_fit_score: float

class AdAnalysisResponse(BaseModel):
    analysis_id: str
    scores: AdScore
    feedback: str

# Routes
@app.get("/")
async def root():
    return {"message": "Minimal test server running", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

@app.post("/api/ads/comprehensive-analyze")
async def comprehensive_analyze_ad(request: dict):
    """Test comprehensive analysis endpoint"""
    try:
        ad_copy = request.get('ad_copy', '')
        platform = request.get('platform', 'facebook')
        
        if not ad_copy:
            raise HTTPException(status_code=400, detail="ad_copy is required")
        
        # Mock response
        return {
            "original": {
                "copy": ad_copy,
                "score": 65.0
            },
            "improved": {
                "copy": "Enhanced: " + ad_copy,
                "score": 80.0,
                "improvements": [
                    {"category": "Headline", "description": "Enhanced for better engagement"},
                    {"category": "CTA", "description": "Optimized call-to-action"}
                ]
            },
            "compliance": {"status": "COMPLIANT", "totalIssues": 0, "issues": []},
            "psychology": {"overallScore": 72, "topOpportunity": "Add social proof"},
            "platform": platform
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@app.post("/api/ads/analyze", response_model=AdAnalysisResponse)
async def analyze_ad(ad_input: AdInput):
    """Test regular analysis endpoint"""
    try:
        # Mock analysis
        scores = AdScore(
            overall_score=72.5,
            clarity_score=75.0,
            persuasion_score=70.0,
            emotion_score=68.0,
            cta_strength=80.0,
            platform_fit_score=72.0
        )
        
        return AdAnalysisResponse(
            analysis_id=f"test_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            scores=scores,
            feedback="Mock analysis completed successfully"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)