"""
Tool orchestrator for chaining and coordinating multiple tools
"""

import asyncio
import time
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
from datetime import datetime

from .core import ToolInput, ToolOutput, ToolType
from .registry import ToolRegistry, default_registry
from .exceptions import ToolError, ToolTimeoutError


@dataclass
class OrchestrationResult:
    """Result of tool orchestration"""
    
    success: bool
    total_execution_time: float
    tool_results: Dict[str, ToolOutput] = field(default_factory=dict)
    errors: List[Dict[str, Any]] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    
    # Aggregated scores from all tools
    aggregated_scores: Dict[str, float] = field(default_factory=dict)
    overall_score: Optional[float] = None
    
    # Metadata
    request_id: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.utcnow)
    
    def get_successful_tools(self) -> List[str]:
        """Get names of tools that executed successfully"""
        return [
            tool_name for tool_name, result in self.tool_results.items()
            if result.success
        ]
    
    def get_failed_tools(self) -> List[str]:
        """Get names of tools that failed"""
        return [
            error['tool_name'] for error in self.errors
            if 'tool_name' in error
        ]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            'success': self.success,
            'total_execution_time': self.total_execution_time,
            'tool_results': {
                name: result.to_dict() for name, result in self.tool_results.items()
            },
            'errors': self.errors,
            'warnings': self.warnings,
            'aggregated_scores': self.aggregated_scores,
            'overall_score': self.overall_score,
            'request_id': self.request_id,
            'timestamp': self.timestamp.isoformat(),
            'successful_tools': self.get_successful_tools(),
            'failed_tools': self.get_failed_tools()
        }


