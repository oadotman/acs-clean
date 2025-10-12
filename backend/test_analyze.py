#!/usr/bin/env python3
import requests
import json

def test_analyze_endpoint():
    print("🧪 Testing /ads/analyze endpoint...")
    
    data = {
        'ad': {
            'headline': 'Test Ad',
            'body_text': 'This is a test ad for checking the backend',
            'platform': 'facebook',
            'cta': 'Click here'
        },
        'user_id': 'test-user-123'
    }
    
    try:
        response = requests.post(
            'http://localhost:8000/api/ads/analyze',
            json=data,
            timeout=30,
            headers={'Content-Type': 'application/json'}
        )
        
        print(f"📊 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Success! Response keys: {list(result.keys())}")
            if 'scores' in result:
                print(f"📈 Scores: {result['scores']}")
            if 'alternatives' in result:
                print(f"🔄 Alternatives count: {len(result.get('alternatives', []))}")
            print(f"📝 Full response: {json.dumps(result, indent=2)}")
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"📝 Response: {response.text}")
            
    except requests.exceptions.Timeout:
        print("⏰ Request timed out - backend might be processing")
    except requests.exceptions.ConnectionError:
        print("🔌 Connection error - is backend running on localhost:8000?")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

if __name__ == "__main__":
    test_analyze_endpoint()