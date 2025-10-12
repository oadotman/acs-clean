"""
Compliance rules and safety configurations for ad copy generation.

This module contains banned words lists, compliance mode settings, and validation
rules to ensure generated ad copy meets platform guidelines and legal requirements.
"""

from typing import Dict, List, Set, Any
from enum import Enum
import re

class ComplianceMode(str, Enum):
    """Compliance modes for different industry requirements"""
    STANDARD = "standard"                # General advertising best practices
    HEALTHCARE_SAFE = "healthcare_safe"  # Medical/health industry compliance
    FINANCE_SAFE = "finance_safe"        # Financial services compliance
    LEGAL_SAFE = "legal_safe"           # Legal services compliance
    SUPPLEMENT_SAFE = "supplement_safe"  # Dietary supplement compliance

class ComplianceSeverity(str, Enum):
    """Severity levels for compliance violations"""
    INFO = "info"        # Informational, suggestions
    WARNING = "warning"  # Should be addressed
    ERROR = "error"      # Must be fixed
    CRITICAL = "critical" # Will cause rejection

# Spam trigger words and phrases that harm deliverability
SPAM_TRIGGER_WORDS: Set[str] = {
    # Excessive urgency words
    "act now", "urgent", "hurry", "limited time", "expires soon", "don't wait",
    "immediate", "instant", "right now", "today only", "last chance",
    
    # Money-related spam triggers
    "make money fast", "get rich quick", "easy money", "cash fast",
    "make $$$", "work from home", "financial freedom", "passive income",
    
    # Exaggerated claims
    "guaranteed", "miracle", "amazing", "incredible", "unbelievable",
    "revolutionary", "breakthrough", "secret", "hidden", "exclusive",
    
    # Clickbait phrases
    "you won't believe", "shocking", "this one trick", "doctors hate",
    "click here", "click now", "learn this secret", "find out how",
    
    # All-caps aggressive words
    "free", "buy now", "order now", "call now", "limited offer",
    "special offer", "act fast", "don't miss out"
}

# Excessive punctuation patterns
EXCESSIVE_PUNCTUATION_PATTERNS: List[str] = [
    r'[!]{2,}',      # Multiple exclamation marks
    r'[\?]{2,}',     # Multiple question marks
    r'[\.]{3,}',     # Multiple periods (more than ellipsis)
    r'[!]{1}[\?]{1}[!]{1}',  # Mixed punctuation
    r'[A-Z\s]{5,}[!]{1,}',   # All caps followed by exclamation
]

# Healthcare-specific banned words and phrases
HEALTHCARE_BANNED_TERMS: Set[str] = {
    "cure", "heal", "treat", "diagnosis", "medicine", "drug", "therapy",
    "medical advice", "doctor approved", "clinically proven", "fda approved",
    "guaranteed results", "miracle cure", "instant relief", "pain free",
    "eliminate", "destroy", "kill", "prevent disease", "boost immunity",
    "detox", "cleanse", "purify", "anti-aging", "fountain of youth"
}

# Finance-specific banned words and phrases
FINANCE_BANNED_TERMS: Set[str] = {
    "guaranteed returns", "risk-free", "no risk", "guaranteed profit",
    "get rich quick", "easy money", "passive income", "financial freedom",
    "investment advice", "insider information", "hot tip", "sure thing",
    "double your money", "overnight success", "foolproof", "can't lose",
    "tax loophole", "secret strategy", "beat the market", "guaranteed income"
}

# Legal-specific banned words and phrases
LEGAL_BANNED_TERMS: Set[str] = {
    "guaranteed win", "we will win", "assured victory", "best lawyer",
    "never lose", "always win", "guaranteed settlement", "easy money",
    "quick settlement", "maximum compensation", "no fee guarantee",
    "sue anyone", "lawsuit guaranteed", "instant lawsuit", "easy case"
}

# Supplement-specific banned words and phrases
SUPPLEMENT_BANNED_TERMS: Set[str] = {
    "fda approved", "scientifically proven", "clinical studies show",
    "doctor recommended", "medical breakthrough", "miracle supplement",
    "cure", "treat", "prevent", "diagnosis", "disease", "illness",
    "guaranteed results", "instant results", "lose weight fast",
    "burn fat instantly", "muscle building", "testosterone booster"
}

