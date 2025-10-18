#!/usr/bin/env python3
"""
Simple test script to debug the API 500 error
"""
import requests
import json
import traceback

def test_api_endpoint():
    """Test the /api/ads/improve endpoint"""
    url = "http://localhost:8000/api/ads/improve"
    
    test_data = {
        "ad_copy": "Check out our amazing new product! It will change your life.",
        "platform": "facebook"
    }
    
    print("🧪 Testing API endpoint...")
    print(f"URL: {url}")
    print(f"Data: {json.dumps(test_data, indent=2)}")
    
    try:
        response = requests.post(
            url,
            json=test_data,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        print(f"\n📊 Response Status: {response.status_code}")
        print(f"📊 Response Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            print("✅ Success!")
            result = response.json()
            print(f"Result: {json.dumps(result, indent=2)}")
        else:
            print("❌ Error!")
            print(f"Error Text: {response.text}")
            try:
                error_json = response.json()
                print(f"Error JSON: {json.dumps(error_json, indent=2)}")
            except:
                print("Could not parse error as JSON")
        
        return response.status_code == 200
        
    except requests.exceptions.RequestException as e:
        print(f"💥 Request Exception: {e}")
        return False
    except Exception as e:
        print(f"💥 General Exception: {e}")
        traceback.print_exc()
        return False

def test_health_endpoint():
    """Test the /health endpoint first"""
    url = "http://localhost:8000/health"
    
    print("🏥 Testing health endpoint...")
    
    try:
        response = requests.get(url, timeout=10)
        print(f"Health Status: {response.status_code}")
        if response.status_code == 200:
            print(f"Health Response: {response.json()}")
            return True
        else:
            print(f"Health Error: {response.text}")
            return False
    except Exception as e:
        print(f"💥 Health check failed: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Starting API Debug Test\n")
    
    # Test health first
    if test_health_endpoint():
        print("\n" + "="*50)
        # Test the improve endpoint
        success = test_api_endpoint()
        
        if success:
            print("\n🎉 API test completed successfully!")
        else:
            print("\n💥 API test failed!")
    else:
        print("\n💥 Health check failed - server may not be running")