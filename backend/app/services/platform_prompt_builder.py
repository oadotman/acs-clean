"""
Platform-Specific Prompt Builder

Creates tailored LLM prompts for each platform with exact requirements,
character limits, tone guidelines, and structured JSON output format.
"""
import json
import logging
from typing import Dict, Any, Optional
from dataclasses import asdict

from .platform_registry import get_platform_config, PlatformConfig
from .platform_aware_parser import ParsedAd

logger = logging.getLogger(__name__)

class PlatformPromptBuilder:
    """Builds platform-specific prompts for LLM generation"""
    
    def __init__(self):
        self.base_instructions = {
            'grammar': "CRITICAL: Output must be grammatically perfect with no errors, fragments, or awkward phrasing.",
            'banned_phrases': "FORBIDDEN: Never use these template phrases: 'Unlock the benefits of', 'Tired of the problem?', 'Imagine this:', 'Get all products today!'",
            'format': "OUTPUT FORMAT: Respond with valid JSON only. No additional text, explanations, or formatting.",
            'uniqueness': "UNIQUENESS: Ensure no repetitive language or redundant phrases within the output.",
        }
    
    def build_prompt(self, platform_id: str, parsed_ad: ParsedAd, additional_context: Optional[Dict[str, Any]] = None) -> Dict[str, str]:
        """Build complete prompt for platform"""
        config = get_platform_config(platform_id)
        if not config:
            raise ValueError(f"No configuration found for platform: {platform_id}")
        
        # Get platform-specific prompt template
        if platform_id == 'facebook':
            return self._build_facebook_prompt(config, parsed_ad, additional_context)
        elif platform_id == 'instagram':
            return self._build_instagram_prompt(config, parsed_ad, additional_context)
        elif platform_id == 'google_ads':
            return self._build_google_ads_prompt(config, parsed_ad, additional_context)
        elif platform_id == 'linkedin':
            return self._build_linkedin_prompt(config, parsed_ad, additional_context)
        elif platform_id == 'twitter_x':
            return self._build_twitter_x_prompt(config, parsed_ad, additional_context)
        elif platform_id == 'tiktok':
            return self._build_tiktok_prompt(config, parsed_ad, additional_context)
        else:
            raise ValueError(f"Unsupported platform: {platform_id}")
    
    def _build_facebook_prompt(self, config: PlatformConfig, parsed_ad: ParsedAd, context: Optional[Dict[str, Any]]) -> Dict[str, str]:
        """Build Facebook-specific prompt"""
        system_prompt = f"""You are an expert Facebook ad copywriter with 10+ years of experience creating high-converting social media ads.

PLATFORM: Facebook
TONE: {config.tone}
AUDIENCE: {config.audience_mindset}

STRICT REQUIREMENTS:
- Headline: Maximum {config.fields['headline'].max_chars} characters, conversational and attention-grabbing
- Body: Maximum {config.fields['body'].max_chars} characters, friendly and engaging  
- CTA: Maximum {config.fields['cta'].max_chars} characters, clear action-oriented button text
- {self.base_instructions['grammar']}
- {self.base_instructions['banned_phrases']}
- NO repetition of headline text in body copy
- Community-focused language that encourages engagement

EXAMPLE OUTPUT FORMAT:
{json.dumps({
    "headline": "Save 50% on premium software today",
    "body": "Join thousands who've transformed their business with our proven tools. Limited time offer ends soon!",
    "cta": "Get Started Now"
}, indent=2)}"""

        user_prompt = f"""Transform this ad copy for Facebook:

ORIGINAL CONTENT:
{json.dumps(parsed_ad.content, indent=2)}

CONTEXT:
- Industry: {context.get('industry', 'general') if context else 'general'}
- Target Audience: {context.get('target_audience', 'general audience') if context else 'general audience'}
- Brand Voice: {context.get('brand_voice', 'friendly and professional') if context else 'friendly and professional'}

CREATE: High-converting Facebook ad that follows all character limits and requirements.
{self.base_instructions['format']}"""

        return {
            'system': system_prompt,
            'user': user_prompt
        }
    
    def _build_instagram_prompt(self, config: PlatformConfig, parsed_ad: ParsedAd, context: Optional[Dict[str, Any]]) -> Dict[str, str]:
        """Build Instagram-specific prompt"""
        system_prompt = f"""You are an expert Instagram content creator specializing in viral, engaging posts that drive action.

PLATFORM: Instagram  
TONE: {config.tone}
AUDIENCE: {config.audience_mindset}

STRICT REQUIREMENTS:
- Body: Maximum {config.fields['body'].max_chars} characters, with first 125 characters as a strong hook
- Hashtags: Include {config.fields['hashtags'].min_count}-{config.fields['hashtags'].count} relevant hashtags
- CTA: Optional, maximum {config.fields['cta'].max_chars} characters, soft and non-pushy
- {self.base_instructions['grammar']}
- {self.base_instructions['banned_phrases']}
- Visual storytelling style that complements imagery
- Natural hashtag integration (not forced)

EXAMPLE OUTPUT FORMAT:
{json.dumps({
    "body": "Transform your morning routine with our game-changing wellness ritual. Here's what happened when I tried it for 30 days...",
    "hashtags": ["#wellness", "#morningroutine", "#selfcare", "#healthy", "#lifestyle"],
    "cta": "Discover More"
}, indent=2)}"""

        user_prompt = f"""Transform this content for Instagram:

ORIGINAL CONTENT:
{json.dumps(parsed_ad.content, indent=2)}

CONTEXT:
- Industry: {context.get('industry', 'general') if context else 'general'}  
- Target Audience: {context.get('target_audience', 'lifestyle enthusiasts') if context else 'lifestyle enthusiasts'}
- Visual Style: {context.get('visual_style', 'inspiring and aesthetic') if context else 'inspiring and aesthetic'}

CREATE: Engaging Instagram post with compelling hook, relevant hashtags, and optional soft CTA.
{self.base_instructions['format']}"""

        return {
            'system': system_prompt,
            'user': user_prompt
        }
    
    def _build_google_ads_prompt(self, config: PlatformConfig, parsed_ad: ParsedAd, context: Optional[Dict[str, Any]]) -> Dict[str, str]:
        """Build Google Ads-specific prompt"""
        system_prompt = f"""You are a Google Ads specialist with expertise in search marketing and keyword optimization.

PLATFORM: Google Ads
TONE: {config.tone}  
AUDIENCE: {config.audience_mindset}

CRITICAL REQUIREMENTS:
- Headlines: Exactly {config.fields['headlines'].count} headlines, each maximum {config.fields['headlines'].max_chars} characters
- Headlines MUST be completely unique - no duplicates or near-duplicates
- Descriptions: Exactly {config.fields['descriptions'].count} descriptions, each maximum {config.fields['descriptions'].max_chars} characters  
- CTA: Optional, maximum {config.fields['cta'].max_chars} characters
- {self.base_instructions['grammar']}
- {self.base_instructions['banned_phrases']}
- Include relevant keywords naturally
- Direct, clear value proposition
- Match search intent precisely

EXAMPLE OUTPUT FORMAT:
{json.dumps({
    "headlines": [
        "Professional Web Design Services",
        "Custom Websites Built Fast", 
        "Affordable Business Web Solutions"
    ],
    "descriptions": [
        "Get a stunning, mobile-friendly website designed by experts. Free consultation included.",
        "Boost your online presence with our proven web design process. Contact us today!"
    ],
    "cta": "Get Quote"
}, indent=2)}"""

        user_prompt = f"""Create Google Ads copy from this content:

ORIGINAL CONTENT:
{json.dumps(parsed_ad.content, indent=2)}

CONTEXT:
- Industry: {context.get('industry', 'general') if context else 'general'}
- Keywords: {context.get('keywords', 'relevant terms') if context else 'relevant terms'}
- Search Intent: {context.get('search_intent', 'solution-seeking') if context else 'solution-seeking'}

CREATE: Google Ads with 3 unique headlines, 2 descriptions, and optional CTA. Ensure headlines are completely different.
{self.base_instructions['format']}"""

        return {
            'system': system_prompt,
            'user': user_prompt
        }
    
    def _build_linkedin_prompt(self, config: PlatformConfig, parsed_ad: ParsedAd, context: Optional[Dict[str, Any]]) -> Dict[str, str]:
        """Build LinkedIn-specific prompt"""
        system_prompt = f"""You are a B2B marketing expert specializing in LinkedIn content that drives professional engagement.

PLATFORM: LinkedIn
TONE: {config.tone}
AUDIENCE: {config.audience_mindset}

STRICT REQUIREMENTS:
- Headline: Maximum {config.fields['headline'].max_chars} characters, professional and authoritative
- Body: Maximum {config.fields['body'].max_chars} characters, business-focused with clear ROI
- CTA: Maximum {config.fields['cta'].max_chars} characters, professional action language
- {self.base_instructions['grammar']}
- {self.base_instructions['banned_phrases']}  
- NO casual slang or informal language
- Emphasize business outcomes and professional growth
- Authority and expertise positioning

EXAMPLE OUTPUT FORMAT:
{json.dumps({
    "headline": "Accelerate Your Team's Productivity with Advanced Project Management Solutions", 
    "body": "Industry leaders are achieving 40% faster project completion with our enterprise platform. Streamline workflows, improve collaboration, and deliver results that matter to your bottom line.",
    "cta": "Request Demo"
}, indent=2)}"""

        user_prompt = f"""Transform this content for LinkedIn professionals:

ORIGINAL CONTENT:
{json.dumps(parsed_ad.content, indent=2)}

CONTEXT:
- Industry: {context.get('industry', 'B2B services') if context else 'B2B services'}
- Target Role: {context.get('target_role', 'business decision-makers') if context else 'business decision-makers'}  
- Business Value: {context.get('business_value', 'increased efficiency and ROI') if context else 'increased efficiency and ROI'}

CREATE: Professional LinkedIn content emphasizing business outcomes and authority.
{self.base_instructions['format']}"""

        return {
            'system': system_prompt,
            'user': user_prompt
        }
    
    def _build_twitter_x_prompt(self, config: PlatformConfig, parsed_ad: ParsedAd, context: Optional[Dict[str, Any]]) -> Dict[str, str]:
        """Build Twitter/X-specific prompt"""
        system_prompt = f"""You are a Twitter/X content strategist known for creating viral, engaging tweets that drive action.

PLATFORM: Twitter/X
TONE: {config.tone}
AUDIENCE: {config.audience_mindset}

STRICT REQUIREMENTS:  
- Body: Maximum {config.fields['body'].max_chars} characters total (including embedded CTA)
- CTA must be naturally embedded in the body text - no separate CTA field
- {self.base_instructions['grammar']}
- {self.base_instructions['banned_phrases']}
- Punchy, quotable, shareable content
- Quick attention grabbers that stop the scroll
- Conversational and authentic tone

EXAMPLE OUTPUT FORMAT:
{json.dumps({
    "body": "Just discovered this productivity hack that saves me 2 hours daily. Game changer for busy entrepreneurs. Try it free: [link] 🚀"
}, indent=2)}"""

        user_prompt = f"""Create a Twitter/X post from this content:

ORIGINAL CONTENT:
{json.dumps(parsed_ad.content, indent=2)}

CONTEXT:
- Industry: {context.get('industry', 'general') if context else 'general'}
- Audience Interest: {context.get('audience_interest', 'productivity and growth') if context else 'productivity and growth'}
- Viral Elements: {context.get('viral_elements', 'tips and insights') if context else 'tips and insights'}

CREATE: Concise, engaging Twitter/X post with embedded CTA under 280 characters.
{self.base_instructions['format']}"""

        return {
            'system': system_prompt,
            'user': user_prompt
        }
    
    def _build_tiktok_prompt(self, config: PlatformConfig, parsed_ad: ParsedAd, context: Optional[Dict[str, Any]]) -> Dict[str, str]:
        """Build TikTok-specific prompt"""
        system_prompt = f"""You are a TikTok content creator specializing in viral short-form content that drives engagement and action.

PLATFORM: TikTok
TONE: {config.tone} 
AUDIENCE: {config.audience_mindset}

STRICT REQUIREMENTS:
- Body: Maximum {config.fields['body'].max_chars} characters, energetic and scroll-stopping
- CTA: Maximum {config.fields['cta'].max_chars} characters, action-focused button text
- {self.base_instructions['grammar']}
- {self.base_instructions['banned_phrases']}
- Use Gen-Z language naturally (not forced or cringe)
- Entertainment-first approach with viral potential
- Hook that stops the scroll immediately

EXAMPLE OUTPUT FORMAT:
{json.dumps({
    "body": "POV: You found the productivity app that actually works 😱 No more endless to-do lists!",
    "cta": "Try Now"
}, indent=2)}"""

        user_prompt = f"""Create TikTok content from this:

ORIGINAL CONTENT:
{json.dumps(parsed_ad.content, indent=2)}

CONTEXT:
- Industry: {context.get('industry', 'general') if context else 'general'}
- Trend Element: {context.get('trend_element', 'life hacks') if context else 'life hacks'}  
- Hook Style: {context.get('hook_style', 'POV or surprising fact') if context else 'POV or surprising fact'}

CREATE: Short, energetic TikTok content with viral potential and clear CTA.
{self.base_instructions['format']}"""

        return {
            'system': system_prompt,
            'user': user_prompt
        }

def build_platform_prompt(platform_id: str, parsed_ad: ParsedAd, context: Optional[Dict[str, Any]] = None) -> Dict[str, str]:
    """Convenience function to build platform-specific prompt"""
    builder = PlatformPromptBuilder()
    return builder.build_prompt(platform_id, parsed_ad, context)