# Platform-specific compliance rules
PLATFORM_COMPLIANCE_RULES: Dict[str, Dict[str, Any]] = {
    "facebook": {
        "max_caps_percentage": 0.2,  # Max 20% capital letters
        "banned_before_after": True,  # No before/after claims
        "requires_landing_page": True,
        "adult_content_restrictions": True,
        "political_disclaimer_required": False
    },
    "google": {
        "max_caps_percentage": 0.15,
        "trademark_restrictions": True,
        "requires_business_verification": True,
        "adult_content_restrictions": True,
        "gambling_restrictions": True
    },
    "linkedin": {
        "professional_language_required": True,
        "no_personal_attacks": True,
        "business_content_only": True,
        "max_caps_percentage": 0.1
    },
    "tiktok": {
        "community_guidelines_strict": True,
        "age_appropriate_content": True,
        "music_copyright_aware": True,
        "trend_appropriate": True
    },
    "instagram": {
        "hashtag_compliance": True,
        "influencer_disclosure": True,
        "visual_content_focus": True,
        "story_vs_feed_rules": True
    },
    "twitter": {
        "character_limit_strict": True,
        "trending_topic_appropriate": True,
        "no_harassment_policy": True,
        "link_safety_check": True
    }
}

# Compliance mode configurations
COMPLIANCE_MODE_CONFIG: Dict[ComplianceMode, Dict[str, Any]] = {
    ComplianceMode.STANDARD: {
        "banned_terms": SPAM_TRIGGER_WORDS,
        "max_caps_percentage": 0.2,
        "min_readability_score": 60,
        "allow_strong_claims": True,
        "require_disclaimers": False,
        "severity_multiplier": 1.0
    },
    ComplianceMode.HEALTHCARE_SAFE: {
        "banned_terms": SPAM_TRIGGER_WORDS.union(HEALTHCARE_BANNED_TERMS),
        "max_caps_percentage": 0.1,
        "min_readability_score": 70,
        "allow_strong_claims": False,
        "require_disclaimers": True,
        "severity_multiplier": 2.0,
        "required_disclaimers": [
            "This statement has not been evaluated by the FDA",
            "Consult your healthcare provider",
            "Individual results may vary"
        ]
    },
    ComplianceMode.FINANCE_SAFE: {
        "banned_terms": SPAM_TRIGGER_WORDS.union(FINANCE_BANNED_TERMS),
        "max_caps_percentage": 0.05,
        "min_readability_score": 65,
        "allow_strong_claims": False,
        "require_disclaimers": True,
        "severity_multiplier": 2.5,
        "required_disclaimers": [
            "Past performance does not guarantee future results",
            "All investments carry risk",
            "Consult a financial advisor"
        ]
    },
    ComplianceMode.LEGAL_SAFE: {
        "banned_terms": SPAM_TRIGGER_WORDS.union(LEGAL_BANNED_TERMS),
        "max_caps_percentage": 0.05,
        "min_readability_score": 65,
        "allow_strong_claims": False,
        "require_disclaimers": True,
        "severity_multiplier": 2.5,
        "required_disclaimers": [
            "No attorney-client relationship is formed",
            "Past results do not guarantee future outcomes",
            "Each case is unique"
        ]
    },
    ComplianceMode.SUPPLEMENT_SAFE: {
        "banned_terms": SPAM_TRIGGER_WORDS.union(SUPPLEMENT_BANNED_TERMS),
        "max_caps_percentage": 0.1,
        "min_readability_score": 70,
        "allow_strong_claims": False,
        "require_disclaimers": True,
        "severity_multiplier": 2.0,
        "required_disclaimers": [
            "This product is not intended to diagnose, treat, cure, or prevent any disease",
            "Individual results may vary",
            "Consult your healthcare provider before use"
        ]
    }
}

