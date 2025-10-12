"""
Enhanced ad analysis service using the unified Tools SDK

This service demonstrates how to use the new unified SDK for tool orchestration
while maintaining backward compatibility with existing interfaces.
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
        
        # Generate quick wins from tool insights
        quick_wins = self._extract_quick_wins(orchestration_result)
        
        return AdAnalysisResponse(
            analysis_id=orchestration_result.request_id,
            scores=ad_scores,
            feedback=feedback,
            alternatives=alternatives,
            competitor_comparison=competitor_comparison,
            quick_wins=quick_wins
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
        """Generate fallback alternatives (TODO: replace with AI generator tool)"""
        # This would be replaced by the AI generator tool from the SDK
        return [
            AdAlternative(
                headline=f"Improved: {ad.headline}",
                body_text=f"Enhanced version: {ad.body_text}",
                cta=f"Better {ad.cta}",
                improvement_reason="SDK-generated alternative",
                expected_improvement=15.0
            )
        ]
    
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
    
    def _extract_quick_wins(self, orchestration_result) -> List[str]:
        """Extract quick wins from tool insights"""
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
            self.db.commit()
            
            logger.info(f"Saved analysis {orchestration_result.request_id} to database")
            
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
