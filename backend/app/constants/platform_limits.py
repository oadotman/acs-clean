"""
Platform-specific constraints and configuration for ad copy generation.

This module centralizes character limits, tone preferences, and platform-specific
settings for optimal ad copy generation across different social media platforms.
"""

from typing import Dict, Any, List, Tuple
from enum import Enum
from .creative_controls import (
    CreativityLevel, UrgencyLevel, EmotionType,
    get_creativity_parameters, get_emotion_config,
    PLATFORM_CREATIVITY_GUIDELINES
)

class EmojiLevel(str, Enum):
    """Emoji usage levels for ad copy generation"""
    MINIMAL = "minimal"      # 1-2 emojis max
    MODERATE = "moderate"    # 3-5 emojis
    EXPRESSIVE = "expressive"  # Liberal use of emojis

class HumanTone(str, Enum):
    """Human tone levels for ad copy generation"""
    BALANCED = "balanced"              # Natural but professional
    CONVERSATIONAL = "conversational" # Like talking to a friend  
    DEEPLY_EMOTIONAL = "deeply_emotional"  # Evocative, connects on feelings

class Platform(str, Enum):
    """Supported advertising platforms"""
    FACEBOOK = "facebook"
    INSTAGRAM = "instagram"
    LINKEDIN = "linkedin"
    TWITTER = "twitter"
    TIKTOK = "tiktok"
    GOOGLE = "google"

class BrandTone(str, Enum):
    """Brand tone options for ad copy generation"""
    PROFESSIONAL = "professional"      # B2B, corporate
    CASUAL = "casual"                  # Friendly brands, lifestyle
    PLAYFUL = "playful"                # Youth brands, entertainment
    URGENT = "urgent"                  # Sales, limited offers
    LUXURY = "luxury"                  # High-end, aspirational

class CTAStyle(str, Enum):
    """Call-to-action style levels"""
    SOFT = "soft"        # Learn more, Discover
    MEDIUM = "medium"    # Get started, Try it now
    HARD = "hard"        # Buy now, Limited spots - claim yours

# Detailed character limits for each platform component
PLATFORM_LIMITS_DETAILED: Dict[str, Dict[str, Dict[str, int]]] = {
    Platform.FACEBOOK: {
        "primary_text": {"optimal": 125, "max": 500},
        "headline": {"optimal": 27, "max": 40},
        "description": {"optimal": 30, "max": 30},
    },
    Platform.INSTAGRAM: {
        "caption": {"optimal": 125, "max": 2200},  # 125 visible before "more"
    },
    Platform.GOOGLE: {
        "headline": {"optimal": 30, "max": 30},  # 3 headlines
        "description": {"optimal": 90, "max": 90},  # 2 descriptions
    },
    Platform.LINKEDIN: {
        "intro_text": {"optimal": 150, "max": 3000},  # 150 optimal for feed display
    },
    Platform.TWITTER: {
        "tweet": {"optimal": 280, "max": 280},
    },
    Platform.TIKTOK: {
        "caption": {"optimal": 150, "max": 2200},  # 150 optimal, but much shorter works better
    },
}

# Simple character limits for backwards compatibility
PLATFORM_LIMITS: Dict[str, int] = {
    Platform.FACEBOOK: 125,     # Primary text optimal
    Platform.INSTAGRAM: 125,    # Visible caption before "more"
    Platform.LINKEDIN: 150,     # Feed display optimal
    Platform.TWITTER: 280,      # Platform maximum
    Platform.TIKTOK: 150,       # Optimal length
    Platform.GOOGLE: 90,        # Google Ads description
}

