#!/usr/bin/env python3
"""
AdCopySurge End-to-End API Validation Tests
Tests the complete analysis pipeline without mock data or fallbacks
Run before production deployment to ensure all services work correctly
"""

import asyncio
import json
import time
import uuid
import requests
from typing import Dict, List, Any, Optional
from datetime import datetime
import sys
import os

# Configuration
class APIValidationConfig:
    def __init__(self):
        # API endpoints - adjust for your deployment
        self.BASE_URL = os.getenv('API_BASE_URL', 'http://localhost:8000/api')
        self.FRONTEND_URL = os.getenv('FRONTEND_URL', 'http://localhost:3000')
        
        # Test user credentials (create a test user for these tests)
        self.TEST_USER_EMAIL = os.getenv('TEST_USER_EMAIL', 'api-test@adcopysurge.com')
        self.TEST_USER_PASSWORD = os.getenv('TEST_USER_PASSWORD', 'test-password-123')
        
        # Test timeout settings
        self.REQUEST_TIMEOUT = 30
        self.ANALYSIS_TIMEOUT = 60
        
        # Test data (REAL ad copy for authentic testing)
        self.TEST_ADS = [
            {
                "headline": "Transform Your Marketing ROI with AI-Powered Analytics",
                "body_text": "Stop guessing what works. Our advanced analytics platform uses machine learning to identify your highest-converting campaigns, optimize ad spend in real-time, and deliver 3x better ROI. Join 5,000+ marketers already scaling their results.",
                "cta": "Start Free Trial",
                "platform": "facebook",
                "industry": "MarTech",
                "target_audience": "Digital marketers at B2B companies"
            },
            {
                "headline": "The Smartwatch That Actually Improves Your Health",
                "body_text": "Unlike other fitness trackers that just count steps, our medical-grade sensors provide real health insights. Monitor blood oxygen, detect irregular heartbeats, and get personalized recommendations from real doctors. FDA-approved accuracy you can trust.",
                "cta": "Shop Now",
                "platform": "google",
                "industry": "Health & Fitness",
                "target_audience": "Health-conscious adults 25-55"
            },
            {
                "headline": "Scale Your SaaS from $0 to $1M ARR",
                "body_text": "The proven playbook used by 200+ successful SaaS founders. Learn the exact strategies, templates, and growth tactics that consistently drive customer acquisition, reduce churn, and accelerate revenue growth. Implementation guaranteed.",
                "cta": "Get Playbook",
                "platform": "linkedin", 
                "industry": "SaaS",
                "target_audience": "SaaS founders and growth teams"
            }
        ]

class APITestResult:
    def __init__(self, test_name: str):
        self.test_name = test_name
        self.start_time = time.time()
        self.end_time = None
        self.success = False
        self.error_message = None
        self.response_data = None
        self.duration = None
        
    def complete(self, success: bool, error_message: str = None, response_data: Any = None):
        self.end_time = time.time()
        self.duration = self.end_time - self.start_time
        self.success = success
        self.error_message = error_message
        self.response_data = response_data
        
    def to_dict(self):
        return {
            'test_name': self.test_name,
            'success': self.success,
            'duration': round(self.duration, 2) if self.duration else None,
            'error_message': self.error_message,
            'timestamp': datetime.now().isoformat()
        }

