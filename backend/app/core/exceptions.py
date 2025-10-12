"""
Production Exception Classes for AdCopySurge
Ensures all failures result in proper errors rather than fallback to mock data
"""

import uuid
from datetime import datetime
from typing import Optional, Dict, Any


class ProductionError(Exception):
    """
    Base production error class - never allow fallback to mock data
    All production errors should inherit from this to ensure proper handling
    """
    def __init__(self, message: str, error_code: str = None, context: Dict[str, Any] = None):
        super().__init__(message)
        self.message = message
        self.error_code = error_code or self.__class__.__name__
        self.context = context or {}
        self.timestamp = datetime.utcnow()
        self.request_id = str(uuid.uuid4())
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert error to dictionary for logging/API responses"""
        return {
            "error_code": self.error_code,
            "message": self.message,
            "timestamp": self.timestamp.isoformat(),
            "request_id": self.request_id,
            "context": self.context
        }


class ProductionAnalysisError(ProductionError):
    """
    Analysis pipeline failure - fail fast with proper error codes
    Never fallback to template alternatives or default scores
    """
    def __init__(self, message: str, user_id: str = None, ad_text: str = None, 
                 failed_tools: list = None, error_code: str = None):
        context = {
            "user_id": user_id,
            "ad_text_preview": ad_text[:100] if ad_text else None,
            "failed_tools": failed_tools or [],
            "service": "analysis_pipeline"
        }
        super().__init__(message, error_code or "ANALYSIS_FAILED", context)
        self.user_id = user_id
        self.ad_text = ad_text
        self.failed_tools = failed_tools or []


class AIProviderUnavailable(ProductionError):
    """
    AI provider is down or failed - don't use template alternatives
    This should result in a 503 Service Unavailable response
    """
    def __init__(self, provider_name: str, reason: str = None, retry_after: int = None):
        message = f"AI provider '{provider_name}' is unavailable"
        if reason:
            message += f": {reason}"
            
        context = {
            "provider": provider_name,
            "reason": reason,
            "retry_after_seconds": retry_after,
            "service": "ai_generation"
        }
        super().__init__(message, "AI_PROVIDER_UNAVAILABLE", context)
        self.provider_name = provider_name
        self.retry_after = retry_after


class ToolsSDKError(ProductionError):
    """
    Tools SDK execution failure - don't fallback to legacy services
    All tools must execute successfully or analysis should fail
    """
    def __init__(self, tool_name: str, reason: str, tool_output: Dict[str, Any] = None):
        message = f"Tools SDK tool '{tool_name}' failed: {reason}"
        
        context = {
            "tool_name": tool_name,
            "tool_output": tool_output,
            "service": "tools_sdk"
        }
        super().__init__(message, "TOOLS_SDK_FAILED", context)
        self.tool_name = tool_name
        self.tool_output = tool_output or {}


class DatabaseConstraintError(ProductionError):
    """
    Database validation failed - don't insert bad data
    Production should enforce strict data constraints
    """
    def __init__(self, constraint: str, table: str, data: Dict[str, Any] = None):
        message = f"Database constraint '{constraint}' failed for table '{table}'"
        
        context = {
            "constraint": constraint,
            "table": table,
            "attempted_data": data,
            "service": "database"
        }
        super().__init__(message, "DATABASE_CONSTRAINT_FAILED", context)
        self.constraint = constraint
        self.table = table


class ConfigurationError(ProductionError):
    """
    Missing or invalid configuration - fail fast on startup
    Don't allow production to run with invalid configs
    """
    def __init__(self, config_key: str, reason: str, required_value: str = None):
        message = f"Configuration error for '{config_key}': {reason}"
        
        context = {
            "config_key": config_key,
            "required_value": required_value,
            "service": "configuration"
        }
        super().__init__(message, "CONFIGURATION_ERROR", context)
        self.config_key = config_key


class AuthenticationError(ProductionError):
    """
    Authentication/authorization failures in production
    No bypasses or demo modes allowed
    """
    def __init__(self, user_id: str = None, action: str = None, reason: str = None):
        message = f"Authentication failed"
        if action:
            message += f" for action '{action}'"
        if reason:
            message += f": {reason}"
            
        context = {
            "user_id": user_id,
            "attempted_action": action,
            "reason": reason,
            "service": "authentication"
        }
        super().__init__(message, "AUTHENTICATION_FAILED", context)
        self.user_id = user_id


class ResourceExhausted(ProductionError):
    """
    Resource limits exceeded (credits, API limits, etc.)
    Must be properly enforced in production
    """
    def __init__(self, resource_type: str, limit: int, current_usage: int, user_id: str = None):
        message = f"Resource limit exceeded: {resource_type} ({current_usage}/{limit})"
        
        context = {
            "resource_type": resource_type,
            "limit": limit,
            "current_usage": current_usage,
            "user_id": user_id,
            "service": "resource_management"
        }
        super().__init__(message, "RESOURCE_EXHAUSTED", context)
        self.resource_type = resource_type
        self.limit = limit
        self.current_usage = current_usage


class ExternalServiceError(ProductionError):
    """
    External service (Supabase, OpenAI, etc.) failures
    Should not fallback to mock responses
    """
    def __init__(self, service_name: str, operation: str, status_code: int = None, 
                 response_body: str = None):
        message = f"External service '{service_name}' failed during '{operation}'"
        if status_code:
            message += f" (HTTP {status_code})"
            
        context = {
            "service_name": service_name,
            "operation": operation,
            "status_code": status_code,
            "response_preview": response_body[:200] if response_body else None,
            "service": "external_integration"
        }
        super().__init__(message, "EXTERNAL_SERVICE_ERROR", context)
        self.service_name = service_name
        self.status_code = status_code


# Production validation helpers

def validate_production_environment():
    """
    Validate that we're not running with development/mock settings
    Raise ConfigurationError if any mock patterns are detected
    """
    import os
    
    # Check for development environment variables
    debug_vars = [
        ("DEBUG", "True"),
        ("MOCK_AI_RESPONSES", "True"),  
        ("DEMO_MODE", "True"),
        ("USE_TEMPLATE_ALTERNATIVES", "True")
    ]
    
    for var_name, bad_value in debug_vars:
        if os.getenv(var_name, "").lower() == bad_value.lower():
            raise ConfigurationError(
                var_name, 
                f"Production environment cannot have {var_name}={bad_value}",
                "False"
            )
    
    # Check for required production environment variables
    required_vars = [
        "OPENAI_API_KEY",
        "SUPABASE_URL", 
        "SUPABASE_ANON_KEY",
        "DATABASE_URL"
    ]
    
    missing_vars = []
    for var_name in required_vars:
        if not os.getenv(var_name):
            missing_vars.append(var_name)
    
    if missing_vars:
        raise ConfigurationError(
            "missing_environment_variables",
            f"Required environment variables not set: {', '.join(missing_vars)}"
        )


def fail_fast_on_mock_data(data: Any, context: str = "unknown"):
    """
    Helper function to detect and prevent mock data usage in production
    Raises ProductionError if mock patterns are detected
    """
    if isinstance(data, dict):
        # Check for common mock data patterns
        mock_indicators = [
            "mock", "fake", "template", "sample", "demo", "test"
        ]
        
        for key, value in data.items():
            key_lower = str(key).lower()
            value_lower = str(value).lower()
            
            for indicator in mock_indicators:
                if indicator in key_lower or indicator in value_lower:
                    raise ProductionError(
                        f"Mock data detected in production: {key}={value}",
                        "MOCK_DATA_DETECTED",
                        {"context": context, "detected_key": key, "detected_value": str(value)}
                    )
    
    # Check for common mock score patterns
    if isinstance(data, (int, float)) and data in [70.0, 75.0, 80.0, 85.0]:
        raise ProductionError(
            f"Suspicious default score detected: {data}",
            "SUSPICIOUS_DEFAULT_SCORE",
            {"context": context, "score": data}
        )


class ProductionErrorHandler:
    """
    Centralized error handling for production deployment
    Ensures consistent error responses and logging
    """
    
    @staticmethod
    def format_error_response(error: ProductionError, include_debug: bool = False) -> Dict[str, Any]:
        """Format production error for API response"""
        response = {
            "success": False,
            "error": {
                "code": error.error_code,
                "message": error.message,
                "request_id": error.request_id,
                "timestamp": error.timestamp.isoformat()
            }
        }
        
        # Only include debug info in development
        if include_debug and hasattr(error, 'context'):
            response["error"]["debug"] = error.context
            
        return response
    
    @staticmethod
    def get_http_status_code(error: ProductionError) -> int:
        """Map production errors to appropriate HTTP status codes"""
        error_status_map = {
            "ANALYSIS_FAILED": 503,
            "AI_PROVIDER_UNAVAILABLE": 503,
            "TOOLS_SDK_FAILED": 503,
            "DATABASE_CONSTRAINT_FAILED": 400,
            "CONFIGURATION_ERROR": 500,
            "AUTHENTICATION_FAILED": 401,
            "RESOURCE_EXHAUSTED": 429,
            "EXTERNAL_SERVICE_ERROR": 502,
            "MOCK_DATA_DETECTED": 500,
            "SUSPICIOUS_DEFAULT_SCORE": 500
        }
        
        return error_status_map.get(error.error_code, 500)