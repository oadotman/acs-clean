"""
Production Error Handling Middleware

Provides structured error responses, proper HTTP status codes, and comprehensive
logging without falling back to mock data or template responses.
"""

import json
import time
import uuid
import traceback
from typing import Dict, Any, Optional
from fastapi import Request, Response, HTTPException
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from app.core.exceptions import (
    ProductionError, 
    ProductionAnalysisError,
    AIProviderUnavailable,
    ToolsSDKError,
    DatabaseConstraintError,
    ConfigurationError,
    AuthenticationError,
    ResourceExhausted,
    ExternalServiceError,
    ProductionErrorHandler
)
from app.core.logging import get_logger

logger = get_logger(__name__)


class ProductionErrorMiddleware(BaseHTTPMiddleware):
    """
    Production-ready error handling middleware
    
    - Provides structured JSON error responses
    - Maps exceptions to appropriate HTTP status codes
    - Logs errors with proper context for monitoring
    - NEVER falls back to mock data or template responses
    """
    
    def __init__(self, app: ASGIApp, include_debug: bool = False):
        super().__init__(app)
        self.include_debug = include_debug
    
    async def dispatch(self, request: Request, call_next):
        """Handle all requests and catch production errors"""
        
        # Generate request ID for tracking
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id
        
        start_time = time.time()
        
        try:
            # Process the request
            response = await call_next(request)
            
            # Add request ID to successful responses
            response.headers["X-Request-ID"] = request_id
            
            # Log successful requests (non-health checks)
            if not request.url.path.startswith(("/health", "/metrics")):
                processing_time = time.time() - start_time
                logger.info(f"Request completed", extra={
                    "request_id": request_id,
                    "method": request.method,
                    "path": request.url.path,
                    "status_code": response.status_code,
                    "processing_time": processing_time
                })
            
            return response
            
        except ProductionError as e:
            # Handle production errors with proper status codes
            return self._handle_production_error(e, request_id, request, start_time)
            
        except HTTPException as e:
            # Handle FastAPI HTTPExceptions
            return self._handle_http_exception(e, request_id, request, start_time)
            
        except Exception as e:
            # Handle unexpected errors
            return self._handle_unexpected_error(e, request_id, request, start_time)
    
    def _handle_production_error(self, error: ProductionError, request_id: str, 
                                request: Request, start_time: float) -> JSONResponse:
        """Handle production errors with proper logging and structured responses"""
        
        processing_time = time.time() - start_time
        
        # Get appropriate HTTP status code
        status_code = ProductionErrorHandler.get_http_status_code(error)
        
        # Create structured error response
        error_response = {
            "success": False,
            "error": {
                "code": error.error_code,
                "message": error.message,
                "request_id": request_id,
                "timestamp": error.timestamp.isoformat()
            },
            "request_info": {
                "method": request.method,
                "path": request.url.path,
                "processing_time": processing_time
            }
        }
        
        # Include debug info if enabled (development only)
        if self.include_debug and hasattr(error, 'context') and error.context:
            error_response["debug"] = {
                "context": error.context,
                "error_class": error.__class__.__name__
            }
        
        # Log error with structured data
        log_data = {
            "request_id": request_id,
            "error_code": error.error_code,
            "error_message": error.message,
            "method": request.method,
            "path": request.url.path,
            "status_code": status_code,
            "processing_time": processing_time,
            "user_agent": request.headers.get("user-agent"),
            "client_ip": self._get_client_ip(request)
        }
        
        # Add error-specific context
        if hasattr(error, 'context') and error.context:
            log_data["error_context"] = error.context
        
        # Log at appropriate level based on error type
        if isinstance(error, (ConfigurationError, DatabaseConstraintError)):
            logger.error(f"Critical production error: {error.message}", extra=log_data)
        elif isinstance(error, (AIProviderUnavailable, ToolsSDKError)):
            logger.warning(f"Service degradation: {error.message}", extra=log_data)
        elif isinstance(error, (AuthenticationError, ResourceExhausted)):
            logger.info(f"Client error: {error.message}", extra=log_data)
        else:
            logger.warning(f"Production error: {error.message}", extra=log_data)
        
        return JSONResponse(
            status_code=status_code,
            content=error_response,
            headers={"X-Request-ID": request_id}
        )
    
    def _handle_http_exception(self, error: HTTPException, request_id: str,
                              request: Request, start_time: float) -> JSONResponse:
        """Handle FastAPI HTTP exceptions"""
        
        processing_time = time.time() - start_time
        
        error_response = {
            "success": False,
            "error": {
                "code": f"HTTP_{error.status_code}",
                "message": error.detail,
                "request_id": request_id,
                "timestamp": time.time()
            },
            "request_info": {
                "method": request.method,
                "path": request.url.path,
                "processing_time": processing_time
            }
        }
        
        # Log HTTP errors
        log_data = {
            "request_id": request_id,
            "method": request.method,
            "path": request.url.path,
            "status_code": error.status_code,
            "detail": error.detail,
            "processing_time": processing_time
        }
        
        if error.status_code >= 500:
            logger.error(f"HTTP {error.status_code} error: {error.detail}", extra=log_data)
        else:
            logger.info(f"HTTP {error.status_code} error: {error.detail}", extra=log_data)
        
        return JSONResponse(
            status_code=error.status_code,
            content=error_response,
            headers={"X-Request-ID": request_id}
        )
    
    def _handle_unexpected_error(self, error: Exception, request_id: str,
                                request: Request, start_time: float) -> JSONResponse:
        """Handle unexpected errors with full logging"""
        
        processing_time = time.time() - start_time
        
        # Create generic error response (no sensitive data exposure)
        error_response = {
            "success": False,
            "error": {
                "code": "INTERNAL_SERVER_ERROR",
                "message": "An internal server error occurred. Please try again later.",
                "request_id": request_id,
                "timestamp": time.time()
            },
            "request_info": {
                "method": request.method,
                "path": request.url.path,
                "processing_time": processing_time
            }
        }
        
        # Include full error details in debug mode only
        if self.include_debug:
            error_response["debug"] = {
                "error_type": error.__class__.__name__,
                "error_message": str(error),
                "traceback": traceback.format_exc()
            }
        
        # Log full error details for debugging
        log_data = {
            "request_id": request_id,
            "error_type": error.__class__.__name__,
            "error_message": str(error),
            "method": request.method,
            "path": request.url.path,
            "processing_time": processing_time,
            "client_ip": self._get_client_ip(request),
            "user_agent": request.headers.get("user-agent"),
            "traceback": traceback.format_exc()
        }
        
        logger.error(f"Unexpected error: {str(error)}", extra=log_data)
        
        return JSONResponse(
            status_code=500,
            content=error_response,
            headers={"X-Request-ID": request_id}
        )
    
    def _get_client_ip(self, request: Request) -> Optional[str]:
        """Extract client IP address from request"""
        # Check forwarded headers first (for reverse proxy setups)
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip
        
        # Fall back to direct client
        if hasattr(request, "client") and request.client:
            return request.client.host
        
        return None