# Platform-specific metadata and recommendations
PLATFORM_CONFIG: Dict[str, Dict[str, Any]] = {
    Platform.FACEBOOK: {
        "recommended_tone": HumanTone.CONVERSATIONAL,
        "emoji_default": EmojiLevel.MODERATE,
        "formality_level": 5,  # 1-10 scale (1=very casual, 10=very formal)
        "typical_cta": ["Learn More", "Shop Now", "Sign Up"],
        "audience_mindset": "Social browsing, quick engagement",
        "optimization_tips": [
            "Use clear, benefit-focused headlines",
            "Include social proof when possible",
            "Keep it scannable with short paragraphs",
            "Use questions to create curiosity gaps",
            "Strategic emoji placement enhances engagement"
        ],
        "platform_warnings": [
            "Avoid 'Click here' or similar CTAs that violate Meta policies",
            "Don't use excessive capitalization or special characters",
            "Avoid making exaggerated health/financial claims"
        ],
        "power_words": ["Discover", "Proven", "Exclusive", "Transform", "Revolutionary"],
        # Phase 4 & 5: Creative controls
        "recommended_creativity": 6,  # Balanced creative
        "max_safe_creativity": 8,
        "recommended_urgency": 5,
        "max_safe_urgency": 8,
        "preferred_emotions": [EmotionType.TRUST_BUILDING, EmotionType.PROBLEM_SOLVING, EmotionType.EXCITEMENT],
        "cliche_tolerance": "medium",  # low, medium, high
        "creative_approaches": ["storytelling", "emotional appeals", "social proof"],
        "creative_avoid": ["overly corporate", "too experimental", "complex concepts"]
    },
    Platform.INSTAGRAM: {
        "recommended_tone": HumanTone.CONVERSATIONAL,
        "emoji_default": EmojiLevel.EXPRESSIVE,
        "formality_level": 3,
        "typical_cta": ["Link in Bio", "Swipe Up", "DM Us"],
        "audience_mindset": "Visual-first, lifestyle focused",
        "optimization_tips": [
            "Be authentic and relatable",
            "Use storytelling approach",
            "Hashtag strategy is crucial",
            "First 125 chars visible - front-load key message",
            "Use line breaks for readability"
        ],
        "platform_warnings": [
            "Avoid overly promotional language - native feel is key",
            "Don't use banned hashtags or spam hashtags",
            "Excessive emojis can look spammy despite platform culture"
        ],
        "power_words": ["Authentic", "Lifestyle", "Community", "Inspiration", "Journey"],
        # Phase 4 & 5: Creative controls
        "recommended_creativity": 7,  # Creative
        "max_safe_creativity": 9,
        "recommended_urgency": 4,
        "max_safe_urgency": 7,
        "preferred_emotions": [EmotionType.ASPIRATIONAL, EmotionType.EXCITEMENT, EmotionType.INSPIRING],
        "cliche_tolerance": "low",  # Instagram users expect fresh content
        "creative_approaches": ["visual metaphors", "lifestyle appeals", "trendy language", "authentic storytelling"],
        "creative_avoid": ["text-heavy approaches", "boring corporate speak", "generic stock phrases"]
    },
    Platform.LINKEDIN: {
        "recommended_tone": HumanTone.BALANCED,
        "emoji_default": EmojiLevel.MINIMAL,
        "formality_level": 7,
        "typical_cta": ["Learn More", "Download", "Connect"],
        "audience_mindset": "Professional networking, business focus",
        "optimization_tips": [
            "Lead with business value and ROI",
            "Use industry-specific language and terminology",
            "Include credibility indicators and data/statistics",
            "First 150 chars are crucial for feed visibility",
            "Professional authority and thought leadership angle"
        ],
        "platform_warnings": [
            "Avoid overly casual language or slang",
            "Don't use aggressive sales tactics",
            "Excessive emojis hurt professional credibility"
        ],
        "power_words": ["Professional", "ROI", "Strategy", "Insights", "Industry-Leading"],
        # Phase 4 & 5: Creative controls
        "recommended_creativity": 4,  # Balanced conservative
        "max_safe_creativity": 6,
        "recommended_urgency": 3,
        "max_safe_urgency": 6,
        "preferred_emotions": [EmotionType.TRUST_BUILDING, EmotionType.CONFIDENCE, EmotionType.PROBLEM_SOLVING],
        "cliche_tolerance": "high",  # Business audience more tolerant of established phrases
        "creative_approaches": ["professional insights", "industry trends", "thought leadership", "data-driven appeals"],
        "creative_avoid": ["casual language", "overly creative angles", "entertainment focus", "excessive urgency"]
    },
    Platform.TWITTER: {
        "recommended_tone": HumanTone.CONVERSATIONAL,
        "emoji_default": EmojiLevel.MODERATE,
        "formality_level": 4,
        "typical_cta": ["Read more", "RT", "Reply"],
        "audience_mindset": "Quick consumption, real-time engagement",
        "optimization_tips": [
            "Be concise and punchy - every word counts",
            "Use trending topics/hashtags strategically",
            "Encourage engagement (replies, RTs)",
            "Thread potential for longer stories",
            "Conversational and shareable content performs best"
        ],
        "platform_warnings": [
            "Avoid hashtag spam (max 2-3 hashtags)",
            "Don't be overly promotional - native feel required",
            "Excessive emojis can look unprofessional"
        ],
        "power_words": ["Breaking", "Thread", "Quick", "Now", "Here's how"],
        # Phase 4 & 5: Creative controls
        "recommended_creativity": 7,  # Creative
        "max_safe_creativity": 9,
        "recommended_urgency": 6,
        "max_safe_urgency": 9,
        "preferred_emotions": [EmotionType.EXCITEMENT, EmotionType.CURIOSITY, EmotionType.FEAR_OF_MISSING_OUT],
        "cliche_tolerance": "low",  # Twitter users appreciate wit and originality
        "creative_approaches": ["witty one-liners", "trending topics", "conversational tone", "timely commentary"],
        "creative_avoid": ["long explanations", "formal language", "complex ideas", "outdated references"]
    },
    Platform.TIKTOK: {
        "recommended_tone": HumanTone.DEEPLY_EMOTIONAL,
        "emoji_default": EmojiLevel.EXPRESSIVE,
        "formality_level": 2,  # Very casual
        "typical_cta": ["Check comments", "Follow for more", "Try this"],
        "audience_mindset": "Entertainment-first, trend-aware",
        "optimization_tips": [
            "Use Gen Z language naturally (not forced)",
            "Focus on hooks that stop the scroll in first 3 seconds",
            "Be conversational and relatable, not promotional",
            "Embrace humor and authenticity over polish",
            "Trend-aware content and challenges perform best",
            "Educational or entertaining - pick one angle"
        ],
        "platform_warnings": [
            "Avoid corporate/professional language - instant skip",
            "Don't use hard sales tactics - native content only",
            "Overly polished content feels inauthentic",
            "Forced Gen Z slang is cringe - be natural"
        ],
        "power_words": ["POV", "How to", "This is your sign", "Wait for it", "Day in the life"],
        # Phase 4 & 5: Creative controls
        "recommended_creativity": 9,  # Bold
        "max_safe_creativity": 10,
        "recommended_urgency": 3,  # TikTok doesn't respond well to high urgency
        "max_safe_urgency": 6,
        "preferred_emotions": [EmotionType.EXCITEMENT, EmotionType.INSPIRING, EmotionType.CURIOSITY],
        "cliche_tolerance": "very_low",  # TikTok demands authentic, fresh content
        "creative_approaches": ["trend-jacking", "humor", "authentic voice", "bold statements", "storytelling hooks"],
        "creative_avoid": ["corporate speak", "overly polished", "traditional approaches", "heavy sales pitches"]
    },
    Platform.GOOGLE: {
        "recommended_tone": HumanTone.BALANCED,
        "emoji_default": EmojiLevel.MINIMAL,
        "formality_level": 6,
        "typical_cta": ["Get Started", "Free Trial", "Buy Now"],
        "audience_mindset": "Intent-driven, solution seeking",
        "optimization_tips": [
            "Lead with clear value proposition",
            "Include compelling offer/benefit in headline",
            "Use action-oriented language",
            "Include price/offer when possible",
            "Use specific numbers and results",
            "Match search intent with keyword integration"
        ],
        "platform_warnings": [
            "No emojis in Google Ads - they're not displayed",
            "Avoid excessive punctuation (!!!)",
            "Don't violate Google Ads policies on superlatives without proof"
        ],
        "power_words": ["Save", "Free", "Results", "Guaranteed", "Official"],
        # Phase 4 & 5: Creative controls
        "recommended_creativity": 5,  # Balanced
        "max_safe_creativity": 7,
        "recommended_urgency": 7,  # Google Ads can handle higher urgency
        "max_safe_urgency": 9,
        "preferred_emotions": [EmotionType.PROBLEM_SOLVING, EmotionType.TRUST_BUILDING, EmotionType.URGENT],
        "cliche_tolerance": "medium",  # Google users focused on solutions, less sensitive to clichés
        "creative_approaches": ["clear value props", "benefit-focused", "solution-oriented", "results-driven"],
        "creative_avoid": ["abstract concepts", "unclear messaging", "overly artistic language", "vague benefits"]
    }
}

