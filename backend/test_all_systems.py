#!/usr/bin/env python3
"""
Comprehensive system test for AdCopySurge backend
Tests all critical systems after fixes implementation
"""

import asyncio
import os
import sys
import json
import httpx
import time
from typing import Dict, Any, List
from datetime import datetime

# Add the backend directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

class AdCopySurgeSystemTester:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.client = httpx.AsyncClient(timeout=30.0)
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "base_url": base_url,
            "tests": {},
            "summary": {
                "total": 0,
                "passed": 0,
                "failed": 0,
                "warnings": 0
            }
        }
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.aclose()
    
    def log_result(self, test_name: str, status: str, message: str, details: Dict = None):
        """Log test result"""
        self.results["tests"][test_name] = {
            "status": status,
            "message": message,
            "details": details or {},
            "timestamp": datetime.now().isoformat()
        }
        
        self.results["summary"]["total"] += 1
        if status == "PASS":
            self.results["summary"]["passed"] += 1
            print(f"✅ {test_name}: {message}")
        elif status == "WARN":
            self.results["summary"]["warnings"] += 1
            print(f"⚠️  {test_name}: {message}")
        else:
            self.results["summary"]["failed"] += 1
            print(f"❌ {test_name}: {message}")
    
    async def test_health_endpoints(self):
        """Test all health check endpoints"""
        print("\n🏥 Testing Health Check Endpoints...")
        
        # Test main health endpoint
        try:
            response = await self.client.get(f"{self.base_url}/health")
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "healthy":
                    self.log_result("health_main", "PASS", "Main health check passed")
                else:
                    self.log_result("health_main", "WARN", f"Health check degraded: {data}")
            else:
                self.log_result("health_main", "FAIL", f"Health check failed: {response.status_code}")
        except Exception as e:
            self.log_result("health_main", "FAIL", f"Health check exception: {e}")
        
        # Test readiness probe
        try:
            response = await self.client.get(f"{self.base_url}/health/ready")
            if response.status_code == 200:
                self.log_result("health_ready", "PASS", "Readiness probe passed")
            else:
                self.log_result("health_ready", "FAIL", f"Readiness probe failed: {response.status_code}")
        except Exception as e:
            self.log_result("health_ready", "FAIL", f"Readiness probe exception: {e}")
        
        # Test liveness probe
        try:
            response = await self.client.get(f"{self.base_url}/health/live")
            if response.status_code == 200:
                self.log_result("health_live", "PASS", "Liveness probe passed")
            else:
                self.log_result("health_live", "FAIL", f"Liveness probe failed: {response.status_code}")
        except Exception as e:
            self.log_result("health_live", "FAIL", f"Liveness probe exception: {e}")
    
    async def test_blog_endpoints(self):
        """Test blog functionality"""
        print("\n📝 Testing Blog Endpoints...")
        
        # Test blog listing
        try:
            response = await self.client.get(f"{self.base_url}/api/blog/")
            if response.status_code == 200:
                data = response.json()
                if isinstance(data.get("posts"), list):
                    self.log_result("blog_list", "PASS", f"Blog listing returned {len(data['posts'])} posts")
                else:
                    self.log_result("blog_list", "WARN", "Blog listing returned empty response (degraded mode)")
            else:
                self.log_result("blog_list", "FAIL", f"Blog listing failed: {response.status_code}")
        except Exception as e:
            self.log_result("blog_list", "FAIL", f"Blog listing exception: {e}")
        
        # Test blog categories
        try:
            response = await self.client.get(f"{self.base_url}/api/blog/categories")
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list) and len(data) > 0:
                    self.log_result("blog_categories", "PASS", f"Blog categories returned {len(data)} categories")
                else:
                    self.log_result("blog_categories", "WARN", "Blog categories empty (possible degraded mode)")
            else:
                self.log_result("blog_categories", "FAIL", f"Blog categories failed: {response.status_code}")
        except Exception as e:
            self.log_result("blog_categories", "FAIL", f"Blog categories exception: {e}")
        
        # Test popular posts
        try:
            response = await self.client.get(f"{self.base_url}/api/blog/popular")
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    self.log_result("blog_popular", "PASS", f"Popular posts returned {len(data)} posts")
                else:
                    self.log_result("blog_popular", "WARN", "Popular posts empty (possible degraded mode)")
            else:
                self.log_result("blog_popular", "FAIL", f"Popular posts failed: {response.status_code}")
        except Exception as e:
            self.log_result("blog_popular", "FAIL", f"Popular posts exception: {e}")
        
        # Test specific blog post (if any exist)
        try:
            # Try to get a specific post
            response = await self.client.get(f"{self.base_url}/api/blog/facebook-ad-copy-secrets")
            if response.status_code == 200:
                data = response.json()
                if data.get("title"):
                    self.log_result("blog_post_detail", "PASS", f"Blog post detail loaded: {data['title']}")
                else:
                    self.log_result("blog_post_detail", "WARN", "Blog post detail structure unexpected")
            elif response.status_code == 404:
                self.log_result("blog_post_detail", "WARN", "No blog posts found (expected for empty blog)")
            else:
                self.log_result("blog_post_detail", "FAIL", f"Blog post detail failed: {response.status_code}")
        except Exception as e:
            self.log_result("blog_post_detail", "FAIL", f"Blog post detail exception: {e}")
    
    async def test_api_endpoints(self):
        """Test main API endpoints"""
        print("\n🔌 Testing Main API Endpoints...")
        
        # Test root endpoint
        try:
            response = await self.client.get(f"{self.base_url}/")
            if response.status_code == 200:
                data = response.json()
                if data.get("message"):
                    self.log_result("api_root", "PASS", f"Root endpoint: {data['message']}")
                else:
                    self.log_result("api_root", "WARN", "Root endpoint unexpected response")
            else:
                self.log_result("api_root", "FAIL", f"Root endpoint failed: {response.status_code}")
        except Exception as e:
            self.log_result("api_root", "FAIL", f"Root endpoint exception: {e}")
        
        # Test API docs
        try:
            response = await self.client.get(f"{self.base_url}/api/docs")
            if response.status_code == 200:
                self.log_result("api_docs", "PASS", "API documentation accessible")
            else:
                self.log_result("api_docs", "FAIL", f"API docs failed: {response.status_code}")
        except Exception as e:
            self.log_result("api_docs", "FAIL", f"API docs exception: {e}")
    
    async def test_celery_integration(self):
        """Test Celery integration"""
        print("\n⚙️ Testing Celery Integration...")
        
        try:
            # Import Celery app to test configuration
            from app.celery_app import celery_app
            from app.tasks import health_check
            
            # Test Celery app configuration
            if celery_app.conf.broker_url:
                self.log_result("celery_config", "PASS", "Celery configuration loaded successfully")
            else:
                self.log_result("celery_config", "FAIL", "Celery configuration missing broker URL")
            
            # Test task import
            if hasattr(health_check, 'apply_async'):
                self.log_result("celery_tasks", "PASS", "Celery tasks imported successfully")
            else:
                self.log_result("celery_tasks", "FAIL", "Celery tasks not properly configured")
                
        except ImportError as e:
            self.log_result("celery_import", "FAIL", f"Celery import failed: {e}")
        except Exception as e:
            self.log_result("celery_general", "FAIL", f"Celery test failed: {e}")
    
    def test_configuration(self):
        """Test application configuration"""
        print("\n⚙️ Testing Configuration...")
        
        try:
            from app.core.config import settings
            
            # Test critical settings
            if settings.SECRET_KEY and len(settings.SECRET_KEY) >= 32:
                self.log_result("config_secret", "PASS", "SECRET_KEY properly configured")
            else:
                self.log_result("config_secret", "FAIL", "SECRET_KEY missing or too short")
            
            if settings.DATABASE_URL:
                self.log_result("config_database", "PASS", "DATABASE_URL configured")
            else:
                self.log_result("config_database", "FAIL", "DATABASE_URL missing")
            
            if hasattr(settings, 'VERSION') and settings.VERSION:
                self.log_result("config_version", "PASS", f"Version configured: {settings.VERSION}")
            else:
                self.log_result("config_version", "FAIL", "Version setting missing")
            
            if hasattr(settings, 'NODE_ENV'):
                self.log_result("config_node_env", "PASS", f"NODE_ENV configured: {settings.NODE_ENV}")
            else:
                self.log_result("config_node_env", "FAIL", "NODE_ENV setting missing")
                
            # Test blog configuration
            if hasattr(settings, 'ENABLE_BLOG'):
                self.log_result("config_blog", "PASS", f"Blog enabled: {settings.ENABLE_BLOG}")
            else:
                self.log_result("config_blog", "FAIL", "ENABLE_BLOG setting missing")
                
        except Exception as e:
            self.log_result("config_general", "FAIL", f"Configuration test failed: {e}")
    
    def test_imports(self):
        """Test critical imports"""
        print("\n📦 Testing Critical Imports...")
        
        # Test main app import
        try:
            from main import app
            self.log_result("import_main", "PASS", "Main application imported successfully")
        except Exception as e:
            self.log_result("import_main", "FAIL", f"Main app import failed: {e}")
        
        # Test blog imports
        try:
            from app.blog import router as blog_router
            self.log_result("import_blog", "PASS", "Blog router imported successfully")
        except Exception as e:
            self.log_result("import_blog", "FAIL", f"Blog import failed: {e}")
        
        # Test authentication imports
        try:
            from app.auth.dependencies import get_current_user, require_admin
            self.log_result("import_auth", "PASS", "Authentication imports successful")
        except Exception as e:
            self.log_result("import_auth", "FAIL", f"Auth imports failed: {e}")
        
        # Test model imports
        try:
            from app.models.user import User
            from app.models.ad_analysis import AdAnalysis
            self.log_result("import_models", "PASS", "Model imports successful")
        except Exception as e:
            self.log_result("import_models", "FAIL", f"Model imports failed: {e}")
    
    async def run_all_tests(self):
        """Run all system tests"""
        print("🔍 Starting AdCopySurge System Tests...")
        print(f"Testing against: {self.base_url}")
        print("=" * 50)
        
        # Run synchronous tests first
        self.test_configuration()
        self.test_imports()
        await self.test_celery_integration()
        
        # Run async API tests
        await self.test_health_endpoints()
        await self.test_api_endpoints()
        await self.test_blog_endpoints()
        
        # Print summary
        print("\n" + "=" * 50)
        print("📊 TEST SUMMARY")
        print("=" * 50)
        print(f"Total Tests: {self.results['summary']['total']}")
        print(f"✅ Passed: {self.results['summary']['passed']}")
        print(f"⚠️  Warnings: {self.results['summary']['warnings']}")
        print(f"❌ Failed: {self.results['summary']['failed']}")
        
        success_rate = (self.results['summary']['passed'] / self.results['summary']['total']) * 100
        print(f"Success Rate: {success_rate:.1f}%")
        
        # Show failed tests
        if self.results['summary']['failed'] > 0:
            print("\n❌ FAILED TESTS:")
            for test_name, result in self.results['tests'].items():
                if result['status'] == 'FAIL':
                    print(f"  - {test_name}: {result['message']}")
        
        # Show warnings
        if self.results['summary']['warnings'] > 0:
            print("\n⚠️  WARNINGS:")
            for test_name, result in self.results['tests'].items():
                if result['status'] == 'WARN':
                    print(f"  - {test_name}: {result['message']}")
        
        return self.results

async def main():
    """Main test runner"""
    import argparse
    
    parser = argparse.ArgumentParser(description='AdCopySurge System Tester')
    parser.add_argument('--url', default='http://localhost:8000', 
                       help='Base URL to test (default: http://localhost:8000)')
    parser.add_argument('--output', help='Save results to JSON file')
    
    args = parser.parse_args()
    
    async with AdCopySurgeSystemTester(args.url) as tester:
        results = await tester.run_all_tests()
        
        if args.output:
            with open(args.output, 'w') as f:
                json.dump(results, f, indent=2)
            print(f"\n💾 Results saved to: {args.output}")
        
        # Exit with appropriate code
        if results['summary']['failed'] > 0:
            print("\n❌ Some tests failed. Please review and fix issues before deployment.")
            sys.exit(1)
        elif results['summary']['warnings'] > 0:
            print("\n⚠️  Some tests have warnings. Review before production deployment.")
            sys.exit(0)
        else:
            print("\n✅ All tests passed! System ready for deployment.")
            sys.exit(0)

if __name__ == "__main__":
    asyncio.run(main())