class CircuitBreaker:
    """
    Circuit breaker for external service calls
    Prevents cascading failures and provides fail-fast behavior
    """
    
    def __init__(self, failure_threshold: int = 5, recovery_timeout: int = 60):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.failure_count = 0
        self.last_failure_time = None
        self.state = "CLOSED"  # CLOSED, OPEN, HALF_OPEN
    
    def call(self, func, *args, **kwargs):
        """Execute function with circuit breaker protection"""
        
        if self.state == "OPEN":
            if self._should_attempt_reset():
                self.state = "HALF_OPEN"
            else:
                raise ExternalServiceError(
                    "circuit_breaker",
                    "Service temporarily unavailable due to repeated failures"
                )
        
        try:
            result = func(*args, **kwargs)
            self._on_success()
            return result
            
        except Exception as e:
            self._on_failure()
            raise
    
    def _should_attempt_reset(self) -> bool:
        """Check if enough time has passed to attempt reset"""
        if not self.last_failure_time:
            return False
        
        return (time.time() - self.last_failure_time) >= self.recovery_timeout
    
    def _on_success(self):
        """Handle successful call"""
        self.failure_count = 0
        self.state = "CLOSED"
        self.last_failure_time = None
    
    def _on_failure(self):
        """Handle failed call"""
        self.failure_count += 1
        self.last_failure_time = time.time()
        
        if self.failure_count >= self.failure_threshold:
            self.state = "OPEN"
            logger.warning(f"Circuit breaker opened after {self.failure_count} failures")


