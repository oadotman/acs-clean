"""
FastAPI Integration Layer for AdCopySurge Tools SDK

This module provides a complete FastAPI integration layer that exposes the unified tools service
through REST API endpoints with comprehensive error handling, validation, and documentation.
"""

import asyncio
import logging
import time
import traceback
import uuid
from typing import Dict, Any, List, Optional

from fastapi import FastAPI, HTTPException, Depends, Request, BackgroundTasks
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.openapi.utils import get_openapi
from pydantic import ValidationError
from starlette.middleware.base import BaseHTTPMiddleware

# SDK imports
from ..orchestrator import (
    UnifiedToolsService, AnalysisRequest as ServiceAnalysisRequest, 
    AnalysisResponse as ServiceAnalysisResponse
)
from ..contracts.api_schemas import (
    AnalysisRequest, AnalysisResponse, BatchAnalysisRequest, BatchAnalysisResponse,
    FlowConfiguration, HealthCheckResponse, SystemStatistics, ApiError,
    UsageAnalytics, build_error_response, build_success_response
)
from ..observability.metrics_collector import MetricsCollector
from ..observability.request_logger import RequestLogger


# ===== MIDDLEWARE =====

class RequestTrackingMiddleware(BaseHTTPMiddleware):
    """Middleware to track requests and add correlation IDs"""
    
    def __init__(self, app, metrics_collector: MetricsCollector, request_logger: RequestLogger):
        super().__init__(app)
        self.metrics_collector = metrics_collector
        self.request_logger = request_logger
    
    async def dispatch(self, request: Request, call_next):
        # Generate correlation ID
        correlation_id = str(uuid.uuid4())
        request.state.correlation_id = correlation_id
        
        # Track request start
        start_time = time.time()
        self.request_logger.log_request_start(request, correlation_id)
        
        try:
            # Process request
            response = await call_next(request)
            
            # Track successful request
            execution_time = time.time() - start_time
            self.metrics_collector.record_request(
                method=request.method,
                endpoint=str(request.url.path),
                status_code=response.status_code,
                execution_time=execution_time
            )
            
            # Add correlation ID to response headers
            response.headers["X-Correlation-ID"] = correlation_id
            
            self.request_logger.log_request_end(request, response, execution_time)
            
            return response
            
        except Exception as e:
            # Track failed request
            execution_time = time.time() - start_time
            self.metrics_collector.record_request(
                method=request.method,
                endpoint=str(request.url.path),
                status_code=500,
                execution_time=execution_time,
                error=str(e)
            )
            
            self.request_logger.log_request_error(request, e, execution_time)
            
            # Return standardized error response
            error_response = build_error_response(
                error_type="internal_server_error",
                message="An internal server error occurred",
                request_id=correlation_id
            )
            
            return JSONResponse(
                status_code=500,
                content=error_response.dict(),
                headers={"X-Correlation-ID": correlation_id}
            )


# ===== EXCEPTION HANDLERS =====

class APIExceptionHandler:
    """Centralized exception handling for the API"""
    
    def __init__(self, metrics_collector: MetricsCollector):
        self.metrics_collector = metrics_collector
        self.logger = logging.getLogger(__name__)
    
    def create_validation_error_handler(self):
        """Create handler for validation errors"""
        async def validation_error_handler(request: Request, exc: ValidationError):
            correlation_id = getattr(request.state, 'correlation_id', str(uuid.uuid4()))
            
            # Log validation error
            self.logger.warning(f"Validation error [{correlation_id}]: {exc}")
            
            # Track validation error
            self.metrics_collector.record_validation_error(str(request.url.path))
            
            # Build detailed validation error response
            validation_errors = []
            for error in exc.errors():
                validation_errors.append({
                    'field': '.'.join(str(loc) for loc in error['loc']),
                    'rule': error['type'],
                    'message': error['msg'],
                    'received_value': error.get('input'),
                    'expected_format': error.get('ctx', {}).get('expected')
                })
            
            error_response = build_error_response(
                error_type="validation_error",
                message="Request validation failed",
                request_id=correlation_id,
                details={"validation_errors": validation_errors}
            )
            
            return JSONResponse(
                status_code=422,
                content=error_response.dict(),
                headers={"X-Correlation-ID": correlation_id}
            )
        
        return validation_error_handler
    
    def create_http_exception_handler(self):
        """Create handler for HTTP exceptions"""
        async def http_exception_handler(request: Request, exc: HTTPException):
            correlation_id = getattr(request.state, 'correlation_id', str(uuid.uuid4()))
            
            # Log HTTP exception
            self.logger.warning(f"HTTP exception [{correlation_id}]: {exc.status_code} - {exc.detail}")
            
            # Track HTTP error
            self.metrics_collector.record_http_error(str(request.url.path), exc.status_code)
            
            error_response = build_error_response(
                error_type="http_error",
                message=str(exc.detail),
                request_id=correlation_id,
                details={"status_code": exc.status_code}
            )
            
            return JSONResponse(
                status_code=exc.status_code,
                content=error_response.dict(),
                headers={"X-Correlation-ID": correlation_id}
            )
        
        return http_exception_handler
    
    def create_general_exception_handler(self):
        """Create handler for general exceptions"""
        async def general_exception_handler(request: Request, exc: Exception):
            correlation_id = getattr(request.state, 'correlation_id', str(uuid.uuid4()))
            
            # Log general exception
            self.logger.error(f"General exception [{correlation_id}]: {str(exc)}")
            self.logger.debug(f"Stack trace [{correlation_id}]: {traceback.format_exc()}")
            
            # Track general error
            self.metrics_collector.record_general_error(str(request.url.path), type(exc).__name__)
            
            error_response = build_error_response(
                error_type="internal_server_error",
                message="An internal server error occurred",
                request_id=correlation_id,
                details={"exception_type": type(exc).__name__}
            )
            
            return JSONResponse(
                status_code=500,
                content=error_response.dict(),
                headers={"X-Correlation-ID": correlation_id}
            )
        
        return general_exception_handler


