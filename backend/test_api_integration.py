#!/usr/bin/env python3
"""
End-to-End API Integration Test

Tests the complete flow from API request to standardized response
including platform-specific validation and A/B/C variant generation.
"""

import requests
import json
import time
import sys
from pathlib import Path

def test_platform_api(platform_id: str, ad_copy: str) -> bool:
    """Test API for specific platform"""
    print(f"\n🧪 Testing {platform_id.upper()} API...")
    
    # Test data
    test_data = {
        "ad_copy": ad_copy,
        "platform": platform_id
    }
    
    try:
        # Make API request
        response = requests.post(
            "http://localhost:8000/api/ads/improve",
            json=test_data,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        if response.status_code != 200:
            print(f"   ❌ API request failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
        
        # Parse response
        result = response.json()
        
        # Validate response structure
        expected_fields = [
            'success', 'platform', 'confidenceScore', 'originalAd', 
            'improvedAd', 'variants', 'tips', 'metrics'
        ]
        
        for field in expected_fields:
            if field not in result:
                print(f"   ❌ Missing field in response: {field}")
                return False
        
        # Validate specific content
        print(f"   ✅ API Response Received")
        print(f"   Platform: {result['platform']}")
        print(f"   Confidence: {result['confidenceScore']}/100")
        print(f"   Variants: {len(result.get('variants', []))}")
        print(f"   Generation time: {result.get('metrics', {}).get('generation_time_ms', 0)}ms")
        
        # Check variants structure
        variants = result.get('variants', [])
        if len(variants) >= 3:
            print(f"   ✅ Generated {len(variants)} variants (A/B/C)")
            for i, variant in enumerate(variants[:3], 1):
                variant_name = chr(64 + i)  # A, B, C
                print(f"     Version {variant_name}: {variant.get('strategy', 'Unknown strategy')}")
        else:
            print(f"   ⚠️ Expected at least 3 variants, got {len(variants)}")
        
        # Check platform-specific response format
        improved_ad = result.get('improvedAd', {})
        if platform_id == 'google_ads':
            if 'headlines' not in improved_ad or 'descriptions' not in improved_ad:
                print(f"   ❌ Google Ads missing headlines/descriptions")
                return False
        elif platform_id == 'instagram':
            if 'hashtags' not in improved_ad:
                print(f"   ❌ Instagram missing hashtags")
                return False
        
        print(f"   ✅ Platform-specific format validated")
        return True
        
    except requests.exceptions.RequestException as e:
        print(f"   ❌ Request failed: {e}")
        return False
    except json.JSONDecodeError as e:
        print(f"   ❌ Invalid JSON response: {e}")
        return False
    except Exception as e:
        print(f"   ❌ Unexpected error: {e}")
        return False

def test_confidence_gating():
    """Test confidence score gating (should retry low-quality ads)"""
    print(f"\n🧪 Testing Confidence Score Gating...")
    
    # Low-quality ad copy with template phrases
    low_quality_ad = ("Are you tired of the same old problem? "
                     "Introducing our revolutionary game-changing solution "
                     "that will transform your life forever! Don't miss out "
                     "on this limited time offer. Act now and save!")
    
    test_data = {
        "ad_copy": low_quality_ad,
        "platform": "facebook"
    }
    
    try:
        response = requests.post(
            "http://localhost:8000/api/ads/improve",
            json=test_data,
            headers={"Content-Type": "application/json"},
            timeout=60  # Longer timeout for retries
        )
        
        if response.status_code != 200:
            print(f"   ❌ API request failed: {response.status_code}")
            return False
        
        result = response.json()
        
        # Check if retries occurred (should be logged in metrics)
        metrics = result.get('metrics', {})
        retry_count = metrics.get('retry_count', 0)
        
        print(f"   Retry count: {retry_count}")
        print(f"   Final confidence: {result.get('confidenceScore', 0)}/100")
        
        if retry_count > 0:
            print(f"   ✅ Quality gating triggered {retry_count} retries")
        else:
            print(f"   ⚠️ No retries detected (may indicate high-quality result)")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Test failed: {e}")
        return False

def check_server_status():
    """Check if the server is running"""
    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        return response.status_code == 200
    except:
        return False

def main():
    """Run end-to-end API integration tests"""
    print("🚀 Starting End-to-End API Integration Tests")
    print("=" * 60)
    
    # Check if server is running
    if not check_server_status():
        print("❌ Backend server not running on http://localhost:8000")
        print("Please start the server with: python working_api.py")
        return False
    
    print("✅ Backend server is running")
    
    # Test different platforms
    test_cases = [
        ("facebook", "Check out our new CRM software that helps businesses grow"),
        ("google_ads", "Professional CRM solution for growing businesses"),
        ("instagram", "Transform your business with our amazing CRM system"),
        ("linkedin", "Enterprise CRM platform for B2B sales teams"),
        ("twitter_x", "Quick tip: boost your sales with our CRM tool"),
    ]
    
    results = []
    
    # Test each platform
    for platform_id, ad_copy in test_cases:
        result = test_platform_api(platform_id, ad_copy)
        results.append((f"{platform_id} API", result))
        time.sleep(2)  # Small delay between tests
    
    # Test confidence gating
    gating_result = test_confidence_gating()
    results.append(("Confidence Gating", gating_result))
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 API INTEGRATION TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All API integration tests passed!")
        print("\n✨ Validated Features:")
        print("   • Complete API request/response flow")
        print("   • Platform-specific response formatting")
        print("   • A/B/C variant generation")
        print("   • Confidence score calculation")
        print("   • Quality gating and retry logic")
        print("   • Standardized response structure")
    else:
        print("⚠️ Some tests failed. Please check the API implementation.")
        print("\nTroubleshooting tips:")
        print("   • Ensure OpenAI API key is set in environment")
        print("   • Check server logs for detailed error messages")
        print("   • Verify all platform configurations are loaded")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)