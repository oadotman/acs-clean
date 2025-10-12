#!/usr/bin/env python3
"""
AdCopySurge Deployment Test Script
Tests the complete user journey end-to-end to verify deployment success.
"""

import asyncio
import json
import time
from typing import Dict, Any
import httpx
import pytest
from datetime import datetime

# Configuration
API_BASE_URL = "https://api.adcopysurge.com"
FRONTEND_URL = "https://adcopysurge.com"
TIMEOUT = 30

class DeploymentTester:
    def __init__(self, api_url: str = API_BASE_URL):
        self.api_url = api_url.rstrip('/')
        self.client = httpx.AsyncClient(timeout=TIMEOUT)
        self.auth_token = None
        self.user_id = None
        
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.aclose()

    async def test_infrastructure(self) -> Dict[str, Any]:
        """Test basic infrastructure health."""
        results = {}
        
        # Test API health
        try:
            response = await self.client.get(f"{self.api_url}/health")
            results['api_health'] = {
                'status': 'pass' if response.status_code == 200 else 'fail',
                'response_time': response.elapsed.total_seconds(),
                'status_code': response.status_code
            }
        except Exception as e:
            results['api_health'] = {'status': 'fail', 'error': str(e)}
        
        # Test detailed health check
        try:
            response = await self.client.get(f"{self.api_url}/healthz")
            results['api_healthz'] = {
                'status': 'pass' if response.status_code == 200 else 'fail',
                'response_time': response.elapsed.total_seconds(),
                'checks': response.json().get('checks', {}) if response.status_code == 200 else {}
            }
        except Exception as e:
            results['api_healthz'] = {'status': 'fail', 'error': str(e)}
        
        # Test frontend
        try:
            response = await self.client.get(FRONTEND_URL)
            results['frontend'] = {
                'status': 'pass' if response.status_code == 200 else 'fail',
                'response_time': response.elapsed.total_seconds(),
                'status_code': response.status_code
            }
        except Exception as e:
            results['frontend'] = {'status': 'fail', 'error': str(e)}
            
        return results

    async def test_authentication(self) -> Dict[str, Any]:
        """Test user registration and authentication."""
        results = {}
        timestamp = int(time.time())
        
        # Test user registration
        test_user = {
            "email": f"test_{timestamp}@example.com",
            "password": "TestPassword123!",
            "full_name": f"Test User {timestamp}"
        }
        
        try:
            response = await self.client.post(
                f"{self.api_url}/api/auth/register",
                json=test_user
            )
            results['registration'] = {
                'status': 'pass' if response.status_code in [200, 201] else 'fail',
                'status_code': response.status_code,
                'response': response.json() if response.status_code < 500 else None
            }
            
            if response.status_code in [200, 201]:
                data = response.json()
                if 'access_token' in data:
                    self.auth_token = data['access_token']
                    self.user_id = data.get('user', {}).get('id')
                    
        except Exception as e:
            results['registration'] = {'status': 'fail', 'error': str(e)}
        
        # Test user login
        if not self.auth_token:
            try:
                response = await self.client.post(
                    f"{self.api_url}/api/auth/login",
                    data={
                        "username": test_user["email"],
                        "password": test_user["password"]
                    },
                    headers={"Content-Type": "application/x-www-form-urlencoded"}
                )
                results['login'] = {
                    'status': 'pass' if response.status_code == 200 else 'fail',
                    'status_code': response.status_code
                }
                
                if response.status_code == 200:
                    data = response.json()
                    self.auth_token = data.get('access_token')
                    
            except Exception as e:
                results['login'] = {'status': 'fail', 'error': str(e)}
        else:
            results['login'] = {'status': 'skip', 'reason': 'Token from registration'}
        
        # Test token validation
        if self.auth_token:
            try:
                response = await self.client.get(
                    f"{self.api_url}/api/auth/me",
                    headers={"Authorization": f"Bearer {self.auth_token}"}
                )
                results['token_validation'] = {
                    'status': 'pass' if response.status_code == 200 else 'fail',
                    'status_code': response.status_code
                }
            except Exception as e:
                results['token_validation'] = {'status': 'fail', 'error': str(e)}
        else:
            results['token_validation'] = {'status': 'fail', 'error': 'No auth token available'}
            
        return results

    async def test_ad_analysis(self) -> Dict[str, Any]:
        """Test the core ad analysis functionality."""
        results = {}
        
        if not self.auth_token:
            return {'status': 'skip', 'reason': 'No auth token available'}
        
        # Test ad analysis
        test_ad = {
            "headline": "Revolutionary AI Tool Boosts Your Marketing ROI by 300%",
            "body_text": "Discover the secret weapon that top marketers use to create converting ad copy in minutes, not hours. Our AI-powered platform analyzes your audience and generates high-performing ads that drive real results.",
            "cta": "Start Your Free Trial Today",
            "platform": "facebook",
            "target_audience": "Small business owners aged 25-45",
            "industry": "Marketing Technology"
        }
        
        try:
            response = await self.client.post(
                f"{self.api_url}/api/ads/analyze",
                json=test_ad,
                headers={"Authorization": f"Bearer {self.auth_token}"}
            )
            
            results['ad_analysis'] = {
                'status': 'pass' if response.status_code == 200 else 'fail',
                'status_code': response.status_code,
                'response_time': response.elapsed.total_seconds()
            }
            
            if response.status_code == 200:
                data = response.json()
                results['ad_analysis']['has_scores'] = 'scores' in data
                results['ad_analysis']['has_feedback'] = 'feedback' in data
                results['ad_analysis']['has_alternatives'] = 'alternatives' in data
                results['ad_analysis']['analysis_id'] = data.get('analysis_id')
                
        except Exception as e:
            results['ad_analysis'] = {'status': 'fail', 'error': str(e)}
        
        # Test analysis history
        try:
            response = await self.client.get(
                f"{self.api_url}/api/ads/history",
                headers={"Authorization": f"Bearer {self.auth_token}"}
            )
            
            results['analysis_history'] = {
                'status': 'pass' if response.status_code == 200 else 'fail',
                'status_code': response.status_code
            }
            
        except Exception as e:
            results['analysis_history'] = {'status': 'fail', 'error': str(e)}
            
        return results

    async def test_analytics(self) -> Dict[str, Any]:
        """Test analytics endpoints."""
        results = {}
        
        if not self.auth_token:
            return {'status': 'skip', 'reason': 'No auth token available'}
        
        # Test usage analytics
        try:
            response = await self.client.get(
                f"{self.api_url}/api/analytics/usage",
                headers={"Authorization": f"Bearer {self.auth_token}"}
            )
            
            results['usage_analytics'] = {
                'status': 'pass' if response.status_code == 200 else 'fail',
                'status_code': response.status_code
            }
            
        except Exception as e:
            results['usage_analytics'] = {'status': 'fail', 'error': str(e)}
        
        # Test performance analytics
        try:
            response = await self.client.get(
                f"{self.api_url}/api/analytics/performance",
                headers={"Authorization": f"Bearer {self.auth_token}"}
            )
            
            results['performance_analytics'] = {
                'status': 'pass' if response.status_code in [200, 404] else 'fail',
                'status_code': response.status_code
            }
            
        except Exception as e:
            results['performance_analytics'] = {'status': 'fail', 'error': str(e)}
            
        return results

    async def test_subscriptions(self) -> Dict[str, Any]:
        """Test subscription management."""
        results = {}
        
        # Test subscription plans (public endpoint)
        try:
            response = await self.client.get(f"{self.api_url}/api/subscriptions/plans")
            
            results['subscription_plans'] = {
                'status': 'pass' if response.status_code == 200 else 'fail',
                'status_code': response.status_code
            }
            
            if response.status_code == 200:
                plans = response.json()
                results['subscription_plans']['has_plans'] = len(plans) > 0
                
        except Exception as e:
            results['subscription_plans'] = {'status': 'fail', 'error': str(e)}
        
        # Test user subscription status (requires auth)
        if self.auth_token:
            try:
                response = await self.client.get(
                    f"{self.api_url}/api/subscriptions/status",
                    headers={"Authorization": f"Bearer {self.auth_token}"}
                )
                
                results['subscription_status'] = {
                    'status': 'pass' if response.status_code in [200, 404] else 'fail',
                    'status_code': response.status_code
                }
                
            except Exception as e:
                results['subscription_status'] = {'status': 'fail', 'error': str(e)}
        
        return results

    async def run_all_tests(self) -> Dict[str, Any]:
        """Run all deployment tests."""
        print("🚀 Starting AdCopySurge Deployment Tests...")
        print(f"API URL: {self.api_url}")
        print(f"Frontend URL: {FRONTEND_URL}")
        print("-" * 60)
        
        all_results = {
            'test_run': {
                'timestamp': datetime.now().isoformat(),
                'api_url': self.api_url,
                'frontend_url': FRONTEND_URL
            }
        }
        
        # Test infrastructure
        print("📡 Testing infrastructure...")
        all_results['infrastructure'] = await self.test_infrastructure()
        
        # Test authentication
        print("🔐 Testing authentication...")
        all_results['authentication'] = await self.test_authentication()
        
        # Test ad analysis
        print("🧠 Testing ad analysis...")
        all_results['ad_analysis'] = await self.test_ad_analysis()
        
        # Test analytics
        print("📊 Testing analytics...")
        all_results['analytics'] = await self.test_analytics()
        
        # Test subscriptions
        print("💳 Testing subscriptions...")
        all_results['subscriptions'] = await self.test_subscriptions()
        
        return all_results

