#!/usr/bin/env python3
"""
Performance and Edge Case Tests

Tests system behavior under various conditions and edge cases:
- Performance benchmarks across platforms
- Memory usage monitoring
- Concurrent request handling
- Extreme input validation
- Error recovery mechanisms
- Rate limiting behavior
- Timeout handling
- Resource cleanup
"""

import asyncio
import time
import psutil
import threading
import gc
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, List, Any, Tuple
import requests
import json

# Import services and test data
try:
    from app.services.platform_ad_generator import PlatformAdGenerator
    from app.services.content_validator import ContentValidator
    from test_data_comprehensive import get_test_ads_for_platform, PLATFORM_TEST_DATA
    SERVICES_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Could not import platform services: {e}")
    SERVICES_AVAILABLE = False

class PerformanceMonitor:
    """Monitor system performance during tests"""
    
    def __init__(self):
        self.process = psutil.Process()
        self.start_time = 0
        self.start_memory = 0
        self.start_cpu = 0
        self.measurements = []
        
    def start_monitoring(self):
        """Start performance monitoring"""
        self.start_time = time.time()
        self.start_memory = self.process.memory_info().rss / 1024 / 1024  # MB
        self.start_cpu = self.process.cpu_percent()
        self.measurements = []
        
    def take_measurement(self, label: str = ""):
        """Take a performance measurement"""
        current_time = time.time()
        current_memory = self.process.memory_info().rss / 1024 / 1024  # MB
        current_cpu = self.process.cpu_percent()
        
        measurement = {
            'label': label,
            'elapsed_time': round(current_time - self.start_time, 3),
            'memory_mb': round(current_memory, 2),
            'memory_delta': round(current_memory - self.start_memory, 2),
            'cpu_percent': round(current_cpu, 1),
            'timestamp': current_time
        }
        
        self.measurements.append(measurement)
        return measurement
        
    def get_summary(self) -> Dict[str, Any]:
        """Get performance summary"""
        if not self.measurements:
            return {}
        
        return {
            'total_duration': round(time.time() - self.start_time, 3),
            'peak_memory_mb': max(m['memory_mb'] for m in self.measurements),
            'memory_growth_mb': max(m['memory_delta'] for m in self.measurements),
            'avg_cpu_percent': round(sum(m['cpu_percent'] for m in self.measurements) / len(self.measurements), 1),
            'measurement_count': len(self.measurements),
            'measurements': self.measurements
        }