class E2EAPIValidator:
    def __init__(self, config: APIValidationConfig):
        self.config = config
        self.session = requests.Session()
        self.session.timeout = config.REQUEST_TIMEOUT
        self.auth_token = None
        self.test_results: List[APITestResult] = []
        
    def log(self, message: str, level: str = "INFO"):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] [{level}] {message}")
        
    def add_test_result(self, result: APITestResult):
        self.test_results.append(result)
        status = "✅ PASS" if result.success else "❌ FAIL"
        duration = f" ({result.duration:.2f}s)" if result.duration else ""
        self.log(f"{status} {result.test_name}{duration}")
        if not result.success and result.error_message:
            self.log(f"   Error: {result.error_message}", "ERROR")
            
    def test_health_checks(self) -> APITestResult:
        """Test basic API health and connectivity"""
        result = APITestResult("API Health Checks")
        
        try:
            # Test backend API health
            response = self.session.get(f"{self.config.BASE_URL}/health")
            if response.status_code != 200:
                result.complete(False, f"API health check failed: {response.status_code}")
                return result
                
            health_data = response.json()
            if health_data.get('status') != 'healthy':
                result.complete(False, f"API reports unhealthy status: {health_data}")
                return result
                
            # Test frontend connectivity (if available)
            try:
                frontend_response = self.session.get(f"{self.config.FRONTEND_URL}/health", timeout=5)
                self.log(f"Frontend health: {frontend_response.status_code}")
            except:
                self.log("Frontend health check skipped (may not be available)", "WARN")
                
            result.complete(True, response_data=health_data)
            
        except Exception as e:
            result.complete(False, f"Health check failed: {str(e)}")
            
        return result
        
    def test_authentication(self) -> APITestResult:
        """Test user authentication flow"""
        result = APITestResult("User Authentication")
        
        try:
            # Test login
            login_data = {
                "username": self.config.TEST_USER_EMAIL,
                "password": self.config.TEST_USER_PASSWORD
            }
            
            response = self.session.post(f"{self.config.BASE_URL}/auth/token", data=login_data)
            
            if response.status_code == 404:
                result.complete(False, "Authentication endpoint not found - check API configuration")
                return result
                
            if response.status_code != 200:
                result.complete(False, f"Login failed: {response.status_code} - {response.text}")
                return result
                
            token_data = response.json()
            self.auth_token = token_data.get('access_token')
            
            if not self.auth_token:
                result.complete(False, f"No access token received: {token_data}")
                return result
                
            # Set auth header for future requests
            self.session.headers.update({'Authorization': f'Bearer {self.auth_token}'})
            
            # Test authenticated endpoint
            me_response = self.session.get(f"{self.config.BASE_URL}/auth/me")
            if me_response.status_code != 200:
                result.complete(False, f"Authenticated request failed: {me_response.status_code}")
                return result
                
            user_data = me_response.json()
            result.complete(True, response_data={
                'user_id': user_data.get('id'),
                'email': user_data.get('email')
            })
            
        except Exception as e:
            result.complete(False, f"Authentication test failed: {str(e)}")
            
        return result
        
    def test_single_ad_analysis(self, ad_data: Dict) -> APITestResult:
        """Test single ad analysis pipeline"""
        test_name = f"Single Ad Analysis ({ad_data['platform']})"
        result = APITestResult(test_name)
        
        try:
            # Prepare analysis request
            analysis_request = {
                "ad": ad_data,
                "competitor_ads": [],
                "enabled_tools": [
                    "compliance",
                    "legal",
                    "brand_voice", 
                    "psychology",
                    "roi_generator",
                    "ab_test_generator",
                    "industry_optimizer",
                    "performance_forensics"
                ]
            }
            
            self.log(f"Starting analysis for {ad_data['platform']} ad: '{ad_data['headline'][:50]}...'")
            
            # Submit analysis (with extended timeout for AI processing)
            response = self.session.post(
                f"{self.config.BASE_URL}/ads/analyze",
                json=analysis_request,
                timeout=self.config.ANALYSIS_TIMEOUT
            )
            
            if response.status_code == 401:
                result.complete(False, "Authentication failed - check test user credentials")
                return result
                
            if response.status_code == 404:
                result.complete(False, "Analysis endpoint not found - check API configuration")
                return result
                
            if response.status_code != 200:
                result.complete(False, f"Analysis request failed: {response.status_code} - {response.text}")
                return result
                
            analysis_data = response.json()
            
            # Validate response structure
            validation_errors = self._validate_analysis_response(analysis_data)
            if validation_errors:
                result.complete(False, f"Invalid analysis response: {', '.join(validation_errors)}")
                return result
                
            # Check for real scores (not mock data)
            scores = analysis_data.get('scores', {})
            if not scores or scores.get('overall_score') is None:
                result.complete(False, "Analysis returned no scores - AI processing may have failed")
                return result
                
            # Verify scores are realistic (not obvious mock values like 70, 75, 80)
            overall_score = scores.get('overall_score', 0)
            if overall_score in [70, 75, 80, 85] and all(
                scores.get(field) in [70, 75, 80, 85] 
                for field in ['clarity_score', 'persuasion_score', 'emotion_score']
            ):
                result.complete(False, f"Suspicious mock-like scores detected: {scores}")
                return result
                
            # Check for alternatives generation
            alternatives = analysis_data.get('alternatives', [])
            if not alternatives:
                self.log("No alternatives generated - this may be expected", "WARN")
                
            result.complete(True, response_data={
                'analysis_id': analysis_data.get('analysis_id'),
                'scores': scores,
                'alternatives_count': len(alternatives),
                'processing_time': analysis_data.get('processing_time')
            })
            
        except requests.exceptions.Timeout:
            result.complete(False, f"Analysis timed out after {self.config.ANALYSIS_TIMEOUT} seconds")
        except Exception as e:
            result.complete(False, f"Analysis test failed: {str(e)}")
            
        return result
        
    def test_comprehensive_analysis(self) -> APITestResult:
        """Test comprehensive analysis with all tools"""
        result = APITestResult("Comprehensive Analysis (All Tools)")
        
        try:
            # Use the first test ad for comprehensive analysis
            ad_data = self.config.TEST_ADS[0]
            
            self.log("Starting comprehensive analysis with all 9 tools...")
            
            response = self.session.post(
                f"{self.config.BASE_URL}/ads/comprehensive-analyze",
                json={
                    "ad_copy": f"{ad_data['headline']} {ad_data['body_text']} {ad_data['cta']}",
                    "platform": ad_data['platform'],
                    "industry": ad_data.get('industry'),
                    "target_audience": ad_data.get('target_audience')
                },
                timeout=self.config.ANALYSIS_TIMEOUT
            )
            
            if response.status_code == 404:
                result.complete(False, "Comprehensive analysis endpoint not available")
                return result
                
            if response.status_code != 200:
                result.complete(False, f"Comprehensive analysis failed: {response.status_code} - {response.text}")
                return result
                
            analysis_data = response.json()
            
            # Validate comprehensive response
            required_sections = ['original', 'improved', 'compliance', 'psychology', 'abTests', 'roi', 'legal']
            missing_sections = [section for section in required_sections if section not in analysis_data]
            
            if missing_sections:
                result.complete(False, f"Missing analysis sections: {missing_sections}")
                return result
                
            # Verify improved copy exists and is different from original
            original_copy = analysis_data.get('original', {}).get('copy', '')
            improved_copy = analysis_data.get('improved', {}).get('copy', '')
            
            if not improved_copy or improved_copy == original_copy:
                result.complete(False, "No improved copy generated or identical to original")
                return result
                
            result.complete(True, response_data={
                'original_score': analysis_data.get('original', {}).get('score'),
                'improved_score': analysis_data.get('improved', {}).get('score'),
                'compliance_status': analysis_data.get('compliance', {}).get('status'),
                'psychology_score': analysis_data.get('psychology', {}).get('overallScore'),
                'ab_tests_count': len(analysis_data.get('abTests', {}).get('variations', [])),
                'legal_risk': analysis_data.get('legal', {}).get('riskLevel')
            })
            
        except requests.exceptions.Timeout:
            result.complete(False, f"Comprehensive analysis timed out after {self.config.ANALYSIS_TIMEOUT} seconds")
        except Exception as e:
            result.complete(False, f"Comprehensive analysis test failed: {str(e)}")
            
        return result
        
    def test_analysis_history(self) -> APITestResult:
        """Test analysis history retrieval"""
        result = APITestResult("Analysis History Retrieval")
        
        try:
            response = self.session.get(f"{self.config.BASE_URL}/analyses/history?limit=10")
            
            if response.status_code != 200:
                result.complete(False, f"History retrieval failed: {response.status_code} - {response.text}")
                return result
                
            history_data = response.json()
            
            # Validate history structure
            if not isinstance(history_data, list):
                result.complete(False, f"History response is not a list: {type(history_data)}")
                return result
                
            result.complete(True, response_data={
                'total_analyses': len(history_data),
                'recent_platforms': list(set(item.get('platform') for item in history_data if item.get('platform')))
            })
            
        except Exception as e:
            result.complete(False, f"History test failed: {str(e)}")
            
        return result
        
    def test_individual_tools(self) -> List[APITestResult]:
        """Test individual AI tools"""
        results = []
        ad_data = self.config.TEST_ADS[0]
        
        tools = [
            ("compliance", "/tools/compliance-checker"),
            ("psychology", "/tools/psychology-scorer"),
            ("brand_voice", "/tools/brand-voice-engine"),
            ("legal", "/tools/legal-risk-scanner"),
            ("roi", "/tools/roi-generator"),
            ("ab_test", "/tools/ab-test-generator"),
            ("industry", "/tools/industry-optimizer"),
            ("performance", "/tools/performance-forensics")
        ]
        
        for tool_name, endpoint in tools:
            result = APITestResult(f"Individual Tool: {tool_name}")
            
            try:
                tool_request = {
                    "ad_copy": ad_data,
                    "platform": ad_data['platform'],
                    "industry": ad_data.get('industry'),
                    "target_audience": ad_data.get('target_audience')
                }
                
                response = self.session.post(
                    f"{self.config.BASE_URL}{endpoint}",
                    json=tool_request,
                    timeout=30
                )
                
                if response.status_code == 404:
                    result.complete(False, f"Tool endpoint {endpoint} not found")
                elif response.status_code != 200:
                    result.complete(False, f"Tool failed: {response.status_code} - {response.text}")
                else:
                    tool_data = response.json()
                    result.complete(True, response_data={'tool': tool_name, 'response_keys': list(tool_data.keys())})
                    
            except requests.exceptions.Timeout:
                result.complete(False, f"Tool {tool_name} timed out")
            except Exception as e:
                result.complete(False, f"Tool {tool_name} failed: {str(e)}")
                
            results.append(result)
            
        return results
        
    def _validate_analysis_response(self, data: Dict) -> List[str]:
        """Validate analysis response structure"""
        errors = []
        
        # Check required top-level fields
        required_fields = ['analysis_id', 'scores']
        for field in required_fields:
            if field not in data:
                errors.append(f"Missing required field: {field}")
                
        # Validate scores structure
        scores = data.get('scores', {})
        if scores:
            score_fields = ['overall_score', 'clarity_score', 'persuasion_score', 'emotion_score']
            for field in score_fields:
                if field in scores:
                    score = scores[field]
                    if not isinstance(score, (int, float)) or score < 0 or score > 100:
                        errors.append(f"Invalid score for {field}: {score}")
                        
        return errors
        
    def run_all_tests(self) -> Dict[str, Any]:
        """Run all validation tests"""
        self.log("🚀 Starting AdCopySurge E2E API Validation Tests")
        self.log(f"Testing against: {self.config.BASE_URL}")
        
        start_time = time.time()
        
        # Test 1: Health checks
        health_result = self.test_health_checks()
        self.add_test_result(health_result)
        
        if not health_result.success:
            self.log("❌ Health checks failed - aborting remaining tests", "ERROR")
            return self._generate_report(start_time)
            
        # Test 2: Authentication
        auth_result = self.test_authentication()
        self.add_test_result(auth_result)
        
        if not auth_result.success:
            self.log("❌ Authentication failed - aborting remaining tests", "ERROR")
            return self._generate_report(start_time)
            
        # Test 3: Single ad analyses
        for i, ad_data in enumerate(self.config.TEST_ADS):
            analysis_result = self.test_single_ad_analysis(ad_data)
            self.add_test_result(analysis_result)
            
            # Add delay between analyses to avoid overwhelming the API
            if i < len(self.config.TEST_ADS) - 1:
                time.sleep(2)
                
        # Test 4: Comprehensive analysis
        comprehensive_result = self.test_comprehensive_analysis()
        self.add_test_result(comprehensive_result)
        
        # Test 5: Analysis history
        history_result = self.test_analysis_history()
        self.add_test_result(history_result)
        
        # Test 6: Individual tools (optional - can be slow)
        self.log("Testing individual AI tools...")
        tool_results = self.test_individual_tools()
        for tool_result in tool_results:
            self.add_test_result(tool_result)
            
        return self._generate_report(start_time)
        
    def _generate_report(self, start_time: float) -> Dict[str, Any]:
        """Generate test report"""
        end_time = time.time()
        total_duration = end_time - start_time
        
        passed_tests = [r for r in self.test_results if r.success]
        failed_tests = [r for r in self.test_results if not r.success]
        
        report = {
            'summary': {
                'total_tests': len(self.test_results),
                'passed': len(passed_tests),
                'failed': len(failed_tests),
                'success_rate': round(len(passed_tests) / len(self.test_results) * 100, 1) if self.test_results else 0,
                'total_duration': round(total_duration, 2),
                'timestamp': datetime.now().isoformat()
            },
            'results': [r.to_dict() for r in self.test_results],
            'failed_tests': [r.to_dict() for r in failed_tests]
        }
        
        # Print summary
        self.log("=" * 60)
        self.log("🎯 E2E API VALIDATION SUMMARY")
        self.log("=" * 60)
        self.log(f"Total Tests: {report['summary']['total_tests']}")
        self.log(f"Passed: {report['summary']['passed']} ✅")
        self.log(f"Failed: {report['summary']['failed']} ❌")
        self.log(f"Success Rate: {report['summary']['success_rate']}%")
        self.log(f"Total Duration: {report['summary']['total_duration']}s")
        
        if failed_tests:
            self.log("\n❌ FAILED TESTS:")
            for failed in failed_tests:
                self.log(f"  • {failed.test_name}: {failed.error_message}")
                
        if report['summary']['success_rate'] >= 90:
            self.log("\n🎉 API VALIDATION PASSED - READY FOR PRODUCTION!")
        elif report['summary']['success_rate'] >= 75:
            self.log("\n⚠️ API VALIDATION MOSTLY PASSED - REVIEW FAILURES")
        else:
            self.log("\n❌ API VALIDATION FAILED - NOT READY FOR PRODUCTION")
            
        return report

def main():
    """Main test execution"""
    config = APIValidationConfig()
    validator = E2EAPIValidator(config)
    
    # Run all tests
    report = validator.run_all_tests()
    
    # Save report to file
    report_filename = f"e2e_api_validation_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(report_filename, 'w') as f:
        json.dump(report, f, indent=2)
        
    print(f"\n📄 Full report saved to: {report_filename}")
    
    # Exit with error code if tests failed
    if report['summary']['success_rate'] < 90:
        sys.exit(1)
    else:
        sys.exit(0)

if __name__ == "__main__":
    main()