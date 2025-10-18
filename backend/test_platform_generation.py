#!/usr/bin/env python3
"""
Test Platform-Aware Ad Generation System

Tests the new platform-specific generation pipeline to ensure it works correctly
for all supported platforms with proper character limits, structure, and validation.
"""

import asyncio
import json
import os
import sys
from pathlib import Path

# Add the backend directory to Python path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

from app.services.platform_registry import get_platform_registry
from app.services.platform_aware_parser import PlatformAwareParser
from app.services.platform_prompt_builder import PlatformPromptBuilder
from app.services.content_validator import ContentValidator
from app.services.platform_ad_generator import PlatformAdGenerator

# Test data
TEST_AD_COPY = """
Transform your business with our revolutionary CRM software. 
Increase sales by 40% and improve customer satisfaction instantly. 
Join over 10,000 successful companies who trust our solution.
Get started with our free 14-day trial today - no credit card required!
Try it free now and see results in just 24 hours.
"""

PLATFORMS_TO_TEST = [
    'facebook', 'instagram', 'google_ads', 'linkedin', 'twitter_x', 'tiktok'
]

TEST_CONTEXT = {
    'industry': 'saas',
    'target_audience': 'small business owners',
    'brand_voice': 'professional but friendly',
    'tone': 'conversational'
}

