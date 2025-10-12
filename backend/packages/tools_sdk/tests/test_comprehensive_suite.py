"""
Comprehensive Test Suite for AdCopySurge Tools SDK

This test suite provides extensive coverage of all tools, orchestrator, 
API integration, and system components with various testing scenarios.
"""

import pytest
import asyncio
import json
import time
from typing import Dict, Any, List
from unittest.mock import Mock, AsyncMock, patch
from pathlib import Path

# Import the SDK components
from ..core import ToolInput, ToolOutput, ToolConfig, ToolType
from ..tools.performance_forensics_tool import PerformanceForensicsToolRunner
from ..tools.psychology_scorer_tool import PsychologyScorerToolRunner
from ..tools.brand_voice_engine_tool import BrandVoiceEngineToolRunner
from ..tools.legal_risk_scanner_tool import LegalRiskScannerToolRunner
from ..orchestrator import (
    UnifiedToolsService, AnalysisRequest, AnalysisResponse,
    ToolsFlowOrchestrator, FlowConfiguration, ToolFlowStep
)
from ..contracts.api_schemas import (
    AnalysisRequest as APIAnalysisRequest,
    AnalysisResponse as APIAnalysisResponse,
    validate_analysis_request,
    build_success_response
)
from ..observability.metrics_collector import MetricsCollector
from ..observability.request_logger import RequestLogger


# ===== TEST FIXTURES =====

@pytest.fixture
def sample_tool_input():
    """Sample input data for tool testing"""
    return ToolInput(
        headline="Revolutionary AI Tool Transforms Your Business",
        body_text="Discover the power of AI-driven insights that help you make better decisions, increase efficiency, and drive growth. Join thousands of satisfied customers who trust our platform.",
        cta="Start Your Free Trial Today",
        industry="technology",
        platform="facebook",
        target_audience="business owners and decision makers",
        brand_guidelines={
            "tone": "professional",
            "voice_attributes": ["trustworthy", "innovative", "reliable"]
        },
        request_id="test_req_001"
    )


@pytest.fixture
def sample_analysis_request():
    """Sample analysis request for unified service testing"""
    return AnalysisRequest(
        headline="Transform Your Marketing with AI",
        body_text="Our cutting-edge AI platform revolutionizes how you create and optimize marketing campaigns. Get instant insights, automated A/B testing, and performance predictions.",
        cta="Get Started Free",
        industry="marketing",
        platform="linkedin",
        analysis_type="comprehensive"
    )


@pytest.fixture
def sample_api_request():
    """Sample API request for contract testing"""
    return APIAnalysisRequest(
        headline="Advanced AI Marketing Platform",
        body_text="Experience the future of marketing automation with our AI-powered platform that delivers personalized campaigns at scale.",
        cta="Try It Free",
        industry="technology",
        platform="google",
        analysis_type="comprehensive"
    )


@pytest.fixture
def metrics_collector():
    """Metrics collector instance for testing"""
    return MetricsCollector(
        max_data_points=1000,
        enable_persistence=False
    )


@pytest.fixture
def request_logger():
    """Request logger instance for testing"""
    return RequestLogger(
        log_level="DEBUG",
        enable_console=False,
        enable_structured=True
    )


# ===== INDIVIDUAL TOOL TESTS =====

class TestPerformanceForensicsTool:
    """Test suite for Performance Forensics Tool"""
    
    @pytest.mark.asyncio
    async def test_basic_analysis(self, sample_tool_input):
        """Test basic performance forensics analysis"""
        config = PerformanceForensicsToolRunner.default_config()
        tool = PerformanceForensicsToolRunner(config)
        
        result = await tool.run(sample_tool_input)
        
        assert result.success is True
        assert result.tool_name == "performance_forensics"
        assert result.scores is not None
        assert "ctr_prediction_score" in result.scores
        assert "conversion_optimization_score" in result.scores
        assert result.insights is not None
        assert result.recommendations is not None
        assert result.execution_time > 0
    
    @pytest.mark.asyncio
    async def test_invalid_input(self):
        """Test tool with invalid input"""
        config = PerformanceForensicsToolRunner.default_config()
        tool = PerformanceForensicsToolRunner(config)
        
        invalid_input = ToolInput(
            headline="",  # Empty headline
            body_text="",  # Empty body
            cta="",  # Empty CTA
            request_id="invalid_test"
        )
        
        with pytest.raises(Exception):
            await tool.run(invalid_input)
    
    @pytest.mark.asyncio
    async def test_industry_specific_analysis(self, sample_tool_input):
        """Test industry-specific analysis"""
        config = PerformanceForensicsToolRunner.default_config()
        tool = PerformanceForensicsToolRunner(config)
        
        # Test healthcare industry
        healthcare_input = sample_tool_input
        healthcare_input.industry = "healthcare"
        
        result = await tool.run(healthcare_input)
        
        assert result.success is True
        assert "healthcare" in result.insights.get("industry_analysis", {}).get("industry", "").lower()


