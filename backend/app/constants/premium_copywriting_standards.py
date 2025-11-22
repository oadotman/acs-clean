"""
Premium Copywriting Standards for AdCopySurge
Ensures all ad copy output feels strategic, premium, and human-written.
"""

from typing import List, Dict, Set
import re

# ❌ BANNED CLICHÉS - Never use these
BANNED_CLICHES = {
    # Overused hype words
    "game-changer", "game changer", "revolutionary", "groundbreaking", "next-level",
    "cutting-edge", "cutting edge", "world-class", "world class", "best-in-class",
    "industry-leading", "industry leading", "state-of-the-art", "state of the art",
    
    # Generic transformations
    "transform your life", "change your life", "life-changing", "life changing",
    "amazing results", "incredible results", "unbelievable results",
    
    # Desperate urgency
    "don't miss out", "don't wait", "act now or regret it", "once in a lifetime",
    "limited time only" # Use "limited time" is okay, but not "only"
    
    # Vague promises
    "unlock your potential", "reach your goals", "achieve success",
    "take it to the next level", "elevate your game",
    
    # Buzzword fatigue
    "synergy", "leverage", "paradigm shift", "disruptive", "ninja", "guru",
    "rockstar", "unicorn" # (Unless it's a literal unicorn product)
}

# ⚠️ USE WITH CAUTION - Can work if used strategically, not repeatedly
CAUTION_PHRASES = {
    "exclusive", "limited", "proven", "guaranteed", "secret", "hack",
    "discover", "unlock", "transform", "revolutionary" # Context matters
}

# ✅ POWER WORDS - Premium alternatives
PREMIUM_ALTERNATIVES = {
    "game-changer": ["innovation", "breakthrough solution", "strategic advantage"],
    "revolutionary": ["advanced", "cutting-edge approach", "sophisticated system"],
    "amazing": ["remarkable", "exceptional", "outstanding", "compelling"],
    "incredible": ["impressive", "substantial", "significant", "notable"],
    "transform your life": ["elevate your results", "accelerate your progress", "enhance your outcomes"],
    "unlock your potential": ["maximize your capabilities", "optimize your performance", "achieve measurable growth"],
    "don't miss out": ["reserve your spot", "secure your access", "join today"],
    "act now": ["start today", "begin now", "get started"],
}

# 🚫 FORBIDDEN PATTERNS
class CopywritingViolations:
    """Define patterns that make copy feel crass or unprofessional"""
    
    MULTIPLE_EXCLAMATIONS = r'!{2,}'  # "Amazing!! Great!!" = banned
    ALL_CAPS_WORDS = r'\b[A-Z]{4,}\b'  # "AMAZING DEAL" = banned (unless acronym)
    PHRASE_STACKING = r'(Amazing|Incredible|Must-have|Revolutionary)[!,\s]+(Amazing|Incredible|Must-have|Revolutionary)'
    EXCESSIVE_EMOJIS = r'([\U0001F300-\U0001F9FF]){4,}'  # 4+ emojis in a row
    ROBOTIC_TRANSITIONS = r'\b(Additionally|Furthermore|Moreover|In addition|Subsequently)\b'

# ✅ QUALITY STANDARDS
class PremiumCopyStandards:
    """Standards all output must meet"""
    
    # Exclamation marks
    MAX_EXCLAMATIONS_PER_VARIANT = 1
    
    # Emoji usage by platform
    EMOJI_LIMITS = {
        "facebook": {"min": 0, "max": 3, "style": "strategic"},
        "instagram": {"min": 1, "max": 5, "style": "expressive"},
        "linkedin": {"min": 0, "max": 1, "style": "professional"},
        "twitter": {"min": 0, "max": 2, "style": "conversational"},
        "tiktok": {"min": 1, "max": 4, "style": "authentic"},
        "google": {"min": 0, "max": 0, "style": "none"}  # Google strips emojis
    }
    
    # Length requirements (words, not chars)
    IMPROVED_VERSION_WORDS = {"min": 60, "max": 120}
    VARIANT_WORDS = {"min": 50, "max": 100}
    
    # Hook requirements (first 5 words)
    HOOK_PATTERNS = [
        "question", "bold_statement", "specific_number", 
        "transformation_promise", "pain_point_call_out"
    ]


def detect_cliches(text: str) -> List[Dict[str, str]]:
    """
    Detect clichés in copy and return violations.
    
    Returns:
        List of {phrase, severity, suggestion} dicts
    """
    violations = []
    text_lower = text.lower()
    
    # Check banned clichés
    for cliche in BANNED_CLICHES:
        if cliche in text_lower:
            violations.append({
                "phrase": cliche,
                "severity": "critical",
                "suggestion": PREMIUM_ALTERNATIVES.get(cliche, ["Use specific, measurable language"])[0],
                "reason": "Overused marketing cliché - feels generic and unprofessional"
            })
    
    # Check caution phrases (only flag if used multiple times)
    for phrase in CAUTION_PHRASES:
        count = text_lower.count(phrase)
        if count > 1:
            violations.append({
                "phrase": phrase,
                "severity": "warning",
                "suggestion": f"Use '{phrase}' once at most, or replace with specific details",
                "reason": f"Used {count} times - overuse reduces impact"
            })
    
    return violations