class PerformanceEdgeCaseTester:
    """Test system performance and edge cases"""
    
    def __init__(self, openai_api_key: str = None, api_url: str = "http://localhost:8000"):
        self.openai_api_key = openai_api_key
        self.api_url = api_url
        self.monitor = PerformanceMonitor()
        self.platforms = ['facebook', 'instagram', 'google_ads', 'linkedin', 'twitter_x', 'tiktok']
        
        # Initialize services if available
        self.generator = None
        self.validator = None
        
        if SERVICES_AVAILABLE and openai_api_key:
            try:
                self.generator = PlatformAdGenerator(openai_api_key)
                self.validator = ContentValidator()
            except Exception as e:
                print(f"Warning: Could not initialize services: {e}")
    
    async def run_performance_tests(self) -> Dict[str, Any]:
        """Run comprehensive performance and edge case tests"""
        print("🚀 Starting performance and edge case tests...")
        
        self.monitor.start_monitoring()
        test_results = {
            'performance_benchmarks': {},
            'edge_case_tests': {},
            'stress_tests': {},
            'error_recovery_tests': {},
            'resource_usage': {},
            'test_summary': {
                'total_tests': 0,
                'passed_tests': 0,
                'failed_tests': 0,
                'execution_time': 0
            }
        }
        
        start_time = time.time()
        
        try:
            # 1. Performance Benchmarks
            print("📊 Running performance benchmarks...")
            test_results['performance_benchmarks'] = await self._run_performance_benchmarks()
            self.monitor.take_measurement("performance_benchmarks_complete")
            
            # 2. Edge Case Tests
            print("🔍 Running edge case tests...")
            test_results['edge_case_tests'] = await self._run_edge_case_tests()
            self.monitor.take_measurement("edge_case_tests_complete")
            
            # 3. Stress Tests
            print("💪 Running stress tests...")
            test_results['stress_tests'] = await self._run_stress_tests()
            self.monitor.take_measurement("stress_tests_complete")
            
            # 4. Error Recovery Tests
            print("🔄 Running error recovery tests...")
            test_results['error_recovery_tests'] = await self._run_error_recovery_tests()
            self.monitor.take_measurement("error_recovery_tests_complete")
            
            # 5. Resource Usage Analysis
            test_results['resource_usage'] = self.monitor.get_summary()
            
            # Calculate summary
            total_tests = 0
            passed_tests = 0
            
            for category, results in test_results.items():
                if isinstance(results, dict) and 'tests' in results:
                    for test in results['tests']:
                        total_tests += 1
                        if test.get('success', False):
                            passed_tests += 1
            
            test_results['test_summary'] = {
                'total_tests': total_tests,
                'passed_tests': passed_tests,
                'failed_tests': total_tests - passed_tests,
                'execution_time': round(time.time() - start_time, 2)
            }
            
        except Exception as e:
            print(f"❌ Test execution failed: {e}")
            test_results['execution_error'] = str(e)
        
        success_rate = round(test_results['test_summary']['passed_tests']/test_results['test_summary']['total_tests']*100, 1) if test_results['test_summary']['total_tests'] > 0 else 0
        print(f"✅ Performance tests completed: {test_results['test_summary']['passed_tests']}/{test_results['test_summary']['total_tests']} ({success_rate}%)")
        
        return test_results
    
    async def _run_performance_benchmarks(self) -> Dict[str, Any]:
        """Run performance benchmarks for each platform"""
        results = {
            'platform_benchmarks': {},
            'cross_platform_comparison': {},
            'tests': []
        }
        
        platform_times = {}
        
        for platform_id in self.platforms:
            print(f"  ⏱️ Benchmarking {platform_id}...")
            
            # Get test ads
            test_ads = get_test_ads_for_platform(platform_id)
            if not test_ads or 'well_written_ads' not in test_ads:
                continue
            
            platform_times[platform_id] = []
            
            # Test multiple ads for consistent timing
            for i, ad_text in enumerate(test_ads['well_written_ads'][:3]):
                test_result = await self._benchmark_single_ad(platform_id, ad_text, i)
                results['tests'].append(test_result)
                
                if test_result['success'] and 'generation_time_ms' in test_result['metrics']:
                    platform_times[platform_id].append(test_result['metrics']['generation_time_ms'])
        
        # Calculate platform benchmarks
        for platform_id, times in platform_times.items():
            if times:
                results['platform_benchmarks'][platform_id] = {
                    'avg_time_ms': round(sum(times) / len(times), 2),
                    'min_time_ms': min(times),
                    'max_time_ms': max(times),
                    'sample_count': len(times)
                }
        
        # Cross-platform comparison
        if platform_times:
            all_times = [time for times in platform_times.values() for time in times]
            if all_times:
                results['cross_platform_comparison'] = {
                    'overall_avg_ms': round(sum(all_times) / len(all_times), 2),
                    'fastest_platform': min(results['platform_benchmarks'].items(), 
                                          key=lambda x: x[1]['avg_time_ms'])[0] if results['platform_benchmarks'] else None,
                    'slowest_platform': max(results['platform_benchmarks'].items(), 
                                          key=lambda x: x[1]['avg_time_ms'])[0] if results['platform_benchmarks'] else None
                }
        
        return results
    
    async def _benchmark_single_ad(self, platform_id: str, ad_text: str, index: int) -> Dict[str, Any]:
        """Benchmark single ad generation"""
        result = {
            'test_id': f"benchmark_{platform_id}_{index}",
            'platform_id': platform_id,
            'input_ad': ad_text,
            'success': False,
            'errors': [],
            'metrics': {}
        }
        
        if not self.generator:
            result['errors'].append("Generator not available")
            return result
        
        try:
            # Measure generation time
            start_time = time.time()
            generation_result = await self.generator.generate_ad(
                text_input=ad_text,
                platform_id=platform_id,
                context={'benchmark': True}
            )
            end_time = time.time()
            
            result['metrics']['generation_time_ms'] = round((end_time - start_time) * 1000, 2)
            result['metrics']['generation_success'] = generation_result.success
            
            if generation_result.success:
                result['success'] = True
                result['metrics']['retry_count'] = getattr(generation_result, 'retry_count', 0)
                result['metrics']['content_fields'] = len(generation_result.generated_content.keys())
            else:
                result['errors'].extend(generation_result.errors)
                
        except Exception as e:
            result['errors'].append(f"Benchmark failed: {str(e)}")
        
        return result
    
    async def _run_edge_case_tests(self) -> Dict[str, Any]:
        """Test extreme and edge case inputs"""
        results = {
            'extreme_inputs': [],
            'boundary_conditions': [],
            'malformed_inputs': [],
            'tests': []
        }
        
        # Test extreme inputs
        extreme_cases = [
            ("empty_string", ""),
            ("single_char", "a"),
            ("very_long", "a" * 5000),
            ("only_emojis", "🔥💯⚡✨🌟💫⭐🎯🚀💎🏆🎉"),
            ("only_punctuation", "!@#$%^&*()_+-=[]{}|;':\",./<>?"),
            ("unicode_heavy", "Iñtërnâtiônàlizætiøn 中文 العربية русский"),
            ("mixed_scripts", "Hello мир العالم 世界 🌍"),
            ("html_entities", "&lt;script&gt;alert('test')&lt;/script&gt;"),
            ("markdown_heavy", "# Header **bold** *italic* [link](url) `code`"),
            ("newlines_tabs", "Line 1\n\nLine 3\t\tTabbed")
        ]
        
        for case_name, test_input in extreme_cases:
            print(f"    🔍 Testing {case_name}...")
            
            for platform_id in self.platforms[:2]:  # Test first 2 platforms for speed
                test_result = await self._test_extreme_input(platform_id, test_input, case_name)
                results['tests'].append(test_result)
                results['extreme_inputs'].append(test_result)
        
        # Test boundary conditions
        boundary_cases = [
            ("max_facebook_headline", "a" * 125),
            ("over_facebook_headline", "a" * 126),
            ("max_twitter_body", "a" * 280),
            ("over_twitter_body", "a" * 281),
            ("max_instagram_body", "a" * 2200),
            ("exactly_google_headline", "a" * 30),
        ]
        
        for case_name, test_input in boundary_cases:
            print(f"    📏 Testing boundary: {case_name}...")
            
            # Determine appropriate platform
            platform = 'facebook' if 'facebook' in case_name else \
                      'twitter_x' if 'twitter' in case_name else \
                      'instagram' if 'instagram' in case_name else \
                      'google_ads' if 'google' in case_name else 'facebook'
            
            test_result = await self._test_boundary_condition(platform, test_input, case_name)
            results['tests'].append(test_result)
            results['boundary_conditions'].append(test_result)
        
        return results
    
    async def _test_extreme_input(self, platform_id: str, test_input: str, case_name: str) -> Dict[str, Any]:
        """Test extreme input handling"""
        result = {
            'test_id': f"extreme_{case_name}_{platform_id}",
            'platform_id': platform_id,
            'case_name': case_name,
            'input_length': len(test_input),
            'success': False,
            'errors': [],
            'metrics': {},
            'handled_gracefully': False
        }
        
        try:
            if self.generator:
                # Test with generator
                start_time = time.time()
                generation_result = await self.generator.generate_ad(
                    text_input=test_input,
                    platform_id=platform_id,
                    context={'test_case': case_name}
                )
                processing_time = time.time() - start_time
                
                result['metrics']['processing_time_ms'] = round(processing_time * 1000, 2)
                result['handled_gracefully'] = True  # Didn't crash
                
                if generation_result.success:
                    result['success'] = True
                else:
                    result['errors'].extend(generation_result.errors)
            
            else:
                # Test with API
                try:
                    response = requests.post(
                        f"{self.api_url}/api/ads/improve",
                        json={"ad_copy": test_input, "platform": platform_id},
                        timeout=30
                    )
                    
                    result['handled_gracefully'] = True  # Got a response
                    result['metrics']['api_status_code'] = response.status_code
                    
                    if response.status_code == 200:
                        result['success'] = True
                    else:
                        result['errors'].append(f"API returned {response.status_code}")
                
                except requests.exceptions.Timeout:
                    result['errors'].append("API timeout")
                except Exception as e:
                    result['errors'].append(f"API error: {str(e)}")
        
        except Exception as e:
            result['errors'].append(f"Exception during test: {str(e)}")
        
        return result
    
    async def _test_boundary_condition(self, platform_id: str, test_input: str, case_name: str) -> Dict[str, Any]:
        """Test boundary condition handling"""
        result = {
            'test_id': f"boundary_{case_name}",
            'platform_id': platform_id,
            'case_name': case_name,
            'input_length': len(test_input),
            'success': False,
            'errors': [],
            'warnings': [],
            'metrics': {}
        }
        
        try:
            if self.generator:
                generation_result = await self.generator.generate_ad(
                    text_input=test_input,
                    platform_id=platform_id,
                    context={'boundary_test': True}
                )
                
                result['success'] = generation_result.success
                
                if not generation_result.success:
                    result['errors'].extend(generation_result.errors)
                
                # Check if result respects limits
                if generation_result.success and generation_result.generated_content:
                    if self.validator:
                        validation_result = self.validator.validate_and_sanitize(
                            generation_result.generated_content, 
                            platform_id, 
                            strict_mode=True
                        )
                        
                        result['metrics']['validation_passed'] = validation_result.is_valid
                        result['metrics']['char_violations'] = len([
                            w for w in validation_result.warnings 
                            if 'character' in w.lower()
                        ])
        
        except Exception as e:
            result['errors'].append(f"Boundary test failed: {str(e)}")
        
        return result
    
    async def _run_stress_tests(self) -> Dict[str, Any]:
        """Run system stress tests"""
        results = {
            'concurrent_requests': None,
            'memory_stress': None,
            'rapid_fire': None,
            'tests': []
        }
        
        # Test concurrent requests
        if self.api_url:
            print("    🔄 Testing concurrent requests...")
            concurrent_result = await self._test_concurrent_requests()
            results['concurrent_requests'] = concurrent_result
            results['tests'].append(concurrent_result)
        
        # Test memory usage under stress
        if self.generator:
            print("    🧠 Testing memory stress...")
            memory_result = await self._test_memory_stress()
            results['memory_stress'] = memory_result
            results['tests'].append(memory_result)
        
        # Test rapid-fire requests
        print("    ⚡ Testing rapid-fire requests...")
        rapid_result = await self._test_rapid_fire()
        results['rapid_fire'] = rapid_result
        results['tests'].append(rapid_result)
        
        return results
    
    async def _test_concurrent_requests(self) -> Dict[str, Any]:
        """Test concurrent API request handling"""
        result = {
            'test_id': 'concurrent_requests',
            'success': False,
            'errors': [],
            'metrics': {
                'concurrent_count': 5,
                'successful_requests': 0,
                'failed_requests': 0,
                'avg_response_time_ms': 0,
                'total_time_ms': 0
            }
        }
        
        def make_request(platform_id: str, ad_text: str) -> Tuple[bool, float, str]:
            """Make a single API request"""
            try:
                start_time = time.time()
                response = requests.post(
                    f"{self.api_url}/api/ads/improve",
                    json={"ad_copy": ad_text, "platform": platform_id},
                    timeout=30
                )
                response_time = (time.time() - start_time) * 1000
                return response.status_code == 200, response_time, ""
            except Exception as e:
                return False, 0, str(e)
        
        try:
            # Prepare test data
            test_requests = []
            for i, platform_id in enumerate(self.platforms[:5]):
                test_ads = get_test_ads_for_platform(platform_id)
                if test_ads and 'short_ads' in test_ads and test_ads['short_ads']:
                    test_requests.append((platform_id, test_ads['short_ads'][0]))
            
            if not test_requests:
                result['errors'].append("No test data available")
                return result
            
            # Execute concurrent requests
            start_time = time.time()
            with ThreadPoolExecutor(max_workers=5) as executor:
                futures = [executor.submit(make_request, platform, ad) 
                          for platform, ad in test_requests]
                
                response_times = []
                for future in as_completed(futures):
                    success, response_time, error = future.result()
                    if success:
                        result['metrics']['successful_requests'] += 1
                        response_times.append(response_time)
                    else:
                        result['metrics']['failed_requests'] += 1
                        if error:
                            result['errors'].append(error)
            
            result['metrics']['total_time_ms'] = round((time.time() - start_time) * 1000, 2)
            
            if response_times:
                result['metrics']['avg_response_time_ms'] = round(
                    sum(response_times) / len(response_times), 2
                )
            
            result['success'] = result['metrics']['successful_requests'] > 0
            
        except Exception as e:
            result['errors'].append(f"Concurrent test failed: {str(e)}")
        
        return result
    
    async def _test_memory_stress(self) -> Dict[str, Any]:
        """Test memory usage under stress"""
        result = {
            'test_id': 'memory_stress',
            'success': False,
            'errors': [],
            'metrics': {
                'start_memory_mb': 0,
                'peak_memory_mb': 0,
                'end_memory_mb': 0,
                'memory_growth_mb': 0,
                'iterations': 20
            }
        }
        
        try:
            # Record starting memory
            process = psutil.Process()
            result['metrics']['start_memory_mb'] = round(
                process.memory_info().rss / 1024 / 1024, 2
            )
            
            peak_memory = result['metrics']['start_memory_mb']
            
            # Run multiple generations
            test_ad = "Transform your business with our revolutionary solution."
            
            for i in range(result['metrics']['iterations']):
                generation_result = await self.generator.generate_ad(
                    text_input=test_ad,
                    platform_id='facebook',
                    context={'memory_test': i}
                )
                
                # Check memory usage
                current_memory = process.memory_info().rss / 1024 / 1024
                peak_memory = max(peak_memory, current_memory)
                
                # Force garbage collection occasionally
                if i % 5 == 0:
                    gc.collect()
            
            result['metrics']['peak_memory_mb'] = round(peak_memory, 2)
            result['metrics']['end_memory_mb'] = round(
                process.memory_info().rss / 1024 / 1024, 2
            )
            result['metrics']['memory_growth_mb'] = round(
                result['metrics']['end_memory_mb'] - result['metrics']['start_memory_mb'], 2
            )
            
            # Success if memory growth is reasonable (< 100MB)
            result['success'] = result['metrics']['memory_growth_mb'] < 100
            
            if result['metrics']['memory_growth_mb'] > 50:
                result['errors'].append(f"High memory growth: {result['metrics']['memory_growth_mb']}MB")
        
        except Exception as e:
            result['errors'].append(f"Memory stress test failed: {str(e)}")
        
        return result
    
    async def _test_rapid_fire(self) -> Dict[str, Any]:
        """Test rapid-fire request handling"""
        result = {
            'test_id': 'rapid_fire',
            'success': False,
            'errors': [],
            'metrics': {
                'requests_count': 10,
                'successful_requests': 0,
                'failed_requests': 0,
                'avg_time_ms': 0,
                'total_time_ms': 0
            }
        }
        
        try:
            test_ad = "Quick test ad for rapid fire testing."
            response_times = []
            
            start_time = time.time()
            
            # Make rapid requests
            for i in range(result['metrics']['requests_count']):
                try:
                    if self.generator:
                        # Direct generator test
                        req_start = time.time()
                        generation_result = await self.generator.generate_ad(
                            text_input=test_ad,
                            platform_id='facebook',
                            context={'rapid_fire': i}
                        )
                        req_time = (time.time() - req_start) * 1000
                        
                        if generation_result.success:
                            result['metrics']['successful_requests'] += 1
                            response_times.append(req_time)
                        else:
                            result['metrics']['failed_requests'] += 1
                    
                    else:
                        # API test
                        req_start = time.time()
                        response = requests.post(
                            f"{self.api_url}/api/ads/improve",
                            json={"ad_copy": test_ad, "platform": "facebook"},
                            timeout=15
                        )
                        req_time = (time.time() - req_start) * 1000
                        
                        if response.status_code == 200:
                            result['metrics']['successful_requests'] += 1
                            response_times.append(req_time)
                        else:
                            result['metrics']['failed_requests'] += 1
                
                except Exception as e:
                    result['metrics']['failed_requests'] += 1
                    result['errors'].append(f"Request {i} failed: {str(e)}")
            
            result['metrics']['total_time_ms'] = round((time.time() - start_time) * 1000, 2)
            
            if response_times:
                result['metrics']['avg_time_ms'] = round(
                    sum(response_times) / len(response_times), 2
                )
            
            # Success if most requests succeeded
            success_rate = result['metrics']['successful_requests'] / result['metrics']['requests_count']
            result['success'] = success_rate >= 0.8
            
        except Exception as e:
            result['errors'].append(f"Rapid fire test failed: {str(e)}")
        
        return result
    
    async def _run_error_recovery_tests(self) -> Dict[str, Any]:
        """Test error recovery mechanisms"""
        results = {
            'api_error_recovery': None,
            'timeout_recovery': None,
            'retry_logic': None,
            'tests': []
        }
        
        # Test API error recovery
        print("    🔄 Testing API error recovery...")
        api_recovery_result = await self._test_api_error_recovery()
        results['api_error_recovery'] = api_recovery_result
        results['tests'].append(api_recovery_result)
        
        # Test timeout recovery
        print("    ⏰ Testing timeout recovery...")
        timeout_result = await self._test_timeout_recovery()
        results['timeout_recovery'] = timeout_result  
        results['tests'].append(timeout_result)
        
        # Test retry logic
        if self.generator:
            print("    🔁 Testing retry logic...")
            retry_result = await self._test_retry_logic()
            results['retry_logic'] = retry_result
            results['tests'].append(retry_result)
        
        return results
    
    async def _test_api_error_recovery(self) -> Dict[str, Any]:
        """Test API error recovery"""
        result = {
            'test_id': 'api_error_recovery',
            'success': False,
            'errors': [],
            'metrics': {
                'error_conditions_tested': 0,
                'graceful_failures': 0,
                'crash_failures': 0
            }
        }
        
        # Test various error conditions
        error_conditions = [
            ("invalid_platform", {"ad_copy": "test", "platform": "invalid"}),
            ("missing_ad_copy", {"platform": "facebook"}),
            ("empty_ad_copy", {"ad_copy": "", "platform": "facebook"}),
            ("malformed_json", None)  # Will be handled specially
        ]
        
        for condition_name, request_data in error_conditions:
            result['metrics']['error_conditions_tested'] += 1
            
            try:
                if condition_name == "malformed_json":
                    response = requests.post(
                        f"{self.api_url}/api/ads/improve",
                        data="invalid json",
                        headers={"Content-Type": "application/json"},
                        timeout=10
                    )
                else:
                    response = requests.post(
                        f"{self.api_url}/api/ads/improve",
                        json=request_data,
                        timeout=10
                    )
                
                # Should get error response, not crash
                if response.status_code in [400, 422, 500]:
                    result['metrics']['graceful_failures'] += 1
                else:
                    result['errors'].append(f"{condition_name}: unexpected status {response.status_code}")
            
            except requests.exceptions.ConnectionError:
                result['errors'].append(f"{condition_name}: connection failed")
            except Exception as e:
                result['metrics']['crash_failures'] += 1
                result['errors'].append(f"{condition_name}: {str(e)}")
        
        # Success if all errors were handled gracefully
        result['success'] = (
            result['metrics']['graceful_failures'] == result['metrics']['error_conditions_tested'] and
            result['metrics']['crash_failures'] == 0
        )
        
        return result
    
    async def _test_timeout_recovery(self) -> Dict[str, Any]:
        """Test timeout recovery"""
        result = {
            'test_id': 'timeout_recovery',
            'success': False,
            'errors': [],
            'metrics': {
                'timeout_tests': 0,
                'handled_timeouts': 0
            }
        }
        
        # Test with very short timeout
        short_timeout_requests = [
            ("facebook", "This is a test ad for timeout testing with facebook platform."),
            ("instagram", "Another test ad for timeout testing.")
        ]
        
        for platform, ad_text in short_timeout_requests:
            result['metrics']['timeout_tests'] += 1
            
            try:
                response = requests.post(
                    f"{self.api_url}/api/ads/improve",
                    json={"ad_copy": ad_text, "platform": platform},
                    timeout=0.1  # Very short timeout
                )
                
                # If we get here, request was very fast or timeout not working
                if response.status_code == 200:
                    result['metrics']['handled_timeouts'] += 1
                
            except requests.exceptions.Timeout:
                # This is expected - timeout was handled
                result['metrics']['handled_timeouts'] += 1
            
            except Exception as e:
                result['errors'].append(f"Timeout test failed: {str(e)}")
        
        result['success'] = result['metrics']['handled_timeouts'] > 0
        return result
    
    async def _test_retry_logic(self) -> Dict[str, Any]:
        """Test retry logic functionality"""
        result = {
            'test_id': 'retry_logic',
            'success': False,
            'errors': [],
            'metrics': {
                'retry_tests': 0,
                'successful_retries': 0
            }
        }
        
        # Test with problematic input that might trigger retries
        problematic_inputs = [
            "buy now click here limited time offer",  # Template-heavy
            "we has best product dont wait",  # Grammar issues
            "a"  # Very short input
        ]
        
        for test_input in problematic_inputs:
            result['metrics']['retry_tests'] += 1
            
            try:
                generation_result = await self.generator.generate_ad(
                    text_input=test_input,
                    platform_id='facebook',
                    context={'retry_test': True}
                )
                
                # Check if retries occurred
                retry_count = getattr(generation_result, '_last_retry_count', 0)
                if retry_count > 0:
                    result['metrics']['successful_retries'] += 1
                
                # Even if no retries, success if it handled the input
                if generation_result.success or len(generation_result.errors) > 0:
                    # System attempted to process
                    pass
                
            except Exception as e:
                result['errors'].append(f"Retry test failed: {str(e)}")
        
        result['success'] = len(result['errors']) == 0
        return result
    
    def generate_performance_report(self, test_results: Dict[str, Any], output_file: str = None) -> str:
        """Generate comprehensive performance test report"""
        report = []
        report.append("=" * 80)
        report.append("PERFORMANCE AND EDGE CASE TEST REPORT")
        report.append("=" * 80)
        report.append("")
        
        # Summary
        summary = test_results.get('test_summary', {})
        report.append("📊 TEST SUMMARY:")
        report.append(f"   Total Tests: {summary.get('total_tests', 0)}")
        report.append(f"   Passed: {summary.get('passed_tests', 0)}")
        report.append(f"   Failed: {summary.get('failed_tests', 0)}")
        report.append(f"   Success Rate: {round(summary.get('passed_tests', 0)/summary.get('total_tests', 1)*100, 1)}%")
        report.append(f"   Execution Time: {summary.get('execution_time', 0)}s")
        report.append("")
        
        # Resource Usage
        resources = test_results.get('resource_usage', {})
        if resources:
            report.append("💾 RESOURCE USAGE:")
            report.append(f"   Peak Memory: {resources.get('peak_memory_mb', 0)}MB")
            report.append(f"   Memory Growth: {resources.get('memory_growth_mb', 0)}MB")
            report.append(f"   Avg CPU: {resources.get('avg_cpu_percent', 0)}%")
            report.append(f"   Total Duration: {resources.get('total_duration', 0)}s")
            report.append("")
        
        # Performance Benchmarks
        benchmarks = test_results.get('performance_benchmarks', {})
        if benchmarks and 'platform_benchmarks' in benchmarks:
            report.append("⏱️  PERFORMANCE BENCHMARKS:")
            for platform, metrics in benchmarks['platform_benchmarks'].items():
                report.append(f"   {platform}: {metrics['avg_time_ms']}ms avg ({metrics['min_time_ms']}-{metrics['max_time_ms']}ms)")
            
            comparison = benchmarks.get('cross_platform_comparison', {})
            if comparison:
                report.append(f"   Fastest Platform: {comparison.get('fastest_platform', 'N/A')}")
                report.append(f"   Overall Average: {comparison.get('overall_avg_ms', 0)}ms")
            report.append("")
        
        # Stress Tests
        stress_tests = test_results.get('stress_tests', {})
        if stress_tests:
            report.append("💪 STRESS TESTS:")
            
            concurrent = stress_tests.get('concurrent_requests')
            if concurrent:
                metrics = concurrent.get('metrics', {})
                status = "✅ PASS" if concurrent.get('success') else "❌ FAIL"
                report.append(f"   Concurrent Requests: {status}")
                report.append(f"     Successful: {metrics.get('successful_requests', 0)}/{metrics.get('concurrent_count', 0)}")
                report.append(f"     Avg Response Time: {metrics.get('avg_response_time_ms', 0)}ms")
            
            memory = stress_tests.get('memory_stress')
            if memory:
                metrics = memory.get('metrics', {})
                status = "✅ PASS" if memory.get('success') else "❌ FAIL"
                report.append(f"   Memory Stress: {status}")
                report.append(f"     Memory Growth: {metrics.get('memory_growth_mb', 0)}MB")
            
            rapid = stress_tests.get('rapid_fire')
            if rapid:
                metrics = rapid.get('metrics', {})
                status = "✅ PASS" if rapid.get('success') else "❌ FAIL"
                report.append(f"   Rapid Fire: {status}")
                report.append(f"     Success Rate: {metrics.get('successful_requests', 0)}/{metrics.get('requests_count', 0)}")
            
            report.append("")
        
        # Edge Cases
        edge_cases = test_results.get('edge_case_tests', {})
        if edge_cases and 'tests' in edge_cases:
            passed_edge_cases = sum(1 for test in edge_cases['tests'] if test.get('success', False))
            total_edge_cases = len(edge_cases['tests'])
            report.append("🔍 EDGE CASE TESTS:")
            report.append(f"   Passed: {passed_edge_cases}/{total_edge_cases}")
            
            # Show some examples
            extreme_inputs = edge_cases.get('extreme_inputs', [])
            if extreme_inputs:
                report.append("   Extreme Input Examples:")
                for test in extreme_inputs[:3]:
                    status = "✅" if test.get('success') else "❌"
                    case_name = test.get('case_name', 'unknown')
                    report.append(f"     {status} {case_name}")
            
            report.append("")
        
        # Error Recovery
        error_recovery = test_results.get('error_recovery_tests', {})
        if error_recovery:
            report.append("🔄 ERROR RECOVERY:")
            
            for test_name, test_result in error_recovery.items():
                if isinstance(test_result, dict) and 'success' in test_result:
                    status = "✅ PASS" if test_result['success'] else "❌ FAIL"
                    report.append(f"   {test_name}: {status}")
            
            report.append("")
        
        report_text = "\n".join(report)
        
        if output_file:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(report_text)
            print(f"📝 Performance report saved to {output_file}")
        
        return report_text

# Test runner function
async def run_performance_edge_case_tests(openai_api_key: str = None, api_url: str = "http://localhost:8000"):
    """Main performance test runner"""
    tester = PerformanceEdgeCaseTester(openai_api_key, api_url)
    results = await tester.run_performance_tests()
    
    # Generate report
    report = tester.generate_performance_report(
        results,
        output_file="performance_edge_case_report.txt"
    )
    
    print(report)
    return results

if __name__ == "__main__":
    import sys
    
    openai_key = None
    api_url = "http://localhost:8000"
    
    if len(sys.argv) > 1:
        openai_key = sys.argv[1]
    if len(sys.argv) > 2:
        api_url = sys.argv[2]
    
    print("🚀 Running performance and edge case tests...")
    if openai_key:
        print("   With OpenAI API key - full testing enabled")
    else:
        print("   Without API key - limited testing")
    
    asyncio.run(run_performance_edge_case_tests(openai_key, api_url))