# ===== DEPENDENCIES =====

class ServiceDependencies:
    """Dependency injection container for services"""
    
    def __init__(self):
        self._tools_service: Optional[UnifiedToolsService] = None
        self._metrics_collector: Optional[MetricsCollector] = None
        self._request_logger: Optional[RequestLogger] = None
    
    def get_tools_service(self) -> UnifiedToolsService:
        """Get or create tools service instance"""
        if self._tools_service is None:
            self._tools_service = UnifiedToolsService(max_workers=4)
        return self._tools_service
    
    def get_metrics_collector(self) -> MetricsCollector:
        """Get or create metrics collector instance"""
        if self._metrics_collector is None:
            self._metrics_collector = MetricsCollector()
        return self._metrics_collector
    
    def get_request_logger(self) -> RequestLogger:
        """Get or create request logger instance"""
        if self._request_logger is None:
            self._request_logger = RequestLogger()
        return self._request_logger


# Global dependency container
services = ServiceDependencies()


# Dependency providers
def get_tools_service() -> UnifiedToolsService:
    return services.get_tools_service()


def get_metrics_collector() -> MetricsCollector:
    return services.get_metrics_collector()


def get_request_logger() -> RequestLogger:
    return services.get_request_logger()


# ===== API ROUTER CREATION =====

def create_tools_api_app(
    title: str = "AdCopySurge Tools SDK API",
    version: str = "1.0.0",
    description: str = "API for ad copy analysis using multiple AI tools",
    enable_cors: bool = True,
    cors_origins: List[str] = None
) -> FastAPI:
    """
    Create and configure the FastAPI application
    
    Args:
        title: API title
        version: API version
        description: API description
        enable_cors: Whether to enable CORS
        cors_origins: Allowed CORS origins
    
    Returns:
        Configured FastAPI application
    """
    
    # Create FastAPI app
    app = FastAPI(
        title=title,
        version=version,
        description=description,
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json"
    )
    
    # Get service dependencies
    metrics_collector = services.get_metrics_collector()
    request_logger = services.get_request_logger()
    
    # Add middleware
    if enable_cors:
        allowed_origins = cors_origins or ["*"]
        app.add_middleware(
            CORSMiddleware,
            allow_origins=allowed_origins,
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"]
        )
    
    app.add_middleware(GZipMiddleware, minimum_size=1000)
    app.add_middleware(RequestTrackingMiddleware, metrics_collector, request_logger)
    
    # Set up exception handlers
    exception_handler = APIExceptionHandler(metrics_collector)
    app.add_exception_handler(ValidationError, exception_handler.create_validation_error_handler())
    app.add_exception_handler(HTTPException, exception_handler.create_http_exception_handler())
    app.add_exception_handler(Exception, exception_handler.create_general_exception_handler())
    
    # Add routes
    _add_analysis_routes(app)
    _add_health_routes(app)
    _add_configuration_routes(app)
    _add_analytics_routes(app)
    
    # Customize OpenAPI schema
    _customize_openapi_schema(app)
    
    return app