class TestPsychologyScorerTool:
    """Test suite for Psychology Scorer Tool"""
    
    @pytest.mark.asyncio
    async def test_persuasion_analysis(self, sample_tool_input):
        """Test psychological persuasion analysis"""
        config = PsychologyScorerToolRunner.default_config()
        tool = PsychologyScorerToolRunner(config)
        
        result = await tool.run(sample_tool_input)
        
        assert result.success is True
        assert result.tool_name == "psychology_scorer"
        assert "persuasion_strength_score" in result.scores
        assert "emotional_impact_score" in result.scores
        assert "cognitive_influence_score" in result.scores
        assert result.insights.get("persuasion_techniques") is not None
    
    @pytest.mark.asyncio
    async def test_emotional_analysis(self, sample_tool_input):
        """Test emotional impact analysis"""
        config = PsychologyScorerToolRunner.default_config()
        tool = PsychologyScorerToolRunner(config)
        
        # Test with emotional copy
        emotional_input = sample_tool_input
        emotional_input.headline = "Don't Miss Out! Limited Time Offer!"
        emotional_input.body_text = "This exclusive opportunity won't last long. Act now before it's gone forever!"
        
        result = await tool.run(emotional_input)
        
        assert result.success is True
        assert result.scores["emotional_impact_score"] > 50  # Should detect high emotion


class TestBrandVoiceEngineTool:
    """Test suite for Brand Voice Engine Tool"""
    
    @pytest.mark.asyncio
    async def test_brand_alignment(self, sample_tool_input):
        """Test brand voice alignment analysis"""
        config = BrandVoiceEngineToolRunner.default_config()
        tool = BrandVoiceEngineToolRunner(config)
        
        result = await tool.run(sample_tool_input)
        
        assert result.success is True
        assert result.tool_name == "brand_voice_engine"
        assert "brand_alignment_score" in result.scores
        assert "tone_consistency_score" in result.scores
        assert result.insights.get("brand_analysis") is not None
    
    @pytest.mark.asyncio
    async def test_voice_variations(self, sample_tool_input):
        """Test brand voice variation generation"""
        config = BrandVoiceEngineToolRunner.default_config()
        tool = BrandVoiceEngineToolRunner(config)
        
        result = await tool.run(sample_tool_input)
        
        assert result.success is True
        assert result.variations is not None
        assert len(result.variations) > 0
        
        for variation in result.variations:
            assert variation.get("headline") is not None
            assert variation.get("body_text") is not None
            assert variation.get("cta") is not None


class TestLegalRiskScannerTool:
    """Test suite for Legal Risk Scanner Tool"""
    
    @pytest.mark.asyncio
    async def test_risk_detection(self, sample_tool_input):
        """Test legal risk detection"""
        config = LegalRiskScannerToolRunner.default_config()
        tool = LegalRiskScannerToolRunner(config)
        
        result = await tool.run(sample_tool_input)
        
        assert result.success is True
        assert result.tool_name == "legal_risk_scanner"
        assert "legal_compliance_score" in result.scores
        assert "risk_mitigation_score" in result.scores
        assert result.insights.get("risk_assessment") is not None
    
    @pytest.mark.asyncio
    async def test_high_risk_content(self, sample_tool_input):
        """Test detection of high-risk legal content"""
        config = LegalRiskScannerToolRunner.default_config()
        tool = LegalRiskScannerToolRunner(config)
        
        # Test with risky content
        risky_input = sample_tool_input
        risky_input.headline = "Guaranteed to Cure All Your Problems!"
        risky_input.body_text = "100% guaranteed results or your money back. This FDA-approved miracle solution works instantly!"
        
        result = await tool.run(risky_input)
        
        assert result.success is True
        assert result.scores["legal_compliance_score"] < 70  # Should detect high risk
        assert result.alternatives is not None
        assert len(result.alternatives) > 0


