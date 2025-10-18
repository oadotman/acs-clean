#!/usr/bin/env python3
"""
Backend Response Validator & Text Cleaner

This module ensures all API responses match the unified contract EXACTLY
and prevents "Backend did not return valid A/B/C variants" errors.

⚠️ CRITICAL: This must be used before ANY response is sent to the frontend.
"""

import re
from typing import Dict, List, Any, Tuple
from datetime import datetime

def clean_ad_text(text: str) -> str:
    """
    Clean ad text to remove unwanted characters and formatting issues.
    
    Args:
        text: Raw text from AI or user input
        
    Returns:
        Clean text ready for frontend consumption
    """
    if not text or not isinstance(text, str):
        return ""
    
    # Step 1: Strip leading/trailing whitespace
    cleaned = text.strip()
    
    # Step 2: Remove leading/trailing quotes (both single and double)
    cleaned = re.sub(r'^["\']+|["\']+$', '', cleaned)
    
    # Step 3: Fix escaped quotes
    cleaned = cleaned.replace('\\"', '"').replace("\\'", "'")
    
    # Step 4: Replace all newline characters with single space
    cleaned = re.sub(r'\r?\n', ' ', cleaned)
    
    # Step 5: Collapse multiple consecutive spaces
    cleaned = re.sub(r'\s+', ' ', cleaned)
    
    # Step 6: Final trim
    cleaned = cleaned.strip()
    
    # Step 7: Ensure text doesn't end mid-word (basic check)
    if cleaned and cleaned.endswith(('...', ' of', ' an', ' a ', ' the ')):
        # Try to find a better ending point
        words = cleaned.split()
        if len(words) > 1:
            # Remove incomplete phrase from end
            while words and words[-1].lower() in ['of', 'an', 'a', 'the', 'and', 'or', 'but']:
                words.pop()
            if words:
                cleaned = ' '.join(words)
    
    return cleaned

def validate_variant_uniqueness(variants: List[Dict[str, Any]]) -> List[str]:
    """
    Ensure variants don't quote or embed each other's content.
    
    Args:
        variants: List of variant dictionaries
        
    Returns:
        List of error messages (empty if valid)
    """
    errors = []
    
    if len(variants) != 3:
        return [f"Must have exactly 3 variants, got {len(variants)}"]
    
    # Check for duplicate versions
    versions = [v.get('version') for v in variants]
    if len(set(versions)) != 3 or not all(v in ['A', 'B', 'C'] for v in versions):
        errors.append("Variants must have unique versions A, B, and C")
    
    # Check that headlines are unique
    headlines = [clean_ad_text(v.get('headline', '')) for v in variants]
    if len(set(headlines)) != 3:
        errors.append("All variant headlines must be unique")
    
    # Check that body text is unique  
    bodies = [clean_ad_text(v.get('body', '')) for v in variants]
    if len(set(bodies)) != 3:
        errors.append("All variant body texts must be unique")
    
    # Check that CTAs are unique
    ctas = [clean_ad_text(v.get('cta', '')) for v in variants]
    if len(set(ctas)) != 3:
        errors.append("All variant CTAs must be unique")
    
    # Check for template-like phrases
    template_phrases = [
        "Join thousands who love",
        "My journey with", 
        "Here's how it changed everything",
        "See why our community raves",
        "We understand your frustration"
    ]
    
    for i, variant in enumerate(variants):
        headline = variant.get('headline', '')
        body = variant.get('body', '')
        
        for phrase in template_phrases:
            if phrase in headline or phrase in body:
                errors.append(f"Variant {variant.get('version', i+1)} contains template phrase: '{phrase}'")
    
    return errors

