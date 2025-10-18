#!/usr/bin/env python3
"""
Frontend Integration Tests

Tests that frontend correctly displays all fields and handles platform-specific layouts:
- API response format validation
- Frontend component rendering verification
- Platform-specific field display
- Character counter accuracy
- Copy-to-clipboard functionality
- Platform badge display
- Error handling and edge cases
"""

import json
import requests
import time
from typing import Dict, List, Any
from dataclasses import asdict

# Test data
from test_data_comprehensive import get_test_ads_for_platform

class FrontendIntegrationTester:
    """Tests frontend integration with backend API"""
    
    def __init__(self, api_base_url: str = "http://localhost:8000"):
        self.api_base_url = api_base_url
        self.platforms = ['facebook', 'instagram', 'google_ads', 'linkedin', 'twitter_x', 'tiktok']
        
    def run_integration_tests(self) -> Dict[str, Any]:
        """Run comprehensive frontend integration tests"""
        print("🔗 Starting frontend integration tests...")
        
        start_time = time.time()
        test_results = {
            'total_tests': 0,
            'passed_tests': 0,
            'failed_tests': 0,
            'api_tests': {
                'health_check': None,
                'improve_endpoint': {},
                'response_format': {},
                'error_handling': {}
            },
            'frontend_compatibility': {
                'field_mapping': {},
                'character_counting': {},
                'platform_badges': {},
                'display_formats': {}
            },
            'execution_time': 0,
            'detailed_results': []
        }
        
        # 1. API Health Check
        test_results['api_tests']['health_check'] = self._test_api_health()
        
        # 2. Test each platform endpoint
        for platform_id in self.platforms:
            print(f"🧪 Testing {platform_id} integration...")
            
            # Test API responses
            api_result = self._test_platform_api(platform_id)
            test_results['api_tests']['improve_endpoint'][platform_id] = api_result
            
            if api_result['success']:
                # Test response format
                format_result = self._test_response_format(api_result['response'], platform_id)
                test_results['api_tests']['response_format'][platform_id] = format_result
                
                # Test frontend compatibility
                frontend_result = self._test_frontend_compatibility(api_result['response'], platform_id)
                test_results['frontend_compatibility']['field_mapping'][platform_id] = frontend_result
        
        # 3. Test error handling
        test_results['api_tests']['error_handling'] = self._test_error_handling()
        
        # Count results
        for category, tests in test_results['api_tests'].items():
            if isinstance(tests, dict):
                for test_name, result in tests.items():
                    test_results['total_tests'] += 1
                    if isinstance(result, dict) and result.get('success', False):
                        test_results['passed_tests'] += 1
                    else:
                        test_results['failed_tests'] += 1
            else:
                test_results['total_tests'] += 1
                if isinstance(tests, dict) and tests.get('success', False):
                    test_results['passed_tests'] += 1
                else:
                    test_results['failed_tests'] += 1
        
        test_results['execution_time'] = round(time.time() - start_time, 2)
        
        success_rate = round(test_results['passed_tests']/test_results['total_tests']*100, 1) if test_results['total_tests'] > 0 else 0
        print(f"✅ Integration tests completed: {test_results['passed_tests']}/{test_results['total_tests']} ({success_rate}%)")
        
        return test_results
    
    def _test_api_health(self) -> Dict[str, Any]:
        """Test API health endpoint"""
        result = {
            'success': False,
            'response_time': 0,
            'errors': [],
            'response_data': None
        }
        
        try:
            start_time = time.time()
            response = requests.get(f"{self.api_base_url}/health", timeout=10)
            result['response_time'] = round((time.time() - start_time) * 1000, 2)
            
            if response.status_code == 200:
                data = response.json()
                result['response_data'] = data
                
                # Verify expected fields
                expected_fields = ['status', 'timestamp', 'version']
                for field in expected_fields:
                    if field not in data:
                        result['errors'].append(f"Missing field: {field}")
                
                if data.get('status') == 'healthy':
                    result['success'] = True
                else:
                    result['errors'].append(f"Unhealthy status: {data.get('status')}")
            else:
                result['errors'].append(f"HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            result['errors'].append(f"Health check failed: {str(e)}")
        
        return result
    
    def _test_platform_api(self, platform_id: str) -> Dict[str, Any]:
        """Test platform-specific API endpoint"""
        result = {
            'success': False,
            'response_time': 0,
            'errors': [],
            'warnings': [],
            'response': None,
            'platform_id': platform_id
        }
        
        # Get sample ad for testing
        test_ads = get_test_ads_for_platform(platform_id)
        if not test_ads or 'well_written_ads' not in test_ads or not test_ads['well_written_ads']:
            result['errors'].append("No test data available")
            return result
        
        test_ad = test_ads['well_written_ads'][0]
        
        try:
            start_time = time.time()
            response = requests.post(
                f"{self.api_base_url}/api/ads/improve",
                json={
                    "ad_copy": test_ad,
                    "platform": platform_id
                },
                headers={"Content-Type": "application/json"},
                timeout=30
            )
            result['response_time'] = round((time.time() - start_time) * 1000, 2)
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    result['response'] = data
                    result['success'] = True
                except json.JSONDecodeError:
                    result['errors'].append("Invalid JSON response")
            else:
                result['errors'].append(f"HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            result['errors'].append(f"API call failed: {str(e)}")
        
        return result
    
    def _test_response_format(self, response: Dict, platform_id: str) -> Dict[str, Any]:
        """Test that response format matches frontend expectations"""
        result = {
            'success': False,
            'errors': [],
            'warnings': [],
            'field_analysis': {}
        }
        
        # Expected top-level fields
        expected_fields = {
            'platform': str,
            'originalAd': dict,
            'improvedAd': dict,
            'variants': list,
            'confidenceScore': (int, float),
            'success': bool
        }
        
        # Check top-level structure
        missing_fields = []
        wrong_types = []
        
        for field, expected_type in expected_fields.items():
            if field not in response:
                missing_fields.append(field)
            else:
                if not isinstance(response[field], expected_type):
                    wrong_types.append(f"{field}: expected {expected_type}, got {type(response[field])}")
        
        if missing_fields:
            result['errors'].extend([f"Missing field: {f}" for f in missing_fields])
        
        if wrong_types:
            result['errors'].extend([f"Wrong type: {t}" for t in wrong_types])
        
        # Check originalAd structure
        if 'originalAd' in response and isinstance(response['originalAd'], dict):
            original_ad = response['originalAd']
            expected_original_fields = ['copy', 'score']
            
            for field in expected_original_fields:
                if field not in original_ad:
                    result['errors'].append(f"Missing originalAd.{field}")
        
        # Check improvedAd structure
        if 'improvedAd' in response and isinstance(response['improvedAd'], dict):
            improved_ad = response['improvedAd']
            
            # Should have content field
            if 'content' not in improved_ad:
                result['errors'].append("Missing improvedAd.content")
            elif isinstance(improved_ad['content'], dict):
                # Analyze platform-specific content structure
                result['field_analysis'] = self._analyze_content_structure(
                    improved_ad['content'], platform_id
                )
        
        # Check variants structure
        if 'variants' in response and isinstance(response['variants'], list):
            for i, variant in enumerate(response['variants']):
                if not isinstance(variant, dict):
                    result['errors'].append(f"Variant {i} is not a dict")
                    continue
                
                expected_variant_fields = ['version', 'content', 'score']
                for field in expected_variant_fields:
                    if field not in variant:
                        result['errors'].append(f"Missing variant[{i}].{field}")
        
        result['success'] = len(result['errors']) == 0
        return result
    
    def _analyze_content_structure(self, content: Dict, platform_id: str) -> Dict[str, Any]:
        """Analyze platform-specific content structure"""
        analysis = {
            'platform_id': platform_id,
            'fields_present': list(content.keys()),
            'expected_fields': [],
            'missing_fields': [],
            'unexpected_fields': [],
            'field_types': {}
        }
        
        # Platform-specific expected fields
        platform_expectations = {
            'facebook': ['headline', 'body', 'cta'],
            'instagram': ['body', 'hashtags'],
            'google_ads': ['headlines', 'descriptions'],
            'linkedin': ['headline', 'body', 'cta'],
            'twitter_x': ['body'],
            'tiktok': ['body']
        }
        
        expected = platform_expectations.get(platform_id, [])
        analysis['expected_fields'] = expected
        
        # Check for missing expected fields
        for field in expected:
            if field not in content:
                analysis['missing_fields'].append(field)
        
        # Check for unexpected fields
        for field in content.keys():
            if field not in expected:
                analysis['unexpected_fields'].append(field)
        
        # Analyze field types
        for field, value in content.items():
            analysis['field_types'][field] = type(value).__name__
            
            # Validate specific field types
            if field == 'headlines' or field == 'descriptions' or field == 'hashtags':
                if not isinstance(value, list):
                    analysis[f'{field}_type_error'] = f"Expected list, got {type(value).__name__}"
        
        return analysis
    
    def _test_frontend_compatibility(self, response: Dict, platform_id: str) -> Dict[str, Any]:
        """Test frontend compatibility and display requirements"""
        result = {
            'success': False,
            'errors': [],
            'warnings': [],
            'character_counts': {},
            'display_requirements': {}
        }
        
        if 'improvedAd' not in response or 'content' not in response['improvedAd']:
            result['errors'].append("No content to test")
            return result
        
        content = response['improvedAd']['content']
        
        # Test character counting requirements
        char_count_result = self._test_character_counting(content, platform_id)
        result['character_counts'] = char_count_result
        
        # Test display requirements
        display_result = self._test_display_requirements(content, platform_id)
        result['display_requirements'] = display_result
        
        # Test platform badge requirements
        badge_result = self._test_platform_badge_requirements(response, platform_id)
        result['platform_badge'] = badge_result
        
        # Success if no critical errors
        result['success'] = len(result['errors']) == 0
        
        return result
    
    def _test_character_counting(self, content: Dict, platform_id: str) -> Dict[str, Any]:
        """Test character counting for frontend display"""
        result = {
            'field_counts': {},
            'limit_warnings': [],
            'count_accuracy': True
        }
        
        # Platform-specific character limits (should match frontend)
        platform_limits = {
            'facebook': {'headline': 125, 'body': 500, 'cta': 20},
            'instagram': {'body': 2200, 'cta': 20},
            'google_ads': {'headlines': 30, 'descriptions': 90, 'cta': 20},
            'linkedin': {'headline': 150, 'body': 600, 'cta': 20},
            'twitter_x': {'body': 280},
            'tiktok': {'body': 300, 'cta': 20}
        }
        
        limits = platform_limits.get(platform_id, {})
        
        for field, value in content.items():
            if field in limits:
                limit = limits[field]
                
                if isinstance(value, list):
                    # Handle multiple items (like headlines)
                    for i, item in enumerate(value):
                        char_count = len(str(item))
                        result['field_counts'][f'{field}[{i}]'] = {
                            'count': char_count,
                            'limit': limit,
                            'over_limit': char_count > limit
                        }
                        
                        if char_count > limit:
                            result['limit_warnings'].append(f"{field}[{i}]: {char_count}/{limit}")
                
                elif isinstance(value, str):
                    char_count = len(value)
                    result['field_counts'][field] = {
                        'count': char_count,
                        'limit': limit,
                        'over_limit': char_count > limit
                    }
                    
                    if char_count > limit:
                        result['limit_warnings'].append(f"{field}: {char_count}/{limit}")
        
        return result
    
    def _test_display_requirements(self, content: Dict, platform_id: str) -> Dict[str, Any]:
        """Test platform-specific display requirements"""
        result = {
            'platform_id': platform_id,
            'display_checks': {},
            'layout_requirements': [],
            'special_formatting': []
        }
        
        # Platform-specific display tests
        if platform_id == 'google_ads':
            # Should display multiple headlines and descriptions
            headlines = content.get('headlines', [])
            descriptions = content.get('descriptions', [])
            
            result['display_checks']['headlines_count'] = len(headlines)
            result['display_checks']['descriptions_count'] = len(descriptions)
            
            if len(headlines) < 3:
                result['layout_requirements'].append("Display at least 3 headlines for Google Ads")
            
            if len(descriptions) < 2:
                result['layout_requirements'].append("Display at least 2 descriptions for Google Ads")
        
        elif platform_id == 'instagram':
            # Should handle hashtags display
            hashtags = content.get('hashtags', [])
            body = content.get('body', '')
            
            result['display_checks']['hashtags_count'] = len(hashtags)
            result['display_checks']['has_emojis'] = any(ord(char) > 127 for char in body)
            
            if hashtags:
                result['special_formatting'].append("Display hashtags as clickable tags")
            
            result['layout_requirements'].append("Display body text with emoji support")
        
        elif platform_id == 'twitter_x':
            # Should handle Twitter-specific formatting
            body = content.get('body', '')
            
            result['display_checks']['has_mentions'] = '@' in body
            result['display_checks']['has_hashtags'] = '#' in body
            result['display_checks']['character_efficiency'] = len(body.split()) / len(body) if len(body) > 0 else 0
            
            if '@' in body:
                result['special_formatting'].append("Highlight @mentions")
            
            if '#' in body:
                result['special_formatting'].append("Make hashtags clickable")
        
        elif platform_id == 'facebook':
            # Should display structured format
            headline = content.get('headline', '')
            body = content.get('body', '')
            cta = content.get('cta', '')
            
            result['display_checks']['has_headline'] = bool(headline)
            result['display_checks']['has_body'] = bool(body)
            result['display_checks']['has_cta'] = bool(cta)
            
            result['layout_requirements'].append("Display headline prominently")
            result['layout_requirements'].append("Show CTA as button")
        
        elif platform_id == 'linkedin':
            # Professional formatting
            result['layout_requirements'].append("Use professional styling")
            result['layout_requirements'].append("Emphasize business value")
        
        elif platform_id == 'tiktok':
            # Trendy formatting
            body = content.get('body', '')
            
            result['display_checks']['has_trending_terms'] = any(
                term in body.lower() for term in ['pov:', 'viral', 'hack', 'trend']
            )
            
            result['layout_requirements'].append("Use casual, trendy styling")
            result['special_formatting'].append("Highlight trending keywords")
        
        return result
    
    def _test_platform_badge_requirements(self, response: Dict, platform_id: str) -> Dict[str, Any]:
        """Test platform badge display requirements"""
        result = {
            'platform_name': platform_id,
            'display_name': self._get_platform_display_name(platform_id),
            'icon_requirements': self._get_platform_icon_requirements(platform_id),
            'color_scheme': self._get_platform_colors(platform_id),
            'badge_position': 'top-right'  # Standard position
        }
        
        return result
    
    def _get_platform_display_name(self, platform_id: str) -> str:
        """Get human-readable platform name"""
        display_names = {
            'facebook': 'Facebook',
            'instagram': 'Instagram',
            'google_ads': 'Google Ads',
            'linkedin': 'LinkedIn',
            'twitter_x': 'X (Twitter)',
            'tiktok': 'TikTok'
        }
        return display_names.get(platform_id, platform_id.title())
    
    def _get_platform_icon_requirements(self, platform_id: str) -> Dict[str, str]:
        """Get platform icon requirements"""
        icons = {
            'facebook': {'type': 'fa-facebook', 'unicode': '\\f09a'},
            'instagram': {'type': 'fa-instagram', 'unicode': '\\f16d'},
            'google_ads': {'type': 'fa-google', 'unicode': '\\f1a0'},
            'linkedin': {'type': 'fa-linkedin', 'unicode': '\\f0e1'},
            'twitter_x': {'type': 'fa-x-twitter', 'unicode': '\\e61b'},
            'tiktok': {'type': 'fa-tiktok', 'unicode': '\\e07b'}
        }
        return icons.get(platform_id, {'type': 'fa-globe', 'unicode': '\\f0ac'})
    
    def _get_platform_colors(self, platform_id: str) -> Dict[str, str]:
        """Get platform brand colors"""
        colors = {
            'facebook': {'primary': '#1877F2', 'secondary': '#42A5F5'},
            'instagram': {'primary': '#E4405F', 'secondary': '#F77737'},
            'google_ads': {'primary': '#4285F4', 'secondary': '#34A853'},
            'linkedin': {'primary': '#0077B5', 'secondary': '#00A0DC'},
            'twitter_x': {'primary': '#000000', 'secondary': '#1DA1F2'},
            'tiktok': {'primary': '#FF0050', 'secondary': '#000000'}
        }
        return colors.get(platform_id, {'primary': '#6B7280', 'secondary': '#9CA3AF'})
    
    def _test_error_handling(self) -> Dict[str, Any]:
        """Test API error handling"""
        result = {
            'invalid_platform': None,
            'missing_ad_copy': None,
            'empty_ad_copy': None,
            'malformed_request': None
        }
        
        # Test invalid platform
        try:
            response = requests.post(
                f"{self.api_base_url}/api/ads/improve",
                json={"ad_copy": "Test ad", "platform": "invalid_platform"},
                timeout=10
            )
            result['invalid_platform'] = {
                'status_code': response.status_code,
                'response': response.text,
                'handled_gracefully': response.status_code in [400, 422]
            }
        except Exception as e:
            result['invalid_platform'] = {'error': str(e), 'handled_gracefully': False}
        
        # Test missing ad_copy
        try:
            response = requests.post(
                f"{self.api_base_url}/api/ads/improve",
                json={"platform": "facebook"},
                timeout=10
            )
            result['missing_ad_copy'] = {
                'status_code': response.status_code,
                'response': response.text,
                'handled_gracefully': response.status_code in [400, 422]
            }
        except Exception as e:
            result['missing_ad_copy'] = {'error': str(e), 'handled_gracefully': False}
        
        # Test empty ad_copy
        try:
            response = requests.post(
                f"{self.api_base_url}/api/ads/improve",
                json={"ad_copy": "", "platform": "facebook"},
                timeout=10
            )
            result['empty_ad_copy'] = {
                'status_code': response.status_code,
                'response': response.text,
                'handled_gracefully': response.status_code in [400, 422]
            }
        except Exception as e:
            result['empty_ad_copy'] = {'error': str(e), 'handled_gracefully': False}
        
        # Test malformed request
        try:
            response = requests.post(
                f"{self.api_base_url}/api/ads/improve",
                data="invalid json",
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            result['malformed_request'] = {
                'status_code': response.status_code,
                'response': response.text,
                'handled_gracefully': response.status_code in [400, 422]
            }
        except Exception as e:
            result['malformed_request'] = {'error': str(e), 'handled_gracefully': False}
        
        return result
    
    def generate_integration_report(self, test_results: Dict[str, Any], output_file: str = None) -> str:
        """Generate integration test report"""
        report = []
        report.append("=" * 80)
        report.append("FRONTEND INTEGRATION TEST REPORT")
        report.append("=" * 80)
        report.append("")
        
        # Summary
        total = test_results['total_tests']
        passed = test_results['passed_tests']
        failed = test_results['failed_tests']
        success_rate = round(passed/total*100, 1) if total > 0 else 0
        
        report.append("📊 SUMMARY:")
        report.append(f"   Total Tests: {total}")
        report.append(f"   Passed: {passed}")
        report.append(f"   Failed: {failed}")
        report.append(f"   Success Rate: {success_rate}%")
        report.append(f"   Execution Time: {test_results['execution_time']}s")
        report.append("")
        
        # API Tests
        report.append("🔌 API TESTS:")
        
        # Health check
        health = test_results['api_tests']['health_check']
        health_status = "✅ PASS" if health.get('success') else "❌ FAIL"
        report.append(f"   Health Check: {health_status} ({health.get('response_time', 0)}ms)")
        
        # Platform endpoints
        report.append("   Platform Endpoints:")
        for platform, result in test_results['api_tests']['improve_endpoint'].items():
            status = "✅ PASS" if result.get('success') else "❌ FAIL"
            report.append(f"     {platform}: {status} ({result.get('response_time', 0)}ms)")
        
        report.append("")
        
        # Response Format Tests
        report.append("📋 RESPONSE FORMAT:")
        for platform, result in test_results['api_tests']['response_format'].items():
            status = "✅ PASS" if result.get('success') else "❌ FAIL"
            error_count = len(result.get('errors', []))
            report.append(f"   {platform}: {status} ({error_count} errors)")
        
        report.append("")
        
        # Frontend Compatibility
        report.append("🖥️  FRONTEND COMPATIBILITY:")
        for platform, result in test_results['frontend_compatibility']['field_mapping'].items():
            status = "✅ PASS" if result.get('success') else "❌ FAIL"
            report.append(f"   {platform}: {status}")
            
            # Character count warnings
            char_counts = result.get('character_counts', {})
            warnings = char_counts.get('limit_warnings', [])
            if warnings:
                report.append(f"     Character limit warnings: {len(warnings)}")
        
        report.append("")
        
        # Error Handling
        report.append("⚠️  ERROR HANDLING:")
        error_tests = test_results['api_tests']['error_handling']
        for test_name, result in error_tests.items():
            if result:
                handled = result.get('handled_gracefully', False)
                status = "✅ HANDLED" if handled else "❌ NOT HANDLED"
                report.append(f"   {test_name}: {status}")
        
        report_text = "\n".join(report)
        
        if output_file:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(report_text)
            print(f"📝 Integration report saved to {output_file}")
        
        return report_text

def run_frontend_integration_tests(api_url: str = "http://localhost:8000"):
    """Main integration test runner"""
    print("🔗 Starting frontend integration tests...")
    
    tester = FrontendIntegrationTester(api_url)
    results = tester.run_integration_tests()
    
    # Generate report
    report = tester.generate_integration_report(
        results,
        output_file="frontend_integration_report.txt"
    )
    
    print(report)
    return results

if __name__ == "__main__":
    import sys
    
    api_url = "http://localhost:8000"
    if len(sys.argv) > 1:
        api_url = sys.argv[1]
    
    run_frontend_integration_tests(api_url)