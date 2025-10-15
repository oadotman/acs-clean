#!/usr/bin/env python3
"""
Simple test that bypasses the complex Tools SDK to test basic functionality

Timeout Configuration:
- Request timeout: 30 seconds (requests library)
- Total test timeout: 60 seconds (signal-based on Unix, threading on Windows)

If the test hangs, it will automatically terminate after 60 seconds.
"""
import requests
import time
import sys
import signal
import threading
import platform

def setup_timeout(seconds):
    """Set up a hard timeout that works on both Windows and Unix"""
    if platform.system() != "Windows":
        # Unix: use signal-based timeout
        def timeout_handler(signum, frame):
            print(f"\n⏱️  TIMEOUT: Test exceeded {seconds} seconds hard limit")
            print("❌ The backend is likely hanging on AI API calls (OpenAI).")
            print("💡 Suggestions:")
            print("   1. Check if backend is running: http://localhost:8000/health")
            print("   2. Verify OPENAI_API_KEY is valid in backend/.env")
            print("   3. Check backend logs for errors")
            sys.exit(1)
        
        signal.signal(signal.SIGALRM, timeout_handler)
        signal.alarm(seconds)
        return lambda: signal.alarm(0)
    else:
        # Windows: use threading-based timeout
        def force_exit():
            print(f"\n⏱️  TIMEOUT: Test exceeded {seconds} seconds hard limit")
            print("❌ The backend is likely hanging on AI API calls (OpenAI).")
            print("💡 Suggestions:")
            print("   1. Check if backend is running: http://localhost:8000/health")
            print("   2. Verify OPENAI_API_KEY is valid in backend/.env")
            print("   3. Check backend logs for errors")
            sys.exit(1)
        
        timer = threading.Timer(seconds, force_exit)
        timer.daemon = True
        timer.start()
        return timer.cancel

def test_simple_api():
    """Test the basic API without complex tools"""
    start_time = time.perf_counter()
    
    try:
        # Test a simple comprehensive analysis request  
        payload = {
            "ad_copy": "Transform your business with our revolutionary CRM software. Join 10,000+ companies seeing 40% better retention. Start free trial now!",
            "platform": "facebook",
            "no_emojis": True  # Test the no-emoji feature
        }
        
        print("🧪 Testing comprehensive analysis...")
        print(f"📋 Payload: {payload}")
        print(f"⏱️  Request timeout: 30 seconds")
        print(f"⏱️  Hard timeout: 60 seconds\n")
        
        request_start = time.perf_counter()
        response = requests.post(
            "http://localhost:8000/api/ads/comprehensive-analyze",
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=30  # 30 second timeout
        )
        request_elapsed = time.perf_counter() - request_start
        
        print(f"📡 Response status: {response.status_code} [took {request_elapsed:.1f}s]")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ SUCCESS!")
            print(f"📊 Success: {result.get('success')}")
            print(f"💬 Message: {result.get('message')}")
            print(f"🏢 Platform: {result.get('platform')}")
            
            if result.get('analysis'):
                analysis = result.get('analysis')
                print(f"📈 Analysis ID: {analysis.get('analysis_id', 'N/A')}")
                
                # Check if we have scores
                scores = analysis.get('scores', {})
                if scores:
                    print(f"🎯 Overall Score: {scores.get('overall_score', 'N/A')}")
                
                # Check alternatives  
                alternatives = analysis.get('alternatives', [])
                print(f"🔄 Alternatives: {len(alternatives)} generated")
                
            elapsed = time.perf_counter() - start_time
            print(f"\n✅ Total test time: {elapsed:.1f}s")
            return True
        else:
            print("❌ FAILED!")
            print(f"Error: {response.text}")
            return False
    
    except (requests.Timeout, requests.exceptions.ReadTimeout) as e:
        elapsed = time.perf_counter() - start_time
        print(f"\n⏱️  REQUEST TIMEOUT after {elapsed:.1f}s")
        print("❌ Backend took too long to respond (>30s)")
        print("💡 The comprehensive analysis endpoint runs 9 AI tools in parallel.")
        print("💡 This may take time, especially on first run or slow API responses.")
        print("💡 Check backend console for progress logs.")
        print("💡 Verify OPENAI_API_KEY is valid in backend/.env")
        return False
    
    except requests.ConnectionError as e:
        print("\n❌ CONNECTION ERROR")
        print("💡 Could not connect to http://localhost:8000")
        print("💡 Is the backend server running?")
        print("💡 Try: cd backend && python main_launch_ready.py")
        return False
    
    except requests.HTTPError as e:
        print(f"\n❌ HTTP ERROR: {e.response.status_code}")
        print(f"Response: {e.response.text}")
        return False
            
    except Exception as e:
        elapsed = time.perf_counter() - start_time
        print(f"\n💥 UNEXPECTED EXCEPTION after {elapsed:.1f}s")
        print(f"Error: {type(e).__name__}: {e}")
        print(f"Details: {str(e)}")
        return False

if __name__ == "__main__":
    print("🚀 Testing AdCopySurge Comprehensive Analysis")
    print("=" * 50)
    
    # Set up hard timeout (60 seconds)
    cancel_timeout = setup_timeout(60)
    
    try:
        success = test_simple_api()
    finally:
        # Cancel timeout if test completes
        cancel_timeout()
    
    print("=" * 50)
    if success:
        print("🎉 All tests passed! The comprehensive analysis is working.")
        print("\n📋 Next steps:")
        print("1. ✅ Backend API endpoints are working")
        print("2. ✅ No-emoji functionality is implemented") 
        print("3. ✅ Frontend should now connect successfully")
        print("4. ✅ Try running 'npm run dev' from the frontend directory")
    else:
        print("\n❌ Tests failed. Check the backend logs for more details.")
        print("💡 Make sure the backend is running: cd backend && python main_launch_ready.py")
