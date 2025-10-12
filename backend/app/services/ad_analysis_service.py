import uuid
from datetime import datetime
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
import openai
from app.core.config import settings
# Legacy analyzers replaced with Tools SDK
# from app.services.readability_analyzer import ReadabilityAnalyzer
# from app.services.emotion_analyzer import EmotionAnalyzer
# from app.services.cta_analyzer import CTAAnalyzer
from app.models.ad_analysis import AdAnalysis
from app.schemas.ads import AdInput, CompetitorAd, AdScore, AdAlternative, AdAnalysisResponse

class AdAnalysisService:
    """Main service for ad analysis and optimization"""
    
    def __init__(self, db: Session):
        self.db = db
        # Legacy analyzers removed - now using Tools SDK through main analysis service
        # Analysis functionality moved to main_launch_ready.py with Tools SDK integration
        
        # Initialize OpenAI
        if settings.OPENAI_API_KEY:
            openai.api_key = settings.OPENAI_API_KEY
    
    async def analyze_ad(self, user_id: int, ad: AdInput, 
                        competitor_ads: List[CompetitorAd] = []) -> AdAnalysisResponse:
        """Perform comprehensive ad analysis"""
        analysis_id = str(uuid.uuid4())
        
        # Combine all ad text for analysis
        full_text = f"{ad.headline} {ad.body_text} {ad.cta}"
        
        # DEPRECATED: Individual analyzers replaced with Tools SDK
        # Use main_launch_ready.py analyze_ad_internal() for full Tools SDK analysis
        # This method is kept for database operations but analysis logic moved
        
        # Placeholder analysis data - real analysis done through Tools SDK
        clarity_analysis = {'clarity_score': 75, 'recommendations': ['Use Tools SDK for analysis']}
        emotion_analysis = {'emotion_score': 70}
        cta_analysis = {'cta_strength_score': 68}
        
        # Calculate platform fit score
        platform_fit_score = self._calculate_platform_fit(ad)
        
        # Calculate overall score
        scores = AdScore(
            clarity_score=clarity_analysis['clarity_score'],
            persuasion_score=clarity_analysis.get('power_score', 70),
            emotion_score=emotion_analysis['emotion_score'],
            cta_strength=cta_analysis['cta_strength_score'],
            platform_fit_score=platform_fit_score,
            overall_score=self._calculate_overall_score(
                clarity_analysis['clarity_score'],
                clarity_analysis.get('power_score', 70),
                emotion_analysis['emotion_score'],
                cta_analysis['cta_strength_score'],
                platform_fit_score
            )
        )
        
        # Generate feedback
        feedback = self._generate_feedback(clarity_analysis, emotion_analysis, cta_analysis)
        
        # Generate alternatives
        alternatives = await self._generate_alternatives(ad)
        
        # Competitor comparison (if provided)
        competitor_comparison = None
        if competitor_ads:
            competitor_comparison = await self._analyze_competitors(ad, competitor_ads)
        
        # Quick wins
        quick_wins = self._generate_quick_wins(clarity_analysis, emotion_analysis, cta_analysis)
        
        # Save analysis to database
        analysis_record = AdAnalysis(
            id=analysis_id,
            user_id=user_id,
            headline=ad.headline,
            body_text=ad.body_text,
            cta=ad.cta,
            platform=ad.platform,
            overall_score=scores.overall_score,
            clarity_score=scores.clarity_score,
            persuasion_score=scores.persuasion_score,
            emotion_score=scores.emotion_score,
            cta_strength_score=scores.cta_strength,
            platform_fit_score=scores.platform_fit_score,
            analysis_data={
                'clarity_analysis': clarity_analysis,
                'emotion_analysis': emotion_analysis,
                'cta_analysis': cta_analysis,
                'alternatives': [alt.dict() for alt in alternatives]
            },
            created_at=datetime.utcnow()
        )
        self.db.add(analysis_record)
        self.db.commit()
        
        return AdAnalysisResponse(
            analysis_id=analysis_id,
            scores=scores,
            feedback=feedback,
            alternatives=alternatives,
            competitor_comparison=competitor_comparison,
            quick_wins=quick_wins
        )
    
    def _calculate_platform_fit(self, ad: AdInput) -> float:
        """Calculate how well the ad fits the target platform"""
        platform_scores = {
            'facebook': self._score_facebook_fit(ad),
            'google': self._score_google_fit(ad),
            'linkedin': self._score_linkedin_fit(ad),
            'tiktok': self._score_tiktok_fit(ad)
        }
        
        return platform_scores.get(ad.platform, 75.0)
    
    def _score_facebook_fit(self, ad: AdInput) -> float:
        """Score ad fit for Facebook platform"""
        score = 75  # Base score
        
        # Ideal headline length: 5-7 words
        headline_words = len(ad.headline.split())
        if 5 <= headline_words <= 7:
            score += 15
        elif headline_words > 10:
            score -= 10
        
        # Body text length: 90-125 characters ideal
        body_length = len(ad.body_text)
        if 90 <= body_length <= 125:
            score += 10
        elif body_length > 200:
            score -= 15
        
        return min(100, score)
    
    def _score_google_fit(self, ad: AdInput) -> float:
        """Score ad fit for Google Ads platform"""
        score = 75
        
        # Headlines should be 30 characters or less
        if len(ad.headline) <= 30:
            score += 20
        elif len(ad.headline) > 40:
            score -= 15
        
        # Description should be under 90 characters
        if len(ad.body_text) <= 90:
            score += 15
        
        return min(100, score)
    
    def _score_linkedin_fit(self, ad: AdInput) -> float:
        """Score ad fit for LinkedIn platform"""
        score = 75
        
        # Professional tone check (simplified)
        professional_words = ['professional', 'business', 'career', 'industry', 'expertise']
        if any(word in ad.body_text.lower() for word in professional_words):
            score += 15
        
        # Longer text acceptable on LinkedIn
        if len(ad.body_text) > 150:
            score += 10
        
        return min(100, score)
    
    def _score_tiktok_fit(self, ad: AdInput) -> float:
        """Score ad fit for TikTok platform"""
        score = 75
        
        # Very short text preferred
        total_length = len(ad.headline + ad.body_text)
        if total_length <= 80:
            score += 25
        elif total_length > 150:
            score -= 20
        
        # Casual tone preferred
        casual_indicators = ['!', 'wow', 'amazing', 'incredible']
        if any(indicator in ad.body_text.lower() for indicator in casual_indicators):
            score += 10
        
        return min(100, score)
    
    def _calculate_overall_score(self, clarity: float, persuasion: float, 
                                emotion: float, cta: float, platform_fit: float) -> float:
        """Calculate weighted overall score"""
        weights = {
            'clarity': 0.2,
            'persuasion': 0.25,
            'emotion': 0.2,
            'cta': 0.25,
            'platform_fit': 0.1
        }
        
        overall = (
            clarity * weights['clarity'] +
            persuasion * weights['persuasion'] +
            emotion * weights['emotion'] +
            cta * weights['cta'] +
            platform_fit * weights['platform_fit']
        )
        
        return round(overall, 1)
    
    def _generate_feedback(self, clarity_analysis: Dict, emotion_analysis: Dict, 
                          cta_analysis: Dict) -> str:
        """Generate human-readable feedback"""
        feedback_parts = []
        
        # Clarity feedback
        if clarity_analysis['clarity_score'] < 70:
            feedback_parts.append("Your ad copy could be clearer and easier to read.")
        
        # Emotion feedback
        if emotion_analysis['emotion_score'] < 60:
            feedback_parts.append("Consider adding more emotional triggers to connect with your audience.")
        
        # CTA feedback
        if cta_analysis['cta_strength_score'] < 70:
            feedback_parts.append("Your call-to-action needs to be stronger and more compelling.")
        
        if not feedback_parts:
            feedback_parts.append("Your ad has good fundamentals but can still be optimized.")
        
        return " ".join(feedback_parts)
    
    async def _generate_alternatives(self, ad: AdInput) -> List[AdAlternative]:
        """Generate alternative ad variations using AI"""
        alternatives = []
        
        # Try to use OpenAI for generation
        if settings.OPENAI_API_KEY:
            alternatives = await self._generate_ai_alternatives(ad)
        
        # Fallback to template-based alternatives
        if not alternatives:
            alternatives = self._generate_template_alternatives(ad)
        
        return alternatives
    
    async def _generate_ai_alternatives(self, ad: AdInput) -> List[AdAlternative]:
        """Generate alternatives using OpenAI"""
        try:
            prompts = [
                f"Rewrite this ad to be more persuasive and action-oriented: Headline: {ad.headline}, Body: {ad.body_text}, CTA: {ad.cta}",
                f"Rewrite this ad with stronger emotional appeal: Headline: {ad.headline}, Body: {ad.body_text}, CTA: {ad.cta}",
                f"Rewrite this ad with more data/stats focus: Headline: {ad.headline}, Body: {ad.body_text}, CTA: {ad.cta}",
                f"Optimize this ad for {ad.platform} platform: Headline: {ad.headline}, Body: {ad.body_text}, CTA: {ad.cta}"
            ]
            
            alternatives = []
            variant_types = ['persuasive', 'emotional', 'stats_heavy', 'platform_optimized']
            
            for i, prompt in enumerate(prompts):
                try:
                    response = await openai.ChatCompletion.acreate(
                        model="gpt-3.5-turbo",
                        messages=[{"role": "user", "content": prompt}],
                        max_tokens=200
                    )
                    
                    content = response.choices[0].message.content
                    # Parse response (simplified - would need better parsing)
                    lines = content.split('\n')
                    headline = lines[0] if lines else ad.headline
                    body = lines[1] if len(lines) > 1 else ad.body_text
                    cta = lines[-1] if len(lines) > 2 else ad.cta
                    
                    alternatives.append(AdAlternative(
                        variant_type=variant_types[i],
                        headline=headline.strip(),
                        body_text=body.strip(),
                        cta=cta.strip(),
                        improvement_reason=f"Optimized for {variant_types[i]} approach"
                    ))
                except Exception:
                    continue
            
            return alternatives
        except Exception:
            return []
    
    def _generate_template_alternatives(self, ad: AdInput) -> List[AdAlternative]:
        """Generate template-based alternatives as fallback"""
        return [
            AdAlternative(
                variant_type="persuasive",
                headline=f"Proven: {ad.headline}",
                body_text=f"Join thousands who already {ad.body_text.lower()}",
                cta="Get Started Now",
                improvement_reason="Added social proof and urgency"
            ),
            AdAlternative(
                variant_type="emotional",
                headline=f"Transform Your {ad.headline}",
                body_text=f"Imagine {ad.body_text}",
                cta="Claim Your Success",
                improvement_reason="Enhanced emotional appeal"
            )
        ]
    
    async def _analyze_competitors(self, user_ad: AdInput, 
                                 competitor_ads: List[CompetitorAd]) -> Dict[str, Any]:
        """Analyze user ad against competitors"""
        # Simplified competitor analysis
        competitor_scores = []
        
        for comp_ad in competitor_ads:
            comp_text = f"{comp_ad.headline} {comp_ad.body_text} {comp_ad.cta}"
            comp_clarity = self.readability_analyzer.analyze_clarity(comp_text)
            comp_emotion = self.emotion_analyzer.analyze_emotion(comp_text)
            comp_cta = self.cta_analyzer.analyze_cta(comp_ad.cta, comp_ad.platform)
            
            competitor_scores.append({
                'competitor_text': comp_text[:100] + "...",
                'overall_score': (comp_clarity['clarity_score'] + 
                                comp_emotion['emotion_score'] + 
                                comp_cta['cta_strength_score']) / 3
            })
        
        avg_competitor_score = sum(comp['overall_score'] for comp in competitor_scores) / len(competitor_scores)
        
        return {
            'average_competitor_score': avg_competitor_score,
            'competitor_count': len(competitor_ads),
            'performance_comparison': "above_average" if avg_competitor_score > 70 else "below_average"
        }
    
    def _generate_quick_wins(self, clarity_analysis: Dict, emotion_analysis: Dict, 
                            cta_analysis: Dict) -> List[str]:
        """Generate quick improvement suggestions"""
        quick_wins = []
        
        # Combine recommendations from all analyzers
        all_recommendations = []
        all_recommendations.extend(clarity_analysis.get('recommendations', []))
        all_recommendations.extend(emotion_analysis.get('recommendations', []))
        all_recommendations.extend(cta_analysis.get('recommendations', []))
        
        # Return top 3 most impactful recommendations
        return all_recommendations[:3]
    
    def get_user_analysis_history(self, user_id: int, limit: int = 10, offset: int = 0) -> List[Dict]:
        """Get user's analysis history"""
        analyses = self.db.query(AdAnalysis)\
                          .filter(AdAnalysis.user_id == user_id)\
                          .order_by(AdAnalysis.created_at.desc())\
                          .offset(offset)\
                          .limit(limit)\
                          .all()
        
        return [
            {
                'id': analysis.id,
                'headline': analysis.headline,
                'platform': analysis.platform,
                'overall_score': analysis.overall_score,
                'created_at': analysis.created_at.isoformat()
            }
            for analysis in analyses
        ]
    
    def get_analysis_by_id(self, analysis_id: str, user_id: int) -> Optional[Dict]:
        """Get specific analysis by ID"""
        analysis = self.db.query(AdAnalysis)\
                          .filter(AdAnalysis.id == analysis_id, AdAnalysis.user_id == user_id)\
                          .first()
        
        if not analysis:
            return None
        
        return {
            'id': analysis.id,
            'headline': analysis.headline,
            'body_text': analysis.body_text,
            'cta': analysis.cta,
            'platform': analysis.platform,
            'scores': {
                'overall_score': analysis.overall_score,
                'clarity_score': analysis.clarity_score,
                'persuasion_score': analysis.persuasion_score,
                'emotion_score': analysis.emotion_score,
                'cta_strength': analysis.cta_strength_score,
                'platform_fit_score': analysis.platform_fit_score
            },
            'analysis_data': analysis.analysis_data,
            'created_at': analysis.created_at.isoformat()
        }
    
    async def generate_ad_alternatives(self, ad: AdInput) -> List[AdAlternative]:
        """Generate alternative variations for an ad"""
        return await self._generate_alternatives(ad)
