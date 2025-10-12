"""
Global error handling strategy for AdCopySurge API
Provides structured error responses and never returns unhandled 500s
"""

import logging
import traceback
from datetime import datetime
from typing import Dict, Any, Optional, Union
from enum import Enum

from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError, HTTPException
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.status import HTTP_500_INTERNAL_SERVER_ERROR, HTTP_422_UNPROCESSABLE_ENTITY

# Optional imports
try:
    import sentry_sdk
    SENTRY_AVAILABLE = True
except ImportError:
    SENTRY_AVAILABLE = False

logger = logging.getLogger(__name__)

class ErrorCode(str, Enum):
    """Standardized error codes for the API"""
    # Authentication & Authorization
    UNAUTHORIZED = "UNAUTHORIZED"
    FORBIDDEN = "FORBIDDEN"
    TOKEN_EXPIRED = "TOKEN_EXPIRED"
    INVALID_CREDENTIALS = "INVALID_CREDENTIALS"
    
    # Validation
    VALIDATION_ERROR = "VALIDATION_ERROR"
    INVALID_INPUT = "INVALID_INPUT"
    MISSING_REQUIRED_FIELD = "MISSING_REQUIRED_FIELD"
    
    # Resources
    NOT_FOUND = "NOT_FOUND"
    RESOURCE_CONFLICT = "RESOURCE_CONFLICT"
    RESOURCE_LIMIT_EXCEEDED = "RESOURCE_LIMIT_EXCEEDED"
    
    # Business Logic
    SUBSCRIPTION_REQUIRED = "SUBSCRIPTION_REQUIRED"
    QUOTA_EXCEEDED = "QUOTA_EXCEEDED"
    FEATURE_DISABLED = "FEATURE_DISABLED"
    
    # External Services
    SERVICE_UNAVAILABLE = "SERVICE_UNAVAILABLE"
    EXTERNAL_API_ERROR = "EXTERNAL_API_ERROR"
    DATABASE_ERROR = "DATABASE_ERROR"
    
    # System
    INTERNAL_ERROR = "INTERNAL_ERROR"
    CONFIGURATION_ERROR = "CONFIGURATION_ERROR"
    MAINTENANCE_MODE = "MAINTENANCE_MODE"

