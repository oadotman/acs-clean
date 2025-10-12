"""
Request Logger for AdCopySurge Tools SDK

This module provides structured logging for HTTP requests, responses, and system events
with comprehensive context tracking, performance monitoring, and debugging capabilities.
"""

import time
import json
import logging
import logging.handlers
import sys
from typing import Dict, Any, Optional, Union
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass, asdict
from contextlib import contextmanager
import traceback
from fastapi import Request, Response


@dataclass
class RequestContext:
    """Request context information"""
    correlation_id: str
    user_id: Optional[str]
    session_id: Optional[str]
    ip_address: str
    user_agent: str
    method: str
    path: str
    query_params: Dict[str, Any]
    headers: Dict[str, str]
    timestamp: float


@dataclass 
class ResponseContext:
    """Response context information"""
    status_code: int
    response_size: Optional[int]
    execution_time: float
    cache_hit: bool
    error_type: Optional[str]
    timestamp: float


class StructuredFormatter(logging.Formatter):
    """Custom formatter for structured JSON logging"""
    
    def format(self, record):
        # Create base log entry
        log_entry = {
            'timestamp': datetime.fromtimestamp(record.created).isoformat(),
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno
        }
        
        # Add request context if available
        if hasattr(record, 'correlation_id'):
            log_entry['correlation_id'] = record.correlation_id
        
        if hasattr(record, 'request_context'):
            log_entry['request'] = record.request_context
        
        if hasattr(record, 'response_context'):
            log_entry['response'] = record.response_context
        
        # Add extra fields
        if hasattr(record, 'extra_fields'):
            log_entry.update(record.extra_fields)
        
        # Add exception information
        if record.exc_info:
            log_entry['exception'] = {
                'type': record.exc_info[0].__name__ if record.exc_info[0] else None,
                'message': str(record.exc_info[1]) if record.exc_info[1] else None,
                'traceback': self.formatException(record.exc_info)
            }
        
        return json.dumps(log_entry, default=str, ensure_ascii=False)