# AI Generation parameter mapping based on human tone
HUMAN_TONE_PARAMS: Dict[HumanTone, Dict[str, float]] = {
    HumanTone.BALANCED: {
        "temperature": 0.7,
        "presence_penalty": 0.2,
        "frequency_penalty": 0.3
    },
    HumanTone.CONVERSATIONAL: {
        "temperature": 0.8,
        "presence_penalty": 0.4,
        "frequency_penalty": 0.4
    },
    HumanTone.DEEPLY_EMOTIONAL: {
        "temperature": 0.9,
        "presence_penalty": 0.6,
        "frequency_penalty": 0.5
    }
}

# Emoji usage guidelines for prompt generation
EMOJI_GUIDELINES: Dict[EmojiLevel, str] = {
    EmojiLevel.MINIMAL: "Use 1-2 emojis maximum, only when they genuinely enhance meaning. Prefer professional, universally understood emojis.",
    EmojiLevel.MODERATE: "Use 3-5 emojis strategically to enhance emotional connection and readability. Balance professionalism with personality.",
    EmojiLevel.EXPRESSIVE: "Use emojis liberally to create emotional resonance and visual appeal. Embrace platform culture while maintaining brand appropriateness."
}

# Human tone instructions for prompt generation
HUMAN_TONE_INSTRUCTIONS: Dict[HumanTone, str] = {
    HumanTone.BALANCED: """Write in a natural, professional tone that feels authentic. Use clear, direct language that builds trust. Avoid corporate jargon while maintaining credibility.""",
    
    HumanTone.CONVERSATIONAL: """Write as if speaking directly to a friend - warm, approachable, and genuine. Use contractions (you're, we'll, don't), varied sentence lengths, and rhetorical questions. Inject personality while staying relatable.""",
    
    HumanTone.DEEPLY_EMOTIONAL: """Create deep emotional resonance through vivid imagery, sensory language, and powerful storytelling. Connect with core human emotions like aspiration, fear, desire, or frustration. Use language that moves people to feel, not just think."""
}

