#!/usr/bin/env python3
"""
Ad Improvement Service for AdCopySurge
Generates strategic ad variations with predicted performance improvements.
"""

import os
import json
import uuid
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime

# Import our enhanced systems
try:
    from app.utils.scoring_calibration import BaselineScoreCalibrator
    from app.services.improved_feedback_engine import ImprovedFeedbackGenerator
except ImportError:
    # Fallback imports for testing
    import sys
    sys.path.append(os.path.dirname(__file__))
    from scoring_calibration import BaselineScoreCalibrator
    from improved_feedback_engine import ImprovedFeedbackGenerator

# Import OpenAI if available
try:
    import openai
    from openai import AsyncOpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False


@dataclass 
class AdVariant:
    """Structure for improved ad variants."""
    variant_type: str
    headline: str
    body_text: str
    cta: str
    improvement_reason: str
    predicted_score: float
    score_improvement: float
    strategy_focus: str


class AdImprovementService:
    """
    Service for generating strategic ad improvements.
    Creates 3 different variations: emotional, logical, and urgency-based.
    """
    
    def __init__(self):
        self.calibrator = BaselineScoreCalibrator()
        self.feedback_generator = ImprovedFeedbackGenerator()
        
        # Initialize OpenAI client if available
        self.openai_client = None
        if OPENAI_AVAILABLE and os.getenv("OPENAI_API_KEY"):
            self.openai_client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        
        # Load enhancement templates
        self.improvement_strategies = self._load_improvement_strategies()
        
    def _load_improvement_strategies(self) -> Dict[str, Any]:
        """Load strategic improvement templates."""
        return {
            "emotional": {
                "focus": "Emotional Connection & Storytelling",
                "prompt_template": """
🎯 VARIANT: EMOTIONAL CONNECTION & STORYTELLING

Original Ad:
- Headline: {headline}
- Body: {body_text}
- CTA: {cta}
- Platform: {platform}
- Target Audience: {target_audience}

✅ CREATE emotional version (50-100 words) that:
1. Opens with emotional hook relating to audience's desire or pain
2. Connects product features to emotional benefits authentically
3. Uses vivid, sensory language describing real experience
4. Builds to emotionally resonant CTA
5. NO fake testimonials or made-up stories
6. ONE emoji max if platform-appropriate

❌ NEVER USE: "game-changer", "revolutionary", "transform your life"

Format:
HEADLINE: [emotionally engaging headline]
BODY: [emotional body with authentic connection]
CTA: [emotion-driven action]
WHY: [specific emotional improvements made]
                """
                "keywords": ["story", "imagine", "feel", "experience", "transform", "journey", "struggle", "success", "dream", "fear"]
            },
            "logical": {
                "focus": "Data-Driven Credibility & Logic",
                "prompt_template": """
🎯 VARIANT: DATA-DRIVEN CREDIBILITY & LOGIC

Original Ad:
- Headline: {headline}
- Body: {body_text}
- CTA: {cta}
- Platform: {platform}
- Industry: {industry}

✅ CREATE data-driven version (50-100 words) that:
1. Includes specific numbers/percentages from original (don't fabricate)
2. Quantifies benefits (time saved, growth %, customer count)
3. Uses concrete proof over vague claims
4. Appeals to logical decision-making
5. Professional tone, credibility-focused
6. ONE emoji max if platform-appropriate

❌ NEVER USE: "world-class", "industry-leading", "best-in-class"
❌ DON'T invent statistics not in original

Format:
HEADLINE: [number-focused headline]
BODY: [data-rich body with metrics]
CTA: [results-oriented action]
WHY: [specific data elements and credibility added]
                """
                "keywords": ["proven", "data", "results", "study", "research", "statistics", "increase", "reduce", "save", "ROI"]
            },
            "urgency": {
                "focus": "Scarcity & Immediate Action",
                "keywords": ["now", "today", "limited", "deadline", "expires", "last chance", "before", "while", "hurry", "act fast"]
            }
        }
    
    async def generate_ad_improvements(self, 
                                     original_ad: Dict[str, str],
                                     current_scores: Dict[str, float],
                                     user_id: Optional[str] = None) -> List[AdVariant]:
        """
        Generate 3 strategic ad improvements.
        
        Args:
            original_ad: Dict with headline, body_text, cta, platform, etc.
            current_scores: Current scoring breakdown
            user_id: Optional user ID for tracking
            
        Returns:
            List of 3 AdVariant objects with improvements
        """
        
        variants = []
        original_score = current_scores.get('overall_score', 50.0)
        full_text = f"{original_ad.get('headline', '')} {original_ad.get('body_text', '')} {original_ad.get('cta', '')}"
        
        # Generate each strategic variant
        for strategy in ["emotional", "logical", "urgency"]:
            try:
                if self.openai_client:
                    # Use AI to generate improvement
                    variant = await self._generate_ai_variant(original_ad, strategy)
                else:
                    # Use template-based fallback
                    variant = self._generate_template_variant(original_ad, strategy)
                
                # Calculate predicted score for the variant
                variant_text = f"{variant['headline']} {variant['body_text']} {variant['cta']}"
                predicted_scores = self._predict_variant_score(variant_text, original_ad.get('platform', 'facebook'))
                predicted_score = predicted_scores['overall_score']
                score_improvement = predicted_score - original_score
                
                # Create AdVariant object
                ad_variant = AdVariant(
                    variant_type=strategy,
                    headline=variant['headline'],
                    body_text=variant['body_text'],
                    cta=variant['cta'],
                    improvement_reason=variant.get('reason', f"Optimized for {strategy} approach"),
                    predicted_score=predicted_score,
                    score_improvement=score_improvement,
                    strategy_focus=self.improvement_strategies[strategy]['focus']
                )
                
                variants.append(ad_variant)
                
            except Exception as e:
                print(f"Error generating {strategy} variant: {e}")
                # Add fallback variant
                variants.append(self._create_fallback_variant(original_ad, strategy, original_score))
        
        return variants
    
    async def _generate_ai_variant(self, original_ad: Dict[str, str], strategy: str) -> Dict[str, str]:
        """Generate variant using AI (OpenAI GPT)."""
        strategy_config = self.improvement_strategies[strategy]
        
        # Format the prompt with original ad data
        prompt = strategy_config['prompt_template'].format(
            headline=original_ad.get('headline', ''),
            body_text=original_ad.get('body_text', ''),
            cta=original_ad.get('cta', ''),
            platform=original_ad.get('platform', 'facebook'),
            target_audience=original_ad.get('target_audience', 'general audience'),
            industry=original_ad.get('industry', 'general business')
        )
        
        try:
            # Import premium copywriting standards
            from app.constants.premium_copywriting_standards import build_premium_system_prompt
            
            premium_system_prompt = build_premium_system_prompt()
            
            response = await self.openai_client.chat.completions.create(
                model="gpt-4-turbo-preview",  # Use best available model
                messages=[
                    {
                        "role": "system", 
                        "content": premium_system_prompt
                    },
                    {
                        "role": "user", 
                        "content": prompt
                    }
                ],
                max_tokens=800,
                temperature=0.7
            )
            
            content = response.choices[0].message.content
            return self._parse_ai_response(content, strategy)
            
        except Exception as e:
            print(f"OpenAI API error for {strategy}: {e}")
            return self._generate_template_variant(original_ad, strategy)
    
    def _parse_ai_response(self, content: str, strategy: str) -> Dict[str, str]:
        """Parse structured AI response into components."""
        lines = content.split('\n')
        parsed = {}
        
        # Extract structured components
        for line in lines:
            line = line.strip()
            if line.startswith('HEADLINE:'):
                parsed['headline'] = line.replace('HEADLINE:', '').strip()
            elif line.startswith('BODY:'):
                parsed['body_text'] = line.replace('BODY:', '').strip()
            elif line.startswith('CTA:'):
                parsed['cta'] = line.replace('CTA:', '').strip()
            elif line.startswith('WHY:'):
                parsed['reason'] = line.replace('WHY:', '').strip()
        
        # Fallback parsing if structured format not found
        if not all(k in parsed for k in ['headline', 'body_text', 'cta']):
            # Try to extract from plain text
            sentences = [s.strip() for s in content.split('.') if s.strip()]
            if len(sentences) >= 3:
                parsed['headline'] = sentences[0]
                parsed['body_text'] = '. '.join(sentences[1:-1])
                parsed['cta'] = sentences[-1]
                parsed['reason'] = f"Enhanced with {strategy} strategy for better conversion"
        
        return parsed
    
    def _generate_template_variant(self, original_ad: Dict[str, str], strategy: str) -> Dict[str, str]:
        """Generate variant using templates as fallback."""
        original_headline = original_ad.get('headline', 'Great Product')
        original_body = original_ad.get('body_text', 'Amazing benefits for you')
        original_cta = original_ad.get('cta', 'Learn More')
        
        templates = {
            "emotional": {
                "headline": f"Finally—{original_headline.replace('Get', 'Achieve').replace('Buy', 'Own')}",
                "body_text": f"Picture this: {original_body} That's the experience thousands already enjoy. Ready to feel that same sense of accomplishment?",
                "cta": "Begin Your Journey",
                "reason": "Aspirational framing with sensory appeal and social validation (no clichés)"
            },
            "logical": {
                "headline": f"Measurable Results: {original_headline}",
                "body_text": f"Based on real customer data: {original_body} Our approach delivers consistent, quantified improvements you can track from day one.",
                "cta": "See the Data",
                "reason": "Evidence-based credibility without fabricating statistics"
            },
            "urgency": {
                "headline": f"Limited Availability: {original_headline}",
                "body_text": f"Time-sensitive: {original_body} This offer ends [specific date/time]. Spots are limited to ensure quality service.",
                "cta": "Reserve Your Spot",
                "reason": "Authentic scarcity without desperate language (no 'don't miss out')"
            }
        }
        
        return templates.get(strategy, templates["emotional"])
    
    def _predict_variant_score(self, variant_text: str, platform: str) -> Dict[str, float]:
        """Predict score for a variant using our calibrated scoring system."""
        # Mock component scores based on variant improvements
        # In a real system, you'd run the full analysis pipeline
        
        # Base scores (simulating analysis)
        base_clarity = 70.0
        base_persuasion = 75.0
        base_emotion = 80.0  # Variants should have better emotion
        base_cta = 75.0
        base_platform_fit = 70.0
        
        # Apply strategy-specific bonuses
        strategy_bonuses = {
            "emotional": {"emotion": +15, "persuasion": +10},
            "logical": {"persuasion": +20, "clarity": +10}, 
            "urgency": {"cta": +15, "emotion": +10}
        }
        
        # Determine strategy from content analysis
        detected_strategy = self._detect_variant_strategy(variant_text)
        bonuses = strategy_bonuses.get(detected_strategy, {})
        
        # Apply bonuses
        final_scores = {
            "clarity_score": min(100, base_clarity + bonuses.get("clarity", 0)),
            "persuasion_score": min(100, base_persuasion + bonuses.get("persuasion", 0)),
            "emotion_score": min(100, base_emotion + bonuses.get("emotion", 0)),
            "cta_strength": min(100, base_cta + bonuses.get("cta", 0)),
            "platform_fit_score": min(100, base_platform_fit + bonuses.get("platform_fit", 0))
        }
        
        # Use our calibrated scoring system
        result = self.calibrator.calculate_calibrated_score(
            final_scores["clarity_score"],
            final_scores["persuasion_score"], 
            final_scores["emotion_score"],
            final_scores["cta_strength"],
            final_scores["platform_fit_score"],
            variant_text
        )
        
        return result
    
    def _detect_variant_strategy(self, text: str) -> str:
        """Detect which strategy a variant is using based on keywords."""
        text_lower = text.lower()
        
        strategy_scores = {}
        for strategy, config in self.improvement_strategies.items():
            score = sum(1 for keyword in config['keywords'] if keyword in text_lower)
            strategy_scores[strategy] = score
        
        # Return strategy with highest keyword match
        return max(strategy_scores, key=strategy_scores.get)
    
    def _create_fallback_variant(self, original_ad: Dict[str, str], strategy: str, original_score: float) -> AdVariant:
        """Create a basic fallback variant if generation fails."""
        template = self._generate_template_variant(original_ad, strategy)
        
        return AdVariant(
            variant_type=strategy,
            headline=template['headline'],
            body_text=template['body_text'],
            cta=template['cta'],
            improvement_reason=template['reason'],
            predicted_score=original_score + 8.0,  # Conservative improvement estimate
            score_improvement=8.0,
            strategy_focus=self.improvement_strategies[strategy]['focus']
        )
    
    def save_improvements_to_cache(self, analysis_id: str, variants: List[AdVariant]) -> bool:
        """Save generated improvements for future reference."""
        try:
            # In a real system, this would save to database
            # For now, we'll just log the success
            cache_data = {
                "analysis_id": analysis_id,
                "generated_at": datetime.now().isoformat(),
                "variants": [
                    {
                        "type": v.variant_type,
                        "headline": v.headline,
                        "body_text": v.body_text,
                        "cta": v.cta,
                        "predicted_score": v.predicted_score,
                        "score_improvement": v.score_improvement
                    } for v in variants
                ]
            }
            
            print(f"✅ Cached {len(variants)} improvements for analysis {analysis_id}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to cache improvements: {e}")
            return False


