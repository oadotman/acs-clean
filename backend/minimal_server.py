import os
# Prevent accidental use in production: use main_production instead
if os.getenv("ENVIRONMENT", "").lower() == "production":
    raise SystemExit("Deprecated entrypoint: use 'uvicorn main_production:app' for production")
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import uvicorn

app = FastAPI(title="AdCopySurge API - Minimal", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request/Response models
class AdAnalysisRequest(BaseModel):
    analysis_id: str
    ad: str
    competitor_ads: Optional[List[str]] = []
    user_id: str

class AdAnalysisResponse(BaseModel):
    scores: Dict[str, Any]
    alternatives: List[str]
    feedback: str

@app.get("/")
async def root():
    return {"message": "AdCopySurge API is running", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.post("/api/ads/analyze")
async def analyze_ad(request: AdAnalysisRequest):
    """
    Minimal ad analysis endpoint for testing
    """
    try:
        # Mock response to test connectivity
        mock_response = AdAnalysisResponse(
            scores={
                "overall_score": 7.5,
                "readability_score": 8.2,
                "emotion_score": 7.8,
                "cta_score": 6.9,
                "platform_optimization": {
                    "facebook": 8.0,
                    "google": 7.5,
                    "linkedin": 6.8,
                    "tiktok": 7.2
                }
            },
            alternatives=[
                "Test alternative 1 - This is a mock response to verify API connectivity",
                "Test alternative 2 - Your backend is now responding to requests",
                "Test alternative 3 - Connection issue has been resolved"
            ],
            feedback="This is a test response from your minimal backend server. The API is now responding correctly!"
        )
        
        return mock_response
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@app.get("/api/auth/me")
async def get_current_user():
    """Mock user endpoint"""
    return {
        "id": "test-user-123",
        "email": "test@example.com", 
        "subscription_tier": "free",
        "monthly_analyses": 1
    }

if __name__ == "__main__":
    uvicorn.run(
        "minimal_server:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
