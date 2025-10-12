"""
API Schemas for AdCopySurge Tools SDK

This module contains JSON schemas and Pydantic models for API request/response validation,
documentation generation, and ensuring data consistency across the system.
"""

from typing import Dict, Any, List, Optional, Union, Literal
from pydantic import BaseModel, Field, validator
from enum import Enum
import json


# ===== ENUMS =====

class AnalysisType(str, Enum):
    """Available analysis types"""
    COMPREHENSIVE = "comprehensive"
    QUICK = "quick"
    COMPLIANCE = "compliance"
    OPTIMIZATION = "optimization"


class ExecutionStrategy(str, Enum):
    """Tool execution strategies"""
    SEQUENTIAL = "sequential"
    PARALLEL = "parallel"
    MIXED = "mixed"


class Priority(str, Enum):
    """Flow priority levels"""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    CRITICAL = "critical"


class Severity(str, Enum):
    """Issue severity levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class HealthStatus(str, Enum):
    """System health status values"""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"


# ===== CORE REQUEST/RESPONSE MODELS =====

class BrandGuidelines(BaseModel):
    """Brand guidelines configuration"""
    voice_attributes: Optional[List[str]] = Field(None, description="Brand voice characteristics")
    tone: Optional[str] = Field(None, description="Preferred tone (e.g., 'professional', 'casual', 'urgent')")
    personality_traits: Optional[List[str]] = Field(None, description="Brand personality traits")
    messaging_hierarchy: Optional[List[str]] = Field(None, description="Messaging priorities and hierarchy")
    required_phrases: Optional[List[str]] = Field(None, description="Required brand phrases or terminology")
    prohibited_phrases: Optional[List[str]] = Field(None, description="Prohibited words or phrases")
    voice_examples: Optional[List[str]] = Field(None, description="Brand voice examples")

    class Config:
        schema_extra = {
            "example": {
                "voice_attributes": ["professional", "trustworthy", "innovative"],
                "tone": "professional",
                "personality_traits": ["expert", "reliable", "cutting-edge"],
                "messaging_hierarchy": ["benefits", "features", "social_proof"],
                "required_phrases": ["industry-leading", "trusted by professionals"],
                "prohibited_phrases": ["cheap", "basic", "amateur"],
                "voice_examples": ["Transform your business with industry-leading solutions"]
            }
        }


class AnalysisRequest(BaseModel):
    """Main request structure for ad copy analysis"""
    headline: str = Field(..., min_length=1, max_length=500, description="The headline text to analyze")
    body_text: str = Field(..., min_length=1, max_length=5000, description="The main body text content")
    cta: str = Field(..., min_length=1, max_length=200, description="Call-to-action text")
    industry: Optional[str] = Field(None, max_length=100, description="Industry context")
    platform: Optional[str] = Field(None, max_length=50, description="Platform context")
    target_audience: Optional[str] = Field(None, max_length=500, description="Target audience description")
    brand_guidelines: Optional[BrandGuidelines] = Field(None, description="Brand guidelines and voice requirements")
    analysis_type: AnalysisType = Field(AnalysisType.COMPREHENSIVE, description="Type of analysis to perform")
    custom_flow_id: Optional[str] = Field(None, max_length=100, description="Custom flow configuration ID")
    request_metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata for the request")

    @validator('headline', 'body_text', 'cta')
    def validate_text_fields(cls, v):
        if not v.strip():
            raise ValueError('Text field cannot be empty or whitespace only')
        return v.strip()

    class Config:
        schema_extra = {
            "example": {
                "headline": "Revolutionary AI Tool Transforms Your Business",
                "body_text": "Discover the power of AI-driven insights that help you make better decisions, increase efficiency, and drive growth. Join thousands of satisfied customers who trust our platform.",
                "cta": "Start Your Free Trial Today",
                "industry": "technology",
                "platform": "facebook",
                "target_audience": "business owners and decision makers",
                "analysis_type": "comprehensive"
            }
        }


class CopyVariation(BaseModel):
    """Copy variation structure"""
    id: str = Field(..., description="Variation identifier")
    type: str = Field(..., description="Type of optimization applied")
    headline: str = Field(..., description="Modified headline")
    body_text: str = Field(..., description="Modified body text")
    cta: str = Field(..., description="Modified CTA")
    optimization_focus: str = Field(..., description="Focus of the optimization")
    improvement_score: Optional[float] = Field(None, ge=0, le=100, description="Expected improvement score")
    disclaimers: Optional[List[str]] = Field(None, description="Additional disclaimers if applicable")


class Alternative(BaseModel):
    """Alternative suggestion structure"""
    original: str = Field(..., description="Original text that was flagged")
    alternatives: List[str] = Field(..., min_items=1, description="Suggested alternatives")
    category: str = Field(..., description="Category of the issue")
    severity: Severity = Field(..., description="Severity level")
    reasoning: str = Field(..., description="Reasoning for the suggestion")
    persuasion_impact: Optional[str] = Field(None, description="Impact on persuasion if changed")


class ToolResult(BaseModel):
    """Individual tool result structure"""
    success: bool = Field(..., description="Whether the tool executed successfully")
    scores: Optional[Dict[str, float]] = Field(None, description="Tool-specific scores")
    insights: Optional[Dict[str, Any]] = Field(None, description="Tool-specific insights")
    recommendations: Optional[List[str]] = Field(None, description="Tool-specific recommendations")
    variations: Optional[List[CopyVariation]] = Field(None, description="Generated variations")
    alternatives: Optional[List[Alternative]] = Field(None, description="Alternative suggestions")
    error: Optional[str] = Field(None, description="Error message if failed")
    execution_time: Optional[float] = Field(None, ge=0, description="Execution time for this tool")
    confidence_score: Optional[float] = Field(None, ge=0, le=100, description="Confidence score for the analysis")


class ToolResults(BaseModel):
    """Tool execution results"""
    performance_forensics: Optional[ToolResult] = None
    psychology_scorer: Optional[ToolResult] = None
    brand_voice_engine: Optional[ToolResult] = None
    legal_risk_scanner: Optional[ToolResult] = None


class ExecutionMetadata(BaseModel):
    """Execution metadata"""
    successful_tools: List[str] = Field(..., description="Tools that executed successfully")
    failed_tools: List[str] = Field(..., description="Tools that failed")
    execution_strategy: str = Field(..., description="Execution strategy used")
    total_tools: int = Field(..., ge=0, description="Total number of tools attempted")
    cached_at: Optional[float] = Field(None, description="Cache timestamp")


class AnalysisResponse(BaseModel):
    """Unified response structure for ad copy analysis results"""
    success: bool = Field(..., description="Whether the analysis completed successfully")
    request_id: str = Field(..., description="Unique request identifier")
    execution_time: float = Field(..., ge=0, description="Total execution time in seconds")
    analysis_type: AnalysisType = Field(..., description="Type of analysis performed")
    
    # Scores
    overall_score: float = Field(..., ge=0, le=100, description="Overall quality score")
    performance_score: float = Field(..., ge=0, le=100, description="Performance potential score")
    psychology_score: float = Field(..., ge=0, le=100, description="Psychological appeal score")
    brand_score: float = Field(..., ge=0, le=100, description="Brand alignment score")
    legal_score: float = Field(..., ge=0, le=100, description="Legal compliance score")
    
    # Insights
    strengths: List[str] = Field(..., description="Key strengths identified")
    weaknesses: List[str] = Field(..., description="Areas needing improvement")
    recommendations: List[str] = Field(..., description="Prioritized recommendations")
    
    # Detailed results
    tool_results: ToolResults = Field(..., description="Detailed results from each tool")
    execution_metadata: ExecutionMetadata = Field(..., description="Execution metadata and statistics")
    
    # Optional error information
    errors: Optional[List[str]] = Field(None, description="Error messages if any")
    warnings: Optional[List[str]] = Field(None, description="Warning messages if any")

    class Config:
        schema_extra = {
            "example": {
                "success": True,
                "request_id": "req_12345",
                "execution_time": 2.45,
                "analysis_type": "comprehensive",
                "overall_score": 78.5,
                "performance_score": 82.0,
                "psychology_score": 75.0,
                "brand_score": 80.0,
                "legal_score": 77.0,
                "strengths": ["Strong emotional appeal", "Clear value proposition"],
                "weaknesses": ["Limited social proof", "Vague call-to-action"],
                "recommendations": ["Add customer testimonials", "Make CTA more specific"],
                "tool_results": {},
                "execution_metadata": {
                    "successful_tools": ["performance_forensics", "psychology_scorer"],
                    "failed_tools": [],
                    "execution_strategy": "parallel",
                    "total_tools": 4
                }
            }
        }


# ===== BATCH PROCESSING MODELS =====

class BatchOptions(BaseModel):
    """Batch processing options"""
    max_parallel: Optional[int] = Field(None, ge=1, le=10, description="Maximum parallel executions")
    continue_on_error: Optional[bool] = Field(True, description="Continue processing if individual requests fail")
    priority: Optional[Priority] = Field(Priority.NORMAL, description="Priority for batch processing")


class BatchAnalysisRequest(BaseModel):
    """Batch analysis request"""
    requests: List[AnalysisRequest] = Field(..., min_items=1, max_items=50, description="Array of analysis requests")
    options: Optional[BatchOptions] = Field(None, description="Batch processing options")

    class Config:
        schema_extra = {
            "example": {
                "requests": [
                    {
                        "headline": "First headline",
                        "body_text": "First body text",
                        "cta": "First CTA",
                        "analysis_type": "quick"
                    },
                    {
                        "headline": "Second headline", 
                        "body_text": "Second body text",
                        "cta": "Second CTA",
                        "analysis_type": "comprehensive"
                    }
                ],
                "options": {
                    "max_parallel": 2,
                    "continue_on_error": True
                }
            }
        }


class BatchStatistics(BaseModel):
    """Batch processing statistics"""
    total_requests: int = Field(..., ge=0, description="Total requests processed")
    successful_analyses: int = Field(..., ge=0, description="Successful analyses")
    failed_analyses: int = Field(..., ge=0, description="Failed analyses")
    average_execution_time: float = Field(..., ge=0, description="Average execution time per request")
    average_overall_score: float = Field(..., ge=0, le=100, description="Average overall score")


class BatchAnalysisResponse(BaseModel):
    """Batch analysis response"""
    success: bool = Field(..., description="Whether the batch completed successfully")
    batch_id: str = Field(..., description="Batch identifier")
    total_execution_time: float = Field(..., ge=0, description="Total execution time")
    results: List[AnalysisResponse] = Field(..., description="Individual analysis results")
    statistics: BatchStatistics = Field(..., description="Batch statistics")
    errors: Optional[List[str]] = Field(None, description="Batch-level errors")


# ===== CONFIGURATION MODELS =====

class ToolConfig(BaseModel):
    """Tool configuration"""
    name: str = Field(..., description="Tool name")
    tool_type: str = Field(..., description="Tool type")
    timeout: float = Field(..., gt=0, description="Execution timeout")
    parameters: Dict[str, Any] = Field(..., description="Tool-specific parameters")


class FlowStep(BaseModel):
    """Individual flow step"""
    tool_name: str = Field(..., description="Tool name to execute")
    tool_class: str = Field(..., description="Tool class name")
    config: ToolConfig = Field(..., description="Tool configuration")
    dependencies: List[str] = Field(default_factory=list, description="Dependencies on other tools")
    parallel_group: Optional[str] = Field(None, description="Parallel execution group")
    required: bool = Field(True, description="Whether this step is required")
    timeout_override: Optional[float] = Field(None, gt=0, description="Timeout override for this step")
    retry_count: int = Field(1, ge=1, le=5, description="Number of retry attempts")


class FlowConfiguration(BaseModel):
    """Flow configuration for custom analysis"""
    flow_id: str = Field(..., min_length=1, max_length=100, description="Unique flow identifier")
    name: str = Field(..., min_length=1, max_length=200, description="Human-readable name")
    description: str = Field(..., min_length=1, max_length=1000, description="Description of the flow")
    execution_strategy: ExecutionStrategy = Field(..., description="Execution strategy")
    priority: Priority = Field(Priority.NORMAL, description="Priority level")
    max_parallel_workers: int = Field(4, ge=1, le=10, description="Maximum parallel workers")
    total_timeout: Optional[float] = Field(None, gt=0, description="Total timeout in seconds")
    continue_on_error: bool = Field(True, description="Continue on individual tool errors")
    output_aggregation_strategy: str = Field("weighted_average", description="Output aggregation strategy")
    steps: List[FlowStep] = Field(..., min_items=1, description="Flow steps configuration")


# ===== HEALTH AND STATUS MODELS =====

class SystemStatistics(BaseModel):
    """System statistics"""
    total_analyses: int = Field(..., ge=0, description="Total analyses performed")
    analyses_24h: int = Field(..., ge=0, description="Analyses in last 24 hours")
    average_response_time: float = Field(..., ge=0, description="Average response time")
    success_rate: float = Field(..., ge=0, le=100, description="Success rate percentage")
    cache_hit_rate: float = Field(..., ge=0, le=100, description="Cache hit rate")
    memory_usage: float = Field(..., ge=0, le=100, description="Memory usage percentage")
    cpu_usage: float = Field(..., ge=0, le=100, description="CPU usage percentage")


class HealthCheckResponse(BaseModel):
    """System health status"""
    status: HealthStatus = Field(..., description="Overall system status")
    timestamp: float = Field(..., description="Health check timestamp")
    tools: Dict[str, bool] = Field(..., description="Individual tool health")
    statistics: SystemStatistics = Field(..., description="System statistics")
    active_executions: int = Field(..., ge=0, description="Active executions count")
    issues: Optional[List[str]] = Field(None, description="Any system issues")

    class Config:
        schema_extra = {
            "example": {
                "status": "healthy",
                "timestamp": 1638360000.0,
                "tools": {
                    "performance_forensics": True,
                    "psychology_scorer": True,
                    "brand_voice_engine": True,
                    "legal_risk_scanner": True
                },
                "statistics": {
                    "total_analyses": 1250,
                    "analyses_24h": 45,
                    "average_response_time": 2.3,
                    "success_rate": 98.5,
                    "cache_hit_rate": 35.2,
                    "memory_usage": 45.0,
                    "cpu_usage": 25.0
                },
                "active_executions": 2
            }
        }


# ===== ERROR MODELS =====

class ValidationError(BaseModel):
    """Validation error details"""
    field: str = Field(..., description="Field that failed validation")
    rule: str = Field(..., description="Validation rule that was violated")
    message: str = Field(..., description="Error message")
    received_value: Optional[Any] = Field(None, description="Received value")
    expected_format: Optional[str] = Field(None, description="Expected value format")


class ApiError(BaseModel):
    """API error response"""
    error_type: str = Field(..., description="Error type")
    message: str = Field(..., description="Human-readable error message")
    details: Optional[Dict[str, Any]] = Field(None, description="Error details")
    request_id: Optional[str] = Field(None, description="Request ID for tracking")
    timestamp: float = Field(..., description="Timestamp of error")
    stack_trace: Optional[str] = Field(None, description="Stack trace (development only)")
    validation_errors: Optional[List[ValidationError]] = Field(None, description="Validation error details")

    class Config:
        schema_extra = {
            "example": {
                "error_type": "validation_error",
                "message": "Request validation failed",
                "details": {"field": "headline", "issue": "too_short"},
                "request_id": "req_12345",
                "timestamp": 1638360000.0,
                "validation_errors": [
                    {
                        "field": "headline",
                        "rule": "min_length",
                        "message": "Headline must be at least 1 character long",
                        "received_value": "",
                        "expected_format": "non-empty string"
                    }
                ]
            }
        }


# ===== ANALYTICS MODELS =====

class ToolUsageStats(BaseModel):
    """Tool usage statistics"""
    total_executions: int = Field(..., ge=0, description="Total executions")
    success_rate: float = Field(..., ge=0, le=100, description="Success rate")
    average_execution_time: float = Field(..., ge=0, description="Average execution time")
    average_confidence: float = Field(..., ge=0, le=100, description="Average confidence score")


class PerformanceMetrics(BaseModel):
    """Performance metrics"""
    average_overall_score: float = Field(..., ge=0, le=100, description="Average overall score")
    score_distribution: Dict[str, int] = Field(..., description="Score distribution")
    top_recommendations: List[Dict[str, Union[str, int]]] = Field(..., description="Most common recommendations")
    average_improvement_potential: float = Field(..., ge=0, le=100, description="Average improvement potential")


class UsageAnalytics(BaseModel):
    """Usage analytics data"""
    period: str = Field(..., description="Time period for analytics")
    analysis_type_usage: Dict[str, int] = Field(..., description="Analysis type usage breakdown")
    tool_usage: Dict[str, ToolUsageStats] = Field(..., description="Tool usage statistics")
    performance_metrics: PerformanceMetrics = Field(..., description="Performance metrics")
    industry_breakdown: Dict[str, int] = Field(..., description="Industry breakdown")
    platform_breakdown: Dict[str, int] = Field(..., description="Platform breakdown")


# ===== UTILITY MODELS =====

class PaginationMetadata(BaseModel):
    """Pagination metadata"""
    page: int = Field(..., ge=1, description="Current page number")
    per_page: int = Field(..., ge=1, le=100, description="Items per page")
    total_items: int = Field(..., ge=0, description="Total number of items")
    total_pages: int = Field(..., ge=0, description="Total number of pages")
    has_next: bool = Field(..., description="Whether there are more pages")
    has_prev: bool = Field(..., description="Whether there are previous pages")


class PaginatedResponse(BaseModel):
    """Paginated response wrapper"""
    data: List[Any] = Field(..., description="Data items")
    pagination: PaginationMetadata = Field(..., description="Pagination metadata")


# ===== JSON SCHEMA GENERATION =====

def generate_openapi_schemas() -> Dict[str, Any]:
    """Generate OpenAPI schemas for all models"""
    schemas = {}
    
    # Core models
    schemas['AnalysisRequest'] = AnalysisRequest.schema()
    schemas['AnalysisResponse'] = AnalysisResponse.schema()
    schemas['BatchAnalysisRequest'] = BatchAnalysisRequest.schema()
    schemas['BatchAnalysisResponse'] = BatchAnalysisResponse.schema()
    
    # Configuration models
    schemas['FlowConfiguration'] = FlowConfiguration.schema()
    schemas['FlowStep'] = FlowStep.schema()
    schemas['ToolConfig'] = ToolConfig.schema()
    
    # Health and status models
    schemas['HealthCheckResponse'] = HealthCheckResponse.schema()
    schemas['SystemStatistics'] = SystemStatistics.schema()
    
    # Error models
    schemas['ApiError'] = ApiError.schema()
    schemas['ValidationError'] = ValidationError.schema()
    
    # Analytics models
    schemas['UsageAnalytics'] = UsageAnalytics.schema()
    schemas['PerformanceMetrics'] = PerformanceMetrics.schema()
    
    return schemas


def save_schemas_to_file(file_path: str):
    """Save all schemas to a JSON file"""
    schemas = generate_openapi_schemas()
    
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(schemas, f, indent=2, ensure_ascii=False)


# ===== VALIDATION FUNCTIONS =====

def validate_analysis_request(data: Dict[str, Any]) -> AnalysisRequest:
    """Validate and parse analysis request data"""
    return AnalysisRequest.parse_obj(data)


def validate_batch_request(data: Dict[str, Any]) -> BatchAnalysisRequest:
    """Validate and parse batch analysis request data"""
    return BatchAnalysisRequest.parse_obj(data)


def validate_flow_configuration(data: Dict[str, Any]) -> FlowConfiguration:
    """Validate and parse flow configuration data"""
    return FlowConfiguration.parse_obj(data)


# ===== RESPONSE BUILDERS =====

def build_error_response(
    error_type: str,
    message: str,
    request_id: Optional[str] = None,
    details: Optional[Dict[str, Any]] = None,
    validation_errors: Optional[List[ValidationError]] = None
) -> ApiError:
    """Build standardized error response"""
    import time
    
    return ApiError(
        error_type=error_type,
        message=message,
        details=details,
        request_id=request_id,
        timestamp=time.time(),
        validation_errors=validation_errors
    )


def build_success_response(data: Any, message: str = "Success") -> Dict[str, Any]:
    """Build standardized success response"""
    import time
    
    return {
        "success": True,
        "message": message,
        "data": data,
        "timestamp": time.time()
    }


# Export all schemas for external use
__all__ = [
    # Models
    'AnalysisRequest', 'AnalysisResponse', 'BrandGuidelines',
    'BatchAnalysisRequest', 'BatchAnalysisResponse', 'BatchOptions', 'BatchStatistics',
    'FlowConfiguration', 'FlowStep', 'ToolConfig',
    'HealthCheckResponse', 'SystemStatistics',
    'ApiError', 'ValidationError',
    'UsageAnalytics', 'PerformanceMetrics', 'ToolUsageStats',
    'CopyVariation', 'Alternative', 'ToolResult', 'ToolResults',
    'ExecutionMetadata', 'PaginatedResponse', 'PaginationMetadata',
    
    # Enums
    'AnalysisType', 'ExecutionStrategy', 'Priority', 'Severity', 'HealthStatus',
    
    # Functions
    'generate_openapi_schemas', 'save_schemas_to_file',
    'validate_analysis_request', 'validate_batch_request', 'validate_flow_configuration',
    'build_error_response', 'build_success_response'
]