class ProductionRetryHandler:
    """
    Retry handler for transient failures
    Does NOT retry with mock data - only retries the actual operation
    """
    
    def __init__(self, max_retries: int = 3, base_delay: float = 1.0, max_delay: float = 30.0):
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.max_delay = max_delay
    
    async def retry_async(self, func, *args, **kwargs):
        """Retry async function with exponential backoff"""
        last_exception = None
        
        for attempt in range(self.max_retries + 1):
            try:
                return await func(*args, **kwargs)
                
            except (AIProviderUnavailable, ExternalServiceError, ToolsSDKError) as e:
                last_exception = e
                
                if attempt < self.max_retries:
                    # Calculate delay with exponential backoff and jitter
                    delay = min(
                        self.base_delay * (2 ** attempt) + (time.time() % 1),
                        self.max_delay
                    )
                    
                    logger.warning(f"Retry {attempt + 1}/{self.max_retries} after {delay:.2f}s: {str(e)}")
                    
                    import asyncio
                    await asyncio.sleep(delay)
                else:
                    logger.error(f"All {self.max_retries} retries exhausted for {func.__name__}")
            
            except ProductionError as e:
                # Don't retry production errors - they indicate configuration or validation issues
                raise
            
            except Exception as e:
                # Don't retry unexpected errors
                raise
        
        # Re-raise the last exception if all retries failed
        raise last_exception


class ProductionMonitoringHooks:
    """
    Hooks for monitoring and alerting in production
    Integrates with monitoring systems without exposing sensitive data
    """
    
    @staticmethod
    def emit_error_metric(error: ProductionError, request_path: str):
        """Emit error metric to monitoring system"""
        # This would integrate with your monitoring system (DataDog, New Relic, etc.)
        try:
            metric_data = {
                "error_code": error.error_code,
                "path": request_path,
                "timestamp": error.timestamp.isoformat(),
                "service": "adcopysurge_api"
            }
            
            # Example: Send to monitoring system
            # monitoring_client.increment('api.errors', tags=metric_data)
            logger.info(f"Error metric emitted: {error.error_code}", extra=metric_data)
            
        except Exception as e:
            # Never let monitoring failures break the main application
            logger.warning(f"Failed to emit error metric: {e}")
    
    @staticmethod
    def emit_performance_metric(request_path: str, processing_time: float, status_code: int):
        """Emit performance metric to monitoring system"""
        try:
            metric_data = {
                "path": request_path,
                "processing_time": processing_time,
                "status_code": status_code,
                "service": "adcopysurge_api"
            }
            
            # Example: Send to monitoring system
            # monitoring_client.timing('api.response_time', processing_time, tags=metric_data)
            
            if processing_time > 5.0:  # Log slow requests
                logger.warning(f"Slow request detected: {processing_time:.2f}s", extra=metric_data)
            
        except Exception as e:
            logger.warning(f"Failed to emit performance metric: {e}")
    
    @staticmethod
    def emit_alert(alert_type: str, message: str, severity: str = "warning", context: Dict = None):
        """Emit alert to monitoring/alerting system"""
        try:
            alert_data = {
                "alert_type": alert_type,
                "message": message,
                "severity": severity,
                "timestamp": time.time(),
                "service": "adcopysurge_api",
                "context": context or {}
            }
            
            # Example: Send to alerting system
            # alerting_client.send_alert(alert_data)
            
            # Log alert for immediate visibility
            if severity == "critical":
                logger.error(f"CRITICAL ALERT: {message}", extra=alert_data)
            elif severity == "warning":
                logger.warning(f"Alert: {message}", extra=alert_data)
            else:
                logger.info(f"Alert: {message}", extra=alert_data)
            
        except Exception as e:
            logger.error(f"Failed to emit alert: {e}")


# Global instances for reuse
default_circuit_breaker = CircuitBreaker(failure_threshold=5, recovery_timeout=60)
default_retry_handler = ProductionRetryHandler(max_retries=3, base_delay=1.0, max_delay=30.0)
monitoring_hooks = ProductionMonitoringHooks()