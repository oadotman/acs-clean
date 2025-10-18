"""
Content Validator and Sanitizer

Validates and sanitizes AI-generated content to ensure it meets all platform 
requirements including character limits, uniqueness, banned phrases, etc.
"""
import re
import json
import logging
from typing import Dict, Any, List, Optional, Tuple
from difflib import SequenceMatcher

from .platform_registry import get_platform_config, validate_platform_content

logger = logging.getLogger(__name__)

class ValidationResult:
    """Result of content validation with confidence scoring"""
    
    def __init__(self):
        self.is_valid: bool = True
        self.errors: List[str] = []
        self.warnings: List[str] = []
        self.sanitized_content: Dict[str, Any] = {}
        self.char_counts: Dict[str, int] = {}
        self.validation_report: Dict[str, Any] = {}
        self.confidence_score: int = 100
        self.quality_issues: List[str] = []
        self.platform_specific_issues: List[str] = []
        self.template_phrases_found: List[str] = []

class ContentValidator:
    """Validates and sanitizes platform-specific content"""
    
    def __init__(self):
        self.similarity_threshold = 0.7  # For detecting near-duplicate content
    
    def validate_and_sanitize(self, content: Dict[str, Any], platform_id: str, strict_mode: bool = True) -> ValidationResult:
        """Main validation and sanitization method"""
        result = ValidationResult()
        
        # Get platform configuration
        config = get_platform_config(platform_id)
        if not config:
            result.is_valid = False
            result.errors.append(f"Unknown platform: {platform_id}")
            return result
        
        # Step 1: Parse and validate JSON structure
        parsed_content = self._parse_content(content, config, result)
        if not result.is_valid and strict_mode:
            return result
        
        # Step 2: Validate required fields
        self._validate_required_fields(parsed_content, config, result)
        if not result.is_valid and strict_mode:
            return result
        
        # Step 3: Check banned phrases
        self._check_banned_phrases(parsed_content, config, result)
        
        # Step 4: Validate character limits
        self._validate_character_limits(parsed_content, config, result)
        
        # Step 5: Check uniqueness requirements (Google Ads headlines)
        self._check_uniqueness_requirements(parsed_content, config, result)
        
        # Step 6: Check repetition rules
        self._check_repetition_rules(parsed_content, config, result)
        
        # Step 7: Platform-specific advanced checks
        self._perform_platform_specific_checks(parsed_content, platform_id, result)
        
        # Step 8: Check for template phrases
        self._detect_template_phrases(parsed_content, result)
        
        # Step 9: Calculate confidence score
        result.confidence_score = self._calculate_confidence_score(parsed_content, config, result)
        
        # Step 10: Sanitize content
        result.sanitized_content = self._sanitize_content(parsed_content, config, result)
        
        # Step 11: Calculate character counts
        result.char_counts = self._calculate_char_counts(result.sanitized_content)
        
        # Step 12: Final validation after sanitization
        if strict_mode:
            final_validation = validate_platform_content(platform_id, result.sanitized_content)
            if not final_validation['valid']:
                result.errors.extend(final_validation['errors'])
                result.is_valid = False
        
        result.validation_report = {
            'platform_id': platform_id,
            'strict_mode': strict_mode,
            'total_errors': len(result.errors),
            'total_warnings': len(result.warnings),
            'confidence_score': result.confidence_score,
            'quality_issues': result.quality_issues,
            'platform_specific_issues': result.platform_specific_issues,
            'template_phrases_found': result.template_phrases_found,
            'fields_validated': list(result.sanitized_content.keys())
        }
        
        return result
    
    def _parse_content(self, content: Any, config, result: ValidationResult) -> Dict[str, Any]:
        """Parse content from various input formats"""
        if isinstance(content, str):
            try:
                # Try to parse as JSON
                parsed = json.loads(content)
                if isinstance(parsed, dict):
                    return parsed
                else:
                    result.errors.append("Content must be a JSON object")
                    return {}
            except json.JSONDecodeError:
                result.errors.append("Invalid JSON format in content")
                return {}
        elif isinstance(content, dict):
            return content
        else:
            result.errors.append("Content must be a dictionary or valid JSON string")
            return {}
    
    def _validate_required_fields(self, content: Dict[str, Any], config, result: ValidationResult):
        """Validate that all required fields are present"""
        for field_name, field_config in config.fields.items():
            if field_config.required:
                field_value = content.get(field_name)
                
                if not field_value:
                    result.errors.append(f"Required field '{field_name}' is missing or empty")
                    result.is_valid = False
                elif isinstance(field_value, list) and len(field_value) == 0:
                    result.errors.append(f"Required field '{field_name}' cannot be an empty list")
                    result.is_valid = False
                elif isinstance(field_value, str) and not field_value.strip():
                    result.errors.append(f"Required field '{field_name}' cannot be empty")
                    result.is_valid = False
    
    def _check_banned_phrases(self, content: Dict[str, Any], config, result: ValidationResult):
        """Check for banned phrases in content"""
        all_text = self._extract_all_text(content)
        
        for banned_phrase in config.banned_phrases:
            if banned_phrase.lower() in all_text.lower():
                result.errors.append(f"Content contains banned phrase: '{banned_phrase}'")
                result.is_valid = False
    
    def _validate_character_limits(self, content: Dict[str, Any], config, result: ValidationResult):
        """Validate character limits for all fields"""
        for field_name, field_config in config.fields.items():
            field_value = content.get(field_name)
            
            if not field_value:
                continue
            
            if isinstance(field_value, str):
                char_count = len(field_value)
                if char_count > field_config.max_chars:
                    if config.hard_limits:
                        result.errors.append(
                            f"Field '{field_name}' exceeds {field_config.max_chars} character limit "
                            f"({char_count} chars)"
                        )
                        result.is_valid = False
                    else:
                        result.warnings.append(
                            f"Field '{field_name}' exceeds recommended {field_config.max_chars} character limit "
                            f"({char_count} chars)"
                        )
            
            elif isinstance(field_value, list):
                for i, item in enumerate(field_value):
                    if isinstance(item, str):
                        char_count = len(item)
                        if char_count > field_config.max_chars:
                            if config.hard_limits:
                                result.errors.append(
                                    f"Field '{field_name}[{i}]' exceeds {field_config.max_chars} character limit "
                                    f"({char_count} chars)"
                                )
                                result.is_valid = False
                            else:
                                result.warnings.append(
                                    f"Field '{field_name}[{i}]' exceeds recommended {field_config.max_chars} character limit "
                                    f"({char_count} chars)"
                                )
    
    def _check_uniqueness_requirements(self, content: Dict[str, Any], config, result: ValidationResult):
        """Check uniqueness requirements (e.g., Google Ads headlines)"""
        for field_name, field_config in config.fields.items():
            if field_config.uniqueness:
                field_value = content.get(field_name)
                
                if isinstance(field_value, list):
                    # Check for exact duplicates
                    if len(field_value) != len(set([item.lower() for item in field_value if isinstance(item, str)])):
                        result.errors.append(f"Field '{field_name}' contains duplicate items - all items must be unique")
                        result.is_valid = False
                    
                    # Check for near-duplicates (similarity threshold)
                    for i, item1 in enumerate(field_value):
                        for j, item2 in enumerate(field_value[i+1:], i+1):
                            if isinstance(item1, str) and isinstance(item2, str):
                                similarity = self._calculate_similarity(item1, item2)
                                if similarity > self.similarity_threshold:
                                    result.errors.append(
                                        f"Field '{field_name}' items {i} and {j} are too similar "
                                        f"(similarity: {similarity:.2f}). All items must be unique."
                                    )
                                    result.is_valid = False
    
    def _check_repetition_rules(self, content: Dict[str, Any], config, result: ValidationResult):
        """Check repetition rules (e.g., headline not in body)"""
        rules = config.repetition_rules
        
        if rules.get('preventHeadlineInBody', False):
            headline = content.get('headline', '')
            body = content.get('body', '')
            
            if headline and body and headline.strip().lower() in body.lower():
                result.errors.append("Headline text should not be repeated in body copy")
                result.is_valid = False
        
        if rules.get('enforceHeadlineUniqueness', False):
            headlines = content.get('headlines', [])
            if headlines and len(headlines) != len(set([h.lower() for h in headlines if isinstance(h, str)])):
                result.errors.append("All headlines must be completely unique")
                result.is_valid = False
    
    def _sanitize_content(self, content: Dict[str, Any], config, result: ValidationResult) -> Dict[str, Any]:
        """Sanitize content to fix common issues"""
        sanitized = {}
        
        for field_name, field_value in content.items():
            field_config = config.fields.get(field_name)
            if not field_config:
                # Keep unknown fields as-is
                sanitized[field_name] = field_value
                continue
            
            if isinstance(field_value, str):
                sanitized[field_name] = self._sanitize_string_field(field_value, field_config)
            elif isinstance(field_value, list):
                sanitized[field_name] = self._sanitize_list_field(field_value, field_config)
            else:
                sanitized[field_name] = field_value
        
        return sanitized
    
    def _sanitize_string_field(self, value: str, field_config) -> str:
        """Sanitize a string field"""
        # Clean whitespace
        value = ' '.join(value.split())
        
        # Remove trailing punctuation from CTAs
        if 'cta' in str(field_config).lower():
            value = re.sub(r'[.!?]+$', '', value)
        
        # Smart trim to character limit
        if len(value) > field_config.max_chars:
            value = self._smart_trim(value, field_config.max_chars)
        
        return value.strip()
    
    def _sanitize_list_field(self, value: List, field_config) -> List:
        """Sanitize a list field"""
        sanitized = []
        
        for item in value:
            if isinstance(item, str):
                sanitized_item = self._sanitize_string_field(item, field_config)
                if sanitized_item:  # Only add non-empty items
                    sanitized.append(sanitized_item)
        
        # Ensure correct count
        while len(sanitized) < field_config.count and sanitized:
            # Duplicate last item if needed (with variation)
            base_item = sanitized[-1]
            variation = self._create_variation(base_item, len(sanitized))
            sanitized.append(variation)
        
        return sanitized[:field_config.count]
    
    def _smart_trim(self, text: str, max_chars: int, preserve_words: bool = True) -> str:
        """Trim text to character limit without breaking words"""
        if len(text) <= max_chars:
            return text
        
        if not preserve_words:
            return text[:max_chars]
        
        # Find the last space before the limit
        trimmed = text[:max_chars]
        last_space = trimmed.rfind(' ')
        
        if last_space > max_chars * 0.8:  # Only trim at word boundary if it's not too short
            return text[:last_space].strip()
        else:
            return text[:max_chars].strip()
    
    def _create_variation(self, base_text: str, variation_index: int) -> str:
        """Create a variation of text for uniqueness"""
        if variation_index == 1:
            return f"Premium {base_text}"
        elif variation_index == 2:
            return f"Top {base_text}"
        else:
            return f"Best {base_text}"
    
    def _calculate_similarity(self, text1: str, text2: str) -> float:
        """Calculate similarity between two texts"""
        return SequenceMatcher(None, text1.lower(), text2.lower()).ratio()
    
    def _extract_all_text(self, content: Dict[str, Any]) -> str:
        """Extract all text from content for banned phrase checking"""
        all_text = ""
        
        for field_name, field_value in content.items():
            if isinstance(field_value, str):
                all_text += f" {field_value}"
            elif isinstance(field_value, list):
                for item in field_value:
                    if isinstance(item, str):
                        all_text += f" {item}"
        
        return all_text
    
    def _calculate_char_counts(self, content: Dict[str, Any]) -> Dict[str, int]:
        """Calculate character counts for all fields"""
        char_counts = {}
        
        for field_name, field_value in content.items():
            if isinstance(field_value, str):
                char_counts[field_name] = len(field_value)
            elif isinstance(field_value, list):
                char_counts[field_name] = sum(len(str(item)) for item in field_value)
        
        return char_counts
    
    def _perform_platform_specific_checks(self, content: Dict[str, Any], platform_id: str, result: ValidationResult):
        """Perform platform-specific validation checks"""
        if platform_id == 'google_ads':
            self._check_google_ads_requirements(content, result)
        elif platform_id == 'instagram':
            self._check_instagram_requirements(content, result)
        elif platform_id == 'linkedin':
            self._check_linkedin_requirements(content, result)
        elif platform_id == 'twitter_x':
            self._check_twitter_requirements(content, result)
        elif platform_id == 'facebook':
            self._check_facebook_requirements(content, result)
        elif platform_id == 'tiktok':
            self._check_tiktok_requirements(content, result)
    
    def _check_google_ads_requirements(self, content: Dict[str, Any], result: ValidationResult):
        """Google Ads specific validation"""
        headlines = content.get('headlines', [])
        
        if len(headlines) >= 2:
            # Check headline uniqueness more strictly
            for i, headline1 in enumerate(headlines):
                for j, headline2 in enumerate(headlines[i+1:], i+1):
                    if isinstance(headline1, str) and isinstance(headline2, str):
                        # Check exact match
                        if headline1.lower().strip() == headline2.lower().strip():
                            issue = f"Headlines {i+1} and {j+1} are identical: '{headline1}'"
                            result.platform_specific_issues.append(issue)
                            result.errors.append(issue)
                            result.is_valid = False
                        
                        # Check similarity (more strict than base validator)
                        similarity = self._calculate_similarity(headline1, headline2)
                        if similarity > 0.8:  # Stricter threshold for Google Ads
                            issue = f"Headlines {i+1} and {j+1} are too similar ({similarity:.2f}): '{headline1}' vs '{headline2}'"
                            result.platform_specific_issues.append(issue)
                            result.warnings.append(issue)
        
        # Check for keyword stuffing
        all_headlines_text = ' '.join(headlines) if headlines else ''
        descriptions = content.get('descriptions', [])
        all_descriptions_text = ' '.join(descriptions) if descriptions else ''
        
        # Look for repeated words across headlines/descriptions
        words_count = {}
        for text in [all_headlines_text, all_descriptions_text]:
            words = re.findall(r'\b\w+\b', text.lower())
            for word in words:
                if len(word) > 3:  # Ignore short words
                    words_count[word] = words_count.get(word, 0) + 1
        
        repeated_words = [word for word, count in words_count.items() if count > 3]
        if repeated_words:
            issue = f"Potential keyword stuffing detected: {', '.join(repeated_words[:3])}"
            result.platform_specific_issues.append(issue)
            result.warnings.append(issue)
    
    def _check_instagram_requirements(self, content: Dict[str, Any], result: ValidationResult):
        """Instagram specific validation"""
        hashtags = content.get('hashtags', [])
        
        # Check hashtag count (should be 5-30, but our config allows up to 10)
        if len(hashtags) > 30:
            issue = f"Too many hashtags ({len(hashtags)}). Instagram allows maximum 30."
            result.platform_specific_issues.append(issue)
            result.errors.append(issue)
            result.is_valid = False
        
        # Check hashtag format
        for i, hashtag in enumerate(hashtags):
            if isinstance(hashtag, str):
                if not hashtag.startswith('#'):
                    issue = f"Hashtag {i+1} missing # symbol: '{hashtag}'"
                    result.platform_specific_issues.append(issue)
                    result.warnings.append(issue)
                
                if len(hashtag) > 100:  # Instagram hashtag limit
                    issue = f"Hashtag {i+1} too long ({len(hashtag)} chars): '{hashtag[:50]}...'"
                    result.platform_specific_issues.append(issue)
                    result.warnings.append(issue)
        
        # Check for hook in first 125 characters
        body = content.get('body', '')
        if isinstance(body, str) and len(body) > 125:
            first_125 = body[:125]
            if not any(word in first_125.lower() for word in ['discover', 'see', 'look', 'check', 'find', 'get', 'try', 'new', 'now']):
                issue = "First 125 characters should include a strong hook word"
                result.platform_specific_issues.append(issue)
                result.warnings.append(issue)
    
    def _check_linkedin_requirements(self, content: Dict[str, Any], result: ValidationResult):
        """LinkedIn specific validation"""
        # Check for casual language that's unprofessional
        casual_phrases = ['lol', 'omg', 'tbh', 'dm me', 'hit me up', 'sup', 'hey guys', 'whatup', 'ur', 'u r']
        
        all_text = self._extract_all_text(content).lower()
        
        found_casual = [phrase for phrase in casual_phrases if phrase in all_text]
        if found_casual:
            issue = f"Unprofessional language detected: {', '.join(found_casual)}"
            result.platform_specific_issues.append(issue)
            result.errors.append(issue)
            result.is_valid = False
        
        # Check for business/professional tone indicators
        professional_indicators = ['roi', 'revenue', 'growth', 'efficiency', 'productivity', 'solutions', 'enterprise', 'business', 'professional', 'industry']
        has_professional_tone = any(indicator in all_text for indicator in professional_indicators)
        
        if not has_professional_tone:
            issue = "Content lacks professional/business tone expected for LinkedIn"
            result.platform_specific_issues.append(issue)
            result.warnings.append(issue)
    
    def _check_twitter_requirements(self, content: Dict[str, Any], result: ValidationResult):
        """Twitter/X specific validation"""
        body = content.get('body', '')
        
        if isinstance(body, str):
            # Check for embedded CTA
            cta_indicators = ['click', 'visit', 'check', 'see', 'get', 'try', 'join', 'follow', 'download']
            has_cta = any(indicator in body.lower() for indicator in cta_indicators)
            
            if not has_cta:
                issue = "Twitter/X body should include an embedded call-to-action"
                result.platform_specific_issues.append(issue)
                result.warnings.append(issue)
            
            # Check for quotable/shareable elements
            shareable_indicators = ['tip:', 'fact:', 'remember:', 'pro tip:', 'did you know', '💡', '🔥', '🚀']
            is_shareable = any(indicator in body.lower() for indicator in shareable_indicators)
            
            if not is_shareable and len(body) > 50:
                issue = "Consider adding shareable elements (tips, facts, emojis) for better engagement"
                result.platform_specific_issues.append(issue)
                result.warnings.append(issue)
    
    def _check_facebook_requirements(self, content: Dict[str, Any], result: ValidationResult):
        """Facebook specific validation"""
        # Check for community/social elements
        social_indicators = ['join', 'community', 'share', 'connect', 'together', 'family', 'friends', 'network']
        all_text = self._extract_all_text(content).lower()
        
        has_social_element = any(indicator in all_text for indicator in social_indicators)
        if not has_social_element:
            issue = "Consider adding social/community elements for better Facebook engagement"
            result.platform_specific_issues.append(issue)
            result.warnings.append(issue)
    
    def _check_tiktok_requirements(self, content: Dict[str, Any], result: ValidationResult):
        """TikTok specific validation"""
        body = content.get('body', '')
        
        if isinstance(body, str):
            # Check for Gen-Z/trendy language
            trendy_indicators = ['pov:', 'no cap', 'fr', 'periodt', 'slay', 'vibe', 'mood', 'lowkey', 'highkey', 'bet']
            has_trendy = any(indicator in body.lower() for indicator in trendy_indicators)
            
            # Check for hook words
            hook_words = ['wait', 'stop', 'omg', 'wow', 'crazy', 'insane', 'mind-blown', 'secret', 'hack']
            has_hook = any(hook in body.lower() for hook in hook_words)
            
            if not has_trendy and not has_hook:
                issue = "Consider adding trendy language or hook words for TikTok engagement"
                result.platform_specific_issues.append(issue)
                result.warnings.append(issue)
    
    def _detect_template_phrases(self, content: Dict[str, Any], result: ValidationResult):
        """Detect generic/robotic template phrases"""
        template_phrases = [
            'are you tired of',
            'introducing our',
            'the solution you\'ve been waiting for',
            'revolutionary new',
            'game-changing',
            'industry-leading',
            'cutting-edge',
            'state-of-the-art',
            'best-in-class',
            'world-class',
            'take your [x] to the next level',
            'transform your life',
            'change your life forever',
            'the secret to',
            'discover the power of',
            'unleash the potential',
            'boost your [x] today',
            'don\'t miss out',
            'limited time only',
            'act now',
            'call now',
            'order now',
            'buy now and save',
        ]
        
        all_text = self._extract_all_text(content).lower()
        
        found_templates = []
        for phrase in template_phrases:
            # Use regex to match with wildcards
            pattern = phrase.replace('[x]', r'\w+')
            if re.search(pattern, all_text):
                found_templates.append(phrase)
        
        if found_templates:
            result.template_phrases_found = found_templates
            for phrase in found_templates:
                issue = f"Generic template phrase detected: '{phrase}'"
                result.quality_issues.append(issue)
                result.warnings.append(issue)
    
    def _calculate_confidence_score(self, content: Dict[str, Any], config, result: ValidationResult) -> int:
        """Calculate confidence score from 0-100"""
        score = 100
        
        # Subtract 20 points for each validation error
        score -= len(result.errors) * 20
        
        # Subtract 10 points for each quality issue
        score -= len(result.quality_issues) * 10
        
        # Subtract 5 points for each platform-specific issue
        score -= len(result.platform_specific_issues) * 5
        
        # Subtract 5 points for each template phrase
        score -= len(result.template_phrases_found) * 5
        
        # Bonus points for good practices
        headline = content.get('headline', '')
        cta = content.get('cta', '')
        
        # Bonus for short headline (under 60 chars)
        if isinstance(headline, str) and 0 < len(headline) < 60:
            score += 5
        
        # Bonus for short CTA (5 words or less)
        if isinstance(cta, str) and len(cta.split()) <= 5 and len(cta.split()) > 0:
            score += 5
        
        # Bonus for proper field structure
        required_fields = [field for field, field_config in config.fields.items() if field_config.required]
        has_all_required = all(content.get(field) for field in required_fields)
        if has_all_required:
            score += 10
        
        # Ensure score is between 0-100
        return max(0, min(100, score))
    
    def create_retry_feedback(self, validation_result: ValidationResult) -> str:
        """Create feedback message for LLM retry"""
        if validation_result.is_valid and validation_result.confidence_score >= 60:
            return ""
        
        feedback_parts = ["VALIDATION ISSUES - Please fix:"]
        
        # Add critical errors first
        for error in validation_result.errors:
            feedback_parts.append(f"- CRITICAL: {error}")
        
        # Add platform-specific issues
        for issue in validation_result.platform_specific_issues:
            feedback_parts.append(f"- PLATFORM: {issue}")
        
        # Add template phrase issues
        for phrase in validation_result.template_phrases_found:
            feedback_parts.append(f"- TEMPLATE: Avoid generic phrase '{phrase}'")
        
        # Add quality suggestions
        for issue in validation_result.quality_issues:
            feedback_parts.append(f"- QUALITY: {issue}")
        
        feedback_parts.append(f"\nCurrent confidence score: {validation_result.confidence_score}/100")
        feedback_parts.append("Target: 60+ confidence score")
        feedback_parts.append("\nPlease generate improved content addressing all issues above.")
        
        return "\n".join(feedback_parts)

# Convenience functions
def validate_content(content: Dict[str, Any], platform_id: str, strict_mode: bool = True) -> ValidationResult:
    """Validate content for platform"""
    validator = ContentValidator()
    return validator.validate_and_sanitize(content, platform_id, strict_mode)

def sanitize_content(content: Dict[str, Any], platform_id: str) -> Dict[str, Any]:
    """Sanitize content for platform"""
    validator = ContentValidator()
    result = validator.validate_and_sanitize(content, platform_id, strict_mode=False)
    return result.sanitized_content