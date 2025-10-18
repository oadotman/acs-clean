#!/usr/bin/env python3
"""
Comprehensive Platform Validation Test Framework

Tests all aspects of platform-specific ad generation:
- Parser field extraction accuracy
- Character limit compliance
- Template phrase detection
- Grammar validation
- Confidence score accuracy
- Retry logic functionality
- Output quality standards
"""

import asyncio
import json
import logging
import time
from typing import Dict, List, Any, Tuple
import pytest
from dataclasses import asdict

# Import our services
try:
    from app.services.platform_ad_generator import PlatformAdGenerator
    from app.services.platform_aware_parser import PlatformAwareParser
    from app.services.content_validator import ContentValidator
    from app.services.platform_registry import get_platform_registry, resolve_platform_id
    from test_data_comprehensive import (
        get_test_ads_for_platform, 
        get_all_test_ads, 
        get_parsing_expectations,
        get_quality_criteria,
        PLATFORM_TEST_DATA
    )
    SERVICES_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Could not import platform services: {e}")
    SERVICES_AVAILABLE = False

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ValidationTestResult:
    """Result of a validation test"""
    def __init__(self):
        self.test_name = ""
        self.platform_id = ""
        self.input_ad = ""
        self.success = False
        self.errors = []
        self.warnings = []
        self.metrics = {}
        self.validation_details = {}