def validate_response_contract(response: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """
    Validate response against the unified API contract.
    
    Args:
        response: Response dictionary to validate
        
    Returns:
        Tuple of (is_valid, list_of_errors)
    """
    errors = []
    
    # Check required top-level fields
    if not isinstance(response, dict):
        return False, ["Response must be a dictionary"]
    
    if response.get('success') is not True:
        errors.append("success must be true")
    
    if not isinstance(response.get('platform'), str):
        errors.append("platform must be a string")
    
    # Check scores are numbers between 0-100
    score_fields = ['originalScore', 'improvedScore', 'confidenceScore']
    for field in score_fields:
        value = response.get(field)
        if not isinstance(value, (int, float)) or not 0 <= value <= 100:
            errors.append(f"{field} must be a number between 0-100, got {type(value).__name__}: {value}")
    
    # Check original ad structure
    original = response.get('original')
    if not isinstance(original, dict):
        errors.append("original must be a dictionary")
    else:
        if not isinstance(original.get('copy'), str):
            errors.append("original.copy must be a string")
        if not isinstance(original.get('score'), (int, float)):
            errors.append("original.score must be a number")
    
    # Check improved ad structure
    improved = response.get('improved')
    if not isinstance(improved, dict):
        errors.append("improved must be a dictionary")
    else:
        if not isinstance(improved.get('copy'), str):
            errors.append("improved.copy must be a string")
        if not isinstance(improved.get('score'), (int, float)):
            errors.append("improved.score must be a number")
        if not isinstance(improved.get('improvements'), list):
            errors.append("improved.improvements must be a list")
    
    # Check abTests structure - CRITICAL
    ab_tests = response.get('abTests')
    if not isinstance(ab_tests, dict):
        errors.append("abTests must be a dictionary")
    else:
        if not isinstance(ab_tests.get('variations'), list):
            errors.append("abTests.variations must be a list")
        
        abc_variants = ab_tests.get('abc_variants')
        if not isinstance(abc_variants, list):
            errors.append("abTests.abc_variants must be a list")
        elif len(abc_variants) != 3:
            errors.append(f"abTests.abc_variants must have exactly 3 items, got {len(abc_variants)}")
        else:
            # Validate each variant
            required_variant_fields = ['id', 'version', 'focus', 'name', 'description', 'bestFor', 'headline', 'body', 'cta', 'platform']
            for i, variant in enumerate(abc_variants):
                if not isinstance(variant, dict):
                    errors.append(f"Variant {i+1} must be a dictionary")
                    continue
                
                for field in required_variant_fields:
                    if field not in variant:
                        errors.append(f"Variant {i+1} missing required field: {field}")
                    elif field in ['headline', 'body', 'cta', 'platform', 'id', 'version', 'focus', 'name', 'description']:
                        if not isinstance(variant[field], str):
                            errors.append(f"Variant {i+1}.{field} must be a string")
                    elif field == 'bestFor':
                        if not isinstance(variant[field], list):
                            errors.append(f"Variant {i+1}.bestFor must be a list")
            
            # Check variant uniqueness
            uniqueness_errors = validate_variant_uniqueness(abc_variants)
            errors.extend(uniqueness_errors)
    
    # Check required object fields exist
    required_objects = ['compliance', 'psychology', 'roi', 'legal', 'metadata']
    for field in required_objects:
        if not isinstance(response.get(field), dict):
            errors.append(f"{field} must be a dictionary")
    
    # Check required string fields
    required_strings = ['tips', 'analysis_id']
    for field in required_strings:
        if not isinstance(response.get(field), str):
            errors.append(f"{field} must be a string")
    
    # Check required boolean fields
    if response.get('comprehensive_analysis_complete') is not True:
        errors.append("comprehensive_analysis_complete must be true")
    
    return len(errors) == 0, errors

def clean_response(response: Dict[str, Any]) -> Dict[str, Any]:
    """
    Clean all text fields in the response to ensure quality output.
    
    Args:
        response: Raw response dictionary
        
    Returns:
        Cleaned response dictionary
    """
    if not isinstance(response, dict):
        return response
    
    # Clean improved ad text
    if 'improved' in response and isinstance(response['improved'], dict):
        if 'copy' in response['improved']:
            response['improved']['copy'] = clean_ad_text(response['improved']['copy'])
    
    # Clean tips
    if 'tips' in response:
        response['tips'] = clean_ad_text(response['tips'])
    
    # Clean variants
    if 'abTests' in response and 'abc_variants' in response['abTests']:
        variants = response['abTests']['abc_variants']
        if isinstance(variants, list):
            for variant in variants:
                if isinstance(variant, dict):
                    for text_field in ['headline', 'body', 'cta', 'name', 'description']:
                        if text_field in variant:
                            variant[text_field] = clean_ad_text(variant[text_field])
    
    return response

def validate_and_clean_response(response: Dict[str, Any]) -> Tuple[bool, Dict[str, Any], List[str]]:
    """
    Master function: Clean and validate response before sending to frontend.
    
    Args:
        response: Raw response from API endpoint
        
    Returns:
        Tuple of (is_valid, cleaned_response, error_messages)
    """
    # Step 1: Clean all text fields
    cleaned_response = clean_response(response.copy())
    
    # Step 2: Validate contract compliance
    is_valid, errors = validate_response_contract(cleaned_response)
    
    # Step 3: Log validation results
    if not is_valid:
        print(f"❌ RESPONSE VALIDATION FAILED:")
        for error in errors:
            print(f"   - {error}")
        print(f"❌ Full response (first 500 chars): {str(cleaned_response)[:500]}...")
    else:
        print("✅ Response validation passed - sending to frontend")
    
    return is_valid, cleaned_response, errors

# Test function
def test_validator():
    """Test the validator with sample data"""
    test_response = {
        "success": True,
        "platform": "facebook",
        "originalScore": 65,
        "improvedScore": 85,
        "confidenceScore": 85,
        "original": {"copy": "Test ad", "score": 65},
        "improved": {"copy": "Better test ad", "score": 85, "improvements": []},
        "abTests": {
            "variations": [],
            "abc_variants": [
                {
                    "id": "variant_a",
                    "version": "A",
                    "focus": "benefit",
                    "name": "Social Proof",
                    "description": "Tests social proof",
                    "bestFor": ["users"],
                    "headline": "Unique headline A",
                    "body": "Unique body A",
                    "cta": "Click A",
                    "platform": "facebook"
                },
                {
                    "id": "variant_b", 
                    "version": "B",
                    "focus": "problem",
                    "name": "Problem Solution",
                    "description": "Tests problem solving",
                    "bestFor": ["users"],
                    "headline": "Unique headline B",
                    "body": "Unique body B", 
                    "cta": "Click B",
                    "platform": "facebook"
                },
                {
                    "id": "variant_c",
                    "version": "C",
                    "focus": "story", 
                    "name": "Story Driven",
                    "description": "Tests storytelling",
                    "bestFor": ["users"],
                    "headline": "Unique headline C",
                    "body": "Unique body C",
                    "cta": "Click C",
                    "platform": "facebook"
                }
            ]
        },
        "compliance": {},
        "psychology": {},
        "roi": {},
        "legal": {},
        "metadata": {},
        "tips": "Test tips",
        "analysis_id": "test-123",
        "comprehensive_analysis_complete": True
    }
    
    valid, cleaned, errors = validate_and_clean_response(test_response)
    print(f"Test result: {'PASSED' if valid else 'FAILED'}")
    if errors:
        print("Errors:", errors)

if __name__ == "__main__":
    test_validator()