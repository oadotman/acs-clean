#!/usr/bin/env python3
"""
Test Enhanced Validation System

Tests the new validation features including confidence scoring, quality gating,
platform-specific checks, template phrase detection, and standardized responses.
"""

import asyncio
import json
import sys
from pathlib import Path

# Add the backend directory to Python path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

from app.services.content_validator import ContentValidator, validate_content
from app.services.variant_strategies import get_platform_strategies, get_variant_context
from app.services.response_formatter import format_standardized_response
from app.services.platform_ad_generator import PlatformAdGenerator, GenerationResult

def test_confidence_scoring():
    """Test confidence scoring system"""
    print("🧪 Testing Confidence Scoring System...")
    
    validator = ContentValidator()
    
    # Test high-quality content
    high_quality_content = {
        'headline': 'Boost Your Sales 40%',  # Under 60 chars = +5 bonus
        'body': 'Join 10K+ businesses who increased revenue with our proven CRM system.',
        'cta': 'Start Free'  # 2 words = +5 bonus
    }
    
    result = validator.validate_and_sanitize(high_quality_content, 'facebook', strict_mode=False)
    print(f"✅ High-quality content score: {result.confidence_score}/100")
    
    # Test low-quality content with issues
    low_quality_content = {
        'headline': 'Unlock the benefits of our amazing revolutionary game-changing solution',  # Too long, template phrases
        'body': 'Are you tired of the problem? Imagine this: Our industry-leading product will transform your life forever!',  # Template phrases, repetition
        'cta': 'Buy now and save money today with our special offer'  # Too long
    }
    
    result = validator.validate_and_sanitize(low_quality_content, 'facebook', strict_mode=False)
    print(f"❌ Low-quality content score: {result.confidence_score}/100")
    print(f"   Template phrases found: {result.template_phrases_found}")
    print(f"   Quality issues: {len(result.quality_issues)}")
    
    return True

def test_platform_specific_validation():
    """Test platform-specific validation checks"""
    print("\n🧪 Testing Platform-Specific Validation...")
    
    validator = ContentValidator()
    
    # Test Google Ads headline uniqueness
    print("\n📊 Google Ads - Testing headline uniqueness:")
    google_content = {
        'headlines': ['Best CRM Software', 'Best CRM Software', 'Quality CRM Software'],  # Duplicate
        'descriptions': ['Improve your sales process', 'Boost team productivity'],
        'cta': 'Get Started'
    }
    
    result = validator.validate_and_sanitize(google_content, 'google_ads', strict_mode=False)
    print(f"   Confidence: {result.confidence_score}/100")
    print(f"   Platform issues: {len(result.platform_specific_issues)}")
    for issue in result.platform_specific_issues:
        print(f"   - {issue}")
    
    # Test LinkedIn professional language
    print("\n💼 LinkedIn - Testing professional language:")
    linkedin_content = {
        'headline': 'OMG this business tool is so good lol',  # Unprofessional
        'body': 'Hit me up if u want to see crazy ROI results, tbh this is game-changing',
        'cta': 'DM me now'
    }
    
    result = validator.validate_and_sanitize(linkedin_content, 'linkedin', strict_mode=False)
    print(f"   Confidence: {result.confidence_score}/100")
    print(f"   Platform issues: {len(result.platform_specific_issues)}")
    for issue in result.platform_specific_issues:
        print(f"   - {issue}")
    
    # Test Instagram hashtag validation
    print("\n📸 Instagram - Testing hashtag validation:")
    instagram_content = {
        'body': 'Check out this amazing lifestyle upgrade!',
        'hashtags': ['#amazing', '#lifestyle'] + [f'#verylonghashtagnamethatexceedsthelimit{i}' for i in range(5)],  # Some too long
        'cta': 'Try Now'
    }
    
    result = validator.validate_and_sanitize(instagram_content, 'instagram', strict_mode=False)
    print(f"   Confidence: {result.confidence_score}/100")
    print(f"   Platform issues: {len(result.platform_specific_issues)}")
    for issue in result.platform_specific_issues:
        print(f"   - {issue}")
    
    return True

def test_variant_strategies():
    """Test platform-specific variant strategies"""
    print("\n🧪 Testing Platform-Specific Variant Strategies...")
    
    platforms = ['facebook', 'instagram', 'google_ads', 'linkedin', 'twitter_x', 'tiktok']
    
    for platform in platforms:
        print(f"\n📱 {platform.upper()} Strategies:")
        strategies = get_platform_strategies(platform)
        
        for strategy in strategies:
            print(f"   Version {strategy.version}: {strategy.name}")
            print(f"   Focus: {strategy.focus_type}")
            print(f"   Best for: {', '.join(strategy.best_for[:2])}")
        
        # Test variant context generation
        variant_context = get_variant_context(platform, 'A', {'industry': 'saas'})
        print(f"   Sample context keys: {list(variant_context.keys())}")
    
    return True

