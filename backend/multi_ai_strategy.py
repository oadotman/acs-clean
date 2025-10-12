#!/usr/bin/env python3
"""
Multi-AI Provider Strategy for AdCopySurge
Implements OpenAI, Gemini, and HuggingFace with intelligent failover and optimization
"""
import asyncio
import openai
import google.generativeai as genai
from transformers import pipeline
from typing import Dict, List, Optional, Any
import time
import logging
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class AIProviderConfig:
    """Configuration for AI providers"""
    name: str
    priority: int  # 1 = highest priority
    cost_per_1k_tokens: float
    max_tokens: int
    rate_limit_rpm: int
    strengths: List[str]

class MultiAIService:
    """
    Intelligent multi-AI provider service with failover and cost optimization
    """
    
    def __init__(self, openai_key: str, gemini_key: str):
        self.providers = {
            'openai': AIProviderConfig(
                name='openai',
                priority=1,  # Best for creative writing
                cost_per_1k_tokens=0.03,  # GPT-4 pricing
                max_tokens=4096,
                rate_limit_rpm=3000,
                strengths=['creativity', 'copywriting', 'persuasion', 'emotional_content']
            ),
            'gemini': AIProviderConfig(
                name='gemini',
                priority=2,  # Great for analysis and structured output
                cost_per_1k_tokens=0.001,  # Much cheaper!
                max_tokens=2048,
                rate_limit_rpm=60,
                strengths=['analysis', 'structured_output', 'platform_optimization', 'data_analysis']
            ),
            'huggingface': AIProviderConfig(
                name='huggingface',
                priority=3,  # Local/free fallback
                cost_per_1k_tokens=0.0,  # Free!
                max_tokens=512,
                rate_limit_rpm=1000,
                strengths=['emotion_detection', 'sentiment', 'classification', 'fallback']
            )
        }
        
        # Initialize providers
        openai.api_key = openai_key
        genai.configure(api_key=gemini_key)
        
        # Usage tracking
        self.usage_stats = {provider: {'requests': 0, 'tokens': 0, 'cost': 0} 
                           for provider in self.providers}

    def select_optimal_provider(self, task_type: str, text_length: int = 0) -> str:
        """
        Intelligently select the best AI provider based on task type and requirements
        """
        task_preferences = {
            'creative_rewrite': ['openai', 'gemini', 'huggingface'],
            'emotional_analysis': ['huggingface', 'openai', 'gemini'], 
            'platform_optimization': ['gemini', 'openai', 'huggingface'],
            'data_analysis': ['gemini', 'openai', 'huggingface'],
            'quick_scoring': ['huggingface', 'gemini', 'openai'],
            'bulk_processing': ['gemini', 'huggingface', 'openai']  # Cost-effective
        }
        
        preferred_order = task_preferences.get(task_type, ['openai', 'gemini', 'huggingface'])
        
        # Check rate limits and availability
        for provider_name in preferred_order:
            if self._is_provider_available(provider_name):
                return provider_name
        
        return 'huggingface'  # Ultimate fallback

    def _is_provider_available(self, provider_name: str) -> bool:
        """Check if provider is available and not rate limited"""
        # Simple rate limit check - in production, implement proper rate limiting
        return True

    async def generate_ad_alternative(self, ad_data: Dict, variant_type: str) -> Optional[Dict]:
        """
        Generate ad alternative using optimal AI provider
        """
        provider = self.select_optimal_provider('creative_rewrite')
        
        try:
            if provider == 'openai':
                return await self._openai_generate(ad_data, variant_type)
            elif provider == 'gemini':
                return await self._gemini_generate(ad_data, variant_type)
            else:
                return await self._huggingface_generate(ad_data, variant_type)
                
        except Exception as e:
            logger.warning(f"{provider} failed: {e}. Trying fallback...")
            return await self._try_fallback_providers(ad_data, variant_type, exclude=provider)

    async def _openai_generate(self, ad_data: Dict, variant_type: str) -> Dict:
        """Generate using OpenAI GPT-4"""
        prompt = self._build_enhanced_prompt(ad_data, variant_type)
        
        response = await openai.ChatCompletion.acreate(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are an expert copywriter with 15+ years creating high-converting ads."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=400,
            temperature=0.7
        )
        
        content = response.choices[0].message.content
        self._track_usage('openai', response.usage.total_tokens)
        
        return self._parse_structured_response(content, variant_type)

    async def _gemini_generate(self, ad_data: Dict, variant_type: str) -> Dict:
        """Generate using Google Gemini"""
        model = genai.GenerativeModel('gemini-pro')
        prompt = self._build_enhanced_prompt(ad_data, variant_type)
        
        response = await model.generate_content_async(
            prompt,
            generation_config=genai.types.GenerationConfig(
                max_output_tokens=400,
                temperature=0.7,
            )
        )
        
        self._track_usage('gemini', len(response.text.split()) * 1.3)  # Estimate tokens
        
        return self._parse_structured_response(response.text, variant_type)

    async def _huggingface_generate(self, ad_data: Dict, variant_type: str) -> Dict:
        """Generate using HuggingFace (template-based fallback)"""
        # Use template-based generation as HF doesn't have good generative models for free
        templates = {
            'persuasive': {
                'headline': f"Proven: {ad_data['headline']}",
                'body_text': f"Join thousands who {ad_data['body_text'].lower()}",
                'cta': 'Get Started Now'
            },
            'emotional': {
                'headline': f"Transform Your {ad_data['headline']}",
                'body_text': f"Imagine {ad_data['body_text']}",
                'cta': 'Claim Your Success'
            },
            'data_driven': {
                'headline': f"93% Improved: {ad_data['headline']}",
                'body_text': f"Join 10,000+ users. {ad_data['body_text']}",
                'cta': 'See Results'
            }
        }
        
        template = templates.get(variant_type, templates['persuasive'])
        self._track_usage('huggingface', 0)  # Free
        
        return {
            'headline': template['headline'][:50],  # Truncate appropriately
            'body_text': template['body_text'][:200],
            'cta': template['cta'][:30],
            'variant_type': variant_type,
            'improvement_reason': f"Template-based {variant_type} optimization"
        }

    def _build_enhanced_prompt(self, ad_data: Dict, variant_type: str) -> str:
        """Build enhanced prompt based on variant type"""
        
        base_context = f"""
Original Ad:
- Headline: {ad_data.get('headline', '')}
- Body: {ad_data.get('body_text', '')}
- CTA: {ad_data.get('cta', '')}
- Platform: {ad_data.get('platform', 'facebook')}
- Industry: {ad_data.get('industry', 'general')}
"""
        
        variant_prompts = {
            'persuasive': f"""
{base_context}

Create a PERSUASIVE version that:
1. Uses social proof (numbers, testimonials, popularity indicators)
2. Creates urgency with time-sensitive language
3. Emphasizes benefits over features
4. Addresses common objections preemptively
5. Uses power words that drive immediate action

Format: HEADLINE: [new] | BODY: [new] | CTA: [new] | REASON: [why better]
""",
            
            'emotional': f"""
{base_context}

Create an EMOTIONAL version that:
1. Identifies the core emotion (fear, desire, aspiration, frustration)
2. Creates a relatable scenario or micro-story
3. Uses sensory language and vivid imagery
4. Appeals to identity and self-image
5. Builds tension that resolves with action

Format: HEADLINE: [emotional] | BODY: [story/scenario] | CTA: [emotion-driven] | REASON: [emotional trigger used]
""",
            
            'data_driven': f"""
{base_context}

Create a DATA-HEAVY version that:
1. Include specific statistics, percentages, or metrics
2. Mention customer counts, time savings, ROI improvements
3. Reference studies, awards, or third-party validation
4. Use quantified benefits instead of vague claims
5. Appeal to logical, evidence-based decision making

Format: HEADLINE: [with numbers] | BODY: [stat-rich] | CTA: [results-focused] | REASON: [key proof points]
""",
            
            'platform_optimized': f"""
{base_context}

Create a {ad_data.get('platform', 'FACEBOOK')}-OPTIMIZED version that:
1. Follows platform character limits and best practices
2. Uses platform-appropriate tone and language
3. Leverages platform user behavior patterns
4. Optimizes for platform algorithm preferences
5. Considers platform demographics and mindset

Format: HEADLINE: [platform-perfect] | BODY: [platform-optimized] | CTA: [platform-appropriate] | REASON: [platform optimizations]
"""
        }
        
        return variant_prompts.get(variant_type, variant_prompts['persuasive'])

    def _parse_structured_response(self, response: str, variant_type: str) -> Dict:
        """Parse AI response into structured format"""
        try:
            parts = response.split('|')
            
            headline = self._extract_field(parts, 'HEADLINE')
            body = self._extract_field(parts, 'BODY')
            cta = self._extract_field(parts, 'CTA')
            reason = self._extract_field(parts, 'REASON')
            
            return {
                'headline': headline[:60],  # Platform limits
                'body_text': body[:200],
                'cta': cta[:30],
                'variant_type': variant_type,
                'improvement_reason': reason[:150]
            }
            
        except Exception as e:
            logger.warning(f"Failed to parse response: {e}")
            # Return fallback
            return {
                'headline': f"Optimized: {variant_type.title()}",
                'body_text': "Enhanced copy optimized for performance.",
                'cta': "Take Action",
                'variant_type': variant_type,
                'improvement_reason': f"AI-generated {variant_type} optimization"
            }

    def _extract_field(self, parts: List[str], field_name: str) -> str:
        """Extract field from structured response"""
        for part in parts:
            if field_name in part.upper():
                return part.split(':', 1)[-1].strip()
        return f"Enhanced {field_name.lower()}"

    async def _try_fallback_providers(self, ad_data: Dict, variant_type: str, exclude: str) -> Dict:
        """Try other providers if primary fails"""
        providers = ['openai', 'gemini', 'huggingface']
        providers = [p for p in providers if p != exclude]
        
        for provider in providers:
            try:
                if provider == 'openai':
                    return await self._openai_generate(ad_data, variant_type)
                elif provider == 'gemini':
                    return await self._gemini_generate(ad_data, variant_type)
                else:
                    return await self._huggingface_generate(ad_data, variant_type)
            except Exception as e:
                logger.warning(f"Fallback {provider} failed: {e}")
                continue
        
        # Ultimate fallback
        return await self._huggingface_generate(ad_data, variant_type)

    def _track_usage(self, provider: str, tokens: int):
        """Track usage statistics"""
        self.usage_stats[provider]['requests'] += 1
        self.usage_stats[provider]['tokens'] += tokens
        
        cost_per_token = self.providers[provider].cost_per_1k_tokens / 1000
        self.usage_stats[provider]['cost'] += tokens * cost_per_token

    def get_usage_summary(self) -> Dict:
        """Get usage and cost summary"""
        return {
            'total_cost': sum(stats['cost'] for stats in self.usage_stats.values()),
            'total_requests': sum(stats['requests'] for stats in self.usage_stats.values()),
            'total_tokens': sum(stats['tokens'] for stats in self.usage_stats.values()),
            'by_provider': self.usage_stats,
            'cost_savings': self._calculate_cost_savings()
        }

    def _calculate_cost_savings(self) -> float:
        """Calculate cost savings from using cheaper providers"""
        total_tokens = sum(stats['tokens'] for stats in self.usage_stats.values())
        actual_cost = sum(stats['cost'] for stats in self.usage_stats.values())
        
        # What it would cost if we used only OpenAI
        openai_only_cost = total_tokens * (self.providers['openai'].cost_per_1k_tokens / 1000)
        
        return max(0, openai_only_cost - actual_cost)

