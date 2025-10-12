"""
Tools Orchestrator Module - Unified Ad Copy Analysis System

This module provides a complete orchestration system for coordinating multiple
ad copy analysis tools, managing configurations, and delivering unified results.

Key Components:
- ToolsFlowOrchestrator: Coordinates multiple tools with parallel/sequential execution
- FlowConfigurationManager: Manages and persists flow configurations
- UnifiedToolsService: Main API interface with simplified analysis requests

Main Classes:
- UnifiedToolsService: Primary interface for ad copy analysis
- AnalysisRequest: Simplified request structure
- AnalysisResponse: Unified response with aggregated insights
- FlowConfiguration: Tool flow definition and configuration
- FlowTemplate: Reusable flow templates

Pre-defined Flow Types:
- comprehensive: Complete analysis using all tools (Performance + Psychology + Brand + Legal)
- quick: Fast performance and psychology analysis for quick optimization
- compliance: Brand alignment and legal compliance focused
- optimization: Deep dive into performance metrics and psychological triggers

Usage:
    from tools_sdk.orchestrator import UnifiedToolsService, AnalysisRequest
    
    # Simple analysis
    service = UnifiedToolsService()
    request = AnalysisRequest(
        headline="Your headline here",
        body_text="Your body text here", 
        cta="Your CTA here",
        analysis_type="comprehensive"
    )
    result = await service.analyze_copy(request)
    
    # Or use convenience function
    from tools_sdk.orchestrator import analyze_ad_copy
    result = await analyze_ad_copy("headline", "body", "cta", analysis_type="quick")
"""

from .tools_flow_orchestrator import (
    ToolsFlowOrchestrator,
    FlowConfiguration,
    ToolFlowStep,
    FlowExecutionStrategy,
    FlowPriority,
    FlowExecutionResult
)

from .flow_config_manager import (
    FlowConfigurationManager,
    FlowTemplate,
    FlowConfigurationHistory
)

from .unified_tools_service import (
    UnifiedToolsService,
    AnalysisRequest,
    AnalysisResponse,
    analyze_ad_copy,
    quick_performance_check
)

# Version information
__version__ = "1.0.0"
__author__ = "AdCopySurge Team"

# Main exports for easy access
__all__ = [
    # Main service classes
    "UnifiedToolsService",
    "ToolsFlowOrchestrator",
    "FlowConfigurationManager",
    
    # Request/Response structures
    "AnalysisRequest", 
    "AnalysisResponse",
    "FlowExecutionResult",
    
    # Configuration structures
    "FlowConfiguration",
    "ToolFlowStep", 
    "FlowTemplate",
    "FlowConfigurationHistory",
    
    # Enums
    "FlowExecutionStrategy",
    "FlowPriority",
    
    # Convenience functions
    "analyze_ad_copy",
    "quick_performance_check"
]

# Pre-defined analysis types for convenience
ANALYSIS_TYPES = {
    "comprehensive": "Complete analysis using all tools for maximum insights",
    "quick": "Fast performance and psychology analysis for quick optimization", 
    "compliance": "Focus on brand alignment and legal compliance",
    "optimization": "Deep dive into performance metrics and psychological triggers"
}

# Tool execution strategies
EXECUTION_STRATEGIES = {
    "sequential": FlowExecutionStrategy.SEQUENTIAL,
    "parallel": FlowExecutionStrategy.PARALLEL,
    "mixed": FlowExecutionStrategy.MIXED
}

# Flow priorities
PRIORITIES = {
    "low": FlowPriority.LOW,
    "normal": FlowPriority.NORMAL,
    "high": FlowPriority.HIGH,
    "critical": FlowPriority.CRITICAL
}


def create_service(config_directory: str = None, max_workers: int = 4) -> UnifiedToolsService:
    """
    Factory function to create a UnifiedToolsService instance
    
    Args:
        config_directory: Directory for storing flow configurations
        max_workers: Maximum parallel workers for tool execution
        
    Returns:
        Configured UnifiedToolsService instance
    """
    return UnifiedToolsService(config_directory=config_directory, max_workers=max_workers)


def get_available_analysis_types() -> dict:
    """Get available analysis types and their descriptions"""
    return ANALYSIS_TYPES.copy()


def get_execution_strategies() -> dict:
    """Get available execution strategies"""
    return EXECUTION_STRATEGIES.copy()


def get_priorities() -> dict:
    """Get available flow priorities"""
    return PRIORITIES.copy()


# Module level convenience functions for direct import
async def comprehensive_analysis(headline: str, body_text: str, cta: str, 
                               industry: str = "", platform: str = "") -> AnalysisResponse:
    """Comprehensive analysis using all tools"""
    return await analyze_ad_copy(headline, body_text, cta, industry, platform, "comprehensive")


async def quick_analysis(headline: str, body_text: str, cta: str,
                        industry: str = "", platform: str = "") -> AnalysisResponse:
    """Quick performance and psychology analysis"""
    return await analyze_ad_copy(headline, body_text, cta, industry, platform, "quick")


async def compliance_analysis(headline: str, body_text: str, cta: str,
                            industry: str = "", platform: str = "") -> AnalysisResponse:
    """Brand and legal compliance analysis"""
    return await analyze_ad_copy(headline, body_text, cta, industry, platform, "compliance")


async def optimization_analysis(headline: str, body_text: str, cta: str,
                              industry: str = "", platform: str = "") -> AnalysisResponse:
    """Performance optimization focused analysis"""
    return await analyze_ad_copy(headline, body_text, cta, industry, platform, "optimization")


# Add convenience functions to __all__
__all__.extend([
    "create_service",
    "get_available_analysis_types", 
    "get_execution_strategies",
    "get_priorities",
    "comprehensive_analysis",
    "quick_analysis",
    "compliance_analysis", 
    "optimization_analysis",
    "ANALYSIS_TYPES",
    "EXECUTION_STRATEGIES",
    "PRIORITIES"
])