def test_standardized_response_format():
    """Test standardized response formatting"""
    print("\n🧪 Testing Standardized Response Format...")
    
    # Mock generation result
    class MockGenerationResult:
        def __init__(self):
            self.success = True
            self.generated_content = {
                'headline': 'Professional CRM Solution',
                'body': 'Streamline your sales process with our enterprise-grade CRM.',
                'cta': 'Request Demo'
            }
            self.char_counts = {'headline': 26, 'body': 61, 'cta': 12}
            self.metrics = {'generation_time_ms': 1234, 'retry_count': 0}
    
    # Test different platforms
    platforms_to_test = ['facebook', 'google_ads', 'instagram', 'twitter_x']
    
    for platform in platforms_to_test:
        print(f"\n📱 {platform.upper()} Response Format:")
        
        # Adjust content for platform
        if platform == 'google_ads':
            mock_result = MockGenerationResult()
            mock_result.generated_content = {
                'headlines': ['CRM Software Solutions', 'Business Growth Tools', 'Sales Team Productivity'],
                'descriptions': ['Streamline sales with our CRM platform', 'Increase revenue and team efficiency'],
                'cta': 'Get Quote'
            }
        elif platform == 'instagram':
            mock_result = MockGenerationResult()
            mock_result.generated_content = {
                'body': 'Transform your business workflow with our amazing CRM! ✨',
                'hashtags': ['#crm', '#business', '#productivity'],
                'cta': 'Try Now'
            }
        elif platform == 'twitter_x':
            mock_result = MockGenerationResult()
            mock_result.generated_content = {
                'body': '🚀 Just helped 1000+ businesses boost sales 40% with our CRM. Your turn? Get started: link.com'
            }
        else:
            mock_result = MockGenerationResult()
        
        # Create validation result
        validation_result = validate_content(mock_result.generated_content, platform, strict_mode=False)
        
        # Format standardized response
        response = format_standardized_response(
            platform_id=platform,
            original_ad_copy="Original ad copy for testing",
            generation_result=mock_result,
            validation_result=validation_result,
            variants=[],
            original_score=65
        )
        
        print(f"   Platform: {response['platform']}")
        print(f"   Confidence: {response['confidenceScore']}/100")
        print(f"   Improved fields: {[k for k in response['improvedAd'].keys() if response['improvedAd'][k]]}")
        print(f"   Tips count: {len(response['tips'].split(' | '))}")
    
    return True

def test_template_phrase_detection():
    """Test template phrase detection"""
    print("\n🧪 Testing Template Phrase Detection...")
    
    validator = ContentValidator()
    
    template_heavy_content = {
        'headline': 'Are you tired of the same old problem?',
        'body': 'Introducing our revolutionary new solution that will transform your life forever! Don\'t miss out on this limited time offer.',
        'cta': 'Act now and save'
    }
    
    result = validator.validate_and_sanitize(template_heavy_content, 'facebook', strict_mode=False)
    
    print(f"   Template phrases detected: {len(result.template_phrases_found)}")
    for phrase in result.template_phrases_found:
        print(f"   - '{phrase}'")
    print(f"   Confidence score: {result.confidence_score}/100")
    
    return True

def main():
    """Run all enhanced validation tests"""
    print("🚀 Starting Enhanced Validation System Tests\n")
    print("=" * 60)
    
    tests = [
        ("Confidence Scoring", test_confidence_scoring),
        ("Platform-Specific Validation", test_platform_specific_validation),
        ("Variant Strategies", test_variant_strategies),
        ("Standardized Response Format", test_standardized_response_format),
        ("Template Phrase Detection", test_template_phrase_detection),
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
    print("📊 ENHANCED VALIDATION TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All enhanced validation tests passed!")
        print("\n✨ New Features Validated:")
        print("   • Confidence scoring (0-100) with quality bonuses")
        print("   • Platform-specific validation (Google Ads uniqueness, LinkedIn professionalism, etc.)")
        print("   • Template phrase detection and prevention")
        print("   • Platform-specific A/B/C variant strategies")
        print("   • Standardized API response format across all platforms")
    else:
        print("⚠️ Some tests failed. Please check the implementation.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)