class ToolOrchestrator:
    """Coordinates execution of multiple tools"""
    
    def __init__(self, registry: ToolRegistry = None):
        self.registry = registry or default_registry
        self.score_weights = {
            'clarity': 0.2,
            'persuasion': 0.25,
            'emotion': 0.2,
            'cta_strength': 0.25,
            'platform_fit': 0.1
        }
    
    async def run_tools(
        self,
        input_data: ToolInput,
        tool_names: List[str],
        execution_mode: str = "parallel"
    ) -> OrchestrationResult:
        """
        Execute multiple tools on the same input
        
        Args:
            input_data: Unified input for all tools
            tool_names: List of tool names to execute
            execution_mode: "parallel", "sequential", or "mixed"
            
        Returns:
            OrchestrationResult with all tool outputs
        """
        start_time = time.time()
        
        result = OrchestrationResult(
            success=True,
            total_execution_time=0.0,
            request_id=input_data.request_id
        )
        
        if execution_mode == "parallel":
            await self._run_tools_parallel(input_data, tool_names, result)
        elif execution_mode == "sequential":
            await self._run_tools_sequential(input_data, tool_names, result)
        else:
            await self._run_tools_mixed(input_data, tool_names, result)
        
        result.total_execution_time = time.time() - start_time
        
        # Calculate aggregated scores and overall score
        self._calculate_aggregated_scores(result)
        
        # Determine overall success
        result.success = len(result.get_successful_tools()) > len(result.get_failed_tools())
        
        return result
    
    async def _run_tools_parallel(
        self,
        input_data: ToolInput,
        tool_names: List[str],
        result: OrchestrationResult
    ):
        """Execute tools in parallel"""
        tasks = []
        
        for tool_name in tool_names:
            task = asyncio.create_task(
                self._execute_single_tool(tool_name, input_data),
                name=tool_name
            )
            tasks.append(task)
        
        # Wait for all tasks to complete
        completed_tasks = await asyncio.gather(*tasks, return_exceptions=True)
        
        for i, task_result in enumerate(completed_tasks):
            tool_name = tool_names[i]
            
            if isinstance(task_result, Exception):
                self._handle_tool_error(tool_name, task_result, result)
            else:
                result.tool_results[tool_name] = task_result
    
    async def _run_tools_sequential(
        self,
        input_data: ToolInput,
        tool_names: List[str],
        result: OrchestrationResult
    ):
        """Execute tools sequentially"""
        for tool_name in tool_names:
            try:
                tool_output = await self._execute_single_tool(tool_name, input_data)
                result.tool_results[tool_name] = tool_output
                
                # Could potentially modify input_data based on previous results
                # for tool chaining scenarios
                
            except Exception as e:
                self._handle_tool_error(tool_name, e, result)
                
                # In sequential mode, decide whether to continue or abort
                if self._should_abort_on_error(tool_name, e):
                    result.warnings.append(f"Aborting sequential execution due to critical error in {tool_name}")
                    break
    
    async def _run_tools_mixed(
        self,
        input_data: ToolInput,
        tool_names: List[str],
        result: OrchestrationResult
    ):
        """Execute tools in mixed mode (some parallel, some sequential)"""
        # Group tools by type for intelligent execution
        tool_groups = self._group_tools_by_execution_priority(tool_names)
        
        # Execute analyzers first (parallel)
        if tool_groups.get('analyzers'):
            await self._run_tools_parallel(input_data, tool_groups['analyzers'], result)
        
        # Execute generators next (parallel)  
        if tool_groups.get('generators'):
            await self._run_tools_parallel(input_data, tool_groups['generators'], result)
        
        # Execute reporters last (could depend on previous results)
        if tool_groups.get('reporters'):
            await self._run_tools_sequential(input_data, tool_groups['reporters'], result)
    
    def _group_tools_by_execution_priority(self, tool_names: List[str]) -> Dict[str, List[str]]:
        """Group tools by their optimal execution order"""
        groups = {
            'analyzers': [],
            'generators': [],
            'reporters': []
        }
        
        for tool_name in tool_names:
            try:
                tool_info = self.registry.get_tool_info(tool_name)
                tool_type = tool_info.get('tool_type', ToolType.ANALYZER)
                
                if tool_type in [ToolType.ANALYZER, ToolType.VALIDATOR]:
                    groups['analyzers'].append(tool_name)
                elif tool_type in [ToolType.GENERATOR, ToolType.OPTIMIZER]:
                    groups['generators'].append(tool_name)
                elif tool_type == ToolType.REPORTER:
                    groups['reporters'].append(tool_name)
                else:
                    groups['analyzers'].append(tool_name)  # Default
                    
            except Exception:
                groups['analyzers'].append(tool_name)  # Safe default
        
        return groups
    
    async def _execute_single_tool(self, tool_name: str, input_data: ToolInput) -> ToolOutput:
        """Execute a single tool with error handling"""
        try:
            tool = self.registry.get_tool(tool_name)
            
            # Validate input
            if not tool.validate_input(input_data):
                raise ToolError(
                    f"Input validation failed for tool '{tool_name}'",
                    tool_name=tool_name
                )
            
            # Execute with timeout
            try:
                output = await asyncio.wait_for(
                    tool.run(input_data),
                    timeout=tool.config.timeout
                )
                return output
            except asyncio.TimeoutError:
                raise ToolTimeoutError(tool_name, tool.config.timeout)
                
        except Exception as e:
            # Re-raise as ToolError if not already
            if not isinstance(e, ToolError):
                raise ToolError(
                    f"Unexpected error in tool '{tool_name}': {str(e)}",
                    tool_name=tool_name
                ) from e
            raise
    
    def _handle_tool_error(self, tool_name: str, error: Exception, result: OrchestrationResult):
        """Handle and record tool execution errors"""
        error_dict = {
            'tool_name': tool_name,
            'error_type': type(error).__name__,
            'error_message': str(error),
            'timestamp': datetime.utcnow().isoformat()
        }
        
        # Add additional context for ToolError instances
        if isinstance(error, ToolError):
            error_dict.update({
                'error_code': error.error_code,
                'details': error.details
            })
        
        result.errors.append(error_dict)
    
    def _should_abort_on_error(self, tool_name: str, error: Exception) -> bool:
        """Determine if sequential execution should abort on this error"""
        # Only abort on critical configuration errors, not execution errors
        if isinstance(error, ToolError):
            return error.error_code in ['TOOL_CONFIG_ERROR', 'TOOL_NOT_FOUND']
        return False
    
    def _calculate_aggregated_scores(self, result: OrchestrationResult):
        """Calculate aggregated scores from all successful tool results"""
        all_scores = {}
        score_counts = {}
        
        # Collect all scores from successful tools
        for tool_name, tool_output in result.tool_results.items():
            if tool_output.success:
                for score_name, score_value in tool_output.scores.items():
                    if score_name not in all_scores:
                        all_scores[score_name] = 0
                        score_counts[score_name] = 0
                    
                    all_scores[score_name] += score_value
                    score_counts[score_name] += 1
        
        # Calculate averages
        for score_name in all_scores:
            if score_counts[score_name] > 0:
                result.aggregated_scores[score_name] = all_scores[score_name] / score_counts[score_name]
        
        # Calculate overall score using weights
        if result.aggregated_scores:
            weighted_sum = 0
            weight_sum = 0
            
            for score_name, weight in self.score_weights.items():
                if score_name in result.aggregated_scores:
                    weighted_sum += result.aggregated_scores[score_name] * weight
                    weight_sum += weight
            
            if weight_sum > 0:
                result.overall_score = weighted_sum / weight_sum
    
    async def health_check_tools(self, tool_names: List[str] = None) -> Dict[str, Dict[str, Any]]:
        """
        Run health checks on specified tools or all registered tools
        
        Args:
            tool_names: List of tool names to check, or None for all
            
        Returns:
            Dictionary mapping tool names to health check results
        """
        if tool_names is None:
            tool_names = self.registry.list_tools()
        
        health_results = {}
        
        # Run health checks in parallel
        tasks = []
        for tool_name in tool_names:
            try:
                tool = self.registry.get_tool(tool_name)
                task = asyncio.create_task(
                    tool.health_check(),
                    name=f"health_check_{tool_name}"
                )
                tasks.append((tool_name, task))
            except Exception as e:
                health_results[tool_name] = {
                    'status': 'error',
                    'error': str(e),
                    'tool_available': False
                }
        
        # Wait for all health checks
        for tool_name, task in tasks:
            try:
                health_result = await asyncio.wait_for(task, timeout=10.0)
                health_results[tool_name] = health_result
            except asyncio.TimeoutError:
                health_results[tool_name] = {
                    'status': 'timeout',
                    'error': 'Health check timed out',
                    'tool_available': True
                }
            except Exception as e:
                health_results[tool_name] = {
                    'status': 'error',
                    'error': str(e),
                    'tool_available': True
                }
        
        return health_results
    
    def get_tool_capabilities(self) -> Dict[str, Dict[str, Any]]:
        """Get capabilities of all registered tools"""
        capabilities = {}
        
        for tool_name in self.registry.list_tools():
            try:
                capabilities[tool_name] = self.registry.get_tool_info(tool_name)
            except Exception as e:
                capabilities[tool_name] = {
                    'error': str(e),
                    'available': False
                }
        
        return capabilities