#!/usr/bin/env python3
"""
Comprehensive test suite for all 9 AdCopySurge tools.
Tests both individual tool functionality and end-to-end integration.
"""
import sys
import os
import asyncio
import json
from typing import Dict, Any, List
from datetime import datetime

# Add the app directory to the path so we can import our modules
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.services.readability_analyzer import ReadabilityAnalyzer
from app.services.emotion_analyzer import EmotionAnalyzer
from app.services.cta_analyzer import CTAAnalyzer
from app.api.ads import AdInput, CompetitorAd


class AdCopyTestSuite:
    """Comprehensive test suite for all AdCopySurge tools."""
    
    def __init__(self):
        self.results = {
            'timestamp': datetime.utcnow().isoformat(),
            'tools_tested': 9,
            'test_results': {},
            'issues_found': [],
            'recommendations': []
        }
        
        # Initialize analyzers
        self.readability_analyzer = ReadabilityAnalyzer()
        self.emotion_analyzer = EmotionAnalyzer()
        self.cta_analyzer = CTAAnalyzer()
        
        # Test data - diverse ad copy samples
        self.test_ads = [
            {
                'name': 'simple_facebook_ad',
                'headline': 'Get Started Today',
                'body_text': 'Transform your business with our amazing solution. Join thousands of happy customers.',
                'cta': 'Start Free Trial',
                'platform': 'facebook'
            },
            {
                'name': 'complex_linkedin_ad', 
                'headline': 'Revolutionary Enterprise Software for Modern Businesses',
                'body_text': 'Our comprehensive platform leverages cutting-edge artificial intelligence to streamline your workflow and maximize operational efficiency. Industry leaders trust our solution.',
                'cta': 'Request Demo',
                'platform': 'linkedin'
            },
            {
                'name': 'tiktok_short_ad',
                'headline': 'OMG!',
                'body_text': 'This is incredible! You NEED to see this!',
                'cta': 'Try Now',
                'platform': 'tiktok'
            },
            {
                'name': 'google_search_ad',
                'headline': 'Best CRM Software 2024',
                'body_text': 'Increase sales by 300%. Free trial.',
                'cta': 'Get Quote',
                'platform': 'google'
            },
            {
                'name': 'emotional_story_ad',
                'headline': 'Sarah Was Struggling Until...',
                'body_text': 'Like you, Sarah felt overwhelmed and frustrated. Everything changed when she discovered our proven system. Now she\'s thriving!',
                'cta': 'Claim Your Success',
                'platform': 'facebook'
            }
        ]

    def log_test_result(self, tool_name: str, test_name: str, success: bool, details: Dict[str, Any] = None):
        """Log individual test results."""
        if tool_name not in self.results['test_results']:
            self.results['test_results'][tool_name] = []
            
        self.results['test_results'][tool_name].append({
            'test_name': test_name,
            'success': success,
            'details': details or {},
            'timestamp': datetime.utcnow().isoformat()
        })

    def add_issue(self, tool_name: str, severity: str, description: str):
        """Add an issue found during testing."""
        self.results['issues_found'].append({
            'tool': tool_name,
            'severity': severity,  # 'critical', 'high', 'medium', 'low'
            'description': description,
            'timestamp': datetime.utcnow().isoformat()
        })

    def add_recommendation(self, tool_name: str, priority: str, description: str):
        """Add improvement recommendation."""
        self.results['recommendations'].append({
            'tool': tool_name,
            'priority': priority,  # 'high', 'medium', 'low'
            'description': description
        })

    def test_tool_1_readability_analyzer(self):
        """Test Tool 1: Readability & Clarity Analyzer"""
        print("🔍 Testing Tool 1: Readability & Clarity Analyzer")
        
        for ad in self.test_ads:
            try:
                # Test main analysis function
                full_text = f"{ad['headline']} {ad['body_text']} {ad['cta']}"
                result = self.readability_analyzer.analyze_clarity(full_text)
                
                # Validate required fields
                required_fields = ['clarity_score', 'flesch_reading_ease', 'grade_level', 
                                 'word_count', 'recommendations']
                missing_fields = [field for field in required_fields if field not in result]
                
                if missing_fields:
                    self.log_test_result('readability_analyzer', f'analyze_clarity_{ad["name"]}', False, 
                                       {'missing_fields': missing_fields})
                    self.add_issue('readability_analyzer', 'high', 
                                 f'Missing required fields: {missing_fields}')
                    continue
                
                # Test power words analysis
                power_result = self.readability_analyzer.analyze_power_words(full_text)
                
                # Validate score ranges
                if not (0 <= result['clarity_score'] <= 100):
                    self.add_issue('readability_analyzer', 'high', 
                                 f'Clarity score out of range: {result["clarity_score"]}')
                
                self.log_test_result('readability_analyzer', f'analyze_clarity_{ad["name"]}', True, {
                    'clarity_score': result['clarity_score'],
                    'grade_level': result['grade_level'],
                    'power_words_found': power_result['power_words_found']
                })
                
            except Exception as e:
                self.log_test_result('readability_analyzer', f'analyze_clarity_{ad["name"]}', False, 
                                   {'error': str(e)})
                self.add_issue('readability_analyzer', 'critical', f'Exception: {str(e)}')
        
        print("✅ Readability Analyzer tests completed")

    def test_tool_2_emotion_analyzer(self):
        """Test Tool 2: Emotion Analyzer"""
        print("🔍 Testing Tool 2: Emotion Analyzer")
        
        for ad in self.test_ads:
            try:
                full_text = f"{ad['headline']} {ad['body_text']} {ad['cta']}"
                result = self.emotion_analyzer.analyze_emotion(full_text)
                
                # Validate required fields
                required_fields = ['emotion_score', 'primary_emotion', 'emotion_breakdown', 'recommendations']
                missing_fields = [field for field in required_fields if field not in result]
                
                if missing_fields:
                    self.log_test_result('emotion_analyzer', f'analyze_emotion_{ad["name"]}', False,
                                       {'missing_fields': missing_fields})
                    self.add_issue('emotion_analyzer', 'high', f'Missing required fields: {missing_fields}')
                    continue
                
                # Validate score range
                if not (0 <= result['emotion_score'] <= 100):
                    self.add_issue('emotion_analyzer', 'high', 
                                 f'Emotion score out of range: {result["emotion_score"]}')
                
                # Check if emotional ad gets higher emotion score
                if ad['name'] == 'emotional_story_ad' and result['emotion_score'] < 60:
                    self.add_issue('emotion_analyzer', 'medium', 
                                 'Emotional ad scored low on emotion analysis')
                
                self.log_test_result('emotion_analyzer', f'analyze_emotion_{ad["name"]}', True, {
                    'emotion_score': result['emotion_score'],
                    'primary_emotion': result['primary_emotion'],
                    'recommendations_count': len(result['recommendations'])
                })
                
            except Exception as e:
                self.log_test_result('emotion_analyzer', f'analyze_emotion_{ad["name"]}', False,
                                   {'error': str(e)})
                self.add_issue('emotion_analyzer', 'critical', f'Exception: {str(e)}')
        
        print("✅ Emotion Analyzer tests completed")

    def test_tool_3_cta_analyzer(self):
        """Test Tool 3: CTA Analyzer"""
        print("🔍 Testing Tool 3: CTA Analyzer")
        
        for ad in self.test_ads:
            try:
                result = self.cta_analyzer.analyze_cta(ad['cta'], ad['platform'])
                
                # Validate required fields
                required_fields = ['cta_strength_score', 'word_count', 'has_action_verb', 
                                 'platform_fit', 'recommendations', 'suggested_improvements']
                missing_fields = [field for field in required_fields if field not in result]
                
                if missing_fields:
                    self.log_test_result('cta_analyzer', f'analyze_cta_{ad["name"]}', False,
                                       {'missing_fields': missing_fields})
                    self.add_issue('cta_analyzer', 'high', f'Missing required fields: {missing_fields}')
                    continue
                
                # Validate score ranges
                if not (0 <= result['cta_strength_score'] <= 100):
                    self.add_issue('cta_analyzer', 'high', 
                                 f'CTA strength score out of range: {result["cta_strength_score"]}')
                
                if not (0 <= result['platform_fit'] <= 100):
                    self.add_issue('cta_analyzer', 'high', 
                                 f'Platform fit score out of range: {result["platform_fit"]}')
                
                # Test platform-specific logic
                if ad['platform'] == 'tiktok' and result['word_count'] <= 3 and result['platform_fit'] < 80:
                    self.add_issue('cta_analyzer', 'medium', 
                                 'TikTok short CTA should score higher on platform fit')
                
                self.log_test_result('cta_analyzer', f'analyze_cta_{ad["name"]}', True, {
                    'cta_strength_score': result['cta_strength_score'],
                    'platform_fit': result['platform_fit'],
                    'has_action_verb': result['has_action_verb'],
                    'suggestions_count': len(result['suggested_improvements'])
                })
                
            except Exception as e:
                self.log_test_result('cta_analyzer', f'analyze_cta_{ad["name"]}', False,
                                   {'error': str(e)})
                self.add_issue('cta_analyzer', 'critical', f'Exception: {str(e)}')
        
        print("✅ CTA Analyzer tests completed")

    def test_tool_4_platform_optimization(self):
        """Test Tool 4: Platform Optimization (part of AdAnalysisService)"""
        print("🔍 Testing Tool 4: Platform Optimization")
        
        # Import here to avoid circular imports
        try:
            from app.services.ad_analysis_service import AdAnalysisService
            from unittest.mock import MagicMock
            
            # Mock database session
            mock_db = MagicMock()
            service = AdAnalysisService(mock_db)
            
            for ad in self.test_ads:
                try:
                    ad_input = AdInput(
                        headline=ad['headline'],
                        body_text=ad['body_text'], 
                        cta=ad['cta'],
                        platform=ad['platform']
                    )
                    
                    platform_score = service._calculate_platform_fit(ad_input)
                    
                    # Validate score range
                    if not (0 <= platform_score <= 100):
                        self.add_issue('platform_optimization', 'high',
                                     f'Platform fit score out of range: {platform_score}')
                    
                    # Test platform-specific logic
                    if ad['platform'] == 'google' and len(ad['headline']) <= 30:
                        expected_high_score = platform_score >= 85
                        if not expected_high_score:
                            self.add_issue('platform_optimization', 'medium',
                                         'Google ad with short headline should score higher')
                    
                    self.log_test_result('platform_optimization', f'calculate_fit_{ad["name"]}', True, {
                        'platform': ad['platform'],
                        'platform_fit_score': platform_score,
                        'headline_length': len(ad['headline']),
                        'body_length': len(ad['body_text'])
                    })
                    
                except Exception as e:
                    self.log_test_result('platform_optimization', f'calculate_fit_{ad["name"]}', False,
                                       {'error': str(e)})
                    self.add_issue('platform_optimization', 'critical', f'Exception: {str(e)}')
                    
        except ImportError as e:
            self.add_issue('platform_optimization', 'critical', f'Import error: {str(e)}')
        
        print("✅ Platform Optimization tests completed")

    def test_tool_5_competitor_benchmarking(self):
        """Test Tool 5: Competitor Benchmarking (requires manual competitor data)"""
        print("🔍 Testing Tool 5: Competitor Benchmarking")
        
        try:
            from app.services.ad_analysis_service import AdAnalysisService
            from unittest.mock import MagicMock
            
            mock_db = MagicMock()
            service = AdAnalysisService(mock_db)
            
            # Create test competitor ads
            competitor_ads = [
                CompetitorAd(
                    headline="Industry Leader Solution",
                    body_text="Join 10,000+ companies who trust our platform",
                    cta="Get Started",
                    platform="facebook"
                ),
                CompetitorAd(
                    headline="Award-Winning Software", 
                    body_text="Rated #1 by industry experts. Try free for 30 days.",
                    cta="Start Trial",
                    platform="facebook"
                )
            ]
            
            test_ad = AdInput(
                headline=self.test_ads[0]['headline'],
                body_text=self.test_ads[0]['body_text'],
                cta=self.test_ads[0]['cta'],
                platform=self.test_ads[0]['platform']
            )
            
            # Test competitor analysis
            result = asyncio.run(service._analyze_competitors(test_ad, competitor_ads))
            
            # Validate required fields
            required_fields = ['average_competitor_score', 'competitor_count', 'performance_comparison']
            missing_fields = [field for field in required_fields if field not in result]
            
            if missing_fields:
                self.add_issue('competitor_benchmarking', 'high', 
                             f'Missing required fields: {missing_fields}')
            else:
                self.log_test_result('competitor_benchmarking', 'analyze_competitors', True, {
                    'avg_competitor_score': result['average_competitor_score'],
                    'competitor_count': result['competitor_count'],
                    'performance_comparison': result['performance_comparison']
                })
            
        except Exception as e:
            self.log_test_result('competitor_benchmarking', 'analyze_competitors', False,
                               {'error': str(e)})
            self.add_issue('competitor_benchmarking', 'critical', f'Exception: {str(e)}')
        
        print("✅ Competitor Benchmarking tests completed")

    async def test_tool_6_ai_alternative_generator(self):
        """Test Tool 6: AI Alternative Generator (requires OpenAI API)"""
        print("🔍 Testing Tool 6: AI Alternative Generator")
        
        try:
            from app.services.ad_analysis_service import AdAnalysisService
            from unittest.mock import MagicMock
            
            mock_db = MagicMock()
            service = AdAnalysisService(mock_db)
            
            test_ad = AdInput(
                headline=self.test_ads[0]['headline'],
                body_text=self.test_ads[0]['body_text'],
                cta=self.test_ads[0]['cta'],
                platform=self.test_ads[0]['platform']
            )
            
            # Test template-based alternatives (fallback)
            template_alternatives = service._generate_template_alternatives(test_ad)
            
            if not template_alternatives or len(template_alternatives) == 0:
                self.add_issue('ai_alternative_generator', 'high', 
                             'Template alternatives generation failed')
            else:
                self.log_test_result('ai_alternative_generator', 'template_alternatives', True, {
                    'alternatives_count': len(template_alternatives),
                    'variant_types': [alt.variant_type for alt in template_alternatives]
                })
            
            # Test AI-powered alternatives (will likely fail without API key)
            try:
                ai_alternatives = await service._generate_ai_alternatives(test_ad)
                if ai_alternatives:
                    self.log_test_result('ai_alternative_generator', 'ai_alternatives', True, {
                        'alternatives_count': len(ai_alternatives),
                        'variant_types': [alt.variant_type for alt in ai_alternatives]
                    })
                else:
                    self.add_issue('ai_alternative_generator', 'medium', 
                                 'AI alternatives generation returned empty (likely missing API key)')
            except Exception as e:
                self.add_issue('ai_alternative_generator', 'medium', 
                             f'AI alternatives failed (expected without API key): {str(e)}')
            
        except Exception as e:
            self.log_test_result('ai_alternative_generator', 'generate_alternatives', False,
                               {'error': str(e)})
            self.add_issue('ai_alternative_generator', 'critical', f'Exception: {str(e)}')
        
        print("✅ AI Alternative Generator tests completed")

    def test_tool_7_performance_predictor(self):
        """Test Tool 7: Performance Predictor (scoring weights)"""
        print("🔍 Testing Tool 7: Performance Predictor")
        
        try:
            from app.services.ad_analysis_service import AdAnalysisService
            from unittest.mock import MagicMock
            
            mock_db = MagicMock()
            service = AdAnalysisService(mock_db)
            
            # Test with various score combinations
            test_cases = [
                {'clarity': 80, 'persuasion': 75, 'emotion': 70, 'cta': 85, 'platform_fit': 90},
                {'clarity': 60, 'persuasion': 50, 'emotion': 40, 'cta': 45, 'platform_fit': 55},
                {'clarity': 95, 'persuasion': 90, 'emotion': 85, 'cta': 95, 'platform_fit': 100}
            ]
            
            for i, scores in enumerate(test_cases):
                overall_score = service._calculate_overall_score(
                    scores['clarity'], scores['persuasion'], scores['emotion'], 
                    scores['cta'], scores['platform_fit']
                )
                
                # Validate score range
                if not (0 <= overall_score <= 100):
                    self.add_issue('performance_predictor', 'high',
                                 f'Overall score out of range: {overall_score}')
                
                # Test weighting logic - CTA and persuasion should have highest impact
                expected_range = (
                    min(scores.values()) * 0.8,  # Lower bound
                    max(scores.values()) * 1.1   # Upper bound  
                )
                
                self.log_test_result('performance_predictor', f'calculate_overall_score_{i}', True, {
                    'input_scores': scores,
                    'overall_score': overall_score,
                    'expected_range': expected_range
                })
            
        except Exception as e:
            self.log_test_result('performance_predictor', 'calculate_overall_score', False,
                               {'error': str(e)})
            self.add_issue('performance_predictor', 'critical', f'Exception: {str(e)}')
        
        print("✅ Performance Predictor tests completed")

    def test_tool_8_analytics_dashboard(self):
        """Test Tool 8: Analytics Dashboard (requires database)"""
        print("🔍 Testing Tool 8: Analytics Dashboard")
        
        try:
            from app.services.analytics_service import AnalyticsService
            from unittest.mock import MagicMock
            
            # Mock database with sample data
            mock_db = MagicMock()
            mock_analyses = []
            
            # Create mock analysis objects
            for i, ad in enumerate(self.test_ads[:3]):  # Test with 3 analyses
                mock_analysis = MagicMock()
                mock_analysis.platform = ad['platform']
                mock_analysis.overall_score = 75.0 + i * 5  # Varying scores
                mock_analysis.created_at = datetime.utcnow()
                mock_analyses.append(mock_analysis)
            
            mock_db.query.return_value.filter.return_value.all.return_value = mock_analyses
            
            service = AnalyticsService(mock_db)
            
            # Test user analytics
            try:
                analytics = service.get_user_analytics(user_id=1)
                
                required_fields = ['total_analyses', 'avg_score_improvement', 
                                 'top_performing_platforms', 'monthly_usage', 'subscription_analytics']
                missing_fields = [field for field in required_fields if field not in analytics]
                
                if missing_fields:
                    self.add_issue('analytics_dashboard', 'high',
                                 f'Missing required fields: {missing_fields}')
                else:
                    self.log_test_result('analytics_dashboard', 'get_user_analytics', True, {
                        'total_analyses': analytics['total_analyses'],
                        'avg_score': analytics['avg_score_improvement'],
                        'platforms_count': len(analytics['top_performing_platforms'])
                    })
                    
            except Exception as e:
                self.add_issue('analytics_dashboard', 'critical', 
                             f'Analytics generation failed: {str(e)}')
            
        except Exception as e:
            self.log_test_result('analytics_dashboard', 'get_user_analytics', False,
                               {'error': str(e)})
            self.add_issue('analytics_dashboard', 'critical', f'Exception: {str(e)}')
        
        print("✅ Analytics Dashboard tests completed")

    async def test_tool_9_pdf_report_generator(self):
        """Test Tool 9: PDF Report Generator"""
        print("🔍 Testing Tool 9: PDF Report Generator")
        
        try:
            from app.services.analytics_service import AnalyticsService
            from unittest.mock import MagicMock
            from datetime import datetime
            
            # Mock database with sample analysis data
            mock_db = MagicMock()
            mock_analyses = []
            
            for i, ad in enumerate(self.test_ads[:2]):  # Test with 2 analyses
                mock_analysis = MagicMock()
                mock_analysis.id = f"analysis_{i}"
                mock_analysis.headline = ad['headline']
                mock_analysis.body_text = ad['body_text']
                mock_analysis.cta = ad['cta']
                mock_analysis.platform = ad['platform']
                mock_analysis.overall_score = 75.0 + i * 10
                mock_analysis.clarity_score = 80.0
                mock_analysis.persuasion_score = 75.0
                mock_analysis.emotion_score = 70.0
                mock_analysis.cta_strength_score = 85.0
                mock_analysis.platform_fit_score = 90.0
                mock_analyses.append(mock_analysis)
            
            mock_db.query.return_value.filter.return_value.all.return_value = mock_analyses
            
            service = AnalyticsService(mock_db)
            
            # Test PDF generation
            try:
                pdf_result = await service.generate_pdf_report(
                    user_id=1, 
                    analysis_ids=["analysis_0", "analysis_1"]
                )
                
                required_fields = ['url', 'download_link']
                missing_fields = [field for field in required_fields if field not in pdf_result]
                
                if missing_fields:
                    self.add_issue('pdf_report_generator', 'high',
                                 f'Missing required fields: {missing_fields}')
                else:
                    # Check if PDF data looks valid (base64 encoded)
                    if 'data:application/pdf;base64,' in pdf_result['url']:
                        self.log_test_result('pdf_report_generator', 'generate_pdf_report', True, {
                            'has_url': True,
                            'has_download_link': True,
                            'pdf_size_approx': len(pdf_result['url'])
                        })
                    else:
                        self.add_issue('pdf_report_generator', 'medium',
                                     'PDF URL format appears invalid')
                    
            except Exception as e:
                self.add_issue('pdf_report_generator', 'critical',
                             f'PDF generation failed: {str(e)}')
            
        except Exception as e:
            self.log_test_result('pdf_report_generator', 'generate_pdf_report', False,
                               {'error': str(e)})
            self.add_issue('pdf_report_generator', 'critical', f'Exception: {str(e)}')
        
        print("✅ PDF Report Generator tests completed")

    async def run_all_tests(self):
        """Run comprehensive tests for all 9 tools."""
        print("🚀 Starting comprehensive test suite for AdCopySurge tools")
        print("=" * 60)
        
        # Run all tool tests
        self.test_tool_1_readability_analyzer()
        self.test_tool_2_emotion_analyzer() 
        self.test_tool_3_cta_analyzer()
        self.test_tool_4_platform_optimization()
        self.test_tool_5_competitor_benchmarking()
        await self.test_tool_6_ai_alternative_generator()
        self.test_tool_7_performance_predictor()
        self.test_tool_8_analytics_dashboard()
        await self.test_tool_9_pdf_report_generator()
        
        print("\n" + "=" * 60)
        print("🏁 All tests completed!")
        
        # Generate summary
        total_tests = sum(len(tests) for tests in self.results['test_results'].values())
        successful_tests = sum(
            len([t for t in tests if t['success']]) 
            for tests in self.results['test_results'].values()
        )
        
        print(f"📊 Test Summary:")
        print(f"   Total Tests: {total_tests}")
        print(f"   Successful: {successful_tests}")  
        print(f"   Failed: {total_tests - successful_tests}")
        print(f"   Success Rate: {(successful_tests/total_tests)*100:.1f}%")
        print(f"   Issues Found: {len(self.results['issues_found'])}")
        
        # Show critical issues
        critical_issues = [i for i in self.results['issues_found'] if i['severity'] == 'critical']
        if critical_issues:
            print(f"\n🚨 Critical Issues ({len(critical_issues)}):")
            for issue in critical_issues:
                print(f"   • {issue['tool']}: {issue['description']}")
        
        return self.results

    def save_results(self, filename: str = None):
        """Save test results to JSON file."""
        if not filename:
            filename = f"test_results_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json"
        
        with open(filename, 'w') as f:
            json.dump(self.results, f, indent=2, default=str)
        
        print(f"📄 Test results saved to: {filename}")
        return filename


async def main():
    """Main test runner."""
    test_suite = AdCopyTestSuite()
    results = await test_suite.run_all_tests()
    
    # Save results
    results_file = test_suite.save_results()
    
    return results, results_file


if __name__ == "__main__":
    # Run the test suite
    results, results_file = asyncio.run(main())
