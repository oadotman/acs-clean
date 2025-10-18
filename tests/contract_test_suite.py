#!/usr/bin/env python3
"""
Contract Testing Suite

Tests the API contract between backend and frontend to ensure:
1. Backend returns exactly what frontend expects
2. All edge cases are handled gracefully  
3. Text cleaning works properly
4. All 6 platforms work correctly

⚠️ CRITICAL: Run this before any deployment to prevent "Backend did not return valid A/B/C variants" errors
"""

import requests
import json
import time
import sys
import os
from typing import Dict, List, Any, Tuple

# Add backend directory to path for imports
backend_dir = os.path.join(os.path.dirname(__file__), '..', 'backend')
sys.path.insert(0, backend_dir)

from response_validator import validate_and_clean_response

class ContractTestSuite:
    """Test suite for API contract validation"""
    
    def __init__(self, base_url: str = "http://127.0.0.1:8000"):
        self.base_url = base_url
        self.endpoint = "/api/ads/improve"
        self.results = []
        
    def log_test(self, test_name: str, success: bool, message: str = "", details: Dict = None):
        """Log test result"""
        result = {
            "test": test_name,
            "success": success,
            "message": message,
            "details": details or {},
            "timestamp": time.time()
        }
        self.results.append(result)
        
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status}: {test_name}")
        if message:
            print(f"    {message}")
        if not success and details:
            print(f"    Details: {json.dumps(details, indent=4)}")
    
    def make_request(self, ad_copy: str, platform: str) -> Tuple[bool, Dict, str]:
        """Make API request and return success, data, error"""
        try:
            response = requests.post(
                f"{self.base_url}{self.endpoint}",
                json={"ad_copy": ad_copy, "platform": platform},
                timeout=30
            )
            
            if response.status_code == 200:
                return True, response.json(), ""
            else:
                return False, {}, f"HTTP {response.status_code}: {response.text}"
                
        except Exception as e:
            return False, {}, str(e)
    
    def test_valid_response_structure(self):
        """Test 1: Valid response structure for all platforms"""
        platforms = ['facebook', 'instagram', 'google', 'linkedin', 'twitter', 'tiktok']
        test_ad = "Get 50% off all products today! Limited time offer - shop now and save big."
        
        for platform in platforms:
            success, data, error = self.make_request(test_ad, platform)
            
            if not success:
                self.log_test(f"Valid Response - {platform.title()}", False, error)
                continue
            
            # Validate using backend validator
            is_valid, cleaned_data, validation_errors = validate_and_clean_response(data)
            
            if is_valid:
                self.log_test(f"Valid Response - {platform.title()}", True, "Contract validation passed")
            else:
                self.log_test(
                    f"Valid Response - {platform.title()}", 
                    False, 
                    f"Validation failed: {'; '.join(validation_errors[:3])}",
                    {"errors": validation_errors, "response_keys": list(data.keys())}
                )
    
    def test_edge_cases(self):
        """Test 2: Edge cases that could break validation"""
        edge_cases = [
            {
                "name": "Very Short Ad", 
                "ad": "Sale!", 
                "platform": "facebook"
            },
            {
                "name": "Very Long Ad",
                "ad": "This is an incredibly long advertisement that goes on and on with lots of details about our amazing product that will transform your life in ways you never imagined possible. " * 5,
                "platform": "facebook" 
            },
            {
                "name": "Ad with Quotes",
                "ad": 'Check out our "amazing" product today! It\'s the "best" choice.',
                "platform": "facebook"
            },
            {
                "name": "Ad with Newlines", 
                "ad": "Line 1\nLine 2\nLine 3\nBuy now!",
                "platform": "facebook"
            },
            {
                "name": "Ad with Special Characters",
                "ad": "Save 50% 💰 on ALL items! 🎉 Limited time ⏰ Don't wait! 🚀",
                "platform": "facebook"
            },
            {
                "name": "Empty-ish Ad",
                "ad": "   \n\n   Sale   \n\n   ",
                "platform": "facebook"
            }
        ]
        
        for case in edge_cases:
            success, data, error = self.make_request(case["ad"], case["platform"])
            
            if not success:
                self.log_test(f"Edge Case - {case['name']}", False, error)
                continue
            
            # Check that variants have actual content
            variants = data.get("abTests", {}).get("abc_variants", [])
            if len(variants) != 3:
                self.log_test(
                    f"Edge Case - {case['name']}", 
                    False, 
                    f"Expected 3 variants, got {len(variants)}"
                )
                continue
            
            # Check that variant text is not empty after cleaning
            variant_texts_empty = []
            for i, variant in enumerate(variants):
                headline = variant.get("headline", "").strip()
                body = variant.get("body", "").strip()  
                cta = variant.get("cta", "").strip()
                
                if not headline or not body or not cta:
                    variant_texts_empty.append(f"Variant {variant.get('version', i+1)}")
            
            if variant_texts_empty:
                self.log_test(
                    f"Edge Case - {case['name']}", 
                    False,
                    f"Empty variant text in: {', '.join(variant_texts_empty)}"
                )
            else:
                self.log_test(f"Edge Case - {case['name']}", True, "All variants have content")
    
    def test_text_cleaning(self):
        """Test 3: Text cleaning works properly"""
        cleaning_tests = [
            {
                "name": "Remove Quotes",
                "input": '"Get the best deal!" "Limited time only!"',
                "should_not_contain": ['""', "''"]
            },
            {
                "name": "Remove Newlines",
                "input": "Line 1\nLine 2\rLine 3\r\nLine 4",
                "should_not_contain": ["\n", "\r"]
            },
            {
                "name": "Remove Escaped Quotes", 
                "input": 'He said \\"Hello\\" and she replied \\"Hi\\"',
                "should_not_contain": ['\\"']
            },
            {
                "name": "Collapse Spaces",
                "input": "Too    many     spaces      here",
                "should_not_contain": ["  "]  # Two or more spaces
            }
        ]
        
        for test in cleaning_tests:
            success, data, error = self.make_request(test["input"], "facebook")
            
            if not success:
                self.log_test(f"Text Cleaning - {test['name']}", False, error)
                continue
                
            # Check all text fields in the response
            text_fields_to_check = []
            
            # Add improved ad text
            if "improved" in data and "copy" in data["improved"]:
                text_fields_to_check.append(("improved.copy", data["improved"]["copy"]))
            
            # Add variant texts
            variants = data.get("abTests", {}).get("abc_variants", [])
            for i, variant in enumerate(variants):
                for field in ["headline", "body", "cta"]:
                    if field in variant:
                        text_fields_to_check.append((f"variant_{i+1}.{field}", variant[field]))
            
            # Check for unwanted content
            issues = []
            for field_name, text_value in text_fields_to_check:
                if isinstance(text_value, str):
                    for unwanted in test["should_not_contain"]:
                        if unwanted in text_value:
                            issues.append(f"{field_name} contains '{unwanted}': {text_value[:50]}...")
            
            if issues:
                self.log_test(
                    f"Text Cleaning - {test['name']}", 
                    False, 
                    f"Cleaning failed: {'; '.join(issues[:2])}"
                )
            else:
                self.log_test(f"Text Cleaning - {test['name']}", True, "Text properly cleaned")
    
    def test_variant_uniqueness(self):
        """Test 4: Variants are unique and not templates"""
        test_ad = "Transform your business with our revolutionary AI solution."
        
        success, data, error = self.make_request(test_ad, "facebook")
        
        if not success:
            self.log_test("Variant Uniqueness", False, error)
            return
        
        variants = data.get("abTests", {}).get("abc_variants", [])
        if len(variants) != 3:
            self.log_test("Variant Uniqueness", False, f"Expected 3 variants, got {len(variants)}")
            return
        
        # Check for uniqueness
        headlines = [v.get("headline", "") for v in variants]
        bodies = [v.get("body", "") for v in variants] 
        ctas = [v.get("cta", "") for v in variants]
        
        unique_headlines = len(set(headlines))
        unique_bodies = len(set(bodies))
        unique_ctas = len(set(ctas))
        
        # Check for template phrases
        template_phrases = [
            "Join thousands who love",
            "My journey with", 
            "Here's how it changed everything",
            "See why our community raves",
            "We understand your frustration"
        ]
        
        template_issues = []
        for i, variant in enumerate(variants):
            text_to_check = f"{variant.get('headline', '')} {variant.get('body', '')}"
            for phrase in template_phrases:
                if phrase in text_to_check:
                    template_issues.append(f"Variant {variant.get('version', i+1)} uses template: '{phrase}'")
        
        issues = []
        if unique_headlines != 3:
            issues.append(f"Headlines not unique: {unique_headlines}/3")
        if unique_bodies != 3:
            issues.append(f"Bodies not unique: {unique_bodies}/3") 
        if unique_ctas != 3:
            issues.append(f"CTAs not unique: {unique_ctas}/3")
        if template_issues:
            issues.extend(template_issues[:2])  # First 2 template issues
        
        if issues:
            self.log_test("Variant Uniqueness", False, "; ".join(issues))
        else:
            self.log_test("Variant Uniqueness", True, "All variants are unique and original")
    
    def test_performance(self):
        """Test 5: API performance is acceptable"""
        test_ad = "Get amazing results with our premium solution. Limited time offer!"
        
        start_time = time.time()
        success, data, error = self.make_request(test_ad, "facebook")
        end_time = time.time()
        
        response_time = (end_time - start_time) * 1000  # milliseconds
        
        if not success:
            self.log_test("Performance", False, f"Request failed: {error}")
            return
        
        # Performance thresholds
        if response_time < 5000:  # Under 5 seconds
            self.log_test("Performance", True, f"Response time: {response_time:.0f}ms")
        elif response_time < 15000:  # Under 15 seconds  
            self.log_test("Performance", True, f"Response time acceptable: {response_time:.0f}ms")
        else:  # Over 15 seconds
            self.log_test("Performance", False, f"Response time too slow: {response_time:.0f}ms")
    
    def run_all_tests(self):
        """Run complete test suite"""
        print("=" * 60)
        print("🧪 CONTRACT TESTING SUITE")
        print("=" * 60)
        print(f"Testing endpoint: {self.base_url}{self.endpoint}")
        print()
        
        # Run all test methods
        test_methods = [
            self.test_valid_response_structure,
            self.test_edge_cases,
            self.test_text_cleaning,
            self.test_variant_uniqueness,
            self.test_performance
        ]
        
        for test_method in test_methods:
            print(f"\nRunning {test_method.__name__.replace('test_', '').replace('_', ' ').title()}...")
            try:
                test_method()
            except Exception as e:
                self.log_test(test_method.__name__, False, f"Test crashed: {str(e)}")
        
        # Summary
        print("\n" + "=" * 60)
        print("📊 TEST RESULTS SUMMARY")
        print("=" * 60)
        
        total_tests = len(self.results)
        passed_tests = sum(1 for r in self.results if r["success"])
        failed_tests = total_tests - passed_tests
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests} ✅")
        print(f"Failed: {failed_tests} ❌")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        if failed_tests > 0:
            print(f"\n🚨 FAILED TESTS ({failed_tests}):")
            for result in self.results:
                if not result["success"]:
                    print(f"  ❌ {result['test']}: {result['message']}")
        
        print(f"\n{'🎉 ALL TESTS PASSED!' if failed_tests == 0 else '⚠️ SOME TESTS FAILED - FIX BEFORE DEPLOYMENT'}")
        
        return failed_tests == 0

def main():
    """Main test execution"""
    # Check if server is running
    base_url = "http://127.0.0.1:8000"
    
    try:
        response = requests.get(f"{base_url}/health", timeout=5)
        if response.status_code != 200:
            print("❌ Backend server health check failed")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Backend server not running. Start with: python working_api.py")
        return False
    except Exception as e:
        print(f"❌ Cannot reach backend server: {e}")
        return False
    
    # Run tests
    suite = ContractTestSuite(base_url)
    success = suite.run_all_tests()
    
    # Save results
    with open("contract_test_results.json", "w") as f:
        json.dump(suite.results, f, indent=2)
    
    print(f"\n📄 Detailed results saved to: contract_test_results.json")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)