# Brand tone guidelines for prompt generation
BRAND_TONE_GUIDELINES: Dict[BrandTone, str] = {
    BrandTone.PROFESSIONAL: """Maintain a professional, authoritative tone suitable for B2B and corporate audiences. Use industry-appropriate terminology, emphasize credibility and expertise, and focus on business value and ROI. Avoid overly casual language or slang.""",
    
    BrandTone.CASUAL: """Adopt a friendly, approachable tone that feels like a conversation with a trusted friend. Use everyday language, relatable examples, and a warm, welcoming style. Perfect for lifestyle brands and consumer-focused companies.""",
    
    BrandTone.PLAYFUL: """Embrace creativity, humor, and energy. Use wordplay, pop culture references, and fun language that resonates with younger audiences. Be bold, memorable, and entertaining while maintaining brand appropriateness.""",
    
    BrandTone.URGENT: """Create immediate action with time-sensitive language, scarcity indicators, and compelling urgency. Use phrases like 'limited time,' 'act now,' 'don't miss out.' Focus on immediate benefits and consequences of waiting.""",
    
    BrandTone.LUXURY: """Convey sophistication, exclusivity, and premium quality. Use elevated language, emphasize craftsmanship and heritage, and appeal to aspirational desires. Avoid aggressive sales language in favor of elegant persuasion."""
}