# INTEGRATION EXAMPLE FOR YOUR EXISTING CODEBASE

class EnhancedAdAnalysisService:
    """Enhanced version of your existing AdAnalysisService with multi-AI support"""
    
    def __init__(self, db, openai_key: str, gemini_key: str):
        self.db = db
        self.ai_service = MultiAIService(openai_key, gemini_key)
        
        # Initialize your existing analyzers
        from app.services.readability_analyzer import ReadabilityAnalyzer
        from app.services.emotion_analyzer import EmotionAnalyzer
        from app.services.cta_analyzer import CTAAnalyzer
        
        self.readability_analyzer = ReadabilityAnalyzer()
        self.emotion_analyzer = EmotionAnalyzer()
        self.cta_analyzer = CTAAnalyzer()

    async def generate_ai_alternatives(self, ad_data: Dict) -> List[Dict]:
        """Generate multiple AI alternatives using different providers optimally"""
        
        variant_types = ['persuasive', 'emotional', 'data_driven', 'platform_optimized']
        alternatives = []
        
        # Generate alternatives in parallel for speed
        tasks = [
            self.ai_service.generate_ad_alternative(ad_data, variant_type)
            for variant_type in variant_types
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        for result in results:
            if isinstance(result, dict):
                alternatives.append(result)
        
        return alternatives

    def get_ai_cost_summary(self) -> Dict:
        """Get AI usage and cost summary for analytics"""
        return self.ai_service.get_usage_summary()

# CONFIGURATION FOR YOUR .ENV FILE
RECOMMENDED_ENV_VARS = """
# Multi-AI Configuration
OPENAI_API_KEY=your-openai-key
GEMINI_API_KEY=your-gemini-key
HUGGINGFACE_API_TOKEN=your-hf-token  # Optional

# AI Provider Preferences
PRIMARY_AI_PROVIDER=openai
FALLBACK_AI_PROVIDER=gemini
COST_OPTIMIZATION_ENABLED=true
MAX_AI_COST_PER_ANALYSIS=0.05  # USD

# Feature Flags
USE_MULTI_AI=true
ENABLE_AI_FAILOVER=true
ENABLE_COST_TRACKING=true
"""

if __name__ == "__main__":
    # Test the multi-AI service
    async def test_multi_ai():
        ai_service = MultiAIService("test-openai-key", "test-gemini-key")
        
        test_ad = {
            'headline': 'Amazing Product Sale',
            'body_text': 'Buy our product and save money today!',
            'cta': 'Shop Now',
            'platform': 'facebook',
            'industry': 'ecommerce'
        }
        
        result = await ai_service.generate_ad_alternative(test_ad, 'persuasive')
        print(f"Generated alternative: {result}")
        
        summary = ai_service.get_usage_summary()
        print(f"Usage summary: {summary}")
    
    # asyncio.run(test_multi_ai())