def detect_violations(text: str) -> List[Dict[str, str]]:
    """
    Detect copywriting violations (exclamations, caps, phrase stacking).
    
    Returns:
        List of {type, severity, message} dicts
    """
    violations = []
    
    # Multiple exclamation marks
    if re.search(CopywritingViolations.MULTIPLE_EXCLAMATIONS, text):
        violations.append({
            "type": "multiple_exclamations",
            "severity": "critical",
            "message": "Multiple exclamation marks (!!!) look desperate and unprofessional. Use one max."
        })
    
    # ALL CAPS (excluding common acronyms)
    caps_matches = re.findall(CopywritingViolations.ALL_CAPS_WORDS, text)
    caps_words = [w for w in caps_matches if w not in {"FREE", "NEW", "SALE", "ROI", "AI", "API", "CRM", "SEO"}]
    if caps_words:
        violations.append({
            "type": "all_caps",
            "severity": "critical",
            "message": f"ALL CAPS words detected: {', '.join(caps_words)}. Use sentence case for professionalism."
        })
    
    # Phrase stacking
    if re.search(CopywritingViolations.PHRASE_STACKING, text, re.IGNORECASE):
        violations.append({
            "type": "phrase_stacking",
            "severity": "warning",
            "message": "Stacking hype phrases ('Amazing! Incredible!') feels robotic. Space out power words."
        })
    
    # Robotic transitions
    if re.search(CopywritingViolations.ROBOTIC_TRANSITIONS, text):
        violations.append({
            "type": "robotic_transitions",
            "severity": "warning",
            "message": "Corporate transitions (Additionally, Furthermore) sound AI-generated. Use natural flow."
        })
    
    return violations


def validate_emoji_usage(text: str, platform: str, user_emoji_preference: str = None) -> Dict:
    """
    Validate emoji usage against platform standards.
    
    Args:
        text: Copy to validate
        platform: Platform name (facebook, instagram, etc.)
        user_emoji_preference: User's explicit choice (include/exclude/auto)
    
    Returns:
        {valid: bool, emoji_count: int, message: str}
    """
    # Count emojis (Unicode emoji range)
    emoji_pattern = r'[\U0001F300-\U0001F9FF]'
    emojis = re.findall(emoji_pattern, text)
    emoji_count = len(emojis)
    
    # Get platform limits
    platform_limits = PremiumCopyStandards.EMOJI_LIMITS.get(platform, {"min": 0, "max": 2})
    
    # User explicitly said no emojis
    if user_emoji_preference == "exclude" or user_emoji_preference == "no":
        if emoji_count > 0:
            return {
                "valid": False,
                "emoji_count": emoji_count,
                "message": f"User requested no emojis, but {emoji_count} found. Remove all emojis."
            }
        return {"valid": True, "emoji_count": 0, "message": "No emojis as requested"}
    
    # Check platform limits
    if emoji_count < platform_limits["min"]:
        return {
            "valid": False,
            "emoji_count": emoji_count,
            "message": f"{platform.title()} performs best with {platform_limits['min']}-{platform_limits['max']} emojis. Currently: {emoji_count}"
        }
    
    if emoji_count > platform_limits["max"]:
        return {
            "valid": False,
            "emoji_count": emoji_count,
            "message": f"{platform.title()} allows max {platform_limits['max']} emojis for professionalism. Currently: {emoji_count}"
        }
    
    return {
        "valid": True,
        "emoji_count": emoji_count,
        "message": f"Emoji usage optimal for {platform} ({emoji_count}/{platform_limits['max']})"
    }


def assess_copy_quality(text: str, platform: str, variant_type: str = "improved") -> Dict:
    """
    Comprehensive quality assessment of ad copy.
    
    Returns:
        {
            score: 0-100,
            cliche_violations: [...],
            writing_violations: [...],
            emoji_check: {...},
            length_check: {...},
            overall_verdict: str
        }
    """
    cliche_violations = detect_cliches(text)
    writing_violations = detect_violations(text)
    emoji_check = validate_emoji_usage(text, platform)
    
    # Length check
    word_count = len(text.split())
    length_standard = PremiumCopyStandards.IMPROVED_VERSION_WORDS if variant_type == "improved" else PremiumCopyStandards.VARIANT_WORDS
    
    length_valid = length_standard["min"] <= word_count <= length_standard["max"]
    length_check = {
        "valid": length_valid,
        "word_count": word_count,
        "target": f"{length_standard['min']}-{length_standard['max']} words",
        "message": f"Word count: {word_count} ({'✓' if length_valid else '✗ Out of range'})"
    }
    
    # Calculate score
    score = 100
    score -= len(cliche_violations) * 15  # -15 per cliché
    score -= len([v for v in writing_violations if v["severity"] == "critical"]) * 10
    score -= len([v for v in writing_violations if v["severity"] == "warning"]) * 5
    if not emoji_check["valid"]:
        score -= 5
    if not length_valid:
        score -= 10
    
    score = max(0, score)
    
    # Verdict
    if score >= 90:
        verdict = "Premium quality - ready to use"
    elif score >= 75:
        verdict = "Good quality - minor improvements recommended"
    elif score >= 60:
        verdict = "Acceptable - needs refinement"
    else:
        verdict = "Poor quality - major revision needed"
    
    return {
        "score": score,
        "cliche_violations": cliche_violations,
        "writing_violations": writing_violations,
        "emoji_check": emoji_check,
        "length_check": length_check,
        "overall_verdict": verdict,
        "passes_standards": score >= 75
    }