# Formality level guidelines (0-10 scale)
FORMALITY_GUIDELINES: Dict[int, str] = {
    0: "Extremely casual - like texting a close friend. Use slang, abbreviations, and very informal language.",
    1: "Very casual - relaxed conversation style with contractions and informal expressions.",
    2: "Casual - friendly and approachable, using everyday language and personal pronouns.",
    3: "Relaxed - comfortable tone with some casual elements but maintaining clarity.",
    4: "Conversational - natural speaking style that's approachable yet clear.",
    5: "Balanced - neutral tone that works for most audiences, neither too formal nor casual.",
    6: "Semi-formal - professional but warm, appropriate for most business communications.",
    7: "Professional - business-appropriate language with proper grammar and structure.",
    8: "Formal - corporate tone suitable for official communications and serious subjects.",
    9: "Very formal - highly structured, precise language appropriate for legal or academic contexts.",
    10: "Extremely formal - maximum formality for the most serious or prestigious communications."
}

# CTA style examples
CTA_STYLE_EXAMPLES: Dict[CTAStyle, List[str]] = {
    CTAStyle.SOFT: [
        "Learn More", "Discover", "Explore", "Find Out", "See How", "Get Inspired", "Take a Look"
    ],
    CTAStyle.MEDIUM: [
        "Get Started", "Try It Now", "Join Us", "Sign Up", "Start Free", "Begin Today", "Take Action"
    ],
    CTAStyle.HARD: [
        "Buy Now", "Order Today", "Claim Yours", "Limited Spots - Act Fast", "Don't Miss Out", "Secure Your Spot", "Get Yours Before It's Gone"
    ]
}

def get_platform_limit(platform: str) -> int:
    """Get character limit for a specific platform (simple version)."""
    return PLATFORM_LIMITS.get(platform, 125)  # Default to Facebook limit

def get_platform_limits_detailed(platform: str) -> Dict[str, Dict[str, int]]:
    """Get detailed character limits for all components of a platform.
    
    Returns:
        Dict with keys like 'primary_text', 'headline', 'description' containing
        'optimal' and 'max' values for each component.
    """
    return PLATFORM_LIMITS_DETAILED.get(platform, PLATFORM_LIMITS_DETAILED[Platform.FACEBOOK])

def get_platform_warnings(platform: str) -> List[str]:
    """Get platform-specific warnings about what to avoid.
    
    Returns:
        List of warning strings (e.g., policy violations, best practices to avoid).
    """
    config = get_platform_config(platform)
    return config.get("platform_warnings", [])

def get_platform_power_words(platform: str) -> List[str]:
    """Get recommended power words that perform well on the platform.
    
    Returns:
        List of power words optimized for the platform's audience.
    """
    config = get_platform_config(platform)
    return config.get("power_words", [])

def get_platform_config(platform: str) -> Dict[str, Any]:
    """Get platform-specific configuration."""
    return PLATFORM_CONFIG.get(platform, PLATFORM_CONFIG[Platform.FACEBOOK])

def get_ai_parameters(human_tone: HumanTone) -> Dict[str, float]:
    """Get OpenAI/Gemini parameters for a specific human tone."""
    return HUMAN_TONE_PARAMS[human_tone]