class RequestLogger:
    """
    Comprehensive request logging system
    
    Features:
    - Structured JSON logging
    - Request/response correlation tracking  
    - Performance monitoring
    - Error tracking and debugging
    - Multiple output destinations
    - Log rotation and retention
    - Context propagation
    """
    
    def __init__(self,
                 log_level: str = "INFO",
                 log_file: Optional[str] = None,
                 max_file_size: int = 10 * 1024 * 1024,  # 10MB
                 backup_count: int = 5,
                 enable_console: bool = True,
                 enable_structured: bool = True):
        
        self.enable_structured = enable_structured
        
        # Set up main logger
        self.logger = logging.getLogger("adcopysurge.requests")
        self.logger.setLevel(getattr(logging, log_level.upper()))
        
        # Clear any existing handlers
        self.logger.handlers.clear()
        
        # Set up formatters
        if enable_structured:
            self.formatter = StructuredFormatter()
        else:
            self.formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
        
        # Console handler
        if enable_console:
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setFormatter(self.formatter)
            self.logger.addHandler(console_handler)
        
        # File handler with rotation
        if log_file:
            log_path = Path(log_file)
            log_path.parent.mkdir(parents=True, exist_ok=True)
            
            file_handler = logging.handlers.RotatingFileHandler(
                log_file,
                maxBytes=max_file_size,
                backupCount=backup_count,
                encoding='utf-8'
            )
            file_handler.setFormatter(self.formatter)
            self.logger.addHandler(file_handler)
        
        # Specialized loggers for different components
        self.api_logger = self._create_component_logger("api")
        self.tool_logger = self._create_component_logger("tools")
        self.orchestrator_logger = self._create_component_logger("orchestrator")
        self.metrics_logger = self._create_component_logger("metrics")
        
        # Request context storage
        self.active_requests: Dict[str, RequestContext] = {}
    
    def _create_component_logger(self, component: str) -> logging.Logger:
        """Create a specialized logger for a component"""
        logger = logging.getLogger(f"adcopysurge.{component}")
        logger.setLevel(self.logger.level)
        logger.handlers = self.logger.handlers.copy()
        return logger
    
    def log_request_start(self, request: Request, correlation_id: str) -> None:
        """Log the start of a request"""
        
        # Extract request context
        context = RequestContext(
            correlation_id=correlation_id,
            user_id=self._extract_user_id(request),
            session_id=self._extract_session_id(request),
            ip_address=self._extract_ip_address(request),
            user_agent=request.headers.get("user-agent", "unknown"),
            method=request.method,
            path=str(request.url.path),
            query_params=dict(request.query_params),
            headers=self._sanitize_headers(dict(request.headers)),
            timestamp=time.time()
        )
        
        # Store context for correlation
        self.active_requests[correlation_id] = context
        
        # Log request start
        self.api_logger.info(
            f"Request started: {request.method} {request.url.path}",
            extra={
                'correlation_id': correlation_id,
                'request_context': asdict(context),
                'event': 'request_start'
            }
        )
    
    def log_request_end(self, request: Request, response: Response, execution_time: float) -> None:
        """Log the end of a request"""
        
        correlation_id = getattr(request.state, 'correlation_id', 'unknown')
        
        # Create response context
        response_context = ResponseContext(
            status_code=response.status_code,
            response_size=self._get_response_size(response),
            execution_time=execution_time,
            cache_hit=self._is_cache_hit(response),
            error_type=self._get_error_type(response),
            timestamp=time.time()
        )
        
        # Log request completion
        log_level = logging.INFO if response.status_code < 400 else logging.WARNING
        
        self.api_logger.log(
            log_level,
            f"Request completed: {request.method} {request.url.path} -> {response.status_code} in {execution_time:.2f}s",
            extra={
                'correlation_id': correlation_id,
                'request_context': asdict(self.active_requests.get(correlation_id)),
                'response_context': asdict(response_context),
                'event': 'request_end'
            }
        )
        
        # Clean up context
        self.active_requests.pop(correlation_id, None)
    
    def log_request_error(self, request: Request, error: Exception, execution_time: float) -> None:
        """Log request errors"""
        
        correlation_id = getattr(request.state, 'correlation_id', 'unknown')
        
        # Create error response context
        response_context = ResponseContext(
            status_code=500,
            response_size=None,
            execution_time=execution_time,
            cache_hit=False,
            error_type=type(error).__name__,
            timestamp=time.time()
        )
        
        # Log error with full stack trace
        self.api_logger.error(
            f"Request failed: {request.method} {request.url.path} - {str(error)}",
            extra={
                'correlation_id': correlation_id,
                'request_context': asdict(self.active_requests.get(correlation_id)),
                'response_context': asdict(response_context),
                'event': 'request_error',
                'error_details': {
                    'error_type': type(error).__name__,
                    'error_message': str(error),
                    'stack_trace': traceback.format_exc()
                }
            },
            exc_info=True
        )
        
        # Clean up context
        self.active_requests.pop(correlation_id, None)
    
    def log_tool_execution_start(self, tool_name: str, request_id: str, input_data: Dict[str, Any]) -> None:
        """Log tool execution start"""
        
        self.tool_logger.info(
            f"Tool execution started: {tool_name}",
            extra={
                'correlation_id': request_id,
                'event': 'tool_execution_start',
                'tool_name': tool_name,
                'input_summary': self._summarize_input_data(input_data)
            }
        )
    
    def log_tool_execution_end(self, tool_name: str, request_id: str, 
                              success: bool, execution_time: float, 
                              output_summary: Optional[Dict[str, Any]] = None) -> None:
        """Log tool execution end"""
        
        log_level = logging.INFO if success else logging.WARNING
        
        self.tool_logger.log(
            log_level,
            f"Tool execution {'completed' if success else 'failed'}: {tool_name} in {execution_time:.2f}s",
            extra={
                'correlation_id': request_id,
                'event': 'tool_execution_end',
                'tool_name': tool_name,
                'success': success,
                'execution_time': execution_time,
                'output_summary': output_summary or {}
            }
        )
    
    def log_tool_execution_error(self, tool_name: str, request_id: str, 
                                error: Exception, execution_time: float) -> None:
        """Log tool execution errors"""
        
        self.tool_logger.error(
            f"Tool execution error: {tool_name} - {str(error)}",
            extra={
                'correlation_id': request_id,
                'event': 'tool_execution_error',
                'tool_name': tool_name,
                'execution_time': execution_time,
                'error_details': {
                    'error_type': type(error).__name__,
                    'error_message': str(error),
                    'stack_trace': traceback.format_exc()
                }
            },
            exc_info=True
        )
    
    def log_orchestrator_event(self, event_type: str, flow_id: str, 
                              execution_id: str, details: Dict[str, Any]) -> None:
        """Log orchestrator events"""
        
        self.orchestrator_logger.info(
            f"Orchestrator event: {event_type} for flow {flow_id}",
            extra={
                'correlation_id': execution_id,
                'event': f'orchestrator_{event_type}',
                'flow_id': flow_id,
                'execution_id': execution_id,
                'details': details
            }
        )
    
    def log_metrics_event(self, event_type: str, metrics_data: Dict[str, Any]) -> None:
        """Log metrics collection events"""
        
        self.metrics_logger.debug(
            f"Metrics event: {event_type}",
            extra={
                'event': f'metrics_{event_type}',
                'metrics_data': metrics_data
            }
        )
    
    def log_validation_error(self, correlation_id: str, field: str, 
                           error_message: str, received_value: Any) -> None:
        """Log validation errors"""
        
        self.api_logger.warning(
            f"Validation error: {field} - {error_message}",
            extra={
                'correlation_id': correlation_id,
                'event': 'validation_error',
                'validation_details': {
                    'field': field,
                    'error_message': error_message,
                    'received_value': str(received_value)[:200]  # Limit size
                }
            }
        )
    
    def log_security_event(self, event_type: str, request: Request, 
                          details: Dict[str, Any]) -> None:
        """Log security-related events"""
        
        correlation_id = getattr(request.state, 'correlation_id', 'unknown')
        
        self.api_logger.warning(
            f"Security event: {event_type}",
            extra={
                'correlation_id': correlation_id,
                'event': f'security_{event_type}',
                'security_details': {
                    **details,
                    'ip_address': self._extract_ip_address(request),
                    'user_agent': request.headers.get("user-agent", "unknown"),
                    'path': str(request.url.path)
                }
            }
        )
    
    def log_performance_alert(self, alert_type: str, threshold: float, 
                            actual_value: float, context: Dict[str, Any]) -> None:
        """Log performance alerts"""
        
        self.api_logger.warning(
            f"Performance alert: {alert_type} - {actual_value:.2f} exceeds threshold {threshold:.2f}",
            extra={
                'event': 'performance_alert',
                'alert_type': alert_type,
                'threshold': threshold,
                'actual_value': actual_value,
                'context': context
            }
        )
    
    @contextmanager
    def request_context(self, correlation_id: str):
        """Context manager for request-scoped logging"""
        try:
            # Set up context
            old_factory = logging.getLogRecordFactory()
            
            def record_factory(*args, **kwargs):
                record = old_factory(*args, **kwargs)
                record.correlation_id = correlation_id
                return record
            
            logging.setLogRecordFactory(record_factory)
            yield
            
        finally:
            # Restore original factory
            logging.setLogRecordFactory(old_factory)
    
    def search_logs(self, correlation_id: str, log_file: str = None) -> List[Dict[str, Any]]:
        """Search logs by correlation ID"""
        
        if not log_file:
            return []  # Would need to specify log file to search
        
        matching_logs = []
        
        try:
            with open(log_file, 'r', encoding='utf-8') as f:
                for line in f:
                    try:
                        log_entry = json.loads(line.strip())
                        if log_entry.get('correlation_id') == correlation_id:
                            matching_logs.append(log_entry)
                    except json.JSONDecodeError:
                        continue
        except FileNotFoundError:
            pass
        
        return sorted(matching_logs, key=lambda x: x.get('timestamp', ''))
    
    def get_request_trace(self, correlation_id: str) -> Dict[str, Any]:
        """Get complete trace for a request"""
        
        trace = {
            'correlation_id': correlation_id,
            'events': [],
            'summary': {
                'total_duration': 0,
                'tool_executions': 0,
                'errors': 0,
                'warnings': 0
            }
        }
        
        # This would search through log files to build a complete trace
        # Implementation would depend on log storage strategy
        
        return trace
    
    def _extract_user_id(self, request: Request) -> Optional[str]:
        """Extract user ID from request"""
        # Implementation would depend on authentication system
        return request.headers.get("x-user-id")
    
    def _extract_session_id(self, request: Request) -> Optional[str]:
        """Extract session ID from request"""
        return request.headers.get("x-session-id")
    
    def _extract_ip_address(self, request: Request) -> str:
        """Extract client IP address"""
        # Check for forwarded headers first
        forwarded_for = request.headers.get("x-forwarded-for")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        
        real_ip = request.headers.get("x-real-ip")
        if real_ip:
            return real_ip
        
        # Fallback to client host
        if hasattr(request, 'client') and request.client:
            return request.client.host
        
        return "unknown"
    
    def _sanitize_headers(self, headers: Dict[str, str]) -> Dict[str, str]:
        """Sanitize headers by removing sensitive information"""
        
        sensitive_headers = {
            'authorization', 'cookie', 'x-api-key', 'x-auth-token',
            'password', 'secret', 'token'
        }
        
        sanitized = {}
        for key, value in headers.items():
            key_lower = key.lower()
            if any(sensitive in key_lower for sensitive in sensitive_headers):
                sanitized[key] = "[REDACTED]"
            elif len(value) > 500:  # Truncate very long headers
                sanitized[key] = value[:497] + "..."
            else:
                sanitized[key] = value
        
        return sanitized
    
    def _get_response_size(self, response: Response) -> Optional[int]:
        """Get response size from headers"""
        content_length = response.headers.get("content-length")
        if content_length:
            try:
                return int(content_length)
            except ValueError:
                pass
        return None
    
    def _is_cache_hit(self, response: Response) -> bool:
        """Check if response was served from cache"""
        return response.headers.get("x-cache-hit", "false").lower() == "true"
    
    def _get_error_type(self, response: Response) -> Optional[str]:
        """Get error type from response if it's an error"""
        if response.status_code >= 400:
            return response.headers.get("x-error-type")
        return None
    
    def _summarize_input_data(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a summary of input data for logging"""
        
        summary = {}
        
        for key, value in input_data.items():
            if isinstance(value, str):
                # Truncate long strings
                summary[key] = value[:100] + "..." if len(value) > 100 else value
            elif isinstance(value, (list, dict)):
                # Show length/size for collections
                summary[key] = f"<{type(value).__name__} with {len(value)} items>"
            else:
                summary[key] = str(value)[:100]
        
        return summary
    
    def set_log_level(self, level: str) -> None:
        """Change log level at runtime"""
        log_level = getattr(logging, level.upper())
        self.logger.setLevel(log_level)
        
        for handler in self.logger.handlers:
            handler.setLevel(log_level)
    
    def add_log_handler(self, handler: logging.Handler) -> None:
        """Add additional log handler"""
        handler.setFormatter(self.formatter)
        self.logger.addHandler(handler)
    
    def flush_logs(self) -> None:
        """Force flush all log handlers"""
        for handler in self.logger.handlers:
            if hasattr(handler, 'flush'):
                handler.flush()


# Export the main class
__all__ = [
    'RequestLogger',
    'StructuredFormatter',
    'RequestContext',
    'ResponseContext'
]