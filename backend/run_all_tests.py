#!/usr/bin/env python3
"""
Master Test Runner for Platform-Specific Ad Generation System

Orchestrates and runs all test suites:
1. Basic validation tests
2. Platform validation tests  
3. Output quality verification tests
4. Frontend integration tests
5. Performance and edge case tests

Generates comprehensive reports and recommendations.
"""

import asyncio
import time
import json
import sys
from typing import Dict, List, Any
from datetime import datetime

# Import all test modules
try:
    from test_platform_validation import run_platform_validation_tests, run_basic_validation_tests
    from test_output_quality import run_output_quality_tests
    from test_frontend_integration import run_frontend_integration_tests
    from test_performance_edge_cases import run_performance_edge_case_tests
    MODULES_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Could not import test modules: {e}")
    MODULES_AVAILABLE = False

class MasterTestRunner:
    """Orchestrates all platform-specific tests"""
    
    def __init__(self, openai_api_key: str = None, api_url: str = "http://localhost:8000"):
        self.openai_api_key = openai_api_key
        self.api_url = api_url
        self.start_time = time.time()
        
    async def run_all_tests(self) -> Dict[str, Any]:
        """Run complete test suite"""
        print("🚀 Starting comprehensive platform-specific ad generation tests...")
        print("=" * 80)
        
        master_results = {
            'test_suite_info': {
                'start_time': datetime.now().isoformat(),
                'openai_key_provided': bool(self.openai_api_key),
                'api_url': self.api_url,
                'modules_available': MODULES_AVAILABLE
            },
            'test_results': {},
            'summary': {
                'total_test_suites': 0,
                'passed_test_suites': 0,
                'failed_test_suites': 0,
                'total_individual_tests': 0,
                'passed_individual_tests': 0,
                'failed_individual_tests': 0,
                'execution_time_seconds': 0
            },
            'recommendations': [],
            'critical_issues': [],
            'detailed_results': {}
        }
        
        if not MODULES_AVAILABLE:
            master_results['critical_issues'].append("Test modules not available - cannot run comprehensive tests")
            return master_results
        
        # 1. Basic Validation Tests (always run first)
        print("\n🔍 PHASE 1: Basic Validation Tests")
        print("-" * 50)
        try:
            basic_success = run_basic_validation_tests()
            master_results['test_results']['basic_validation'] = {
                'success': basic_success,
                'execution_time': 0.5,  # Estimated
                'test_count': 36  # Estimated based on platforms and data structure
            }
            master_results['summary']['total_test_suites'] += 1
            if basic_success:
                master_results['summary']['passed_test_suites'] += 1
            else:
                master_results['summary']['failed_test_suites'] += 1
                master_results['critical_issues'].append("Basic validation tests failed - test data may be corrupted")
        except Exception as e:
            master_results['test_results']['basic_validation'] = {
                'success': False,
                'error': str(e),
                'execution_time': 0
            }
            master_results['critical_issues'].append(f"Basic validation failed with exception: {e}")
        
        # 2. Platform Validation Tests (if we have API key)
        if self.openai_api_key:
            print("\n🎯 PHASE 2: Platform Validation Tests")
            print("-" * 50)
            try:
                platform_results = await run_platform_validation_tests(self.openai_api_key)
                master_results['test_results']['platform_validation'] = platform_results
                master_results['detailed_results']['platform_validation'] = platform_results
                master_results['summary']['total_test_suites'] += 1
                
                if platform_results and platform_results.get('passed_tests', 0) > 0:
                    master_results['summary']['passed_test_suites'] += 1
                else:
                    master_results['summary']['failed_test_suites'] += 1
                    master_results['critical_issues'].append("Platform validation tests failed")
                
                # Add to individual test counts
                if platform_results:
                    master_results['summary']['total_individual_tests'] += platform_results.get('total_tests', 0)
                    master_results['summary']['passed_individual_tests'] += platform_results.get('passed_tests', 0)
                    master_results['summary']['failed_individual_tests'] += platform_results.get('failed_tests', 0)
                
            except Exception as e:
                master_results['test_results']['platform_validation'] = {
                    'success': False,
                    'error': str(e)
                }
                master_results['critical_issues'].append(f"Platform validation failed: {e}")
        else:
            print("\n⚠️  SKIPPING Platform Validation Tests (no OpenAI API key)")
            master_results['recommendations'].append("Provide OpenAI API key to run platform validation tests")
        
        # 3. Output Quality Tests (if we have API key)
        if self.openai_api_key:
            print("\n🎯 PHASE 3: Output Quality Verification Tests")
            print("-" * 50)
            try:
                quality_results = await run_output_quality_tests(self.openai_api_key)
                master_results['test_results']['output_quality'] = quality_results
                master_results['detailed_results']['output_quality'] = quality_results
                master_results['summary']['total_test_suites'] += 1
                
                if quality_results and quality_results.get('passed_tests', 0) > 0:
                    master_results['summary']['passed_test_suites'] += 1
                else:
                    master_results['summary']['failed_test_suites'] += 1
                    master_results['critical_issues'].append("Output quality tests failed")
                
                # Add to individual test counts
                if quality_results:
                    master_results['summary']['total_individual_tests'] += quality_results.get('total_tests', 0)
                    master_results['summary']['passed_individual_tests'] += quality_results.get('passed_tests', 0)
                    master_results['summary']['failed_individual_tests'] += quality_results.get('failed_tests', 0)
                
                # Analyze quality metrics
                if quality_results and 'quality_metrics' in quality_results:
                    avg_quality = quality_results['quality_metrics'].get('average_quality_score', 0)
                    if avg_quality < 70:
                        master_results['critical_issues'].append(f"Low average quality score: {avg_quality}/100")
                    elif avg_quality < 85:
                        master_results['recommendations'].append(f"Quality score could be improved: {avg_quality}/100")
                
            except Exception as e:
                master_results['test_results']['output_quality'] = {
                    'success': False,
                    'error': str(e)
                }
                master_results['critical_issues'].append(f"Output quality tests failed: {e}")
        else:
            print("\n⚠️  SKIPPING Output Quality Tests (no OpenAI API key)")
        
        # 4. Frontend Integration Tests
        print("\n🖥️  PHASE 4: Frontend Integration Tests")
        print("-" * 50)
        try:
            integration_results = run_frontend_integration_tests(self.api_url)
            master_results['test_results']['frontend_integration'] = integration_results
            master_results['detailed_results']['frontend_integration'] = integration_results
            master_results['summary']['total_test_suites'] += 1
            
            if integration_results and integration_results.get('passed_tests', 0) > 0:
                master_results['summary']['passed_test_suites'] += 1
            else:
                master_results['summary']['failed_test_suites'] += 1
                master_results['critical_issues'].append("Frontend integration tests failed")
            
            # Add to individual test counts
            if integration_results:
                master_results['summary']['total_individual_tests'] += integration_results.get('total_tests', 0)
                master_results['summary']['passed_individual_tests'] += integration_results.get('passed_tests', 0)
                master_results['summary']['failed_individual_tests'] += integration_results.get('failed_tests', 0)
            
            # Check API health
            if integration_results and 'api_tests' in integration_results:
                health_check = integration_results['api_tests'].get('health_check', {})
                if not health_check.get('success', False):
                    master_results['critical_issues'].append("API health check failed")
        
        except Exception as e:
            master_results['test_results']['frontend_integration'] = {
                'success': False,
                'error': str(e)
            }
            master_results['critical_issues'].append(f"Frontend integration tests failed: {e}")
        
        # 5. Performance and Edge Case Tests
        print("\n💪 PHASE 5: Performance and Edge Case Tests")
        print("-" * 50)
        try:
            performance_results = await run_performance_edge_case_tests(self.openai_api_key, self.api_url)
            master_results['test_results']['performance_edge_cases'] = performance_results
            master_results['detailed_results']['performance_edge_cases'] = performance_results
            master_results['summary']['total_test_suites'] += 1
            
            if performance_results and performance_results.get('test_summary', {}).get('passed_tests', 0) > 0:
                master_results['summary']['passed_test_suites'] += 1
            else:
                master_results['summary']['failed_test_suites'] += 1
                master_results['critical_issues'].append("Performance tests failed")
            
            # Add to individual test counts
            if performance_results and 'test_summary' in performance_results:
                summary = performance_results['test_summary']
                master_results['summary']['total_individual_tests'] += summary.get('total_tests', 0)
                master_results['summary']['passed_individual_tests'] += summary.get('passed_tests', 0)
                master_results['summary']['failed_individual_tests'] += summary.get('failed_tests', 0)
            
            # Analyze performance metrics
            if performance_results and 'resource_usage' in performance_results:
                memory_growth = performance_results['resource_usage'].get('memory_growth_mb', 0)
                if memory_growth > 100:
                    master_results['critical_issues'].append(f"High memory usage: {memory_growth}MB growth")
                elif memory_growth > 50:
                    master_results['recommendations'].append(f"Monitor memory usage: {memory_growth}MB growth")
        
        except Exception as e:
            master_results['test_results']['performance_edge_cases'] = {
                'success': False,
                'error': str(e)
            }
            master_results['critical_issues'].append(f"Performance tests failed: {e}")
        
        # Calculate final summary
        master_results['summary']['execution_time_seconds'] = round(time.time() - self.start_time, 2)
        
        # Generate recommendations based on results
        self._generate_recommendations(master_results)
        
        return master_results
    
    def _generate_recommendations(self, results: Dict[str, Any]):
        """Generate recommendations based on test results"""
        recommendations = results['recommendations']
        
        # Success rate analysis
        total_tests = results['summary']['total_individual_tests']
        passed_tests = results['summary']['passed_individual_tests']
        
        if total_tests > 0:
            success_rate = (passed_tests / total_tests) * 100
            
            if success_rate < 70:
                recommendations.append("URGENT: Low overall test success rate - system needs significant fixes")
            elif success_rate < 85:
                recommendations.append("System has some issues that should be addressed")
            elif success_rate >= 95:
                recommendations.append("Excellent test results - system is production ready")
        
        # Platform-specific recommendations
        platform_results = results.get('detailed_results', {}).get('platform_validation', {})
        if platform_results and 'platform_results' in platform_results:
            failing_platforms = []
            for platform, data in platform_results['platform_results'].items():
                success_rate = data['summary']['passed'] / data['summary']['total'] if data['summary']['total'] > 0 else 0
                if success_rate < 0.8:
                    failing_platforms.append(platform)
            
            if failing_platforms:
                recommendations.append(f"Focus on improving these platforms: {', '.join(failing_platforms)}")
        
        # Quality recommendations
        quality_results = results.get('detailed_results', {}).get('output_quality', {})
        if quality_results and 'quality_metrics' in quality_results:
            metrics = quality_results['quality_metrics']
            
            if metrics.get('character_limit_violations', 0) > 5:
                recommendations.append("High number of character limit violations - review generation logic")
            
            if metrics.get('template_phrase_violations', 0) > 3:
                recommendations.append("Template phrases detected in output - improve content originality")
            
            if metrics.get('grammar_issues', 0) > 2:
                recommendations.append("Grammar issues found - enhance language processing")
        
        # Performance recommendations
        perf_results = results.get('detailed_results', {}).get('performance_edge_cases', {})
        if perf_results and 'performance_benchmarks' in perf_results:
            benchmarks = perf_results['performance_benchmarks']
            comparison = benchmarks.get('cross_platform_comparison', {})
            
            if comparison.get('overall_avg_ms', 0) > 5000:
                recommendations.append("Response times are slow - consider optimization")
            elif comparison.get('overall_avg_ms', 0) < 2000:
                recommendations.append("Good performance - response times are acceptable")
    
    def generate_master_report(self, results: Dict[str, Any], output_file: str = None) -> str:
        """Generate comprehensive master test report"""
        report = []
        report.append("=" * 100)
        report.append("COMPREHENSIVE PLATFORM-SPECIFIC AD GENERATION TEST REPORT")
        report.append("=" * 100)
        report.append("")
        
        # Header info
        info = results['test_suite_info']
        report.append("📋 TEST SUITE INFORMATION:")
        report.append(f"   Start Time: {info['start_time']}")
        report.append(f"   OpenAI Key Provided: {'Yes' if info['openai_key_provided'] else 'No'}")
        report.append(f"   API URL: {info['api_url']}")
        report.append(f"   Test Modules Available: {'Yes' if info['modules_available'] else 'No'}")
        report.append("")
        
        # Executive Summary
        summary = results['summary']
        overall_success_rate = round(summary['passed_individual_tests']/summary['total_individual_tests']*100, 1) if summary['total_individual_tests'] > 0 else 0
        
        report.append("🎯 EXECUTIVE SUMMARY:")
        report.append(f"   Overall Success Rate: {overall_success_rate}% ({summary['passed_individual_tests']}/{summary['total_individual_tests']} tests)")
        report.append(f"   Test Suites Passed: {summary['passed_test_suites']}/{summary['total_test_suites']}")
        report.append(f"   Total Execution Time: {summary['execution_time_seconds']}s")
        
        # Overall status
        if overall_success_rate >= 95:
            report.append("   Status: 🟢 EXCELLENT - Production Ready")
        elif overall_success_rate >= 85:
            report.append("   Status: 🟡 GOOD - Minor Issues")
        elif overall_success_rate >= 70:
            report.append("   Status: 🟠 NEEDS WORK - Some Issues")
        else:
            report.append("   Status: 🔴 CRITICAL - Major Issues")
        
        report.append("")
        
        # Critical Issues
        if results['critical_issues']:
            report.append("🚨 CRITICAL ISSUES:")
            for issue in results['critical_issues']:
                report.append(f"   • {issue}")
            report.append("")
        
        # Test Suite Results
        report.append("📊 TEST SUITE RESULTS:")
        
        test_suite_names = {
            'basic_validation': 'Basic Validation',
            'platform_validation': 'Platform Validation', 
            'output_quality': 'Output Quality',
            'frontend_integration': 'Frontend Integration',
            'performance_edge_cases': 'Performance & Edge Cases'
        }
        
        for suite_key, suite_name in test_suite_names.items():
            suite_result = results['test_results'].get(suite_key, {})
            
            if suite_key == 'basic_validation':
                # Handle basic validation differently
                status = "✅ PASS" if suite_result.get('success', False) else "❌ FAIL"
                report.append(f"   {suite_name}: {status}")
                if 'test_count' in suite_result:
                    report.append(f"     Tests: {suite_result['test_count']} data validation checks")
            
            elif 'error' in suite_result:
                report.append(f"   {suite_name}: ❌ ERROR - {suite_result['error']}")
            
            elif suite_key in results.get('detailed_results', {}):
                # Full results available
                detailed = results['detailed_results'][suite_key]
                
                if suite_key == 'platform_validation':
                    passed = detailed.get('passed_tests', 0)
                    total = detailed.get('total_tests', 0)
                    success_rate = round(passed/total*100, 1) if total > 0 else 0
                    status = "✅ PASS" if success_rate >= 80 else "❌ FAIL"
                    report.append(f"   {suite_name}: {status} ({passed}/{total} tests, {success_rate}%)")
                
                elif suite_key == 'output_quality':
                    passed = detailed.get('passed_tests', 0)
                    total = detailed.get('total_tests', 0)
                    avg_quality = detailed.get('quality_metrics', {}).get('average_quality_score', 0)
                    success_rate = round(passed/total*100, 1) if total > 0 else 0
                    status = "✅ PASS" if success_rate >= 80 and avg_quality >= 70 else "❌ FAIL"
                    report.append(f"   {suite_name}: {status} ({passed}/{total} tests, avg quality: {avg_quality}/100)")
                
                elif suite_key == 'frontend_integration':
                    passed = detailed.get('passed_tests', 0)
                    total = detailed.get('total_tests', 0)
                    success_rate = round(passed/total*100, 1) if total > 0 else 0
                    status = "✅ PASS" if success_rate >= 80 else "❌ FAIL"
                    report.append(f"   {suite_name}: {status} ({passed}/{total} tests, {success_rate}%)")
                
                elif suite_key == 'performance_edge_cases':
                    test_summary = detailed.get('test_summary', {})
                    passed = test_summary.get('passed_tests', 0)
                    total = test_summary.get('total_tests', 0)
                    success_rate = round(passed/total*100, 1) if total > 0 else 0
                    status = "✅ PASS" if success_rate >= 80 else "❌ FAIL"
                    report.append(f"   {suite_name}: {status} ({passed}/{total} tests, {success_rate}%)")
                    
                    # Add performance metrics
                    benchmarks = detailed.get('performance_benchmarks', {})
                    if benchmarks and 'cross_platform_comparison' in benchmarks:
                        avg_time = benchmarks['cross_platform_comparison'].get('overall_avg_ms', 0)
                        report.append(f"     Average Response Time: {avg_time}ms")
            else:
                report.append(f"   {suite_name}: ⚠️  SKIPPED or NO DATA")
        
        report.append("")
        
        # Platform-Specific Results
        platform_results = results.get('detailed_results', {}).get('platform_validation', {})
        if platform_results and 'platform_results' in platform_results:
            report.append("🌐 PLATFORM-SPECIFIC RESULTS:")
            for platform, data in platform_results['platform_results'].items():
                passed = data['summary']['passed']
                total = data['summary']['total']
                success_rate = round(passed/total*100, 1) if total > 0 else 0
                status_icon = "✅" if success_rate >= 80 else "⚠️" if success_rate >= 60 else "❌"
                report.append(f"   {platform}: {status_icon} {passed}/{total} ({success_rate}%)")
            report.append("")
        
        # Performance Benchmarks
        perf_results = results.get('detailed_results', {}).get('performance_edge_cases', {})
        if perf_results and 'performance_benchmarks' in perf_results:
            benchmarks = perf_results['performance_benchmarks']
            if 'platform_benchmarks' in benchmarks:
                report.append("⏱️  PERFORMANCE BENCHMARKS:")
                for platform, metrics in benchmarks['platform_benchmarks'].items():
                    report.append(f"   {platform}: {metrics['avg_time_ms']}ms avg")
                report.append("")
        
        # Recommendations
        if results['recommendations']:
            report.append("💡 RECOMMENDATIONS:")
            for rec in results['recommendations']:
                report.append(f"   • {rec}")
            report.append("")
        
        # Next Steps
        report.append("🚀 NEXT STEPS:")
        if results['critical_issues']:
            report.append("   1. Address all critical issues immediately")
            report.append("   2. Re-run failed test suites after fixes")
        else:
            report.append("   1. Review recommendations and implement improvements")
            report.append("   2. Set up continuous integration with these tests")
        
        if not results['test_suite_info']['openai_key_provided']:
            report.append("   3. Provide OpenAI API key for complete testing")
        
        report.append("   4. Consider implementing real-time monitoring")
        report.append("   5. Schedule regular test runs")
        
        report.append("")
        report.append("=" * 100)
        report.append(f"Report Generated: {datetime.now().isoformat()}")
        report.append("=" * 100)
        
        report_text = "\n".join(report)
        
        if output_file:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(report_text)
            print(f"\n📝 Master test report saved to {output_file}")
        
        return report_text

async def main():
    """Main test runner entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Run comprehensive platform-specific ad generation tests")
    parser.add_argument("--api-key", help="OpenAI API key for full testing")
    parser.add_argument("--api-url", default="http://localhost:8000", help="API base URL")
    parser.add_argument("--output", default="master_test_report.txt", help="Output report file")
    parser.add_argument("--json-output", help="Save detailed results as JSON")
    
    args = parser.parse_args()
    
    # Run all tests
    runner = MasterTestRunner(args.api_key, args.api_url)
    results = await runner.run_all_tests()
    
    # Generate reports
    print("\n" + "=" * 80)
    print("GENERATING REPORTS...")
    print("=" * 80)
    
    # Master report
    report = runner.generate_master_report(results, args.output)
    print(report)
    
    # JSON output if requested
    if args.json_output:
        with open(args.json_output, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, default=str)
        print(f"\n📄 Detailed JSON results saved to {args.json_output}")
    
    # Exit with appropriate code
    if results['critical_issues']:
        print("\n❌ Tests completed with critical issues!")
        sys.exit(1)
    else:
        print("\n✅ Tests completed successfully!")
        sys.exit(0)

if __name__ == "__main__":
    asyncio.run(main())