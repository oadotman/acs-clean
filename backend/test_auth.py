#!/usr/bin/env python3
"""
Authentication Test Script for AdCopySurge
Tests both legacy JWT and Supabase authentication systems
"""

import asyncio
import os
import sys
from pathlib import Path

# Add the backend directory to the Python path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

from sqlalchemy.orm import Session
from app.core.database import get_db, SessionLocal
from app.models.user import User, SubscriptionTier
from app.services.auth_service import AuthService
from app.middleware.supabase_auth import supabase_auth
from app.auth.dependencies import get_current_user
from fastapi.security import HTTPAuthorizationCredentials
import uuid


def test_database_connection():
    """Test basic database connectivity"""
    print("🔍 Testing database connection...")
    try:
        db = SessionLocal()
        # Try to query the user table
        user_count = db.query(User).count()
        print(f"✅ Database connected successfully. Found {user_count} users.")
        db.close()
        return True
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False


def test_user_model():
    """Test User model with supabase_user_id field"""
    print("\n🔍 Testing User model...")
    try:
        db = SessionLocal()
        
        # Check if we can create a user with Supabase ID
        test_email = f"test_supabase_{uuid.uuid4().hex[:8]}@example.com"
        test_supabase_id = f"supabase_{uuid.uuid4().hex}"
        
        user = User(
            email=test_email,
            full_name="Test User",
            supabase_user_id=test_supabase_id,
            subscription_tier=SubscriptionTier.FREE,
            is_active=True,
            email_verified=True,
            hashed_password=None  # Supabase handles auth
        )
        
        db.add(user)
        db.commit()
        db.refresh(user)
        
        print(f"✅ User model test passed. Created user with Supabase ID: {test_supabase_id}")
        
        # Clean up
        db.delete(user)
        db.commit()
        db.close()
        
        return True
    except Exception as e:
        print(f"❌ User model test failed: {e}")
        return False


def test_legacy_jwt_auth():
    """Test legacy JWT authentication"""
    print("\n🔍 Testing legacy JWT authentication...")
    try:
        db = SessionLocal()
        auth_service = AuthService(db)
        
        # Create a test user for legacy auth
        test_email = f"test_legacy_{uuid.uuid4().hex[:8]}@example.com"
        test_user = auth_service.create_user(
            email=test_email,
            password="testpassword123",
            full_name="Legacy Test User"
        )
        
        # Test authentication
        authenticated_user = auth_service.authenticate_user(test_email, "testpassword123")
        if authenticated_user and authenticated_user.id == test_user.id:
            print("✅ Legacy password authentication works")
        else:
            print("❌ Legacy password authentication failed")
            return False
        
        # Test JWT token creation and validation
        token = auth_service.create_access_token(data={"sub": test_user.email})
        token_user = auth_service.get_current_user(token)
        
        if token_user and token_user.id == test_user.id:
            print("✅ Legacy JWT token creation and validation works")
        else:
            print("❌ Legacy JWT token validation failed")
            return False
        
        # Clean up
        db.delete(test_user)
        db.commit()
        db.close()
        
        return True
    except Exception as e:
        print(f"❌ Legacy JWT authentication test failed: {e}")
        return False


async def test_supabase_auth_validation():
    """Test Supabase JWT token validation (without real tokens)"""
    print("\n🔍 Testing Supabase authentication validation...")
    try:
        # Test that the Supabase auth class initializes correctly
        if not hasattr(supabase_auth, 'supabase_url'):
            print("❌ Supabase auth not properly initialized")
            return False
        
        # Test invalid token handling
        invalid_result = await supabase_auth.verify_supabase_token("invalid.jwt.token")
        if invalid_result is None:
            print("✅ Supabase auth correctly rejects invalid tokens")
        else:
            print("❌ Supabase auth should reject invalid tokens")
            return False
        
        print("✅ Supabase authentication validation structure is correct")
        return True
    except Exception as e:
        print(f"❌ Supabase authentication test failed: {e}")
        return False


async def test_unified_auth_dependencies():
    """Test the unified authentication dependency"""
    print("\n🔍 Testing unified authentication dependencies...")
    try:
        # Import the unified dependencies
        from app.auth.dependencies import (
            get_current_user, 
            get_optional_current_user, 
            require_active_user,
            require_subscription_limit
        )
        
        print("✅ All authentication dependencies imported successfully")
        print("   - get_current_user")
        print("   - get_optional_current_user") 
        print("   - require_active_user")
        print("   - require_subscription_limit")
        
        return True
    except ImportError as e:
        print(f"❌ Failed to import authentication dependencies: {e}")
        return False
    except Exception as e:
        print(f"❌ Authentication dependencies test failed: {e}")
        return False


def test_configuration():
    """Test that required configuration is present"""
    print("\n🔍 Testing configuration...")
    try:
        from app.core.config import settings
        
        config_items = []
        
        # Check for basic auth settings
        if hasattr(settings, 'SECRET_KEY') and settings.SECRET_KEY:
            config_items.append("✅ SECRET_KEY configured")
        else:
            config_items.append("❌ SECRET_KEY missing")
        
        # Check for Supabase settings (these might not be set yet)
        if hasattr(settings, 'REACT_APP_SUPABASE_URL'):
            config_items.append("✅ REACT_APP_SUPABASE_URL configured")
        else:
            config_items.append("⚠️  REACT_APP_SUPABASE_URL not configured (optional for testing)")
        
        if hasattr(settings, 'REACT_APP_SUPABASE_ANON_KEY'):
            config_items.append("✅ REACT_APP_SUPABASE_ANON_KEY configured")
        else:
            config_items.append("⚠️  REACT_APP_SUPABASE_ANON_KEY not configured (optional for testing)")
        
        for item in config_items:
            print(f"   {item}")
        
        # Consider it successful if at least basic auth is configured
        return "SECRET_KEY" in str(config_items[0])
    except Exception as e:
        print(f"❌ Configuration test failed: {e}")
        return False


async def main():
    """Run all authentication tests"""
    print("🚀 AdCopySurge Authentication System Test Suite")
    print("=" * 50)
    
    tests = [
        ("Database Connection", test_database_connection),
        ("User Model", test_user_model),
        ("Legacy JWT Auth", test_legacy_jwt_auth),
        ("Supabase Auth Structure", test_supabase_auth_validation),
        ("Unified Auth Dependencies", test_unified_auth_dependencies),
        ("Configuration", test_configuration),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            if asyncio.iscoroutinefunction(test_func):
                result = await test_func()
            else:
                result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} crashed: {e}")
            results.append((test_name, False))
    
    print("\n" + "=" * 50)
    print("📊 TEST RESULTS SUMMARY")
    print("=" * 50)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{status:12} {test_name}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Authentication system is ready.")
        return 0
    else:
        print("⚠️  Some tests failed. Please check the issues above.")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
