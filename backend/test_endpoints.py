#!/usr/bin/env python3
"""
Quick test script to verify our API endpoints work
"""
import requests
import json
import time
import sys
import subprocess
import threading

def start_server():
    """Start the server in a subprocess"""
    try:
        # Start server
        process = subprocess.Popen([
            sys.executable, "-m", "uvicorn", 
            "main_launch_ready:app", 
            "--port", "8000", 
            "--host", "127.0.0.1"
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Give server time to start
        time.sleep(5)
        return process
    except Exception as e:
        print(f"Failed to start server: {e}")
        return None

def test_endpoints():
    """Test our API endpoints"""
    base_url = "http://127.0.0.1:8000"
    
    # Test health endpoint
    try:
        response = requests.get(f"{base_url}/health")
        print(f"✅ Health check: {response.status_code} - {response.json()}")
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return False
    
    # Test root endpoint
    try:
        response = requests.get(base_url)
        print(f"✅ Root endpoint: {response.status_code} - {response.json()}")
    except Exception as e:
        print(f"❌ Root endpoint failed: {e}")
    
    # Test comprehensive analyze endpoint
    try:
        test_data = {
            "ad_copy": "Get 50% off all products today! Limited time offer - shop now and save big.",
            "platform": "facebook",
            "user_id": "test_user"
        }
        
        response = requests.post(f"{base_url}/api/ads/comprehensive-analyze", json=test_data)
        print(f"✅ Comprehensive analyze: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"   Original score: {result.get('original', {}).get('score', 'N/A')}")
            print(f"   Platform: {result.get('platform', 'N/A')}")
        else:
            print(f"   Error: {response.text}")
    except Exception as e:
        print(f"❌ Comprehensive analyze failed: {e}")
    
    # Test regular analyze endpoint
    try:
        test_data = {
            "headline": "Amazing Product Sale!",
            "body_text": "Get 50% off all products today! Limited time offer - shop now and save big.",
            "cta": "Shop Now",
            "platform": "facebook"
        }
        
        response = requests.post(f"{base_url}/api/ads/analyze", json=test_data)
        print(f"✅ Regular analyze: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"   Overall score: {result.get('scores', {}).get('overall_score', 'N/A')}")
        else:
            print(f"   Error: {response.text}")
    except Exception as e:
        print(f"❌ Regular analyze failed: {e}")
    
    return True

if __name__ == "__main__":
    print("🚀 Starting AdCopySurge API test...")
    
    # Start server
    server_process = start_server()
    if not server_process:
        print("❌ Failed to start server")
        sys.exit(1)
    
    try:
        # Test endpoints
        if test_endpoints():
            print("✅ All tests completed!")
        else:
            print("❌ Some tests failed")
    finally:
        # Clean up server
        if server_process:
            server_process.terminate()
            server_process.wait()
            print("🛑 Server stopped")