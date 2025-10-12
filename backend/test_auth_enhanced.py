#!/usr/bin/env python3
"""
Test script for enhanced Supabase authentication middleware
Tests various authentication scenarios and configurations
"""

import asyncio
import httpx
import json
import os
import sys
from typing import Dict, Any, Optional

# Test endpoints
BASE_URL = "http://localhost:8000"
ENDPOINTS = {
    "auth_status": f"{BASE_URL}/api/auth/status",
    "auth_user": f"{BASE_URL}/api/auth/user", 
    "auth_test": f"{BASE_URL}/api/auth/test",
    "auth_health": f"{BASE_URL}/api/auth/health",
    "health": f"{BASE_URL}/health"
}

class AuthTester:
    def __init__(self, base_url: str = BASE_URL):
        self.base_url = base_url
        self.client = httpx.AsyncClient(timeout=30.0)
        
    async def close(self):
        await self.client.aclose()
    
    async def test_endpoint(self, name: str, url: str, method: str = "GET", 
                           headers: Optional[Dict] = None, 
                           json_data: Optional[Dict] = None) -> Dict[str, Any]:
        """Test a single endpoint"""
        try:
            if method.upper() == "POST":
                response = await self.client.post(url, headers=headers or {}, json=json_data)
            else:
                response = await self.client.get(url, headers=headers or {})
            
            return {
                "name": name,
                "url": url,
                "status_code": response.status_code,
                "success": response.status_code < 400,
                "headers": dict(response.headers),
                "data": response.json() if response.headers.get("content-type", "").startswith("application/json") else response.text
            }
        except Exception as e:
            return {
                "name": name,
                "url": url,
                "status_code": 0,
                "success": False,
                "error": str(e),
                "data": None
            }
    
    async def test_all_endpoints(self, bearer_token: Optional[str] = None) -> Dict[str, Any]:
        """Test all authentication endpoints"""
        headers = {}
        if bearer_token:
            headers["Authorization"] = f"Bearer {bearer_token}"
        
        results = {}
        
        # Test auth status (should always work)
        results["auth_status"] = await self.test_endpoint("Auth Status", ENDPOINTS["auth_status"])
        
        # Test auth user info
        results["auth_user"] = await self.test_endpoint("Auth User", ENDPOINTS["auth_user"], headers=headers)
        
        # Test auth functionality
        results["auth_test"] = await self.test_endpoint("Auth Test", ENDPOINTS["auth_test"], "POST", headers=headers)
        
        # Test auth health
        results["auth_health"] = await self.test_endpoint("Auth Health", ENDPOINTS["auth_health"])
        
        # Test main health (should include auth status)
        results["main_health"] = await self.test_endpoint("Main Health", ENDPOINTS["health"])
        
        return results
    
    def print_results(self, results: Dict[str, Any], title: str = "Test Results"):
        """Print test results in a readable format"""
        print(f"\n{'='*60}")
        print(f"{title:^60}")
        print(f"{'='*60}")
        
        for endpoint_name, result in results.items():
            success_icon = "✅" if result["success"] else "❌"
            status_code = result.get("status_code", 0)
            
            print(f"\n{success_icon} {result['name']} ({status_code})")
            print(f"   URL: {result['url']}")
            
            if "error" in result:
                print(f"   Error: {result['error']}")
            elif result["data"]:
                # Print key information from response
                data = result["data"]
                if isinstance(data, dict):
                    if "status" in data:
                        print(f"   Status: {data['status']}")
                    if "authentication_system" in data:
                        print(f"   Auth System: {data['authentication_system']}")
                    if "available_auth_methods" in data:
                        print(f"   Available Methods: {', '.join(data['available_auth_methods'])}")
                    if "supabase_configured" in data:
                        print(f"   Supabase Configured: {data['supabase_configured']}")
                    if "allow_anonymous" in data:
                        print(f"   Allow Anonymous: {data['allow_anonymous']}")
                    if "authenticated" in data:
                        print(f"   Authenticated: {data['authenticated']}")
                        if data.get("user"):
                            user = data["user"]
                            print(f"   User: {user.get('email', 'N/A')} ({user.get('id', 'N/A')})")
                    if "checks" in data:
                        print(f"   Checks Passed: {sum(1 for check in data['checks'].values() if isinstance(check, dict) and check.get('status') in ['healthy', True])}/{len(data['checks'])}")