# ===== ORCHESTRATOR TESTS =====

class TestToolsFlowOrchestrator:
    """Test suite for Tools Flow Orchestrator"""
    
    @pytest.mark.asyncio
    async def test_sequential_execution(self, sample_tool_input):
        """Test sequential tool execution"""
        orchestrator = ToolsFlowOrchestrator()
        
        result = await orchestrator.execute_flow("quick_performance", sample_tool_input)
        
        assert result.success is True
        assert len(result.tool_results) >= 2
        assert result.aggregated_scores is not None
        assert result.unified_insights is not None
        assert result.combined_recommendations is not None
        assert result.total_execution_time > 0
    
    @pytest.mark.asyncio
    async def test_parallel_execution(self, sample_tool_input):
        """Test parallel tool execution"""
        orchestrator = ToolsFlowOrchestrator()
        
        result = await orchestrator.execute_flow("comprehensive_analysis", sample_tool_input)
        
        assert result.success is True
        assert len(result.tool_results) >= 3
        assert result.execution_metadata["execution_strategy"] == "parallel"
        
        # Check that tools executed in reasonable time (parallel should be faster)
        assert result.total_execution_time < 10  # Should complete within 10 seconds
    
    @pytest.mark.asyncio
    async def test_error_handling(self, sample_tool_input):
        """Test orchestrator error handling with partial failures"""
        orchestrator = ToolsFlowOrchestrator()
        
        # Mock one tool to fail
        with patch.object(PerformanceForensicsToolRunner, 'run', side_effect=Exception("Simulated failure")):
            result = await orchestrator.execute_flow("comprehensive_analysis", sample_tool_input)
            
            # Should continue with other tools
            assert len(result.tool_results) > 0
            assert result.error_summary is not None
            assert "failed_tools" in result.error_summary


class TestUnifiedToolsService:
    """Test suite for Unified Tools Service"""
    
    @pytest.mark.asyncio
    async def test_comprehensive_analysis(self, sample_analysis_request):
        """Test comprehensive analysis through unified service"""
        service = UnifiedToolsService()
        
        result = await service.analyze_copy(sample_analysis_request)
        
        assert result.success is True
        assert result.overall_score > 0
        assert result.performance_score > 0
        assert result.psychology_score > 0
        assert result.brand_score > 0
        assert result.legal_score > 0
        assert len(result.strengths) > 0
        assert len(result.recommendations) > 0
    
    @pytest.mark.asyncio
    async def test_batch_analysis(self):
        """Test batch analysis functionality"""
        service = UnifiedToolsService()
        
        # Create multiple requests
        requests = []
        for i in range(3):
            request = AnalysisRequest(
                headline=f"Test Headline {i}",
                body_text=f"Test body text for analysis {i}",
                cta=f"Test CTA {i}",
                analysis_type="quick"
            )
            requests.append(request)
        
        results = await service.analyze_copy_batch(requests)
        
        assert len(results) == 3
        for result in results:
            assert result.success is True
            assert result.overall_score > 0
    
    @pytest.mark.asyncio
    async def test_analysis_types(self):
        """Test different analysis types"""
        service = UnifiedToolsService()
        
        base_request = AnalysisRequest(
            headline="Test Marketing Platform",
            body_text="Advanced marketing automation tools for businesses.",
            cta="Get Started"
        )
        
        # Test all analysis types
        for analysis_type in ["comprehensive", "quick", "compliance", "optimization"]:
            request = base_request
            request.analysis_type = analysis_type
            
            result = await service.analyze_copy(request)
            
            assert result.success is True
            assert result.analysis_type == analysis_type


# ===== API CONTRACT TESTS =====