def get_emoji_guideline(emoji_level: EmojiLevel) -> str:
    """Get emoji usage guideline for prompt generation."""
    return EMOJI_GUIDELINES[emoji_level]

def get_tone_instruction(human_tone: HumanTone) -> str:
    """Get human tone instruction for prompt generation."""
    return HUMAN_TONE_INSTRUCTIONS[human_tone]

def validate_content_length(content: str, platform: str) -> bool:
    """Validate if content length is within platform limits."""
    limit = get_platform_limit(platform)
    return len(content) <= limit

def get_content_length_info(platform: str) -> Dict[str, Any]:
    """Get comprehensive length information for a platform."""
    limit = get_platform_limit(platform)
    config = get_platform_config(platform)
    
    return {
        "character_limit": limit,
        "recommended_length": int(limit * 0.8),  # 80% of limit for safety
        "platform_name": platform.title(),
        "formality_level": config.get("formality_level", 5),
        "audience_mindset": config.get("audience_mindset", "General audience")
    }

def get_brand_tone_guideline(brand_tone: BrandTone) -> str:
    """Get brand tone guideline for prompt generation."""
    return BRAND_TONE_GUIDELINES[brand_tone]

def get_formality_guideline(formality_level: int) -> str:
    """Get formality guideline for a specific level (0-10)."""
    # Clamp formality level to valid range
    clamped_level = max(0, min(10, formality_level))
    return FORMALITY_GUIDELINES[clamped_level]

def get_cta_examples(cta_style: CTAStyle) -> List[str]:
    """Get example CTAs for a specific style."""
    return CTA_STYLE_EXAMPLES[cta_style]

def get_recommended_formality(platform: str, brand_tone: BrandTone) -> int:
    """Get recommended formality level based on platform and brand tone."""
    platform_config = get_platform_config(platform)
    base_formality = platform_config.get("formality_level", 5)
    
    # Adjust based on brand tone
    tone_adjustments = {
        BrandTone.PROFESSIONAL: +2,
        BrandTone.CASUAL: -1,
        BrandTone.PLAYFUL: -2,
        BrandTone.URGENT: 0,
        BrandTone.LUXURY: +3
    }
    
    adjustment = tone_adjustments.get(brand_tone, 0)
    recommended = base_formality + adjustment
    
    # Clamp to valid range
    return max(0, min(10, recommended))

def get_platform_tone_compatibility(platform: str) -> Dict[BrandTone, str]:
    """Get compatibility ratings for different tones on each platform."""
    compatibilities = {
        "facebook": {
            BrandTone.PROFESSIONAL: "Good",
            BrandTone.CASUAL: "Excellent",
            BrandTone.PLAYFUL: "Good",
            BrandTone.URGENT: "Excellent",
            BrandTone.LUXURY: "Good"
        },
        "instagram": {
            BrandTone.PROFESSIONAL: "Fair",
            BrandTone.CASUAL: "Excellent",
            BrandTone.PLAYFUL: "Excellent",
            BrandTone.URGENT: "Good",
            BrandTone.LUXURY: "Excellent"
        },
        "linkedin": {
            BrandTone.PROFESSIONAL: "Excellent",
            BrandTone.CASUAL: "Good",
            BrandTone.PLAYFUL: "Fair",
            BrandTone.URGENT: "Good",
            BrandTone.LUXURY: "Good"
        },
        "twitter": {
            BrandTone.PROFESSIONAL: "Good",
            BrandTone.CASUAL: "Excellent",
            BrandTone.PLAYFUL: "Excellent",
            BrandTone.URGENT: "Excellent",
            BrandTone.LUXURY: "Fair"
        },
        "tiktok": {
            BrandTone.PROFESSIONAL: "Poor",
            BrandTone.CASUAL: "Good",
            BrandTone.PLAYFUL: "Excellent",
            BrandTone.URGENT: "Fair",
            BrandTone.LUXURY: "Fair"
        },
        "google": {
            BrandTone.PROFESSIONAL: "Excellent",
            BrandTone.CASUAL: "Good",
            BrandTone.PLAYFUL: "Fair",
            BrandTone.URGENT: "Excellent",
            BrandTone.LUXURY: "Good"
        }
    }
    
    return compatibilities.get(platform, {
        tone: "Good" for tone in BrandTone
    })

