"""
Metrics Collector for AdCopySurge Tools SDK

This module provides comprehensive metrics collection, monitoring, and observability
for the tools system including performance metrics, usage analytics, and system health.
"""

import time
import asyncio
import threading
from typing import Dict, Any, List, Optional, Union
from collections import defaultdict, deque
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import json
import psutil
import logging
from pathlib import Path


@dataclass
class MetricDataPoint:
    """Individual metric data point"""
    timestamp: float
    value: Union[float, int, str]
    labels: Dict[str, str] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AnalysisMetrics:
    """Metrics for analysis operations"""
    analysis_type: str
    execution_time: float
    success: bool
    overall_score: float
    tools_used: List[str]
    timestamp: float
    request_id: str


@dataclass
class ToolMetrics:
    """Metrics for individual tool execution"""
    tool_name: str
    execution_time: float
    success: bool
    confidence_score: Optional[float]
    error_type: Optional[str]
    timestamp: float
    request_id: str


@dataclass
class SystemMetrics:
    """System performance metrics"""
    cpu_usage_percent: float
    memory_usage_percent: float
    memory_usage_mb: float
    disk_usage_percent: float
    network_io: Dict[str, int]
    timestamp: float


class MetricsCollector:
    """
    Comprehensive metrics collection system for the tools SDK
    
    Features:
    - Real-time performance metrics collection
    - Analysis execution tracking
    - Tool-specific metrics
    - System resource monitoring  
    - Usage analytics and reporting
    - Anomaly detection
    - Metric persistence and retrieval
    """
    
    def __init__(self, 
                 max_data_points: int = 10000,
                 collection_interval: float = 30.0,
                 enable_persistence: bool = True,
                 persistence_path: Optional[str] = None):
        
        self.max_data_points = max_data_points
        self.collection_interval = collection_interval
        self.enable_persistence = enable_persistence
        
        # Set up persistence path
        if persistence_path:
            self.persistence_path = Path(persistence_path)
        else:
            self.persistence_path = Path(__file__).parent.parent / "data" / "metrics"
        
        self.persistence_path.mkdir(parents=True, exist_ok=True)
        
        self.logger = logging.getLogger(__name__)
        
        # Metric storage with time-based rotation
        self.analysis_metrics = deque(maxlen=max_data_points)
        self.tool_metrics = deque(maxlen=max_data_points)
        self.system_metrics = deque(maxlen=max_data_points)
        self.request_metrics = deque(maxlen=max_data_points)
        
        # Real-time counters and aggregations
        self.counters = defaultdict(int)
        self.gauges = defaultdict(float)
        self.histograms = defaultdict(list)
        
        # Analysis type tracking
        self.analysis_type_counts = defaultdict(int)
        self.tool_usage_counts = defaultdict(int)
        self.error_counts = defaultdict(int)
        
        # Performance tracking
        self.response_times = deque(maxlen=1000)  # Last 1000 response times
        self.success_count = 0
        self.total_requests = 0
        
        # Background collection control
        self._collection_task: Optional[asyncio.Task] = None
        self._stop_collection = False
        self._lock = threading.Lock()
        
        # Load persisted metrics on startup
        if enable_persistence:
            self._load_persisted_metrics()
    
    def record_analysis(self, 
                       analysis_type: str,
                       execution_time: float, 
                       success: bool,
                       overall_score: float,
                       tools_used: List[str] = None,
                       request_id: str = None) -> None:
        """Record analysis execution metrics"""
        
        with self._lock:
            # Create analysis metrics record
            metrics = AnalysisMetrics(
                analysis_type=analysis_type,
                execution_time=execution_time,
                success=success,
                overall_score=overall_score,
                tools_used=tools_used or [],
                timestamp=time.time(),
                request_id=request_id or ""
            )
            
            self.analysis_metrics.append(metrics)
            
            # Update counters
            self.counters['total_analyses'] += 1
            self.analysis_type_counts[analysis_type] += 1
            
            if success:
                self.counters['successful_analyses'] += 1
                self.gauges['average_overall_score'] = self._calculate_moving_average(
                    'overall_score', overall_score, 100
                )
            else:
                self.counters['failed_analyses'] += 1
            
            # Update response times
            self.response_times.append(execution_time)
            self.gauges['average_response_time'] = sum(self.response_times) / len(self.response_times)
            
            # Track tool usage
            for tool in tools_used or []:
                self.tool_usage_counts[tool] += 1
        
        self.logger.debug(f"Recorded analysis metrics: {analysis_type}, {execution_time:.2f}s, success: {success}")
    
    def record_tool_execution(self,
                             tool_name: str,
                             execution_time: float,
                             success: bool,
                             confidence_score: Optional[float] = None,
                             error_type: Optional[str] = None,
                             request_id: str = None) -> None:
        """Record individual tool execution metrics"""
        
        with self._lock:
            metrics = ToolMetrics(
                tool_name=tool_name,
                execution_time=execution_time,
                success=success,
                confidence_score=confidence_score,
                error_type=error_type,
                timestamp=time.time(),
                request_id=request_id or ""
            )
            
            self.tool_metrics.append(metrics)
            
            # Update tool-specific counters
            self.counters[f'tool_{tool_name}_executions'] += 1
            
            if success:
                self.counters[f'tool_{tool_name}_successes'] += 1
                if confidence_score is not None:
                    self.gauges[f'tool_{tool_name}_avg_confidence'] = self._calculate_moving_average(
                        f'tool_{tool_name}_confidence', confidence_score, 50
                    )
            else:
                self.counters[f'tool_{tool_name}_failures'] += 1
                if error_type:
                    self.error_counts[f'{tool_name}_{error_type}'] += 1
            
            # Track execution times per tool
            if f'tool_{tool_name}_response_times' not in self.histograms:
                self.histograms[f'tool_{tool_name}_response_times'] = deque(maxlen=500)
            self.histograms[f'tool_{tool_name}_response_times'].append(execution_time)
        
        self.logger.debug(f"Recorded tool metrics: {tool_name}, {execution_time:.2f}s, success: {success}")
    
    def record_request(self,
                      method: str,
                      endpoint: str,
                      status_code: int,
                      execution_time: float,
                      error: Optional[str] = None) -> None:
        """Record HTTP request metrics"""
        
        with self._lock:
            request_metric = {
                'method': method,
                'endpoint': endpoint,
                'status_code': status_code,
                'execution_time': execution_time,
                'error': error,
                'timestamp': time.time()
            }
            
            self.request_metrics.append(request_metric)
            
            # Update request counters
            self.total_requests += 1
            self.counters[f'requests_{method}'] += 1
            self.counters[f'responses_{status_code}'] += 1
            
            if 200 <= status_code < 300:
                self.success_count += 1
            
            # Track response times by endpoint
            endpoint_key = f'endpoint_{endpoint.replace("/", "_")}_response_times'
            if endpoint_key not in self.histograms:
                self.histograms[endpoint_key] = deque(maxlen=200)
            self.histograms[endpoint_key].append(execution_time)
        
        self.logger.debug(f"Recorded request: {method} {endpoint} -> {status_code} in {execution_time:.2f}s")
    
    def record_batch_analysis(self,
                             batch_size: int,
                             execution_time: float,
                             success_count: int,
                             failed_count: int) -> None:
        """Record batch analysis metrics"""
        
        with self._lock:
            self.counters['batch_analyses'] += 1
            self.counters['batch_total_items'] += batch_size
            self.counters['batch_successful_items'] += success_count
            self.counters['batch_failed_items'] += failed_count
            
            self.gauges['average_batch_size'] = self._calculate_moving_average('batch_size', batch_size, 50)
            self.gauges['average_batch_success_rate'] = (success_count / batch_size * 100) if batch_size > 0 else 0
            
            if 'batch_response_times' not in self.histograms:
                self.histograms['batch_response_times'] = deque(maxlen=200)
            self.histograms['batch_response_times'].append(execution_time)
    
    def record_validation_error(self, endpoint: str) -> None:
        """Record validation error"""
        with self._lock:
            self.error_counts[f'validation_error_{endpoint}'] += 1
            self.counters['validation_errors'] += 1
    
    def record_http_error(self, endpoint: str, status_code: int) -> None:
        """Record HTTP error"""
        with self._lock:
            self.error_counts[f'http_error_{endpoint}_{status_code}'] += 1
            self.counters['http_errors'] += 1
    
    def record_general_error(self, endpoint: str, error_type: str) -> None:
        """Record general error"""
        with self._lock:
            self.error_counts[f'general_error_{endpoint}_{error_type}'] += 1
            self.counters['general_errors'] += 1
    
    def get_system_metrics(self) -> Dict[str, Any]:
        """Get current system performance metrics"""
        
        # Get CPU usage
        cpu_percent = psutil.cpu_percent(interval=0.1)
        
        # Get memory usage
        memory = psutil.virtual_memory()
        memory_percent = memory.percent
        memory_mb = memory.used / (1024 * 1024)
        
        # Get disk usage
        disk = psutil.disk_usage('/')
        disk_percent = disk.percent
        
        # Get network I/O
        network_io = psutil.net_io_counters()._asdict()
        
        with self._lock:
            success_rate = (self.success_count / self.total_requests * 100) if self.total_requests > 0 else 100.0
            
            metrics = {
                'cpu_usage_percent': cpu_percent,
                'memory_usage_percent': memory_percent,
                'memory_usage_mb': memory_mb,
                'disk_usage_percent': disk_percent,
                'network_io': network_io,
                'total_requests': self.total_requests,
                'success_rate': success_rate,
                'average_response_time': self.gauges.get('average_response_time', 0.0),
                'cache_hit_rate': self.gauges.get('cache_hit_rate', 0.0),
                'active_connections': len(self.request_metrics),
                'timestamp': time.time()
            }
        
        return metrics
    
    def get_usage_analytics(self, period: str = "7d") -> Dict[str, Any]:
        """Get usage analytics for specified period"""
        
        # Calculate time range
        now = time.time()
        if period == "1h":
            start_time = now - 3600
        elif period == "24h":
            start_time = now - 86400
        elif period == "7d":
            start_time = now - 604800
        elif period == "30d":
            start_time = now - 2592000
        else:
            start_time = now - 604800  # Default to 7 days
        
        with self._lock:
            # Filter metrics by time range
            recent_analyses = [m for m in self.analysis_metrics if m.timestamp >= start_time]
            recent_tools = [m for m in self.tool_metrics if m.timestamp >= start_time]
            
            # Analysis type breakdown
            type_usage = defaultdict(int)
            for analysis in recent_analyses:
                type_usage[analysis.analysis_type] += 1
            
            # Tool usage breakdown
            tool_usage_stats = defaultdict(lambda: {
                'total_executions': 0,
                'successful_executions': 0,
                'average_execution_time': 0.0,
                'average_confidence': 0.0,
                'confidence_scores': []
            })
            
            for tool_metric in recent_tools:
                stats = tool_usage_stats[tool_metric.tool_name]
                stats['total_executions'] += 1
                
                if tool_metric.success:
                    stats['successful_executions'] += 1
                
                if tool_metric.confidence_score is not None:
                    stats['confidence_scores'].append(tool_metric.confidence_score)
            
            # Calculate averages for tools
            for tool_name, stats in tool_usage_stats.items():
                if stats['total_executions'] > 0:
                    stats['success_rate'] = (stats['successful_executions'] / stats['total_executions']) * 100
                else:
                    stats['success_rate'] = 0.0
                
                if stats['confidence_scores']:
                    stats['average_confidence'] = sum(stats['confidence_scores']) / len(stats['confidence_scores'])
                else:
                    stats['average_confidence'] = 0.0
                
                # Clean up temporary data
                del stats['confidence_scores']
                del stats['successful_executions']
            
            # Performance metrics
            recent_scores = [a.overall_score for a in recent_analyses if a.success]
            avg_score = sum(recent_scores) / len(recent_scores) if recent_scores else 0.0
            
            score_distribution = defaultdict(int)
            for score in recent_scores:
                if score >= 90:
                    score_distribution['excellent'] += 1
                elif score >= 75:
                    score_distribution['good'] += 1
                elif score >= 60:
                    score_distribution['average'] += 1
                elif score >= 40:
                    score_distribution['poor'] += 1
                else:
                    score_distribution['critical'] += 1
        
        return {
            'period': period,
            'total_analyses': len(recent_analyses),
            'analysis_type_usage': dict(type_usage),
            'tool_usage_stats': dict(tool_usage_stats),
            'performance_metrics': {
                'average_overall_score': avg_score,
                'score_distribution': dict(score_distribution),
                'total_successful': len(recent_scores),
                'success_rate': (len(recent_scores) / len(recent_analyses) * 100) if recent_analyses else 100.0
            },
            'time_range': {
                'start': start_time,
                'end': now
            }
        }
    
    def get_performance_analytics(self, period: str = "7d") -> Dict[str, Any]:
        """Get performance analytics for specified period"""
        
        analytics = self.get_usage_analytics(period)
        
        with self._lock:
            # Add detailed performance metrics
            response_time_percentiles = self._calculate_percentiles(list(self.response_times))
            
            # Tool performance breakdown
            tool_performance = {}
            for tool_name in self.tool_usage_counts.keys():
                tool_times = self.histograms.get(f'tool_{tool_name}_response_times', [])
                if tool_times:
                    tool_performance[tool_name] = {
                        'average_response_time': sum(tool_times) / len(tool_times),
                        'percentiles': self._calculate_percentiles(list(tool_times)),
                        'total_executions': len(tool_times)
                    }
            
            # Error analysis
            error_summary = {
                'total_errors': sum(self.error_counts.values()),
                'error_types': dict(self.error_counts),
                'error_rate': (sum(self.error_counts.values()) / max(self.total_requests, 1)) * 100
            }
        
        analytics['detailed_performance'] = {
            'response_time_percentiles': response_time_percentiles,
            'tool_performance': tool_performance,
            'error_analysis': error_summary
        }
        
        return analytics
    
    def get_detailed_metrics(self) -> Dict[str, Any]:
        """Get comprehensive system metrics"""
        
        system_metrics = self.get_system_metrics()
        usage_analytics = self.get_usage_analytics("24h")
        
        with self._lock:
            detailed_metrics = {
                'system': system_metrics,
                'usage': usage_analytics,
                'counters': dict(self.counters),
                'gauges': dict(self.gauges),
                'tool_usage_counts': dict(self.tool_usage_counts),
                'analysis_type_counts': dict(self.analysis_type_counts),
                'error_counts': dict(self.error_counts),
                'data_points': {
                    'analysis_metrics': len(self.analysis_metrics),
                    'tool_metrics': len(self.tool_metrics),
                    'request_metrics': len(self.request_metrics)
                }
            }
        
        return detailed_metrics
    
    def start_background_collection(self) -> None:
        """Start background metrics collection"""
        if self._collection_task is None:
            self._stop_collection = False
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            self._collection_task = loop.create_task(self._background_collection_loop())
            
            # Start the loop in a separate thread
            collection_thread = threading.Thread(target=loop.run_forever, daemon=True)
            collection_thread.start()
            
            self.logger.info("Started background metrics collection")
    
    def stop_background_collection(self) -> None:
        """Stop background metrics collection"""
        self._stop_collection = True
        if self._collection_task:
            self._collection_task.cancel()
            self._collection_task = None
        
        if self.enable_persistence:
            self._persist_metrics()
        
        self.logger.info("Stopped background metrics collection")
    
    async def _background_collection_loop(self) -> None:
        """Background loop for collecting system metrics"""
        while not self._stop_collection:
            try:
                # Collect system metrics
                system_metrics = SystemMetrics(
                    cpu_usage_percent=psutil.cpu_percent(interval=0.1),
                    memory_usage_percent=psutil.virtual_memory().percent,
                    memory_usage_mb=psutil.virtual_memory().used / (1024 * 1024),
                    disk_usage_percent=psutil.disk_usage('/').percent,
                    network_io=psutil.net_io_counters()._asdict(),
                    timestamp=time.time()
                )
                
                with self._lock:
                    self.system_metrics.append(system_metrics)
                
                # Persist metrics periodically
                if self.enable_persistence and len(self.analysis_metrics) % 100 == 0:
                    self._persist_metrics()
                
                await asyncio.sleep(self.collection_interval)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Error in background collection: {str(e)}")
                await asyncio.sleep(5)  # Wait before retrying
    
    def _calculate_moving_average(self, key: str, new_value: float, window_size: int) -> float:
        """Calculate moving average for a metric"""
        if f'{key}_values' not in self.histograms:
            self.histograms[f'{key}_values'] = deque(maxlen=window_size)
        
        self.histograms[f'{key}_values'].append(new_value)
        values = list(self.histograms[f'{key}_values'])
        
        return sum(values) / len(values)
    
    def _calculate_percentiles(self, values: List[float]) -> Dict[str, float]:
        """Calculate percentiles for a list of values"""
        if not values:
            return {}
        
        sorted_values = sorted(values)
        n = len(sorted_values)
        
        return {
            'p50': sorted_values[int(n * 0.5)],
            'p75': sorted_values[int(n * 0.75)],
            'p90': sorted_values[int(n * 0.9)],
            'p95': sorted_values[int(n * 0.95)],
            'p99': sorted_values[int(n * 0.99)],
            'min': min(sorted_values),
            'max': max(sorted_values),
            'count': n
        }
    
    def _persist_metrics(self) -> None:
        """Persist metrics to disk"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            # Prepare metrics for persistence
            metrics_data = {
                'timestamp': timestamp,
                'analysis_metrics': [
                    {
                        'analysis_type': m.analysis_type,
                        'execution_time': m.execution_time,
                        'success': m.success,
                        'overall_score': m.overall_score,
                        'tools_used': m.tools_used,
                        'timestamp': m.timestamp,
                        'request_id': m.request_id
                    }
                    for m in list(self.analysis_metrics)
                ],
                'counters': dict(self.counters),
                'gauges': dict(self.gauges),
                'tool_usage_counts': dict(self.tool_usage_counts),
                'analysis_type_counts': dict(self.analysis_type_counts),
                'error_counts': dict(self.error_counts)
            }
            
            # Write to file
            metrics_file = self.persistence_path / f"metrics_{timestamp}.json"
            with open(metrics_file, 'w', encoding='utf-8') as f:
                json.dump(metrics_data, f, indent=2, ensure_ascii=False)
            
            # Keep only last 10 metric files
            metric_files = sorted(self.persistence_path.glob("metrics_*.json"))
            if len(metric_files) > 10:
                for old_file in metric_files[:-10]:
                    old_file.unlink()
                    
            self.logger.debug(f"Persisted metrics to {metrics_file}")
            
        except Exception as e:
            self.logger.error(f"Failed to persist metrics: {str(e)}")
    
    def _load_persisted_metrics(self) -> None:
        """Load persisted metrics from disk"""
        try:
            # Find the most recent metrics file
            metric_files = sorted(self.persistence_path.glob("metrics_*.json"))
            if not metric_files:
                return
            
            latest_file = metric_files[-1]
            
            with open(latest_file, 'r', encoding='utf-8') as f:
                metrics_data = json.load(f)
            
            # Restore counters and aggregations
            self.counters.update(metrics_data.get('counters', {}))
            self.gauges.update(metrics_data.get('gauges', {}))
            self.tool_usage_counts.update(metrics_data.get('tool_usage_counts', {}))
            self.analysis_type_counts.update(metrics_data.get('analysis_type_counts', {}))
            self.error_counts.update(metrics_data.get('error_counts', {}))
            
            # Restore recent analysis metrics
            analysis_data = metrics_data.get('analysis_metrics', [])
            for data in analysis_data[-1000:]:  # Load last 1000 records
                metrics = AnalysisMetrics(**data)
                self.analysis_metrics.append(metrics)
            
            self.logger.info(f"Loaded persisted metrics from {latest_file}")
            
        except Exception as e:
            self.logger.warning(f"Failed to load persisted metrics: {str(e)}")
    
    def export_metrics(self, output_file: str, format: str = "json") -> None:
        """Export metrics to file in specified format"""
        try:
            metrics_data = self.get_detailed_metrics()
            
            if format.lower() == "json":
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(metrics_data, f, indent=2, ensure_ascii=False, default=str)
            elif format.lower() == "csv":
                import csv
                with open(output_file, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    # Write analysis metrics as CSV
                    writer.writerow(['timestamp', 'analysis_type', 'execution_time', 'success', 'overall_score'])
                    for metrics in self.analysis_metrics:
                        writer.writerow([
                            metrics.timestamp, metrics.analysis_type, 
                            metrics.execution_time, metrics.success, metrics.overall_score
                        ])
            
            self.logger.info(f"Exported metrics to {output_file}")
            
        except Exception as e:
            self.logger.error(f"Failed to export metrics: {str(e)}")


# Export the main class
__all__ = [
    'MetricsCollector',
    'MetricDataPoint', 
    'AnalysisMetrics',
    'ToolMetrics', 
    'SystemMetrics'
]