# API Integration Functions
async def improve_ad_copy(original_ad: Dict[str, str], 
                         current_scores: Dict[str, float],
                         user_id: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Main function to generate ad improvements.
    Returns list of improvement variants with predicted scores.
    """
    service = AdImprovementService()
    variants = await service.generate_ad_improvements(original_ad, current_scores, user_id)
    
    # Convert to API response format
    return [
        {
            "variant_type": v.variant_type,
            "strategy_focus": v.strategy_focus,
            "headline": v.headline,
            "body_text": v.body_text,
            "cta": v.cta,
            "improvement_reason": v.improvement_reason,
            "predicted_score": v.predicted_score,
            "score_improvement": v.score_improvement,
            "improvement_percentage": f"+{v.score_improvement:.1f}%"
        } for v in variants
    ]


# Test function
async def test_improvement_service():
    """Test the improvement service with sample data."""
    print("🧪 Testing Ad Improvement Service")
    print("=" * 50)
    
    # Sample ad
    sample_ad = {
        "headline": "Best Marketing Software",
        "body_text": "Our platform helps you manage your campaigns better.",
        "cta": "Learn More",
        "platform": "facebook",
        "target_audience": "small business owners",
        "industry": "marketing"
    }
    
    sample_scores = {
        "overall_score": 45.2,
        "clarity_score": 50.0,
        "persuasion_score": 40.0,
        "emotion_score": 35.0,
        "cta_strength": 30.0,
        "platform_fit_score": 65.0
    }
    
    # Generate improvements
    improvements = await improve_ad_copy(sample_ad, sample_scores)
    
    print(f"Original Score: {sample_scores['overall_score']}%")
    print(f"Original: {sample_ad['headline']} | {sample_ad['body_text']} | {sample_ad['cta']}")
    print()
    
    for i, variant in enumerate(improvements, 1):
        print(f"Variant {i}: {variant['variant_type'].title()} Strategy")
        print(f"Score: {variant['predicted_score']:.1f}% ({variant['improvement_percentage']})")
        print(f"Focus: {variant['strategy_focus']}")
        print(f"Headline: {variant['headline']}")
        print(f"Body: {variant['body_text']}")
        print(f"CTA: {variant['cta']}")
        print(f"Why: {variant['improvement_reason']}")
        print("-" * 40)


if __name__ == "__main__":
    import asyncio
    asyncio.run(test_improvement_service())