async def test_basic_scenario():
    """Test basic authentication scenarios"""
    tester = AuthTester()
    
    try:
        # Test without authentication
        print("Testing WITHOUT authentication...")
        results_no_auth = await tester.test_all_endpoints()
        tester.print_results(results_no_auth, "WITHOUT Authentication")
        
        # Test with dummy bearer token 
        print("\n" + "="*60)
        print("Testing WITH dummy bearer token...")
        results_with_auth = await tester.test_all_endpoints("dummy_token_for_testing")
        tester.print_results(results_with_auth, "WITH Dummy Bearer Token")
        
        # Configuration summary
        print(f"\n{'='*60}")
        print("CONFIGURATION SUMMARY")
        print(f"{'='*60}")
        
        auth_status = results_no_auth.get("auth_status", {}).get("data", {})
        if auth_status:
            print(f"Authentication System: {auth_status.get('authentication_system', 'unknown')}")
            print(f"Version: {auth_status.get('version', 'unknown')}")
            print(f"Supabase Configured: {auth_status.get('supabase_configured', False)}")
            print(f"Allow Anonymous: {auth_status.get('allow_anonymous', False)}")
            print(f"Available Methods: {', '.join(auth_status.get('available_auth_methods', []))}")
            
            if auth_status.get('supabase_url'):
                print(f"Supabase URL: {auth_status['supabase_url']}")
            if auth_status.get('has_anon_key'):
                print(f"Has Anon Key: {auth_status['has_anon_key']}")
            if auth_status.get('has_jwt_secret'):
                print(f"Has JWT Secret: {auth_status['has_jwt_secret']}")
        
        # Health check summary
        health_data = results_no_auth.get("main_health", {}).get("data", {})
        if health_data:
            print(f"\nOverall Health: {health_data.get('status', 'unknown')}")
            auth_check = health_data.get('checks', {}).get('authentication', {})
            if auth_check:
                print(f"Auth Health: {auth_check.get('status', 'unknown')} - {auth_check.get('message', 'N/A')}")
        
        return results_no_auth, results_with_auth
        
    finally:
        await tester.close()

def check_environment():
    """Check environment configuration"""
    print("Environment Configuration:")
    print("-" * 40)
    
    supabase_vars = [
        "SUPABASE_URL", "REACT_APP_SUPABASE_URL",
        "SUPABASE_ANON_KEY", "REACT_APP_SUPABASE_ANON_KEY", 
        "SUPABASE_SERVICE_ROLE_KEY", "SUPABASE_JWT_SECRET",
        "ALLOW_ANON"
    ]
    
    for var in supabase_vars:
        value = os.getenv(var)
        if value:
            if "KEY" in var or "SECRET" in var:
                display_value = f"{value[:10]}..." if len(value) > 10 else value
            else:
                display_value = value
            print(f"✅ {var}: {display_value}")
        else:
            print(f"❌ {var}: Not set")

async def main():
    """Main test function"""
    print("Enhanced Supabase Authentication Test Suite")
    print("=" * 60)
    
    # Check environment
    check_environment()
    
    # Run tests
    try:
        await test_basic_scenario()
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
    except Exception as e:
        print(f"\n\nTest failed with error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    if len(sys.argv) > 1:
        BASE_URL = sys.argv[1]
        ENDPOINTS = {k: v.replace("http://localhost:8000", BASE_URL) for k, v in ENDPOINTS.items()}
        print(f"Using custom base URL: {BASE_URL}")
    
    asyncio.run(main())