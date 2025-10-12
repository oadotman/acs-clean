"""
Unified Tools Flow Service - Main API interface for the complete ad copy analysis system
Integrates orchestrator, configuration management, and provides simplified API
"""

import asyncio
import time
import logging
from typing import Dict, Any, List, Optional, Union
from dataclasses import dataclass, asdict

from .tools_flow_orchestrator import (
    ToolsFlowOrchestrator, FlowExecutionResult, FlowConfiguration,
    ToolFlowStep, FlowExecutionStrategy, FlowPriority
)
from .flow_config_manager import FlowConfigurationManager, FlowTemplate
from ..core import ToolInput, ToolOutput, ToolConfig
from ..tools.performance_forensics_tool import PerformanceForensicsToolRunner
from ..tools.psychology_scorer_tool import PsychologyScorerToolRunner
from ..tools.brand_voice_engine_tool import BrandVoiceEngineToolRunner
from ..tools.legal_risk_scanner_tool import LegalRiskScannerToolRunner


@dataclass
class AnalysisRequest:
    """Simplified request structure for ad copy analysis"""
    headline: str
    body_text: str
    cta: str
    industry: str = ""
    platform: str = ""
    target_audience: str = ""
    brand_guidelines: Optional[Dict[str, Any]] = None
    analysis_type: str = "comprehensive"  # comprehensive, quick, compliance, optimization
    custom_flow_id: Optional[str] = None
    request_metadata: Optional[Dict[str, Any]] = None


@dataclass
class AnalysisResponse:
    """Unified response structure for ad copy analysis results"""
    success: bool
    request_id: str
    execution_time: float
    analysis_type: str
    
    # Aggregated scores (0-100)
    overall_score: float
    performance_score: float
    psychology_score: float
    brand_score: float
    legal_score: float
    
    # Key insights
    strengths: List[str]
    weaknesses: List[str]
    recommendations: List[str]
    
    # Detailed results
    tool_results: Dict[str, Any]
    execution_metadata: Dict[str, Any]
    
    # Error information
    errors: Optional[List[str]] = None
    warnings: Optional[List[str]] = None