def print_results(results: Dict[str, Any]):
    """Print test results in a readable format."""
    print("\n" + "="*60)
    print("🧪 DEPLOYMENT TEST RESULTS")
    print("="*60)
    
    total_tests = 0
    passed_tests = 0
    failed_tests = 0
    
    for category, tests in results.items():
        if category == 'test_run':
            continue
            
        print(f"\n📋 {category.upper().replace('_', ' ')}")
        print("-" * 40)
        
        for test_name, test_result in tests.items():
            if isinstance(test_result, dict) and 'status' in test_result:
                total_tests += 1
                status = test_result['status']
                
                if status == 'pass':
                    print(f"  ✅ {test_name}: PASS")
                    passed_tests += 1
                elif status == 'fail':
                    print(f"  ❌ {test_name}: FAIL")
                    failed_tests += 1
                    if 'error' in test_result:
                        print(f"     Error: {test_result['error']}")
                elif status == 'skip':
                    print(f"  ⏭️  {test_name}: SKIP")
                    if 'reason' in test_result:
                        print(f"     Reason: {test_result['reason']}")
                
                # Show additional info
                if 'response_time' in test_result:
                    print(f"     Response Time: {test_result['response_time']:.2f}s")
                if 'status_code' in test_result:
                    print(f"     Status Code: {test_result['status_code']}")
    
    print("\n" + "="*60)
    print("📈 SUMMARY")
    print("="*60)
    print(f"Total Tests: {total_tests}")
    print(f"✅ Passed: {passed_tests}")
    print(f"❌ Failed: {failed_tests}")
    print(f"⏭️  Skipped: {total_tests - passed_tests - failed_tests}")
    
    success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
    print(f"Success Rate: {success_rate:.1f}%")
    
    if failed_tests == 0:
        print("\n🎉 ALL TESTS PASSED! Deployment is ready for production!")
    else:
        print(f"\n⚠️  {failed_tests} test(s) failed. Please check the issues above.")
    
    print("="*60)

async def main():
    """Main test runner."""
    async with DeploymentTester() as tester:
        results = await tester.run_all_tests()
        print_results(results)
        
        # Save results to file
        with open(f"deployment_test_results_{int(time.time())}.json", 'w') as f:
            json.dump(results, f, indent=2, default=str)
        
        print(f"\n💾 Results saved to deployment_test_results_{int(time.time())}.json")

if __name__ == "__main__":
    asyncio.run(main())
