"""
Core SDK interfaces and data models for unified tool integration
"""

import uuid
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional, Union
from datetime import datetime
from enum import Enum


class ToolType(str, Enum):
    """Tool categorization for routing and orchestration"""
    ANALYZER = "analyzer"          # Analyzes content (readability, emotion, CTA)
    GENERATOR = "generator"        # Generates alternatives (AI, templates)
    OPTIMIZER = "optimizer"        # Optimizes for platforms, industries
    VALIDATOR = "validator"        # Validates compliance, legal
    REPORTER = "reporter"          # Creates reports, exports


class ToolExecutionMode(str, Enum):
    """Tool execution modes"""
    SYNC = "sync"                  # Synchronous execution
    ASYNC = "async"                # Asynchronous execution  
    BATCH = "batch"                # Batch processing


@dataclass
class ToolInput:
    """Unified input structure for all tools"""
    
    # Core ad copy data - REQUIRED
    headline: str
    body_text: str
    cta: str
    platform: str
    
    # Context data - OPTIONAL but recommended
    industry: Optional[str] = None
    target_audience: Optional[str] = None
    brand_voice: Optional[str] = None
    campaign_goal: Optional[str] = None
    
    # Tool-specific parameters
    tool_params: Dict[str, Any] = field(default_factory=dict)
    
    # Metadata
    request_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = field(default_factory=datetime.utcnow)
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            'headline': self.headline,
            'body_text': self.body_text, 
            'cta': self.cta,
            'platform': self.platform,
            'industry': self.industry,
            'target_audience': self.target_audience,
            'brand_voice': self.brand_voice,
            'campaign_goal': self.campaign_goal,
            'tool_params': self.tool_params,
            'request_id': self.request_id,
            'timestamp': self.timestamp.isoformat(),
            'user_id': self.user_id,
            'session_id': self.session_id
        }
    
    @classmethod
    def from_legacy_ad_input(cls, ad_data: Dict[str, Any], **kwargs) -> 'ToolInput':
        """Create ToolInput from legacy ad input formats"""
        return cls(
            headline=ad_data.get('headline', ''),
            body_text=ad_data.get('body_text', ''),
            cta=ad_data.get('cta', ''),
            platform=ad_data.get('platform', 'facebook'),
            industry=ad_data.get('industry'),
            target_audience=ad_data.get('target_audience'), 
            brand_voice=ad_data.get('brand_voice'),
            campaign_goal=ad_data.get('campaign_goal'),
            **kwargs
        )


@dataclass
class ToolOutput:
    """Unified output structure for all tools"""
    
    # Core results
    tool_name: str
    tool_type: ToolType
    success: bool
    
    # Analysis results
    scores: Dict[str, float] = field(default_factory=dict)
    insights: Dict[str, Any] = field(default_factory=dict)
    recommendations: List[str] = field(default_factory=list)
    
    # Generated content (for generators)
    generated_content: List[Dict[str, Any]] = field(default_factory=list)
    
    # Metadata
    execution_time: float = 0.0
    timestamp: datetime = field(default_factory=datetime.utcnow)
    request_id: Optional[str] = None
    confidence_score: Optional[float] = None
    
    # Error information
    error_message: Optional[str] = None
    warnings: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            'tool_name': self.tool_name,
            'tool_type': self.tool_type,
            'success': self.success,
            'scores': self.scores,
            'insights': self.insights,
            'recommendations': self.recommendations,
            'generated_content': self.generated_content,
            'execution_time': self.execution_time,
            'timestamp': self.timestamp.isoformat(),
            'request_id': self.request_id,
            'confidence_score': self.confidence_score,
            'error_message': self.error_message,
            'warnings': self.warnings
        }


@dataclass
class ToolConfig:
    """Configuration for tool execution"""
    
    name: str
    tool_type: ToolType
    execution_mode: ToolExecutionMode = ToolExecutionMode.SYNC
    timeout: float = 30.0
    retry_count: int = 2
    fallback_enabled: bool = True
    
    # Tool-specific configuration
    parameters: Dict[str, Any] = field(default_factory=dict)
    
    # API keys and credentials
    credentials: Dict[str, str] = field(default_factory=dict)
    
    # Performance settings
    cache_enabled: bool = True
    cache_ttl: int = 3600  # seconds
    max_batch_size: int = 10
    
    def get_parameter(self, key: str, default: Any = None) -> Any:
        """Get a parameter value with fallback"""
        return self.parameters.get(key, default)


class ToolRunner(ABC):
    """
    Abstract base class for all tool runners
    
    This is the core interface that all tools must implement to be part of 
    the unified SDK. Each tool provides a consistent run() method that accepts
    ToolInput and returns ToolOutput.
    """
    
    def __init__(self, config: ToolConfig):
        self.config = config
        self.name = config.name
        self.tool_type = config.tool_type
        
    @abstractmethod
    async def run(self, input_data: ToolInput) -> ToolOutput:
        """
        Main execution method - must be implemented by each tool
        
        Args:
            input_data: Unified input structure
            
        Returns:
            ToolOutput with results, scores, and recommendations
        """
        pass
    
    @abstractmethod
    def validate_input(self, input_data: ToolInput) -> bool:
        """
        Validate that the input data is sufficient for this tool
        
        Args:
            input_data: Input to validate
            
        Returns:
            True if input is valid, raises exception if not
        """
        pass
    
    def get_capabilities(self) -> Dict[str, Any]:
        """
        Get tool capabilities and metadata
        
        Returns:
            Dictionary describing what this tool can do
        """
        return {
            'name': self.name,
            'tool_type': self.tool_type,
            'execution_mode': self.config.execution_mode,
            'timeout': self.config.timeout,
            'fallback_enabled': self.config.fallback_enabled,
            'supported_platforms': self.get_supported_platforms(),
            'required_fields': self.get_required_fields(),
            'output_scores': self.get_output_scores()
        }
    
    def get_supported_platforms(self) -> List[str]:
        """Get list of supported platforms"""
        return ['facebook', 'google', 'linkedin', 'tiktok', 'instagram']
    
    def get_required_fields(self) -> List[str]:
        """Get list of required input fields"""
        return ['headline', 'body_text', 'cta', 'platform']
    
    def get_output_scores(self) -> List[str]:
        """Get list of scores this tool outputs"""
        return []
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Check if the tool is healthy and ready to process requests
        
        Returns:
            Dictionary with health status
        """
        try:
            # Basic test input
            test_input = ToolInput(
                headline="Test Headline",
                body_text="Test body text for health check",
                cta="Test Now",
                platform="facebook"
            )
            
            # Quick validation test
            is_valid = self.validate_input(test_input)
            
            return {
                'tool_name': self.name,
                'status': 'healthy',
                'validation_working': is_valid,
                'last_check': datetime.utcnow().isoformat()
            }
        except Exception as e:
            return {
                'tool_name': self.name,
                'status': 'unhealthy',
                'error': str(e),
                'last_check': datetime.utcnow().isoformat()
            }