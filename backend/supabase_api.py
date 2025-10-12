#!/usr/bin/env python3
"""
AdCopySurge Supabase-Integrated API
Real backend with Supabase database integration for dashboard metrics
"""
from fastapi import FastAPI, HTTPException, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import os
import asyncpg
import json
from datetime import datetime
from supabase import create_client, Client
import jwt
import asyncio
from contextlib import asynccontextmanager

# Environment variables
SUPABASE_URL = os.getenv('SUPABASE_URL', '')
SUPABASE_SERVICE_KEY = os.getenv('SUPABASE_SERVICE_ROLE_KEY', '')  # Service role key for admin operations
SUPABASE_ANON_KEY = os.getenv('SUPABASE_ANON_KEY', '')
JWT_SECRET = os.getenv('SUPABASE_JWT_SECRET', '')

if not SUPABASE_URL or not SUPABASE_SERVICE_KEY:
    print("⚠️  WARNING: Supabase credentials not found in environment variables")
    print("Set SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY environment variables")

# Initialize Supabase client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)

# Database connection pool
db_pool = None

async def init_db_pool():
    """Initialize database connection pool"""
    global db_pool
    if db_pool is None:
        # Extract database connection details from Supabase URL
        # Format: postgresql://postgres:[password]@[host]:5432/postgres
        db_url = SUPABASE_URL.replace('https://', '').replace('.supabase.co', '.supabase.co')
        
        # For Supabase, use direct PostgreSQL connection
        # You'll need to get your direct database URL from Supabase Dashboard > Settings > Database
        print("⚠️  Note: You need to set up direct PostgreSQL connection")
        print("Go to Supabase Dashboard > Settings > Database > Connection string (Direct connection)")
        
        # For now, we'll use the Supabase client instead of direct PostgreSQL
        # This is less efficient but works without additional configuration
        return None

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await init_db_pool()
    yield
    # Shutdown
    if db_pool:
        await db_pool.close()

