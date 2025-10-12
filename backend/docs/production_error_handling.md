# Production Error Handling Middleware

This document describes the production error handling middleware implementation that provides structured error responses, proper HTTP status codes, and comprehensive logging **without falling back to mock data or template responses**.

## Overview

The production error handling system consists of several key components:

1. **ProductionErrorMiddleware** - Core middleware that catches and handles all exceptions
2. **CircuitBreaker** - Prevents cascading failures from external services
3. **ProductionRetryHandler** - Handles retries with exponential backoff (no mock fallbacks)
4. **ProductionMonitoringHooks** - Integrates with monitoring and alerting systems

## Key Features

### Fail-Fast Architecture
- **No Mock Data**: Never falls back to mock data or template responses
- **Structured Errors**: All errors return structured JSON with proper status codes
- **Request Tracking**: Every request gets a unique ID for tracing
- **Comprehensive Logging**: All errors are logged with full context

### Error Categories

The middleware handles different types of production errors:

- **ProductionAnalysisError** (500) - Analysis pipeline failures
- **AIProviderUnavailable** (503) - AI provider failures (no fallback allowed)
- **ToolsSDKError** (502) - Tools SDK execution failures
- **DatabaseConstraintError** (422) - Invalid data insertion attempts
- **ConfigurationError** (500) - Missing or invalid configuration
- **AuthenticationError** (401) - Authentication failures
- **ResourceExhausted** (429) - Rate limiting and resource exhaustion
- **ExternalServiceError** (502/503) - External service failures

### Response Format

All error responses follow this structured format:

```json
{
  "success": false,
  "error": {
    "code": "AI_PROVIDER_UNAVAILABLE",
    "message": "OpenAI API is currently unavailable",
    "request_id": "uuid-string",
    "timestamp": "2024-01-15T10:30:00Z"
  },
  "request_info": {
    "method": "POST",
    "path": "/api/v1/analyze",
    "processing_time": 1.23
  }
}
```

## Integration

### FastAPI Application Setup

```python
from app.middleware import ProductionErrorMiddleware

app = FastAPI()

# Add error middleware FIRST (important for proper error handling)
app.add_middleware(
    ProductionErrorMiddleware,
    include_debug=False  # Set to True only in development
)
```

### Service Integration

Services should use the production error classes to ensure proper error propagation:

```python
from app.core.exceptions import AIProviderUnavailable, ProductionAnalysisError

class MyService:
    async def analyze_ad(self, ad_data):
        try:
            result = await ai_provider.analyze(ad_data)
            if not result:
                raise AIProviderUnavailable(
                    "openai_no_response", 
                    "OpenAI returned no response"
                )
            return result
        except Exception as e:
            raise ProductionAnalysisError(
                "analysis_failed",
                f"Failed to analyze ad: {str(e)}"
            )
```

## Circuit Breaker Usage

The circuit breaker prevents cascading failures:

```python
from app.middleware import default_circuit_breaker

# Protect external service calls
result = default_circuit_breaker.call(external_api_call, *args)
```

Circuit breaker states:
- **CLOSED** - Normal operation
- **OPEN** - Failing fast (service unavailable)
- **HALF_OPEN** - Testing service recovery

## Retry Handler Usage

The retry handler provides exponential backoff for transient failures:

```python
from app.middleware import default_retry_handler

# Retry with exponential backoff (no mock fallbacks)
result = await default_retry_handler.retry_async(
    ai_service.generate_alternatives,
    ad_content
)
```

**Important**: The retry handler only retries the actual operation - it never falls back to mock data.

## Monitoring Integration

The middleware includes hooks for monitoring systems:

```python
from app.middleware import monitoring_hooks

# Emit custom alerts
monitoring_hooks.emit_alert(
    alert_type="ai_provider_down",
    message="OpenAI API has been unavailable for 5 minutes",
    severity="critical",
    context={"provider": "openai", "duration": 300}
)
```

## Logging Format

All errors are logged in structured format:

```json
{
  "request_id": "uuid-string",
  "error_code": "AI_PROVIDER_UNAVAILABLE",
  "error_message": "OpenAI API is currently unavailable",
  "method": "POST",
  "path": "/api/v1/generate-alternatives",
  "status_code": 503,
  "processing_time": 2.45,
  "client_ip": "192.168.1.100",
  "user_agent": "Mozilla/5.0...",
  "error_context": {
    "provider": "openai",
    "model": "gpt-4"
  }
}
```

## Environment Configuration

### Production Environment
```bash
ENVIRONMENT=production
ALLOWED_ORIGINS=https://app.adcopysurge.com
LOG_LEVEL=INFO
```

### Development Environment
```bash
ENVIRONMENT=development
LOG_LEVEL=DEBUG
```

## Error Response Examples

### AI Provider Unavailable
```json
{
  "success": false,
  "error": {
    "code": "AI_PROVIDER_UNAVAILABLE",
    "message": "OpenAI API is currently unavailable. Please try again later.",
    "request_id": "123e4567-e89b-12d3-a456-426614174000",
    "timestamp": "2024-01-15T10:30:00Z"
  },
  "request_info": {
    "method": "POST",
    "path": "/api/v1/analyze",
    "processing_time": 1.23
  }
}
```

### Database Constraint Error
```json
{
  "success": false,
  "error": {
    "code": "DATABASE_CONSTRAINT_ERROR",
    "message": "Invalid ad data: headline cannot be empty",
    "request_id": "987f6543-e21b-43c5-b789-123456789abc",
    "timestamp": "2024-01-15T10:31:00Z"
  },
  "request_info": {
    "method": "POST",
    "path": "/api/v1/ads",
    "processing_time": 0.15
  }
}
```

## Best Practices

1. **Always Use Production Errors**: Import and use the production error classes instead of generic exceptions
2. **Provide Context**: Include relevant context in error messages and error objects
3. **Fail Fast**: Never fall back to mock data - fail immediately with clear errors
4. **Log Appropriately**: Use appropriate log levels (ERROR for system issues, WARNING for service degradation)
5. **Monitor Patterns**: Set up monitoring for error patterns and thresholds

## Security Considerations

- **No Sensitive Data**: Error responses never expose sensitive information
- **Debug Mode**: Debug information is only included in development environments
- **Request IDs**: Use for tracing without exposing internal implementation details
- **Rate Limiting**: Integrated with ResourceExhausted error handling

This middleware ensures that the application fails fast and provides clear error information without ever falling back to mock data or template responses, making it suitable for production deployment.