# Phase 4 & 5: Creative Controls Helper Functions

def get_platform_creativity_config(platform: str) -> Dict[str, Any]:
    """Get creativity-specific configuration for a platform."""
    config = get_platform_config(platform)
    return {
        "recommended_creativity": config.get("recommended_creativity", 5),
        "max_safe_creativity": config.get("max_safe_creativity", 7),
        "recommended_urgency": config.get("recommended_urgency", 5),
        "max_safe_urgency": config.get("max_safe_urgency", 8),
        "preferred_emotions": config.get("preferred_emotions", [EmotionType.TRUST_BUILDING]),
        "cliche_tolerance": config.get("cliche_tolerance", "medium"),
        "creative_approaches": config.get("creative_approaches", []),
        "creative_avoid": config.get("creative_avoid", [])
    }

def get_optimal_creative_parameters(
    platform: str,
    creativity_level: int = None,
    urgency_level: int = None,
    emotion_type: EmotionType = None,
    human_tone: HumanTone = None
) -> Dict[str, Any]:
    """Get optimal creative parameters combining platform defaults with user preferences."""
    platform_config = get_platform_creativity_config(platform)
    base_config = get_platform_config(platform)
    
    # Use provided values or fall back to platform recommendations
    final_creativity = creativity_level if creativity_level is not None else platform_config["recommended_creativity"]
    final_urgency = urgency_level if urgency_level is not None else platform_config["recommended_urgency"]
    final_emotion = emotion_type if emotion_type is not None else platform_config["preferred_emotions"][0]
    final_tone = human_tone if human_tone is not None else base_config["recommended_tone"]
    
    # Get AI parameters from creativity level or human tone (creativity takes precedence)
    if creativity_level is not None:
        ai_params = dict(zip(["temperature", "presence_penalty", "frequency_penalty"], 
                           get_creativity_parameters(final_creativity)))
    else:
        ai_params = get_ai_parameters(final_tone)
    
    return {
        "creativity_level": final_creativity,
        "urgency_level": final_urgency,
        "emotion_type": final_emotion,
        "human_tone": final_tone,
        "ai_parameters": ai_params,
        "platform_warnings": _get_creative_warnings(platform, final_creativity, final_urgency, final_emotion)
    }

def _get_creative_warnings(platform: str, creativity: int, urgency: int, emotion: EmotionType) -> List[str]:
    """Get warnings if creative settings might not be optimal for platform."""
    warnings = []
    platform_config = get_platform_creativity_config(platform)
    
    if creativity > platform_config["max_safe_creativity"]:
        warnings.append(f"Creativity level {creativity} is higher than recommended maximum of {platform_config['max_safe_creativity']} for {platform}")
    
    if urgency > platform_config["max_safe_urgency"]:
        warnings.append(f"Urgency level {urgency} is higher than recommended maximum of {platform_config['max_safe_urgency']} for {platform}")
    
    # Emotion-specific warnings
    preferred_emotions = platform_config["preferred_emotions"]
    if emotion not in preferred_emotions:
        preferred_names = [e.value for e in preferred_emotions]
        warnings.append(f"Emotion '{emotion.value}' may not be optimal for {platform}. Consider: {', '.join(preferred_names)}")
    
    return warnings

