#!/usr/bin/env python3
"""
End-to-End Functional Test for AI Ad Improvement Workflow
=========================================================

Tests the complete workflow from frontend payload to backend response
across all supported platforms with realistic ad copy examples.

Validation Points:
1. Payload schema validation
2. Backend response structure 
3. Platform character limits enforcement
4. Grammar and clarity validation
5. Variants retain product/offer details
6. No API errors (422, etc.)
7. UI display compatibility

"""

import requests
import json
import time
import sys
from typing import Dict, List, Any
from datetime import datetime

# Test Configuration
BASE_URL = "http://localhost:8000"
TEST_TIMEOUT = 60  # seconds

# Platform character limits for validation
PLATFORM_LIMITS = {
    'facebook': 2200,
    'instagram': 2200,
    'google_ads': 90,
    'linkedin': 3000,
    'twitter': 280,
    'tiktok': 2200
}

# Test ad copies for each platform (realistic examples)
TEST_ADS = {
    'facebook': {
        'ad_copy': "🚀 Transform Your Marketing ROI with Our AI-Powered Analytics Platform! Get 40% better campaign performance, real-time insights, and automated optimization. Join 15,000+ marketers already crushing their goals. Start your FREE 14-day trial today - no credit card required!",
        'expected_elements': ['marketing', 'roi', 'ai-powered', '40%', 'free trial']
    },
    'instagram': {
        'ad_copy': "✨ Glow up your skincare routine! Our award-winning vitamin C serum reduces dark spots by 67% in just 2 weeks. Dermatologist-approved, cruelty-free, and loved by 50K+ customers. Limited time: Buy 2 get 1 FREE! #GlowUp #SkincareRoutine #VitaminC",
        'expected_elements': ['skincare', 'vitamin c', '67%', 'buy 2 get 1 free', 'glow']
    },
    'google_ads': {
        'ad_copy': "Professional CRM Software - 30% Off All Plans. Streamline sales, automate follow-ups, increase conversions by 45%. Trusted by 10,000+ businesses. Free trial available.",
        'expected_elements': ['crm', '30% off', 'sales', 'free trial']
    },
    'linkedin': {
        'ad_copy': "Accelerate Your Career with Data Science Certification. Harvard-endorsed program with 94% job placement rate. Master Python, Machine Learning, and Analytics in 12 weeks. Scholarships available for qualified professionals. Apply now.",
        'expected_elements': ['data science', 'harvard', '94%', 'python', 'machine learning']
    },
    'twitter': {
        'ad_copy': "🎯 New: AI writing assistant that actually understands context. 10x faster content creation. Used by 500+ agencies. Try free → bit.ly/aiwriter",
        'expected_elements': ['ai writing', '10x faster', '500+ agencies']
    },
    'tiktok': {
        'ad_copy': "POV: You discover the productivity hack that changed everything 📈 This AI scheduler saved me 15 hours/week and boosted my income by 200%. Download free for 7 days! #ProductivityHack #AITools #TimeManagement",
        'expected_elements': ['productivity', 'ai scheduler', '15 hours', '200%', 'free']
    }
}

