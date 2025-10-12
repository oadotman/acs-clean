"""
AdCopySurge Tools SDK - Unified Tool Integration Framework

This package provides a thin SDK that wraps all analysis tools with a consistent interface.
The orchestrator can chain tools consistently using the unified ToolRunner interface.
"""

from .core import ToolRunner, ToolInput, ToolOutput, ToolConfig, ToolType
from .registry import ToolRegistry, default_registry
from .tool_orchestrator import ToolOrchestrator, OrchestrationResult
from .exceptions import ToolError, ToolTimeoutError, ToolConfigError

__version__ = "1.0.0"
__all__ = [
    "ToolRunner",
    "ToolInput", 
    "ToolOutput",
    "ToolConfig",
    "ToolType",
    "ToolRegistry",
    "default_registry",
    "ToolOrchestrator",
    "OrchestrationResult",
    "ToolError",
    "ToolTimeoutError", 
    "ToolConfigError"
]