def _add_analysis_routes(app: FastAPI):
    """Add analysis-related routes"""
    
    @app.post(
        "/api/v1/analysis/single",
        response_model=AnalysisResponse,
        summary="Analyze single ad copy",
        description="Perform comprehensive analysis of a single ad copy using selected tools",
        tags=["Analysis"]
    )
    async def analyze_single_copy(
        request: AnalysisRequest,
        tools_service: UnifiedToolsService = Depends(get_tools_service),
        metrics_collector: MetricsCollector = Depends(get_metrics_collector)
    ) -> AnalysisResponse:
        
        # Convert API request to service request
        service_request = ServiceAnalysisRequest(
            headline=request.headline,
            body_text=request.body_text,
            cta=request.cta,
            industry=request.industry or "",
            platform=request.platform or "",
            target_audience=request.target_audience or "",
            brand_guidelines=request.brand_guidelines.dict() if request.brand_guidelines else None,
            analysis_type=request.analysis_type.value,
            custom_flow_id=request.custom_flow_id,
            request_metadata=request.request_metadata
        )
        
        # Track analysis start
        analysis_start = time.time()
        
        # Execute analysis
        result = await tools_service.analyze_copy(service_request)
        
        # Track analysis completion
        analysis_time = time.time() - analysis_start
        metrics_collector.record_analysis(
            analysis_type=request.analysis_type.value,
            execution_time=analysis_time,
            success=result.success,
            overall_score=result.overall_score
        )
        
        # Convert service response to API response
        return AnalysisResponse(
            success=result.success,
            request_id=result.request_id,
            execution_time=result.execution_time,
            analysis_type=request.analysis_type,
            overall_score=result.overall_score,
            performance_score=result.performance_score,
            psychology_score=result.psychology_score,
            brand_score=result.brand_score,
            legal_score=result.legal_score,
            strengths=result.strengths,
            weaknesses=result.weaknesses,
            recommendations=result.recommendations,
            tool_results=result.tool_results,
            execution_metadata=result.execution_metadata,
            errors=result.errors,
            warnings=result.warnings
        )
    
    @app.post(
        "/api/v1/analysis/batch",
        response_model=BatchAnalysisResponse,
        summary="Analyze multiple ad copies",
        description="Perform batch analysis of multiple ad copies with optimized processing",
        tags=["Analysis"]
    )
    async def analyze_batch_copies(
        request: BatchAnalysisRequest,
        background_tasks: BackgroundTasks,
        tools_service: UnifiedToolsService = Depends(get_tools_service),
        metrics_collector: MetricsCollector = Depends(get_metrics_collector)
    ) -> BatchAnalysisResponse:
        
        batch_id = str(uuid.uuid4())
        batch_start = time.time()
        
        # Convert API requests to service requests
        service_requests = []
        for api_req in request.requests:
            service_req = ServiceAnalysisRequest(
                headline=api_req.headline,
                body_text=api_req.body_text,
                cta=api_req.cta,
                industry=api_req.industry or "",
                platform=api_req.platform or "",
                target_audience=api_req.target_audience or "",
                brand_guidelines=api_req.brand_guidelines.dict() if api_req.brand_guidelines else None,
                analysis_type=api_req.analysis_type.value,
                custom_flow_id=api_req.custom_flow_id,
                request_metadata=api_req.request_metadata
            )
            service_requests.append(service_req)
        
        # Execute batch analysis
        results = await tools_service.analyze_copy_batch(service_requests)
        
        # Calculate batch statistics
        total_time = time.time() - batch_start
        successful_count = sum(1 for r in results if r.success)
        failed_count = len(results) - successful_count
        avg_time = sum(r.execution_time for r in results) / len(results) if results else 0
        avg_score = sum(r.overall_score for r in results if r.success) / successful_count if successful_count > 0 else 0
        
        # Track batch completion
        metrics_collector.record_batch_analysis(
            batch_size=len(request.requests),
            execution_time=total_time,
            success_count=successful_count,
            failed_count=failed_count
        )
        
        # Convert results to API response format
        api_results = []
        for result in results:
            api_result = AnalysisResponse(
                success=result.success,
                request_id=result.request_id,
                execution_time=result.execution_time,
                analysis_type=result.analysis_type,  # This might need conversion
                overall_score=result.overall_score,
                performance_score=result.performance_score,
                psychology_score=result.psychology_score,
                brand_score=result.brand_score,
                legal_score=result.legal_score,
                strengths=result.strengths,
                weaknesses=result.weaknesses,
                recommendations=result.recommendations,
                tool_results=result.tool_results,
                execution_metadata=result.execution_metadata,
                errors=result.errors,
                warnings=result.warnings
            )
            api_results.append(api_result)
        
        return BatchAnalysisResponse(
            success=failed_count == 0,
            batch_id=batch_id,
            total_execution_time=total_time,
            results=api_results,
            statistics={
                'total_requests': len(request.requests),
                'successful_analyses': successful_count,
                'failed_analyses': failed_count,
                'average_execution_time': avg_time,
                'average_overall_score': avg_score
            }
        )
    
    @app.get(
        "/api/v1/analysis/types",
        summary="Get available analysis types",
        description="Get list of available analysis types and their descriptions",
        tags=["Analysis"]
    )
    async def get_analysis_types(
        tools_service: UnifiedToolsService = Depends(get_tools_service)
    ) -> Dict[str, Any]:
        
        analysis_types = tools_service.get_available_analysis_types()
        
        return build_success_response(
            data=analysis_types,
            message="Available analysis types retrieved successfully"
        )


