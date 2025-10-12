"""
Tools Flow Orchestrator - Coordinates multiple tools and unifies their outputs
Manages tool execution order, dependencies, parallel processing, and output aggregation
"""

import asyncio
import time
import uuid
from typing import Dict, Any, List, Optional, Union, Set, Tuple
from dataclasses import dataclass, field
from enum import Enum
from concurrent.futures import ThreadPoolExecutor
import logging

from ..core import ToolRunner, ToolInput, ToolOutput, ToolConfig, ToolType
from ..exceptions import ToolValidationError, ToolExecutionError
from ..tools.performance_forensics_tool import PerformanceForensicsToolRunner
from ..tools.psychology_scorer_tool import PsychologyScorerToolRunner
from ..tools.brand_voice_engine_tool import BrandVoiceEngineToolRunner
from ..tools.legal_risk_scanner_tool import LegalRiskScannerToolRunner


class FlowExecutionStrategy(Enum):
    """Strategy for executing tools in a flow"""
    SEQUENTIAL = "sequential"
    PARALLEL = "parallel"
    MIXED = "mixed"  # Some tools parallel, some sequential based on dependencies


class FlowPriority(Enum):
    """Priority levels for flow execution"""
    LOW = 1
    NORMAL = 2
    HIGH = 3
    CRITICAL = 4


@dataclass
class ToolFlowStep:
    """Individual step in a tool flow"""
    tool_name: str
    tool_class: type
    config: ToolConfig
    dependencies: Set[str] = field(default_factory=set)
    parallel_group: Optional[str] = None
    required: bool = True
    timeout_override: Optional[float] = None
    retry_count: int = 1


@dataclass
class FlowConfiguration:
    """Configuration for a complete tool flow"""
    flow_id: str
    name: str
    description: str
    steps: List[ToolFlowStep]
    execution_strategy: FlowExecutionStrategy = FlowExecutionStrategy.MIXED
    priority: FlowPriority = FlowPriority.NORMAL
    max_parallel_workers: int = 4
    total_timeout: Optional[float] = None
    continue_on_error: bool = True
    output_aggregation_strategy: str = "weighted_average"


@dataclass
class FlowExecutionResult:
    """Result of a complete flow execution"""
    flow_id: str
    execution_id: str
    success: bool
    total_execution_time: float
    tool_results: Dict[str, ToolOutput]
    aggregated_scores: Dict[str, float]
    unified_insights: Dict[str, Any]
    combined_recommendations: List[str]
    execution_metadata: Dict[str, Any]
    error_summary: Optional[Dict[str, Any]] = None