class UnifiedToolsService:
    """
    Unified service for ad copy analysis using multiple tools
    
    Features:
    - Simplified API for different analysis types
    - Automatic flow selection based on requirements
    - Configuration management and persistence
    - Results caching and performance optimization
    - Error handling and fallback strategies
    """
    
    def __init__(self, config_directory: str = None, max_workers: int = 4):
        self.logger = logging.getLogger(__name__)
        
        # Initialize core components
        self.orchestrator = ToolsFlowOrchestrator(max_workers=max_workers)
        self.config_manager = FlowConfigurationManager(config_directory)
        
        # Analysis type mappings
        self.analysis_type_mappings = {
            'comprehensive': 'comprehensive_analysis',
            'quick': 'quick_performance',
            'compliance': 'compliance_check',
            'optimization': 'optimization_focused'
        }
        
        # Results cache for performance
        self.results_cache: Dict[str, AnalysisResponse] = {}
        self.cache_ttl = 300  # 5 minutes
        
        # Initialize default configurations if not exist
        self._ensure_default_configurations()
    
    async def analyze_copy(self, request: AnalysisRequest) -> AnalysisResponse:
        """
        Main entry point for ad copy analysis
        
        Automatically selects appropriate flow based on analysis_type,
        executes the analysis, and returns unified results
        """
        start_time = time.time()
        
        try:
            # Generate cache key
            cache_key = self._generate_cache_key(request)
            
            # Check cache first
            if cache_key in self.results_cache:
                cached_result = self.results_cache[cache_key]
                if time.time() - cached_result.execution_metadata.get('cached_at', 0) < self.cache_ttl:
                    self.logger.info(f"Returning cached result for {cache_key}")
                    return cached_result
            
            # Convert to ToolInput format
            tool_input = self._convert_to_tool_input(request)
            
            # Select flow configuration
            flow_config = self._select_flow_configuration(request)
            
            # Execute analysis
            self.logger.info(f"Starting analysis: {request.analysis_type} for request {tool_input.request_id}")
            flow_result = await self.orchestrator.execute_flow(flow_config, tool_input)
            
            # Convert to unified response
            response = self._convert_to_analysis_response(
                flow_result, request, time.time() - start_time
            )
            
            # Cache successful results
            if response.success:
                response.execution_metadata['cached_at'] = time.time()
                self.results_cache[cache_key] = response
                
                # Clean old cache entries
                self._clean_cache()
            
            self.logger.info(
                f"Analysis completed: {request.analysis_type} - "
                f"Success: {response.success}, Score: {response.overall_score:.1f}, "
                f"Time: {response.execution_time:.2f}s"
            )
            
            return response
            
        except Exception as e:
            execution_time = time.time() - start_time
            self.logger.error(f"Analysis failed: {str(e)}")
            
            return AnalysisResponse(
                success=False,
                request_id=getattr(request, 'request_id', 'unknown'),
                execution_time=execution_time,
                analysis_type=request.analysis_type,
                overall_score=0.0,
                performance_score=0.0,
                psychology_score=0.0,
                brand_score=0.0,
                legal_score=0.0,
                strengths=[],
                weaknesses=[],
                recommendations=[],
                tool_results={},
                execution_metadata={'error': str(e)},
                errors=[str(e)]
            )
    
    async def analyze_copy_batch(self, requests: List[AnalysisRequest]) -> List[AnalysisResponse]:
        """Analyze multiple ad copies in batch with optimal performance"""
        
        # Group requests by analysis type for optimization
        grouped_requests = {}
        for i, request in enumerate(requests):
            analysis_type = request.analysis_type
            if analysis_type not in grouped_requests:
                grouped_requests[analysis_type] = []
            grouped_requests[analysis_type].append((i, request))
        
        # Process groups in parallel
        all_tasks = []
        result_mapping = {}
        
        for analysis_type, type_requests in grouped_requests.items():
            for original_index, request in type_requests:
                task = self.analyze_copy(request)
                all_tasks.append(task)
                result_mapping[len(all_tasks) - 1] = original_index
        
        # Execute all analyses
        results = await asyncio.gather(*all_tasks, return_exceptions=True)
        
        # Reorder results to match original request order
        ordered_results = [None] * len(requests)
        for task_index, result in enumerate(results):
            original_index = result_mapping[task_index]
            
            if isinstance(result, Exception):
                # Create error response
                ordered_results[original_index] = AnalysisResponse(
                    success=False,
                    request_id=f"batch_{original_index}",
                    execution_time=0.0,
                    analysis_type=requests[original_index].analysis_type,
                    overall_score=0.0,
                    performance_score=0.0,
                    psychology_score=0.0,
                    brand_score=0.0,
                    legal_score=0.0,
                    strengths=[],
                    weaknesses=[],
                    recommendations=[],
                    tool_results={},
                    execution_metadata={},
                    errors=[str(result)]
                )
            else:
                ordered_results[original_index] = result
        
        return ordered_results
    
    def get_available_analysis_types(self) -> Dict[str, str]:
        """Get available analysis types and their descriptions"""
        return {
            'comprehensive': 'Complete analysis using all tools for maximum insights',
            'quick': 'Fast performance and psychology analysis for quick optimization',
            'compliance': 'Focus on brand alignment and legal compliance',
            'optimization': 'Deep dive into performance metrics and psychological triggers'
        }
    
    def get_flow_configurations(self) -> Dict[str, Dict[str, Any]]:
        """Get all available flow configurations"""
        return self.config_manager.list_configurations()
    
    def create_custom_flow(self, flow_config: FlowConfiguration) -> bool:
        """Create a custom flow configuration"""
        return self.config_manager.save_configuration(flow_config)
    
    def validate_flow_configuration(self, flow_config: FlowConfiguration) -> Dict[str, Any]:
        """Validate a flow configuration"""
        return self.config_manager.validate_configuration(flow_config)
    
    def get_analysis_statistics(self) -> Dict[str, Any]:
        """Get usage statistics and performance metrics"""
        return {
            'cached_results': len(self.results_cache),
            'available_flows': len(self.config_manager.list_configurations()),
            'available_templates': len(self.config_manager.list_templates()),
            'active_executions': len(self.orchestrator.active_executions)
        }
    
    async def test_tools_health(self) -> Dict[str, bool]:
        """Test the health of all individual tools"""
        health_status = {}
        
        # Create minimal test input
        test_input = ToolInput(
            headline="Test headline for health check",
            body_text="Test body text for tool health verification",
            cta="Test CTA",
            industry="test",
            platform="test",
            request_id="health_check"
        )
        
        # Test each tool individually
        tools_to_test = {
            'performance_forensics': PerformanceForensicsToolRunner,
            'psychology_scorer': PsychologyScorerToolRunner,
            'brand_voice_engine': BrandVoiceEngineToolRunner,
            'legal_risk_scanner': LegalRiskScannerToolRunner
        }
        
        for tool_name, tool_class in tools_to_test.items():
            try:
                tool_runner = tool_class(tool_class.default_config())
                result = await tool_runner.run(test_input)
                health_status[tool_name] = result.success
            except Exception as e:
                self.logger.warning(f"Tool health check failed for {tool_name}: {str(e)}")
                health_status[tool_name] = False
        
        return health_status
    
    def _convert_to_tool_input(self, request: AnalysisRequest) -> ToolInput:
        """Convert AnalysisRequest to ToolInput format"""
        return ToolInput(
            headline=request.headline,
            body_text=request.body_text,
            cta=request.cta,
            industry=request.industry,
            platform=request.platform,
            target_audience=request.target_audience,
            brand_guidelines=request.brand_guidelines or {},
            request_id=f"req_{int(time.time())}_{hash(request.headline)}"[:16],
            additional_data=request.request_metadata or {}
        )
    
    def _select_flow_configuration(self, request: AnalysisRequest) -> Union[str, FlowConfiguration]:
        """Select appropriate flow configuration based on request"""
        
        # Use custom flow if specified
        if request.custom_flow_id:
            custom_flow = self.config_manager.load_configuration(request.custom_flow_id)
            if custom_flow:
                return custom_flow
            else:
                self.logger.warning(f"Custom flow {request.custom_flow_id} not found, using default")
        
        # Map analysis type to predefined flow
        flow_name = self.analysis_type_mappings.get(request.analysis_type, 'comprehensive_analysis')
        
        # Return flow name (orchestrator will resolve it)
        return flow_name
    
    def _convert_to_analysis_response(self, flow_result: FlowExecutionResult, 
                                    request: AnalysisRequest, execution_time: float) -> AnalysisResponse:
        """Convert FlowExecutionResult to AnalysisResponse"""
        
        # Extract scores
        scores = flow_result.aggregated_scores
        overall_score = scores.get('overall_copy_quality', 0.0)
        performance_score = scores.get('overall_performance', 0.0)
        psychology_score = scores.get('overall_psychology', 0.0)
        brand_score = scores.get('overall_brand', 0.0)
        legal_score = scores.get('overall_legal', 0.0)
        
        # Extract insights
        strengths, weaknesses = self._extract_strengths_weaknesses(flow_result)
        recommendations = flow_result.combined_recommendations[:10]  # Top 10
        
        # Prepare detailed tool results
        tool_results = {}
        for tool_name, result in flow_result.tool_results.items():
            if result.success:
                tool_results[tool_name] = {
                    'scores': result.scores,
                    'insights': result.insights,
                    'recommendations': result.recommendations[:3]  # Top 3 per tool
                }
            else:
                tool_results[tool_name] = {
                    'error': result.error_message,
                    'success': False
                }
        
        # Handle errors and warnings
        errors = None
        warnings = None
        
        if not flow_result.success:
            errors = []
            if flow_result.error_summary:
                if 'fatal_error' in flow_result.error_summary:
                    errors.append(flow_result.error_summary['fatal_error'])
                if 'failed_tools' in flow_result.error_summary:
                    errors.extend([
                        f"Tool {tool} failed: {error}" 
                        for tool, error in flow_result.error_summary.get('error_details', {}).items()
                    ])
        
        return AnalysisResponse(
            success=flow_result.success,
            request_id=flow_result.execution_id,
            execution_time=execution_time,
            analysis_type=request.analysis_type,
            overall_score=overall_score,
            performance_score=performance_score,
            psychology_score=psychology_score,
            brand_score=brand_score,
            legal_score=legal_score,
            strengths=strengths,
            weaknesses=weaknesses,
            recommendations=recommendations,
            tool_results=tool_results,
            execution_metadata=flow_result.execution_metadata,
            errors=errors,
            warnings=warnings
        )
    
    def _extract_strengths_weaknesses(self, flow_result: FlowExecutionResult) -> tuple[List[str], List[str]]:
        """Extract strengths and weaknesses from analysis results"""
        strengths = []
        weaknesses = []
        
        # Analyze scores to determine strengths and weaknesses
        scores = flow_result.aggregated_scores
        
        # Performance analysis
        perf_score = scores.get('overall_performance', 0.0)
        if perf_score >= 80:
            strengths.append("Strong performance indicators - high CTR and conversion potential")
        elif perf_score <= 50:
            weaknesses.append("Performance concerns - may have low engagement potential")
        
        # Psychology analysis
        psych_score = scores.get('overall_psychology', 0.0)
        if psych_score >= 80:
            strengths.append("Excellent psychological appeal with strong persuasion elements")
        elif psych_score <= 50:
            weaknesses.append("Limited psychological impact - lacks persuasive elements")
        
        # Brand analysis
        brand_score = scores.get('overall_brand', 0.0)
        if brand_score >= 80:
            strengths.append("Strong brand alignment and consistent voice")
        elif brand_score <= 50:
            weaknesses.append("Brand voice inconsistency - may not align with guidelines")
        
        # Legal analysis
        legal_score = scores.get('overall_legal', 0.0)
        if legal_score >= 80:
            strengths.append("Low legal risk with compliant language")
        elif legal_score <= 50:
            weaknesses.append("Legal compliance concerns - contains risky claims")
        
        # Cross-tool insights
        if 'cross_tool_correlations' in flow_result.unified_insights:
            correlations = flow_result.unified_insights['cross_tool_correlations']
            
            perf_psych = correlations.get('performance_psychology_alignment', {})
            if perf_psych.get('correlation_strength', 0) > 0.8:
                strengths.append("Excellent alignment between performance potential and psychological appeal")
            elif perf_psych.get('correlation_strength', 0) < 0.5:
                weaknesses.append("Misalignment between performance and psychology - optimization needed")
        
        return strengths[:5], weaknesses[:5]  # Limit to top 5 each
    
    def _generate_cache_key(self, request: AnalysisRequest) -> str:
        """Generate cache key for request"""
        content_hash = hash(f"{request.headline}{request.body_text}{request.cta}")
        context_hash = hash(f"{request.industry}{request.platform}{request.analysis_type}")
        return f"cache_{content_hash}_{context_hash}"
    
    def _clean_cache(self):
        """Clean expired cache entries"""
        current_time = time.time()
        expired_keys = []
        
        for key, result in self.results_cache.items():
            cached_at = result.execution_metadata.get('cached_at', 0)
            if current_time - cached_at > self.cache_ttl:
                expired_keys.append(key)
        
        for key in expired_keys:
            del self.results_cache[key]
    
    def _ensure_default_configurations(self):
        """Ensure default flow configurations are available"""
        # This would check if default configurations exist and create them if not
        # For now, the orchestrator creates them automatically
        self.logger.info("Default flow configurations initialized")


