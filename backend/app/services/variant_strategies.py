"""
Platform-Specific A/B/C Variant Strategies

Defines custom approaches for generating A/B/C test variants tailored to each platform's
unique characteristics and user behavior patterns.
"""
from typing import Dict, List, Any
from dataclasses import dataclass

@dataclass
class VariantStrategy:
    """Strategy for generating platform-specific variants"""
    version: str  # A, B, or C
    focus_type: str  # benefit_focused, pain_point_focused, etc.
    name: str  # Human-readable name
    description: str  # What this variant tests
    best_for: List[str]  # Audience types this works best for
    tone_modifier: str  # How to adjust tone
    content_approach: str  # Specific content strategy
    cta_style: str  # CTA approach for this variant

class PlatformVariantStrategies:
    """Platform-specific variant generation strategies"""
    
    @staticmethod
    def get_facebook_strategies() -> List[VariantStrategy]:
        """Facebook: Community-focused, emotional, social proof"""
        return [
            VariantStrategy(
                version="A",
                focus_type="benefit_focused",
                name="Social Benefit",
                description="Emphasizes community benefits and social proof",
                best_for=["community-minded users", "social shoppers", "brand loyalists"],
                tone_modifier="enthusiastic and community-focused",
                content_approach="Highlight how many people have benefited, use 'join thousands who...' language, emphasize shared experiences",
                cta_style="Join Now, Get Started, Become Part Of"
            ),
            VariantStrategy(
                version="B",
                focus_type="pain_point_focused",
                name="Problem Solution",
                description="Addresses specific pain points with relatable scenarios",
                best_for=["problem-aware users", "comparison shoppers", "skeptical audiences"],
                tone_modifier="empathetic and solution-oriented",
                content_approach="Start with relatable problem, validate frustration, present clear solution with social validation",
                cta_style="Fix This, Solve Now, Get Relief"
            ),
            VariantStrategy(
                version="C",
                focus_type="story_driven",
                name="Personal Story",
                description="Uses storytelling and emotional connection",
                best_for=["story-loving users", "emotional buyers", "lifestyle-focused audiences"],
                tone_modifier="personal and narrative",
                content_approach="Brief personal story or scenario, emotional journey, relatable transformation",
                cta_style="Start Your Story, Begin Journey, Transform Now"
            )
        ]
    
    @staticmethod
    def get_instagram_strategies() -> List[VariantStrategy]:
        """Instagram: Visual benefits, lifestyle, aesthetic focus"""
        return [
            VariantStrategy(
                version="A",
                focus_type="visual_benefit",
                name="Lifestyle Upgrade",
                description="Focuses on visual and lifestyle improvements",
                best_for=["lifestyle enthusiasts", "visual learners", "aspiration-driven users"],
                tone_modifier="aspirational and aesthetic",
                content_approach="Paint picture of improved lifestyle, use sensory language, focus on visual outcomes and aesthetic benefits",
                cta_style="Glow Up, Level Up, Upgrade Now"
            ),
            VariantStrategy(
                version="B",
                focus_type="urgency",
                name="FOMO Creator",
                description="Creates urgency through trending and limited availability",
                best_for=["trend followers", "FOMO-sensitive users", "impulse buyers"],
                tone_modifier="urgent but trendy",
                content_approach="Emphasize what's trending now, limited time/stock, what others are doing, fear of missing out",
                cta_style="Don't Miss Out, Trending Now, Get Yours"
            ),
            VariantStrategy(
                version="C",
                focus_type="lifestyle_story",
                name="Day-in-Life",
                description="Shows product/service integrated into daily lifestyle",
                best_for=["lifestyle browsers", "routine-focused users", "influence-seekers"],
                tone_modifier="relatable and lifestyle-focused",
                content_approach="Day-in-the-life scenario, how it fits into routine, aesthetic integration, lifestyle enhancement",
                cta_style="Add To Routine, Make It Yours, Try This"
            )
        ]
    
    @staticmethod
    def get_google_ads_strategies() -> List[VariantStrategy]:
        """Google Ads: Keyword-focused, direct, search-intent matching"""
        return [
            VariantStrategy(
                version="A",
                focus_type="keyword_variant",
                name="Search Optimized",
                description="Heavily keyword-focused with direct search intent matching",
                best_for=["high-intent searchers", "comparison shoppers", "research-mode users"],
                tone_modifier="direct and keyword-rich",
                content_approach="Lead with primary keywords, match search terms, emphasize immediate relevance to search query",
                cta_style="Get Quote, Learn More, Contact Us"
            ),
            VariantStrategy(
                version="B",
                focus_type="cta_variant",
                name="Action Focused",
                description="Emphasizes immediate action and conversion",
                best_for=["ready-to-buy users", "decision-made searchers", "urgent need users"],
                tone_modifier="action-oriented and urgent",
                content_approach="Focus on immediate benefits, quick results, easy process, remove friction points",
                cta_style="Start Today, Get Started, Try Free"
            ),
            VariantStrategy(
                version="C",
                focus_type="headline_variant",
                name="Benefit Headlines",
                description="Uses different headline approaches to test message effectiveness",
                best_for=["benefit-focused users", "feature-comparison users", "value seekers"],
                tone_modifier="benefit-driven and clear",
                content_approach="Multiple benefit angles in headlines, feature highlights, value propositions, competitive advantages",
                cta_style="See Benefits, Compare Now, Get Details"
            )
        ]
    
    @staticmethod
    def get_linkedin_strategies() -> List[VariantStrategy]:
        """LinkedIn: Professional, ROI-focused, authority-based"""
        return [
            VariantStrategy(
                version="A",
                focus_type="roi_focused",
                name="Business ROI",
                description="Emphasizes quantifiable business outcomes and ROI",
                best_for=["decision makers", "budget holders", "ROI-focused professionals"],
                tone_modifier="data-driven and results-focused",
                content_approach="Lead with metrics, ROI calculations, business impact, productivity gains, cost savings",
                cta_style="Calculate ROI, See Results, Get Analysis"
            ),
            VariantStrategy(
                version="B",
                focus_type="pain_relief",
                name="Problem Solver",
                description="Addresses professional pain points and inefficiencies",
                best_for=["problem-aware professionals", "process improvers", "efficiency seekers"],
                tone_modifier="problem-solving and authoritative",
                content_approach="Identify business pain points, validate professional struggles, present systematic solution",
                cta_style="Solve This, Fix Now, Improve Process"
            ),
            VariantStrategy(
                version="C",
                focus_type="thought_leader",
                name="Industry Authority",
                description="Positions as thought leadership and industry expertise",
                best_for=["industry professionals", "knowledge seekers", "networking-focused users"],
                tone_modifier="authoritative and educational",
                content_approach="Share industry insights, best practices, expert perspective, thought leadership content",
                cta_style="Learn More, Get Insights, Access Expertise"
            )
        ]
    
    @staticmethod
    def get_twitter_strategies() -> List[VariantStrategy]:
        """Twitter/X: Punchy, quotable, conversation-starting"""
        return [
            VariantStrategy(
                version="A",
                focus_type="bold_statement",
                name="Hot Take",
                description="Bold, quotable statement that sparks engagement",
                best_for=["engaged followers", "conversation starters", "viral content seekers"],
                tone_modifier="bold and conversation-starting",
                content_approach="Make bold claim, controversial but true statement, thought-provoking angle",
                cta_style="Thoughts?, Agree?, What's your take?"
            ),
            VariantStrategy(
                version="B",
                focus_type="urgent_hook",
                name="Breaking News",
                description="Creates urgency with news-style hook",
                best_for=["news followers", "trend watchers", "early adopters"],
                tone_modifier="urgent and news-like",
                content_approach="News-style hook, breaking development, urgent update, time-sensitive information",
                cta_style="Check this out, See details, Read more"
            ),
            VariantStrategy(
                version="C",
                focus_type="relatable_story",
                name="Micro Story",
                description="Relatable micro-story or scenario",
                best_for=["story lovers", "relatable content seekers", "emotional connection users"],
                tone_modifier="relatable and narrative",
                content_approach="Brief relatable scenario, common experience, micro-story with twist or insight",
                cta_style="Been there?, Sound familiar?, Your story?"
            )
        ]
    
    @staticmethod
    def get_tiktok_strategies() -> List[VariantStrategy]:
        """TikTok: Trendy, energetic, Gen-Z focused"""
        return [
            VariantStrategy(
                version="A",
                focus_type="trendy_benefit",
                name="Trend Integration",
                description="Incorporates current trends with product benefits",
                best_for=["trend followers", "Gen-Z users", "viral content consumers"],
                tone_modifier="trendy and current",
                content_approach="Connect to current trends, trending audio/format, make product part of trend",
                cta_style="Try the trend, Join in, Go viral"
            ),
            VariantStrategy(
                version="B",
                focus_type="urgent_call",
                name="FOMO Energy",
                description="High-energy urgency with trending language",
                best_for=["impulse users", "FOMO-sensitive Gen-Z", "quick decision makers"],
                tone_modifier="high-energy and urgent",
                content_approach="High energy, trending urgency language, fear of missing out, quick action needed",
                cta_style="Do it now, Don't wait, Act fast"
            ),
            VariantStrategy(
                version="C",
                focus_type="relatable_tone",
                name="Real Talk",
                description="Authentic, relatable tone with humor/personality",
                best_for=["authenticity seekers", "humor lovers", "personality-driven users"],
                tone_modifier="authentic and humorous",
                content_approach="Real talk, authentic perspective, relatable struggles, humor and personality",
                cta_style="Real talk, No cap, Fr try this"
            )
        ]

