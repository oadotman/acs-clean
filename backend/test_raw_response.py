#!/usr/bin/env python3
"""
Test script to check raw JSON response and verify body content is present
"""

import requests
import json

def test_raw_response():
    """Test the raw API response"""
    
    url = "http://127.0.0.1:8000/api/ads/improve"
    data = {
        "ad_copy": "Get 50% off all products today! Limited time offer - shop now and save big.",
        "platform": "facebook"
    }
    
    try:
        response = requests.post(url, json=data, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            
            print("=== RAW API RESPONSE ANALYSIS ===")
            print(f"Success: {data.get('success')}")
            print(f"Platform: {data.get('platform')}")
            
            # Check variants structure
            variants = data.get("abTests", {}).get("abc_variants", [])
            print(f"\nFound {len(variants)} variants:")
            
            for i, variant in enumerate(variants):
                print(f"\n--- VARIANT {variant.get('version', i+1)} ---")
                print(f"ID: {variant.get('id')}")
                print(f"Name: {variant.get('name')}")
                print(f"Focus: {variant.get('focus')}")
                
                # Check all three components
                headline = variant.get('headline', '')
                body = variant.get('body', '')
                cta = variant.get('cta', '')
                
                print(f"\n📢 HEADLINE ({len(headline)} chars):")
                print(f"   '{headline}'")
                print(f"   Contains '50%': {'50%' in headline}")
                print(f"   Contains 'products': {'products' in headline.lower()}")
                
                print(f"\n📝 BODY ({len(body)} chars):")
                print(f"   '{body}'")
                print(f"   Has body content: {bool(body)}")
                print(f"   Body word count: {len(body.split()) if body else 0}")
                print(f"   Contains '50%': {'50%' in body}")
                print(f"   Contains 'products': {'products' in body.lower()}")
                print(f"   Contains 'limited time': {'limited time' in body.lower()}")
                
                print(f"\n🎯 CTA ({len(cta)} chars):")
                print(f"   '{cta}'")
                
                # Check for issues
                issues = []
                if not headline:
                    issues.append("Missing headline")
                if not body:
                    issues.append("Missing body")  
                if not cta:
                    issues.append("Missing CTA")
                if body and len(body.split()) < 10:
                    issues.append(f"Body too short ({len(body.split())} words)")
                
                if issues:
                    print(f"\n⚠️ ISSUES: {', '.join(issues)}")
                else:
                    print(f"\n✅ VARIANT COMPLETE")
            
            # Show raw JSON structure (first 2000 chars)
            print(f"\n=== RAW JSON (first 2000 chars) ===")
            json_str = json.dumps(data, indent=2)
            print(json_str[:2000] + ("..." if len(json_str) > 2000 else ""))
            
        else:
            print(f"❌ Request failed: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_raw_response()