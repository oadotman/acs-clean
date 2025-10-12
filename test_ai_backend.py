#!/usr/bin/env python3
"""
Test script for AI-powered AdCopySurge backend API
Tests both with and without OpenAI API key
"""
import asyncio
import requests
import json
import os
import sys

# Test data
TEST_AD_COPY = "Boost your sales with our amazing CRM software. Easy to use, proven results. Start today!"
TEST_PLATFORM = "facebook"

def test_api_endpoint(url, method="GET", data=None):
    """Test an API endpoint"""
    try:
        print(f"\n🔍 Testing {method} {url}")
        
        if method == "GET":
            response = requests.get(url, timeout=10)
        elif method == "POST":
            response = requests.post(
                url, 
                json=data, 
                headers={"Content-Type": "application/json"},
                timeout=30
            )
        
        print(f"✅ Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Response received: {len(str(result))} chars")
            
            # Check for AI indicators
            if isinstance(result, dict):
                if result.get('ai_powered'):
                    print("🤖 AI-powered analysis detected!")
                if result.get('evidence_level') == 'high':
                    print("📊 High evidence level detected!")
                if 'AI-optimized' in str(result):
                    print("⚡ AI optimization detected!")
                    
            return result
        else:
            print(f"❌ Error: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Exception: {e}")
        return None

def main():
    """Run all tests"""
    print("🚀 AdCopySurge AI Backend Test Suite")
    print("=" * 50)
    
    # Check environment
    api_key = os.getenv('OPENAI_API_KEY', '')
    if api_key and api_key.startswith('sk-'):
        print(f"✅ OpenAI API Key configured: {api_key[:7]}...{api_key[-4:]}")
    else:
        print("⚠️ OpenAI API Key not configured - will test fallback mode")
    
    base_url = "http://localhost:8000"
    
    # Test basic endpoints
    print("\n📡 Testing basic endpoints:")
    test_api_endpoint(f"{base_url}/")
    test_api_endpoint(f"{base_url}/health")
    test_api_endpoint(f"{base_url}/api/test")
    test_api_endpoint(f"{base_url}/api/blog/categories")
    
    # Test comprehensive analysis
    print("\n🧠 Testing comprehensive analysis:")
    comprehensive_data = {
        "ad_copy": TEST_AD_COPY,
        "platform": TEST_PLATFORM
    }
    
    result = test_api_endpoint(
        f"{base_url}/api/ads/comprehensive-analyze",
        method="POST",
        data=comprehensive_data
    )
    
    if result:
        print("\n📋 Comprehensive Analysis Results:")
        print(f"  Original Score: {result.get('original', {}).get('score', 'N/A')}")
        print(f"  Improved Score: {result.get('improved', {}).get('score', 'N/A')}")
        print(f"  AI Powered: {result.get('ai_powered', False)}")
        print(f"  Evidence Level: {result.get('evidence_level', 'unknown')}")
        print(f"  Sample Size: {result.get('sample_size', 0)}")
        print(f"  Confidence: {result.get('confidence', 0)}")
        
        # Check improvements
        improvements = result.get('improved', {}).get('improvements', [])
        if improvements:
            print(f"  Improvements ({len(improvements)}):")
            for imp in improvements[:3]:  # Show first 3
                print(f"    - {imp.get('category', 'Unknown')}: {imp.get('description', 'No description')}")
        
        # Check alternatives
        alternatives = result.get('abTests', {}).get('variations', [])
        if alternatives:
            print(f"  Alternatives ({len(alternatives)}):")
            for alt in alternatives[:2]:  # Show first 2
                print(f"    - {alt.get('variant_type', 'unknown')}: {alt.get('improvement_reason', 'no reason')}")
    
    # Test regular analysis
    print("\n📊 Testing regular analysis:")
    regular_data = {
        "headline": "Boost Your Sales",
        "body_text": TEST_AD_COPY,
        "cta": "Start Today",
        "platform": TEST_PLATFORM
    }
    
    result = test_api_endpoint(
        f"{base_url}/api/ads/analyze",
        method="POST", 
        data=regular_data
    )
    
    if result:
        print("\n📋 Regular Analysis Results:")
        scores = result.get('scores', {})
        print(f"  Overall Score: {scores.get('overall_score', 'N/A')}")
        print(f"  Clarity Score: {scores.get('clarity_score', 'N/A')}")
        print(f"  Persuasion Score: {scores.get('persuasion_score', 'N/A')}")
        
        alternatives = result.get('alternatives', [])
        if alternatives:
            ai_alternatives = [alt for alt in alternatives if 'AI-optimized' in alt.get('improvement_reason', '')]
            template_alternatives = [alt for alt in alternatives if 'template-based' in alt.get('improvement_reason', '')]
            
            print(f"  AI Alternatives: {len(ai_alternatives)}")
            print(f"  Template Alternatives: {len(template_alternatives)}")
    
    # Summary
    print("\n🎯 Test Summary:")
    print("All tests completed. Check for:")
    print("✅ AI-powered analysis when OpenAI key is available")
    print("✅ Template fallback when OpenAI key is missing")
    print("✅ High evidence levels for AI analysis")
    print("✅ Low evidence levels for template analysis")
    print("\nIf OpenAI key is configured, you should see 'AI-optimized' messages.")
    print("If not configured, you should see 'template-based' messages.")

if __name__ == "__main__":
    main()