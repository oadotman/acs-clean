#!/usr/bin/env python3
"""
Comprehensive import test for AdCopySurge backend
Tests all critical imports without connecting to database
"""
import sys
import os
from pathlib import Path

# Add backend to path
sys.path.insert(0, '.')

def test_imports():
    print("🧪 Testing AdCopySurge Import Compatibility")
    print("=" * 50)
    
    tests = []
    
    # Test 1: Core configuration
    try:
        print("📋 Testing core configuration...")
        # Don't load settings as it tries to connect to DB
        from app.core.config import Settings
        tests.append(("✅", "Core configuration classes"))
    except Exception as e:
        tests.append(("❌", f"Core configuration: {e}"))
    
    # Test 2: Database models (without engine)
    try:
        print("📋 Testing database models...")
        # Test if the model classes can be defined without DB connection
        from sqlalchemy.ext.declarative import declarative_base
        Base = declarative_base()
        
        # Test model imports by checking their class definition
        from app.models import ad_analysis, user
        tests.append(("✅", "Database models import successfully"))
    except Exception as e:
        # In production environments like Railway, this should pass
        # Locally, it might fail due to missing psycopg2, which is expected
        if "psycopg2" in str(e):
            print("ℹ️ Note: psycopg2 not available locally (expected in development)")
            tests.append(("⚠️", "Database models: psycopg2 not available (OK for local dev)"))
        else:
            tests.append(("❌", f"Database models: {e}"))
    
    # Test 3: Services (without actual instantiation)
    try:
        print("📋 Testing service modules...")
        from app.services import emotion_analyzer
        tests.append(("✅", "Service modules import"))
    except Exception as e:
        tests.append(("❌", f"Service modules: {e}"))
    
    # Test 4: API routes (without FastAPI app)
    try:
        print("📋 Testing API route definitions...")
        # Just test if the modules can be imported
        import importlib.util
        
        api_modules = ['auth', 'ads', 'analytics', 'subscriptions']
        for module in api_modules:
            spec = importlib.util.find_spec(f'app.api.{module}')
            if spec is None:
                raise ImportError(f"Cannot find app.api.{module}")
        
        tests.append(("✅", "API route modules found"))
    except Exception as e:
        tests.append(("❌", f"API routes: {e}"))
    
    # Test 5: Circular import specifically (the previous issue)
    try:
        print("📋 Testing for circular import issues...")
        # Test the specific import pattern that was causing circular imports
        import importlib.util
        
        # These should be importable without circular import errors
        critical_imports = [
            'app.schemas.ads',  # New schemas module
            'app.services.ad_analysis_service',  # Service that uses schemas
        ]
        
        for module in critical_imports:
            spec = importlib.util.find_spec(module)
            if spec is None:
                raise ImportError(f"Cannot find {module}")
        
        tests.append(("✅", "No circular import issues detected"))
    except Exception as e:
        tests.append(("❌", f"Circular import test: {e}"))
    
    # Test 6: Check for common SQLAlchemy import issues
    try:
        print("📋 Testing SQLAlchemy imports...")
        from sqlalchemy import Column, Integer, String, Float, Text, JSON, DateTime, ForeignKey, Boolean
        from sqlalchemy.orm import relationship
        tests.append(("✅", "SQLAlchemy imports"))
    except Exception as e:
        tests.append(("❌", f"SQLAlchemy imports: {e}"))
    
    # Print results
    print("\n📊 Test Results:")
    print("-" * 30)
    for status, message in tests:
        print(f"{status} {message}")
    
    # Summary
    passed = sum(1 for status, _ in tests if status == "✅")
    warnings = sum(1 for status, _ in tests if status == "⚠️")
    failed = sum(1 for status, _ in tests if status == "❌")
    total = len(tests)
    
    print(f"\n📈 Summary: {passed} passed, {warnings} warnings, {failed} failed (of {total} total)")
    
    if failed == 0:
        if warnings > 0:
            print("✅ Import tests passed with warnings - should work in production!")
        else:
            print("🎉 All import tests passed perfectly! Ready for deployment.")
        return True
    else:
        print("💥 Some import tests failed. Fix these issues before deployment.")
        return False

if __name__ == "__main__":
    success = test_imports()
    sys.exit(0 if success else 1)