def get_platform_strategies(platform_id: str) -> List[VariantStrategy]:
    """Get A/B/C variant strategies for specific platform"""
    strategy_map = {
        'facebook': PlatformVariantStrategies.get_facebook_strategies,
        'instagram': PlatformVariantStrategies.get_instagram_strategies,
        'google_ads': PlatformVariantStrategies.get_google_ads_strategies,
        'linkedin': PlatformVariantStrategies.get_linkedin_strategies,
        'twitter_x': PlatformVariantStrategies.get_twitter_strategies,
        'tiktok': PlatformVariantStrategies.get_tiktok_strategies,
    }
    
    strategy_func = strategy_map.get(platform_id)
    if strategy_func:
        return strategy_func()
    else:
        # Fallback to Facebook strategies
        return PlatformVariantStrategies.get_facebook_strategies()

def get_variant_context(platform_id: str, variant_version: str, base_context: Dict[str, Any] = None) -> Dict[str, Any]:
    """Get enhanced context for specific platform variant"""
    strategies = get_platform_strategies(platform_id)
    variant_strategy = next((s for s in strategies if s.version == variant_version), None)
    
    if not variant_strategy:
        return base_context or {}
    
    # Enhance base context with variant-specific instructions
    enhanced_context = base_context.copy() if base_context else {}
    enhanced_context.update({
        'variant_version': variant_version,
        'variant_focus': variant_strategy.focus_type,
        'variant_name': variant_strategy.name,
        'variant_description': variant_strategy.description,
        'tone_modifier': variant_strategy.tone_modifier,
        'content_approach': variant_strategy.content_approach,
        'cta_style': variant_strategy.cta_style,
        'best_for': variant_strategy.best_for
    })
    
    return enhanced_context