#!/usr/bin/env python3
"""
Test script to verify blog service fixes and graceful degradation.
Run this after deploying the blog fixes to test the functionality.
"""

import sys
import requests
import json
from typing import Dict, Any

def test_blog_endpoints(base_url: str = "https://adcopysurge-backend.fly.dev") -> Dict[str, Any]:
    """Test blog endpoints and report status"""
    
    endpoints = {
        'categories': '/api/blog/categories',
        'popular': '/api/blog/popular?limit=5',
        'trending': '/api/blog/trending?limit=5', 
        'health': '/healthz'
    }
    
    results = {}
    
    for name, endpoint in endpoints.items():
        try:
            response = requests.get(f"{base_url}{endpoint}", timeout=30)
            results[name] = {
                'status_code': response.status_code,
                'success': response.status_code == 200,
                'response_size': len(response.content),
                'has_data': len(response.json()) > 0 if response.status_code == 200 else False,
                'error': None
            }
            
            if name == 'health' and response.status_code == 200:
                health_data = response.json()
                results[name]['blog_service_status'] = health_data.get('checks', {}).get('blog_service', 'unknown')
                
        except requests.RequestException as e:
            results[name] = {
                'status_code': None,
                'success': False,
                'response_size': 0,
                'has_data': False,
                'error': str(e)
            }
        except Exception as e:
            results[name] = {
                'status_code': None,
                'success': False, 
                'response_size': 0,
                'has_data': False,
                'error': f"Unexpected error: {str(e)}"
            }
    
    return results

def print_test_results(results: Dict[str, Any]):
    """Print formatted test results"""
    
    print("🧪 BLOG SERVICE TEST RESULTS")
    print("=" * 50)
    
    all_passed = True
    
    for endpoint, result in results.items():
        status = "✅ PASS" if result['success'] else "❌ FAIL"
        print(f"\n{endpoint.upper()}: {status}")
        print(f"  Status Code: {result['status_code']}")
        print(f"  Response Size: {result['response_size']} bytes")
        print(f"  Has Data: {result['has_data']}")
        
        if endpoint == 'health' and 'blog_service_status' in result:
            print(f"  Blog Service: {result['blog_service_status']}")
        
        if result['error']:
            print(f"  Error: {result['error']}")
            
        if not result['success']:
            all_passed = False
    
    print("\n" + "=" * 50)
    if all_passed:
        print("🎉 ALL TESTS PASSED - Blog service is working!")
        print("✨ The graceful degradation fixes have resolved the 502 errors.")
    else:
        print("⚠️  SOME TESTS FAILED - Check the errors above")
        print("💡 If endpoints return empty data (status 200 but no content),")
        print("   this indicates graceful degradation is working correctly.")
        
    return all_passed

def main():
    """Main test execution"""
    
    base_url = sys.argv[1] if len(sys.argv) > 1 else "https://adcopysurge-backend.fly.dev"
    
    print(f"🚀 Testing blog endpoints at: {base_url}")
    print("⏱️  This may take a moment...")
    
    try:
        results = test_blog_endpoints(base_url)
        success = print_test_results(results)
        
        # Exit code for CI/automation
        sys.exit(0 if success else 1)
        
    except KeyboardInterrupt:
        print("\n❌ Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Test failed with unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()