# Convenience functions for common use cases
async def analyze_ad_copy(headline: str, body_text: str, cta: str,
                         industry: str = "", platform: str = "",
                         analysis_type: str = "comprehensive") -> AnalysisResponse:
    """
    Convenience function for quick ad copy analysis
    
    Args:
        headline: Ad headline text
        body_text: Main ad body text
        cta: Call-to-action text
        industry: Industry context (optional)
        platform: Platform context (optional)
        analysis_type: Type of analysis (comprehensive, quick, compliance, optimization)
    
    Returns:
        AnalysisResponse with complete analysis results
    """
    service = UnifiedToolsService()
    
    request = AnalysisRequest(
        headline=headline,
        body_text=body_text,
        cta=cta,
        industry=industry,
        platform=platform,
        analysis_type=analysis_type
    )
    
    return await service.analyze_copy(request)


async def quick_performance_check(headline: str, body_text: str, cta: str) -> Dict[str, Any]:
    """
    Quick performance analysis focusing on CTR and conversion potential
    
    Returns simplified results focusing on performance metrics
    """
    result = await analyze_ad_copy(headline, body_text, cta, analysis_type="quick")
    
    return {
        'overall_score': result.overall_score,
        'performance_score': result.performance_score,
        'psychology_score': result.psychology_score,
        'top_recommendations': result.recommendations[:3],
        'execution_time': result.execution_time,
        'success': result.success
    }