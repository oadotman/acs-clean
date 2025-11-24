"""
Platform Adapter for Tools SDK
Bridges Tools SDK with platform configuration from app.constants.platform_limits

This module provides platform-specific intelligence to all Tools SDK tools,
enabling them to adapt their analysis based on the target advertising platform.
"""

import re
from typing import Dict, Any, List, Optional
from app.constants.platform_limits import (
    get_platform_config,
    get_platform_power_words,
    get_platform_warnings,
    get_platform_creativity_config,
    PLATFORM_CONFIG
)


class PlatformAdapter:
    """
    Provides platform-specific intelligence to Tools SDK

    This adapter serves as a bridge between the Tools SDK and the platform
    configuration system, allowing tools to access platform-specific:
    - Recommended tones and formality levels
    - Power words and optimization tips
    - Emoji usage guidelines
    - Psychology trigger weights
    - Scoring weights by platform
    """

    @staticmethod
    def get_platform_intelligence(platform: str) -> Dict[str, Any]:
        """
        Get all platform-specific intelligence for a platform

        Args:
            platform: Platform name (facebook, google, linkedin, tiktok, instagram)

        Returns:
            Dictionary containing:
                - recommended_tone: HumanTone enum value
                - emoji_default: EmojiLevel enum value
                - formality_level: int (0-10 scale)
                - power_words: List[str] of platform-specific power words
                - optimization_tips: List[str] of optimization suggestions
                - platform_warnings: List[str] of common pitfalls
                - creativity_config: Dict with creativity/urgency/emotion preferences
                - typical_cta: List[str] of effective CTAs for this platform
                - audience_mindset: str describing user behavior on platform
        """
        config = get_platform_config(platform)
        creativity = get_platform_creativity_config(platform)

        return {
            **config,
            'creativity_config': creativity,
            'power_words': get_platform_power_words(platform),
            'platform_warnings': get_platform_warnings(platform)
        }

    @staticmethod
    def get_platform_scoring_weights(platform: str) -> Dict[str, float]:
        """
        Get platform-specific scoring weights

        Different platforms prioritize different aspects:
        - Facebook: Social proof, engagement, emotional connection
        - Google: Clarity, keyword relevance, direct value
        - LinkedIn: Authority, ROI, professional credibility
        - TikTok: Hook strength, authenticity, entertainment
        - Instagram: Visual appeal, aspiration, authenticity

        Args:
            platform: Platform name

        Returns:
            Dictionary of scoring dimension -> weight (0-1 scale, sums to 1.0)
        """
        weights = {
            "facebook": {
                "clarity": 0.15,
                "persuasion": 0.20,
                "emotion": 0.20,
                "cta_strength": 0.15,
                "platform_fit": 0.10,
                "social_proof": 0.20,  # Facebook-specific
            },
            "google": {
                "clarity": 0.30,
                "persuasion": 0.20,
                "emotion": 0.05,
                "cta_strength": 0.25,
                "platform_fit": 0.10,
                "keyword_relevance": 0.10,  # Google-specific
            },
            "linkedin": {
                "clarity": 0.20,
                "persuasion": 0.15,
                "emotion": 0.10,
                "cta_strength": 0.15,
                "platform_fit": 0.10,
                "authority": 0.20,  # LinkedIn-specific
                "roi_emphasis": 0.10,  # LinkedIn-specific
            },
            "tiktok": {
                "clarity": 0.10,
                "persuasion": 0.10,
                "emotion": 0.20,
                "cta_strength": 0.10,
                "platform_fit": 0.10,
                "hook_strength": 0.30,  # TikTok-specific
                "authenticity": 0.10,  # TikTok-specific
            },
            "instagram": {
                "clarity": 0.15,
                "persuasion": 0.15,
                "emotion": 0.20,
                "cta_strength": 0.15,
                "platform_fit": 0.10,
                "visual_appeal": 0.15,  # Instagram-specific
                "aspiration": 0.10,  # Instagram-specific
            }
        }

        return weights.get(platform.lower(), weights["facebook"])

    @staticmethod
    def get_platform_psychology_weights(platform: str) -> Dict[str, float]:
        """
        Get platform-specific psychological trigger weights

        Different platforms respond differently to psychological triggers:
        - Facebook: Social proof > Authority
        - LinkedIn: Authority > Social proof
        - TikTok: Peer validation > Authority (Gen Z psychology)

        Args:
            platform: Platform name

        Returns:
            Dictionary of psychological trigger -> weight (0-10 scale)
            Higher weight = more effective on this platform
        """
        weights = {
            "facebook": {
                "social_proof": 9.0,
                "urgency": 8.0,
                "scarcity": 8.5,
                "authority": 6.5,
                "reciprocity": 7.0,
                "loss_aversion": 8.0,
                "emotional_appeal": 9.0,
            },
            "google": {
                "social_proof": 7.0,
                "urgency": 9.0,
                "scarcity": 8.0,
                "authority": 7.5,
                "reciprocity": 6.0,
                "loss_aversion": 8.5,
                "emotional_appeal": 6.0,
            },
            "linkedin": {
                "social_proof": 7.0,
                "urgency": 6.0,
                "scarcity": 5.0,
                "authority": 9.0,
                "reciprocity": 7.0,
                "loss_aversion": 6.5,
                "emotional_appeal": 5.5,
                "credibility": 9.0,
                "data_driven": 8.5,
            },
            "tiktok": {
                "social_proof": 6.0,  # Lower - formal social proof
                "urgency": 5.0,
                "scarcity": 6.0,
                "authority": 3.0,  # Very low - Gen Z doesn't trust authority
                "reciprocity": 7.0,
                "loss_aversion": 6.0,
                "emotional_appeal": 9.5,
                "peer_validation": 9.5,  # TikTok-specific - high importance
                "authenticity": 9.0,
                "trend_relevance": 8.5,
            },
            "instagram": {
                "social_proof": 8.5,
                "urgency": 6.5,
                "scarcity": 7.5,
                "authority": 6.0,
                "reciprocity": 7.5,
                "loss_aversion": 7.0,
                "emotional_appeal": 9.0,
                "aspiration": 9.0,
                "lifestyle_fit": 8.5,
            }
        }

        return weights.get(platform.lower(), weights["facebook"])

    @staticmethod
    def should_analyze_emojis(platform: str) -> bool:
        """
        Determine if emoji analysis is relevant for this platform

        Args:
            platform: Platform name

        Returns:
            True if platform supports/encourages emojis, False otherwise
        """
        config = get_platform_config(platform)
        emoji_level = str(config.get('emoji_default', 'moderate')).lower()

        # Don't analyze emojis for platforms that don't support them
        if platform.lower() == 'google':
            return False

        return True

    @staticmethod
    def get_emoji_recommendations(platform: str, current_emoji_count: int) -> str:
        """
        Get platform-specific emoji recommendations

        Args:
            platform: Platform name
            current_emoji_count: Number of emojis currently in the ad copy

        Returns:
            Human-readable recommendation string with emoji guidance
        """
        config = get_platform_config(platform)
        emoji_default = str(config.get('emoji_default', 'moderate')).lower()

        recommendations = {
            'minimal': f"Use 1-2 emojis maximum. Current: {current_emoji_count}. ",
            'moderate': f"Use 3-5 emojis strategically. Current: {current_emoji_count}. ",
            'expressive': f"Liberal emoji use expected. Current: {current_emoji_count}. "
        }

        base_rec = recommendations.get(emoji_default, recommendations['moderate'])

        # Platform-specific guidance
        if platform.lower() == 'google':
            return "No emojis - Google Ads strips them from display."
        elif platform.lower() == 'linkedin' and current_emoji_count > 2:
            return base_rec + "Too many emojis hurt professional credibility on LinkedIn."
        elif platform.lower() == 'tiktok' and current_emoji_count == 0:
            return base_rec + "Add emojis - TikTok culture embraces expressive communication."
        elif platform.lower() == 'instagram' and current_emoji_count < 3:
            return base_rec + "Add more emojis - Instagram users expect visual, expressive content."

        return base_rec + "Emoji usage appropriate for platform."

    @staticmethod
    def get_platform_roi_type(platform: str) -> str:
        """
        Get appropriate ROI type for platform

        Different platforms emphasize different types of ROI:
        - Facebook/Instagram: Emotional ROI (time saved, stress reduced, happiness gained)
        - LinkedIn/Google: Financial ROI (revenue increase, cost savings)
        - TikTok: Experience ROI (fun, entertainment, lifestyle improvement)

        Args:
            platform: Platform name

        Returns:
            ROI type string: 'financial', 'emotional_and_financial',
                           'experiential', 'lifestyle_and_emotional',
                           'financial_and_strategic'
        """
        roi_types = {
            "facebook": "emotional_and_financial",
            "google": "financial",
            "linkedin": "financial_and_strategic",
            "tiktok": "experiential",
            "instagram": "lifestyle_and_emotional"
        }
        return roi_types.get(platform.lower(), "financial")

    @staticmethod
    def get_jargon_level_for_platform(platform: str, industry: str) -> str:
        """
        Determine appropriate jargon level based on platform and industry

        Platform-Industry Matrix:
        - LinkedIn-Healthcare: HIGH jargon OK (clinical professionals)
        - Facebook-Healthcare: LOW jargon only (consumer patients)
        - TikTok-Any: MINIMAL jargon (Gen Z audience)
        - Instagram-Lifestyle: MINIMAL jargon (aspirational, not technical)

        Args:
            platform: Platform name
            industry: Industry name (healthcare, technology, finance, etc.)

        Returns:
            Jargon level: 'minimal', 'low', 'medium', or 'high'
        """
        # TikTok always gets minimal jargon
        if platform.lower() == 'tiktok':
            return 'minimal'

        # Instagram depends on industry
        if platform.lower() == 'instagram':
            if industry.lower() in ['retail', 'lifestyle', 'beauty', 'fashion']:
                return 'minimal'
            return 'low'

        # LinkedIn can handle more jargon
        if platform.lower() == 'linkedin':
            if industry.lower() in ['healthcare', 'technology', 'finance']:
                return 'high'
            return 'medium'

        # Facebook and Google default to low-medium
        if platform.lower() in ['facebook', 'google']:
            if industry.lower() in ['healthcare', 'finance']:
                return 'low'  # Consumer-facing, not professionals
            return 'medium'

        return 'medium'  # Default


# Singleton instance for easy import
platform_adapter = PlatformAdapter()
