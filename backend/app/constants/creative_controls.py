"""
Creative excellence and advanced personalization constants for ad copy generation.

This module contains creativity levels, emotion types, urgency controls, and cliché
filtering configurations for Phase 4 & 5 of the ad copy generation system.
"""

from typing import Dict, List, Set, Any, Tuple
from enum import Enum

class CreativityLevel(int, Enum):
    """Creativity levels for ad copy generation (0-10 scale)"""
    ULTRA_SAFE = 0          # Extremely conservative, proven approaches only
    VERY_SAFE = 1           # Very safe, minimal risk
    SAFE = 2                # Safe, conventional approaches
    MOSTLY_SAFE = 3         # Mostly safe with slight variations
    BALANCED_CONSERVATIVE = 4  # Balanced but leaning conservative
    BALANCED = 5            # Perfect balance of safe and creative
    BALANCED_CREATIVE = 6   # Balanced but leaning creative
    CREATIVE = 7            # Creative with bold angles
    VERY_CREATIVE = 8       # Very creative and unconventional
    BOLD = 9                # Bold, risky, attention-grabbing
    EXPERIMENTAL = 10       # Experimental, maximum creativity

class UrgencyLevel(int, Enum):
    """Urgency levels for ad copy (0-10 scale)"""
    NO_PRESSURE = 0         # Completely relaxed, no urgency
    MINIMAL = 1             # Minimal urgency hints
    SUBTLE = 2              # Subtle encouragement
    GENTLE = 3              # Gentle nudging
    MODERATE_LOW = 4        # Moderate but still gentle
    BALANCED = 5            # Balanced urgency
    MODERATE_HIGH = 6       # Moderate with more pressure
    URGENT = 7              # Clear urgency indicators
    HIGH_URGENCY = 8        # High urgency with scarcity
    CRITICAL = 9            # Critical urgency, limited time
    MAXIMUM = 10            # Maximum urgency, immediate action required

class EmotionType(str, Enum):
    """Primary emotion types for ad copy"""
    INSPIRING = "inspiring"             # Motivational, uplifting, aspirational
    URGENT = "urgent"                   # Time-sensitive, scarcity-driven
    TRUST_BUILDING = "trust_building"   # Credible, reliable, professional
    ASPIRATIONAL = "aspirational"       # Luxury, lifestyle, status
    PROBLEM_SOLVING = "problem_solving" # Pain point focused, solution-oriented
    EXCITEMENT = "excitement"           # Energetic, enthusiastic, fun
    FEAR_OF_MISSING_OUT = "fomo"       # FOMO, social proof, popularity
    CURIOSITY = "curiosity"            # Intriguing, mysterious, discovery
    CONFIDENCE = "confidence"          # Empowering, self-assured, bold
    COMFORT = "comfort"                # Safe, familiar, reassuring

# Creativity level to OpenAI temperature mapping
CREATIVITY_TEMPERATURE_MAPPING: Dict[int, Tuple[float, float, float]] = {
    # creativity_level: (temperature, presence_penalty, frequency_penalty)
    0: (0.5, 0.0, 0.0),     # Ultra safe, very predictable
    1: (0.5, 0.1, 0.1),     # Very safe
    2: (0.55, 0.15, 0.15),  # Safe
    3: (0.6, 0.2, 0.2),     # Mostly safe
    4: (0.65, 0.25, 0.25),  # Balanced conservative
    5: (0.7, 0.3, 0.3),     # Balanced (default)
    6: (0.75, 0.35, 0.35),  # Balanced creative
    7: (0.8, 0.4, 0.4),     # Creative
    8: (0.85, 0.5, 0.45),   # Very creative
    9: (0.9, 0.6, 0.5),     # Bold
    10: (1.0, 0.7, 0.6),    # Experimental, maximum creativity
}