def _add_health_routes(app: FastAPI):
    """Add health and monitoring routes"""
    
    @app.get(
        "/api/v1/health/status",
        response_model=HealthCheckResponse,
        summary="System health check",
        description="Get overall system health status and statistics",
        tags=["Health"]
    )
    async def health_check(
        tools_service: UnifiedToolsService = Depends(get_tools_service),
        metrics_collector: MetricsCollector = Depends(get_metrics_collector)
    ) -> HealthCheckResponse:
        
        # Test individual tools
        tools_health = await tools_service.test_tools_health()
        
        # Determine overall health status
        failed_tools = [name for name, healthy in tools_health.items() if not healthy]
        if not failed_tools:
            overall_status = "healthy"
        elif len(failed_tools) < len(tools_health) // 2:
            overall_status = "degraded"
        else:
            overall_status = "unhealthy"
        
        # Get system statistics
        stats = tools_service.get_analysis_statistics()
        system_metrics = metrics_collector.get_system_metrics()
        
        return HealthCheckResponse(
            status=overall_status,
            timestamp=time.time(),
            tools=tools_health,
            statistics={
                'total_analyses': system_metrics.get('total_requests', 0),
                'analyses_24h': system_metrics.get('requests_24h', 0),
                'average_response_time': system_metrics.get('average_response_time', 0.0),
                'success_rate': system_metrics.get('success_rate', 100.0),
                'cache_hit_rate': system_metrics.get('cache_hit_rate', 0.0),
                'memory_usage': system_metrics.get('memory_usage_percent', 0.0),
                'cpu_usage': system_metrics.get('cpu_usage_percent', 0.0)
            },
            active_executions=stats.get('active_executions', 0),
            issues=failed_tools if failed_tools else None
        )
    
    @app.get(
        "/api/v1/health/tools",
        summary="Individual tool health",
        description="Check health of each individual tool",
        tags=["Health"]
    )
    async def tools_health_check(
        tools_service: UnifiedToolsService = Depends(get_tools_service)
    ) -> Dict[str, Any]:
        
        tools_health = await tools_service.test_tools_health()
        
        return build_success_response(
            data=tools_health,
            message="Tool health status retrieved successfully"
        )
    
    @app.get(
        "/api/v1/health/metrics",
        summary="System metrics",
        description="Get detailed system performance metrics",
        tags=["Health"]
    )
    async def system_metrics(
        metrics_collector: MetricsCollector = Depends(get_metrics_collector)
    ) -> Dict[str, Any]:
        
        metrics = metrics_collector.get_detailed_metrics()
        
        return build_success_response(
            data=metrics,
            message="System metrics retrieved successfully"
        )


def _add_configuration_routes(app: FastAPI):
    """Add configuration management routes"""
    
    @app.get(
        "/api/v1/config/flows",
        summary="List flow configurations",
        description="Get list of available flow configurations",
        tags=["Configuration"]
    )
    async def list_flow_configurations(
        tools_service: UnifiedToolsService = Depends(get_tools_service)
    ) -> Dict[str, Any]:
        
        configurations = tools_service.get_flow_configurations()
        
        return build_success_response(
            data=configurations,
            message="Flow configurations retrieved successfully"
        )
    
    @app.post(
        "/api/v1/config/flows/validate",
        summary="Validate flow configuration",
        description="Validate a flow configuration before saving",
        tags=["Configuration"]
    )
    async def validate_flow_configuration(
        flow_config: FlowConfiguration,
        tools_service: UnifiedToolsService = Depends(get_tools_service)
    ) -> Dict[str, Any]:
        
        # Convert API model to service model - would need proper conversion
        validation_result = tools_service.validate_flow_configuration(flow_config)
        
        return build_success_response(
            data=validation_result,
            message="Flow configuration validated successfully"
        )


