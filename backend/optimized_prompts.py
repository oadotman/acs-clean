#!/usr/bin/env python3
"""
Production-Ready Optimized Prompts for AdCopySurge Tools
These prompts are fine-tuned for maximum output quality and conversion optimization
"""

class OptimizedPromptEngine:
    """Advanced prompt engine with context awareness and optimization techniques"""
    
    def __init__(self):
        # Industry-specific context
        self.industry_contexts = {
            'saas': 'SaaS/Software products focusing on efficiency, ROI, and scalability',
            'ecommerce': 'E-commerce products emphasizing value, quality, and urgency',
            'coaching': 'Coaching/consulting services highlighting transformation and results',
            'finance': 'Financial services emphasizing security, growth, and trust',
            'healthcare': 'Healthcare services focusing on wellness, expertise, and care',
            'real_estate': 'Real estate emphasizing investment, lifestyle, and opportunity',
            'education': 'Educational services highlighting knowledge, career advancement',
            'fitness': 'Fitness/wellness focusing on transformation, health, energy'
        }
        
        # Platform-specific optimization rules
        self.platform_rules = {
            'facebook': {
                'tone': 'conversational, social, community-focused',
                'length': 'headlines 5-7 words, body 90-125 characters',
                'triggers': 'social proof, FOMO, visual appeal',
                'audience': 'casual browsers seeking connection and entertainment'
            },
            'google': {
                'tone': 'direct, solution-focused, keyword-rich',
                'length': 'headlines max 30 chars, descriptions max 90 chars',
                'triggers': 'immediate value, search intent matching',
                'audience': 'active searchers with specific problems to solve'
            },
            'linkedin': {
                'tone': 'professional, authoritative, business-focused',
                'length': 'longer content acceptable (150+ characters)',
                'triggers': 'career growth, business outcomes, expertise',
                'audience': 'professionals seeking business advancement'
            },
            'tiktok': {
                'tone': 'casual, trendy, entertainment-first',
                'length': 'ultra-short (under 80 total characters)',
                'triggers': 'viral potential, youth culture, FOMO',
                'audience': 'younger demographics seeking entertainment and trends'
            }
        }

    def generate_persuasive_prompt(self, ad_data: dict) -> str:
        """Generate optimized persuasive rewrite prompt"""
        
        industry = ad_data.get('industry', 'general')
        platform = ad_data.get('platform', 'facebook')
        target_audience = ad_data.get('target_audience', 'general audience')
        
        industry_context = self.industry_contexts.get(industry, 'general business')
        platform_rules = self.platform_rules.get(platform, self.platform_rules['facebook'])
        
        return f"""
You are a world-class copywriter who has generated over $100M in ad revenue. You specialize in {industry_context} and have deep expertise in {platform} advertising.

CONTEXT & CONSTRAINTS:
- Industry: {industry_context}
- Platform: {platform} ({platform_rules['tone']})
- Target Audience: {target_audience}
- Platform Rules: {platform_rules['length']}
- Key Triggers: {platform_rules['triggers']}
- Audience Mindset: {platform_rules['audience']}

ORIGINAL AD TO OPTIMIZE:
- Headline: {ad_data.get('headline', '')}
- Body: {ad_data.get('body_text', '')}
- CTA: {ad_data.get('cta', '')}
- Current Performance Issues: Likely low conversion due to weak persuasion elements

TASK: Create a PERSUASIVE version using proven psychological triggers:

1. **Social Proof Integration**: Add specific numbers, customer counts, or popularity indicators
2. **Urgency & Scarcity**: Create time-sensitive or limited availability elements  
3. **Authority Positioning**: Include expertise indicators, awards, or endorsements
4. **Benefit Amplification**: Transform features into compelling emotional benefits
5. **Objection Handling**: Address the #1 reason prospects don't convert
6. **Power Word Integration**: Use high-converting action words and emotional triggers

OPTIMIZATION REQUIREMENTS:
✓ Must follow {platform} character limits and best practices
✓ Appeal specifically to {target_audience} psychology and pain points
✓ Include at least 2 persuasion principles from Cialdini's framework
✓ Use {platform_rules['triggers']} appropriate for platform
✓ Maintain brand voice while maximizing conversion potential

OUTPUT FORMAT (CRITICAL - Follow exactly):
HEADLINE: [Persuasive headline with social proof or urgency - max appropriate length]
BODY: [Benefit-focused body with objection handling - platform optimized length] 
CTA: [Action-oriented CTA with urgency - compelling and specific]
PERSUASION_ELEMENTS: [List the specific psychological triggers used]
IMPROVEMENT_REASON: [Why this version will convert better - be specific]

EXAMPLES OF EXCELLENCE:
- "Join 47,000+ [audience] who increased [benefit] by [%] in [timeframe]"  
- "Last 72 hours: [Specific benefit] or full refund guaranteed"
- "The [industry] secret that [authority figure] doesn't want you to know"

Now create the persuasive version:"""

    def generate_emotional_prompt(self, ad_data: dict) -> str:
        """Generate optimized emotional rewrite prompt"""
        
        industry = ad_data.get('industry', 'general')
        platform = ad_data.get('platform', 'facebook')
        
        # Determine primary emotion based on industry
        industry_emotions = {
            'saas': 'frustration → relief → empowerment',
            'ecommerce': 'desire → satisfaction → joy',
            'coaching': 'struggle → hope → transformation',
            'finance': 'fear → security → confidence',
            'healthcare': 'concern → trust → wellness',
            'fitness': 'dissatisfaction → motivation → pride'
        }
        
        primary_emotion = industry_emotions.get(industry, 'frustration → solution → success')
        platform_context = self.platform_rules.get(platform, self.platform_rules['facebook'])
        
        return f"""
You are an expert in emotional marketing psychology with deep understanding of human behavior triggers. You've created emotional campaigns that achieved 5x+ engagement rates.

EMOTIONAL STRATEGY BRIEF:
- Industry: {industry}
- Platform: {platform} 
- Emotional Journey: {primary_emotion}
- Platform Context: {platform_context['audience']}
- Tone Requirements: {platform_context['tone']}

ORIGINAL AD (Currently lacks emotional connection):
- Headline: {ad_data.get('headline', '')}
- Body: {ad_data.get('body_text', '')}
- CTA: {ad_data.get('cta', '')}

EMOTIONAL REWRITE MISSION:
Create an ad that triggers deep emotional response leading to immediate action.

EMOTIONAL FRAMEWORK TO APPLY:
1. **Emotional Hook**: Open with relatable pain point or aspiration
2. **Vivid Imagery**: Use sensory language that creates mental pictures
3. **Story Elements**: Include micro-narrative or scenario people relate to
4. **Identity Connection**: Appeal to who they want to become
5. **Emotional Amplification**: Build tension that resolves with action
6. **Urgency Through Emotion**: Create FOMO or fear of remaining stuck

PSYCHOLOGICAL TRIGGERS TO ACTIVATE:
- Loss Aversion: What they'll miss by not acting
- Social Identity: Who they'll become by taking action  
- Temporal Landmarks: "New year, new you" type moments
- Progress Psychology: The journey from struggle to success
- Tribal Belonging: Joining others who made the change

EMOTIONAL WORDS BANK (Use strategically):
Struggle: frustrated, overwhelmed, stuck, tired, worried, stressed
Aspiration: transform, breakthrough, freedom, confidence, success, power
Urgency: finally, tonight, imagine, discover, unlock, claim

OUTPUT FORMAT:
HEADLINE: [Emotionally charged headline that creates instant connection]
BODY: [Story-driven body text with vivid imagery and identity appeal]
CTA: [Emotion-driven CTA that feels like the natural next step]
PRIMARY_EMOTION: [The main emotion this ad triggers and why]
EMOTIONAL_JOURNEY: [The emotional path: current state → desired state]
IMPROVEMENT_REASON: [Why this emotional approach will drive action]

PLATFORM OPTIMIZATION:
- {platform_context['length']}
- {platform_context['triggers']}
- Tone: {platform_context['tone']}

Create the emotionally compelling version:"""

    def generate_data_driven_prompt(self, ad_data: dict) -> str:
        """Generate optimized data-driven rewrite prompt"""
        
        industry = ad_data.get('industry', 'general')
        platform = ad_data.get('platform', 'facebook')
        
        # Industry-specific metrics that resonate
        industry_metrics = {
            'saas': 'productivity increases, time savings, ROI percentages, user adoption rates',
            'ecommerce': 'customer satisfaction ratings, repeat purchase rates, shipping times',
            'coaching': 'success rates, income increases, goal achievement percentages',
            'finance': 'return percentages, risk reduction, growth rates, savings amounts',
            'healthcare': 'patient satisfaction, success rates, time to results, safety scores',
            'fitness': 'weight loss amounts, strength gains, time to results, success rates'
        }
        
        relevant_metrics = industry_metrics.get(industry, 'performance improvements, satisfaction rates, success metrics')
        
        return f"""
You are a performance marketing expert who relies exclusively on data-driven copy. Your ads consistently outperform because they use credible statistics and proof points that build unshakeable trust.

DATA STRATEGY CONTEXT:
- Industry: {industry}
- Platform: {platform}
- Relevant Metrics: {relevant_metrics}
- Target: Logical decision-makers who need proof before buying
- Goal: Build credibility through specific, verifiable claims

ORIGINAL AD (Lacks credible proof points):
- Headline: {ad_data.get('headline', '')}
- Body: {ad_data.get('body_text', '')}
- CTA: {ad_data.get('cta', '')}

DATA-DRIVEN TRANSFORMATION REQUIREMENTS:

1. **Specific Statistics**: Replace vague claims with exact percentages or numbers
2. **Time-Bound Results**: Include specific timeframes for achieving results
3. **Customer Volume**: Mention specific number of customers/clients served
4. **Third-Party Validation**: Reference studies, awards, certifications, or recognition
5. **Quantified Benefits**: Transform abstract benefits into measurable outcomes
6. **Comparison Data**: Show before/after or competitive advantage numbers
7. **Risk Mitigation**: Include guarantee percentages or success rates

CREDIBILITY FRAMEWORK:
- Use specific numbers (87%, 3.2x, $47K, 14 days) not round numbers
- Include source credibility ("According to [Authority]", "Featured in [Publication]")
- Add temporal proof ("In just 30 days", "Within 90 days", "After 6 months")
- Social proof numbers ("Join 12,847 customers", "Trusted by Fortune 500")

DATA POINT EXAMPLES BY INDUSTRY:
{industry}: {relevant_metrics}

STATISTICAL POWER WORDS:
- Proven, verified, measured, documented, certified, validated
- Increased by X%, reduced by X%, improved by X%, achieved X% faster
- Based on analysis of X customers/data points/studies
- Independently tested, peer-reviewed, third-party verified

OUTPUT FORMAT:
HEADLINE: [Number/statistic-focused headline with specific metric]
BODY: [Data-rich body with multiple credible proof points and timeframes]
CTA: [Results-oriented CTA that promises measurable outcomes]
KEY_STATISTICS: [List of main numbers/proof points used and their psychological impact]
DATA_SOURCES: [Types of credibility sources implied or referenced]
IMPROVEMENT_REASON: [Why this data-driven approach builds more trust and converts better]

PLATFORM CONSIDERATIONS:
- {self.platform_rules[platform]['length']}
- Tone: {self.platform_rules[platform]['tone']}
- Optimize for {self.platform_rules[platform]['audience']}

Create the credible, data-driven version:"""

    def generate_platform_optimized_prompt(self, ad_data: dict) -> str:
        """Generate platform-specific optimization prompt"""
        
        platform = ad_data.get('platform', 'facebook')
        industry = ad_data.get('industry', 'general')
        
        platform_context = self.platform_rules.get(platform, self.platform_rules['facebook'])
        
        # Platform-specific best practices and examples
        platform_examples = {
            'facebook': {
                'headlines': ['"Free Trial Started" (3 words)', '"Join 10K Users" (3 words)', '"Save 50% Today" (3 words)'],
                'body_style': 'conversational, benefit-focused, community-oriented',
                'cta_style': '"Get Started Free", "Join Community", "Try Risk-Free"',
                'winning_formula': 'Social proof + Benefit + Clear action'
            },
            'google': {
                'headlines': ['"Best CRM Software" (3 words)', '"Free Trial Available"', '"Get Quote Today"'],
                'body_style': 'direct, keyword-rich, solution-focused',
                'cta_style': '"Get Quote", "Start Trial", "Learn More"',
                'winning_formula': 'Keyword match + Value prop + Direct CTA'
            },
            'linkedin': {
                'headlines': ['"Professional Development Program"', '"Enterprise Solution"', '"Business Growth Strategy"'],
                'body_style': 'professional, outcome-focused, expertise-driven',
                'cta_style': '"Request Demo", "Download Guide", "Schedule Call"',
                'winning_formula': 'Authority + Business outcome + Professional CTA'
            },
            'tiktok': {
                'headlines': ['"OMG!"', '"Wait What?"', '"Mind Blown"'],
                'body_style': 'casual, trendy, hook-driven',
                'cta_style': '"Try Now", "Get It", "Don\'t Miss"',
                'winning_formula': 'Hook + Trend + Quick action'
            }
        }
        
        platform_best_practices = platform_examples.get(platform, platform_examples['facebook'])
        
        return f"""
You are the #1 {platform.upper()} advertising specialist with insider knowledge of what works on this platform. You've managed $50M+ in {platform} ad spend and know exactly how to optimize for {platform}'s algorithm and user behavior.

PLATFORM MASTERY BRIEF:
- Platform: {platform.upper()}
- User Mindset: {platform_context['audience']}
- Optimal Tone: {platform_context['tone']}
- Character Limits: {platform_context['length']}
- Top Triggers: {platform_context['triggers']}
- Winning Formula: {platform_best_practices['winning_formula']}

CURRENT AD (Not optimized for {platform}):
- Headline: {ad_data.get('headline', '')}
- Body: {ad_data.get('body_text', '')}
- CTA: {ad_data.get('cta', '')}

{platform.upper()} OPTIMIZATION STRATEGY:

ALGORITHM OPTIMIZATION:
✓ Follow {platform}'s character limits religiously
✓ Use {platform}-preferred language patterns and vocabulary
✓ Optimize for {platform}'s user engagement behaviors
✓ Include elements that drive {platform}-specific actions (shares, saves, clicks)
✓ Appeal to {platform}'s demographic and psychographic profile

USER BEHAVIOR OPTIMIZATION:
✓ Match how users actually browse/consume content on {platform}
✓ Use {platform}-native tone and communication style
✓ Leverage {platform}-specific social proof and trust signals
✓ Create content that feels native to {platform}'s environment
✓ Optimize for {platform}'s conversion patterns

PLATFORM-SPECIFIC ELEMENTS:
- Headlines: {platform_best_practices['headlines']}
- Body Style: {platform_best_practices['body_style']}
- CTA Examples: {platform_best_practices['cta_style']}
- Character Optimization: {platform_context['length']}

{platform.upper()} SUCCESS PATTERNS:
1. Start with {platform}-appropriate hook/opener
2. Use {platform}-native language and references
3. Include {platform}-preferred social proof types
4. Match {platform}'s typical content consumption speed
5. End with {platform}-optimized call-to-action

OUTPUT FORMAT:
HEADLINE: [Perfect for {platform} - follows all character and style requirements]
BODY: [Optimized for {platform} user behavior and algorithm preferences]
CTA: [Platform-native call-to-action that drives {platform} conversions]
PLATFORM_FEATURES: [Specific {platform} optimizations applied]
ALGORITHM_SIGNALS: [Elements that will help {platform} algorithm favor this ad]
IMPROVEMENT_REASON: [Why this version will perform better on {platform} specifically]

{platform.upper()} PERFORMANCE INDICATORS:
This ad is optimized for: {platform_context['triggers']}
Expected improvement: Higher {platform} relevance score, better cost per click, increased engagement

Create the {platform}-perfect version:"""

    def generate_context_aware_prompt(self, ad_data: dict, variant_type: str) -> str:
        """Generate context-aware prompt based on all available data"""
        
        prompt_generators = {
            'persuasive': self.generate_persuasive_prompt,
            'emotional': self.generate_emotional_prompt,
            'data_driven': self.generate_data_driven_prompt,
            'platform_optimized': self.generate_platform_optimized_prompt
        }
        
        generator = prompt_generators.get(variant_type, self.generate_persuasive_prompt)
        return generator(ad_data)

    def get_system_prompt(self, variant_type: str) -> str:
        """Get optimized system prompt for different variant types"""
        
        system_prompts = {
            'persuasive': """You are Marcus Hopkins, a legendary copywriter who has generated over $500M in advertising revenue. You wrote the ads for 47 companies that went from startup to IPO. Your persuasive copy is studied in marketing schools worldwide. You understand human psychology at the deepest level and know exactly which psychological triggers drive immediate action.""",
            
            'emotional': """You are Dr. Sarah Chen, a behavioral psychologist turned copywriter who specializes in emotional marketing. You've published research on emotional decision-making and have created campaigns that achieved 800%+ engagement increases. You understand the neurological basis of emotional responses and can craft copy that creates deep emotional connections.""",
            
            'data_driven': """You are David Martinez, the "Numbers Guy" of advertising. You only create copy backed by hard data and statistical proof. Your data-driven ads consistently outperform by 300%+ because skeptical audiences trust your evidence-based approach. You have access to performance data from 10,000+ campaigns across all industries.""",
            
            'platform_optimized': """You are Alex Thompson, the platform specialist who knows the secret algorithms and user behaviors of every major advertising platform. You've managed over $100M in ad spend across Facebook, Google, LinkedIn, TikTok, and know exactly what works on each platform. Platform executives consult you on advertising best practices."""
        }
        
        return system_prompts.get(variant_type, system_prompts['persuasive'])

    def parse_ai_response(self, response: str, variant_type: str) -> dict:
        """Enhanced AI response parsing with error handling"""
        
        try:
            # Split by common delimiters
            if '|' in response:
                parts = [part.strip() for part in response.split('|')]
            else:
                # Try line-by-line parsing
                lines = [line.strip() for line in response.split('\n') if line.strip()]
                parts = lines
            
            result = {
                'headline': '',
                'body_text': '', 
                'cta': '',
                'variant_type': variant_type,
                'improvement_reason': ''
            }
            
            # Extract fields using multiple strategies
            for part in parts:
                part_upper = part.upper()
                
                if 'HEADLINE:' in part_upper:
                    result['headline'] = self._clean_field(part.split(':', 1)[-1])
                elif 'BODY:' in part_upper:
                    result['body_text'] = self._clean_field(part.split(':', 1)[-1])
                elif 'CTA:' in part_upper:
                    result['cta'] = self._clean_field(part.split(':', 1)[-1])
                elif 'IMPROVEMENT' in part_upper or 'REASON' in part_upper:
                    result['improvement_reason'] = self._clean_field(part.split(':', 1)[-1])
            
            # Fallback parsing if structured format fails
            if not result['headline'] or not result['body_text'] or not result['cta']:
                result = self._fallback_parse(response, variant_type)
            
            # Apply character limits based on best practices
            result['headline'] = result['headline'][:60]  # Conservative limit
            result['body_text'] = result['body_text'][:200] 
            result['cta'] = result['cta'][:30]
            result['improvement_reason'] = result['improvement_reason'][:150]
            
            return result
            
        except Exception as e:
            # Ultimate fallback
            return self._create_fallback_result(variant_type, str(e))

    def _clean_field(self, text: str) -> str:
        """Clean extracted field text"""
        return text.strip().strip('"').strip("'").strip()

    def _fallback_parse(self, response: str, variant_type: str) -> dict:
        """Fallback parsing when structured format fails"""
        
        lines = [line.strip() for line in response.split('\n') if line.strip()]
        
        # Try to identify headline (usually first substantial line)
        headline = lines[0] if lines else f"Optimized {variant_type.title()}"
        
        # Try to find body (longest line or middle content)  
        body_candidates = [line for line in lines if len(line) > 30]
        body_text = body_candidates[0] if body_candidates else "Enhanced copy optimized for performance."
        
        # Try to find CTA (usually short, action-oriented)
        cta_candidates = [line for line in lines if len(line) < 20 and any(action in line.lower() for action in ['get', 'start', 'try', 'join', 'buy', 'claim'])]
        cta = cta_candidates[0] if cta_candidates else "Take Action"
        
        return {
            'headline': headline[:60],
            'body_text': body_text[:200],
            'cta': cta[:30],
            'variant_type': variant_type,
            'improvement_reason': f"AI-generated {variant_type} optimization with enhanced appeal"
        }

    def _create_fallback_result(self, variant_type: str, error: str) -> dict:
        """Create fallback result when parsing completely fails"""
        
        templates = {
            'persuasive': {
                'headline': 'Proven Results You Can Trust',
                'body_text': 'Join thousands who have achieved remarkable success with our proven system.',
                'cta': 'Get Started Now'
            },
            'emotional': {
                'headline': 'Transform Your Life Today',
                'body_text': 'Imagine finally achieving what you\'ve always dreamed of.',
                'cta': 'Claim Your Success'
            },
            'data_driven': {
                'headline': '87% Proven Success Rate',
                'body_text': 'Based on analysis of 10,000+ customers who achieved measurable results.',
                'cta': 'See Results'
            },
            'platform_optimized': {
                'headline': 'Optimized for Performance',
                'body_text': 'Crafted specifically for maximum engagement and conversions.',
                'cta': 'Learn More'
            }
        }
        
        template = templates.get(variant_type, templates['persuasive'])
        
        return {
            'headline': template['headline'],
            'body_text': template['body_text'], 
            'cta': template['cta'],
            'variant_type': variant_type,
            'improvement_reason': f"Template-based {variant_type} optimization (parsing error: {error[:50]})"
        }

# USAGE EXAMPLE
if __name__ == "__main__":
    prompt_engine = OptimizedPromptEngine()
    
    sample_ad = {
        'headline': 'Amazing Software Solution',
        'body_text': 'Our software helps businesses be more efficient.',
        'cta': 'Learn More',
        'platform': 'facebook',
        'industry': 'saas',
        'target_audience': 'small business owners'
    }
    
    # Generate optimized prompts
    for variant_type in ['persuasive', 'emotional', 'data_driven', 'platform_optimized']:
        prompt = prompt_engine.generate_context_aware_prompt(sample_ad, variant_type)
        system_prompt = prompt_engine.get_system_prompt(variant_type)
        
        print(f"\n{'='*50}")
        print(f"{variant_type.upper()} VARIANT")
        print(f"{'='*50}")
        print(f"System: {system_prompt[:100]}...")
        print(f"Prompt: {prompt[:200]}...")