# Marketing clichés to filter out
MARKETING_CLICHES: Set[str] = {
    # Overused superlatives
    "game-changer", "next-level", "cutting-edge", "revolutionary", "world-class",
    "best-in-class", "paradigm shift", "industry-leading", "state-of-the-art",
    "groundbreaking", "innovative solution", "turnkey solution", "holistic approach",
    
    # Generic business phrases
    "synergistic", "leverage", "optimize", "streamline", "maximize", "utilize",
    "implement", "strategically", "proactively", "seamlessly", "efficiently",
    "effectively", "significantly", "substantially", "exponentially",
    
    # Overused marketing promises
    "transform your life", "change everything", "never seen before", "limited time offer",
    "act now", "don't miss out", "once in a lifetime", "exclusive opportunity",
    "secret revealed", "insider information", "hidden truth", "breakthrough discovery",
    
    # Worn-out descriptors
    "amazing results", "incredible value", "unbelievable deal", "fantastic opportunity",
    "outstanding performance", "exceptional quality", "premium experience",
    "ultimate solution", "perfect choice", "ideal option", "must-have",
    
    # Business jargon
    "low-hanging fruit", "move the needle", "circle back", "touch base", "deep dive",
    "drill down", "high-level overview", "at the end of the day", "bottom line",
    "win-win situation", "think outside the box", "push the envelope"
}

# Fresh alternatives for common clichés
CLICHE_ALTERNATIVES: Dict[str, List[str]] = {
    "game-changer": ["transforms how you work", "shifts your perspective", "changes your approach"],
    "next-level": ["elevated", "advanced", "sophisticated", "enhanced"],
    "cutting-edge": ["latest", "modern", "contemporary", "up-to-date"],
    "revolutionary": ["innovative", "fresh", "new", "different"],
    "world-class": ["excellent", "superior", "high-quality", "professional"],
    "best-in-class": ["top-tier", "leading", "premium", "exceptional"],
    "paradigm shift": ["new way of thinking", "fresh perspective", "different approach"],
    "industry-leading": ["top-performing", "highly-rated", "preferred by professionals"],
    "state-of-the-art": ["modern", "advanced", "current", "up-to-date"],
    "groundbreaking": ["innovative", "pioneering", "first-of-its-kind", "novel"],
    "amazing results": ["impressive outcomes", "notable improvements", "real progress"],
    "incredible value": ["great worth", "excellent return", "smart investment"],
    "unbelievable deal": ["exceptional offer", "rare opportunity", "valuable proposition"],
    "transform your life": ["improve your situation", "enhance your experience", "upgrade your routine"],
    "change everything": ["make a real difference", "create meaningful impact", "shift your results"]
}

# Urgency level instructions for AI prompts
URGENCY_INSTRUCTIONS: Dict[int, str] = {
    0: "Keep tone completely relaxed with no time pressure. Focus on benefits without any urgency.",
    1: "Use minimal urgency with very gentle encouragement. Avoid all pressure tactics.",
    2: "Include subtle suggestions to act, but maintain a relaxed, helpful tone.",
    3: "Gently encourage action with soft nudging language like 'when you're ready' or 'consider'.",
    4: "Use moderate encouragement with phrases like 'don't wait too long' or 'popular choice'.",
    5: "Balance urgency and comfort. Include some time-sensitive language but keep it reasonable.",
    6: "Increase urgency with phrases like 'limited availability' or 'while supplies last'.",
    7: "Create clear urgency with definite time limits and scarcity indicators.",
    8: "Use high urgency language with strong scarcity messaging and immediate action calls.",
    9: "Create critical urgency with countdown language and fear of missing out.",
    10: "Maximum urgency with immediate action required, 'now or never' messaging."
}