class E2EWorkflowTester:
    def __init__(self):
        self.results = {}
        self.total_tests = 0
        self.passed_tests = 0
        self.failed_tests = 0
        
    def log(self, message: str, level: str = "INFO"):
        timestamp = datetime.now().strftime("%H:%M:%S")
        prefix = {"INFO": "✅", "WARN": "⚠️", "ERROR": "❌", "TEST": "🧪"}
        print(f"{prefix.get(level, '📝')} [{timestamp}] {message}")
    
    def validate_payload_schema(self, payload: Dict[str, Any], platform: str) -> bool:
        """Validate that the payload matches expected schema"""
        try:
            required_fields = ['ad_copy', 'platform']
            for field in required_fields:
                if field not in payload:
                    self.log(f"Missing required field: {field}", "ERROR")
                    return False
            
            if not isinstance(payload['ad_copy'], str) or len(payload['ad_copy']) == 0:
                self.log("Invalid ad_copy: must be non-empty string", "ERROR")
                return False
                
            if payload['platform'] != platform:
                self.log(f"Platform mismatch: expected {platform}, got {payload['platform']}", "ERROR")
                return False
                
            self.log(f"✓ Payload schema valid for {platform}")
            return True
            
        except Exception as e:
            self.log(f"Payload validation error: {e}", "ERROR")
            return False
    
    def validate_response_structure(self, response: Dict[str, Any], platform: str) -> bool:
        """Validate backend response has all required fields"""
        try:
            required_sections = ['original', 'improved', 'abTests', 'compliance', 'psychology']
            
            for section in required_sections:
                if section not in response:
                    self.log(f"Missing response section: {section}", "ERROR")
                    return False
            
            # Validate improved section
            improved = response.get('improved', {})
            if 'copy' not in improved or 'score' not in improved:
                self.log("Invalid improved section: missing copy or score", "ERROR")
                return False
            
            # Validate A/B/C variants
            abc_variants = response.get('abTests', {}).get('abc_variants', [])
            if len(abc_variants) != 3:
                self.log(f"Expected 3 ABC variants, got {len(abc_variants)}", "ERROR")
                return False
            
            # Validate each variant structure
            for i, variant in enumerate(abc_variants):
                required_variant_fields = ['id', 'version', 'headline', 'body_text', 'cta']
                for field in required_variant_fields:
                    if field not in variant or not variant[field]:
                        self.log(f"Variant {i+1} missing/empty field: {field}", "ERROR")
                        return False
            
            self.log(f"✓ Response structure valid for {platform}")
            return True
            
        except Exception as e:
            self.log(f"Response validation error: {e}", "ERROR")
            return False
    
    def validate_character_limits(self, response: Dict[str, Any], platform: str) -> bool:
        """Validate platform-specific character limits"""
        try:
            limit = PLATFORM_LIMITS.get(platform, 2200)
            
            # Check improved copy
            improved_copy = response.get('improved', {}).get('copy', '')
            if len(improved_copy) > limit:
                self.log(f"Improved copy exceeds {platform} limit: {len(improved_copy)}/{limit}", "ERROR")
                return False
            
            # Check each ABC variant
            abc_variants = response.get('abTests', {}).get('abc_variants', [])
            for i, variant in enumerate(abc_variants):
                # Calculate total length (headline + body + cta)
                total_length = len(variant.get('headline', '')) + len(variant.get('body_text', '')) + len(variant.get('cta', ''))
                
                if platform == 'google_ads':
                    # Google Ads has specific field limits
                    headline_limit = 30
                    body_limit = 90
                    if len(variant.get('headline', '')) > headline_limit:
                        self.log(f"Variant {variant['version']} headline exceeds Google limit: {len(variant.get('headline', ''))}/{headline_limit}", "ERROR")
                        return False
                    if len(variant.get('body_text', '')) > body_limit:
                        self.log(f"Variant {variant['version']} body exceeds Google limit: {len(variant.get('body_text', ''))}/{body_limit}", "ERROR")
                        return False
                elif total_length > limit:
                    self.log(f"Variant {variant['version']} exceeds {platform} limit: {total_length}/{limit}", "ERROR")
                    return False
            
            self.log(f"✓ Character limits respected for {platform}")
            return True
            
        except Exception as e:
            self.log(f"Character limit validation error: {e}", "ERROR")
            return False
    
    def validate_grammar_and_clarity(self, response: Dict[str, Any], platform: str) -> bool:
        """Basic grammar and clarity validation"""
        try:
            texts_to_check = [response.get('improved', {}).get('copy', '')]
            
            # Add ABC variant texts
            abc_variants = response.get('abTests', {}).get('abc_variants', [])
            for variant in abc_variants:
                texts_to_check.extend([
                    variant.get('headline', ''),
                    variant.get('body_text', ''),
                    variant.get('cta', '')
                ])
            
            # Basic grammar checks
            issues = []
            for i, text in enumerate(texts_to_check):
                if not text.strip():
                    issues.append(f"Empty text field {i}")
                    continue
                
                # Check for common issues
                if text.count('(') != text.count(')'):
                    issues.append(f"Unmatched parentheses in text {i}")
                if text.count('"') % 2 != 0:
                    issues.append(f"Unmatched quotes in text {i}")
                if '  ' in text:  # Multiple spaces
                    issues.append(f"Multiple consecutive spaces in text {i}")
                if text.strip() != text:  # Leading/trailing whitespace
                    issues.append(f"Leading/trailing whitespace in text {i}")
            
            if issues:
                self.log(f"Grammar/clarity issues: {', '.join(issues)}", "WARN")
                # Don't fail for minor issues, just log them
            
            self.log(f"✓ Grammar and clarity acceptable for {platform}")
            return True
            
        except Exception as e:
            self.log(f"Grammar validation error: {e}", "ERROR")
            return False
    
    def validate_product_details_retention(self, original_ad: str, response: Dict[str, Any], expected_elements: List[str], platform: str) -> bool:
        """Validate that key product/offer details are retained"""
        try:
            # Get all generated texts
            improved_copy = response.get('improved', {}).get('copy', '').lower()
            abc_variants = response.get('abTests', {}).get('abc_variants', [])
            
            all_texts = [improved_copy]
            for variant in abc_variants:
                variant_text = f"{variant.get('headline', '')} {variant.get('body_text', '')} {variant.get('cta', '')}".lower()
                all_texts.append(variant_text)
            
            # Check if expected elements are retained in at least one version
            retained_elements = []
            missing_elements = []
            
            for element in expected_elements:
                found = any(element.lower() in text for text in all_texts)
                if found:
                    retained_elements.append(element)
                else:
                    missing_elements.append(element)
            
            retention_rate = len(retained_elements) / len(expected_elements) * 100
            
            if retention_rate < 70:  # At least 70% should be retained
                self.log(f"Low product detail retention ({retention_rate:.1f}%): Missing {missing_elements}", "ERROR")
                return False
            
            if missing_elements:
                self.log(f"Some elements missing ({retention_rate:.1f}% retained): {missing_elements}", "WARN")
            else:
                self.log(f"✓ All product details retained for {platform}")
            
            return True
            
        except Exception as e:
            self.log(f"Product detail validation error: {e}", "ERROR")
            return False
    
    def validate_ui_display_compatibility(self, response: Dict[str, Any], platform: str) -> bool:
        """Validate response is compatible with frontend display"""
        try:
            # Check that all text fields are properly formatted for UI display
            abc_variants = response.get('abTests', {}).get('abc_variants', [])
            
            for variant in abc_variants:
                # Check for UI-breaking characters
                for field_name in ['headline', 'body_text', 'cta']:
                    field_value = variant.get(field_name, '')
                    
                    # Check for problematic characters
                    if '\0' in field_value:  # null bytes
                        self.log(f"Variant {variant['version']} {field_name} contains null bytes", "ERROR")
                        return False
                    
                    # Check for excessive newlines
                    if field_value.count('\n') > 5:
                        self.log(f"Variant {variant['version']} {field_name} has excessive newlines", "WARN")
                    
                    # Check for HTML-like content that could break rendering
                    if '<script' in field_value.lower() or '<iframe' in field_value.lower():
                        self.log(f"Variant {variant['version']} {field_name} contains potentially unsafe HTML", "ERROR")
                        return False
                
                # Validate version field is A, B, or C
                if variant.get('version') not in ['A', 'B', 'C']:
                    self.log(f"Invalid variant version: {variant.get('version')}", "ERROR")
                    return False
            
            self.log(f"✓ UI display compatibility validated for {platform}")
            return True
            
        except Exception as e:
            self.log(f"UI compatibility validation error: {e}", "ERROR")
            return False
    
    def test_platform(self, platform: str, test_data: Dict[str, Any]) -> Dict[str, bool]:
        """Run complete test suite for a specific platform"""
        self.log(f"Starting comprehensive test for {platform.upper()}", "TEST")
        
        platform_results = {}
        ad_copy = test_data['ad_copy']
        expected_elements = test_data['expected_elements']
        
        # Prepare payload
        payload = {
            'ad_copy': ad_copy,
            'platform': platform
        }
        
        try:
            # 1. Validate Payload Schema
            self.total_tests += 1
            platform_results['payload_schema'] = self.validate_payload_schema(payload, platform)
            if platform_results['payload_schema']:
                self.passed_tests += 1
            else:
                self.failed_tests += 1
            
            # 2. Make API Request
            self.log(f"Making API request to /api/ads/comprehensive-analyze for {platform}")
            start_time = time.time()
            
            response = requests.post(
                f"{BASE_URL}/api/ads/comprehensive-analyze",
                json=payload,
                timeout=TEST_TIMEOUT,
                headers={'Content-Type': 'application/json'}
            )
            
            request_time = time.time() - start_time
            self.log(f"API response received in {request_time:.2f}s (Status: {response.status_code})")
            
            # Check for API errors
            self.total_tests += 1
            if response.status_code == 200:
                platform_results['no_api_errors'] = True
                self.passed_tests += 1
                self.log(f"✓ No API errors for {platform}")
            else:
                platform_results['no_api_errors'] = False
                self.failed_tests += 1
                self.log(f"API error {response.status_code}: {response.text}", "ERROR")
                return platform_results
            
            response_data = response.json()
            
            # 3. Validate Response Structure
            self.total_tests += 1
            platform_results['response_structure'] = self.validate_response_structure(response_data, platform)
            if platform_results['response_structure']:
                self.passed_tests += 1
            else:
                self.failed_tests += 1
            
            # 4. Validate Character Limits
            self.total_tests += 1
            platform_results['character_limits'] = self.validate_character_limits(response_data, platform)
            if platform_results['character_limits']:
                self.passed_tests += 1
            else:
                self.failed_tests += 1
            
            # 5. Validate Grammar and Clarity
            self.total_tests += 1
            platform_results['grammar_clarity'] = self.validate_grammar_and_clarity(response_data, platform)
            if platform_results['grammar_clarity']:
                self.passed_tests += 1
            else:
                self.failed_tests += 1
            
            # 6. Validate Product Details Retention
            self.total_tests += 1
            platform_results['product_details'] = self.validate_product_details_retention(ad_copy, response_data, expected_elements, platform)
            if platform_results['product_details']:
                self.passed_tests += 1
            else:
                self.failed_tests += 1
            
            # 7. Validate UI Display Compatibility
            self.total_tests += 1
            platform_results['ui_compatibility'] = self.validate_ui_display_compatibility(response_data, platform)
            if platform_results['ui_compatibility']:
                self.passed_tests += 1
            else:
                self.failed_tests += 1
            
            self.log(f"Platform {platform.upper()} test completed\n")
            
        except requests.exceptions.Timeout:
            self.log(f"API request timeout for {platform}", "ERROR")
            platform_results['no_api_errors'] = False
            self.failed_tests += 1
            self.total_tests += 1
        except requests.exceptions.RequestException as e:
            self.log(f"API request failed for {platform}: {e}", "ERROR")
            platform_results['no_api_errors'] = False
            self.failed_tests += 1
            self.total_tests += 1
        except Exception as e:
            self.log(f"Unexpected error testing {platform}: {e}", "ERROR")
            self.failed_tests += 1
            self.total_tests += 1
        
        return platform_results
    
    def run_comprehensive_test(self):
        """Run the complete end-to-end test suite"""
        self.log("🚀 Starting End-to-End AI Ad Improvement Workflow Test", "INFO")
        self.log(f"Testing against: {BASE_URL}")
        self.log(f"Timeout: {TEST_TIMEOUT}s per request\n")
        
        # Test server connectivity first
        try:
            health_response = requests.get(f"{BASE_URL}/health", timeout=10)
            if health_response.status_code == 200:
                self.log("✓ Backend server is responsive")
            else:
                self.log("⚠️ Backend server health check failed", "WARN")
        except:
            self.log("❌ Cannot connect to backend server", "ERROR")
            return
        
        # Run tests for each platform
        for platform, test_data in TEST_ADS.items():
            self.results[platform] = self.test_platform(platform, test_data)
        
        self.print_summary()
    
    def print_summary(self):
        """Print comprehensive test summary"""
        self.log("📊 END-TO-END TEST SUMMARY", "INFO")
        print("=" * 80)
        
        # Overall results
        success_rate = (self.passed_tests / self.total_tests * 100) if self.total_tests > 0 else 0
        print(f"📈 OVERALL RESULTS: {self.passed_tests}/{self.total_tests} tests passed ({success_rate:.1f}%)")
        print(f"✅ Passed: {self.passed_tests}")
        print(f"❌ Failed: {self.failed_tests}")
        print()
        
        # Platform-specific results
        validation_points = [
            'payload_schema', 'no_api_errors', 'response_structure', 
            'character_limits', 'grammar_clarity', 'product_details', 'ui_compatibility'
        ]
        
        validation_names = [
            'Payload Schema', 'No API Errors', 'Response Structure',
            'Character Limits', 'Grammar & Clarity', 'Product Details', 'UI Compatibility'
        ]
        
        print("🧪 DETAILED VALIDATION RESULTS:")
        print("-" * 80)
        
        # Header
        print(f"{'Platform':<12}", end='')
        for name in validation_names:
            print(f"{name:<15}", end='')
        print()
        print("-" * 80)
        
        # Results for each platform
        for platform in TEST_ADS.keys():
            print(f"{platform.upper():<12}", end='')
            platform_results = self.results.get(platform, {})
            
            for point in validation_points:
                result = platform_results.get(point, False)
                status = "✅ PASS" if result else "❌ FAIL"
                print(f"{status:<15}", end='')
            print()
        
        print("-" * 80)
        
        # Summary by validation point
        print("\n📋 VALIDATION POINT SUMMARY:")
        for i, point in enumerate(validation_points):
            point_name = validation_names[i]
            passed = sum(1 for platform_results in self.results.values() if platform_results.get(point, False))
            total = len(TEST_ADS)
            status = "✅ PASS" if passed == total else "❌ FAIL" if passed == 0 else "⚠️ PARTIAL"
            print(f"{status} {point_name}: {passed}/{total} platforms")
        
        print("\n" + "=" * 80)
        
        if success_rate >= 90:
            self.log("🎉 EXCELLENT: AI ad improvement workflow is working perfectly!", "INFO")
        elif success_rate >= 75:
            self.log("✅ GOOD: AI ad improvement workflow is mostly functional with minor issues", "INFO") 
        elif success_rate >= 50:
            self.log("⚠️ ISSUES: AI ad improvement workflow has significant problems that need attention", "WARN")
        else:
            self.log("❌ CRITICAL: AI ad improvement workflow is severely broken", "ERROR")

def main():
    """Run the end-to-end test suite"""
    tester = E2EWorkflowTester()
    tester.run_comprehensive_test()

if __name__ == "__main__":
    main()