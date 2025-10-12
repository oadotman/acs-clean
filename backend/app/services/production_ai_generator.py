"""
Production AI Alternative Generator - NO TEMPLATES OR FALLBACKS

This service replaces the multi_ai_strategy.py system with a strict production version
that only uses real AI providers and fails fast when they're unavailable.
"""

import asyncio
import openai
try:
    import google.generativeai as genai
    GENAI_AVAILABLE = True
except ImportError:
    genai = None
    GENAI_AVAILABLE = False
from typing import Dict, List, Optional, Any
import time
import logging
from dataclasses import dataclass
from app.core.exceptions import AIProviderUnavailable, ProductionError, fail_fast_on_mock_data

logger = logging.getLogger(__name__)

@dataclass
class AIProviderConfig:
    """Configuration for AI providers - production settings only"""
    name: str
    priority: int  # 1 = highest priority
    cost_per_1k_tokens: float
    max_tokens: int
    rate_limit_rpm: int
    required_env_var: str


class ProductionAIService:
    """
    Production-only multi-AI provider service
    
    NO FALLBACKS TO TEMPLATES - All providers must be real AI services
    Fails fast with proper error codes when AI is unavailable
    """
    
    def __init__(self, openai_key: str, gemini_key: str = None):
        self.providers = {}
        
        # Initialize only real AI providers
        if openai_key and openai_key.startswith('sk-'):
            openai.api_key = openai_key
            self.providers['openai'] = AIProviderConfig(
                name='openai',
                priority=1,
                cost_per_1k_tokens=0.03,  # GPT-4 pricing
                max_tokens=4096,
                rate_limit_rpm=3000,
                required_env_var='OPENAI_API_KEY'
            )
        else:
            logger.warning("OpenAI API key not provided or invalid")
        
        if gemini_key and GENAI_AVAILABLE:
            try:
                genai.configure(api_key=gemini_key)
                self.providers['gemini'] = AIProviderConfig(
                    name='gemini',
                    priority=2,
                    cost_per_1k_tokens=0.001,
                    max_tokens=2048,
                    rate_limit_rpm=60,
                    required_env_var='GEMINI_API_KEY'
                )
            except Exception as e:
                logger.warning(f"Gemini initialization failed: {e}")
        elif gemini_key and not GENAI_AVAILABLE:
            logger.warning("Gemini API key provided but google-generativeai package not installed")
        
        # Validate at least one provider is available
        if not self.providers:
            raise AIProviderUnavailable(
                "initialization",
                "No AI providers configured. Production requires OpenAI or Gemini API keys."
            )
        
        # Usage tracking for production monitoring
        self.usage_stats = {provider: {'requests': 0, 'tokens': 0, 'cost': 0} 
                           for provider in self.providers}
        
        logger.info(f"Production AI service initialized with providers: {list(self.providers.keys())}")
    
    def select_optimal_provider(self, task_type: str) -> str:
        """
        Select best available AI provider - NO TEMPLATE FALLBACK
        """
        if not self.providers:
            raise AIProviderUnavailable(
                "provider_selection",
                "No AI providers available for task"
            )
        
        # Task preferences for production AI providers only
        task_preferences = {
            'creative_rewrite': ['openai', 'gemini'],
            'emotional_analysis': ['openai', 'gemini'], 
            'platform_optimization': ['gemini', 'openai'],
            'data_analysis': ['gemini', 'openai']
        }
        
        preferred_order = task_preferences.get(task_type, ['openai', 'gemini'])
        
        # Select first available provider from preferences
        for provider_name in preferred_order:
            if provider_name in self.providers and self._is_provider_available(provider_name):
                return provider_name
        
        # If no preferred providers available, use any available
        available_providers = [name for name in self.providers.keys() 
                             if self._is_provider_available(name)]
        
        if not available_providers:
            raise AIProviderUnavailable(
                "all_providers",
                f"No AI providers available for {task_type}. Required providers: {preferred_order}"
            )
        
        return available_providers[0]
    
    def _is_provider_available(self, provider_name: str) -> bool:
        """Check if provider is available and configured"""
        return provider_name in self.providers
    
    async def generate_ad_alternative(self, ad_data: Dict, variant_type: str, 
                                    emoji_level: str = "moderate", 
                                    human_tone: str = "conversational",
                                    brand_tone: str = "casual",
                                    formality_level: int = 5,
                                    target_audience_description: str = None,
                                    brand_voice_description: str = None,
                                    include_cta: bool = True,
                                    cta_style: str = "medium",
                                    # Phase 4 & 5: Creative Controls
                                    creativity_level: int = 5,
                                    urgency_level: int = 5,
                                    emotion_type: str = "inspiring",
                                    filter_cliches: bool = True) -> Dict:
        """
        Generate ad alternative using REAL AI only - NO TEMPLATES
        """
        # Validate input data
        fail_fast_on_mock_data(ad_data, "ai_generation_input")
        
        if not ad_data.get('headline') or not ad_data.get('body_text'):
            raise ProductionError(
                "Invalid ad data for AI generation",
                "INVALID_AI_INPUT",
                {"ad_data": ad_data}
            )
        
        # Select optimal provider
        try:
            provider = self.select_optimal_provider('creative_rewrite')
        except AIProviderUnavailable as e:
            # Re-raise with more context
            raise AIProviderUnavailable(
                "creative_rewrite",
                f"No AI providers available for alternative generation: {str(e)}"
            )
        
        # Generate using selected provider
        try:
            if provider == 'openai':
                result = await self._openai_generate(
                    ad_data, variant_type, emoji_level, human_tone,
                    brand_tone, formality_level, target_audience_description,
                    brand_voice_description, include_cta, cta_style,
                    creativity_level, urgency_level, emotion_type, filter_cliches
                )
            elif provider == 'gemini':
                result = await self._gemini_generate(
                    ad_data, variant_type, emoji_level, human_tone,
                    brand_tone, formality_level, target_audience_description,
                    brand_voice_description, include_cta, cta_style,
                    creativity_level, urgency_level, emotion_type, filter_cliches
                )
            else:
                raise AIProviderUnavailable(
                    provider,
                    f"Unknown provider requested: {provider}"
                )
            
            # Validate result is not mock data
            fail_fast_on_mock_data(result, f"ai_generation_result_{provider}")
            
            return result
            
        except Exception as e:
            # NO FALLBACKS - propagate error up
            if isinstance(e, AIProviderUnavailable):
                raise
            else:
                raise AIProviderUnavailable(
                    provider,
                    f"AI generation failed: {str(e)}"
                )
    
    async def _openai_generate(self, ad_data: Dict, variant_type: str, 
                                emoji_level: str = "moderate", 
                                human_tone: str = "conversational",
                                brand_tone: str = "casual",
                                formality_level: int = 5,
                                target_audience_description: str = None,
                                brand_voice_description: str = None,
                                include_cta: bool = True,
                                cta_style: str = "medium",
                                # Phase 4 & 5: Creative Controls
                                creativity_level: int = 5,
                                urgency_level: int = 5,
                                emotion_type: str = "inspiring",
                                filter_cliches: bool = True) -> Dict:
        """Generate using OpenAI GPT-4 - production implementation with creative controls"""
        try:
            # Import platform limits for parameter mapping and creative controls
            from app.constants.platform_limits import (
                get_ai_parameters, HumanTone, get_optimal_creative_parameters
            )
            from app.constants.creative_controls import EmotionType
            
            platform = ad_data.get('platform', 'facebook')
            
            # Get optimal creative parameters combining creativity level with platform settings
            try:
                emotion_enum = EmotionType(emotion_type)
            except ValueError:
                emotion_enum = EmotionType.INSPIRING
                
            try:
                tone_enum = HumanTone(human_tone)
            except ValueError:
                tone_enum = HumanTone.CONVERSATIONAL
            
            # Get optimal parameters that prioritize creativity level over human tone
            optimal_params = get_optimal_creative_parameters(
                platform=platform,
                creativity_level=creativity_level,
                urgency_level=urgency_level,
                emotion_type=emotion_enum,
                human_tone=tone_enum
            )
            
            ai_params = optimal_params["ai_parameters"]
            
            # Log any platform warnings for monitoring
            if optimal_params["platform_warnings"]:
                logger.info(f"Creative warnings for {platform}: {optimal_params['platform_warnings']}")
            
            prompt = self._build_production_prompt(
                ad_data, variant_type, emoji_level, human_tone,
                brand_tone, formality_level, target_audience_description,
                brand_voice_description, include_cta, cta_style,
                creativity_level, urgency_level, emotion_type, filter_cliches
            )
            
            # Use new OpenAI client
            client = openai.AsyncOpenAI(api_key=openai.api_key)
            
            response = await client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {
                        "role": "system", 
                        "content": "You are an expert copywriter with 15+ years creating high-converting ads. Respond only with the requested format, no extra text."
                    },
                    {
                        "role": "user", 
                        "content": prompt
                    }
                ],
                max_tokens=500,
                temperature=ai_params["temperature"],
                presence_penalty=ai_params["presence_penalty"],
                frequency_penalty=ai_params["frequency_penalty"]
            )
            
            content = response.choices[0].message.content
            tokens_used = response.usage.total_tokens
            
            self._track_usage('openai', tokens_used)
            
            # Parse and validate response
            parsed_result = self._parse_structured_response(content, variant_type)
            
            # Ensure we got real content, not placeholder text
            if self._is_placeholder_content(parsed_result):
                raise AIProviderUnavailable(
                    "openai",
                    "OpenAI returned placeholder content"
                )
            
            return parsed_result
            
        except openai.APIError as e:
            raise AIProviderUnavailable(
                "openai",
                f"OpenAI API error: {str(e)}"
            )
        except openai.RateLimitError as e:
            raise AIProviderUnavailable(
                "openai", 
                f"OpenAI rate limit exceeded: {str(e)}",
                retry_after=60
            )
        except Exception as e:
            raise AIProviderUnavailable(
                "openai",
                f"OpenAI generation error: {str(e)}"
            )
    
    async def _gemini_generate(self, ad_data: Dict, variant_type: str,
                                emoji_level: str = "moderate",
                                human_tone: str = "conversational",
                                brand_tone: str = "casual",
                                formality_level: int = 5,
                                target_audience_description: str = None,
                                brand_voice_description: str = None,
                                include_cta: bool = True,
                                cta_style: str = "medium",
                                # Phase 4 & 5: Creative Controls
                                creativity_level: int = 5,
                                urgency_level: int = 5,
                                emotion_type: str = "inspiring",
                                filter_cliches: bool = True) -> Dict:
        """Generate using Google Gemini - production implementation with creative controls"""
        try:
            # Import platform limits for parameter mapping and creative controls
            from app.constants.platform_limits import (
                get_ai_parameters, HumanTone, get_optimal_creative_parameters
            )
            from app.constants.creative_controls import EmotionType
            
            platform = ad_data.get('platform', 'facebook')
            
            # Get optimal creative parameters combining creativity level with platform settings
            try:
                emotion_enum = EmotionType(emotion_type)
            except ValueError:
                emotion_enum = EmotionType.INSPIRING
                
            try:
                tone_enum = HumanTone(human_tone)
            except ValueError:
                tone_enum = HumanTone.CONVERSATIONAL
            
            # Get optimal parameters that prioritize creativity level over human tone
            optimal_params = get_optimal_creative_parameters(
                platform=platform,
                creativity_level=creativity_level,
                urgency_level=urgency_level,
                emotion_type=emotion_enum,
                human_tone=tone_enum
            )
            
            ai_params = optimal_params["ai_parameters"]
            
            # Log any platform warnings for monitoring
            if optimal_params["platform_warnings"]:
                logger.info(f"Creative warnings for {platform}: {optimal_params['platform_warnings']}")
                
            model = genai.GenerativeModel('gemini-pro')
            prompt = self._build_production_prompt(
                ad_data, variant_type, emoji_level, human_tone,
                brand_tone, formality_level, target_audience_description,
                brand_voice_description, include_cta, cta_style,
                creativity_level, urgency_level, emotion_type, filter_cliches
            )
            
            response = await model.generate_content_async(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    max_output_tokens=500,
                    temperature=ai_params["temperature"],
                )
            )
            
            # Estimate tokens for tracking
            estimated_tokens = len(response.text.split()) * 1.3
            self._track_usage('gemini', int(estimated_tokens))
            
            # Parse and validate response
            parsed_result = self._parse_structured_response(response.text, variant_type)
            
            # Ensure we got real content
            if self._is_placeholder_content(parsed_result):
                raise AIProviderUnavailable(
                    "gemini",
                    "Gemini returned placeholder content"
                )
            
            return parsed_result
            
        except Exception as e:
            raise AIProviderUnavailable(
                "gemini",
                f"Gemini generation error: {str(e)}"
            )
    
    def _build_production_prompt(self, ad_data: Dict, variant_type: str, 
                                 emoji_level: str = "moderate",
                                 human_tone: str = "conversational",
                                 brand_tone: str = "casual",
                                 formality_level: int = 5,
                                 target_audience_description: str = None,
                                 brand_voice_description: str = None,
                                 include_cta: bool = True,
                                 cta_style: str = "medium",
                                 # Phase 4 & 5: Creative Controls
                                 creativity_level: int = 5,
                                 urgency_level: int = 5,
                                 emotion_type: str = "inspiring",
                                 filter_cliches: bool = True) -> str:
        """Build enhanced prompt for production AI generation with Phase 4 & 5 creative controls"""
        
        # Import platform configuration and creative controls
        from app.constants.platform_limits import (
            get_platform_limit, get_emoji_guideline, get_tone_instruction, 
            EmojiLevel, HumanTone, get_platform_config, BrandTone, CTAStyle,
            get_brand_tone_guideline, get_formality_guideline, get_cta_examples,
            build_platform_creative_prompt
        )
        from app.constants.creative_controls import (
            EmotionType, get_creativity_description, get_urgency_description,
            get_emotion_config
        )
        
        platform = ad_data.get('platform', 'facebook')
        character_limit = get_platform_limit(platform)
        platform_config = get_platform_config(platform)
        
        # Get emoji and tone instructions
        try:
            emoji_enum = EmojiLevel(emoji_level)
            emoji_guideline = get_emoji_guideline(emoji_enum)
        except ValueError:
            emoji_guideline = get_emoji_guideline(EmojiLevel.MODERATE)
            
        try:
            tone_enum = HumanTone(human_tone)
            tone_instruction = get_tone_instruction(tone_enum)
        except ValueError:
            tone_instruction = get_tone_instruction(HumanTone.CONVERSATIONAL)
            
        # Get brand tone guidelines
        try:
            brand_tone_enum = BrandTone(brand_tone)
            brand_tone_guideline = get_brand_tone_guideline(brand_tone_enum)
        except ValueError:
            brand_tone_guideline = get_brand_tone_guideline(BrandTone.CASUAL)
            
        # Get formality guideline
        formality_guideline = get_formality_guideline(formality_level)
        
        # Get CTA examples if CTA is included
        cta_instruction = ""
        if include_cta:
            try:
                cta_style_enum = CTAStyle(cta_style)
                cta_examples = get_cta_examples(cta_style_enum)
                cta_instruction = f"Include a {cta_style} call-to-action. Examples: {', '.join(cta_examples[:3])}"
            except ValueError:
                cta_instruction = "Include a moderate call-to-action like 'Get Started' or 'Learn More'"
        else:
            cta_instruction = "Do not include any call-to-action. Focus on information and engagement."
        
        # Enhanced audience context
        audience_context = target_audience_description or ad_data.get('target_audience', 'general audience')
        brand_voice_context = brand_voice_description or "authentic and engaging"
        
        # Phase 4 & 5: Creative control descriptions
        try:
            emotion_enum = EmotionType(emotion_type)
            emotion_config = get_emotion_config(emotion_enum)
        except ValueError:
            emotion_config = get_emotion_config(EmotionType.INSPIRING)
        
        creativity_desc = get_creativity_description(creativity_level)
        urgency_desc = get_urgency_description(urgency_level)
        
        base_context = f"""
Original Ad Copy:
- Headline: {ad_data.get('headline', '')}
- Body: {ad_data.get('body_text', '')}
- CTA: {ad_data.get('cta', '')}
- Platform: {platform}
- Industry: {ad_data.get('industry', 'general')}

AUDIENCE & BRAND:
- Target Audience: {audience_context}
- Brand Voice: {brand_voice_context}
- Brand Tone: {brand_tone.title()}
- Formality Level: {formality_level}/10

PLATFORM REQUIREMENTS:
- Character Limit: {character_limit} characters maximum
- Platform Culture: {platform_config.get('audience_mindset', 'General audience')}

CREATIVE CONTROLS (Phase 4 & 5):
- Creativity Level: {creativity_level}/10 ({creativity_desc})
- Urgency Level: {urgency_level}/10 ({urgency_desc})
- Emotion Type: {emotion_type.title()} - {emotion_config['description']}
- Emotion Keywords: {', '.join(emotion_config['keywords'])}
- Filter Clichés: {'YES - Avoid overused marketing phrases' if filter_cliches else 'NO - Standard filtering'}

STYLE GUIDELINES:
- Emoji Usage: {emoji_guideline}
- Human Tone: {tone_instruction}
- Brand Tone: {brand_tone_guideline}
- Formality: {formality_guideline}
- Emotional Approach: {emotion_config['approach']}

CALL-TO-ACTION:
{cta_instruction}
"""
        
        # Add TikTok-specific instructions if needed
        tiktok_note = ""
        if platform.lower() == 'tiktok':
            tiktok_note = f"""
            
⚠️ TIKTOK SPECIAL REQUIREMENTS:
- Use Gen Z language naturally (not forced)
- Focus on hooks that stop the scroll
- Be conversational and relatable, not promotional
- Embrace humor and authenticity over polish
- 100 character limit is STRICT - be concise!
"""

        # Add platform-specific creative instructions from Phase 4 & 5
        try:
            platform_creative_instructions = build_platform_creative_prompt(
                platform, creativity_level, urgency_level, 
                EmotionType(emotion_type), filter_cliches
            )
        except ValueError:
            platform_creative_instructions = build_platform_creative_prompt(
                platform, creativity_level, urgency_level, 
                EmotionType.INSPIRING, filter_cliches
            )
        
        # Character limit enforcement
        char_limit_note = f"\n\n⚠️ STRICT CHARACTER LIMIT: Your entire response MUST NOT exceed {character_limit} characters. Count carefully!"
        
        # Creative instructions based on settings
        creative_instructions = f"""
        
🎨 CREATIVE INSTRUCTIONS:
{platform_creative_instructions}

⚠️ AVOID if filtering clichés is enabled: overused phrases like "game-changer", "next-level", "cutting-edge", "revolutionary", "world-class", "amazing results", "transform your life", etc.
""" if filter_cliches else ""
        
        # Production-quality prompts for each variant type
        variant_prompts = {
            'persuasive': f"""
{base_context}{tiktok_note}{creative_instructions}

Create a HIGHLY PERSUASIVE ad variation that:
1. Uses specific social proof (numbers, testimonials, popularity indicators)
2. Creates urgency with time-sensitive language
3. Emphasizes concrete benefits over features  
4. Addresses common objections preemptively
5. Uses power words that drive immediate action
6. Includes scarcity or limited-time elements
7. Leverages authority and credibility markers
{char_limit_note}

CRITICAL: Respond ONLY in this exact format:
HEADLINE: [new persuasive headline]
BODY: [new persuasive body text]  
CTA: [new persuasive call-to-action]
REASON: [specific persuasion tactics used]
""",
            
            'emotional': f"""
{base_context}{tiktok_note}{creative_instructions}

Create an EMOTIONALLY COMPELLING ad variation that:
1. Identifies and targets the core emotion (fear, desire, aspiration, frustration)
2. Creates a relatable scenario or micro-story that connects
3. Uses sensory language and vivid, specific imagery
4. Appeals to identity and self-image transformation
5. Builds emotional tension that resolves with action
6. Uses emotional triggers appropriate for the target audience
7. Incorporates aspirational outcomes and future-state benefits
{char_limit_note}

CRITICAL: Respond ONLY in this exact format:
HEADLINE: [emotionally compelling headline]
BODY: [emotional story/scenario body text]
CTA: [emotion-driven call-to-action]
REASON: [specific emotional triggers and tactics used]
""",
            
            'data_driven': f"""
{base_context}{tiktok_note}{creative_instructions}

Create a DATA-RICH and EVIDENCE-BASED ad variation that:
1. Include specific statistics, percentages, or quantified metrics
2. Mention customer counts, time savings, ROI improvements with numbers
3. Reference studies, awards, certifications, or third-party validation
4. Use quantified benefits instead of vague claims
5. Appeal to logical, evidence-based decision making
6. Incorporate comparison data vs competitors or industry averages
7. Use concrete before/after numbers and success metrics
{char_limit_note}

CRITICAL: Respond ONLY in this exact format:
HEADLINE: [data-rich headline with numbers]
BODY: [statistically-heavy body text with metrics]
CTA: [results-focused call-to-action]
REASON: [specific data points and proof elements used]
""",
            
            'platform_optimized': f"""
{base_context}{tiktok_note}{creative_instructions}

Create a {ad_data.get('platform', 'FACEBOOK').upper()}-OPTIMIZED ad variation that:
1. Follows platform-specific character limits and formatting best practices
2. Uses platform-appropriate tone, language, and communication style
3. Leverages platform user behavior patterns and expectations
4. Optimizes for platform algorithm preferences and engagement factors
5. Considers platform-specific demographics and user mindset
6. Incorporates platform-native features and call-to-action styles
7. Aligns with how successful ads perform on this specific platform
{char_limit_note}

CRITICAL: Respond ONLY in this exact format:
HEADLINE: [platform-optimized headline]
BODY: [platform-optimized body text]
CTA: [platform-appropriate call-to-action]
REASON: [specific platform optimizations applied]
"""
        }
        
        return variant_prompts.get(variant_type, variant_prompts['persuasive'])
    
    def _parse_structured_response(self, response: str, variant_type: str) -> Dict:
        """Parse AI response into structured format - production validation"""
        try:
            lines = response.strip().split('\n')
            parsed = {}
            
            for line in lines:
                line = line.strip()
                if ':' in line:
                    key, value = line.split(':', 1)
                    key = key.strip().upper()
                    value = value.strip()
                    
                    if key == 'HEADLINE':
                        parsed['headline'] = value[:80]  # Platform limits
                    elif key == 'BODY':
                        parsed['body_text'] = value[:250]
                    elif key == 'CTA':
                        parsed['cta'] = value[:40]
                    elif key == 'REASON':
                        parsed['improvement_reason'] = value[:200]
            
            # Validate required fields are present and not empty
            required_fields = ['headline', 'body_text', 'cta', 'improvement_reason']
            for field in required_fields:
                if not parsed.get(field) or len(parsed[field].strip()) < 5:
                    raise ProductionError(
                        f"AI response missing or insufficient {field}",
                        "AI_RESPONSE_INCOMPLETE",
                        {"parsed_response": parsed, "original_response": response}
                    )
            
            # Add metadata
            parsed['variant_type'] = variant_type
            parsed['ai_generated'] = True
            parsed['generation_timestamp'] = time.time()
            
            return parsed
            
        except Exception as e:
            # NO FALLBACK - raise error for investigation
            raise ProductionError(
                f"Failed to parse AI response: {str(e)}",
                "AI_RESPONSE_PARSE_FAILED",
                {"response": response, "variant_type": variant_type}
            )
    
    def _is_placeholder_content(self, parsed_result: Dict) -> bool:
        """Check if AI returned placeholder/template content"""
        placeholder_indicators = [
            '[new]', '[headline]', '[body]', '[cta]', '[reason]',
            'enhanced copy', 'optimized copy', 'improved copy',
            'take action', 'click here', 'learn more'
        ]
        
        content_to_check = [
            parsed_result.get('headline', ''),
            parsed_result.get('body_text', ''),
            parsed_result.get('cta', ''),
            parsed_result.get('improvement_reason', '')
        ]
        
        for content in content_to_check:
            content_lower = content.lower()
            for indicator in placeholder_indicators:
                if indicator in content_lower:
                    return True
        
        return False
    
    def _track_usage(self, provider: str, tokens: int):
        """Track usage statistics for production monitoring"""
        if provider in self.usage_stats:
            self.usage_stats[provider]['requests'] += 1
            self.usage_stats[provider]['tokens'] += tokens
            
            cost_per_token = self.providers[provider].cost_per_1k_tokens / 1000
            self.usage_stats[provider]['cost'] += tokens * cost_per_token
    
    def get_usage_summary(self) -> Dict:
        """Get production usage and cost summary"""
        summary = {
            'total_cost': sum(stats['cost'] for stats in self.usage_stats.values()),
            'total_requests': sum(stats['requests'] for stats in self.usage_stats.values()),
            'total_tokens': sum(stats['tokens'] for stats in self.usage_stats.values()),
            'by_provider': self.usage_stats,
            'available_providers': list(self.providers.keys()),
            'production_ready': len(self.providers) > 0
        }
        
        return summary
    
    async def health_check(self) -> Dict[str, Any]:
        """Production health check for AI services"""
        health_status = {
            'service': 'production_ai_generator',
            'status': 'healthy',
            'providers': {},
            'total_providers': len(self.providers),
            'healthy_providers': 0
        }
        
        # Test each provider
        test_ad_data = {
            'headline': 'Test Headline',
            'body_text': 'Test body text for health check',
            'cta': 'Test CTA',
            'platform': 'facebook'
        }
        
        for provider_name in self.providers.keys():
            provider_health = {
                'status': 'unknown',
                'last_test': time.time(),
                'error': None
            }
            
            try:
                # Quick test generation
                if provider_name == 'openai':
                    await self._openai_generate(test_ad_data, 'persuasive')
                elif provider_name == 'gemini':
                    await self._gemini_generate(test_ad_data, 'persuasive')
                
                provider_health['status'] = 'healthy'
                health_status['healthy_providers'] += 1
                
            except Exception as e:
                provider_health['status'] = 'unhealthy' 
                provider_health['error'] = str(e)
            
            health_status['providers'][provider_name] = provider_health
        
        # Determine overall status
        if health_status['healthy_providers'] == 0:
            health_status['status'] = 'critical'
        elif health_status['healthy_providers'] < health_status['total_providers']:
            health_status['status'] = 'degraded'
        
        return health_status
    
    async def generate_multiple_alternatives(self, ad_data: Dict, variant_types: List[str] = None) -> List[Dict]:
        """Generate multiple alternatives in parallel - production implementation"""
        
        if not variant_types:
            variant_types = ['persuasive', 'emotional', 'data_driven', 'platform_optimized']
        
        # Generate alternatives in parallel for efficiency
        tasks = [
            self.generate_ad_alternative(ad_data, variant_type)
            for variant_type in variant_types
        ]
        
        try:
            results = await asyncio.gather(*tasks, return_exceptions=True)
        except Exception as e:
            raise AIProviderUnavailable(
                "batch_generation",
                f"Failed to generate alternatives in parallel: {str(e)}"
            )
        
        # Process results and handle any individual failures
        alternatives = []
        failures = []
        
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                failures.append(f"{variant_types[i]}: {str(result)}")
                logger.warning(f"Failed to generate {variant_types[i]} alternative: {result}")
            elif isinstance(result, dict):
                alternatives.append(result)
        
        # Require at least one successful alternative
        if not alternatives:
            raise AIProviderUnavailable(
                "batch_generation",
                f"All alternative generation failed. Failures: {'; '.join(failures)}"
            )
        
        return alternatives
    
    async def generate_creative_variants(
        self,
        ad_data: Dict,
        num_variants: int = 3,
        creativity_level: int = 5,
        urgency_level: int = 5,
        emotion_type: str = "inspiring",
        filter_cliches: bool = True,
        variant_type: str = "persuasive",
        **kwargs
    ) -> List[Dict]:
        """Generate multiple creative variants with different approaches - Phase 4 & 5 feature"""
        
        if num_variants < 1 or num_variants > 5:
            raise ProductionError(
                "Invalid number of variants requested",
                "INVALID_VARIANT_COUNT",
                {"requested": num_variants, "allowed_range": "1-5"}
            )
        
        # Import creative controls for variant generation strategies
        from app.constants.creative_controls import (
            EmotionType, CreativityLevel, UrgencyLevel,
            get_creativity_description, analyze_creative_risk
        )
        
        platform = ad_data.get('platform', 'facebook')
        
        # Analyze risk level for monitoring
        try:
            emotion_enum = EmotionType(emotion_type)
        except ValueError:
            emotion_enum = EmotionType.INSPIRING
        
        risk_analysis = analyze_creative_risk(
            creativity_level, urgency_level, emotion_enum, platform
        )
        
        logger.info(f"Generating {num_variants} variants with {risk_analysis['risk_level']} risk level")
        
        # Create variant generation strategies
        variant_strategies = []
        
        for i in range(num_variants):
            # Vary creativity and urgency slightly for different variants
            variant_creativity = min(10, max(0, creativity_level + (i - 1)))
            variant_urgency = min(10, max(0, urgency_level + ((i - 1) * 2 % 3 - 1)))
            
            # Rotate emotion types for more variety if multiple variants
            emotions = [emotion_type, "trust_building", "excitement", "problem_solving", "curiosity"]
            variant_emotion = emotions[i % len(emotions)] if num_variants > 1 else emotion_type
            
            strategy = {
                'creativity_level': variant_creativity,
                'urgency_level': variant_urgency,
                'emotion_type': variant_emotion,
                'filter_cliches': filter_cliches,
                'variant_name': f"Variant {i+1}",
                'approach_description': f"C{variant_creativity} U{variant_urgency} E:{variant_emotion}"
            }
            variant_strategies.append(strategy)
        
        # Generate variants in parallel
        tasks = []
        for strategy in variant_strategies:
            task = self.generate_ad_alternative(
                ad_data=ad_data,
                variant_type=variant_type,
                creativity_level=strategy['creativity_level'],
                urgency_level=strategy['urgency_level'],
                emotion_type=strategy['emotion_type'],
                filter_cliches=strategy['filter_cliches'],
                **kwargs  # Pass through other parameters like emoji_level, human_tone, etc.
            )
            tasks.append(task)
        
        try:
            results = await asyncio.gather(*tasks, return_exceptions=True)
        except Exception as e:
            raise AIProviderUnavailable(
                "creative_variant_generation",
                f"Failed to generate creative variants: {str(e)}"
            )
        
        # Process results and add variant metadata
        variants = []
        failures = []
        
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                failures.append(f"Variant {i+1}: {str(result)}")
                logger.warning(f"Failed to generate variant {i+1}: {result}")
            elif isinstance(result, dict):
                # Add variant metadata
                result['variant_number'] = i + 1
                result['variant_strategy'] = variant_strategies[i]
                result['creative_risk_level'] = risk_analysis['risk_level']
                result['approach_description'] = variant_strategies[i]['approach_description']
                variants.append(result)
        
        # Require at least one successful variant
        if not variants:
            raise AIProviderUnavailable(
                "creative_variant_generation",
                f"All variant generation failed. Failures: {'; '.join(failures)}"
            )
        
        # Add overall generation metadata
        generation_metadata = {
            'total_requested': num_variants,
            'successful_variants': len(variants),
            'failed_variants': len(failures),
            'risk_analysis': risk_analysis,
            'generation_timestamp': time.time(),
            'base_settings': {
                'creativity_level': creativity_level,
                'urgency_level': urgency_level,
                'emotion_type': emotion_type,
                'filter_cliches': filter_cliches
            }
        }
        
        # Add metadata to each variant
        for variant in variants:
            variant['generation_metadata'] = generation_metadata
        
        logger.info(f"Successfully generated {len(variants)}/{num_variants} creative variants")
        return variants