class ErrorDetail:
    """Structured error detail information"""
    
    def __init__(
        self,
        code: ErrorCode,
        message: str,
        details: Optional[Dict[str, Any]] = None,
        suggestions: Optional[list] = None,
        retry_after: Optional[int] = None
    ):
        self.code = code
        self.message = message
        self.details = details or {}
        self.suggestions = suggestions or []
        self.retry_after = retry_after
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON response"""
        result = {
            "code": self.code,
            "message": self.message,
            "timestamp": datetime.utcnow().isoformat(),
        }
        
        if self.details:
            result["details"] = self.details
        if self.suggestions:
            result["suggestions"] = self.suggestions
        if self.retry_after:
            result["retry_after"] = self.retry_after
        
        return result

class GlobalErrorHandler:
    """Global error handler for the FastAPI application"""
    
    def __init__(self, app: FastAPI, enable_debug: bool = False):
        self.app = app
        self.enable_debug = enable_debug
        self.setup_handlers()
    
    def setup_handlers(self):
        """Setup all error handlers"""
        
        # HTTP Exceptions
        @self.app.exception_handler(HTTPException)
        async def http_exception_handler(request: Request, exc: HTTPException):
            return await self._handle_http_exception(request, exc)
        
        # Starlette HTTP Exceptions
        @self.app.exception_handler(StarletteHTTPException)
        async def starlette_http_exception_handler(request: Request, exc: StarletteHTTPException):
            return await self._handle_http_exception(request, exc)
        
        # Validation Errors
        @self.app.exception_handler(RequestValidationError)
        async def validation_exception_handler(request: Request, exc: RequestValidationError):
            return await self._handle_validation_error(request, exc)
        
        # Global Exception Handler (catches all unhandled exceptions)
        @self.app.exception_handler(Exception)
        async def global_exception_handler(request: Request, exc: Exception):
            return await self._handle_global_exception(request, exc)
    
    async def _handle_http_exception(
        self, 
        request: Request, 
        exc: Union[HTTPException, StarletteHTTPException]
    ) -> JSONResponse:
        """Handle HTTP exceptions with structured responses"""
        
        # Map status codes to error codes
        status_to_error = {
            401: ErrorCode.UNAUTHORIZED,
            403: ErrorCode.FORBIDDEN,
            404: ErrorCode.NOT_FOUND,
            409: ErrorCode.RESOURCE_CONFLICT,
            422: ErrorCode.VALIDATION_ERROR,
            429: ErrorCode.RESOURCE_LIMIT_EXCEEDED,
            503: ErrorCode.SERVICE_UNAVAILABLE,
        }
        
        error_code = status_to_error.get(exc.status_code, ErrorCode.INTERNAL_ERROR)
        
        # Handle special cases
        if exc.status_code == 401 and "token" in str(exc.detail).lower():
            error_code = ErrorCode.TOKEN_EXPIRED
        
        error_detail = ErrorDetail(
            code=error_code,
            message=str(exc.detail) if exc.detail else f"HTTP {exc.status_code}",
            details={
                "status_code": exc.status_code,
                "path": str(request.url.path),
                "method": request.method
            }
        )
        
        # Add suggestions based on error type
        if exc.status_code == 401:
            error_detail.suggestions = [
                "Check your authentication token",
                "Ensure you're logged in",
                "Verify your API key is valid"
            ]
        elif exc.status_code == 403:
            error_detail.suggestions = [
                "Check your user permissions",
                "Verify your subscription plan",
                "Contact support if you believe this is an error"
            ]
        elif exc.status_code == 404:
            error_detail.suggestions = [
                "Check the URL path",
                "Verify the resource exists",
                "Check the documentation for correct endpoints"
            ]
        
        await self._log_error(request, exc, error_detail)
        
        return JSONResponse(
            status_code=exc.status_code,
            content={"error": error_detail.to_dict()}
        )
    
    async def _handle_validation_error(
        self, 
        request: Request, 
        exc: RequestValidationError
    ) -> JSONResponse:
        """Handle validation errors with detailed field information"""
        
        validation_errors = []
        for error in exc.errors():
            field_path = " -> ".join(str(loc) for loc in error["loc"])
            validation_errors.append({
                "field": field_path,
                "message": error["msg"],
                "type": error["type"],
                "input": error.get("input")
            })
        
        error_detail = ErrorDetail(
            code=ErrorCode.VALIDATION_ERROR,
            message="Request validation failed",
            details={
                "validation_errors": validation_errors,
                "path": str(request.url.path),
                "method": request.method
            },
            suggestions=[
                "Check the request format",
                "Verify all required fields are provided",
                "Ensure field types match the expected format",
                "Check the API documentation for correct schema"
            ]
        )
        
        await self._log_error(request, exc, error_detail)
        
        return JSONResponse(
            status_code=HTTP_422_UNPROCESSABLE_ENTITY,
            content={"error": error_detail.to_dict()}
        )
    
    async def _handle_global_exception(
        self, 
        request: Request, 
        exc: Exception
    ) -> JSONResponse:
        """Handle all unhandled exceptions - NEVER return 500 without structure"""
        
        # Determine error code based on exception type
        error_code = ErrorCode.INTERNAL_ERROR
        
        if "database" in str(exc).lower() or "connection" in str(exc).lower():
            error_code = ErrorCode.DATABASE_ERROR
        elif "config" in str(exc).lower() or "setting" in str(exc).lower():
            error_code = ErrorCode.CONFIGURATION_ERROR
        elif "timeout" in str(exc).lower():
            error_code = ErrorCode.SERVICE_UNAVAILABLE
        
        # Create structured error response
        error_detail = ErrorDetail(
            code=error_code,
            message="An unexpected error occurred" if not self.enable_debug else str(exc),
            details={
                "path": str(request.url.path),
                "method": request.method,
                "exception_type": type(exc).__name__
            },
            suggestions=[
                "Please try again in a few moments",
                "If the problem persists, contact support",
                "Check your network connection"
            ]
        )
        
        # Add debug information if enabled
        if self.enable_debug:
            error_detail.details.update({
                "exception_message": str(exc),
                "traceback": traceback.format_exc()
            })
        
        # Log the error with full context
        await self._log_error(request, exc, error_detail, is_unhandled=True)
        
        return JSONResponse(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            content={"error": error_detail.to_dict()}
        )
    
    async def _log_error(
        self, 
        request: Request, 
        exception: Exception, 
        error_detail: ErrorDetail,
        is_unhandled: bool = False
    ):
        """Log error with structured information"""
        
        # Prepare log context
        log_context = {
            "error_code": error_detail.code,
            "path": str(request.url.path),
            "method": request.method,
            "user_agent": request.headers.get("user-agent"),
            "ip": getattr(request.client, "host", None),
            "exception_type": type(exception).__name__,
            "exception_message": str(exception)
        }
        
        # Add request ID if available
        if hasattr(request, "state") and hasattr(request.state, "request_id"):
            log_context["request_id"] = request.state.request_id
        
        # Log based on severity
        if is_unhandled:
            logger.error(
                f"Unhandled exception in {request.method} {request.url.path}",
                extra=log_context,
                exc_info=True
            )
            
            # Send to Sentry if available
            if SENTRY_AVAILABLE:
                sentry_sdk.capture_exception(exception)
        else:
            logger.warning(
                f"HTTP exception in {request.method} {request.url.path}: {error_detail.message}",
                extra=log_context
            )

def setup_error_handling(app: FastAPI, enable_debug: bool = False) -> GlobalErrorHandler:
    """Setup global error handling for the FastAPI app"""
    error_handler = GlobalErrorHandler(app, enable_debug)
    logger.info("Global error handling configured")
    return error_handler

# Utility functions for raising structured errors
def raise_not_found(resource: str, identifier: str = None):
    """Raise a structured not found error"""
    message = f"{resource} not found"
    if identifier:
        message += f": {identifier}"
    raise HTTPException(status_code=404, detail=message)

def raise_validation_error(message: str, field: str = None):
    """Raise a structured validation error"""
    detail = message
    if field:
        detail = f"{field}: {message}"
    raise HTTPException(status_code=422, detail=detail)

def raise_service_unavailable(service: str, retry_after: int = None):
    """Raise a structured service unavailable error"""
    detail = f"{service} is temporarily unavailable"
    exc = HTTPException(status_code=503, detail=detail)
    if retry_after:
        exc.headers = {"Retry-After": str(retry_after)}
    raise exc

def raise_quota_exceeded(resource: str, limit: int = None):
    """Raise a structured quota exceeded error"""
    message = f"{resource} quota exceeded"
    if limit:
        message += f" (limit: {limit})"
    raise HTTPException(status_code=429, detail=message)