# Emotion type instructions and characteristics
EMOTION_TYPE_CONFIG: Dict[EmotionType, Dict[str, Any]] = {
    EmotionType.INSPIRING: {
        "description": "Motivational and uplifting content that inspires action",
        "keywords": ["achieve", "dream", "potential", "success", "growth", "transform", "elevate"],
        "tone": "uplifting and motivational",
        "approach": "Focus on possibilities, personal growth, and achievement",
        "avoid": ["negative language", "limitations", "problems without solutions"],
        "sample_phrases": ["unlock your potential", "achieve your dreams", "make it happen"]
    },
    
    EmotionType.URGENT: {
        "description": "Time-sensitive content that drives immediate action",
        "keywords": ["now", "limited", "ending soon", "last chance", "hurry", "today only"],
        "tone": "urgent and compelling",
        "approach": "Create time pressure and scarcity to motivate quick decisions",
        "avoid": ["relaxed language", "open-ended offers", "vague timelines"],
        "sample_phrases": ["limited time", "act fast", "don't miss out"]
    },
    
    EmotionType.TRUST_BUILDING: {
        "description": "Professional content that establishes credibility and reliability",
        "keywords": ["proven", "trusted", "reliable", "professional", "experienced", "certified"],
        "tone": "professional and trustworthy",
        "approach": "Build confidence through credibility, testimonials, and proven results",
        "avoid": ["exaggerated claims", "unverifiable promises", "overly casual language"],
        "sample_phrases": ["trusted by thousands", "proven track record", "reliable solution"]
    },
    
    EmotionType.ASPIRATIONAL: {
        "description": "Luxury and lifestyle content that appeals to status and desires",
        "keywords": ["exclusive", "premium", "luxury", "elite", "sophisticated", "refined"],
        "tone": "sophisticated and desirable",
        "approach": "Appeal to status, exclusivity, and lifestyle aspirations",
        "avoid": ["budget language", "mass market appeals", "urgent pressure tactics"],
        "sample_phrases": ["exclusive access", "premium experience", "luxury lifestyle"]
    },
    
    EmotionType.PROBLEM_SOLVING: {
        "description": "Solution-focused content that addresses specific pain points",
        "keywords": ["solve", "fix", "eliminate", "overcome", "solution", "answer"],
        "tone": "helpful and solution-oriented",
        "approach": "Identify specific problems and present clear solutions",
        "avoid": ["dwelling on problems", "vague solutions", "overpromising"],
        "sample_phrases": ["solve your problem", "end the frustration", "finally, a solution"]
    },
    
    EmotionType.EXCITEMENT: {
        "description": "Energetic content that generates enthusiasm and fun",
        "keywords": ["amazing", "awesome", "incredible", "fantastic", "thrilling", "exciting"],
        "tone": "energetic and enthusiastic",
        "approach": "Generate enthusiasm and excitement about the offer",
        "avoid": ["boring language", "overly formal tone", "understated benefits"],
        "sample_phrases": ["get excited", "amazing opportunity", "thrilling experience"]
    },
    
    EmotionType.FEAR_OF_MISSING_OUT: {
        "description": "Social proof content that leverages FOMO and popularity",
        "keywords": ["everyone", "trending", "popular", "selling fast", "join", "thousands"],
        "tone": "socially aware and trend-conscious",
        "approach": "Use social proof and popularity to create FOMO",
        "avoid": ["isolation", "unpopular positioning", "low adoption claims"],
        "sample_phrases": ["join thousands", "trending now", "everyone's talking about"]
    },
    
    EmotionType.CURIOSITY: {
        "description": "Intriguing content that sparks interest and discovery",
        "keywords": ["discover", "secret", "hidden", "reveal", "uncover", "find out"],
        "tone": "mysterious and intriguing",
        "approach": "Create intrigue and curiosity to drive engagement",
        "avoid": ["revealing everything upfront", "boring straightforward language"],
        "sample_phrases": ["discover the secret", "hidden benefits", "find out why"]
    },
    
    EmotionType.CONFIDENCE: {
        "description": "Empowering content that builds self-assurance and boldness",
        "keywords": ["confident", "powerful", "strong", "bold", "fearless", "capable"],
        "tone": "empowering and bold",
        "approach": "Make the audience feel capable and confident",
        "avoid": ["self-doubt language", "hesitant positioning", "weak calls-to-action"],
        "sample_phrases": ["be confident", "take control", "you've got this"]
    },
    
    EmotionType.COMFORT: {
        "description": "Reassuring content that provides safety and familiarity",
        "keywords": ["safe", "secure", "comfortable", "familiar", "peace of mind", "worry-free"],
        "tone": "reassuring and comfortable",
        "approach": "Provide reassurance and reduce anxiety about the decision",
        "avoid": ["risky language", "uncertainty", "pressure tactics"],
        "sample_phrases": ["peace of mind", "safe choice", "worry-free"]
    }
}

