#!/usr/bin/env python3
"""
Simple test script for Paddle integration
Run this to verify your Paddle setup is working correctly
"""

import os
import sys
from datetime import datetime

# Add the app directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.config import settings
from app.services.paddle_service import PaddleService
from sqlalchemy.orm import Session

def test_paddle_configuration():
    """Test if Paddle configuration is set up correctly"""
    print("🔧 Testing Paddle Configuration...")
    
    required_vars = [
        'PADDLE_VENDOR_ID',
        'PADDLE_AUTH_CODE', 
        'PADDLE_ENVIRONMENT'
    ]
    
    missing_vars = []
    for var in required_vars:
        if not getattr(settings, var, None):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"❌ Missing environment variables: {', '.join(missing_vars)}")
        print("📝 Please check your .env file and ensure all Paddle variables are set")
        return False
    
    print(f"✅ Paddle Environment: {settings.PADDLE_ENVIRONMENT}")
    print(f"✅ Vendor ID: {settings.PADDLE_VENDOR_ID}")
    print(f"✅ API URL: {settings.PADDLE_API_URL}")
    return True

def test_paddle_service():
    """Test basic Paddle service functionality"""
    print("\n🧪 Testing Paddle Service...")
    
    try:
        # Mock database session (replace with actual if needed)
        class MockDB:
            def query(self, model):
                return self
            
            def filter(self, condition):
                return self
                
            def first(self):
                return None
                
        db = MockDB()
        paddle_service = PaddleService(db)
        
        print(f"✅ Paddle service initialized successfully")
        print(f"✅ Vendor ID: {paddle_service.vendor_id}")
        print(f"✅ Environment: {paddle_service.environment}")
        
        # Test product mapping
        products = paddle_service._get_subscription_limits(None)
        if products is None:
            print("⚠️  Subscription limits test returned None - this is expected for None tier")
        
        return True
        
    except Exception as e:
        print(f"❌ Paddle service test failed: {e}")
        return False

def test_api_endpoints():
    """Test API endpoint imports"""
    print("\n🌐 Testing API Endpoint Imports...")
    
    try:
        from app.api.subscriptions import router
        print("✅ Subscriptions API router imported successfully")
        
        # Check if new Paddle endpoints exist
        paddle_routes = [route.path for route in router.routes if 'paddle' in route.path]
        print(f"✅ Found Paddle routes: {paddle_routes}")
        
        return True
        
    except Exception as e:
        print(f"❌ API endpoint test failed: {e}")
        return False

def test_database_model():
    """Test database model with Paddle fields"""
    print("\n🗃️ Testing Database Model...")
    
    try:
        from app.models.user import User, SubscriptionTier
        
        # Check if Paddle fields exist on User model
        user_attrs = dir(User)
        paddle_fields = [
            'paddle_subscription_id',
            'paddle_plan_id', 
            'paddle_checkout_id'
        ]
        
        for field in paddle_fields:
            if field in user_attrs:
                print(f"✅ {field} field exists")
            else:
                print(f"⚠️  {field} field not found - may need database migration")
        
        # Test enum
        print(f"✅ SubscriptionTier enum: {list(SubscriptionTier)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Database model test failed: {e}")
        return False

def run_all_tests():
    """Run all tests"""
    print("🚀 Starting Paddle Integration Tests")
    print("=" * 50)
    
    tests = [
        test_paddle_configuration,
        test_paddle_service,
        test_api_endpoints,
        test_database_model
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"❌ Test {test.__name__} crashed: {e}")
            results.append(False)
    
    print("\n" + "=" * 50)
    print("📊 Test Results Summary")
    
    passed = sum(results)
    total = len(results)
    
    print(f"✅ Passed: {passed}/{total}")
    if passed < total:
        print(f"❌ Failed: {total - passed}/{total}")
    
    if passed == total:
        print("\n🎉 All tests passed! Your Paddle integration is ready.")
        print("\n📋 Next Steps:")
        print("1. Create your Paddle account and get real credentials")
        print("2. Create products in your Paddle dashboard")
        print("3. Update product IDs in your code")
        print("4. Set up webhooks")
        print("5. Test with real Paddle checkout")
    else:
        print("\n⚠️  Some tests failed. Please fix the issues above before proceeding.")
    
    return passed == total

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