def build_premium_system_prompt() -> str:
    """
    Build the system prompt that ensures premium copywriting quality.
    This should be prepended to all AI generation requests.
    """
    return """You are a senior copywriter with 15+ years of experience at top agencies (Ogilvy, Wieden+Kennedy, BBDO). You've written campaigns that generated $100M+ in revenue.

🎯 YOUR MISSION: Create premium, strategic, emotionally persuasive ad copy that feels human-written.

✅ ALWAYS DO:
• Write with flow, rhythm, and confidence
• Use specific, concrete details over vague claims
• Make "Improved" versions demonstrably better (not just shorter)
• Start with strong hooks that grab attention in first 5 words
• Build emotional connection through authentic language
• Include clear value propositions (what's in it for them?)
• Use smooth transitions and natural phrasing
• Sound premium, not pushy or desperate

❌ NEVER DO:
• Generic clichés: "game-changer", "revolutionary", "don't miss out", "world-class", "cutting-edge"
• Multiple exclamation marks (max 1 per copy)
• ALL CAPS for emphasis (use word choice instead)
• Phrase stacking ("Amazing! Incredible! Must-have!")
• Robotic transitions ("Additionally", "Furthermore", "Moreover")
• Desperate urgency ("Act now or regret it forever!")

💎 TONE: Confident, strategic, emotionally intelligent. Sound like a trusted advisor, not a used car salesman.

📏 LENGTH: Improved = 60-120 words. Variants A/B/C = 50-100 words each.

Remember: Premium copy persuades through clarity, specificity, and emotional resonance—not through hype."""


def build_variant_framework_prompts() -> Dict[str, str]:
    """
    Build strict framework prompts for A/B/C variants.
    """
    return {
        "benefit_focused": """
🅰️ VARIANT A: BENEFIT-FOCUSED (Aspirational Transformation)

STRATEGY: Lead with the end result, not the process. Paint the "after" picture.

STRUCTURE:
1. Open with aspirational hook: "Imagine...", "Finally...", "Picture yourself..."
2. Describe the transformed state (how life improves after purchase)
3. Highlight positive emotions and end benefits (not features)
4. Close with soft-to-medium CTA that invites into the experience

TONE: Aspirational, premium, inspiring

RULES:
• NO problem language ("struggling", "tired of", "frustrated")
• Focus on GAINS, not pain points
• Use sensory, vivid language
• Show the destination, not the journey
• 50-100 words, one emoji max (if platform appropriate)

EXAMPLE OPENING: "Imagine waking up to..."  "Finally—a way to..." "Picture this:"
""",
        
        "problem_focused": """
🅱️ VARIANT B: PROBLEM-FOCUSED (Pain Point → Solution)

STRATEGY: Agitate the problem, then present product as obvious relief.

STRUCTURE:
1. Open with pain point: "Tired of...", "Struggling with...", "Sick of..."
2. Acknowledge the frustration and validate their feelings
3. Introduce solution as the answer they've been seeking
4. Show before → after contrast
5. Close with action-oriented CTA

TONE: Empathetic, urgent, solution-driven

RULES:
• Start with the PAIN (don't sugarcoat it)
• Make them FEEL the problem
• Position product as relief, not just a feature
• Include specific problem → solution bridge
• 50-100 words, one emoji max (if platform appropriate)

EXAMPLE OPENING: "Tired of wasting hours on..." "Still struggling with..." "Fed up with..."
""",
        
        "story_driven": """
🅲️ VARIANT C: STORY-DRIVEN (Narrative Connection)

STRATEGY: Use mini-story structure to create emotional resonance.

STRUCTURE:
1. Set up relatable scenario or moment
2. Build tension or present challenge
3. Introduce resolution (the product/service)
4. Show transformation through narrative
5. Close with invitation CTA

TONE: Conversational, emotional, authentic

RULES:
• Use NARRATIVE elements (setup → tension → resolution)
• Include specific, relatable moments (not generic)
• Reference "our customer", "real experience", or vivid scenario
• Build trust through authenticity, not hype
• Show, don't just tell
• 50-100 words, one emoji max (if platform appropriate)

EXAMPLE OPENING: "Sarah spent years..." "Here's what happens when..." "Meet the business owner who..."
"""
    }


# Export key functions
__all__ = [
    'detect_cliches',
    'detect_violations',
    'validate_emoji_usage',
    'assess_copy_quality',
    'build_premium_system_prompt',
    'build_variant_framework_prompts',
    'BANNED_CLICHES',
    'PREMIUM_ALTERNATIVES',
    'PremiumCopyStandards'
]