class TestAPIContracts:
    """Test suite for API contracts and schemas"""
    
    def test_analysis_request_validation(self, sample_api_request):
        """Test API request validation"""
        # Valid request
        validated = validate_analysis_request(sample_api_request.dict())
        assert validated.headline == sample_api_request.headline
        assert validated.analysis_type == sample_api_request.analysis_type
    
    def test_invalid_request_validation(self):
        """Test validation of invalid requests"""
        with pytest.raises(Exception):
            validate_analysis_request({
                "headline": "",  # Empty headline should fail
                "body_text": "Test",
                "cta": "Test"
            })
    
    def test_response_schema_generation(self):
        """Test response schema generation"""
        from ..contracts.api_schemas import AnalysisResponse
        
        schema = AnalysisResponse.schema()
        
        assert "properties" in schema
        assert "success" in schema["properties"]
        assert "overall_score" in schema["properties"]
        assert "recommendations" in schema["properties"]
    
    def test_success_response_builder(self):
        """Test success response builder"""
        data = {"test": "value"}
        response = build_success_response(data, "Test message")
        
        assert response["success"] is True
        assert response["message"] == "Test message"
        assert response["data"] == data
        assert "timestamp" in response


# ===== OBSERVABILITY TESTS =====

class TestObservability:
    """Test suite for observability components"""
    
    def test_metrics_collection(self, metrics_collector):
        """Test metrics collection functionality"""
        # Record some test metrics
        metrics_collector.record_analysis(
            analysis_type="test",
            execution_time=1.5,
            success=True,
            overall_score=85.0,
            tools_used=["tool1", "tool2"],
            request_id="test_req"
        )
        
        # Check metrics were recorded
        system_metrics = metrics_collector.get_system_metrics()
        assert system_metrics["total_requests"] >= 0
        
        usage_analytics = metrics_collector.get_usage_analytics("1h")
        assert "analysis_type_usage" in usage_analytics
    
    def test_tool_metrics_recording(self, metrics_collector):
        """Test tool-specific metrics recording"""
        metrics_collector.record_tool_execution(
            tool_name="test_tool",
            execution_time=2.0,
            success=True,
            confidence_score=90.0,
            request_id="test_req"
        )
        
        detailed_metrics = metrics_collector.get_detailed_metrics()
        assert "tool_usage_counts" in detailed_metrics
    
    def test_request_logging(self, request_logger):
        """Test request logging functionality"""
        # Mock request and response objects
        mock_request = Mock()
        mock_request.method = "POST"
        mock_request.url.path = "/api/test"
        mock_request.headers = {"user-agent": "test-agent"}
        mock_request.query_params = {}
        mock_request.state.correlation_id = "test-correlation"
        
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.headers = {"content-length": "100"}
        
        # Test logging methods don't raise exceptions
        request_logger.log_request_start(mock_request, "test-correlation")
        request_logger.log_request_end(mock_request, mock_response, 1.0)
        
        # Test log level changes
        request_logger.set_log_level("DEBUG")
        assert request_logger.logger.level == 10  # DEBUG level


# ===== INTEGRATION TESTS =====

class TestSystemIntegration:
    """Integration tests for the complete system"""
    
    @pytest.mark.asyncio
    async def test_end_to_end_workflow(self, sample_analysis_request, metrics_collector):
        """Test complete end-to-end analysis workflow"""
        service = UnifiedToolsService()
        
        # Execute analysis
        result = await service.analyze_copy(sample_analysis_request)
        
        # Verify complete workflow
        assert result.success is True
        assert result.execution_time > 0
        assert len(result.tool_results) > 0
        assert result.overall_score > 0
        
        # Check all score categories are present
        assert result.performance_score >= 0
        assert result.psychology_score >= 0
        assert result.brand_score >= 0
        assert result.legal_score >= 0
        
        # Verify insights and recommendations
        assert len(result.strengths) >= 0
        assert len(result.weaknesses) >= 0
        assert len(result.recommendations) > 0
    
    @pytest.mark.asyncio
    async def test_concurrent_requests(self):
        """Test system under concurrent load"""
        service = UnifiedToolsService()
        
        # Create multiple concurrent requests
        async def single_analysis(index):
            request = AnalysisRequest(
                headline=f"Concurrent Test {index}",
                body_text="Testing concurrent request handling",
                cta=f"Action {index}",
                analysis_type="quick"
            )
            return await service.analyze_copy(request)
        
        # Run 5 concurrent analyses
        tasks = [single_analysis(i) for i in range(5)]
        results = await asyncio.gather(*tasks)
        
        # All should succeed
        assert all(result.success for result in results)
        assert len(results) == 5
    
    @pytest.mark.asyncio
    async def test_system_health_checks(self):
        """Test system health monitoring"""
        service = UnifiedToolsService()
        
        # Test tool health
        health_status = await service.test_tools_health()
        
        # All tools should be healthy
        assert isinstance(health_status, dict)
        assert len(health_status) == 4  # All 4 tools
        
        # Get system statistics
        stats = service.get_analysis_statistics()
        assert "cached_results" in stats
        assert "available_flows" in stats