# Platform-specific creativity recommendations
PLATFORM_CREATIVITY_GUIDELINES: Dict[str, Dict[str, Any]] = {
    "facebook": {
        "recommended_creativity": 6,  # Balanced creative
        "max_safe_creativity": 8,
        "works_well": ["storytelling", "emotional appeals", "social proof"],
        "avoid": ["overly corporate", "too experimental", "complex concepts"]
    },
    "instagram": {
        "recommended_creativity": 7,  # Creative
        "max_safe_creativity": 9,
        "works_well": ["visual metaphors", "lifestyle appeals", "trendy language"],
        "avoid": ["text-heavy approaches", "boring corporate speak"]
    },
    "linkedin": {
        "recommended_creativity": 4,  # Balanced conservative
        "max_safe_creativity": 6,
        "works_well": ["professional insights", "industry trends", "thought leadership"],
        "avoid": ["casual language", "overly creative angles", "entertainment focus"]
    },
    "twitter": {
        "recommended_creativity": 7,  # Creative
        "max_safe_creativity": 9,
        "works_well": ["witty one-liners", "trending topics", "conversational tone"],
        "avoid": ["long explanations", "formal language", "complex ideas"]
    },
    "tiktok": {
        "recommended_creativity": 9,  # Bold
        "max_safe_creativity": 10,
        "works_well": ["trend-jacking", "humor", "authentic voice", "bold statements"],
        "avoid": ["corporate speak", "overly polished", "traditional approaches"]
    },
    "google": {
        "recommended_creativity": 5,  # Balanced
        "max_safe_creativity": 7,
        "works_well": ["clear value props", "benefit-focused", "solution-oriented"],
        "avoid": ["abstract concepts", "unclear messaging", "overly artistic language"]
    }
}

def get_creativity_parameters(creativity_level: int) -> Tuple[float, float, float]:
    """Get OpenAI parameters for a specific creativity level."""
    return CREATIVITY_TEMPERATURE_MAPPING.get(creativity_level, CREATIVITY_TEMPERATURE_MAPPING[5])

def get_urgency_instruction(urgency_level: int) -> str:
    """Get urgency instruction for a specific level."""
    clamped_level = max(0, min(10, urgency_level))
    return URGENCY_INSTRUCTIONS[clamped_level]

def get_emotion_config(emotion_type: EmotionType) -> Dict[str, Any]:
    """Get configuration for a specific emotion type."""
    return EMOTION_TYPE_CONFIG.get(emotion_type, EMOTION_TYPE_CONFIG[EmotionType.INSPIRING])

def get_platform_creativity_guide(platform: str) -> Dict[str, Any]:
    """Get creativity guidelines for a specific platform."""
    return PLATFORM_CREATIVITY_GUIDELINES.get(platform, PLATFORM_CREATIVITY_GUIDELINES["facebook"])

def is_cliche_phrase(text: str) -> bool:
    """Check if text contains marketing clichés."""
    text_lower = text.lower()
    return any(cliche in text_lower for cliche in MARKETING_CLICHES)

def get_cliche_alternatives(cliche: str) -> List[str]:
    """Get alternative phrases for a cliché."""
    return CLICHE_ALTERNATIVES.get(cliche.lower(), [])

def build_creative_instructions(
    creativity_level: int,
    urgency_level: int,
    emotion_type: EmotionType,
    filter_cliches: bool = True
) -> str:
    """Build comprehensive creative instructions for AI prompts."""
    
    instructions = []
    
    # Creativity instructions
    if creativity_level <= 3:
        instructions.append("Use proven, safe approaches. Stick to conventional messaging that has worked reliably.")
    elif creativity_level <= 6:
        instructions.append("Balance creativity with proven approaches. Be creative but not risky.")
    else:
        instructions.append("Be bold and creative. Use unconventional angles and attention-grabbing approaches.")
    
    # Urgency instructions
    urgency_instruction = get_urgency_instruction(urgency_level)
    instructions.append(f"Urgency level: {urgency_instruction}")
    
    # Emotion instructions
    emotion_config = get_emotion_config(emotion_type)
    instructions.append(f"Emotional tone: {emotion_config['tone']}")
    instructions.append(f"Approach: {emotion_config['approach']}")
    
    # Cliché filtering
    if filter_cliches:
        cliche_list = ", ".join(list(MARKETING_CLICHES)[:15])  # Show first 15 examples
        instructions.append(f"AVOID marketing clichés such as: {cliche_list} and similar overused phrases.")
        instructions.append("Use fresh, original language instead of worn-out marketing speak.")
    
    return " ".join(instructions)

