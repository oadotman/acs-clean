"""
Input validation for ad analysis
Handles edge cases and prevents crashes

Validates:
- Minimum text length (prevents crash on empty input)
- Maximum text length (prevents token limit issues)
- Language support (English, Spanish, German, French, Portuguese)
- Special character sanitization
- Placeholder text detection
- Platform validation
"""

import re
from typing import Dict, List, Optional, Any
from .language_detector import is_supported_language


class ValidationError(Exception):
    """Custom validation error with user-friendly messages"""
    pass


class AdInputValidator:
    """Validates ad input before analysis to prevent crashes and improve UX"""

    # Validation rules
    MIN_HEADLINE_LENGTH = 3
    MAX_HEADLINE_LENGTH = 200
    MIN_BODY_LENGTH = 10
    MAX_BODY_LENGTH = 5000
    MIN_CTA_LENGTH = 2
    MAX_CTA_LENGTH = 50

    ALLOWED_PLATFORMS = ['facebook', 'google', 'linkedin', 'tiktok', 'instagram', 'twitter']

    @staticmethod
    def validate_ad_input(headline: str, body_text: str, cta: str, platform: str) -> Dict[str, Any]:
        """
        Comprehensive validation of ad input

        Args:
            headline: Ad headline
            body_text: Ad body text
            cta: Call-to-action text
            platform: Target platform

        Returns:
            Dict with validated and sanitized values:
                {
                    'headline': str,
                    'body_text': str,
                    'cta': str,
                    'platform': str,
                    'language': str
                }

        Raises:
            ValidationError if validation fails
        """
        errors = []

        # Sanitize inputs first
        headline = AdInputValidator._sanitize_text(headline) if headline else ""
        body_text = AdInputValidator._sanitize_text(body_text) if body_text else ""
        cta = AdInputValidator._sanitize_text(cta) if cta else ""

        # Validate headline
        if len(headline) < AdInputValidator.MIN_HEADLINE_LENGTH:
            errors.append(
                f"Headline too short. Minimum {AdInputValidator.MIN_HEADLINE_LENGTH} characters. "
                f"Got: {len(headline)} characters."
            )
        if len(headline) > AdInputValidator.MAX_HEADLINE_LENGTH:
            errors.append(
                f"Headline too long. Maximum {AdInputValidator.MAX_HEADLINE_LENGTH} characters. "
                f"Got: {len(headline)} characters."
            )

        # Validate body text
        if len(body_text) < AdInputValidator.MIN_BODY_LENGTH:
            errors.append(
                f"Body text too short. Minimum {AdInputValidator.MIN_BODY_LENGTH} characters. "
                f"Got: {len(body_text)} characters."
            )
        if len(body_text) > AdInputValidator.MAX_BODY_LENGTH:
            errors.append(
                f"Body text too long. Maximum {AdInputValidator.MAX_BODY_LENGTH} characters. "
                f"Got: {len(body_text)} characters."
            )

        # Validate CTA
        if len(cta) < AdInputValidator.MIN_CTA_LENGTH:
            errors.append(
                f"CTA too short. Minimum {AdInputValidator.MIN_CTA_LENGTH} characters. "
                f"Got: {len(cta)} characters."
            )
        if len(cta) > AdInputValidator.MAX_CTA_LENGTH:
            errors.append(
                f"CTA too long. Maximum {AdInputValidator.MAX_CTA_LENGTH} characters. "
                f"Got: {len(cta)} characters."
            )

        # Validate platform
        platform = platform.lower() if platform else 'facebook'
        if platform not in AdInputValidator.ALLOWED_PLATFORMS:
            errors.append(
                f"Invalid platform: '{platform}'. "
                f"Allowed platforms: {', '.join(AdInputValidator.ALLOWED_PLATFORMS)}"
            )

        # Validate language (only if text is long enough)
        lang_message = "Language: English (default)"
        if len(headline + body_text + cta) >= 20:
            full_text = f"{headline} {body_text} {cta}"
            is_supported, lang_message = is_supported_language(full_text)
            if not is_supported:
                errors.append(lang_message)

        # Check for common issues
        if AdInputValidator._is_placeholder_text(headline):
            errors.append(
                "Headline appears to be placeholder text (e.g., 'lorem ipsum', 'your headline here'). "
                "Please use real ad copy."
            )

        if AdInputValidator._is_placeholder_text(body_text):
            errors.append(
                "Body text appears to be placeholder text. Please use real ad copy."
            )

        if AdInputValidator._has_excessive_special_chars(body_text):
            errors.append(
                "Body text has too many special characters (>30% of content). "
                "Please use normal text for better analysis."
            )

        # If there are errors, raise ValidationError
        if errors:
            error_message = "\n".join(f"• {error}" for error in errors)
            raise ValidationError(f"Validation failed:\n{error_message}")

        return {
            'headline': headline,
            'body_text': body_text,
            'cta': cta,
            'platform': platform,
            'language': lang_message
        }

    @staticmethod
    def _sanitize_text(text: str) -> str:
        """
        Remove potentially problematic characters

        Removes:
        - Null bytes
        - Excessive whitespace
        - Invisible Unicode characters (zero-width spaces, etc.)
        """
        if not text:
            return ""

        # Remove null bytes
        text = text.replace('\x00', '')

        # Remove invisible Unicode characters
        text = re.sub(r'[\u200B-\u200D\uFEFF]', '', text)

        # Normalize whitespace (replace multiple spaces/tabs/newlines with single space)
        text = re.sub(r'\s+', ' ', text)

        # Strip leading/trailing whitespace
        text = text.strip()

        return text

    @staticmethod
    def _is_placeholder_text(text: str) -> bool:
        """
        Check if text is placeholder/dummy text

        Detects common placeholders:
        - lorem ipsum
        - 'Your headline here'
        - 'Enter text'
        - 'Sample text'
        - Very short test strings
        """
        if not text or len(text) < 5:
            return False

        text_lower = text.lower()

        # Common placeholder patterns
        placeholders = [
            'lorem ipsum',
            'dolor sit amet',
            'your headline here',
            'your text here',
            'enter text',
            'enter your',
            'sample text',
            'example',
            'test',
            'click here',
            'placeholder'
        ]

        # Check for exact matches (short text)
        if len(text) < 20:
            return any(p in text_lower for p in placeholders)

        # For longer text, be more strict (avoid false positives)
        return any(text_lower.startswith(p) or text_lower == p for p in placeholders)

    @staticmethod
    def _has_excessive_special_chars(text: str) -> bool:
        """
        Check for excessive special characters

        Returns True if >30% of characters are special characters
        (excluding common punctuation: . , ! ? - ' ")
        """
        if not text or len(text) < 10:
            return False

        # Count special characters (not letters, digits, or common punctuation)
        special_chars = re.findall(r'[^a-zA-Z0-9\s\.,!?\-\'\"()]', text)
        special_ratio = len(special_chars) / len(text)

        return special_ratio > 0.3  # More than 30% special chars

    @staticmethod
    def validate_quick(headline: str, body_text: str, cta: str) -> bool:
        """
        Quick validation (no exceptions, returns True/False)

        Use this for frontend pre-validation before API call.

        Returns:
            True if input looks valid, False otherwise
        """
        try:
            if not headline or len(headline) < AdInputValidator.MIN_HEADLINE_LENGTH:
                return False
            if not body_text or len(body_text) < AdInputValidator.MIN_BODY_LENGTH:
                return False
            if not cta or len(cta) < AdInputValidator.MIN_CTA_LENGTH:
                return False
            return True
        except Exception:
            return False