def _add_analytics_routes(app: FastAPI):
    """Add analytics and reporting routes"""
    
    @app.get(
        "/api/v1/analytics/usage",
        summary="Usage analytics",
        description="Get usage analytics and statistics",
        tags=["Analytics"]
    )
    async def get_usage_analytics(
        period: str = "7d",  # Query parameter
        metrics_collector: MetricsCollector = Depends(get_metrics_collector)
    ) -> Dict[str, Any]:
        
        analytics_data = metrics_collector.get_usage_analytics(period)
        
        return build_success_response(
            data=analytics_data,
            message="Usage analytics retrieved successfully"
        )
    
    @app.get(
        "/api/v1/analytics/performance",
        summary="Performance metrics",
        description="Get performance metrics and trends",
        tags=["Analytics"]
    )
    async def get_performance_analytics(
        period: str = "7d",
        metrics_collector: MetricsCollector = Depends(get_metrics_collector)
    ) -> Dict[str, Any]:
        
        performance_data = metrics_collector.get_performance_analytics(period)
        
        return build_success_response(
            data=performance_data,
            message="Performance analytics retrieved successfully"
        )


def _customize_openapi_schema(app: FastAPI):
    """Customize OpenAPI schema with additional documentation"""
    
    def custom_openapi():
        if app.openapi_schema:
            return app.openapi_schema
        
        openapi_schema = get_openapi(
            title=app.title,
            version=app.version,
            description=app.description,
            routes=app.routes,
        )
        
        # Add custom documentation
        openapi_schema["info"]["x-logo"] = {
            "url": "https://adcopysurge.com/logo.png"
        }
        
        openapi_schema["info"]["contact"] = {
            "name": "AdCopySurge Support",
            "url": "https://adcopysurge.com/support",
            "email": "support@adcopysurge.com"
        }
        
        # Add server information
        openapi_schema["servers"] = [
            {"url": "https://api.adcopysurge.com", "description": "Production server"},
            {"url": "https://staging-api.adcopysurge.com", "description": "Staging server"},
            {"url": "http://localhost:8000", "description": "Development server"}
        ]
        
        # Add tags descriptions
        openapi_schema["tags"] = [
            {
                "name": "Analysis",
                "description": "Ad copy analysis endpoints using AI tools"
            },
            {
                "name": "Health",
                "description": "System health monitoring and status checks"
            },
            {
                "name": "Configuration",
                "description": "Flow configuration management"
            },
            {
                "name": "Analytics",
                "description": "Usage analytics and performance metrics"
            }
        ]
        
        app.openapi_schema = openapi_schema
        return app.openapi_schema
    
    app.openapi = custom_openapi


# ===== STARTUP/SHUTDOWN EVENTS =====

def add_startup_shutdown_events(app: FastAPI):
    """Add startup and shutdown event handlers"""
    
    @app.on_event("startup")
    async def startup_event():
        """Initialize services on startup"""
        logger = logging.getLogger(__name__)
        logger.info("Starting AdCopySurge Tools API...")
        
        # Initialize services
        tools_service = services.get_tools_service()
        metrics_collector = services.get_metrics_collector()
        request_logger = services.get_request_logger()
        
        # Perform initial health checks
        health_status = await tools_service.test_tools_health()
        logger.info(f"Tool health status: {health_status}")
        
        # Start background tasks
        metrics_collector.start_background_collection()
        
        logger.info("AdCopySurge Tools API started successfully")
    
    @app.on_event("shutdown")
    async def shutdown_event():
        """Clean up resources on shutdown"""
        logger = logging.getLogger(__name__)
        logger.info("Shutting down AdCopySurge Tools API...")
        
        # Stop background tasks
        metrics_collector = services.get_metrics_collector()
        metrics_collector.stop_background_collection()
        
        logger.info("AdCopySurge Tools API shut down successfully")


# ===== MAIN APPLICATION FACTORY =====

def create_production_app() -> FastAPI:
    """Create production-ready FastAPI application"""
    
    app = create_tools_api_app(
        title="AdCopySurge Tools SDK API",
        version="1.0.0",
        description="Professional ad copy analysis using AI-powered tools",
        enable_cors=True,
        cors_origins=[
            "https://adcopysurge.com",
            "https://app.adcopysurge.com",
            "http://localhost:3000",
            "http://localhost:3001"
        ]
    )
    
    add_startup_shutdown_events(app)
    
    return app


# Export main components
__all__ = [
    'create_tools_api_app',
    'create_production_app',
    'ServiceDependencies',
    'APIExceptionHandler',
    'RequestTrackingMiddleware'
]