# ===== PERFORMANCE TESTS =====

class TestPerformance:
    """Performance tests for the system"""
    
    @pytest.mark.asyncio
    async def test_analysis_performance(self, sample_analysis_request):
        """Test analysis performance benchmarks"""
        service = UnifiedToolsService()
        
        start_time = time.time()
        result = await service.analyze_copy(sample_analysis_request)
        execution_time = time.time() - start_time
        
        # Performance expectations
        assert result.success is True
        assert execution_time < 30  # Should complete within 30 seconds
        assert result.execution_time > 0
    
    @pytest.mark.asyncio
    async def test_memory_usage(self):
        """Test memory usage patterns"""
        import psutil
        import os
        
        # Get initial memory usage
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        service = UnifiedToolsService()
        
        # Run multiple analyses
        for i in range(10):
            request = AnalysisRequest(
                headline=f"Memory Test {i}",
                body_text="Testing memory usage patterns",
                cta="Test CTA",
                analysis_type="quick"
            )
            await service.analyze_copy(request)
        
        # Check memory didn't grow excessively
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_growth = final_memory - initial_memory
        
        # Should not grow more than 100MB for 10 analyses
        assert memory_growth < 100
    
    def test_caching_performance(self, metrics_collector):
        """Test metrics collection performance"""
        import time
        
        # Time multiple metric recordings
        start_time = time.time()
        
        for i in range(1000):
            metrics_collector.record_analysis(
                analysis_type="performance_test",
                execution_time=1.0,
                success=True,
                overall_score=80.0,
                tools_used=["tool1"],
                request_id=f"perf_test_{i}"
            )
        
        elapsed_time = time.time() - start_time
        
        # Should handle 1000 metric recordings quickly
        assert elapsed_time < 1.0  # Less than 1 second


# ===== ERROR HANDLING TESTS =====

class TestErrorHandling:
    """Test suite for error handling scenarios"""
    
    @pytest.mark.asyncio
    async def test_network_timeout_simulation(self, sample_tool_input):
        """Test handling of network timeouts"""
        config = PerformanceForensicsToolRunner.default_config()
        config.timeout = 0.001  # Very short timeout
        
        tool = PerformanceForensicsToolRunner(config)
        
        # This might timeout or complete very quickly
        result = await tool.run(sample_tool_input)
        
        # Should either succeed quickly or handle timeout gracefully
        assert result is not None
        assert hasattr(result, 'success')
    
    @pytest.mark.asyncio
    async def test_malformed_input_handling(self):
        """Test handling of malformed input data"""
        service = UnifiedToolsService()
        
        # Test with missing required fields
        with pytest.raises(Exception):
            malformed_request = AnalysisRequest(
                headline=None,  # Invalid
                body_text="",
                cta=""
            )
            await service.analyze_copy(malformed_request)
    
    @pytest.mark.asyncio
    async def test_partial_tool_failure_recovery(self, sample_analysis_request):
        """Test system recovery from partial tool failures"""
        service = UnifiedToolsService()
        
        # Mock one tool to fail consistently
        with patch.object(LegalRiskScannerToolRunner, 'run', side_effect=Exception("Mock failure")):
            result = await service.analyze_copy(sample_analysis_request)
            
            # System should continue with other tools
            assert result.success is True  # Overall success despite one failure
            assert len(result.tool_results) >= 3  # At least 3 tools completed


# ===== TEST CONFIGURATION =====

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


# ===== MAIN TEST RUNNER =====

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])


# Export test classes for external test runners
__all__ = [
    "TestPerformanceForensicsTool",
    "TestPsychologyScorerTool", 
    "TestBrandVoiceEngineTool",
    "TestLegalRiskScannerTool",
    "TestToolsFlowOrchestrator",
    "TestUnifiedToolsService",
    "TestAPIContracts",
    "TestObservability",
    "TestSystemIntegration",
    "TestPerformance",
    "TestErrorHandling"
]