# Create FastAPI app
app = FastAPI(
    title="AdCopySurge Supabase API",
    description="Real AI-powered ad copy analysis with Supabase integration",
    version="2.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    lifespan=lifespan
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Models
class AdAnalysisCreate(BaseModel):
    headline: str
    body_text: str
    cta: str
    platform: str = "facebook"
    target_audience: Optional[str] = None
    industry: Optional[str] = None

# Authentication helper
async def get_current_user(authorization: str = Header(None)) -> str:
    """Extract user ID from JWT token"""
    if not authorization:
        raise HTTPException(status_code=401, detail="Authorization header missing")
    
    try:
        # Remove 'Bearer ' prefix
        token = authorization.replace('Bearer ', '')
        
        # Decode JWT token
        payload = jwt.decode(token, JWT_SECRET, algorithms=['HS256'], options={"verify_aud": False})
        user_id = payload.get('sub')
        
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid token: no user ID")
        
        return user_id
        
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError as e:
        raise HTTPException(status_code=401, detail=f"Invalid token: {str(e)}")

# Dashboard Metrics Endpoints
@app.get("/api/dashboard/metrics")
async def get_dashboard_metrics(
    period_days: int = 30,
    user_id: str = Depends(get_current_user)
) -> Dict[str, Any]:
    """Get dashboard metrics for the current user"""
    try:
        # Call the Supabase function
        result = supabase.rpc('get_dashboard_metrics', {
            'p_user_id': user_id,
            'p_period_days': period_days
        }).execute()
        
        if result.data is None:
            # Return empty metrics for new users
            return {
                "adsAnalyzed": 0,
                "adsAnalyzedChange": 0,
                "avgImprovement": 0,
                "avgImprovementChange": 0,
                "avgScore": 0,
                "avgScoreChange": 0,
                "topPerforming": 0,
                "topPerformingChange": 0,
                "periodStart": (datetime.now().replace(microsecond=0) - 
                               datetime.timedelta(days=period_days)).isoformat(),
                "periodEnd": datetime.now().replace(microsecond=0).isoformat(),
                "periodDays": period_days
            }
        
        return result.data
        
    except Exception as e:
        print(f"Error fetching dashboard metrics: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch dashboard metrics: {str(e)}")

@app.get("/api/dashboard/metrics/summary")
async def get_metrics_summary(
    user_id: str = Depends(get_current_user)
) -> Dict[str, Any]:
    """Get high-level summary metrics for the user"""
    try:
        # Call the Supabase function
        result = supabase.rpc('get_summary_metrics', {
            'p_user_id': user_id
        }).execute()
        
        if result.data is None:
            # Return empty metrics for new users
            return {
                "totalAnalyses": 0,
                "lifetimeAvgScore": 0,
                "bestScore": 0,
                "analysesLast30Days": 0,
                "platformsUsed": 0,
                "projectsCount": 0,
                "firstAnalysisDate": None,
                "lastAnalysisDate": None,
                "isNewUser": True
            }
        
        return result.data
        
    except Exception as e:
        print(f"Error fetching summary metrics: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch summary metrics: {str(e)}")

@app.get("/api/dashboard/metrics/detailed")
async def get_detailed_metrics(
    period_days: int = 30,
    user_id: str = Depends(get_current_user)
) -> Dict[str, Any]:
    """Get detailed dashboard metrics with breakdowns"""
    try:
        # Get platform breakdown
        platform_result = supabase.table('ad_analyses').select(
            'platform, overall_score'
        ).eq('supabase_user_id', user_id).gte(
            'created_at', 
            (datetime.now() - datetime.timedelta(days=period_days)).isoformat()
        ).neq('overall_score', None).execute()
        
        # Process platform breakdown
        platform_data = {}
        for row in platform_result.data:
            platform = row['platform'] or 'Unknown'
            if platform not in platform_data:
                platform_data[platform] = {'count': 0, 'scores': []}
            platform_data[platform]['count'] += 1
            platform_data[platform]['scores'].append(row['overall_score'])
        
        platform_breakdown = [
            {
                'platform': platform,
                'count': data['count'],
                'avgScore': round(sum(data['scores']) / len(data['scores']), 1) if data['scores'] else 0
            }
            for platform, data in platform_data.items()
        ]
        
        # Get industry breakdown
        industry_result = supabase.table('ad_analyses').select(
            'industry, overall_score'
        ).eq('supabase_user_id', user_id).gte(
            'created_at',
            (datetime.now() - datetime.timedelta(days=period_days)).isoformat()
        ).neq('overall_score', None).execute()
        
        # Process industry breakdown
        industry_data = {}
        for row in industry_result.data:
            industry = row['industry'] or 'Unknown'
            if industry not in industry_data:
                industry_data[industry] = {'count': 0, 'scores': []}
            industry_data[industry]['count'] += 1
            industry_data[industry]['scores'].append(row['overall_score'])
        
        industry_breakdown = [
            {
                'industry': industry,
                'count': data['count'],
                'avgScore': round(sum(data['scores']) / len(data['scores']), 1) if data['scores'] else 0
            }
            for industry, data in sorted(industry_data.items(), key=lambda x: x[1]['count'], reverse=True)[:10]
        ]
        
        # Get score distribution
        all_scores = [row['overall_score'] for row in platform_result.data]
        score_distribution = []
        
        if all_scores:
            ranges = [
                ('Excellent (90-100)', 90, 100),
                ('Good (80-89)', 80, 89),
                ('Fair (70-79)', 70, 79),
                ('Poor (60-69)', 60, 69),
                ('Needs Improvement (<60)', 0, 59)
            ]
            
            for range_name, min_score, max_score in ranges:
                count = len([s for s in all_scores if min_score <= s <= max_score])
                if count > 0:
                    score_distribution.append({
                        'range': range_name,
                        'count': count
                    })
        
        # Get recent activity (last 7 days)
        recent_result = supabase.table('ad_analyses').select(
            'created_at, overall_score'
        ).eq('supabase_user_id', user_id).gte(
            'created_at',
            (datetime.now() - datetime.timedelta(days=7)).isoformat()
        ).neq('overall_score', None).execute()
        
        # Process recent activity by date
        daily_data = {}
        for row in recent_result.data:
            date = row['created_at'][:10]  # Extract YYYY-MM-DD
            if date not in daily_data:
                daily_data[date] = {'count': 0, 'scores': []}
            daily_data[date]['count'] += 1
            daily_data[date]['scores'].append(row['overall_score'])
        
        recent_activity = [
            {
                'date': date,
                'count': data['count'],
                'avgScore': round(sum(data['scores']) / len(data['scores']), 1) if data['scores'] else 0
            }
            for date, data in sorted(daily_data.items(), reverse=True)[:7]
        ]
        
        return {
            'platformBreakdown': platform_breakdown,
            'industryBreakdown': industry_breakdown,
            'scoreDistribution': score_distribution,
            'recentActivity': recent_activity
        }
        
    except Exception as e:
        print(f"Error fetching detailed metrics: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch detailed metrics: {str(e)}")

# Analysis endpoint that saves to database
@app.post("/api/ads/analyze")
async def analyze_ad(
    analysis: AdAnalysisCreate,
    user_id: str = Depends(get_current_user)
):
    """Analyze ad copy and save to database"""
    try:
        # Calculate scores (simplified for now)
        full_text = f"{analysis.headline} {analysis.body_text} {analysis.cta}"
        
        # Basic scoring algorithm
        clarity_score = min(100, 70 + len(analysis.body_text) * 0.1)
        persuasion_score = min(100, 65 + full_text.count('!') * 5)
        emotion_score = min(100, 60 + len([w for w in full_text.lower().split() 
                                          if w in ['amazing', 'incredible', 'exclusive', 'free', 'proven']]) * 10)
        cta_strength = min(100, 60 + len(analysis.cta) * 2)
        platform_fit_score = 75  # Base score
        
        overall_score = (clarity_score + persuasion_score + emotion_score + cta_strength + platform_fit_score) / 5
        
        # Generate feedback
        feedback = f"Your ad achieved an overall score of {overall_score:.1f}%. "
        if overall_score >= 80:
            feedback += "Excellent work! Your ad is well-optimized."
        elif overall_score >= 60:
            feedback += "Good foundation with room for improvement."
        else:
            feedback += "Consider optimizing for better performance."
        
        # Save to database
        result = supabase.table('ad_analyses').insert({
            'supabase_user_id': user_id,
            'platform': analysis.platform,
            'industry': analysis.industry,
            'headline': analysis.headline,
            'body_text': analysis.body_text,
            'cta': analysis.cta,
            'overall_score': round(overall_score, 2),
            'clarity_score': round(clarity_score, 2),
            'persuasion_score': round(persuasion_score, 2),
            'emotion_score': round(emotion_score, 2),
            'cta_strength': round(cta_strength, 2),
            'platform_fit_score': round(platform_fit_score, 2),
            'feedback': feedback,
            'analysis_metadata': {
                'version': '2.0.0',
                'timestamp': datetime.now().isoformat()
            }
        }).execute()
        
        return {
            'analysis_id': result.data[0]['id'],
            'scores': {
                'overall_score': round(overall_score, 1),
                'clarity_score': round(clarity_score, 1),
                'persuasion_score': round(persuasion_score, 1),
                'emotion_score': round(emotion_score, 1),
                'cta_strength': round(cta_strength, 1),
                'platform_fit_score': round(platform_fit_score, 1)
            },
            'feedback': feedback,
            'quick_wins': [
                "Add more emotional triggers",
                "Strengthen your call-to-action",
                "Optimize for platform-specific guidelines"
            ][:3]
        }
        
    except Exception as e:
        print(f"Error analyzing ad: {e}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

# Health check
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "2.0.0",
        "database": "supabase" if SUPABASE_URL else "not_configured"
    }

@app.get("/api/test")
async def test_endpoint():
    """Test endpoint"""
    return {
        "status": "success",
        "message": "AdCopySurge Supabase API is working correctly",
        "timestamp": datetime.now().isoformat(),
        "endpoints": [
            "/api/dashboard/metrics",
            "/api/dashboard/metrics/summary", 
            "/api/dashboard/metrics/detailed",
            "/api/ads/analyze",
            "/health",
            "/api/test"
        ]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)