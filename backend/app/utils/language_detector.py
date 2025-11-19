"""
Language detection and validation for ad copy

Supports top 5 revenue-generating languages:
1. English (primary) - 60% of global ad spend
2. Spanish - 15% of US market, LATAM growth
3. German - High-value European market
4. French - European + African markets
5. Portuguese - Brazil (huge market)
"""

from typing import Tuple, Optional
import logging
import re

logger = logging.getLogger(__name__)

# Supported languages (ISO 639-1 codes)
SUPPORTED_LANGUAGES = {
    'en': 'English',
    'es': 'Spanish',
    'de': 'German',
    'fr': 'French',
    'pt': 'Portuguese'
}


def detect_language(text: str) -> Tuple[Optional[str], float]:
    """
    Detect language from text using pattern matching

    This is a simple implementation that works without external dependencies.
    For production, consider using langdetect library for better accuracy.

    Args:
        text: Input text to analyze

    Returns:
        Tuple of (language_code, confidence)
        Example: ('en', 0.95)
    """
    if not text or len(text) < 10:
        logger.warning(f"Text too short for reliable detection: {len(text)} chars")
        return None, 0.0

    text_lower = text.lower()

    # Language-specific patterns and keywords
    language_patterns = {
        'en': {
            'keywords': ['the', 'and', 'you', 'your', 'get', 'now', 'with', 'for', 'this', 'from'],
            'patterns': [r'\b(get|buy|shop|save|free)\b', r'\b(you|your)\b']
        },
        'es': {
            'keywords': ['el', 'la', 'los', 'las', 'de', 'que', 'tu', 'para', 'con', 'más'],
            'patterns': [r'\b(el|la|los|las)\b', r'ción\b', r'dad\b']
        },
        'de': {
            'keywords': ['der', 'die', 'das', 'und', 'sie', 'für', 'mit', 'von', 'den', 'dem'],
            'patterns': [r'\b(der|die|das)\b', r'ung\b', r'keit\b']
        },
        'fr': {
            'keywords': ['le', 'la', 'les', 'de', 'et', 'vous', 'pour', 'avec', 'des', 'sur'],
            'patterns': [r'\b(le|la|les)\b', r'tion\b', r'ment\b']
        },
        'pt': {
            'keywords': ['o', 'a', 'os', 'as', 'de', 'que', 'para', 'com', 'você', 'mais'],
            'patterns': [r'\b(o|a|os|as)\b', r'ção\b', r'dade\b']
        }
    }

    scores = {}

    for lang_code, patterns in language_patterns.items():
        score = 0

        # Check keywords
        keyword_matches = sum(1 for keyword in patterns['keywords'] if keyword in text_lower.split())
        score += keyword_matches

        # Check patterns
        for pattern in patterns['patterns']:
            matches = len(re.findall(pattern, text_lower))
            score += matches

        scores[lang_code] = score

    # Find language with highest score
    if not scores or max(scores.values()) == 0:
        # Default to English if no patterns match
        logger.info("No language patterns matched, defaulting to English")
        return 'en', 0.5

    detected_lang = max(scores, key=scores.get)
    max_score = scores[detected_lang]

    # Calculate confidence based on score
    total_score = sum(scores.values())
    confidence = max_score / total_score if total_score > 0 else 0.5

    logger.info(f"Detected language: {detected_lang} (confidence: {confidence:.2f}, score: {max_score})")
    return detected_lang, confidence


def is_supported_language(text: str) -> Tuple[bool, str]:
    """
    Check if text is in a supported language

    Args:
        text: Input text to validate

    Returns:
        Tuple of (is_supported, message)
        Example: (True, "Detected: English")
    """
    lang_code, confidence = detect_language(text)

    if not lang_code:
        return False, "Could not detect language. Please use at least 10 characters."

    if lang_code in SUPPORTED_LANGUAGES:
        lang_name = SUPPORTED_LANGUAGES[lang_code]
        return True, f"Detected: {lang_name}"

    # Find closest supported language to suggest
    lang_name = _get_language_name(lang_code)
    supported_list = ', '.join(SUPPORTED_LANGUAGES.values())

    return False, (
        f"Detected: {lang_name}. "
        f"Currently supported languages: {supported_list}. "
        f"Want this language? Contact support@adcopysurge.com"
    )


def _get_language_name(lang_code: str) -> str:
    """Get full language name from ISO code"""
    language_names = {
        'en': 'English', 'es': 'Spanish', 'de': 'German', 'fr': 'French', 'pt': 'Portuguese',
        'it': 'Italian', 'nl': 'Dutch', 'pl': 'Polish', 'ru': 'Russian', 'ja': 'Japanese',
        'zh-cn': 'Chinese (Simplified)', 'zh-tw': 'Chinese (Traditional)', 'ko': 'Korean',
        'ar': 'Arabic', 'hi': 'Hindi', 'tr': 'Turkish', 'sv': 'Swedish', 'da': 'Danish',
        'no': 'Norwegian', 'fi': 'Finnish'
    }
    return language_names.get(lang_code, f"Unknown ({lang_code})")


def get_supported_languages_list() -> list:
    """
    Get list of supported languages for display

    Returns:
        List of supported language names
        Example: ['English', 'Spanish', 'German', 'French', 'Portuguese']
    """
    return list(SUPPORTED_LANGUAGES.values())