def get_creativity_description(creativity_level: int) -> str:
    """Get human-readable description of creativity level."""
    descriptions = {
        0: "Ultra Safe - Extremely conservative, proven only",
        1: "Very Safe - Minimal creative risk",
        2: "Safe - Conventional approaches",
        3: "Mostly Safe - Slight variations on proven methods",
        4: "Balanced Conservative - Leaning safe with some creativity",
        5: "Balanced - Perfect balance of safe and creative",
        6: "Balanced Creative - Leaning creative with some safety",
        7: "Creative - Bold angles and fresh approaches",
        8: "Very Creative - Unconventional and attention-grabbing",
        9: "Bold - Risky, standout messaging",
        10: "Experimental - Maximum creativity, highest risk"
    }
    return descriptions.get(creativity_level, "Balanced")

def get_urgency_description(urgency_level: int) -> str:
    """Get human-readable description of urgency level."""
    descriptions = {
        0: "No Pressure - Completely relaxed approach",
        1: "Minimal - Gentle suggestions only",
        2: "Subtle - Light encouragement",
        3: "Gentle - Soft nudging toward action",
        4: "Moderate Low - Some encouragement",
        5: "Balanced - Reasonable time sensitivity",
        6: "Moderate High - Clear action encouragement",
        7: "Urgent - Definite time pressure",
        8: "High Urgency - Strong scarcity messaging",
        9: "Critical - Fear of missing out focus",
        10: "Maximum - Immediate action required"
    }
    return descriptions.get(urgency_level, "Balanced")

def analyze_creative_risk(
    creativity_level: int, 
    urgency_level: int,
    emotion_type: EmotionType,
    platform: str
) -> Dict[str, Any]:
    """Analyze the creative risk level of the current settings."""
    platform_guide = get_platform_creativity_guide(platform)
    
    # Calculate risk scores
    creativity_risk = max(0, creativity_level - platform_guide["recommended_creativity"])
    urgency_risk = max(0, urgency_level - 7)  # 7+ is considered risky urgency
    
    # Emotion risk (some emotions are riskier on certain platforms)
    emotion_risk_map = {
        EmotionType.URGENT: 2 if platform in ["linkedin"] else 0,
        EmotionType.EXCITEMENT: 2 if platform in ["linkedin"] else 0,
        EmotionType.FEAR_OF_MISSING_OUT: 1,
        EmotionType.CURIOSITY: 1 if platform in ["linkedin"] else 0,
    }
    emotion_risk = emotion_risk_map.get(emotion_type, 0)
    
    total_risk = creativity_risk + urgency_risk + emotion_risk
    
    if total_risk == 0:
        risk_level = "Low"
        risk_message = "Safe settings for reliable performance"
    elif total_risk <= 2:
        risk_level = "Medium"
        risk_message = "Moderate risk with potential for higher engagement"
    else:
        risk_level = "High"
        risk_message = "High risk - may not be suitable for all audiences"
    
    return {
        "risk_level": risk_level,
        "risk_score": total_risk,
        "risk_message": risk_message,
        "creativity_risk": creativity_risk,
        "urgency_risk": urgency_risk,
        "emotion_risk": emotion_risk,
        "recommendations": _get_risk_recommendations(total_risk, platform)
    }

def _get_risk_recommendations(total_risk: int, platform: str) -> List[str]:
    """Get recommendations based on risk level."""
    recommendations = []
    
    if total_risk == 0:
        recommendations.append("Consider slightly increasing creativity for better engagement")
        recommendations.append("Test higher creativity levels to find your audience's preference")
    elif total_risk <= 2:
        recommendations.append("Good balance of safety and creativity")
        recommendations.append("Monitor performance and adjust based on results")
    else:
        recommendations.append("High risk settings - test with smaller audiences first")
        recommendations.append("Consider reducing creativity or urgency levels")
        recommendations.append(f"These settings may not align well with {platform} audience expectations")
    
    return recommendations