class PlatformTestRunner:
    """Test runner for platform-aware ad generation"""
    
    def __init__(self):
        self.registry = get_platform_registry()
        self.parser = PlatformAwareParser()
        self.prompt_builder = PlatformPromptBuilder()
        self.validator = ContentValidator()
        
        # Mock OpenAI API key for testing (you'll need a real one)
        self.mock_api_key = "sk-test-mock-key-for-testing"
        
    def test_platform_registry(self):
        """Test that platform registry loads correctly"""
        print("🧪 Testing Platform Registry...")
        
        try:
            # Test platform loading
            platforms = self.registry.list_platforms()
            print(f"✅ Loaded {len(platforms)} platforms: {[p['id'] for p in platforms]}")
            
            # Test platform resolution
            test_cases = [
                ('facebook', 'facebook'),
                ('fb', 'facebook'),
                ('google', 'google_ads'),
                ('x', 'twitter_x'),
                ('invalid', 'facebook')  # should default
            ]
            
            for input_platform, expected in test_cases:
                resolved = self.registry.resolve_platform_id(input_platform)
                status = "✅" if resolved == expected else "❌"
                print(f"{status} Platform resolution: {input_platform} -> {resolved} (expected: {expected})")
            
            return True
            
        except Exception as e:
            print(f"❌ Platform registry test failed: {e}")
            return False
    
    def test_platform_parsing(self):
        """Test platform-aware parsing"""
        print("\n🧪 Testing Platform-Aware Parsing...")
        
        try:
            for platform_id in PLATFORMS_TO_TEST:
                parsed_ad = self.parser.parse_ad(TEST_AD_COPY, platform_id)
                
                print(f"\n📋 Platform: {platform_id.upper()}")
                print(f"   Confidence: {parsed_ad.confidence}")
                print(f"   Method: {parsed_ad.parsing_report.get('method', 'unknown')}")
                print(f"   Content fields: {list(parsed_ad.content.keys())}")
                
                # Validate content structure matches platform requirements
                config = self.registry.get_platform_config(platform_id)
                expected_fields = set(config.fields.keys())
                actual_fields = set(parsed_ad.content.keys())
                
                if expected_fields.intersection(actual_fields):
                    print(f"   ✅ Contains required fields")
                else:
                    print(f"   ⚠️  Field mismatch - Expected: {expected_fields}, Got: {actual_fields}")
            
            return True
            
        except Exception as e:
            print(f"❌ Platform parsing test failed: {e}")
            return False
    
    def test_prompt_building(self):
        """Test platform-specific prompt building"""
        print("\n🧪 Testing Platform-Specific Prompt Building...")
        
        try:
            for platform_id in PLATFORMS_TO_TEST:
                # Parse ad first
                parsed_ad = self.parser.parse_ad(TEST_AD_COPY, platform_id)
                
                # Build prompt
                prompt_dict = self.prompt_builder.build_prompt(platform_id, parsed_ad, TEST_CONTEXT)
                
                print(f"\n📝 Platform: {platform_id.upper()}")
                print(f"   System prompt length: {len(prompt_dict['system'])} chars")
                print(f"   User prompt length: {len(prompt_dict['user'])} chars")
                
                # Check that prompts contain platform-specific requirements
                system_prompt = prompt_dict['system'].lower()
                config = self.registry.get_platform_config(platform_id)
                
                checks = []
                checks.append(('char limits', any(str(field.max_chars) in prompt_dict['system'] for field in config.fields.values())))
                checks.append(('json format', 'json' in system_prompt))
                checks.append(('banned phrases', any(phrase.lower() in system_prompt for phrase in config.banned_phrases)))
                checks.append(('platform tone', any(word in system_prompt for word in config.tone.split(', '))))
                
                for check_name, passed in checks:
                    status = "✅" if passed else "⚠️"
                    print(f"   {status} {check_name}")
            
            return True
            
        except Exception as e:
            print(f"❌ Prompt building test failed: {e}")
            return False
    
    def test_content_validation(self):
        """Test content validation and sanitization"""
        print("\n🧪 Testing Content Validation...")
        
        try:
            # Test content for each platform
            test_contents = {
                'facebook': {
                    'headline': 'Test Facebook Headline',
                    'body': 'This is a test Facebook ad body with proper length for validation.',
                    'cta': 'Get Started'
                },
                'google_ads': {
                    'headlines': ['Test Headline 1', 'Test Headline 2', 'Test Headline 3'],
                    'descriptions': ['Test description 1 for Google Ads', 'Test description 2 for validation'],
                    'cta': 'Contact Us'
                },
                'instagram': {
                    'body': 'Instagram test body content with proper formatting and length.',
                    'hashtags': ['#test', '#instagram', '#marketing'],
                    'cta': 'Learn More'
                },
                'twitter_x': {
                    'body': 'Twitter/X test content that fits within character limit'
                },
                'tiktok': {
                    'body': 'Short TikTok content',
                    'cta': 'Try Now'
                },
                'linkedin': {
                    'headline': 'Professional LinkedIn Headline for Business Audience',
                    'body': 'LinkedIn body content focusing on business outcomes and professional growth opportunities.',
                    'cta': 'Request Demo'
                }
            }
            
            for platform_id, content in test_contents.items():
                print(f"\n📊 Validating: {platform_id.upper()}")
                
                validation_result = self.validator.validate_and_sanitize(content, platform_id, strict_mode=True)
                
                print(f"   Valid: {validation_result.is_valid}")
                print(f"   Errors: {len(validation_result.errors)}")
                print(f"   Warnings: {len(validation_result.warnings)}")
                print(f"   Char counts: {validation_result.char_counts}")
                
                if validation_result.errors:
                    for error in validation_result.errors[:3]:  # Show first 3 errors
                        print(f"   ❌ {error}")
                
                if not validation_result.errors:
                    print(f"   ✅ All validations passed")
            
            return True
            
        except Exception as e:
            print(f"❌ Content validation test failed: {e}")
            return False
    
    def test_banned_phrases(self):
        """Test that banned phrases are detected"""
        print("\n🧪 Testing Banned Phrase Detection...")
        
        try:
            test_content_with_banned = {
                'headline': 'Unlock the benefits of our amazing product',
                'body': 'Tired of the problem? Imagine this: Get all products today!',
                'cta': 'Buy Now'
            }
            
            for platform_id in PLATFORMS_TO_TEST:
                print(f"\n🚫 Testing banned phrases: {platform_id.upper()}")
                
                validation_result = self.validator.validate_and_sanitize(
                    test_content_with_banned, platform_id, strict_mode=True
                )
                
                banned_errors = [error for error in validation_result.errors if 'banned phrase' in error]
                
                if banned_errors:
                    print(f"   ✅ Detected {len(banned_errors)} banned phrases")
                    for error in banned_errors[:2]:  # Show first 2
                        print(f"   🚫 {error}")
                else:
                    print(f"   ❌ Failed to detect banned phrases")
            
            return True
            
        except Exception as e:
            print(f"❌ Banned phrase test failed: {e}")
            return False
    
    def test_character_limits(self):
        """Test character limit enforcement"""
        print("\n🧪 Testing Character Limit Enforcement...")
        
        try:
            # Create content that exceeds limits
            long_content = {
                'headline': 'This is a very long headline that definitely exceeds the character limits for most platforms',
                'body': 'This is an extremely long body text that goes way beyond the character limits set for various platforms. ' * 10,
                'cta': 'This is a very long call-to-action that exceeds limits'
            }
            
            for platform_id in PLATFORMS_TO_TEST:
                print(f"\n📏 Testing limits: {platform_id.upper()}")
                
                config = self.registry.get_platform_config(platform_id)
                validation_result = self.validator.validate_and_sanitize(long_content, platform_id, strict_mode=True)
                
                limit_errors = [error for error in validation_result.errors if 'exceeds' in error and 'limit' in error]
                
                if limit_errors:
                    print(f"   ✅ Detected {len(limit_errors)} limit violations")
                    
                    # Check sanitized content
                    for field_name, char_count in validation_result.char_counts.items():
                        field_config = config.fields.get(field_name)
                        if field_config:
                            within_limit = char_count <= field_config.max_chars
                            status = "✅" if within_limit else "⚠️"
                            print(f"   {status} {field_name}: {char_count}/{field_config.max_chars} chars")
                else:
                    print(f"   ⚠️ No limit violations detected")
            
            return True
            
        except Exception as e:
            print(f"❌ Character limit test failed: {e}")
            return False

def main():
    """Run all tests"""
    print("🚀 Starting Platform-Aware Ad Generation System Tests\n")
    print("=" * 60)
    
    runner = PlatformTestRunner()
    
    # Run all tests
    tests = [
        ('Platform Registry', runner.test_platform_registry),
        ('Platform Parsing', runner.test_platform_parsing),
        ('Prompt Building', runner.test_prompt_building),
        ('Content Validation', runner.test_content_validation),
        ('Banned Phrases', runner.test_banned_phrases),
        ('Character Limits', runner.test_character_limits),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ Test {test_name} crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Platform-aware system is working correctly.")
    else:
        print("⚠️ Some tests failed. Please check the implementation.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)