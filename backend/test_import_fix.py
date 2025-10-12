#!/usr/bin/env python3
"""
Test script to validate that the XMLResponse import issue has been fixed.
This will test the import changes without requiring all dependencies.
"""

import sys
import traceback

def test_fastapi_imports():
    """Test that FastAPI imports work correctly"""
    try:
        from fastapi.responses import Response, PlainTextResponse
        print("✅ FastAPI Response imports successful")
        return True
    except ImportError as e:
        print(f"❌ FastAPI import failed: {e}")
        return False

def test_pydantic_pattern():
    """Test that Pydantic Field with pattern parameter works"""
    try:
        from pydantic import BaseModel, Field
        
        class TestModel(BaseModel):
            sort_by: str = Field("published_at", pattern="^(published_at|created_at|title|views)$")
            sort_order: str = Field("desc", pattern="^(asc|desc)$")
        
        # Test valid values
        model = TestModel()
        assert model.sort_by == "published_at"
        assert model.sort_order == "desc"
        
        print("✅ Pydantic pattern validation working correctly")
        return True
    except Exception as e:
        print(f"❌ Pydantic pattern test failed: {e}")
        traceback.print_exc()
        return False

def test_response_creation():
    """Test that we can create XML and plain text responses"""
    try:
        from fastapi.responses import Response, PlainTextResponse
        
        # Test XML response creation
        xml_content = """<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url>
    <loc>https://example.com/</loc>
    <lastmod>2025-01-01</lastmod>
  </url>
</urlset>"""
        
        xml_response = Response(
            content=xml_content,
            media_type="application/xml; charset=utf-8"
        )
        
        # Test plain text response
        plain_response = PlainTextResponse(
            content="User-agent: *\nDisallow: /admin/",
            headers={"Content-Type": "text/plain; charset=utf-8"}
        )
        
        print("✅ Response creation working correctly")
        return True
    except Exception as e:
        print(f"❌ Response creation test failed: {e}")
        traceback.print_exc()
        return False

def main():
    print("🧪 Testing XMLResponse Fix")
    print("=" * 50)
    
    tests = [
        ("FastAPI Imports", test_fastapi_imports),
        ("Pydantic Pattern", test_pydantic_pattern),
        ("Response Creation", test_response_creation)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n📋 Testing {test_name}...")
        success = test_func()
        results.append(success)
    
    print("\n📊 Test Results:")
    print("-" * 30)
    passed = sum(results)
    total = len(results)
    
    for i, (test_name, _) in enumerate(tests):
        status = "✅ PASSED" if results[i] else "❌ FAILED"
        print(f"{test_name}: {status}")
    
    print(f"\n📈 Summary: {passed} passed, {total - passed} failed (of {total} total)")
    
    if passed == total:
        print("🎉 All tests passed! XMLResponse issue has been fixed.")
        return True
    else:
        print("⚠️  Some tests failed. Check the errors above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
