"""
Exception classes for unified tool error handling
"""

from typing import Optional, Dict, Any


class ToolError(Exception):
    """Base exception for all tool-related errors"""
    
    def __init__(
        self,
        message: str,
        tool_name: Optional[str] = None,
        error_code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message)
        self.message = message
        self.tool_name = tool_name
        self.error_code = error_code
        self.details = details or {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert exception to dictionary for serialization"""
        return {
            'error_type': self.__class__.__name__,
            'message': self.message,
            'tool_name': self.tool_name,
            'error_code': self.error_code,
            'details': self.details
        }


class ToolTimeoutError(ToolError):
    """Raised when a tool execution times out"""
    
    def __init__(self, tool_name: str, timeout: float):
        super().__init__(
            f"Tool '{tool_name}' timed out after {timeout} seconds",
            tool_name=tool_name,
            error_code="TOOL_TIMEOUT"
        )
        self.timeout = timeout


class ToolConfigError(ToolError):
    """Raised when there's an issue with tool configuration"""
    
    def __init__(self, tool_name: str, config_issue: str):
        super().__init__(
            f"Configuration error for tool '{tool_name}': {config_issue}",
            tool_name=tool_name,
            error_code="TOOL_CONFIG_ERROR"
        )


class ToolValidationError(ToolError):
    """Raised when input validation fails"""
    
    def __init__(self, tool_name: str, validation_issue: str, missing_fields: list = None):
        super().__init__(
            f"Input validation failed for tool '{tool_name}': {validation_issue}",
            tool_name=tool_name,
            error_code="TOOL_VALIDATION_ERROR",
            details={'missing_fields': missing_fields or []}
        )


class ToolExecutionError(ToolError):
    """Raised when tool execution fails"""
    
    def __init__(self, tool_name: str, execution_error: str, original_exception: Exception = None):
        super().__init__(
            f"Execution failed for tool '{tool_name}': {execution_error}",
            tool_name=tool_name,
            error_code="TOOL_EXECUTION_ERROR",
            details={'original_exception': str(original_exception) if original_exception else None}
        )
        self.original_exception = original_exception


class ToolDependencyError(ToolError):
    """Raised when a tool dependency is missing or unavailable"""
    
    def __init__(self, tool_name: str, dependency: str, suggestion: str = None):
        message = f"Missing dependency for tool '{tool_name}': {dependency}"
        if suggestion:
            message += f". {suggestion}"
        
        super().__init__(
            message,
            tool_name=tool_name,
            error_code="TOOL_DEPENDENCY_ERROR",
            details={'missing_dependency': dependency, 'suggestion': suggestion}
        )


class ToolApiError(ToolError):
    """Raised when external API calls fail"""
    
    def __init__(self, tool_name: str, api_name: str, api_error: str, status_code: int = None):
        super().__init__(
            f"API error in tool '{tool_name}' calling {api_name}: {api_error}",
            tool_name=tool_name,
            error_code="TOOL_API_ERROR",
            details={'api_name': api_name, 'status_code': status_code, 'api_error': api_error}
        )