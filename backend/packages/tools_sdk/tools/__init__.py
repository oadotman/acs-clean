"""
Tools package initialization with tool registration

This module automatically registers all available SDK-compatible tools
"""

from ..registry import default_registry
from ..core import ToolConfig, ToolType

# Import available tool runners for all 9 core tools
from .ad_copy_analyzer_tool import AdCopyAnalyzerToolRunner
from .compliance_checker_tool import ComplianceCheckerToolRunner
from .psychology_scorer_tool import PsychologyScorerToolRunner
from .ab_test_generator_tool import ABTestGeneratorToolRunner
from .roi_copy_generator_tool import ROICopyGeneratorToolRunner
from .industry_optimizer_tool import IndustryOptimizerToolRunner
from .performance_forensics_tool import PerformanceForensicsToolRunner
from .brand_voice_engine_tool import BrandVoiceEngineToolRunner
from .legal_risk_scanner_tool import LegalRiskScannerToolRunner

# Legacy tools removed - all functionality integrated into core 9 tools

# Tool registration function
def register_all_tools():
    """Register all 9 core AdCopySurge tools with the default registry"""
    
    # Core 9 Tools from Landing Page
    core_tools = [
        (AdCopyAnalyzerToolRunner, "Ad Copy Analyzer"),
        (ComplianceCheckerToolRunner, "Compliance Checker"),
        (PsychologyScorerToolRunner, "Psychology Scorer"),
        (ABTestGeneratorToolRunner, "A/B Test Generator"),
        (ROICopyGeneratorToolRunner, "ROI Copy Generator"),
        (IndustryOptimizerToolRunner, "Industry Optimizer"),
        (PerformanceForensicsToolRunner, "Performance Forensics"),
        (BrandVoiceEngineToolRunner, "Brand Voice Engine"),
        (LegalRiskScannerToolRunner, "Legal Risk Scanner")
    ]
    
    registered_count = 0
    
    for tool_class, tool_name in core_tools:
        try:
            config = tool_class.default_config()
            default_registry.register_tool(tool_class, config, replace_existing=True)
            print(f"[SUCCESS] Registered {tool_name}: {config.name}")
            registered_count += 1
        except Exception as e:
            print(f"[ERROR] Failed to register {tool_name}: {e}")
    
    # Legacy compatibility tools removed - functionality integrated into core 9 tools
    
    print(f"[INFO] Tool registration complete: {registered_count} tools registered")
    return registered_count

# Auto-register tools when module is imported
register_all_tools()

# Export the tools for direct import
__all__ = [
    # Core 9 Tools
    'AdCopyAnalyzerToolRunner',
    'ComplianceCheckerToolRunner', 
    'PsychologyScorerToolRunner',
    'ABTestGeneratorToolRunner',
    'ROICopyGeneratorToolRunner',
    'IndustryOptimizerToolRunner',
    'PerformanceForensicsToolRunner',
    'BrandVoiceEngineToolRunner',
    'LegalRiskScannerToolRunner',
    # Registration function
    'register_all_tools'
]
