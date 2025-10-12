"""
Advanced Variant Generation System - Phase 4 & 5

This service creates multiple ad copy versions with different creative approaches,
emotional tones, and urgency levels. Includes side-by-side comparison and 
mix-and-match functionality for optimal creative testing.
"""

import asyncio
import time
import logging
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from enum import Enum

from app.services.production_ai_generator import ProductionAIService
from app.services.cliche_filter import ClicheFilter
from app.constants.creative_controls import (
    CreativityLevel, UrgencyLevel, EmotionType,
    get_creativity_description, get_urgency_description,
    analyze_creative_risk, get_emotion_config
)
from app.constants.platform_limits import (
    get_platform_creativity_config, get_emotion_platform_compatibility,
    Platform
)
from app.core.exceptions import ProductionError, AIProviderUnavailable

logger = logging.getLogger(__name__)

class VariantStrategy(str, Enum):
    """Different strategies for generating creative variants"""
    DIVERSE = "diverse"           # Mix different creativity/urgency/emotion combinations
    PROGRESSIVE = "progressive"   # Gradually increase creativity/urgency from safe to bold
    EMOTIONAL_RANGE = "emotional_range"  # Same creativity/urgency, different emotions
    CREATIVITY_SPECTRUM = "creativity_spectrum"  # Same emotion, different creativity levels
    URGENCY_SCALE = "urgency_scale"  # Same emotion/creativity, different urgency

@dataclass
class VariantConfig:
    """Configuration for a single variant"""
    creativity_level: int
    urgency_level: int
    emotion_type: EmotionType
    filter_cliches: bool
    variant_name: str
    strategy_description: str
    risk_level: str = "Medium"

@dataclass
class VariantComparison:
    """Side-by-side comparison data for variants"""
    variant_id: str
    headline: str
    body_text: str
    cta: str
    creativity_score: int
    urgency_score: int
    emotion_type: str
    character_count: int
    readability_score: Optional[float] = None
    cliche_count: int = 0
    risk_assessment: str = "Medium"
    platform_compatibility: str = "Good"