class ToolsFlowOrchestrator:
    """
    Main orchestrator for coordinating multiple ad copy analysis tools
    
    Features:
    - Sequential and parallel tool execution
    - Dependency management between tools
    - Output aggregation and unification
    - Error handling and partial result recovery
    - Configurable flow templates
    - Performance optimization
    """
    
    def __init__(self, max_workers: int = 4):
        self.max_workers = max_workers
        self.logger = logging.getLogger(__name__)
        
        # Available tools registry
        self.available_tools = {
            'performance_forensics': PerformanceForensicsToolRunner,
            'psychology_scorer': PsychologyScorerToolRunner,
            'brand_voice_engine': BrandVoiceEngineToolRunner,
            'legal_risk_scanner': LegalRiskScannerToolRunner
        }
        
        # Pre-defined flow configurations
        self.flow_templates = self._initialize_flow_templates()
        
        # Execution tracking
        self.active_executions: Dict[str, Dict[str, Any]] = {}
        
        # Tool weight configurations for score aggregation
        self.tool_weights = {
            'performance_forensics': {
                'ctr_prediction_score': 0.25,
                'conversion_optimization_score': 0.25,
                'engagement_forecast_score': 0.20,
                'overall_performance_score': 0.30
            },
            'psychology_scorer': {
                'persuasion_strength_score': 0.30,
                'emotional_impact_score': 0.25,
                'cognitive_influence_score': 0.25,
                'overall_psychology_score': 0.20
            },
            'brand_voice_engine': {
                'brand_alignment_score': 0.25,
                'tone_consistency_score': 0.25,
                'voice_authenticity_score': 0.25,
                'overall_brand_score': 0.25
            },
            'legal_risk_scanner': {
                'legal_compliance_score': 0.30,
                'risk_mitigation_score': 0.25,
                'alternative_quality_score': 0.20,
                'overall_legal_safety_score': 0.25
            }
        }
    
    def _initialize_flow_templates(self) -> Dict[str, FlowConfiguration]:
        """Initialize pre-defined flow templates"""
        templates = {}
        
        # Full comprehensive analysis
        templates['comprehensive_analysis'] = FlowConfiguration(
            flow_id='comprehensive_analysis',
            name='Comprehensive Ad Copy Analysis',
            description='Complete analysis using all available tools for maximum insights',
            steps=[
                ToolFlowStep(
                    tool_name='performance_forensics',
                    tool_class=PerformanceForensicsToolRunner,
                    config=PerformanceForensicsToolRunner.default_config(),
                    parallel_group='analysis_group'
                ),
                ToolFlowStep(
                    tool_name='psychology_scorer',
                    tool_class=PsychologyScorerToolRunner,
                    config=PsychologyScorerToolRunner.default_config(),
                    parallel_group='analysis_group'
                ),
                ToolFlowStep(
                    tool_name='brand_voice_engine',
                    tool_class=BrandVoiceEngineToolRunner,
                    config=BrandVoiceEngineToolRunner.default_config(),
                    parallel_group='analysis_group'
                ),
                ToolFlowStep(
                    tool_name='legal_risk_scanner',
                    tool_class=LegalRiskScannerToolRunner,
                    config=LegalRiskScannerToolRunner.default_config(),
                    parallel_group='compliance_group'
                )
            ],
            execution_strategy=FlowExecutionStrategy.PARALLEL,
            total_timeout=120.0
        )
        
        # Quick performance check
        templates['quick_performance'] = FlowConfiguration(
            flow_id='quick_performance',
            name='Quick Performance Analysis',
            description='Fast performance and psychology analysis for quick optimization',
            steps=[
                ToolFlowStep(
                    tool_name='performance_forensics',
                    tool_class=PerformanceForensicsToolRunner,
                    config=PerformanceForensicsToolRunner.default_config(),
                    parallel_group='quick_group'
                ),
                ToolFlowStep(
                    tool_name='psychology_scorer',
                    tool_class=PsychologyScorerToolRunner,
                    config=PsychologyScorerToolRunner.default_config(),
                    parallel_group='quick_group'
                )
            ],
            execution_strategy=FlowExecutionStrategy.PARALLEL,
            total_timeout=60.0
        )
        
        # Compliance-focused analysis
        templates['compliance_check'] = FlowConfiguration(
            flow_id='compliance_check',
            name='Brand & Legal Compliance Check',
            description='Focus on brand alignment and legal compliance',
            steps=[
                ToolFlowStep(
                    tool_name='brand_voice_engine',
                    tool_class=BrandVoiceEngineToolRunner,
                    config=BrandVoiceEngineToolRunner.default_config()
                ),
                ToolFlowStep(
                    tool_name='legal_risk_scanner',
                    tool_class=LegalRiskScannerToolRunner,
                    config=LegalRiskScannerToolRunner.default_config(),
                    dependencies={'brand_voice_engine'}  # Run after brand analysis
                )
            ],
            execution_strategy=FlowExecutionStrategy.SEQUENTIAL,
            total_timeout=90.0
        )
        
        # Performance optimization focused
        templates['optimization_focused'] = FlowConfiguration(
            flow_id='optimization_focused',
            name='Performance Optimization Analysis',
            description='Deep dive into performance metrics and psychological triggers',
            steps=[
                ToolFlowStep(
                    tool_name='performance_forensics',
                    tool_class=PerformanceForensicsToolRunner,
                    config=PerformanceForensicsToolRunner.default_config()
                ),
                ToolFlowStep(
                    tool_name='psychology_scorer',
                    tool_class=PsychologyScorerToolRunner,
                    config=PsychologyScorerToolRunner.default_config(),
                    dependencies={'performance_forensics'}  # Use performance insights
                )
            ],
            execution_strategy=FlowExecutionStrategy.SEQUENTIAL,
            total_timeout=90.0
        )
        
        return templates
    
    async def execute_flow(self, flow_config: Union[str, FlowConfiguration], 
                          input_data: ToolInput) -> FlowExecutionResult:
        """Execute a complete tool flow"""
        execution_id = str(uuid.uuid4())
        start_time = time.time()
        
        # Resolve flow configuration
        if isinstance(flow_config, str):
            if flow_config not in self.flow_templates:
                raise ValueError(f"Unknown flow template: {flow_config}")
            flow_config = self.flow_templates[flow_config]
        
        self.logger.info(f"Starting flow execution: {flow_config.flow_id} [{execution_id}]")
        
        # Track execution
        self.active_executions[execution_id] = {
            'flow_id': flow_config.flow_id,
            'start_time': start_time,
            'status': 'running',
            'completed_tools': set(),
            'failed_tools': set()
        }
        
        try:
            # Validate flow configuration
            self._validate_flow_configuration(flow_config)
            
            # Execute tools based on strategy
            tool_results = await self._execute_tools_by_strategy(
                flow_config, input_data, execution_id
            )
            
            # Aggregate results
            aggregated_scores = self._aggregate_scores(tool_results)
            unified_insights = self._unify_insights(tool_results)
            combined_recommendations = self._combine_recommendations(tool_results)
            
            execution_time = time.time() - start_time
            
            # Determine overall success
            successful_tools = [name for name, result in tool_results.items() if result.success]
            failed_tools = [name for name, result in tool_results.items() if not result.success]
            
            overall_success = len(successful_tools) > 0 and (
                flow_config.continue_on_error or len(failed_tools) == 0
            )
            
            # Create execution result
            result = FlowExecutionResult(
                flow_id=flow_config.flow_id,
                execution_id=execution_id,
                success=overall_success,
                total_execution_time=execution_time,
                tool_results=tool_results,
                aggregated_scores=aggregated_scores,
                unified_insights=unified_insights,
                combined_recommendations=combined_recommendations,
                execution_metadata={
                    'successful_tools': successful_tools,
                    'failed_tools': failed_tools,
                    'execution_strategy': flow_config.execution_strategy.value,
                    'total_tools': len(flow_config.steps)
                }
            )
            
            if failed_tools:
                result.error_summary = {
                    'failed_tools': failed_tools,
                    'error_details': {
                        name: result.error_message 
                        for name, result in tool_results.items() 
                        if not result.success
                    }
                }
            
            self.logger.info(
                f"Flow execution completed: {flow_config.flow_id} [{execution_id}] "
                f"- Success: {overall_success}, Time: {execution_time:.2f}s"
            )
            
            return result
            
        except Exception as e:
            execution_time = time.time() - start_time
            self.logger.error(f"Flow execution failed: {flow_config.flow_id} [{execution_id}] - {str(e)}")
            
            return FlowExecutionResult(
                flow_id=flow_config.flow_id,
                execution_id=execution_id,
                success=False,
                total_execution_time=execution_time,
                tool_results={},
                aggregated_scores={},
                unified_insights={},
                combined_recommendations=[],
                execution_metadata={'error': str(e)},
                error_summary={'fatal_error': str(e)}
            )
        
        finally:
            # Clean up execution tracking
            if execution_id in self.active_executions:
                del self.active_executions[execution_id]
    
    def _validate_flow_configuration(self, flow_config: FlowConfiguration):
        """Validate flow configuration before execution"""
        if not flow_config.steps:
            raise ValueError("Flow configuration must have at least one step")
        
        # Check for circular dependencies
        self._check_circular_dependencies(flow_config)
        
        # Validate tool availability
        for step in flow_config.steps:
            if step.tool_name not in self.available_tools:
                raise ValueError(f"Unknown tool: {step.tool_name}")
    
    def _check_circular_dependencies(self, flow_config: FlowConfiguration):
        """Check for circular dependencies in flow configuration"""
        # Build dependency graph
        dependencies = {}
        for step in flow_config.steps:
            dependencies[step.tool_name] = step.dependencies
        
        # DFS to detect cycles
        visited = set()
        rec_stack = set()
        
        def has_cycle(node):
            if node in rec_stack:
                return True
            if node in visited:
                return False
            
            visited.add(node)
            rec_stack.add(node)
            
            for neighbor in dependencies.get(node, set()):
                if has_cycle(neighbor):
                    return True
            
            rec_stack.remove(node)
            return False
        
        for tool_name in dependencies:
            if has_cycle(tool_name):
                raise ValueError(f"Circular dependency detected involving: {tool_name}")
    
    async def _execute_tools_by_strategy(self, flow_config: FlowConfiguration, 
                                       input_data: ToolInput, execution_id: str) -> Dict[str, ToolOutput]:
        """Execute tools based on the specified strategy"""
        
        if flow_config.execution_strategy == FlowExecutionStrategy.SEQUENTIAL:
            return await self._execute_sequential(flow_config, input_data, execution_id)
        elif flow_config.execution_strategy == FlowExecutionStrategy.PARALLEL:
            return await self._execute_parallel(flow_config, input_data, execution_id)
        else:  # MIXED
            return await self._execute_mixed(flow_config, input_data, execution_id)
    
    async def _execute_sequential(self, flow_config: FlowConfiguration, 
                                input_data: ToolInput, execution_id: str) -> Dict[str, ToolOutput]:
        """Execute tools sequentially"""
        results = {}
        
        # Sort steps by dependencies
        sorted_steps = self._topological_sort(flow_config.steps)
        
        for step in sorted_steps:
            try:
                tool_runner = step.tool_class(step.config)
                result = await tool_runner.run(input_data)
                results[step.tool_name] = result
                
                self.active_executions[execution_id]['completed_tools'].add(step.tool_name)
                
                if not result.success and not flow_config.continue_on_error:
                    self.logger.warning(f"Tool {step.tool_name} failed, stopping execution")
                    break
                    
            except Exception as e:
                self.logger.error(f"Error executing tool {step.tool_name}: {str(e)}")
                results[step.tool_name] = self._create_error_result(step.tool_name, str(e), input_data)
                self.active_executions[execution_id]['failed_tools'].add(step.tool_name)
                
                if not flow_config.continue_on_error:
                    break
        
        return results
    
    async def _execute_parallel(self, flow_config: FlowConfiguration, 
                              input_data: ToolInput, execution_id: str) -> Dict[str, ToolOutput]:
        """Execute tools in parallel where possible"""
        results = {}
        
        # Group steps by parallel groups and dependencies
        parallel_groups = self._group_steps_for_parallel_execution(flow_config.steps)
        
        for group in parallel_groups:
            # Execute current group in parallel
            group_tasks = []
            
            for step in group:
                task = self._execute_single_tool(step, input_data, execution_id)
                group_tasks.append((step.tool_name, task))
            
            # Wait for all tasks in this group to complete
            group_results = await asyncio.gather(*[task for _, task in group_tasks], return_exceptions=True)
            
            # Process group results
            for (tool_name, _), result in zip(group_tasks, group_results):
                if isinstance(result, Exception):
                    self.logger.error(f"Error executing tool {tool_name}: {str(result)}")
                    results[tool_name] = self._create_error_result(tool_name, str(result), input_data)
                    self.active_executions[execution_id]['failed_tools'].add(tool_name)
                else:
                    results[tool_name] = result
                    self.active_executions[execution_id]['completed_tools'].add(tool_name)
        
        return results
    
    async def _execute_mixed(self, flow_config: FlowConfiguration, 
                           input_data: ToolInput, execution_id: str) -> Dict[str, ToolOutput]:
        """Execute tools using mixed strategy (optimal parallelization)"""
        # This is similar to parallel execution but more intelligent about dependencies
        return await self._execute_parallel(flow_config, input_data, execution_id)
    
    async def _execute_single_tool(self, step: ToolFlowStep, 
                                 input_data: ToolInput, execution_id: str) -> ToolOutput:
        """Execute a single tool with proper error handling"""
        try:
            tool_runner = step.tool_class(step.config)
            
            # Apply timeout override if specified
            if step.timeout_override:
                # In a real implementation, you'd set this on the tool runner
                pass
            
            result = await tool_runner.run(input_data)
            return result
            
        except Exception as e:
            raise e
    
    def _topological_sort(self, steps: List[ToolFlowStep]) -> List[ToolFlowStep]:
        """Sort steps based on dependencies using topological sort"""
        # Build adjacency lists
        graph = {step.tool_name: list(step.dependencies) for step in steps}
        step_map = {step.tool_name: step for step in steps}
        
        # Kahn's algorithm
        in_degree = {name: 0 for name in graph}
        for node in graph:
            for neighbor in graph[node]:
                if neighbor in in_degree:
                    in_degree[neighbor] += 1
        
        queue = [node for node in in_degree if in_degree[node] == 0]
        result = []
        
        while queue:
            current = queue.pop(0)
            result.append(step_map[current])
            
            for neighbor in graph[current]:
                if neighbor in in_degree:
                    in_degree[neighbor] -= 1
                    if in_degree[neighbor] == 0:
                        queue.append(neighbor)
        
        return result
    
    def _group_steps_for_parallel_execution(self, steps: List[ToolFlowStep]) -> List[List[ToolFlowStep]]:
        """Group steps that can be executed in parallel"""
        # Simple implementation - group by parallel_group or execute independently
        groups = []
        grouped_steps = {}
        independent_steps = []
        
        for step in steps:
            if step.parallel_group:
                if step.parallel_group not in grouped_steps:
                    grouped_steps[step.parallel_group] = []
                grouped_steps[step.parallel_group].append(step)
            else:
                independent_steps.append(step)
        
        # Add grouped steps
        for group_steps in grouped_steps.values():
            groups.append(group_steps)
        
        # Add independent steps as individual groups
        for step in independent_steps:
            groups.append([step])
        
        return groups
    
    def _create_error_result(self, tool_name: str, error_message: str, input_data: ToolInput) -> ToolOutput:
        """Create error result for failed tool execution"""
        return ToolOutput(
            tool_name=tool_name,
            tool_type=ToolType.ANALYZER,  # Default type
            success=False,
            execution_time=0.0,
            request_id=input_data.request_id,
            error_message=error_message
        )
    
    def _aggregate_scores(self, tool_results: Dict[str, ToolOutput]) -> Dict[str, float]:
        """Aggregate scores from multiple tools"""
        aggregated = {}
        
        # Collect all scores with weights
        score_contributions = {}
        
        for tool_name, result in tool_results.items():
            if not result.success or not result.scores:
                continue
                
            tool_weights = self.tool_weights.get(tool_name, {})
            
            for score_name, score_value in result.scores.items():
                if score_name not in score_contributions:
                    score_contributions[score_name] = []
                
                weight = tool_weights.get(score_name, 1.0)
                score_contributions[score_name].append((score_value, weight))
        
        # Calculate weighted averages
        for score_name, contributions in score_contributions.items():
            if contributions:
                total_weighted_score = sum(score * weight for score, weight in contributions)
                total_weight = sum(weight for _, weight in contributions)
                aggregated[score_name] = total_weighted_score / total_weight if total_weight > 0 else 0
        
        # Calculate overall composite scores
        if aggregated:
            performance_scores = [v for k, v in aggregated.items() if 'performance' in k.lower()]
            psychology_scores = [v for k, v in aggregated.items() if 'psychology' in k.lower()]
            brand_scores = [v for k, v in aggregated.items() if 'brand' in k.lower()]
            legal_scores = [v for k, v in aggregated.items() if 'legal' in k.lower()]
            
            if performance_scores:
                aggregated['overall_performance'] = sum(performance_scores) / len(performance_scores)
            if psychology_scores:
                aggregated['overall_psychology'] = sum(psychology_scores) / len(psychology_scores)
            if brand_scores:
                aggregated['overall_brand'] = sum(brand_scores) / len(brand_scores)
            if legal_scores:
                aggregated['overall_legal'] = sum(legal_scores) / len(legal_scores)
            
            # Grand overall score
            main_scores = [
                aggregated.get('overall_performance', 0) * 0.3,
                aggregated.get('overall_psychology', 0) * 0.3,
                aggregated.get('overall_brand', 0) * 0.2,
                aggregated.get('overall_legal', 0) * 0.2
            ]
            aggregated['overall_copy_quality'] = sum(main_scores)
        
        return aggregated
    
    def _unify_insights(self, tool_results: Dict[str, ToolOutput]) -> Dict[str, Any]:
        """Unify insights from multiple tools"""
        unified = {
            'performance_analysis': {},
            'psychological_profile': {},
            'brand_alignment': {},
            'legal_compliance': {},
            'cross_tool_correlations': {}
        }
        
        successful_tools = [name for name, result in tool_results.items() if result.success]
        
        # Organize insights by category
        for tool_name, result in tool_results.items():
            if not result.success or not result.insights:
                continue
                
            if tool_name == 'performance_forensics':
                unified['performance_analysis'] = result.insights
            elif tool_name == 'psychology_scorer':
                unified['psychological_profile'] = result.insights
            elif tool_name == 'brand_voice_engine':
                unified['brand_alignment'] = result.insights
            elif tool_name == 'legal_risk_scanner':
                unified['legal_compliance'] = result.insights
        
        # Add cross-tool correlations and meta-insights
        unified['cross_tool_correlations'] = self._analyze_cross_tool_correlations(tool_results)
        unified['execution_summary'] = {
            'tools_executed': len(successful_tools),
            'successful_tools': successful_tools,
            'analysis_completeness': len(successful_tools) / len(tool_results) if tool_results else 0
        }
        
        return unified
    
    def _analyze_cross_tool_correlations(self, tool_results: Dict[str, ToolOutput]) -> Dict[str, Any]:
        """Analyze correlations and patterns across different tool outputs"""
        correlations = {}
        
        # Extract key metrics for correlation analysis
        performance_data = tool_results.get('performance_forensics')
        psychology_data = tool_results.get('psychology_scorer')
        brand_data = tool_results.get('brand_voice_engine')
        legal_data = tool_results.get('legal_risk_scanner')
        
        # Analyze performance-psychology correlation
        if performance_data and psychology_data and both_successful(performance_data, psychology_data):
            perf_score = performance_data.scores.get('overall_performance_score', 0)
            psych_score = psychology_data.scores.get('overall_psychology_score', 0)
            
            correlations['performance_psychology_alignment'] = {
                'correlation_strength': abs(perf_score - psych_score) / 100,  # Simple correlation
                'analysis': self._analyze_perf_psych_alignment(perf_score, psych_score)
            }
        
        # Analyze brand-legal compliance correlation
        if brand_data and legal_data and both_successful(brand_data, legal_data):
            brand_score = brand_data.scores.get('overall_brand_score', 0)
            legal_score = legal_data.scores.get('overall_legal_safety_score', 0)
            
            correlations['brand_legal_alignment'] = {
                'correlation_strength': min(brand_score, legal_score) / 100,
                'analysis': 'Strong brand-legal alignment' if min(brand_score, legal_score) > 80 else 'Review brand-legal consistency'
            }
        
        return correlations
    
    def _analyze_perf_psych_alignment(self, perf_score: float, psych_score: float) -> str:
        """Analyze alignment between performance and psychology scores"""
        diff = abs(perf_score - psych_score)
        
        if diff < 10:
            return "Excellent performance-psychology alignment"
        elif diff < 20:
            return "Good performance-psychology alignment"
        elif diff < 30:
            return "Moderate performance-psychology alignment - consider optimization"
        else:
            return "Low performance-psychology alignment - significant optimization needed"
    
    def _combine_recommendations(self, tool_results: Dict[str, ToolOutput]) -> List[str]:
        """Combine and prioritize recommendations from multiple tools"""
        all_recommendations = []
        
        # Collect recommendations from all tools
        for tool_name, result in tool_results.items():
            if result.success and result.recommendations:
                # Add tool context to recommendations
                tool_recs = [f"[{tool_name.replace('_', ' ').title()}] {rec}" 
                           for rec in result.recommendations]
                all_recommendations.extend(tool_recs)
        
        # Prioritize recommendations (legal first, then performance, etc.)
        prioritized = []
        legal_recs = [r for r in all_recommendations if 'Legal' in r or 'legal' in r.lower()]
        performance_recs = [r for r in all_recommendations if 'Performance' in r or 'performance' in r.lower()]
        psychology_recs = [r for r in all_recommendations if 'Psychology' in r or 'psychology' in r.lower()]
        brand_recs = [r for r in all_recommendations if 'Brand' in r or 'brand' in r.lower()]
        other_recs = [r for r in all_recommendations if r not in legal_recs + performance_recs + psychology_recs + brand_recs]
        
        prioritized.extend(legal_recs[:3])  # Top 3 legal
        prioritized.extend(performance_recs[:3])  # Top 3 performance
        prioritized.extend(psychology_recs[:2])  # Top 2 psychology
        prioritized.extend(brand_recs[:2])  # Top 2 brand
        prioritized.extend(other_recs[:2])  # Top 2 others
        
        return prioritized
    
    def get_available_flows(self) -> Dict[str, str]:
        """Get list of available flow templates"""
        return {
            flow_id: config.description 
            for flow_id, config in self.flow_templates.items()
        }
    
    def add_flow_template(self, flow_config: FlowConfiguration):
        """Add a new flow template"""
        self.flow_templates[flow_config.flow_id] = flow_config
    
    def get_execution_status(self, execution_id: str) -> Optional[Dict[str, Any]]:
        """Get status of an ongoing execution"""
        return self.active_executions.get(execution_id)


def both_successful(*results: ToolOutput) -> bool:
    """Helper function to check if all results are successful"""
    return all(result.success for result in results)