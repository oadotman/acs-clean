"""
Standardized API Response Formatter

Creates consistent API responses across all platforms while handling
platform-specific content structure differences.
"""
from typing import Dict, Any, List, Optional
from datetime import datetime
import logging

from .platform_registry import get_platform_config
from .content_validator import ValidationResult
from .platform_ad_generator import GenerationResult
from .variant_strategies import get_platform_strategies

logger = logging.getLogger(__name__)

class StandardizedResponseFormatter:
    """Formats API responses in a consistent structure across all platforms"""
    
    @staticmethod
    def create_standardized_response(
        platform_id: str,
        original_ad_copy: str,
        generation_result: GenerationResult,
        validation_result: ValidationResult,
        variants: List[Dict[str, Any]] = None,
        original_score: int = 65
    ) -> Dict[str, Any]:
        """Create standardized API response format"""
        
        # Calculate improved score based on validation
        improved_score = validation_result.confidence_score if validation_result else 70
        
        # Format content for display
        improved_ad = StandardizedResponseFormatter._format_platform_content(
            generation_result.generated_content, 
            platform_id
        )
        original_ad = StandardizedResponseFormatter._format_original_ad(
            original_ad_copy, 
            platform_id
        )
        
        # Format variants
        formatted_variants = StandardizedResponseFormatter._format_variants(
            variants or [], 
            platform_id
        )
        
        # Generate platform-specific tips
        tips = StandardizedResponseFormatter._generate_platform_tips(
            platform_id, 
            validation_result
        )
        
        # Build standardized response
        response = {
            "platform": platform_id,
            "originalScore": original_score,
            "improvedScore": improved_score,
            "confidenceScore": validation_result.confidence_score if validation_result else improved_score,
            "originalAd": original_ad,
            "improvedAd": improved_ad,
            "variants": formatted_variants,
            "tips": tips,
            "metadata": {
                "generatedAt": datetime.utcnow().isoformat(),
                "processingTime": generation_result.metrics.get('generation_time_ms', 0) if generation_result else 0,
                "retryCount": generation_result.metrics.get('retry_count', 0) if generation_result else 0,
                "validationPassed": validation_result.is_valid if validation_result else True,
                "qualityIssues": len(validation_result.quality_issues) if validation_result else 0,
                "platformOptimized": True
            }
        }
        
        return response
    
    @staticmethod
    def _format_platform_content(content: Dict[str, Any], platform_id: str) -> Dict[str, Any]:
        """Format content based on platform structure"""
        
        if platform_id == 'google_ads':
            # Google Ads: headline1, headline2, headline3, description1, description2
            headlines = content.get('headlines', ['', '', ''])
            descriptions = content.get('descriptions', ['', ''])
            
            # Ensure we have exactly 3 headlines and 2 descriptions
            while len(headlines) < 3:
                headlines.append('')
            while len(descriptions) < 2:
                descriptions.append('')
            
            return {
                "headline": None,  # No single headline for Google Ads
                "body": None,      # No single body for Google Ads
                "cta": content.get('cta', ''),
                "headline1": headlines[0],
                "headline2": headlines[1], 
                "headline3": headlines[2],
                "description1": descriptions[0],
                "description2": descriptions[1],
                "platform": platform_id
            }
        
        elif platform_id == 'instagram':
            # Instagram: body, hashtags array, optional cta
            return {
                "headline": None,  # Instagram doesn't use traditional headlines
                "body": content.get('body', ''),
                "cta": content.get('cta', ''),
                "hashtags": content.get('hashtags', []),
                "platform": platform_id
            }
        
        elif platform_id == 'twitter_x':
            # Twitter/X: single body with embedded CTA
            return {
                "headline": None,  # Twitter/X doesn't use headlines
                "body": content.get('body', ''),
                "cta": None,  # CTA is embedded in body
                "platform": platform_id
            }
        
        else:
            # Facebook, LinkedIn, TikTok: standard headline + body + cta
            return {
                "headline": content.get('headline', ''),
                "body": content.get('body', ''),
                "cta": content.get('cta', ''),
                "platform": platform_id
            }
    
    @staticmethod
    def _format_original_ad(original_text: str, platform_id: str) -> Dict[str, Any]:
        """Format original ad text into standardized structure"""
        
        if platform_id == 'google_ads':
            # For Google Ads, create simple structure from original
            return {
                "headline": None,
                "body": None,
                "cta": "",
                "headline1": original_text[:30] if len(original_text) > 30 else original_text,
                "headline2": "Quality Service",
                "headline3": "Get Started Today",
                "description1": original_text[:90] if len(original_text) > 90 else original_text,
                "description2": "Professional solutions for your needs.",
                "platform": platform_id
            }
        
        elif platform_id == 'instagram':
            return {
                "headline": None,
                "body": original_text,
                "cta": "",
                "hashtags": [],
                "platform": platform_id
            }
        
        elif platform_id == 'twitter_x':
            return {
                "headline": None,
                "body": original_text[:280],
                "cta": None,
                "platform": platform_id
            }
        
        else:
            # Standard format for Facebook, LinkedIn, TikTok
            # Simple parsing: first sentence as headline, rest as body
            sentences = [s.strip() for s in original_text.split('.') if s.strip()]
            headline = sentences[0] if sentences else original_text[:50]
            body = '. '.join(sentences[1:]) if len(sentences) > 1 else original_text
            
            return {
                "headline": headline,
                "body": body,
                "cta": "Learn More",
                "platform": platform_id
            }
    
    @staticmethod
    def _format_variants(variants: List[Dict[str, Any]], platform_id: str) -> List[Dict[str, Any]]:
        """Format variants into standardized structure"""
        formatted_variants = []
        
        # Get platform strategies for proper variant naming
        strategies = get_platform_strategies(platform_id)
        strategy_map = {s.version: s for s in strategies}
        
        for variant in variants:
            version = variant.get('version', 'A')
            strategy = strategy_map.get(version)
            
            # Format variant content using platform-specific structure
            variant_content = StandardizedResponseFormatter._format_platform_content(
                {k: v for k, v in variant.items() if k not in ['version', 'type', 'variant_label', 'variant_name', 'variant_description', 'char_counts', 'platform_id']},
                platform_id
            )
            
            formatted_variant = {
                "version": version,
                "focus": strategy.focus_type if strategy else variant.get('type', 'benefit_focused'),
                "name": strategy.name if strategy else variant.get('variant_name', f'Version {version}'),
                "description": strategy.description if strategy else variant.get('variant_description', ''),
                "bestFor": strategy.best_for if strategy else [],
                **variant_content  # Merge platform-specific content structure
            }
            
            formatted_variants.append(formatted_variant)
        
        # Ensure we always have exactly 3 variants
        while len(formatted_variants) < 3:
            version = chr(65 + len(formatted_variants))  # A, B, C
            strategy = strategy_map.get(version)
            
            # Create fallback variant
            fallback_content = formatted_variants[0] if formatted_variants else StandardizedResponseFormatter._format_platform_content({}, platform_id)
            
            formatted_variants.append({
                "version": version,
                "focus": strategy.focus_type if strategy else "benefit_focused",
                "name": strategy.name if strategy else f"Version {version}",
                "description": strategy.description if strategy else f"Variant {version} approach",
                "bestFor": strategy.best_for if strategy else [],
                **fallback_content
            })
        
        return formatted_variants[:3]  # Ensure exactly 3 variants
    
    @staticmethod
    def _generate_platform_tips(platform_id: str, validation_result: Optional[ValidationResult]) -> str:
        """Generate platform-specific improvement tips"""
        
        config = get_platform_config(platform_id)
        if not config:
            return "Focus on clear, compelling copy that drives action."
        
        tips = []
        
        # Platform-specific base tips
        platform_tips = {
            'facebook': [
                "Use conversational tone that encourages community engagement",
                "Include social proof like customer counts or testimonials",
                "Keep headlines under 40 characters for maximum impact"
            ],
            'instagram': [
                "Make the first 125 characters compelling to hook viewers",
                "Use 5-10 relevant hashtags to increase discoverability", 
                "Focus on visual storytelling and lifestyle benefits"
            ],
            'google_ads': [
                "Create 3 unique headlines that target different search intents",
                "Include relevant keywords naturally in your copy",
                "Write clear, direct descriptions that match search queries"
            ],
            'linkedin': [
                "Use professional language and focus on business outcomes",
                "Emphasize ROI, efficiency, and competitive advantages",
                "Target decision-makers with authority-building content"
            ],
            'twitter_x': [
                "Keep total character count under 280 including CTA",
                "Write punchy, quotable content that sparks conversation",
                "Embed your call-to-action naturally in the message"
            ],
            'tiktok': [
                "Use energetic, Gen-Z friendly language and current trends",
                "Create scroll-stopping hooks in the first few words",
                "Keep body text under 100 characters for maximum impact"
            ]
        }
        
        tips.extend(platform_tips.get(platform_id, ["Create clear, compelling copy for your audience"]))
        
        # Add validation-based tips
        if validation_result:
            if validation_result.platform_specific_issues:
                tips.append("Address platform-specific requirements highlighted in validation")
            
            if validation_result.template_phrases_found:
                tips.append("Avoid generic template phrases - use original, specific language")
            
            if validation_result.confidence_score < 80:
                tips.append("Focus on improving content quality and originality for better engagement")
        
        return " | ".join(tips[:3])  # Limit to top 3 tips

# Convenience function
def format_standardized_response(
    platform_id: str,
    original_ad_copy: str,
    generation_result: GenerationResult,
    validation_result: ValidationResult = None,
    variants: List[Dict[str, Any]] = None,
    original_score: int = 65
) -> Dict[str, Any]:
    """Create standardized response format"""
    return StandardizedResponseFormatter.create_standardized_response(
        platform_id=platform_id,
        original_ad_copy=original_ad_copy,
        generation_result=generation_result,
        validation_result=validation_result,
        variants=variants,
        original_score=original_score
    )