class VariantGenerator:
    """
    Advanced variant generation system for Phase 4 & 5 creative controls
    
    Features:
    - Multiple generation strategies
    - Side-by-side comparison
    - Mix-and-match functionality
    - Creative risk analysis
    - Platform compatibility checking
    - Cliché filtering and analysis
    """
    
    def __init__(self, ai_service: ProductionAIService):
        self.ai_service = ai_service
        self.cliche_filter = ClicheFilter()
        logger.info("VariantGenerator initialized with advanced creative controls")
    
    async def generate_variant_set(
        self,
        ad_data: Dict,
        strategy: VariantStrategy = VariantStrategy.DIVERSE,
        num_variants: int = 3,
        base_creativity: int = 5,
        base_urgency: int = 5,
        base_emotion: EmotionType = EmotionType.INSPIRING,
        variant_type: str = "persuasive",
        **generation_kwargs
    ) -> Dict[str, Any]:
        """
        Generate a complete set of variants using specified strategy
        
        Returns comprehensive data for side-by-side comparison and analysis
        """
        
        if num_variants < 1 or num_variants > 5:
            raise ProductionError(
                "Invalid variant count",
                "INVALID_VARIANT_COUNT",
                {"requested": num_variants, "max_allowed": 5}
            )
        
        platform = ad_data.get('platform', 'facebook')
        platform_config = get_platform_creativity_config(platform)
        
        logger.info(f"Generating {num_variants} variants using {strategy.value} strategy for {platform}")
        
        # Generate variant configurations based on strategy
        variant_configs = self._create_variant_configs(
            strategy, num_variants, base_creativity, base_urgency, 
            base_emotion, platform, platform_config
        )
        
        # Generate all variants in parallel
        generation_tasks = []
        for config in variant_configs:
            task = self._generate_single_variant(
                ad_data, config, variant_type, **generation_kwargs
            )
            generation_tasks.append(task)
        
        try:
            variant_results = await asyncio.gather(*generation_tasks, return_exceptions=True)
        except Exception as e:
            raise AIProviderUnavailable(
                "variant_set_generation",
                f"Failed to generate variant set: {str(e)}"
            )
        
        # Process results and create comparison data
        successful_variants = []
        failed_variants = []
        
        for i, result in enumerate(variant_results):
            if isinstance(result, Exception):
                failed_variants.append({
                    "variant_name": variant_configs[i].variant_name,
                    "error": str(result)
                })
                logger.warning(f"Failed to generate {variant_configs[i].variant_name}: {result}")
            else:
                successful_variants.append(result)
        
        if not successful_variants:
            raise AIProviderUnavailable(
                "variant_set_generation",
                f"All variants failed to generate. Errors: {failed_variants}"
            )
        
        # Create comprehensive comparison data
        variant_set = await self._create_variant_comparison_set(
            successful_variants, ad_data, strategy, variant_configs
        )
        
        logger.info(f"Successfully generated {len(successful_variants)}/{num_variants} variants")
        return variant_set
    
    def _create_variant_configs(
        self,
        strategy: VariantStrategy,
        num_variants: int,
        base_creativity: int,
        base_urgency: int,
        base_emotion: EmotionType,
        platform: str,
        platform_config: Dict[str, Any]
    ) -> List[VariantConfig]:
        """Create variant configurations based on generation strategy"""
        
        configs = []
        
        if strategy == VariantStrategy.DIVERSE:
            # Mix different combinations for maximum variety
            emotions = [base_emotion, EmotionType.TRUST_BUILDING, EmotionType.EXCITEMENT, EmotionType.PROBLEM_SOLVING, EmotionType.CURIOSITY]
            
            for i in range(num_variants):
                creativity = min(10, max(0, base_creativity + (i - 1) * 2))
                urgency = min(10, max(0, base_urgency + ((i % 2) * 3 - 1)))
                emotion = emotions[i % len(emotions)]
                
                config = VariantConfig(
                    creativity_level=creativity,
                    urgency_level=urgency,
                    emotion_type=emotion,
                    filter_cliches=True,
                    variant_name=f"Diverse Mix {i+1}",
                    strategy_description=f"C{creativity}/U{urgency}/{emotion.value}"
                )
                configs.append(config)
        
        elif strategy == VariantStrategy.PROGRESSIVE:
            # Gradually increase intensity from safe to bold
            max_safe_creativity = platform_config.get("max_safe_creativity", 7)
            creativity_range = max_safe_creativity - 2  # Start 2 levels below max safe
            
            for i in range(num_variants):
                creativity = min(10, 2 + (creativity_range * i // (num_variants - 1)))
                urgency = min(10, 2 + (6 * i // (num_variants - 1)))
                
                config = VariantConfig(
                    creativity_level=creativity,
                    urgency_level=urgency,
                    emotion_type=base_emotion,
                    filter_cliches=i < num_variants - 1,  # Last variant allows some clichés
                    variant_name=f"Progressive {i+1}" + (" (Safe)" if i == 0 else " (Bold)" if i == num_variants - 1 else " (Balanced)"),
                    strategy_description=f"Progressive C{creativity}/U{urgency}"
                )
                configs.append(config)
        
        elif strategy == VariantStrategy.EMOTIONAL_RANGE:
            # Same creativity/urgency, different emotions
            emotions = [EmotionType.INSPIRING, EmotionType.TRUST_BUILDING, EmotionType.EXCITEMENT, 
                       EmotionType.PROBLEM_SOLVING, EmotionType.CURIOSITY]
            
            for i in range(min(num_variants, len(emotions))):
                config = VariantConfig(
                    creativity_level=base_creativity,
                    urgency_level=base_urgency,
                    emotion_type=emotions[i],
                    filter_cliches=True,
                    variant_name=f"{emotions[i].value.title()} Focus",
                    strategy_description=f"Emotional: {emotions[i].value}"
                )
                configs.append(config)
        
        elif strategy == VariantStrategy.CREATIVITY_SPECTRUM:
            # Same emotion/urgency, different creativity levels
            min_creativity = max(0, base_creativity - 2)
            max_creativity = min(10, base_creativity + 2)
            
            for i in range(num_variants):
                creativity = min_creativity + (max_creativity - min_creativity) * i // (num_variants - 1)
                creativity_desc = get_creativity_description(creativity).split(" - ")[0]
                
                config = VariantConfig(
                    creativity_level=creativity,
                    urgency_level=base_urgency,
                    emotion_type=base_emotion,
                    filter_cliches=creativity < 7,  # More creative variants allow some flexibility
                    variant_name=f"{creativity_desc} Style",
                    strategy_description=f"Creativity Spectrum: {creativity}/10"
                )
                configs.append(config)
        
        elif strategy == VariantStrategy.URGENCY_SCALE:
            # Same emotion/creativity, different urgency levels
            min_urgency = max(0, base_urgency - 2)
            max_urgency = min(10, base_urgency + 3)
            
            for i in range(num_variants):
                urgency = min_urgency + (max_urgency - min_urgency) * i // (num_variants - 1)
                urgency_desc = get_urgency_description(urgency).split(" - ")[0]
                
                config = VariantConfig(
                    creativity_level=base_creativity,
                    urgency_level=urgency,
                    emotion_type=base_emotion,
                    filter_cliches=True,
                    variant_name=f"{urgency_desc} Urgency",
                    strategy_description=f"Urgency Scale: {urgency}/10"
                )
                configs.append(config)
        
        # Analyze risk for each config
        for config in configs:
            risk_analysis = analyze_creative_risk(
                config.creativity_level, config.urgency_level,
                config.emotion_type, platform
            )
            config.risk_level = risk_analysis["risk_level"]
        
        return configs
    
    async def _generate_single_variant(
        self,
        ad_data: Dict,
        config: VariantConfig,
        variant_type: str,
        **generation_kwargs
    ) -> Dict[str, Any]:
        """Generate a single variant with given configuration"""
        
        try:
            result = await self.ai_service.generate_ad_alternative(
                ad_data=ad_data,
                variant_type=variant_type,
                creativity_level=config.creativity_level,
                urgency_level=config.urgency_level,
                emotion_type=config.emotion_type.value,
                filter_cliches=config.filter_cliches,
                **generation_kwargs
            )
            
            # Add variant configuration metadata
            result.update({
                "variant_config": asdict(config),
                "generation_strategy": config.strategy_description,
                "variant_name": config.variant_name,
                "risk_level": config.risk_level
            })
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to generate variant {config.variant_name}: {e}")
            raise
    
    async def _create_variant_comparison_set(
        self,
        variants: List[Dict],
        ad_data: Dict,
        strategy: VariantStrategy,
        original_configs: List[VariantConfig]
    ) -> Dict[str, Any]:
        """Create comprehensive comparison data for variants"""
        
        platform = ad_data.get('platform', 'facebook')
        
        # Create comparison objects for each variant
        comparisons = []
        
        for i, variant in enumerate(variants):
            # Analyze clichés
            cliche_analysis = await self.cliche_filter.analyze_copy_originality(
                variant.get('headline', '') + ' ' + variant.get('body_text', '')
            )
            
            # Get platform compatibility
            emotion_type = variant.get('variant_config', {}).get('emotion_type', 'inspiring')
            try:
                emotion_enum = EmotionType(emotion_type)
                emotion_compatibility = get_emotion_platform_compatibility(emotion_enum)
                platform_compat = emotion_compatibility.get(platform, "Good")
            except (ValueError, AttributeError):
                platform_compat = "Good"
            
            comparison = VariantComparison(
                variant_id=f"variant_{i+1}",
                headline=variant.get('headline', ''),
                body_text=variant.get('body_text', ''),
                cta=variant.get('cta', ''),
                creativity_score=variant.get('variant_config', {}).get('creativity_level', 5),
                urgency_score=variant.get('variant_config', {}).get('urgency_level', 5),
                emotion_type=emotion_type,
                character_count=len(variant.get('headline', '') + variant.get('body_text', '') + variant.get('cta', '')),
                cliche_count=len(cliche_analysis.get('cliches_found', [])),
                risk_assessment=variant.get('risk_level', 'Medium'),
                platform_compatibility=platform_compat
            )
            
            comparisons.append(comparison)
        
        # Calculate comparison metrics
        comparison_metrics = self._calculate_comparison_metrics(comparisons)
        
        # Create recommendations
        recommendations = self._generate_variant_recommendations(
            comparisons, platform, strategy
        )
        
        return {
            "strategy_used": strategy.value,
            "platform": platform,
            "total_variants": len(variants),
            "generation_timestamp": time.time(),
            "variants": variants,
            "comparisons": [asdict(comp) for comp in comparisons],
            "metrics": comparison_metrics,
            "recommendations": recommendations,
            "mix_and_match": self._create_mix_and_match_suggestions(variants, comparisons)
        }
    
    def _calculate_comparison_metrics(self, comparisons: List[VariantComparison]) -> Dict[str, Any]:
        """Calculate metrics for comparing variants"""
        
        creativity_scores = [comp.creativity_score for comp in comparisons]
        urgency_scores = [comp.urgency_score for comp in comparisons]
        character_counts = [comp.character_count for comp in comparisons]
        cliche_counts = [comp.cliche_count for comp in comparisons]
        
        return {
            "creativity_range": {
                "min": min(creativity_scores),
                "max": max(creativity_scores),
                "average": sum(creativity_scores) / len(creativity_scores)
            },
            "urgency_range": {
                "min": min(urgency_scores),
                "max": max(urgency_scores),
                "average": sum(urgency_scores) / len(urgency_scores)
            },
            "length_analysis": {
                "shortest": min(character_counts),
                "longest": max(character_counts),
                "average": sum(character_counts) / len(character_counts)
            },
            "originality_analysis": {
                "most_original": min(cliche_counts),
                "least_original": max(cliche_counts),
                "average_cliches": sum(cliche_counts) / len(cliche_counts)
            },
            "risk_distribution": {
                risk: len([c for c in comparisons if c.risk_assessment == risk])
                for risk in ["Low", "Medium", "High"]
            }
        }
    
    def _generate_variant_recommendations(
        self,
        comparisons: List[VariantComparison],
        platform: str,
        strategy: VariantStrategy
    ) -> List[str]:
        """Generate recommendations for variant selection and optimization"""
        
        recommendations = []
        
        # Find safest and boldest variants
        creativity_scores = [(i, comp.creativity_score) for i, comp in enumerate(comparisons)]
        safest_idx = min(creativity_scores, key=lambda x: x[1])[0]
        boldest_idx = max(creativity_scores, key=lambda x: x[1])[0]
        
        recommendations.append(f"Safest option: '{comparisons[safest_idx].variant_id}' - Good for conservative audiences or first-time testing")
        recommendations.append(f"Boldest option: '{comparisons[boldest_idx].variant_id}' - Best for grabbing attention, but test with smaller audiences first")
        
        # Originality recommendations
        cliche_scores = [(i, comp.cliche_count) for i, comp in enumerate(comparisons)]
        most_original_idx = min(cliche_scores, key=lambda x: x[1])[0]
        
        if comparisons[most_original_idx].cliche_count == 0:
            recommendations.append(f"Most original: '{comparisons[most_original_idx].variant_id}' - Zero marketing clichés detected")
        
        # Length recommendations based on platform
        lengths = [(i, comp.character_count) for i, comp in enumerate(comparisons)]
        platform_limits = {"twitter": 280, "tiktok": 100, "facebook": 125, "instagram": 2200, "linkedin": 3000}
        platform_limit = platform_limits.get(platform, 125)
        
        optimal_length_variants = [(i, length) for i, length in lengths if length <= platform_limit * 0.8]
        if optimal_length_variants:
            best_length_idx = min(optimal_length_variants, key=lambda x: abs(x[1] - platform_limit * 0.6))[0]
            recommendations.append(f"Optimal length: '{comparisons[best_length_idx].variant_id}' - Best fits {platform} character recommendations")
        
        # Strategy-specific recommendations
        if strategy == VariantStrategy.PROGRESSIVE:
            recommendations.append("Progressive strategy: Test the safest variant first, then scale up if it performs well")
        elif strategy == VariantStrategy.DIVERSE:
            recommendations.append("Diverse strategy: A/B test multiple variants simultaneously to find your audience's preference")
        elif strategy == VariantStrategy.EMOTIONAL_RANGE:
            recommendations.append("Emotional strategy: Each variant targets different emotional triggers - ideal for audience segmentation")
        
        return recommendations
    
    def _create_mix_and_match_suggestions(
        self,
        variants: List[Dict],
        comparisons: List[VariantComparison]
    ) -> Dict[str, Any]:
        """Create mix-and-match suggestions for combining best elements"""
        
        # Find best headline, body, and CTA across variants
        best_elements = {
            "headlines": [],
            "bodies": [],
            "ctas": []
        }
        
        for i, variant in enumerate(variants):
            best_elements["headlines"].append({
                "text": variant.get('headline', ''),
                "source_variant": comparisons[i].variant_id,
                "creativity_level": comparisons[i].creativity_score,
                "character_count": len(variant.get('headline', ''))
            })
            
            best_elements["bodies"].append({
                "text": variant.get('body_text', ''),
                "source_variant": comparisons[i].variant_id,
                "urgency_level": comparisons[i].urgency_score,
                "character_count": len(variant.get('body_text', ''))
            })
            
            best_elements["ctas"].append({
                "text": variant.get('cta', ''),
                "source_variant": comparisons[i].variant_id,
                "emotion_type": comparisons[i].emotion_type,
                "character_count": len(variant.get('cta', ''))
            })
        
        # Create combination suggestions
        combinations = []
        
        # High-impact combination: Most creative headline + Most urgent body + Most emotional CTA
        creative_headline = max(best_elements["headlines"], key=lambda x: x["creativity_level"])
        urgent_body = max(best_elements["bodies"], key=lambda x: x["urgency_level"])
        emotional_cta = best_elements["ctas"][0]  # Could be enhanced with emotion scoring
        
        combinations.append({
            "name": "High-Impact Mix",
            "description": "Most creative headline with most urgent body",
            "headline": creative_headline,
            "body": urgent_body,
            "cta": emotional_cta,
            "total_length": creative_headline["character_count"] + urgent_body["character_count"] + emotional_cta["character_count"]
        })
        
        # Balanced combination: Medium creativity across all elements
        balanced_elements = {
            "headline": sorted(best_elements["headlines"], key=lambda x: x["creativity_level"])[len(best_elements["headlines"])//2],
            "body": sorted(best_elements["bodies"], key=lambda x: x["urgency_level"])[len(best_elements["bodies"])//2],
            "cta": best_elements["ctas"][len(best_elements["ctas"])//2]
        }
        
        combinations.append({
            "name": "Balanced Mix",
            "description": "Moderate creativity and urgency for broad appeal",
            "headline": balanced_elements["headline"],
            "body": balanced_elements["body"],
            "cta": balanced_elements["cta"],
            "total_length": sum([elem["character_count"] for elem in balanced_elements.values()])
        })
        
        return {
            "available_elements": best_elements,
            "suggested_combinations": combinations,
            "mix_instructions": [
                "Test different combinations to find optimal performance",
                "Consider platform-specific character limits when mixing",
                "Maintain consistent emotion/tone when combining elements",
                "A/B test mixed versions against original variants"
            ]
        }
    
    async def analyze_variant_performance_potential(
        self,
        variants: List[Dict],
        platform: str,
        target_audience: str = None
    ) -> Dict[str, Any]:
        """Analyze potential performance of variants based on platform and audience"""
        
        # This would integrate with analytics in a full implementation
        # For now, provide predictive analysis based on creative settings
        
        platform_config = get_platform_creativity_config(platform)
        
        performance_predictions = []
        
        for i, variant in enumerate(variants):
            config = variant.get('variant_config', {})
            creativity = config.get('creativity_level', 5)
            urgency = config.get('urgency_level', 5)
            emotion = config.get('emotion_type', 'inspiring')
            
            # Calculate compatibility scores
            creativity_compat = 100 - abs(creativity - platform_config.get('recommended_creativity', 5)) * 10
            urgency_compat = 100 - abs(urgency - platform_config.get('recommended_urgency', 5)) * 10
            
            # Emotion compatibility
            preferred_emotions = platform_config.get('preferred_emotions', [])
            emotion_compat = 90 if any(e.value == emotion for e in preferred_emotions) else 60
            
            overall_score = (creativity_compat + urgency_compat + emotion_compat) / 3
            
            prediction = {
                "variant_id": f"variant_{i+1}",
                "predicted_performance_score": round(overall_score, 1),
                "creativity_platform_fit": round(creativity_compat, 1),
                "urgency_platform_fit": round(urgency_compat, 1),
                "emotion_platform_fit": round(emotion_compat, 1),
                "recommended_for": self._get_audience_recommendations(creativity, urgency, emotion),
                "testing_priority": "High" if overall_score > 80 else "Medium" if overall_score > 60 else "Low"
            }
            
            performance_predictions.append(prediction)
        
        # Sort by predicted performance
        performance_predictions.sort(key=lambda x: x["predicted_performance_score"], reverse=True)
        
        return {
            "platform": platform,
            "analysis_timestamp": time.time(),
            "predictions": performance_predictions,
            "top_performer": performance_predictions[0] if performance_predictions else None,
            "testing_recommendations": self._create_testing_strategy(performance_predictions),
            "disclaimer": "Predictions based on platform compatibility analysis. Actual performance may vary and should be validated through A/B testing."
        }
    
    def _get_audience_recommendations(self, creativity: int, urgency: int, emotion: str) -> List[str]:
        """Get audience type recommendations based on creative settings"""
        
        recommendations = []
        
        if creativity <= 3 and urgency <= 3:
            recommendations.append("Conservative audiences")
            recommendations.append("B2B decision makers")
            recommendations.append("Risk-averse segments")
        elif creativity >= 7 and urgency >= 7:
            recommendations.append("Young demographics")
            recommendations.append("Early adopters")
            recommendations.append("Impulse buyers")
        else:
            recommendations.append("General audiences")
            recommendations.append("Mixed demographics")
        
        if emotion in ["trust_building", "problem_solving"]:
            recommendations.append("Professional audiences")
        elif emotion in ["excitement", "curiosity"]:
            recommendations.append("Engagement-focused audiences")
        elif emotion == "inspiring":
            recommendations.append("Aspiration-driven audiences")
        
        return recommendations
    
    def _create_testing_strategy(self, predictions: List[Dict]) -> List[str]:
        """Create A/B testing strategy recommendations"""
        
        strategies = []
        
        if len(predictions) >= 3:
            top_three = predictions[:3]
            strategies.append(f"Start with 3-way A/B test using top performers: {', '.join([p['variant_id'] for p in top_three])}")
        
        high_priority = [p for p in predictions if p["testing_priority"] == "High"]
        if len(high_priority) >= 2:
            strategies.append("Focus initial testing budget on high-priority variants")
        
        strategies.extend([
            "Run tests for at least 7 days to account for weekly patterns",
            "Monitor both engagement metrics and conversion rates",
            "Consider different audience segments for each variant",
            "Scale successful variants gradually to larger audiences"
        ])
        
        return strategies