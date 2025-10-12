#!/usr/bin/env python3
"""
Health check script for AdCopySurge backend
Used by Docker health checks and monitoring systems
"""

import sys
import os
import requests
import time

def check_health():
    """Check if the application is healthy"""
    try:
        # Get the port from environment or use default
        port = os.getenv('PORT', '8000')
        host = os.getenv('HOST', '127.0.0.1')
        
        # Health check URL
        url = f"http://{host}:{port}/health"
        
        # Make request with timeout
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('status') == 'healthy':
                print("✅ Health check passed")
                return True
            else:
                print(f"❌ Health check failed: Invalid response {data}")
                return False
        else:
            print(f"❌ Health check failed: HTTP {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Health check failed: Connection refused")
        return False
    except requests.exceptions.Timeout:
        print("❌ Health check failed: Request timeout")
        return False
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return False

def main():
    """Main function"""
    print("🔍 Starting health check...")
    
    # Give the app some time to start up if needed
    if len(sys.argv) > 1 and sys.argv[1] == "--wait":
        print("⏳ Waiting 30 seconds for app startup...")
        time.sleep(30)
    
    # Perform health check
    if check_health():
        sys.exit(0)  # Success
    else:
        sys.exit(1)  # Failure

if __name__ == "__main__":
    main()
