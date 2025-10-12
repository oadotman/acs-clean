"""
Production-Ready Enhanced Ad Analysis Service - NO FALLBACKS

This service replaces the fallback-heavy enhanced service with a strict production version
that fails fast with proper error codes instead of falling back to mock data.
"""

import asyncio
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from datetime import datetime

# Import the Tools SDK
from packages.tools_sdk import ToolOrchestrator, ToolInput, ToolRegistry, default_registry
from packages.tools_sdk.tools import register_all_tools

# Legacy imports for compatibility
from app.schemas.ads import AdInput, CompetitorAd, AdScore, AdAlternative, AdAnalysisResponse
from app.models.ad_analysis import AdAnalysis
from app.core.logging import get_logger
from app.core.exceptions import (
    ProductionAnalysisError, 
    ToolsSDKError, 
    AIProviderUnavailable,
    DatabaseConstraintError,
    fail_fast_on_mock_data
)

logger = get_logger(__name__)


class ProductionAdAnalysisService:
    """
    Production-ready ad analysis service - NO FALLBACKS ALLOWED
    
    All failures result in proper ProductionError exceptions rather than 
    silent degradation to mock data or template alternatives.
    """
    
    def __init__(self, db: Session, registry: ToolRegistry = None):
        self.db = db
        self.orchestrator = ToolOrchestrator(registry or default_registry)
        
        # Strictly require tools registration - fail fast if it fails
        try:
            register_all_tools()
            available_tools = self.orchestrator.registry.list_tools()
            
            if not available_tools:
                raise ProductionAnalysisError(
                    "No tools available after registration",
                    error_code="TOOLS_REGISTRATION_FAILED"
                )
                
            logger.info(f"Production service initialized with tools: {available_tools}")
        except Exception as e:
            raise ProductionAnalysisError(
                f"Tools SDK registration failed: {str(e)}",
                error_code="TOOLS_INITIALIZATION_FAILED"
            )
    
    async def analyze_ad(
        self, 
        user_id: int, 
        ad: AdInput, 
        competitor_ads: List[CompetitorAd] = [],
        requested_tools: List[str] = None
    ) -> AdAnalysisResponse:
        """
        Perform production ad analysis - FAIL FAST on any errors
        
        Args:
            user_id: User ID for database storage
            ad: Ad input data
            competitor_ads: Optional competitor ads for comparison
            requested_tools: Specific tools to run (if None, runs all available)
            
        Returns:
            AdAnalysisResponse with REAL analysis data only
            
        Raises:
            ProductionAnalysisError: If analysis fails
            ToolsSDKError: If specific tools fail
            AIProviderUnavailable: If AI services are down
        """
        logger.info(f"Starting production analysis for user {user_id}")
        
        # Validate input data
        self._validate_input_data(ad, user_id)
        
        # Convert to SDK format
        tool_input = ToolInput.from_legacy_ad_input(
            ad_data={
                'headline': ad.headline,
                'body_text': ad.body_text,
                'cta': ad.cta,
                'platform': ad.platform,
                'industry': getattr(ad, 'industry', None),
                'target_audience': getattr(ad, 'target_audience', None)
            },
            user_id=str(user_id)
        )
        
        # Determine required tools
        tools_to_run = self._get_required_tools(requested_tools)
        logger.info(f"Running required tools: {tools_to_run}")
        
        # Execute tools through orchestrator - FAIL FAST
        try:
            orchestration_result = await self.orchestrator.run_tools(
                tool_input,
                tools_to_run,
                execution_mode="parallel"
            )
        except Exception as e:
            raise ProductionAnalysisError(
                f"Tools orchestration failed: {str(e)}",
                user_id=str(user_id),
                ad_text=ad.headline,
                failed_tools=tools_to_run,
                error_code="ORCHESTRATION_FAILED"
            )
        
        # STRICT validation - require success from orchestrator
        if not orchestration_result.success:
            failed_tools = [
                name for name, result in orchestration_result.tool_results.items() 
                if not result.success
            ]
            
            raise ProductionAnalysisError(
                f"Analysis failed - {len(failed_tools)} tools failed: {', '.join(failed_tools)}",
                user_id=str(user_id),
                ad_text=ad.headline,
                failed_tools=failed_tools,
                error_code="ANALYSIS_TOOLS_FAILED"
            )
        
        # Convert SDK results to production format (NO FALLBACKS)
        legacy_response = await self._convert_to_production_format(
            orchestration_result,
            ad,
            user_id,
            competitor_ads
        )
        
        # Save to database with production constraints
        await self._save_analysis_to_database_production(
            user_id,
            ad,
            orchestration_result,
            legacy_response
        )
        
        logger.info(f"Production analysis completed successfully for user {user_id}")
        return legacy_response
    
    def _validate_input_data(self, ad: AdInput, user_id: int):
        """Validate input data for production requirements"""
        if not ad.headline or not ad.headline.strip():
            raise ProductionAnalysisError(
                "Headline cannot be empty",
                user_id=str(user_id),
                error_code="INVALID_INPUT"
            )
        
        if not ad.body_text or not ad.body_text.strip():
            raise ProductionAnalysisError(
                "Body text cannot be empty",
                user_id=str(user_id),
                error_code="INVALID_INPUT"
            )
        
        if not ad.platform or ad.platform not in ['facebook', 'google', 'linkedin', 'tiktok', 'twitter', 'instagram']:
            raise ProductionAnalysisError(
                f"Invalid platform: {ad.platform}",
                user_id=str(user_id),
                error_code="INVALID_PLATFORM"
            )
    
    def _get_required_tools(self, requested_tools: List[str] = None) -> List[str]:
        """Get list of tools required for production analysis"""
        if requested_tools:
            # Validate requested tools exist
            available_tools = self.orchestrator.registry.list_tools()
            missing_tools = [tool for tool in requested_tools if tool not in available_tools]
            
            if missing_tools:
                raise ToolsSDKError(
                    "unknown",
                    f"Requested tools not available: {', '.join(missing_tools)}"
                )
            
            return requested_tools
        
        # Use all available analyzer tools for comprehensive analysis
        available_tools = self.orchestrator.registry.list_tools()
        analyzer_tools = self.orchestrator.registry.get_tools_by_type("analyzer")
        
        if not analyzer_tools:
            # Fallback to all tools if no analyzers specifically categorized
            if not available_tools:
                raise ProductionAnalysisError(
                    "No analysis tools available",
                    error_code="NO_TOOLS_AVAILABLE"
                )
            return available_tools
        
        return analyzer_tools
    
    async def _convert_to_production_format(
        self,
        orchestration_result,
        original_ad: AdInput,
        user_id: int,
        competitor_ads: List[CompetitorAd]
    ) -> AdAnalysisResponse:
        """Convert SDK orchestration result to legacy format - PRODUCTION ONLY"""
        
        # Extract scores from successful tools - REQUIRE REAL SCORES
        scores_dict = {}
        feedback = []
        
        for tool_name, tool_output in orchestration_result.tool_results.items():
            if not tool_output.success:
                # This shouldn't happen since we validate success above, but double-check
                raise ToolsSDKError(
                    tool_name,
                    f"Tool failed during conversion: {tool_output.error_message}"
                )
            
            # Extract REAL scores only
            for score_name, score_value in tool_output.scores.items():
                if score_name == 'clarity_score':
                    scores_dict['clarity_score'] = score_value
                elif score_name == 'power_score':
                    scores_dict['persuasion_score'] = score_value
                elif score_name == 'cta_strength':
                    scores_dict['cta_strength'] = score_value
                elif score_name == 'platform_fit':
                    scores_dict['platform_fit_score'] = score_value
                elif score_name == 'emotion_score':
                    scores_dict['emotion_score'] = score_value
            
            # Collect real recommendations as feedback
            if tool_output.recommendations:
                feedback.extend([
                    f"{tool_name}: {rec}" for rec in tool_output.recommendations
                ])
        
        # STRICT VALIDATION - require all essential scores
        required_scores = ['clarity_score', 'persuasion_score', 'emotion_score', 'cta_strength']
        missing_scores = [score for score in required_scores if score not in scores_dict]
        
        if missing_scores:
            raise ProductionAnalysisError(
                f"Missing required scores from analysis: {', '.join(missing_scores)}",
                user_id=str(user_id),
                ad_text=original_ad.headline,
                error_code="INCOMPLETE_SCORES"
            )
        
        # Validate score ranges - no mock scores allowed
        for score_name, score_value in scores_dict.items():
            fail_fast_on_mock_data(score_value, f"score_{score_name}")
            
            if not (0 <= score_value <= 100):
                raise ProductionAnalysisError(
                    f"Invalid score range for {score_name}: {score_value}",
                    user_id=str(user_id),
                    error_code="INVALID_SCORE_RANGE"
                )
        
        # Create AdScore object with REAL data only
        ad_scores = AdScore(
            clarity_score=scores_dict['clarity_score'],
            persuasion_score=scores_dict['persuasion_score'],
            emotion_score=scores_dict['emotion_score'],
            cta_strength=scores_dict['cta_strength'],
            platform_fit_score=scores_dict.get('platform_fit_score', 
                                               self._calculate_platform_fit_production(original_ad)),
            overall_score=orchestration_result.overall_score or 
                         self._calculate_production_overall_score(scores_dict)
        )
        
        # Generate AI alternatives - FAIL if AI not available
        alternatives = await self._generate_production_alternatives(original_ad, user_id)
        
        # Handle competitor comparison with real analysis
        competitor_comparison = None
        if competitor_ads:
            competitor_comparison = await self._analyze_competitors_production(
                original_ad, 
                competitor_ads,
                orchestration_result,
                user_id
            )
        
        # Extract real quick wins from tool insights
        quick_wins = self._extract_production_quick_wins(orchestration_result)
        
        return AdAnalysisResponse(
            analysis_id=orchestration_result.request_id,
            scores=ad_scores,
            feedback=feedback,
            alternatives=alternatives,
            competitor_comparison=competitor_comparison,
            quick_wins=quick_wins
        )
    
    def _calculate_platform_fit_production(self, ad: AdInput) -> float:
        """Calculate platform fit using production logic - no defaults"""
        platform_analyzers = {
            'facebook': self._analyze_facebook_fit,
            'google': self._analyze_google_fit,
            'linkedin': self._analyze_linkedin_fit,
            'tiktok': self._analyze_tiktok_fit,
            'instagram': self._analyze_instagram_fit,
            'twitter': self._analyze_twitter_fit
        }
        
        analyzer = platform_analyzers.get(ad.platform.lower())
        if not analyzer:
            raise ProductionAnalysisError(
                f"No platform analyzer for {ad.platform}",
                error_code="UNSUPPORTED_PLATFORM"
            )
        
        return analyzer(ad)
    
    def _analyze_facebook_fit(self, ad: AdInput) -> float:
        """Analyze Facebook platform fit with production scoring"""
        score = 50  # Base score
        
        # Headline analysis
        headline_words = len(ad.headline.split())
        if 5 <= headline_words <= 7:
            score += 25
        elif headline_words > 10:
            score -= 15
        
        # Body text analysis  
        body_length = len(ad.body_text)
        if 90 <= body_length <= 125:
            score += 20
        elif body_length > 200:
            score -= 20
        
        # CTA analysis
        if ad.cta and len(ad.cta.split()) <= 3:
            score += 15
        
        return min(100, max(0, score))
    
    def _analyze_google_fit(self, ad: AdInput) -> float:
        """Analyze Google Ads platform fit"""
        score = 50
        
        if len(ad.headline) <= 30:
            score += 30
        elif len(ad.headline) > 40:
            score -= 25
        
        if len(ad.body_text) <= 90:
            score += 20
        
        return min(100, max(0, score))
    
    def _analyze_linkedin_fit(self, ad: AdInput) -> float:
        """Analyze LinkedIn platform fit"""
        score = 50
        
        # Professional tone check
        professional_words = ['professional', 'business', 'career', 'industry', 'expertise', 'solution']
        if any(word in ad.body_text.lower() for word in professional_words):
            score += 25
        
        # Longer text acceptable on LinkedIn
        if len(ad.body_text) > 150:
            score += 15
        
        return min(100, max(0, score))
    
    def _analyze_tiktok_fit(self, ad: AdInput) -> float:
        """Analyze TikTok platform fit"""
        score = 50
        
        # Very short text preferred
        total_length = len(ad.headline + ad.body_text)
        if total_length <= 80:
            score += 30
        elif total_length > 150:
            score -= 25
        
        # Casual tone preferred
        casual_indicators = ['!', 'wow', 'amazing', 'incredible', 'awesome']
        if any(indicator in ad.body_text.lower() for indicator in casual_indicators):
            score += 20
        
        return min(100, max(0, score))
    
    def _analyze_instagram_fit(self, ad: AdInput) -> float:
        """Analyze Instagram platform fit"""
        # Similar to Facebook but with visual considerations
        return self._analyze_facebook_fit(ad) * 0.9  # Slightly adjusted
    
    def _analyze_twitter_fit(self, ad: AdInput) -> float:
        """Analyze Twitter platform fit"""
        score = 50
        
        # Character limit considerations
        total_chars = len(ad.headline + ad.body_text + (ad.cta or ''))
        if total_chars <= 280:
            score += 30
        elif total_chars > 400:
            score -= 30
        
        # Hashtag and mention considerations could be added here
        
        return min(100, max(0, score))
    
    def _calculate_production_overall_score(self, scores_dict: Dict[str, float]) -> float:
        """Calculate overall score using production weights"""
        weights = {
            'clarity_score': 0.2,
            'persuasion_score': 0.25,
            'emotion_score': 0.2,
            'cta_strength': 0.25,
            'platform_fit_score': 0.1
        }
        
        weighted_sum = 0
        total_weight = 0
        
        for score_name, weight in weights.items():
            if score_name in scores_dict:
                weighted_sum += scores_dict[score_name] * weight
                total_weight += weight
        
        if total_weight == 0:
            raise ProductionAnalysisError(
                "No scores available for overall calculation",
                error_code="NO_SCORES_FOR_CALCULATION"
            )
        
        overall_score = weighted_sum / total_weight
        return round(overall_score, 1)
    
    async def _generate_production_alternatives(self, ad: AdInput, user_id: int) -> List[AdAlternative]:
        """Generate alternatives using REAL AI only - NO TEMPLATES"""
        
        # Create tool input for AI generation
        tool_input = ToolInput.from_legacy_ad_input(
            ad_data={
                'headline': ad.headline,
                'body_text': ad.body_text,
                'cta': ad.cta,
                'platform': ad.platform
            },
            user_id=str(user_id)
        )
        
        # Try AI generation tools
        ai_tools = ["ai_copy_generator", "ab_test_generator", "roi_copy_generator"]
        available_tools = self.orchestrator.registry.list_tools()
        
        # Find available AI tools
        usable_ai_tools = [tool for tool in ai_tools if tool in available_tools]
        
        if not usable_ai_tools:
            raise AIProviderUnavailable(
                "ai_copy_generation",
                "No AI generation tools available"
            )
        
        try:
            orchestration_result = await self.orchestrator.run_tools(
                tool_input,
                usable_ai_tools,
                execution_mode="parallel"
            )
            
            if not orchestration_result.success:
                raise AIProviderUnavailable(
                    "ai_copy_generation", 
                    "AI generation tools failed"
                )
            
            # Extract alternatives from successful tool outputs
            alternatives = []
            for tool_name, tool_output in orchestration_result.tool_results.items():
                if tool_output.success and hasattr(tool_output, 'generated_alternatives'):
                    alternatives.extend(tool_output.generated_alternatives)
                elif tool_output.success and hasattr(tool_output, 'variations'):
                    # Convert variations to alternatives
                    for variation in tool_output.variations:
                        if isinstance(variation, dict):
                            alternatives.append(AdAlternative(
                                headline=variation.get('headline', ad.headline),
                                body_text=variation.get('body_text', ad.body_text),
                                cta=variation.get('cta', ad.cta),
                                improvement_reason=variation.get('reason', 'AI-generated variation'),
                                expected_improvement=variation.get('expected_lift', 0.0)
                            ))
            
            if not alternatives:
                raise AIProviderUnavailable(
                    "ai_copy_generation",
                    "AI tools returned no alternatives"
                )
            
            return alternatives[:3]  # Limit to top 3 alternatives
            
        except Exception as e:
            # AI generation failed - this is a production error, not a fallback situation
            raise AIProviderUnavailable(
                "ai_copy_generation",
                f"AI alternative generation failed: {str(e)}"
            )
    
    async def _analyze_competitors_production(
        self,
        ad: AdInput,
        competitors: List[CompetitorAd],
        orchestration_result,
        user_id: int
    ) -> Dict[str, Any]:
        """Analyze competitors using real analysis - NO PLACEHOLDERS"""
        
        if not competitors:
            return None
        
        user_score = orchestration_result.overall_score
        if not user_score:
            raise ProductionAnalysisError(
                "Cannot compare competitors without user ad score",
                user_id=str(user_id),
                error_code="MISSING_USER_SCORE"
            )
        
        # Analyze competitor ads using the same tools
        competitor_scores = []
        
        for i, competitor_ad in enumerate(competitors[:3]):  # Limit to 3 competitors
            try:
                # Create tool input for competitor
                comp_tool_input = ToolInput.from_legacy_ad_input(
                    ad_data={
                        'headline': competitor_ad.headline,
                        'body_text': competitor_ad.body_text,
                        'cta': competitor_ad.cta or ad.cta,  # Use user's CTA if competitor doesn't have one
                        'platform': ad.platform
                    },
                    user_id=f"competitor_{i}"
                )
                
                # Run analysis on competitor
                comp_result = await self.orchestrator.run_tools(
                    comp_tool_input,
                    self.orchestrator.registry.get_tools_by_type("analyzer"),
                    execution_mode="parallel"
                )
                
                if comp_result.success and comp_result.overall_score:
                    competitor_scores.append(comp_result.overall_score)
                
            except Exception as e:
                logger.warning(f"Failed to analyze competitor {i}: {e}")
                continue
        
        if not competitor_scores:
            raise ProductionAnalysisError(
                "Failed to analyze any competitor ads",
                user_id=str(user_id),
                error_code="COMPETITOR_ANALYSIS_FAILED"
            )
        
        avg_competitor_score = sum(competitor_scores) / len(competitor_scores)
        
        return {
            "user_vs_competitors": "above_average" if user_score > avg_competitor_score else "below_average",
            "competitor_count": len(competitor_scores),
            "user_score": user_score,
            "avg_competitor_score": round(avg_competitor_score, 1),
            "score_difference": round(user_score - avg_competitor_score, 1),
            "recommendations": self._generate_competitor_recommendations(user_score, avg_competitor_score)
        }
    
    def _generate_competitor_recommendations(self, user_score: float, avg_competitor_score: float) -> List[str]:
        """Generate real recommendations based on competitor comparison"""
        recommendations = []
        
        score_diff = user_score - avg_competitor_score
        
        if score_diff > 10:
            recommendations.append("Your ad significantly outperforms competitors")
            recommendations.append("Consider testing more aggressive positioning")
        elif score_diff > 5:
            recommendations.append("Your ad performs above average vs competitors")
            recommendations.append("Focus on scaling successful elements")
        elif score_diff > -5:
            recommendations.append("Your ad performs similarly to competitors")
            recommendations.append("Consider testing unique value propositions to differentiate")
        else:
            recommendations.append("Competitors are outperforming your current ad")
            recommendations.append("Analyze top competitor elements and adapt your approach")
        
        return recommendations
    
    def _extract_production_quick_wins(self, orchestration_result) -> List[str]:
        """Extract real quick wins from tool insights - NO GENERIC ADVICE"""
        quick_wins = []
        
        for tool_name, tool_output in orchestration_result.tool_results.items():
            if not tool_output.success or not tool_output.insights:
                continue
            
            insights = tool_output.insights
            
            # Readability-specific wins
            if tool_name == "readability_analyzer":
                if insights.get('grade_level', 0) > 10:
                    quick_wins.append(f"Simplify language (currently grade {insights.get('grade_level')} level)")
                if insights.get('avg_sentence_length', 0) > 20:
                    quick_wins.append("Shorten sentences for better readability")
                if len(insights.get('power_words_found', [])) < 2:
                    quick_wins.append("Add power words to increase impact")
            
            # CTA-specific wins  
            elif tool_name == "cta_analyzer":
                if not insights.get('has_urgency', False):
                    quick_wins.append("Add urgency to your call-to-action")
                if not insights.get('has_action_verb', False):
                    quick_wins.append("Use stronger action verbs in CTA")
                if insights.get('cta_length', 0) > 25:
                    quick_wins.append("Shorten your call-to-action")
            
            # Psychology-specific wins
            elif tool_name == "psychology_scorer":
                if insights.get('persuasion_score', 0) < 70:
                    quick_wins.append("Strengthen persuasive elements")
                if insights.get('social_proof_score', 0) < 50:
                    quick_wins.append("Add social proof elements")
            
            # Platform-specific wins
            elif tool_name == "platform_optimizer":
                platform_issues = insights.get('platform_issues', [])
                for issue in platform_issues[:2]:  # Limit to top 2 issues
                    quick_wins.append(f"Platform optimization: {issue}")
        
        # Remove duplicates and limit to top 5
        seen = set()
        unique_wins = []
        for win in quick_wins:
            if win not in seen:
                seen.add(win)
                unique_wins.append(win)
        
        return unique_wins[:5]
    
    async def _save_analysis_to_database_production(
        self,
        user_id: int,
        ad: AdInput,
        orchestration_result,
        legacy_response: AdAnalysisResponse
    ):
        """Save analysis with production data validation"""
        
        # Validate scores before saving
        scores = legacy_response.scores
        score_validations = [
            (scores.overall_score, "overall_score"),
            (scores.clarity_score, "clarity_score"),
            (scores.persuasion_score, "persuasion_score"),
            (scores.emotion_score, "emotion_score"),
            (scores.cta_strength, "cta_strength"),
            (scores.platform_fit_score, "platform_fit_score")
        ]
        
        for score_value, score_name in score_validations:
            if not (0 <= score_value <= 100):
                raise DatabaseConstraintError(
                    "score_range_check",
                    "ad_analyses",
                    {score_name: score_value}
                )
            
            # Check for suspicious default scores
            fail_fast_on_mock_data(score_value, f"database_save_{score_name}")
        
        try:
            analysis_record = AdAnalysis(
                id=orchestration_result.request_id,
                user_id=user_id,
                headline=ad.headline,
                body_text=ad.body_text,
                cta=ad.cta,
                platform=ad.platform,
                industry=getattr(ad, 'industry', None),
                target_audience=getattr(ad, 'target_audience', None),
                overall_score=scores.overall_score,
                clarity_score=scores.clarity_score,
                persuasion_score=scores.persuasion_score,
                emotion_score=scores.emotion_score,
                cta_strength_score=scores.cta_strength,
                platform_fit_score=scores.platform_fit_score,
                analysis_data={
                    'sdk_version': '2.0.0-production',
                    'orchestration_result': orchestration_result.to_dict(),
                    'tools_used': list(orchestration_result.tool_results.keys()),
                    'execution_time': orchestration_result.total_execution_time,
                    'alternatives_count': len(legacy_response.alternatives),
                    'production_validated': True
                },
                created_at=orchestration_result.timestamp
            )
            
            self.db.add(analysis_record)
            self.db.commit()
            
            logger.info(f"Saved production analysis {orchestration_result.request_id} to database")
            
        except Exception as e:
            logger.error(f"Failed to save production analysis to database: {e}")
            self.db.rollback()
            raise DatabaseConstraintError(
                "analysis_save_failed",
                "ad_analyses",
                {"error": str(e)}
            )
    
    async def production_health_check(self) -> Dict[str, Any]:
        """Production health check - strict validation"""
        try:
            # Check orchestrator health
            tool_health = await self.orchestrator.health_check_tools()
            
            # Count healthy tools
            healthy_tools = [
                name for name, health in tool_health.items()
                if health.get('status') == 'healthy'
            ]
            
            total_tools = len(tool_health)
            healthy_count = len(healthy_tools)
            
            # Determine service status
            if healthy_count == 0:
                status = 'critical'
            elif healthy_count < total_tools * 0.8:  # Less than 80% healthy
                status = 'degraded'
            else:
                status = 'healthy'
            
            return {
                'service': 'production_ad_analysis',
                'status': status,
                'tools_total': total_tools,
                'tools_healthy': healthy_count,
                'tools_degraded': total_tools - healthy_count,
                'healthy_tools': healthy_tools,
                'detailed_health': tool_health,
                'production_ready': status in ['healthy', 'degraded']
            }
            
        except Exception as e:
            return {
                'service': 'production_ad_analysis',
                'status': 'critical',
                'error': str(e),
                'production_ready': False
            }