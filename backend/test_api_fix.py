#!/usr/bin/env python3
"""
Test script to verify the fixed /api/ads/improve endpoint
Ensures the response format matches frontend expectations
"""

import requests
import json
import sys
import time

def test_api_endpoint():
    """Test the fixed API endpoint"""
    print("=== TESTING FIXED /api/ads/improve ENDPOINT ===")
    
    # Test data
    test_data = {
        "ad_copy": "Get 50% off all products today! Limited time offer - shop now and save big.",
        "platform": "facebook"
    }
    
    url = "http://127.0.0.1:8000/api/ads/improve"
    
    try:
        print(f"🔍 Testing: {url}")
        print(f"📤 Request data: {json.dumps(test_data, indent=2)}")
        
        response = requests.post(url, json=test_data, timeout=60)
        print(f"📋 Response status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Response received!")
            
            # Test frontend contract requirements
            print("\n=== FRONTEND CONTRACT VALIDATION ===")
            
            checks = [
                ("analysis_id", "analysis_id" in data),
                ("original field", "original" in data),
                ("improved field", "improved" in data), 
                ("abTests field", "abTests" in data),
                ("abc_variants", "abTests" in data and "abc_variants" in data["abTests"]),
                ("3 variants", "abTests" in data and len(data.get("abTests", {}).get("abc_variants", [])) == 3),
                ("variants have IDs", all(
                    "id" in variant for variant in data.get("abTests", {}).get("abc_variants", [])
                ))
            ]
            
            all_passed = True
            for check_name, result in checks:
                status = "✅ PASS" if result else "❌ FAIL"
                print(f"  {status}: {check_name}")
                if not result:
                    all_passed = False
            
            if all_passed:
                print("\n🎉 ALL FRONTEND VALIDATION CHECKS PASSED!")
            else:
                print("\n⚠️ Some validation checks failed")
            
            # Show variant details
            print("\n=== VARIANT DETAILS ===")
            variants = data.get("abTests", {}).get("abc_variants", [])
            for i, variant in enumerate(variants):
                print(f"Variant {i+1}: {variant.get('version')} - {variant.get('name')}")
                print(f"  ID: {variant.get('id')}")
                print(f"  Headline: '{variant.get('headline', 'Missing')}'")
                print(f"  Body: '{variant.get('body', 'Missing')}'")
                print(f"  CTA: '{variant.get('cta', 'Missing')}'")
                print()
            
            # Show full response structure for debugging
            print("=== FULL RESPONSE (first 1000 chars) ===")
            response_str = json.dumps(data, indent=2)
            print(response_str[:1000] + ("..." if len(response_str) > 1000 else ""))
            
        else:
            print(f"❌ Request failed with status {response.status_code}")
            print(f"❌ Response: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection failed - is the backend server running?")
        print("   Start it with: python working_api.py")
    except requests.exceptions.Timeout:
        print("❌ Request timed out after 60 seconds")
    except Exception as e:
        print(f"❌ Test failed: {e}")

if __name__ == "__main__":
    test_api_endpoint()