def get_emotion_platform_compatibility(emotion_type: EmotionType) -> Dict[str, str]:
    """Get compatibility ratings for an emotion type across all platforms."""
    compatibility_matrix = {
        EmotionType.INSPIRING: {
            "facebook": "Excellent", "instagram": "Excellent", "linkedin": "Good",
            "twitter": "Good", "tiktok": "Excellent", "google": "Good"
        },
        EmotionType.URGENT: {
            "facebook": "Excellent", "instagram": "Good", "linkedin": "Fair",
            "twitter": "Excellent", "tiktok": "Fair", "google": "Excellent"
        },
        EmotionType.TRUST_BUILDING: {
            "facebook": "Excellent", "instagram": "Good", "linkedin": "Excellent",
            "twitter": "Good", "tiktok": "Poor", "google": "Excellent"
        },
        EmotionType.ASPIRATIONAL: {
            "facebook": "Good", "instagram": "Excellent", "linkedin": "Fair",
            "twitter": "Good", "tiktok": "Good", "google": "Good"
        },
        EmotionType.PROBLEM_SOLVING: {
            "facebook": "Excellent", "instagram": "Good", "linkedin": "Excellent",
            "twitter": "Good", "tiktok": "Fair", "google": "Excellent"
        },
        EmotionType.EXCITEMENT: {
            "facebook": "Excellent", "instagram": "Excellent", "linkedin": "Fair",
            "twitter": "Excellent", "tiktok": "Excellent", "google": "Good"
        },
        EmotionType.FEAR_OF_MISSING_OUT: {
            "facebook": "Good", "instagram": "Good", "linkedin": "Poor",
            "twitter": "Excellent", "tiktok": "Good", "google": "Good"
        },
        EmotionType.CURIOSITY: {
            "facebook": "Good", "instagram": "Excellent", "linkedin": "Fair",
            "twitter": "Excellent", "tiktok": "Excellent", "google": "Good"
        },
        EmotionType.CONFIDENCE: {
            "facebook": "Good", "instagram": "Good", "linkedin": "Excellent",
            "twitter": "Good", "tiktok": "Good", "google": "Good"
        },
        EmotionType.COMFORT: {
            "facebook": "Good", "instagram": "Good", "linkedin": "Good",
            "twitter": "Fair", "tiktok": "Fair", "google": "Good"
        }
    }
    
    return compatibility_matrix.get(emotion_type, {
        platform: "Good" for platform in ["facebook", "instagram", "linkedin", "twitter", "tiktok", "google"]
    })

def build_platform_creative_prompt(
    platform: str,
    creativity_level: int,
    urgency_level: int,
    emotion_type: EmotionType,
    filter_cliches: bool = True
) -> str:
    """Build platform-specific creative instructions for AI prompts."""
    platform_config = get_platform_creativity_config(platform)
    base_config = get_platform_config(platform)
    
    instructions = []
    
    # Platform context
    instructions.append(f"Platform: {platform.title()} - {base_config['audience_mindset']}")
    
    # Creative approach guidance
    approaches = platform_config["creative_approaches"]
    if approaches:
        instructions.append(f"Use these creative approaches: {', '.join(approaches)}")
    
    avoids = platform_config["creative_avoid"]
    if avoids:
        instructions.append(f"Avoid: {', '.join(avoids)}")
    
    # Import and use the creative instructions builder
    from .creative_controls import build_creative_instructions
    creative_instructions = build_creative_instructions(
        creativity_level, urgency_level, emotion_type, filter_cliches
    )
    instructions.append(creative_instructions)
    
    # Platform-specific cliché tolerance
    cliche_tolerance = platform_config["cliche_tolerance"]
    if cliche_tolerance == "very_low":
        instructions.append("Be extremely original - this platform heavily penalizes clichéd content.")
    elif cliche_tolerance == "low":
        instructions.append("Prioritize fresh, original language - avoid common marketing phrases.")
    elif cliche_tolerance == "high":
        instructions.append("Some established business phrases are acceptable, but still aim for freshness.")
    
    return " ".join(instructions)
