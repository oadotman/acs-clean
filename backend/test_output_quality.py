#!/usr/bin/env python3
"""
Output Quality Verification Tests

Tests that generated content meets platform requirements and quality standards:
- Content structure validation
- Character limit enforcement
- Language quality assessment
- Platform-specific requirements
- Retry logic effectiveness
- Confidence score accuracy
"""

import asyncio
import json
import logging
import time
import re
from typing import Dict, List, Any, Tuple
from dataclasses import asdict

# Import services
try:
    from app.services.platform_ad_generator import PlatformAdGenerator
    from app.services.content_validator import ContentValidator
    from app.services.platform_registry import get_platform_config
    from test_data_comprehensive import get_test_ads_for_platform, get_quality_criteria
    SERVICES_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Could not import platform services: {e}")
    SERVICES_AVAILABLE = False

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class QualityTestResult:
    """Result of output quality test"""
    def __init__(self):
        self.test_id = ""
        self.platform_id = ""
        self.input_ad = ""
        self.generated_content = None
        self.success = False
        self.quality_score = 0.0
        self.errors = []
        self.warnings = []
        self.metrics = {}
        self.validation_details = {}

class OutputQualityTester:
    """Tests output quality across all platforms"""
    
    def __init__(self, openai_api_key: str):
        if not SERVICES_AVAILABLE:
            raise ImportError("Platform services not available")
        
        self.openai_api_key = openai_api_key
        self.generator = PlatformAdGenerator(openai_api_key)
        self.validator = ContentValidator()
        self.platforms = ['facebook', 'instagram', 'google_ads', 'linkedin', 'twitter_x', 'tiktok']
        
    async def run_quality_tests(self) -> Dict[str, Any]:
        """Run comprehensive quality tests across all platforms"""
        logger.info("🎯 Starting output quality verification tests...")
        
        start_time = time.time()
        test_results = {
            'total_tests': 0,
            'passed_tests': 0,
            'failed_tests': 0,
            'quality_metrics': {
                'average_quality_score': 0.0,
                'character_limit_violations': 0,
                'template_phrase_violations': 0,
                'grammar_issues': 0,
                'retry_successes': 0,
                'confidence_score_accuracy': 0.0
            },
            'platform_results': {},
            'detailed_results': [],
            'execution_time': 0
        }
        
        total_quality_score = 0.0
        quality_test_count = 0
        
        # Test each platform
        for platform_id in self.platforms:
            logger.info(f"🔍 Testing output quality for {platform_id}...")
            platform_results = await self._test_platform_quality(platform_id)
            test_results['platform_results'][platform_id] = platform_results
            
            # Update counters
            for test_result in platform_results['tests']:
                test_results['total_tests'] += 1
                if test_result['success']:
                    test_results['passed_tests'] += 1
                else:
                    test_results['failed_tests'] += 1
                
                if test_result['quality_score'] > 0:
                    total_quality_score += test_result['quality_score']
                    quality_test_count += 1
                
                # Update quality metrics
                metrics = test_result.get('metrics', {})
                if metrics.get('character_violations', 0) > 0:
                    test_results['quality_metrics']['character_limit_violations'] += 1
                if metrics.get('template_phrases_found', 0) > 0:
                    test_results['quality_metrics']['template_phrase_violations'] += 1
                if metrics.get('grammar_issues', 0) > 0:
                    test_results['quality_metrics']['grammar_issues'] += 1
                if metrics.get('retry_successful', False):
                    test_results['quality_metrics']['retry_successes'] += 1
                
                test_results['detailed_results'].append(test_result)
        
        # Calculate averages
        if quality_test_count > 0:
            test_results['quality_metrics']['average_quality_score'] = round(
                total_quality_score / quality_test_count, 1
            )
        
        test_results['execution_time'] = round(time.time() - start_time, 2)
        
        logger.info(f"✅ Quality tests completed in {test_results['execution_time']}s")
        logger.info(f"📊 Average quality score: {test_results['quality_metrics']['average_quality_score']}/100")
        
        return test_results
    
    async def _test_platform_quality(self, platform_id: str) -> Dict[str, Any]:
        """Test output quality for specific platform"""
        platform_test_data = get_test_ads_for_platform(platform_id)
        platform_config = get_platform_config(platform_id)
        
        platform_results = {
            'platform_id': platform_id,
            'tests': [],
            'summary': {
                'total': 0,
                'passed': 0,
                'failed': 0,
                'average_quality': 0.0
            }
        }
        
        total_quality = 0.0
        quality_count = 0
        
        # Test different categories of ads
        for category, ads in platform_test_data.items():
            if category == 'edge_cases':
                # Skip empty ads and extreme edge cases for quality testing
                ads = [ad for ad in ads if ad and len(ad.strip()) > 5]
            
            for i, ad_text in enumerate(ads[:2]):  # Test first 2 ads per category
                if not ad_text:
                    continue
                
                test_id = f"{platform_id}_{category}_{i}"
                logger.info(f"  🧪 Testing {test_id}...")
                
                result = await self._test_single_ad_quality(
                    platform_id, ad_text, test_id, category
                )
                
                platform_results['tests'].append(result)
                platform_results['summary']['total'] += 1
                
                if result['success']:
                    platform_results['summary']['passed'] += 1
                else:
                    platform_results['summary']['failed'] += 1
                
                if result['quality_score'] > 0:
                    total_quality += result['quality_score']
                    quality_count += 1
        
        if quality_count > 0:
            platform_results['summary']['average_quality'] = round(
                total_quality / quality_count, 1
            )
        
        return platform_results
    
    async def _test_single_ad_quality(self, platform_id: str, ad_text: str, test_id: str, category: str) -> Dict[str, Any]:
        """Test output quality for a single ad"""
        result = {
            'test_id': test_id,
            'platform_id': platform_id,
            'input_ad': ad_text,
            'category': category,
            'generated_content': None,
            'success': False,
            'quality_score': 0.0,
            'errors': [],
            'warnings': [],
            'metrics': {},
            'validation_details': {}
        }
        
        try:
            start_time = time.time()
            
            # Generate improved ad
            generation_result = await self.generator.generate_ad(
                text_input=ad_text,
                platform_id=platform_id,
                context={'industry': 'test', 'test_category': category}
            )
            
            generation_time = time.time() - start_time
            result['metrics']['generation_time_ms'] = round(generation_time * 1000, 2)
            result['metrics']['generation_success'] = generation_result.success
            
            if not generation_result.success:
                result['errors'].append("Content generation failed")
                result['errors'].extend(generation_result.errors)
                return result
            
            result['generated_content'] = generation_result.generated_content
            
            # Run quality assessments
            await self._assess_content_structure(result, platform_id)
            await self._assess_character_limits(result, platform_id)
            await self._assess_language_quality(result)
            await self._assess_platform_requirements(result, platform_id)
            await self._assess_confidence_accuracy(result, platform_id)
            
            # Calculate overall quality score
            result['quality_score'] = self._calculate_quality_score(result)
            
            # Success criteria
            result['success'] = (
                len(result['errors']) == 0 and
                result['quality_score'] >= 70 and
                result['metrics'].get('character_violations', 0) == 0
            )
            
        except Exception as e:
            result['errors'].append(f"Quality test exception: {str(e)}")
            logger.exception(f"Error in quality test {test_id}")
        
        return result
    
    async def _assess_content_structure(self, result: Dict, platform_id: str):
        """Assess if generated content has proper structure for platform"""
        content = result['generated_content']
        platform_config = get_platform_config(platform_id)
        
        if not platform_config:
            result['warnings'].append(f"No platform config found for {platform_id}")
            return
        
        required_fields = platform_config.required_fields
        optional_fields = platform_config.optional_fields
        
        # Check required fields are present and non-empty
        missing_required = []
        empty_required = []
        
        for field in required_fields:
            if field not in content:
                missing_required.append(field)
            elif not content[field] or (isinstance(content[field], list) and len(content[field]) == 0):
                empty_required.append(field)
        
        if missing_required:
            result['errors'].append(f"Missing required fields: {missing_required}")
        
        if empty_required:
            result['errors'].append(f"Empty required fields: {empty_required}")
        
        # Count available fields
        available_fields = [field for field in (required_fields + optional_fields) if field in content and content[field]]
        result['metrics']['structure_completeness'] = len(available_fields) / len(required_fields + optional_fields) * 100
        
        logger.debug(f"Structure assessment for {platform_id}: {len(available_fields)}/{len(required_fields + optional_fields)} fields")
    
    async def _assess_character_limits(self, result: Dict, platform_id: str):
        """Assess character limit compliance"""
        content = result['generated_content']
        platform_config = get_platform_config(platform_id)
        
        if not platform_config:
            return
        
        violations = []
        
        for field, limit in platform_config.hard_limits.items():
            if field not in content:
                continue
            
            field_content = content[field]
            
            if isinstance(field_content, list):
                # Handle multiple items (like headlines, descriptions)
                for i, item in enumerate(field_content):
                    if len(str(item)) > limit:
                        violations.append(f"{field}[{i}]: {len(str(item))}/{limit}")
            elif isinstance(field_content, str):
                if len(field_content) > limit:
                    violations.append(f"{field}: {len(field_content)}/{limit}")
        
        result['metrics']['character_violations'] = len(violations)
        if violations:
            result['errors'].extend([f"Character limit violation: {v}" for v in violations])
        
        logger.debug(f"Character limit assessment: {len(violations)} violations")
    
    async def _assess_language_quality(self, result: Dict):
        """Assess language quality and grammar"""
        content = result['generated_content']
        quality_criteria = get_quality_criteria()
        
        # Combine all text content for analysis
        all_text = []
        for field, value in content.items():
            if isinstance(value, str):
                all_text.append(value)
            elif isinstance(value, list):
                all_text.extend([str(item) for item in value if item])
        
        combined_text = " ".join(all_text).lower()
        
        # Check for template phrases
        template_issues = []
        for template in quality_criteria['forbidden_templates']:
            if template.lower() in combined_text:
                template_issues.append(template)
        
        result['metrics']['template_phrases_found'] = len(template_issues)
        if template_issues:
            result['warnings'].extend([f"Template phrase detected: {t}" for t in template_issues])
        
        # Check for grammar issues
        grammar_issues = []
        for issue in quality_criteria['grammar_issues']:
            if issue.lower() in combined_text:
                grammar_issues.append(issue)
        
        result['metrics']['grammar_issues'] = len(grammar_issues)
        if grammar_issues:
            result['errors'].extend([f"Grammar issue: {g}" for g in grammar_issues])
        
        # Basic language quality checks
        quality_score = 100
        
        # Penalty for template phrases
        quality_score -= len(template_issues) * 10
        
        # Penalty for grammar issues
        quality_score -= len(grammar_issues) * 15
        
        # Check for repetitive words
        words = combined_text.split()
        if len(words) > 0:
            unique_words = set(words)
            repetition_ratio = len(words) / len(unique_words)
            if repetition_ratio > 2.0:  # High repetition
                quality_score -= 20
                result['warnings'].append(f"High word repetition: {repetition_ratio:.1f}")
        
        result['metrics']['language_quality_score'] = max(0, quality_score)
        
        logger.debug(f"Language quality score: {quality_score}/100")
    
    async def _assess_platform_requirements(self, result: Dict, platform_id: str):
        """Assess platform-specific requirements"""
        content = result['generated_content']
        
        platform_specific_checks = {
            'instagram': self._check_instagram_requirements,
            'google_ads': self._check_google_ads_requirements,
            'twitter_x': self._check_twitter_requirements,
            'linkedin': self._check_linkedin_requirements,
            'facebook': self._check_facebook_requirements,
            'tiktok': self._check_tiktok_requirements
        }
        
        checker = platform_specific_checks.get(platform_id)
        if checker:
            await checker(result, content)
        
        logger.debug(f"Platform requirements assessed for {platform_id}")
    
    async def _check_instagram_requirements(self, result: Dict, content: Dict):
        """Check Instagram-specific requirements"""
        # Should have engaging body content
        body = content.get('body', '')
        if len(body) < 50:
            result['warnings'].append("Instagram body text quite short")
        
        # Check for hashtags (optional but recommended)
        hashtags = content.get('hashtags', [])
        if not hashtags or len(hashtags) == 0:
            result['warnings'].append("No hashtags provided for Instagram")
        elif len(hashtags) > 30:
            result['warnings'].append(f"Too many hashtags: {len(hashtags)} (recommended: 5-15)")
        
        # Check for emojis (Instagram-appropriate)
        emoji_pattern = re.compile(r'[\U0001F600-\U0001F64F]|[\U0001F300-\U0001F5FF]|[\U0001F680-\U0001F6FF]|[\U0001F1E0-\U0001F1FF]')
        has_emojis = bool(emoji_pattern.search(body))
        result['metrics']['has_emojis'] = has_emojis
        
        if not has_emojis:
            result['warnings'].append("No emojis detected (recommended for Instagram)")
    
    async def _check_google_ads_requirements(self, result: Dict, content: Dict):
        """Check Google Ads-specific requirements"""
        headlines = content.get('headlines', [])
        descriptions = content.get('descriptions', [])
        
        # Should have multiple headlines and descriptions
        if len(headlines) < 3:
            result['warnings'].append(f"Only {len(headlines)} headlines (recommended: 3+)")
        
        if len(descriptions) < 2:
            result['warnings'].append(f"Only {len(descriptions)} descriptions (recommended: 2+)")
        
        # Headlines should be unique
        if len(headlines) != len(set(headlines)):
            result['errors'].append("Duplicate headlines detected")
        
        # Descriptions should be unique
        if len(descriptions) != len(set(descriptions)):
            result['errors'].append("Duplicate descriptions detected")
        
        # Check for strong call-to-action
        all_text = ' '.join(headlines + descriptions).lower()
        action_words = ['buy', 'shop', 'call', 'visit', 'download', 'get', 'try', 'start', 'learn']
        has_cta = any(word in all_text for word in action_words)
        
        if not has_cta:
            result['warnings'].append("No clear call-to-action detected")
    
    async def _check_twitter_requirements(self, result: Dict, content: Dict):
        """Check Twitter/X-specific requirements"""
        body = content.get('body', '')
        
        # Should be concise and engaging
        if len(body) > 250:
            result['warnings'].append("Twitter content quite long (consider shorter)")
        
        # Check for engagement elements
        engagement_indicators = ['?', '!', '@', '#']
        has_engagement = any(indicator in body for indicator in engagement_indicators)
        
        if not has_engagement:
            result['warnings'].append("No engagement indicators (hashtags, mentions, questions)")
        
        # Check character efficiency (not just length)
        words = body.split()
        if len(words) > 0:
            chars_per_word = len(body) / len(words)
            if chars_per_word > 8:  # Very long average words
                result['warnings'].append("Consider shorter, punchier words for Twitter")
    
    async def _check_linkedin_requirements(self, result: Dict, content: Dict):
        """Check LinkedIn-specific requirements"""
        headline = content.get('headline', '')
        body = content.get('body', '')
        
        # Should have professional tone
        professional_words = ['professional', 'career', 'business', 'industry', 'expertise', 'solution', 'strategy']
        all_text = (headline + ' ' + body).lower()
        
        has_professional_tone = any(word in all_text for word in professional_words)
        if not has_professional_tone:
            result['warnings'].append("Consider more professional language for LinkedIn")
        
        # Should have substantive content
        if len(body) < 100:
            result['warnings'].append("LinkedIn content quite brief (consider more detail)")
        
        # Check for business value proposition
        value_words = ['results', 'roi', 'growth', 'efficiency', 'success', 'improve', 'increase']
        has_value_prop = any(word in all_text for word in value_words)
        
        if not has_value_prop:
            result['warnings'].append("Consider adding clear business value proposition")
    
    async def _check_facebook_requirements(self, result: Dict, content: Dict):
        """Check Facebook-specific requirements"""
        headline = content.get('headline', '')
        body = content.get('body', '')
        cta = content.get('cta', '')
        
        # Should have clear structure
        if not headline:
            result['errors'].append("Facebook ads should have headlines")
        
        if not body:
            result['errors'].append("Facebook ads should have body text")
        
        if not cta:
            result['warnings'].append("Facebook ads benefit from clear CTAs")
        
        # Check for storytelling elements
        story_indicators = ['discover', 'story', 'journey', 'transform', 'experience']
        all_text = (headline + ' ' + body).lower()
        
        has_story_element = any(indicator in all_text for indicator in story_indicators)
        if not has_story_element:
            result['warnings'].append("Consider adding storytelling elements for Facebook")
    
    async def _check_tiktok_requirements(self, result: Dict, content: Dict):
        """Check TikTok-specific requirements"""
        body = content.get('body', '')
        
        # Should be trendy and engaging
        trendy_words = ['pov:', 'viral', 'hack', 'trend', 'challenge', 'storytime', 'plot twist']
        has_trendy_language = any(word in body.lower() for word in trendy_words)
        
        if not has_trendy_language:
            result['warnings'].append("Consider using more TikTok-style language")
        
        # Check for engagement hooks
        hooks = ['wait for it', 'this changed everything', 'you won\'t believe', 'day 1 of', 'rating']
        has_hook = any(hook in body.lower() for hook in hooks)
        
        if not has_hook:
            result['warnings'].append("Consider adding an engagement hook")
        
        # Should be action-oriented
        if not ('!' in body or '?' in body):
            result['warnings'].append("TikTok content benefits from excitement/questions")
    
    async def _assess_confidence_accuracy(self, result: Dict, platform_id: str):
        """Assess if confidence scores accurately reflect quality"""
        content = result['generated_content']
        
        try:
            # Use validator to get confidence score
            validation_result = self.validator.validate_and_sanitize(
                content, platform_id, strict_mode=False
            )
            
            confidence_score = validation_result.confidence_score
            result['metrics']['confidence_score'] = confidence_score
            
            # Assess accuracy by comparing to actual quality issues found
            error_count = len(result['errors'])
            warning_count = len(result['warnings'])
            
            # Expected confidence based on issues found
            expected_confidence = 100
            expected_confidence -= error_count * 20  # Major issues
            expected_confidence -= warning_count * 10  # Minor issues
            expected_confidence = max(0, expected_confidence)
            
            confidence_diff = abs(confidence_score - expected_confidence)
            result['metrics']['confidence_accuracy'] = max(0, 100 - confidence_diff)
            
            if confidence_diff > 30:
                result['warnings'].append(f"Confidence score ({confidence_score}) doesn't match quality assessment ({expected_confidence})")
            
        except Exception as e:
            result['warnings'].append(f"Could not assess confidence accuracy: {e}")
    
    def _calculate_quality_score(self, result: Dict) -> float:
        """Calculate overall quality score"""
        base_score = 100.0
        
        # Deduct for errors (major issues)
        base_score -= len(result['errors']) * 20
        
        # Deduct for warnings (minor issues)  
        base_score -= len(result['warnings']) * 5
        
        # Factor in specific metrics
        metrics = result['metrics']
        
        # Structure completeness bonus/penalty
        structure_completeness = metrics.get('structure_completeness', 50)
        if structure_completeness < 100:
            base_score -= (100 - structure_completeness) * 0.3
        
        # Language quality factor
        lang_quality = metrics.get('language_quality_score', 70)
        base_score = (base_score * 0.7) + (lang_quality * 0.3)
        
        # Character violations are serious
        char_violations = metrics.get('character_violations', 0)
        base_score -= char_violations * 25
        
        return max(0.0, min(100.0, base_score))
    
    def generate_quality_report(self, test_results: Dict[str, Any], output_file: str = None) -> str:
        """Generate comprehensive quality report"""
        report = []
        report.append("=" * 80)
        report.append("OUTPUT QUALITY VERIFICATION REPORT")
        report.append("=" * 80)
        report.append("")
        
        # Summary
        total_tests = test_results['total_tests']
        passed_tests = test_results['passed_tests']
        success_rate = round(passed_tests/total_tests*100, 1) if total_tests > 0 else 0
        
        report.append("📊 SUMMARY:")
        report.append(f"   Total Tests: {total_tests}")
        report.append(f"   Passed: {passed_tests}")
        report.append(f"   Failed: {test_results['failed_tests']}")
        report.append(f"   Success Rate: {success_rate}%")
        report.append(f"   Execution Time: {test_results['execution_time']}s")
        report.append("")
        
        # Quality Metrics
        metrics = test_results['quality_metrics']
        report.append("🎯 QUALITY METRICS:")
        report.append(f"   Average Quality Score: {metrics['average_quality_score']}/100")
        report.append(f"   Character Limit Violations: {metrics['character_limit_violations']}")
        report.append(f"   Template Phrase Violations: {metrics['template_phrase_violations']}")
        report.append(f"   Grammar Issues: {metrics['grammar_issues']}")
        report.append(f"   Retry Successes: {metrics['retry_successes']}")
        report.append("")
        
        # Platform Results
        report.append("📋 PLATFORM RESULTS:")
        for platform_id, platform_data in test_results['platform_results'].items():
            summary = platform_data['summary']
            platform_success_rate = round(summary['passed']/summary['total']*100, 1) if summary['total'] > 0 else 0
            report.append(f"   {platform_id}: {summary['passed']}/{summary['total']} ({platform_success_rate}%) - Quality: {summary['average_quality']}/100")
        report.append("")
        
        # Top Issues
        all_errors = []
        for test_result in test_results['detailed_results']:
            all_errors.extend(test_result['errors'])
        
        if all_errors:
            error_counts = {}
            for error in all_errors:
                error_type = error.split(':')[0] if ':' in error else error
                error_counts[error_type] = error_counts.get(error_type, 0) + 1
            
            report.append("❌ TOP ISSUES:")
            sorted_errors = sorted(error_counts.items(), key=lambda x: x[1], reverse=True)
            for error_type, count in sorted_errors[:5]:
                report.append(f"   {error_type}: {count} occurrences")
        
        report_text = "\n".join(report)
        
        if output_file:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(report_text)
            logger.info(f"📝 Quality report saved to {output_file}")
        
        return report_text

# Test runner function
async def run_output_quality_tests(openai_api_key: str):
    """Main quality test runner"""
    if not SERVICES_AVAILABLE:
        print("❌ Platform services not available - cannot run tests")
        return None
    
    if not openai_api_key:
        print("❌ OpenAI API key required for quality testing")
        return None
    
    tester = OutputQualityTester(openai_api_key)
    results = await tester.run_quality_tests()
    
    # Generate report
    report = tester.generate_quality_report(
        results,
        output_file="output_quality_report.txt"
    )
    
    print(report)
    return results

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("❌ OpenAI API key required for output quality tests")
        print("Usage: python test_output_quality.py YOUR_API_KEY")
        sys.exit(1)
    
    openai_key = sys.argv[1]
    asyncio.run(run_output_quality_tests(openai_key))