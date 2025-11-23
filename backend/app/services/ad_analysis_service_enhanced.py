"""
Enhanced ad analysis service using the unified Tools SDK

This service demonstrates how to use the new unified SDK for tool orchestration
while maintaining backward compatibility with existing interfaces.
"""

import asyncio
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from datetime import datetime
import os

# Import the Tools SDK
from packages.tools_sdk import ToolOrchestrator, ToolInput, ToolRegistry, default_registry
from packages.tools_sdk.tools import register_all_tools

# Legacy imports for compatibility
from app.schemas.ads import AdInput, CompetitorAd, AdScore, AdAlternative, AdAnalysisResponse
from app.models.ad_analysis import AdAnalysis
from app.core.logging import get_logger

# Import AI service for real improvement generation
from app.services.production_ai_generator import ProductionAIService
from app.services.agent_system import MultiAgentOptimizer
from app.services.recommendation_orchestrator import RecommendationOrchestrator
from app.core.exceptions import AIProviderUnavailable

logger = get_logger(__name__)


class EnhancedAdAnalysisService:
    """
    Enhanced ad analysis service using the unified Tools SDK
    
    This service provides the same interface as the original AdAnalysisService
    but uses the new unified SDK internally for better consistency and reliability.
    """
    
    def __init__(self, db: Session, registry: ToolRegistry = None):
        self.db = db
        self.orchestrator = ToolOrchestrator(registry or default_registry)
        self.rec_orchestrator = RecommendationOrchestrator()  # NEW: Recommendation prioritization
        
        # Initialize AI service for improvement generation
        openai_key = os.getenv('OPENAI_API_KEY')
        gemini_key = os.getenv('GEMINI_API_KEY')
        
        try:
            self.ai_service = ProductionAIService(openai_key, gemini_key)
            logger.info("AI service initialized for improvement generation")
            
            # Initialize multi-agent optimizer
            self.multi_agent_optimizer = MultiAgentOptimizer(self.ai_service)
            logger.info("Multi-agent optimizer initialized")
        except Exception as e:
            logger.warning(f"AI service initialization failed: {e}. Will use fallback for improvements.")
            self.ai_service = None
            self.multi_agent_optimizer = None
        
        # Ensure tools are registered
        try:
            register_all_tools()
            available_tools = self.orchestrator.registry.list_tools()
            logger.info(f"Enhanced service initialized with tools: {available_tools}")
        except Exception as e:
            logger.warning(f"Tool registration had issues: {e}")
    
    async def analyze_ad(
        self, 
        user_id: int, 
        ad: AdInput, 
        competitor_ads: List[CompetitorAd] = [],
        requested_tools: List[str] = None
    ) -> AdAnalysisResponse:
        """
        Perform comprehensive ad analysis using the unified SDK
        
        Args:
            user_id: User ID for database storage
            ad: Ad input data
            competitor_ads: Optional competitor ads for comparison
            requested_tools: Specific tools to run (if None, runs all available)
            
        Returns:
            AdAnalysisResponse compatible with legacy interface
        """
        logger.info(f"Starting enhanced analysis for user {user_id}")
        
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
        
        # Determine which tools to run
        if requested_tools is None:
            # Run all available analyzer tools
            available_tools = self.orchestrator.registry.list_tools()
            analyzer_tools = self.orchestrator.registry.get_tools_by_type("analyzer")
            tools_to_run = analyzer_tools if analyzer_tools else available_tools
        else:
            tools_to_run = requested_tools
        
        logger.info(f"Running tools: {tools_to_run}")
        
        # Execute tools through orchestrator
        orchestration_result = await self.orchestrator.run_tools(
            tool_input,
            tools_to_run,
            execution_mode="parallel"
        )
        
        # Convert SDK results back to legacy format
        legacy_response = await self._convert_to_legacy_format(
            orchestration_result,
            ad,
            user_id,
            competitor_ads
        )
        
        # Save to database (maintaining compatibility)
        await self._save_analysis_to_database(
            user_id,
            ad,
            orchestration_result,
            legacy_response
        )
        
        logger.info(f"Analysis completed. Success: {orchestration_result.success}")
        
        return legacy_response
    
    async def _convert_to_legacy_format(
        self,
        orchestration_result,
        original_ad: AdInput,
        user_id: int,
        competitor_ads: List[CompetitorAd]
    ) -> AdAnalysisResponse:
        """Convert SDK orchestration result to legacy AdAnalysisResponse format"""
        
        # Extract scores from successful tools
        scores_dict = {}
        feedback = []
        
        for tool_name, tool_output in orchestration_result.tool_results.items():
            if tool_output.success:
                # Map tool scores to legacy score names
                for score_name, score_value in tool_output.scores.items():
                    if score_name == 'clarity_score':
                        scores_dict['clarity_score'] = score_value
                    elif score_name == 'power_score':
                        scores_dict['persuasion_score'] = score_value
                    elif score_name == 'cta_strength':
                        scores_dict['cta_strength'] = score_value
                    elif score_name == 'platform_fit':
                        scores_dict['platform_fit_score'] = score_value
                
                # Collect recommendations as feedback
                if tool_output.recommendations:
                    feedback.extend([
                        f"{tool_name}: {rec}" for rec in tool_output.recommendations
                    ])
        
        # Add emotion score if available (would come from emotion tool)
        if 'emotion_score' not in scores_dict:
            scores_dict['emotion_score'] = 70.0  # Default fallback
        
        # Create AdScore object
        ad_scores = AdScore(
            clarity_score=scores_dict.get('clarity_score', 70.0),
            persuasion_score=scores_dict.get('persuasion_score', 70.0),
            emotion_score=scores_dict.get('emotion_score', 70.0),
            cta_strength=scores_dict.get('cta_strength', 70.0),
            platform_fit_score=scores_dict.get('platform_fit_score', 75.0),
            overall_score=orchestration_result.overall_score or self._calculate_fallback_overall_score(scores_dict)
        )
        
        # Generate alternatives (TODO: integrate with AI generator tool)
        alternatives = await self._generate_fallback_alternatives(original_ad)
        
        # Handle competitor comparison if provided
        competitor_comparison = None
        if competitor_ads:
            competitor_comparison = await self._analyze_competitors_sdk(
                original_ad, 
                competitor_ads,
                orchestration_result
            )
        
        # Generate quick wins using Recommendation Orchestrator (prioritized from 45-72 recommendations down to top 5)
        quick_wins = self._orchestrate_recommendations(orchestration_result)
        
        # Convert feedback list to string to match Pydantic schema expectations
        feedback_text = "\n".join(str(f) for f in feedback if f) if feedback else "Analysis completed successfully"
        
        # Extract tool-specific results for frontend display
        tool_results_dict = {}
        try:
            if hasattr(orchestration_result, 'tool_results') and orchestration_result.tool_results:
                for tool_name, tool_output in orchestration_result.tool_results.items():
                    if tool_output and hasattr(tool_output, 'success') and tool_output.success:
                        tool_results_dict[tool_name] = {
                            'success': True,
                            'scores': getattr(tool_output, 'scores', {}),
                            'insights': getattr(tool_output, 'insights', {}),
                            'recommendations': getattr(tool_output, 'recommendations', []),
                            'execution_time': getattr(tool_output, 'execution_time', 0.0),
                            'confidence_score': getattr(tool_output, 'confidence_score', None)
                        }
        except Exception as e:
            logger.warning(f"Could not extract tool_results: {e}. Continuing without detailed tool results.")
            tool_results_dict = {}
        
        return AdAnalysisResponse(
            analysis_id=orchestration_result.request_id,
            scores=ad_scores,
            feedback=feedback_text,
            alternatives=alternatives,
            competitor_comparison=competitor_comparison,
            quick_wins=quick_wins,
            tool_results=tool_results_dict  # Include all tool-specific results
        )
    
    def _calculate_fallback_overall_score(self, scores_dict: Dict[str, float]) -> float:
        """Calculate overall score using legacy weights"""
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
        
        return weighted_sum / total_weight if total_weight > 0 else 70.0
    
    async def _generate_fallback_alternatives(self, ad: AdInput) -> List[AdAlternative]:
        """Generate AI-powered improvement alternatives using ProductionAIService"""

        # If AI service is available, generate real improvements
        logger.info(f"AI service available: {self.ai_service is not None}")
        if self.ai_service:
            try:
                logger.info(f"Generating AI-powered improvements for platform: {ad.platform}")
                
                # Prepare ad data for AI service
                ad_data = {
                    'headline': ad.headline,
                    'body_text': ad.body_text,
                    'cta': ad.cta,
                    'platform': ad.platform,
                    'industry': getattr(ad, 'industry', 'general'),
                    'target_audience': getattr(ad, 'target_audience', 'general audience')
                }
                
                # Generate single improved version using AI (persuasive variant)
                improved_result = await self.ai_service.generate_ad_alternative(
                    ad_data=ad_data,
                    variant_type='persuasive',
                    emoji_level='moderate',
                    human_tone='conversational',
                    brand_tone='casual',
                    formality_level=5,
                    include_cta=True,
                    cta_style='medium',
                    creativity_level=6,
                    urgency_level=5,
                    emotion_type='inspiring',
                    filter_cliches=True
                )
                
                # Generate A/B/C test variations with different strategic approaches
                logger.info("Generating A/B/C test variations")
                
                # Variation A: Benefit-Focused (appeals to aspirations)
                variation_a_result = await self.ai_service.generate_ad_alternative(
                    ad_data=ad_data,
                    variant_type='persuasive',
                    emoji_level='moderate',
                    human_tone='aspirational',
                    brand_tone='professional',
                    formality_level=6,
                    include_cta=True,
                    cta_style='soft',
                    creativity_level=5,
                    urgency_level=4,
                    emotion_type='inspiring',
                    filter_cliches=True
                )
                
                # Variation B: Problem-Focused (identifies with pain points)
                variation_b_result = await self.ai_service.generate_ad_alternative(
                    ad_data=ad_data,
                    variant_type='emotional',
                    emoji_level='light',
                    human_tone='empathetic',
                    brand_tone='friendly',
                    formality_level=5,
                    include_cta=True,
                    cta_style='medium',
                    creativity_level=6,
                    urgency_level=7,
                    emotion_type='problem_solving',
                    filter_cliches=True
                )
                
                # Variation C: Story-Driven (creates emotional connection)
                variation_c_result = await self.ai_service.generate_ad_alternative(
                    ad_data=ad_data,
                    variant_type='emotional',
                    emoji_level='moderate',
                    human_tone='storytelling',
                    brand_tone='authentic',
                    formality_level=4,
                    include_cta=True,
                    cta_style='soft',
                    creativity_level=7,
                    urgency_level=3,
                    emotion_type='trust_building',
                    filter_cliches=True
                )
                
                # Log what AI generated
                logger.info(f"AI Results - Improved: headline={len(improved_result.get('headline', ''))} chars, body={len(improved_result.get('body_text', ''))} chars")
                logger.info(f"AI Results - Variation A: headline={len(variation_a_result.get('headline', ''))} chars, body={len(variation_a_result.get('body_text', ''))} chars")
                logger.info(f"AI Results - Variation B: headline={len(variation_b_result.get('headline', ''))} chars, body={len(variation_b_result.get('body_text', ''))} chars")
                logger.info(f"AI Results - Variation C: headline={len(variation_c_result.get('headline', ''))} chars, body={len(variation_c_result.get('body_text', ''))} chars")

                # Convert AI results to AdAlternative format
                alternatives = [
                    # Main improved version
                    AdAlternative(
                        variant_type="improved",
                        headline=improved_result.get('headline', ad.headline),
                        body_text=improved_result.get('body_text', ad.body_text),
                        cta=improved_result.get('cta', ad.cta),
                        improvement_reason=improved_result.get('improvement_reason', 'AI-enhanced copy with improved persuasion'),
                        expected_improvement=20.0
                    ),
                    # Variation A: Benefit-Focused
                    AdAlternative(
                        variant_type="benefit_focused",
                        headline=variation_a_result.get('headline', ad.headline),
                        body_text=variation_a_result.get('body_text', ad.body_text),
                        cta=variation_a_result.get('cta', ad.cta),
                        improvement_reason="Variation A - Benefit-Focused: Appeals to aspirations and desired outcomes. Best for solution-seekers, warm leads, known problems.",
                        expected_improvement=18.0
                    ),
                    # Variation B: Problem-Focused
                    AdAlternative(
                        variant_type="problem_focused",
                        headline=variation_b_result.get('headline', ad.headline),
                        body_text=variation_b_result.get('body_text', ad.body_text),
                        cta=variation_b_result.get('cta', ad.cta),
                        improvement_reason="Variation B - Problem-Focused: Identifies with pain points and frustrations. Best for pain-aware audiences, high urgency, immediate solutions.",
                        expected_improvement=22.0
                    ),
                    # Variation C: Story-Driven
                    AdAlternative(
                        variant_type="story_driven",
                        headline=variation_c_result.get('headline', ad.headline),
                        body_text=variation_c_result.get('body_text', ad.body_text),
                        cta=variation_c_result.get('cta', ad.cta),
                        improvement_reason="Variation C - Story-Driven: Creates emotional connection through narrative. Best for building trust, cold traffic, brand awareness.",
                        expected_improvement=16.0
                    )
                ]
                
                logger.info("Successfully generated 4 AI-powered alternatives (1 improved + 3 A/B/C variations)")
                return alternatives
                
            except AIProviderUnavailable as e:
                logger.error(f"AI provider unavailable: {e}. Using fallback alternatives.")
            except Exception as e:
                logger.error(f"Error generating AI alternatives: {e}. Using fallback alternatives.")
        
        # Fallback if AI service is not available or fails
        logger.warning("Using fallback alternatives (AI service unavailable)")
        return [
            AdAlternative(
                variant_type="fallback",
                headline=f"Improved: {ad.headline}",
                body_text=f"Enhanced version: {ad.body_text}",
                cta=f"Better {ad.cta}",
                improvement_reason="Fallback alternative (AI service unavailable)",
                expected_improvement=5.0
            )
        ]
    
    async def analyze_with_multi_agent(
        self,
        user_id: int,
        ad: AdInput,
        max_iterations: int = 1
    ) -> Dict[str, Any]:
        """
        Advanced multi-agent optimization (optional premium feature)
        
        Uses 4 specialized agents:
        1. Analyzer - Scores and identifies issues
        2. Strategist - Plans improvement strategy
        3. Writer - Generates 4 variations (Improved + A/B/C)
        4. Quality Control - Validates output
        
        Args:
            user_id: User ID
            ad: Ad input
            max_iterations: Number of refinement iterations (1-4)
        
        Returns:
            Structured optimization result with reasoning and scores
        """
        if not self.multi_agent_optimizer:
            raise Exception("Multi-agent optimizer not available. AI service may not be initialized.")
        
        logger.info(f"🤖 Starting multi-agent optimization for user {user_id}")
        
        ad_data = {
            'headline': ad.headline,
            'body_text': ad.body_text,
            'cta': ad.cta,
            'platform': ad.platform,
            'industry': getattr(ad, 'industry', None),
            'target_audience': getattr(ad, 'target_audience', None)
        }
        
        # Run multi-agent optimization
        result = await self.multi_agent_optimizer.optimize(ad_data, max_iterations)
        
        logger.info(f"✅ Multi-agent optimization complete. Improvement: {result.improved_score.overall - result.original_score.overall:.1f} points")
        
        return result.to_dict()
    
    async def _analyze_competitors_sdk(
        self,
        ad: AdInput,
        competitors: List[CompetitorAd],
        orchestration_result
    ) -> Dict[str, Any]:
        """Analyze competitors using SDK results"""
        # TODO: This would use the competitor analyzer tool from the SDK
        user_score = orchestration_result.overall_score or 70.0
        
        return {
            "user_vs_competitors": "above_average" if user_score > 70 else "below_average",
            "competitor_count": len(competitors),
            "user_score": user_score,
            "avg_competitor_score": 68.5,  # Placeholder
            "recommendations": [
                "Your ad performs better than average competitors",
                "Consider testing different emotional appeals"
            ]
        }
    
    def _orchestrate_recommendations(self, orchestration_result) -> List[str]:
        """
        Use Recommendation Orchestrator to prioritize recommendations

        Reduces 45-72 recommendations from all tools down to top 5 most impactful
        """
        # Orchestrate recommendations from all tool results
        prioritized_recommendations = self.rec_orchestrator.orchestrate(
            tool_results=orchestration_result.tool_results,
            max_recommendations=5
        )

        # Convert to string format for quick_wins
        quick_wins = []
        for rec in prioritized_recommendations:
            # Format: "🎯 [Priority] Title - Description"
            priority_emoji = {
                'CRITICAL': '❌',
                'HIGH': '⚠️',
                'MEDIUM': '💡',
                'LOW': '✓'
            }
            emoji = priority_emoji.get(rec.priority.name, '•')
            quick_win = f"{emoji} {rec.title}"
            quick_wins.append(quick_win)

        logger.info(f"Orchestrated {len(quick_wins)} prioritized recommendations")

        return quick_wins

    def _extract_quick_wins(self, orchestration_result) -> List[str]:
        """
        DEPRECATED: Old quick wins extraction logic
        Kept for backward compatibility but now delegates to _orchestrate_recommendations
        """
        return self._orchestrate_recommendations(orchestration_result)

        # OLD LOGIC (commented out, using orchestrator now):
        quick_wins = []

        for tool_name, tool_output in orchestration_result.tool_results.items():
            if tool_output.success and tool_output.insights:
                
                # Readability quick wins
                if tool_name == "readability_analyzer":
                    insights = tool_output.insights
                    if insights.get('grade_level', 0) > 10:
                        quick_wins.append("Simplify language to improve readability")
                    if len(insights.get('power_words_found', [])) < 2:
                        quick_wins.append("Add more power words to increase impact")
                
                # CTA quick wins
                elif tool_name == "cta_analyzer":
                    insights = tool_output.insights
                    if not insights.get('has_urgency', False):
                        quick_wins.append("Add urgency to your CTA")
                    if not insights.get('has_action_verb', False):
                        quick_wins.append("Use stronger action verbs in your CTA")
        
        return quick_wins[:5]  # Limit to top 5 quick wins
    
    async def _save_analysis_to_database(
        self,
        user_id: int,
        ad: AdInput,
        orchestration_result,
        legacy_response: AdAnalysisResponse
    ):
        """Save analysis results to database"""
        try:
            analysis_record = AdAnalysis(
                id=orchestration_result.request_id,
                user_id=user_id,
                headline=ad.headline,
                body_text=ad.body_text,
                cta=ad.cta,
                platform=ad.platform,
                overall_score=legacy_response.scores.overall_score,
                clarity_score=legacy_response.scores.clarity_score,
                persuasion_score=legacy_response.scores.persuasion_score,
                emotion_score=legacy_response.scores.emotion_score,
                cta_strength_score=legacy_response.scores.cta_strength,
                platform_fit_score=legacy_response.scores.platform_fit_score,
                analysis_data={
                    'sdk_version': '1.0.0',
                    'orchestration_result': orchestration_result.to_dict(),
                    'tools_used': list(orchestration_result.tool_results.keys()),
                    'execution_time': orchestration_result.total_execution_time
                },
                created_at=orchestration_result.timestamp
            )
            
            self.db.add(analysis_record)

            # Save alternatives to database
            from app.models.ad_analysis import AdGeneration

            logger.info(f"Saving {len(legacy_response.alternatives)} alternatives to database")
            for alt in legacy_response.alternatives:
                alt_record = AdGeneration(
                    analysis_id=orchestration_result.request_id,
                    variant_type=alt.variant_type,
                    generated_headline=alt.headline,
                    generated_body_text=alt.body_text,
                    generated_cta=alt.cta,
                    improvement_reason=alt.improvement_reason,
                    predicted_score=alt.expected_improvement
                )
                self.db.add(alt_record)
                logger.info(f"  - Saved alternative: {alt.variant_type} (headline: {len(alt.headline or '')} chars)")

            self.db.commit()

            logger.info(f"Saved analysis {orchestration_result.request_id} with {len(legacy_response.alternatives)} alternatives to database")
            
        except Exception as e:
            logger.error(f"Failed to save analysis to database: {e}")
            self.db.rollback()
    
    async def health_check(self) -> Dict[str, Any]:
        """Check health of the enhanced service and all tools"""
        try:
            # Check orchestrator health
            tool_health = await self.orchestrator.health_check_tools()
            
            service_status = {
                'service': 'enhanced_ad_analysis',
                'status': 'healthy',
                'tools_available': list(tool_health.keys()),
                'tools_healthy': [
                    name for name, health in tool_health.items()
                    if health.get('status') == 'healthy'
                ],
                'total_execution_time': 0.0,
                'detailed_tool_health': tool_health
            }
            
            # Determine overall health
            healthy_tools = len(service_status['tools_healthy'])
            total_tools = len(service_status['tools_available'])
            
            if healthy_tools == 0:
                service_status['status'] = 'unhealthy'
            elif healthy_tools < total_tools:
                service_status['status'] = 'degraded'
            
            return service_status
            
        except Exception as e:
            return {
                'service': 'enhanced_ad_analysis',
                'status': 'error',
                'error': str(e),
                'tools_available': [],
                'tools_healthy': []
            }
    
    def get_available_tools(self) -> Dict[str, Any]:
        """Get information about available tools"""
        return self.orchestrator.get_tool_capabilities()
    
    async def analyze_with_specific_tools(
        self,
        user_id: int,
        ad: AdInput,
        tool_names: List[str]
    ) -> Dict[str, Any]:
        """
        Analyze with specific tools only
        
        This method provides more granular control over which tools to run
        and returns the raw SDK results rather than legacy format.
        """
        tool_input = ToolInput.from_legacy_ad_input(
            ad_data={
                'headline': ad.headline,
                'body_text': ad.body_text,
                'cta': ad.cta,
                'platform': ad.platform
            },
            user_id=str(user_id)
        )
        
        orchestration_result = await self.orchestrator.run_tools(
            tool_input,
            tool_names,
            execution_mode="parallel"
        )
        
        return orchestration_result.to_dict()
    
    # Legacy compatibility methods
    def get_user_analysis_history(self, user_id: int, limit: int = 10, offset: int = 0) -> List[Dict]:
        """Get user's analysis history - legacy compatibility method"""
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
        """Get specific analysis by ID - legacy compatibility method"""
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
        """Generate alternative variations for an ad - legacy compatibility method"""
        # Use the SDK to generate alternatives
        tool_input = ToolInput.from_legacy_ad_input(
            ad_data={
                'headline': ad.headline,
                'body_text': ad.body_text,
                'cta': ad.cta,
                'platform': ad.platform
            },
            user_id="anonymous"  # For alternative generation, user_id can be anonymous
        )
        
        # Try to use AI generator tools
        try:
            orchestration_result = await self.orchestrator.run_tools(
                tool_input,
                ["ai_copy_generator", "ab_test_generator"],  # Try these tools first
                execution_mode="parallel"
            )
            
            # Convert to legacy format
            alternatives = []
            for tool_name, tool_output in orchestration_result.tool_results.items():
                if tool_output.success and hasattr(tool_output, 'generated_alternatives'):
                    alternatives.extend(tool_output.generated_alternatives)
            
            if alternatives:
                return alternatives
        
        except Exception as e:
            logger.warning(f"Failed to generate alternatives with SDK: {e}")
        
        # Fallback to template-based alternatives
        return await self._generate_fallback_alternatives(ad)
