#!/usr/bin/env python3
"""
Simplified test suite for AdCopySurge tools that doesn't require ML dependencies.
Tests core functionality without heavy ML models.
"""
import sys
import os
import json
from datetime import datetime
from typing import Dict, Any

# Add the app directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))


class SimpleAdCopyTest:
    """Simplified test suite focusing on core logic."""
    
    def __init__(self):
        self.results = {
            'timestamp': datetime.utcnow().isoformat(),
            'test_results': {},
            'issues_found': [],
            'summary': {}
        }
    
    def log_result(self, test_name: str, success: bool, details: Dict[str, Any] = None):
        """Log test result."""
        self.results['test_results'][test_name] = {
            'success': success,
            'details': details or {},
            'timestamp': datetime.utcnow().isoformat()
        }
    
    def add_issue(self, test_name: str, severity: str, description: str):
        """Add issue."""
        self.results['issues_found'].append({
            'test': test_name,
            'severity': severity,
            'description': description
        })

    def test_readability_analyzer_basic(self):
        """Test readability analyzer without ML dependencies."""
        print("🔍 Testing Tool 1: Readability Analyzer (Basic)")
        
        try:
            # Test textstat import
            import textstat
            
            # Test basic functionality
            test_text = "Get started today with our amazing solution!"
            
            # Test Flesch reading ease
            flesch_score = textstat.flesch_reading_ease(test_text)
            grade_level = textstat.flesch_kincaid_grade(test_text)
            
            # Validate results
            if 0 <= flesch_score <= 100:
                self.log_result('readability_flesch', True, {
                    'flesch_score': flesch_score,
                    'grade_level': grade_level,
                    'text_length': len(test_text)
                })
            else:
                self.add_issue('readability_flesch', 'high', f'Flesch score out of range: {flesch_score}')
                self.log_result('readability_flesch', False)
            
        except ImportError as e:
            self.add_issue('readability_analyzer', 'critical', f'Missing textstat dependency: {e}')
            self.log_result('readability_analyzer', False)
        except Exception as e:
            self.add_issue('readability_analyzer', 'critical', f'Unexpected error: {e}')
            self.log_result('readability_analyzer', False)
        
        print("✅ Readability Analyzer basic test completed")

    def test_cta_analyzer_logic(self):
        """Test CTA analyzer logic without external dependencies."""
        print("🔍 Testing Tool 3: CTA Analyzer Logic")
        
        try:
            # Test CTA word categorization logic
            strong_cta_words = [
                'get', 'start', 'try', 'download', 'claim', 'grab', 'discover',
                'unlock', 'access', 'join', 'register', 'subscribe', 'buy'
            ]
            
            weak_cta_words = [
                'learn', 'read', 'see', 'view', 'check', 'browse', 'explore'
            ]
            
            urgency_words = [
                'now', 'today', 'immediately', 'instantly', 'quick', 'fast',
                'limited', 'expires', 'deadline', 'hurry'
            ]
            
            # Test CTAs
            test_ctas = [
                ("Get Started Now", "strong_with_urgency"),
                ("Learn More", "weak_without_urgency"),
                ("Claim Your Free Trial Today", "strong_with_urgency"),
                ("Click Here", "weak_without_urgency"),
                ("Start Free Trial", "strong_without_urgency")
            ]
            
            results = []
            for cta, expected_type in test_ctas:
                cta_lower = cta.lower()
                
                has_strong_word = any(word in cta_lower for word in strong_cta_words)
                has_weak_word = any(word in cta_lower for word in weak_cta_words)
                has_urgency = any(word in cta_lower for word in urgency_words)
                
                # Basic scoring logic
                score = 50  # Base score
                if has_strong_word:
                    score += 25
                if has_weak_word:
                    score -= 15
                if has_urgency:
                    score += 15
                
                results.append({
                    'cta': cta,
                    'expected': expected_type,
                    'has_strong': has_strong_word,
                    'has_weak': has_weak_word,
                    'has_urgency': has_urgency,
                    'score': score
                })
            
            # Validate results
            success = True
            for result in results:
                if result['expected'] == 'strong_with_urgency':
                    if not (result['has_strong'] and result['has_urgency']):
                        success = False
                        self.add_issue('cta_logic', 'medium', 
                                     f"CTA '{result['cta']}' should have strong word and urgency")
            
            self.log_result('cta_analyzer_logic', success, {
                'test_cases': len(test_ctas),
                'results': results
            })
            
        except Exception as e:
            self.add_issue('cta_analyzer', 'critical', f'CTA logic test failed: {e}')
            self.log_result('cta_analyzer_logic', False)
        
        print("✅ CTA Analyzer logic test completed")

    def test_platform_optimization_logic(self):
        """Test platform-specific optimization logic."""
        print("🔍 Testing Tool 4: Platform Optimization Logic")
        
        try:
            # Platform guidelines (from the code)
            platform_guidelines = {
                'facebook': {
                    'ideal_headline_words': (5, 7),
                    'ideal_body_chars': (90, 125)
                },
                'google': {
                    'max_headline_chars': 30,
                    'max_description_chars': 90
                },
                'linkedin': {
                    'professional_words': ['professional', 'business', 'career', 'industry', 'expertise'],
                    'min_body_chars': 150
                },
                'tiktok': {
                    'max_total_chars': 80,
                    'casual_indicators': ['!', 'wow', 'amazing', 'incredible']
                }
            }
            
            # Test ads for each platform
            test_ads = [
                {
                    'platform': 'facebook',
                    'headline': 'Start Your Business Today',  # 4 words
                    'body': 'Transform your life with our proven system that helps thousands succeed every day.',  # 100 chars
                    'expected_score_range': (80, 100)
                },
                {
                    'platform': 'google', 
                    'headline': 'Best CRM Software',  # 24 chars
                    'body': 'Increase sales by 300%.',  # 23 chars
                    'expected_score_range': (85, 100)
                },
                {
                    'platform': 'linkedin',
                    'headline': 'Professional Development Program',
                    'body': 'Our comprehensive business training program helps industry professionals advance their careers with proven expertise and networking opportunities.',  # 150+ chars
                    'expected_score_range': (80, 100)
                },
                {
                    'platform': 'tiktok',
                    'headline': 'OMG!',
                    'body': 'This is incredible! You need this!',  # Very short + casual
                    'expected_score_range': (85, 100)
                }
            ]
            
            results = []
            for ad in test_ads:
                score = 75  # Base score
                platform = ad['platform']
                
                # Facebook logic
                if platform == 'facebook':
                    headline_words = len(ad['headline'].split())
                    min_words, max_words = platform_guidelines['facebook']['ideal_headline_words']
                    if min_words <= headline_words <= max_words:
                        score += 15
                    
                    body_length = len(ad['body'])
                    min_chars, max_chars = platform_guidelines['facebook']['ideal_body_chars']
                    if min_chars <= body_length <= max_chars:
                        score += 10
                
                # Google logic
                elif platform == 'google':
                    if len(ad['headline']) <= platform_guidelines['google']['max_headline_chars']:
                        score += 20
                    if len(ad['body']) <= platform_guidelines['google']['max_description_chars']:
                        score += 15
                
                # LinkedIn logic
                elif platform == 'linkedin':
                    professional_words = platform_guidelines['linkedin']['professional_words']
                    if any(word in ad['body'].lower() for word in professional_words):
                        score += 15
                    if len(ad['body']) >= platform_guidelines['linkedin']['min_body_chars']:
                        score += 10
                
                # TikTok logic
                elif platform == 'tiktok':
                    total_length = len(ad['headline'] + ad['body'])
                    if total_length <= platform_guidelines['tiktok']['max_total_chars']:
                        score += 25
                    
                    casual_indicators = platform_guidelines['tiktok']['casual_indicators']
                    if any(indicator in ad['body'].lower() for indicator in casual_indicators):
                        score += 10
                
                score = min(100, score)
                results.append({
                    'platform': platform,
                    'calculated_score': score,
                    'expected_range': ad['expected_score_range'],
                    'meets_expectation': ad['expected_score_range'][0] <= score <= ad['expected_score_range'][1]
                })
            
            # Check if all ads meet expectations
            success = all(result['meets_expectation'] for result in results)
            
            self.log_result('platform_optimization_logic', success, {
                'test_cases': len(test_ads),
                'results': results,
                'all_passed': success
            })
            
            if not success:
                failed_platforms = [r['platform'] for r in results if not r['meets_expectation']]
                self.add_issue('platform_optimization', 'medium', 
                             f"Platform scoring failed for: {failed_platforms}")
            
        except Exception as e:
            self.add_issue('platform_optimization', 'critical', f'Platform logic test failed: {e}')
            self.log_result('platform_optimization_logic', False)
        
        print("✅ Platform Optimization logic test completed")

    def test_scoring_weights_logic(self):
        """Test performance prediction scoring weights."""
        print("🔍 Testing Tool 7: Performance Prediction Weights")
        
        try:
            # Scoring weights from the code
            weights = {
                'clarity': 0.2,
                'persuasion': 0.25,
                'emotion': 0.2,
                'cta': 0.25,
                'platform_fit': 0.1
            }
            
            # Test if weights sum to 1.0
            total_weight = sum(weights.values())
            if abs(total_weight - 1.0) > 0.001:  # Allow small floating point errors
                self.add_issue('scoring_weights', 'high', f'Weights sum to {total_weight}, should be 1.0')
                success = False
            else:
                success = True
            
            # Test scoring calculation
            test_scores = [
                {'clarity': 80, 'persuasion': 75, 'emotion': 70, 'cta': 85, 'platform_fit': 90},
                {'clarity': 60, 'persuasion': 50, 'emotion': 40, 'cta': 45, 'platform_fit': 55},
                {'clarity': 95, 'persuasion': 90, 'emotion': 85, 'cta': 95, 'platform_fit': 100}
            ]
            
            calculation_results = []
            for scores in test_scores:
                overall = (
                    scores['clarity'] * weights['clarity'] +
                    scores['persuasion'] * weights['persuasion'] +
                    scores['emotion'] * weights['emotion'] +
                    scores['cta'] * weights['cta'] +
                    scores['platform_fit'] * weights['platform_fit']
                )
                
                calculation_results.append({
                    'input_scores': scores,
                    'calculated_overall': round(overall, 1),
                    'in_valid_range': 0 <= overall <= 100
                })
            
            # Check if all calculations are valid
            all_valid = all(result['in_valid_range'] for result in calculation_results)
            if not all_valid:
                self.add_issue('scoring_weights', 'high', 'Some score calculations out of range')
                success = False
            
            self.log_result('scoring_weights_logic', success, {
                'weight_sum': total_weight,
                'weights_valid': abs(total_weight - 1.0) <= 0.001,
                'calculation_results': calculation_results,
                'all_calculations_valid': all_valid
            })
            
        except Exception as e:
            self.add_issue('scoring_weights', 'critical', f'Scoring weights test failed: {e}')
            self.log_result('scoring_weights_logic', False)
        
        print("✅ Performance Prediction weights test completed")

    def test_api_structure_validation(self):
        """Test API structure and data models."""
        print("🔍 Testing API Structure & Data Models")
        
        try:
            # Test if we can import and create the data models
            from app.api.ads import AdInput, CompetitorAd
            from pydantic import ValidationError
            
            # Test valid AdInput creation
            try:
                valid_ad = AdInput(
                    headline="Test Headline",
                    body_text="This is a test ad body.",
                    cta="Get Started",
                    platform="facebook"
                )
                
                # Check required fields
                required_fields = ['headline', 'body_text', 'cta', 'platform']
                has_all_fields = all(hasattr(valid_ad, field) for field in required_fields)
                
                if has_all_fields:
                    self.log_result('api_adinput_valid', True, {
                        'headline': valid_ad.headline,
                        'platform': valid_ad.platform
                    })
                else:
                    missing = [f for f in required_fields if not hasattr(valid_ad, f)]
                    self.add_issue('api_structure', 'high', f'AdInput missing fields: {missing}')
                    self.log_result('api_adinput_valid', False)
                    
            except ValidationError as e:
                self.add_issue('api_structure', 'high', f'AdInput validation failed: {e}')
                self.log_result('api_adinput_valid', False)
            
            # Test CompetitorAd creation
            try:
                competitor_ad = CompetitorAd(
                    headline="Competitor Headline",
                    body_text="Competitor ad body text.",
                    cta="Try Now",
                    platform="facebook"
                )
                
                self.log_result('api_competitor_valid', True, {
                    'headline': competitor_ad.headline,
                    'platform': competitor_ad.platform
                })
                
            except ValidationError as e:
                self.add_issue('api_structure', 'high', f'CompetitorAd validation failed: {e}')
                self.log_result('api_competitor_valid', False)
            
        except ImportError as e:
            self.add_issue('api_structure', 'critical', f'Cannot import API models: {e}')
            self.log_result('api_structure_validation', False)
        except Exception as e:
            self.add_issue('api_structure', 'critical', f'API structure test failed: {e}')
            self.log_result('api_structure_validation', False)
        
        print("✅ API Structure validation completed")

    def run_all_tests(self):
        """Run all simplified tests."""
        print("🚀 Starting Simplified AdCopySurge Test Suite")
        print("=" * 60)
        
        # Run tests
        self.test_readability_analyzer_basic()
        self.test_cta_analyzer_logic()
        self.test_platform_optimization_logic()
        self.test_scoring_weights_logic()
        self.test_api_structure_validation()
        
        # Generate summary
        total_tests = len(self.results['test_results'])
        successful_tests = sum(1 for test in self.results['test_results'].values() if test['success'])
        failed_tests = total_tests - successful_tests
        
        success_rate = (successful_tests / total_tests * 100) if total_tests > 0 else 0
        
        self.results['summary'] = {
            'total_tests': total_tests,
            'successful_tests': successful_tests,
            'failed_tests': failed_tests,
            'success_rate': round(success_rate, 1),
            'total_issues': len(self.results['issues_found']),
            'critical_issues': len([i for i in self.results['issues_found'] if i['severity'] == 'critical'])
        }
        
        print("\n" + "=" * 60)
        print("🏁 Test Suite Completed!")
        print(f"📊 Results: {successful_tests}/{total_tests} tests passed ({success_rate:.1f}%)")
        print(f"🚨 Issues: {len(self.results['issues_found'])} total")
        
        # Show critical issues
        critical_issues = [i for i in self.results['issues_found'] if i['severity'] == 'critical']
        if critical_issues:
            print(f"⚠️  Critical Issues:")
            for issue in critical_issues:
                print(f"   • {issue['test']}: {issue['description']}")
        
        return self.results

    def save_results(self, filename: str = None):
        """Save results to JSON file."""
        if not filename:
            filename = f"simple_test_results_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json"
        
        with open(filename, 'w') as f:
            json.dump(self.results, f, indent=2, default=str)
        
        print(f"📄 Results saved to: {filename}")
        return filename


def main():
    """Run the simplified test suite."""
    test_suite = SimpleAdCopyTest()
    results = test_suite.run_all_tests()
    
    # Save results
    results_file = test_suite.save_results()
    
    print(f"\n✅ Testing completed. Results: {results_file}")
    return results, results_file


if __name__ == "__main__":
    main()