# Readability score targets by audience
READABILITY_TARGETS: Dict[str, int] = {
    "general": 60,      # 8th-9th grade reading level
    "professional": 50,  # 10th-12th grade reading level  
    "academic": 40,     # College reading level
    "youth": 70,        # 7th grade reading level
    "international": 65 # Slightly higher for ESL audiences
}

# Compliance instructions for AI prompts
COMPLIANCE_INSTRUCTIONS: Dict[ComplianceMode, str] = {
    ComplianceMode.STANDARD: """
Follow general advertising best practices:
- Avoid excessive punctuation and all-caps spam words
- Keep claims realistic and verifiable
- Use clear, professional language
- Maintain ethical advertising standards
""",
    
    ComplianceMode.HEALTHCARE_SAFE: """
STRICT HEALTHCARE COMPLIANCE REQUIRED:
- Never use words like "cure," "heal," "treat," or "prevent"
- Avoid any medical claims or promises of health outcomes
- Do not suggest the product can diagnose, treat, or cure diseases
- Keep language general and focus on lifestyle benefits
- Always suggest consulting healthcare providers
- Use phrases like "may support," "intended to help," or "designed for"
""",
    
    ComplianceMode.FINANCE_SAFE: """
STRICT FINANCIAL COMPLIANCE REQUIRED:
- Never guarantee returns, profits, or financial outcomes
- Avoid terms like "risk-free," "guaranteed," or "sure thing"
- Do not promise specific monetary amounts or percentages
- Focus on service benefits rather than investment returns
- Always include appropriate risk disclosures in tone
- Use phrases like "may help," "designed to support," or "intended to assist"
""",
    
    ComplianceMode.LEGAL_SAFE: """
STRICT LEGAL COMPLIANCE REQUIRED:
- Never guarantee case outcomes or legal victories
- Avoid superlatives like "best lawyer" or "never lose"
- Do not promise specific settlements or compensation amounts
- Focus on experience and service quality
- Make clear no attorney-client relationship is formed by the ad
- Use phrases like "experienced in," "dedicated to," or "committed to helping"
""",
    
    ComplianceMode.SUPPLEMENT_SAFE: """
STRICT SUPPLEMENT COMPLIANCE REQUIRED:
- Never claim to diagnose, treat, cure, or prevent diseases
- Avoid FDA approval claims unless specifically approved
- Do not make specific health outcome promises
- Focus on general wellness and lifestyle support
- Keep all claims general and non-medical
- Use phrases like "supports wellness," "promotes," or "helps maintain"
"""
}

def get_compliance_config(mode: ComplianceMode) -> Dict[str, Any]:
    """Get compliance configuration for a specific mode."""
    return COMPLIANCE_MODE_CONFIG.get(mode, COMPLIANCE_MODE_CONFIG[ComplianceMode.STANDARD])

def get_compliance_instructions(mode: ComplianceMode) -> str:
    """Get compliance instructions for AI prompt generation."""
    return COMPLIANCE_INSTRUCTIONS.get(mode, COMPLIANCE_INSTRUCTIONS[ComplianceMode.STANDARD])

def get_platform_rules(platform: str) -> Dict[str, Any]:
    """Get platform-specific compliance rules."""
    return PLATFORM_COMPLIANCE_RULES.get(platform, {})

def is_banned_term(text: str, mode: ComplianceMode = ComplianceMode.STANDARD) -> bool:
    """Check if text contains any banned terms for the given compliance mode."""
    config = get_compliance_config(mode)
    banned_terms = config.get("banned_terms", set())
    
    text_lower = text.lower()
    return any(term in text_lower for term in banned_terms)

def check_excessive_punctuation(text: str) -> List[str]:
    """Check for excessive punctuation patterns."""
    violations = []
    for pattern in EXCESSIVE_PUNCTUATION_PATTERNS:
        if re.search(pattern, text):
            violations.append(f"Excessive punctuation pattern found: {pattern}")
    return violations

def calculate_caps_percentage(text: str) -> float:
    """Calculate percentage of capital letters in text."""
    if not text:
        return 0.0
    
    letters = [c for c in text if c.isalpha()]
    if not letters:
        return 0.0
        
    caps_count = sum(1 for c in letters if c.isupper())
    return caps_count / len(letters)