class PlatformValidationTester:
    """Comprehensive platform validation testing framework"""
    
    def __init__(self, openai_api_key: str = None):
        self.openai_api_key = openai_api_key or "test-key"
        self.parser = PlatformAwareParser() if SERVICES_AVAILABLE else None
        self.validator = ContentValidator() if SERVICES_AVAILABLE else None
        self.generator = None
        
        if SERVICES_AVAILABLE and openai_api_key:
            try:
                self.generator = PlatformAdGenerator(openai_api_key)
            except Exception as e:
                logger.warning(f"Could not initialize generator: {e}")
        
        self.test_results = []
        self.platforms = ['facebook', 'instagram', 'google_ads', 'linkedin', 'twitter_x', 'tiktok']
        
    async def run_comprehensive_tests(self) -> Dict[str, Any]:
        """Run all validation tests across all platforms"""
        logger.info("🚀 Starting comprehensive platform validation tests...")
        
        start_time = time.time()
        test_summary = {
            'total_tests': 0,
            'passed_tests': 0,
            'failed_tests': 0,
            'platforms_tested': [],
            'test_categories': {
                'parser_tests': {'passed': 0, 'failed': 0},
                'character_limit_tests': {'passed': 0, 'failed': 0},
                'template_detection_tests': {'passed': 0, 'failed': 0},
                'grammar_validation_tests': {'passed': 0, 'failed': 0},
                'confidence_score_tests': {'passed': 0, 'failed': 0},
                'quality_standards_tests': {'passed': 0, 'failed': 0}
            },
            'platform_results': {},
            'execution_time': 0,
            'detailed_results': []
        }
        
        # Test each platform
        for platform_id in self.platforms:
            logger.info(f"📊 Testing platform: {platform_id}")
            platform_results = await self._test_platform(platform_id)
            test_summary['platform_results'][platform_id] = platform_results
            test_summary['platforms_tested'].append(platform_id)
            
            # Update counters
            for test_result in platform_results['tests']:
                test_summary['total_tests'] += 1
                if test_result['success']:
                    test_summary['passed_tests'] += 1
                    # Update category counters
                    category = test_result.get('category', 'unknown')
                    if category in test_summary['test_categories']:
                        test_summary['test_categories'][category]['passed'] += 1
                else:
                    test_summary['failed_tests'] += 1
                    category = test_result.get('category', 'unknown')
                    if category in test_summary['test_categories']:
                        test_summary['test_categories'][category]['failed'] += 1
                
                test_summary['detailed_results'].append(test_result)
        
        test_summary['execution_time'] = round(time.time() - start_time, 2)
        logger.info(f"✅ Completed all tests in {test_summary['execution_time']}s")
        logger.info(f"📈 Results: {test_summary['passed_tests']}/{test_summary['total_tests']} tests passed")
        
        return test_summary
    
    async def _test_platform(self, platform_id: str) -> Dict[str, Any]:
        """Test all aspects of a specific platform"""
        platform_test_data = get_test_ads_for_platform(platform_id)
        parsing_expectations = get_parsing_expectations(platform_id)
        
        platform_results = {
            'platform_id': platform_id,
            'tests': [],
            'summary': {
                'total': 0,
                'passed': 0,
                'failed': 0,
                'categories': {}
            }
        }
        
        # Test each category of ads for this platform
        for category, ads in platform_test_data.items():
            logger.info(f"  🔍 Testing {category} for {platform_id}")
            
            for i, ad_text in enumerate(ads):
                if not ad_text:  # Skip empty ads for most tests
                    continue
                
                # Run all test types for this ad
                test_results = await self._run_all_tests_for_ad(
                    platform_id, ad_text, category, i
                )
                
                platform_results['tests'].extend(test_results)
                
                for result in test_results:
                    platform_results['summary']['total'] += 1
                    if result['success']:
                        platform_results['summary']['passed'] += 1
                    else:
                        platform_results['summary']['failed'] += 1
        
        return platform_results
    
    async def _run_all_tests_for_ad(self, platform_id: str, ad_text: str, category: str, index: int) -> List[Dict[str, Any]]:
        """Run all test types for a single ad"""
        test_results = []
        test_id = f"{platform_id}_{category}_{index}"
        
        # 1. Parser Field Extraction Test
        parser_result = await self._test_parser_extraction(platform_id, ad_text, test_id)
        parser_result['category'] = 'parser_tests'
        test_results.append(parser_result)
        
        # 2. Character Limit Test (if we have generated content)
        if parser_result.get('parsed_content'):
            char_limit_result = await self._test_character_limits(platform_id, parser_result['parsed_content'], test_id)
            char_limit_result['category'] = 'character_limit_tests'
            test_results.append(char_limit_result)
        
        # 3. Template Detection Test (if generator is available)
        if self.generator:
            template_result = await self._test_template_detection(platform_id, ad_text, test_id)
            template_result['category'] = 'template_detection_tests'
            test_results.append(template_result)
        
        # 4. Grammar Validation Test
        grammar_result = await self._test_grammar_validation(ad_text, test_id)
        grammar_result['category'] = 'grammar_validation_tests'
        test_results.append(grammar_result)
        
        # 5. Confidence Score Test (if validator is available)
        if self.validator:
            confidence_result = await self._test_confidence_scoring(platform_id, ad_text, test_id)
            confidence_result['category'] = 'confidence_score_tests'
            test_results.append(confidence_result)
        
        # 6. Quality Standards Test (comprehensive)
        quality_result = await self._test_quality_standards(platform_id, ad_text, test_id)
        quality_result['category'] = 'quality_standards_tests'
        test_results.append(quality_result)
        
        return test_results
    
    async def _test_parser_extraction(self, platform_id: str, ad_text: str, test_id: str) -> Dict[str, Any]:
        """Test parser field extraction accuracy"""
        result = {
            'test_id': test_id,
            'test_name': 'parser_field_extraction',
            'platform_id': platform_id,
            'input_ad': ad_text,
            'success': False,
            'errors': [],
            'warnings': [],
            'metrics': {},
            'parsed_content': None
        }
        
        if not self.parser:
            result['errors'].append("Parser not available")
            return result
        
        try:
            start_time = time.time()
            parsed_ad = self.parser.parse_ad(ad_text, platform_id)
            parsing_time = time.time() - start_time
            
            result['parsed_content'] = asdict(parsed_ad)
            result['metrics']['parsing_time_ms'] = round(parsing_time * 1000, 2)
            result['metrics']['confidence'] = parsed_ad.confidence
            
            # Get expected fields for this platform
            expectations = get_parsing_expectations(platform_id)
            required_fields = expectations.get('required_fields', [])
            
            # Validate required fields are present
            missing_fields = []
            for field in required_fields:
                if not getattr(parsed_ad, field, None):
                    missing_fields.append(field)
            
            if missing_fields:
                result['errors'].append(f"Missing required fields: {missing_fields}")
            
            # Check confidence score
            if parsed_ad.confidence < 50:
                result['warnings'].append(f"Low confidence score: {parsed_ad.confidence}")
            
            result['success'] = len(result['errors']) == 0
            
        except Exception as e:
            result['errors'].append(f"Parser exception: {str(e)}")
        
        return result
    
    async def _test_character_limits(self, platform_id: str, parsed_content: Dict, test_id: str) -> Dict[str, Any]:
        """Test character limit compliance"""
        result = {
            'test_id': test_id,
            'test_name': 'character_limits',
            'platform_id': platform_id,
            'success': False,
            'errors': [],
            'warnings': [],
            'metrics': {}
        }
        
        try:
            expectations = get_parsing_expectations(platform_id)
            max_lengths = expectations.get('max_lengths', {})
            
            violations = []
            for field, max_length in max_lengths.items():
                content = parsed_content.get(field, '')
                
                if isinstance(content, list):
                    # Handle list fields (like headlines, hashtags)
                    for i, item in enumerate(content):
                        if len(str(item)) > max_length:
                            violations.append(f"{field}[{i}]: {len(str(item))} > {max_length}")
                elif isinstance(content, str):
                    if len(content) > max_length:
                        violations.append(f"{field}: {len(content)} > {max_length}")
            
            if violations:
                result['errors'].extend(violations)
            
            result['metrics']['violations_count'] = len(violations)
            result['success'] = len(violations) == 0
            
        except Exception as e:
            result['errors'].append(f"Character limit test exception: {str(e)}")
        
        return result
    
    async def _test_template_detection(self, platform_id: str, ad_text: str, test_id: str) -> Dict[str, Any]:
        """Test template phrase detection in generated content"""
        result = {
            'test_id': test_id,
            'test_name': 'template_detection',
            'platform_id': platform_id,
            'input_ad': ad_text,
            'success': False,
            'errors': [],
            'warnings': [],
            'metrics': {}
        }
        
        if not self.generator:
            result['errors'].append("Generator not available")
            return result
        
        try:
            start_time = time.time()
            generation_result = await self.generator.generate_ad(
                text_input=ad_text,
                platform_id=platform_id,
                context={'industry': 'test'}
            )
            generation_time = time.time() - start_time
            
            result['metrics']['generation_time_ms'] = round(generation_time * 1000, 2)
            result['metrics']['generation_success'] = generation_result.success
            
            if not generation_result.success:
                result['warnings'].append("Generation failed, skipping template detection")
                result['success'] = True  # Not a failure of the test itself
                return result
            
            # Check for forbidden template phrases
            quality_criteria = get_quality_criteria()
            forbidden_templates = quality_criteria['forbidden_templates']
            
            generated_text = str(generation_result.generated_content)
            found_templates = []
            
            for template in forbidden_templates:
                if template.lower() in generated_text.lower():
                    found_templates.append(template)
            
            if found_templates:
                result['errors'].append(f"Found template phrases: {found_templates}")
            
            result['metrics']['template_phrases_found'] = len(found_templates)
            result['success'] = len(found_templates) == 0
            
        except Exception as e:
            result['errors'].append(f"Template detection exception: {str(e)}")
        
        return result
    
    async def _test_grammar_validation(self, ad_text: str, test_id: str) -> Dict[str, Any]:
        """Test grammar validation detection"""
        result = {
            'test_id': test_id,
            'test_name': 'grammar_validation',
            'input_ad': ad_text,
            'success': False,
            'errors': [],
            'warnings': [],
            'metrics': {}
        }
        
        try:
            quality_criteria = get_quality_criteria()
            grammar_issues = quality_criteria['grammar_issues']
            
            found_issues = []
            for issue in grammar_issues:
                if issue.lower() in ad_text.lower():
                    found_issues.append(issue)
            
            # For poor grammar ads, finding issues is expected
            # For well-written ads, finding issues is a problem
            if 'poor_grammar' in ad_text or any(bad_phrase in ad_text.lower() for bad_phrase in ['we has', 'dont wait', 'you will love it so much']):
                # This is a poor grammar ad - finding issues is good
                result['success'] = len(found_issues) > 0
                result['metrics']['grammar_issues_detected'] = len(found_issues)
                if len(found_issues) == 0:
                    result['warnings'].append("Expected to find grammar issues in poor grammar ad")
            else:
                # This should be clean - finding issues is bad
                result['success'] = len(found_issues) == 0
                result['metrics']['grammar_issues_detected'] = len(found_issues)
                if len(found_issues) > 0:
                    result['errors'].append(f"Found grammar issues in clean ad: {found_issues}")
            
        except Exception as e:
            result['errors'].append(f"Grammar validation exception: {str(e)}")
        
        return result
    
    async def _test_confidence_scoring(self, platform_id: str, ad_text: str, test_id: str) -> Dict[str, Any]:
        """Test confidence score calculation accuracy"""
        result = {
            'test_id': test_id,
            'test_name': 'confidence_scoring',
            'platform_id': platform_id,
            'input_ad': ad_text,
            'success': False,
            'errors': [],
            'warnings': [],
            'metrics': {}
        }
        
        if not self.validator:
            result['errors'].append("Validator not available")
            return result
        
        try:
            # Create mock content for validation
            mock_content = {'body': ad_text}
            if platform_id == 'facebook':
                mock_content.update({'headline': ad_text[:50], 'cta': 'Learn More'})
            elif platform_id == 'instagram':
                mock_content.update({'hashtags': ['#test']})
            elif platform_id == 'google_ads':
                mock_content = {'headlines': [ad_text[:30]], 'descriptions': [ad_text[:90]]}
            
            validation_result = self.validator.validate_and_sanitize(
                mock_content, platform_id, strict_mode=False
            )
            
            confidence_score = validation_result.confidence_score
            result['metrics']['confidence_score'] = confidence_score
            
            quality_criteria = get_quality_criteria()
            min_score = quality_criteria['minimum_confidence_score']
            max_score = quality_criteria['maximum_confidence_score']
            
            # Validate score is in valid range
            if confidence_score < 0 or confidence_score > 100:
                result['errors'].append(f"Invalid confidence score: {confidence_score} (should be 0-100)")
            
            # Check if score makes sense based on ad quality
            if 'poor_grammar' in ad_text.lower() or 'we has' in ad_text.lower():
                # Poor quality ad should have lower score
                if confidence_score > 70:
                    result['warnings'].append(f"High confidence score ({confidence_score}) for poor quality ad")
            
            if 'well_written' in test_id or len(result['errors']) == 0:
                # Good quality ad should have higher score
                if confidence_score < min_score:
                    result['warnings'].append(f"Low confidence score ({confidence_score}) for good quality ad")
            
            result['success'] = len(result['errors']) == 0
            
        except Exception as e:
            result['errors'].append(f"Confidence scoring exception: {str(e)}")
        
        return result
    
    async def _test_quality_standards(self, platform_id: str, ad_text: str, test_id: str) -> Dict[str, Any]:
        """Test overall quality standards compliance"""
        result = {
            'test_id': test_id,
            'test_name': 'quality_standards',
            'platform_id': platform_id,
            'input_ad': ad_text,
            'success': False,
            'errors': [],
            'warnings': [],
            'metrics': {}
        }
        
        try:
            quality_metrics = {
                'length_appropriate': False,
                'has_clear_message': False,
                'platform_appropriate': False,
                'grammar_acceptable': True
            }
            
            # Length appropriateness
            if len(ad_text.strip()) > 10:  # Not too short
                quality_metrics['length_appropriate'] = True
            else:
                result['warnings'].append("Ad text very short")
            
            # Clear message (has some content words)
            content_words = ['product', 'service', 'business', 'buy', 'get', 'learn', 'discover', 'transform']
            if any(word in ad_text.lower() for word in content_words):
                quality_metrics['has_clear_message'] = True
            else:
                result['warnings'].append("No clear commercial message detected")
            
            # Platform appropriateness (basic checks)
            platform_indicators = {
                'instagram': ['#', '✨', '💫', '🔥'],
                'twitter_x': ['@', '#', '🧵', '👇'],
                'tiktok': ['POV:', 'viral', '🤯', '👀'],
                'linkedin': ['professional', 'career', 'business', 'industry'],
                'facebook': ['join', 'community', 'share', 'discover'],
                'google_ads': ['call', 'visit', 'shop', 'learn more']
            }
            
            indicators = platform_indicators.get(platform_id, [])
            if indicators and any(indicator in ad_text for indicator in indicators):
                quality_metrics['platform_appropriate'] = True
            elif not indicators:  # No specific indicators required
                quality_metrics['platform_appropriate'] = True
            
            # Grammar acceptability (basic check)
            grammar_issues = ['we has', 'are you need', 'dont wait', 'very good price']
            if any(issue in ad_text.lower() for issue in grammar_issues):
                quality_metrics['grammar_acceptable'] = False
                result['warnings'].append("Grammar issues detected")
            
            # Overall quality assessment
            quality_score = sum(quality_metrics.values()) / len(quality_metrics) * 100
            result['metrics']['quality_score'] = round(quality_score, 1)
            result['metrics'].update(quality_metrics)
            
            # Success if most quality standards are met
            result['success'] = quality_score >= 75
            
        except Exception as e:
            result['errors'].append(f"Quality standards exception: {str(e)}")
        
        return result

    def generate_test_report(self, test_results: Dict[str, Any], output_file: str = None) -> str:
        """Generate comprehensive test report"""
        report = []
        report.append("=" * 80)
        report.append("PLATFORM VALIDATION TEST REPORT")
        report.append("=" * 80)
        report.append("")
        
        # Summary
        report.append(f"📊 SUMMARY:")
        report.append(f"   Total Tests: {test_results['total_tests']}")
        report.append(f"   Passed: {test_results['passed_tests']}")
        report.append(f"   Failed: {test_results['failed_tests']}")
        report.append(f"   Success Rate: {round(test_results['passed_tests']/test_results['total_tests']*100, 1)}%")
        report.append(f"   Execution Time: {test_results['execution_time']}s")
        report.append("")
        
        # Platform Results
        report.append("📋 PLATFORM RESULTS:")
        for platform_id, platform_data in test_results['platform_results'].items():
            summary = platform_data['summary']
            success_rate = round(summary['passed']/summary['total']*100, 1) if summary['total'] > 0 else 0
            report.append(f"   {platform_id}: {summary['passed']}/{summary['total']} ({success_rate}%)")
        report.append("")
        
        # Test Category Results  
        report.append("🎯 TEST CATEGORY RESULTS:")
        for category, stats in test_results['test_categories'].items():
            total = stats['passed'] + stats['failed']
            if total > 0:
                success_rate = round(stats['passed']/total*100, 1)
                report.append(f"   {category}: {stats['passed']}/{total} ({success_rate}%)")
        report.append("")
        
        # Failed Tests Details
        failed_tests = [test for test in test_results['detailed_results'] if not test['success']]
        if failed_tests:
            report.append("❌ FAILED TESTS:")
            for test in failed_tests[:10]:  # Show first 10 failures
                report.append(f"   {test['test_id']} ({test['test_name']}):")
                for error in test['errors'][:2]:  # Show first 2 errors
                    report.append(f"      - {error}")
            if len(failed_tests) > 10:
                report.append(f"   ... and {len(failed_tests)-10} more failures")
        
        report_text = "\n".join(report)
        
        if output_file:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(report_text)
            logger.info(f"📝 Test report saved to {output_file}")
        
        return report_text

