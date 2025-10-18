# backend/app/constants/platform_limits.py

from enum import Enum

class Platform(str, Enum):
    FACEBOOK = "facebook"
    INSTAGRAM = "instagram"
    GOOGLE = "google"
    LINKEDIN = "linkedin"
    TWITTER = "twitter"
    TIKTOK = "tiktok"

class EmojiLevel(str, Enum):
    NONE = "none"
    LIGHT = "light"
    MODERATE = "moderate"
    HEAVY = "heavy"

class HumanTone(str, Enum):
    PROFESSIONAL = "professional"
    CONVERSATIONAL = "conversational"
    CASUAL = "casual"
    FRIENDLY = "friendly"
    AUTHORITATIVE = "authoritative"

# Platform character limits
PLATFORM_LIMITS = {
    Platform.FACEBOOK: 2200,
    Platform.INSTAGRAM: 2200,
    Platform.GOOGLE: 90,
    Platform.LINKEDIN: 3000,
    Platform.TWITTER: 280,
    Platform.TIKTOK: 2200
}

# Extended platform configuration
PLATFORM_CONFIG = {
    Platform.FACEBOOK: {
        "formality_level": 6,
        "emoji_default": EmojiLevel.MODERATE,
        "recommended_tone": HumanTone.CONVERSATIONAL,
        "audience_mindset": "Social, engaged users",
        "typical_cta": ["Learn More", "Sign Up", "Get Started"],
        "optimization_tips": [
            "Use engaging visuals",
            "Ask questions to drive engagement",
            "Include social proof"
        ]
    },
    Platform.INSTAGRAM: {
        "formality_level": 4,
        "emoji_default": EmojiLevel.HEAVY,
        "recommended_tone": HumanTone.CASUAL,
        "audience_mindset": "Visual, lifestyle-focused users",
        "typical_cta": ["Shop Now", "Discover More", "Swipe Up"],
        "optimization_tips": [
            "Use high-quality visuals",
            "Include relevant hashtags",
            "Tell a story"
        ]
    },
    Platform.GOOGLE: {
        "formality_level": 8,
        "emoji_default": EmojiLevel.NONE,
        "recommended_tone": HumanTone.PROFESSIONAL,
        "audience_mindset": "Intent-driven searchers",
        "typical_cta": ["Learn More", "Get Quote", "Contact Us"],
        "optimization_tips": [
            "Include keywords",
            "Be specific and direct",
            "Highlight unique value"
        ]
    },
    Platform.LINKEDIN: {
        "formality_level": 9,
        "emoji_default": EmojiLevel.LIGHT,
        "recommended_tone": HumanTone.PROFESSIONAL,
        "audience_mindset": "Professional, business-focused users",
        "typical_cta": ["Learn More", "Download", "Contact Sales"],
        "optimization_tips": [
            "Focus on business value",
            "Use industry terminology",
            "Include credentials"
        ]
    },
    Platform.TWITTER: {
        "formality_level": 3,
        "emoji_default": EmojiLevel.MODERATE,
        "recommended_tone": HumanTone.CASUAL,
        "audience_mindset": "News-focused, trend-aware users",
        "typical_cta": ["Check it out", "Join the conversation", "RT if you agree"],
        "optimization_tips": [
            "Be concise and punchy",
            "Use trending hashtags",
            "Engage with replies"
        ]
    },
    Platform.TIKTOK: {
        "formality_level": 2,
        "emoji_default": EmojiLevel.HEAVY,
        "recommended_tone": HumanTone.CASUAL,
        "audience_mindset": "Entertainment-focused, younger users",
        "typical_cta": ["Try it", "Follow for more", "Duet this"],
        "optimization_tips": [
            "Be authentic and fun",
            "Use trending sounds",
            "Keep it short and snappy"
        ]
    }
}

def get_platform_limit(platform: str) -> int:
    """Get character limit for a platform"""
    return PLATFORM_LIMITS.get(platform, 2200)

def get_platform_config(platform: str) -> dict:
    """Get configuration for a platform"""
    return PLATFORM_CONFIG.get(platform, PLATFORM_CONFIG[Platform.FACEBOOK])

def get_content_length_info(platform: str) -> dict:
    """Get content length information for a platform"""
    limit = get_platform_limit(platform)
    return {
        "character_limit": limit,
        "recommended_length": int(limit * 0.8),
        "minimum_length": 10
    }

def get_ai_parameters(tone: HumanTone) -> dict:
    """Get AI parameters for a specific tone"""
    parameters = {
        HumanTone.PROFESSIONAL: {"temperature": 0.3, "creativity": 0.2},
        HumanTone.CONVERSATIONAL: {"temperature": 0.7, "creativity": 0.6},
        HumanTone.CASUAL: {"temperature": 0.8, "creativity": 0.8},
        HumanTone.FRIENDLY: {"temperature": 0.6, "creativity": 0.7},
        HumanTone.AUTHORITATIVE: {"temperature": 0.4, "creativity": 0.3}
    }
    return parameters.get(tone, parameters[HumanTone.CONVERSATIONAL])

def get_emoji_guideline(level: EmojiLevel) -> str:
    """Get emoji usage guideline for a specific level"""
    guidelines = {
        EmojiLevel.NONE: "No emojis - keep copy text-only",
        EmojiLevel.LIGHT: "1-2 emojis maximum, use sparingly",
        EmojiLevel.MODERATE: "3-5 emojis, balance text and visual elements",
        EmojiLevel.HEAVY: "6+ emojis welcome, make it visually engaging"
    }
    return guidelines.get(level, guidelines[EmojiLevel.MODERATE])

def get_tone_instruction(tone: HumanTone) -> str:
    """Get tone instruction for AI generation"""
    instructions = {
        HumanTone.PROFESSIONAL: "Use formal language, focus on expertise and credibility",
        HumanTone.CONVERSATIONAL: "Write like you're talking to a friend, warm but informative",
        HumanTone.CASUAL: "Keep it relaxed and approachable, use everyday language",
        HumanTone.FRIENDLY: "Be welcoming and personable, show genuine interest",
        HumanTone.AUTHORITATIVE: "Demonstrate expertise and confidence, be direct and decisive"
    }
    return instructions.get(tone, instructions[HumanTone.CONVERSATIONAL])

PLATFORM_CONFIGS = {
    Platform.FACEBOOK: {
        "fields": {
            "headline": {"max_length": 60, "required": True},
            "body": {"max_length": 125, "required": True},
            "cta": {"required": True, "max_words": 5},
        },
        "tone": "persuasive, friendly",
        "example_output": {
            "headline": "Save 50% on everything today only",
            "body": "Huge savings on our entire collection for 24 hours. Limited stock available.",
            "cta": "Shop the Sale"
        }
    },
    Platform.INSTAGRAM: {
        "fields": {
            "headline": {"max_length": 80, "required": False},
            "body": {"max_length": 150, "required": True},
            "cta": {"required": False}
        },
        "tone": "conversational, lifestyle",
        "example_output": {
            "headline": "Your dream look is one click away ✨",
            "body": "Explore new styles that match your vibe — shop the trend today.",
            "cta": "Discover Now"
        }
    },
    Platform.GOOGLE: {
        "fields": {
            "headline": {"max_length": 30, "required": True},
            "body": {"max_length": 90, "required": True},
            "cta": {"required": True}
        },
        "tone": "direct, clear, informative",
        "example_output": {
            "headline": "Affordable Hosting for Businesses",
            "body": "Get fast, reliable hosting with 24/7 support. Try free for 7 days!",
            "cta": "Start Free Trial"
        }
    },
    Platform.LINKEDIN: {
        "fields": {
            "headline": {"max_length": 70, "required": True},
            "body": {"max_length": 150, "required": True},
            "cta": {"required": True}
        },
        "tone": "professional, insightful",
        "example_output": {
            "headline": "Grow Your Career with Certified Training",
            "body": "Learn in-demand skills from industry experts and boost your resume today.",
            "cta": "Enroll Now"
        }
    },
    Platform.TWITTER: {
        "fields": {
            "headline": {"max_length": 280, "required": True},
            "body": {"max_length": 0, "required": False},
            "cta": {"required": False}
        },
        "tone": "short, punchy, witty",
        "example_output": {
            "headline": "50% off everything. Today only. ⏰",
            "body": "",
            "cta": "Shop Now"
        }
    },
    Platform.TIKTOK: {
        "fields": {
            "headline": {"max_length": 100, "required": False},
            "body": {"max_length": 150, "required": True},
            "cta": {"required": False}
        },
        "tone": "fun, trendy, energetic",
        "example_output": {
            "headline": "New drops just landed 🔥",
            "body": "Don't miss out on what's trending — tap the link now!",
            "cta": "Check it Out"
        }
    },
}