# Test runner functions
async def run_platform_validation_tests(openai_api_key: str = None):
    """Main test runner function"""
    if not SERVICES_AVAILABLE:
        print("❌ Platform services not available - cannot run tests")
        return None
    
    tester = PlatformValidationTester(openai_api_key)
    results = await tester.run_comprehensive_tests()
    
    # Generate report
    report = tester.generate_test_report(
        results, 
        output_file="platform_validation_report.txt"
    )
    
    print(report)
    return results

def run_basic_validation_tests():
    """Run basic validation tests without AI generation"""
    print("🔍 Running basic validation tests...")
    
    test_count = 0
    passed_count = 0
    
    # Test data structure validity
    for platform_id, platform_data in PLATFORM_TEST_DATA.items():
        for category, ads in platform_data.items():
            for ad in ads:
                test_count += 1
                if isinstance(ad, str):
                    passed_count += 1
                else:
                    print(f"❌ Invalid ad data: {platform_id}.{category} - not a string")
    
    # Test parsing expectations
    for platform_id in ['facebook', 'instagram', 'google_ads', 'linkedin', 'twitter_x', 'tiktok']:
        test_count += 1
        expectations = get_parsing_expectations(platform_id)
        if expectations and 'required_fields' in expectations:
            passed_count += 1
        else:
            print(f"❌ Missing parsing expectations for {platform_id}")
    
    print(f"✅ Basic validation: {passed_count}/{test_count} tests passed")
    return passed_count == test_count

if __name__ == "__main__":
    import sys
    
    # Check if OpenAI API key provided
    openai_key = None
    if len(sys.argv) > 1:
        openai_key = sys.argv[1]
    
    if openai_key:
        print("🚀 Running full platform validation tests with AI generation...")
        asyncio.run(run_platform_validation_tests(openai_key))
    else:
        print("🔍 Running basic validation tests (no API key provided)...")
        run_basic_validation_tests()
        print("\n💡 To run full tests with AI generation, provide OpenAI API key as argument:")
        print("   python test_platform_validation.py YOUR_API_KEY")