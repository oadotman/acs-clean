#!/usr/bin/env python3
"""
Enhanced AI Prompts and Improvements for AdCopySurge Tools
Based on comprehensive audit findings.
"""

# IMPROVED PROMPTS FOR TOOL 6: AI ALTERNATIVE GENERATOR

ENHANCED_AI_PROMPTS = {
    "persuasive_rewrite": """
You are an expert copywriter specializing in high-converting ad copy. 
Rewrite the following ad to maximize persuasive impact and conversion rates:

Original Ad:
- Headline: {headline}
- Body: {body_text}  
- CTA: {cta}
- Platform: {platform}
- Target Audience: {target_audience}
- Industry: {industry}

Create a PERSUASIVE version that:
1. Uses proven persuasion techniques (social proof, urgency, authority, reciprocity)
2. Includes specific benefits over features
3. Addresses common objections
4. Creates a sense of urgency or scarcity
5. Uses power words that drive action
6. Optimizes for {platform} best practices

Format your response as:
HEADLINE: [new headline]
BODY: [new body text]
CTA: [new call-to-action]
IMPROVEMENT: [why this will perform better]
""",

    "emotional_rewrite": """
You are an expert in emotional marketing and human psychology.
Rewrite the following ad to create strong emotional connection and drive action:

Original Ad:
- Headline: {headline}
- Body: {body_text}
- CTA: {cta}
- Platform: {platform}
- Target Audience: {target_audience}

Create an EMOTIONAL version that:
1. Identifies and triggers the primary emotion (fear, desire, aspiration, frustration)
2. Uses storytelling elements or scenarios people relate to
3. Creates vivid mental images
4. Appeals to identity and self-image
5. Uses sensory language
6. Builds emotional tension that resolves with action

Format your response as:
HEADLINE: [emotionally charged headline]
BODY: [emotional body text with story/scenario]
CTA: [emotion-driven CTA]
EMOTION: [primary emotion triggered]
IMPROVEMENT: [why this emotional approach will work]
""",

    "data_driven_rewrite": """
You are a performance marketing expert who relies on data and statistics.
Rewrite the following ad to emphasize credibility through numbers, stats, and proof:

Original Ad:
- Headline: {headline}
- Body: {body_text}
- CTA: {cta}
- Platform: {platform}
- Industry: {industry}

Create a DATA-HEAVY version that:
1. Includes specific numbers, percentages, or statistics
2. Mentions customer counts, time savings, ROI improvements
3. References studies, awards, or recognition
4. Uses quantified benefits
5. Includes credibility indicators
6. Appeals to logical decision-making

Format your response as:
HEADLINE: [number/stat-focused headline]
BODY: [data-rich body with specific metrics]
CTA: [results-oriented CTA]
KEY_STATS: [the main numbers/proof points used]
IMPROVEMENT: [why data-driven approach will convert better]
""",

    "platform_optimized_rewrite": """
You are a platform-specific advertising expert with deep knowledge of {platform} best practices.
Optimize the following ad specifically for maximum performance on {platform}:

Original Ad:
- Headline: {headline}
- Body: {body_text}
- CTA: {cta}
- Current Platform: {platform}

Create a {platform}-OPTIMIZED version that:
1. Follows {platform} character limits and formatting best practices
2. Uses {platform}-specific language and tone
3. Leverages {platform} user behavior patterns
4. Optimizes for {platform} algorithm preferences
5. Uses {platform}-appropriate call-to-action phrases
6. Considers {platform} audience demographics and mindset

Platform-Specific Guidelines for {platform}:
{platform_guidelines}

Format your response as:
HEADLINE: [platform-optimized headline]
BODY: [platform-optimized body]
CTA: [platform-specific CTA]
PLATFORM_FEATURES: [specific {platform} optimizations applied]
IMPROVEMENT: [why this will perform better on {platform}]
"""
}

PLATFORM_GUIDELINES = {
    "facebook": """
- Keep headlines 5-7 words for maximum engagement
- Body text 90-125 characters performs best
- Use conversational, friendly tone
- Include social proof elements
- Visual-first platform - copy supports imagery
- Users in social browsing mindset
- Strong emotional hooks work well
- Community and connection focus
""",

    "google": """
- Headlines max 30 characters for search ads
- Descriptions under 90 characters
- Include target keywords
- Focus on immediate value proposition
- Users in problem-solving/research mode
- Be specific and direct
- Match search intent closely
- Include location if relevant
""",

    "linkedin": """
- Professional tone and language
- Longer form content acceptable (150+ chars)
- Industry-specific terminology OK
- Focus on business outcomes
- Career/professional development angle
- Authority and expertise positioning
- B2B decision-maker mindset
- Educational/thought leadership approach
""",

    "tiktok": """
- Very short copy (under 80 total characters)
- Casual, fun, trendy language
- Use current slang and expressions
- Create FOMO and urgency
- Entertainment-first mindset
- Younger demographic focus
- Viral/shareable elements
- Quick attention grabbers
"""
}

# IMPROVED SCORING ALGORITHMS

def calculate_enhanced_readability_score(text: str) -> dict:
    """Enhanced readability scoring with more nuanced analysis."""
    import textstat
    
    # Basic metrics
    flesch_score = textstat.flesch_reading_ease(text)
    grade_level = textstat.flesch_kincaid_grade(text)
    word_count = len(text.split())
    sentence_count = len([s for s in text.split('.') if s.strip()])
    
    # Enhanced scoring factors
    factors = {
        'base_readability': min(flesch_score, 100),
        'ideal_grade_level': 100 if 6 <= grade_level <= 8 else max(0, 100 - (abs(grade_level - 7) * 10)),
        'word_count_penalty': 100 if word_count <= 30 else max(0, 100 - (word_count - 30) * 2),
        'sentence_complexity': 100 if sentence_count > 0 and word_count/sentence_count <= 15 else 80,
        'power_word_bonus': calculate_power_word_score(text)
    }
    
    # Weighted final score
    weights = {
        'base_readability': 0.4,
        'ideal_grade_level': 0.25,
        'word_count_penalty': 0.2,
        'sentence_complexity': 0.1,
        'power_word_bonus': 0.05
    }
    
    final_score = sum(factors[key] * weights[key] for key in factors)
    
    return {
        'clarity_score': round(final_score, 1),
        'factors': factors,
        'recommendations': generate_readability_recommendations(factors)
    }

def calculate_power_word_score(text: str) -> float:
    """Calculate power word usage score."""
    ENHANCED_POWER_WORDS = {
        'urgency': ['now', 'today', 'immediately', 'instant', 'fast', 'quick', 'hurry', 'deadline', 'limited', 'expires'],
        'exclusivity': ['exclusive', 'secret', 'private', 'members-only', 'invitation', 'select', 'elite', 'premium'],
        'social_proof': ['proven', 'trusted', 'verified', 'recommended', 'popular', 'trending', 'bestselling'],
        'benefit': ['free', 'save', 'gain', 'profit', 'earn', 'win', 'achieve', 'success', 'results', 'guaranteed'],
        'emotion': ['amazing', 'incredible', 'stunning', 'breakthrough', 'revolutionary', 'transform', 'unleash']
    }
    
    text_lower = text.lower()
    category_scores = {}
    
    for category, words in ENHANCED_POWER_WORDS.items():
        found_words = [word for word in words if word in text_lower]
        category_scores[category] = len(found_words)
    
    total_power_words = sum(category_scores.values())
    diversity_bonus = len([cat for cat, count in category_scores.items() if count > 0]) * 5
    
    base_score = min(100, total_power_words * 15)
    return min(100, base_score + diversity_bonus)

def generate_readability_recommendations(factors: dict) -> list:
    """Generate specific readability improvement recommendations."""
    recommendations = []
    
    if factors['base_readability'] < 60:
        recommendations.append("Use shorter sentences and simpler words to improve readability")
    
    if factors['ideal_grade_level'] < 80:
        recommendations.append("Adjust complexity to target 6th-8th grade reading level for broader appeal")
    
    if factors['word_count_penalty'] < 80:
        recommendations.append("Shorten your copy - ads under 30 words typically perform better")
    
    if factors['sentence_complexity'] < 90:
        recommendations.append("Break up complex sentences into shorter, punchier statements")
    
    if factors['power_word_bonus'] < 50:
        recommendations.append("Add more power words to increase emotional impact and urgency")
    
    return recommendations

# ENHANCED CTA ANALYSIS

def analyze_cta_with_context(cta: str, platform: str, industry: str = None) -> dict:
    """Enhanced CTA analysis with industry and context awareness."""
    
    INDUSTRY_CTA_BEST_PRACTICES = {
        'saas': {
            'strong': ['start free trial', 'get demo', 'see it in action', 'try risk-free'],
            'avoid': ['learn more', 'find out more', 'discover']
        },
        'ecommerce': {
            'strong': ['buy now', 'shop now', 'add to cart', 'get yours'],
            'avoid': ['browse', 'explore', 'see more']
        },
        'services': {
            'strong': ['get quote', 'book consultation', 'schedule call', 'contact us'],
            'avoid': ['learn about', 'read more', 'view details']
        },
        'education': {
            'strong': ['enroll now', 'start learning', 'join course', 'begin today'],
            'avoid': ['find out', 'see curriculum', 'browse courses']
        }
    }
    
    basic_analysis = analyze_basic_cta(cta, platform)
    
    # Add industry-specific analysis
    if industry and industry.lower() in INDUSTRY_CTA_BEST_PRACTICES:
        industry_practices = INDUSTRY_CTA_BEST_PRACTICES[industry.lower()]
        
        cta_lower = cta.lower()
        has_industry_strong = any(strong in cta_lower for strong in industry_practices['strong'])
        has_industry_avoid = any(avoid in cta_lower for avoid in industry_practices['avoid'])
        
        industry_bonus = 20 if has_industry_strong else 0
        industry_penalty = -15 if has_industry_avoid else 0
        
        basic_analysis['cta_strength_score'] += industry_bonus + industry_penalty
        basic_analysis['cta_strength_score'] = max(0, min(100, basic_analysis['cta_strength_score']))
        
        basic_analysis['industry_analysis'] = {
            'industry': industry,
            'follows_best_practices': has_industry_strong and not has_industry_avoid,
            'recommended_ctas': industry_practices['strong'][:3]
        }
    
    return basic_analysis

def analyze_basic_cta(cta: str, platform: str) -> dict:
    """Basic CTA analysis (original functionality)."""
    # This would contain the original CTA analysis logic
    # Simplified here for brevity
    return {
        'cta_strength_score': 75,
        'word_count': len(cta.split()),
        'has_action_verb': True,
        'platform_fit': 85,
        'recommendations': ['Add more urgency', 'Make it more specific']
    }

# USAGE EXAMPLES AND INTEGRATION GUIDE

def integrate_enhanced_prompts():
    """
    Integration guide for enhanced prompts in the existing system.
    
    To integrate these improvements:
    
    1. Replace the simple prompts in ad_analysis_service.py with ENHANCED_AI_PROMPTS
    2. Add platform guidelines context to prompt formatting
    3. Update the response parsing to handle structured format
    4. Implement enhanced scoring algorithms
    5. Add industry-specific CTA analysis
    """
    
    example_integration = """
    # In ad_analysis_service.py
    
    async def _generate_ai_alternatives(self, ad: AdInput) -> List[AdAlternative]:
        alternatives = []
        
        for prompt_type, template in ENHANCED_AI_PROMPTS.items():
            try:
                # Format prompt with context
                formatted_prompt = template.format(
                    headline=ad.headline,
                    body_text=ad.body_text,
                    cta=ad.cta,
                    platform=ad.platform,
                    target_audience=ad.target_audience or "general audience",
                    industry=ad.industry or "general",
                    platform_guidelines=PLATFORM_GUIDELINES.get(ad.platform, "")
                )
                
                response = await openai.ChatCompletion.acreate(
                    model="gpt-4",  # Use GPT-4 for better results
                    messages=[
                        {"role": "system", "content": "You are an expert copywriter with 15+ years of experience creating high-converting ads."},
                        {"role": "user", "content": formatted_prompt}
                    ],
                    max_tokens=500,
                    temperature=0.7
                )
                
                # Enhanced parsing logic here
                parsed_alternative = parse_structured_response(response.choices[0].message.content)
                if parsed_alternative:
                    alternatives.append(parsed_alternative)
                    
            except Exception as e:
                logger.warning(f"Failed to generate {prompt_type} alternative: {e}")
                continue
        
        return alternatives
    """
    
    return example_integration

if __name__ == "__main__":
    # Test enhanced scoring
    test_text = "Get started today with our amazing solution that transforms your business!"
    result = calculate_enhanced_readability_score(test_text)
    print("Enhanced Readability Analysis:")
    print(f"Score: {result['clarity_score']}")
    print(f"Factors: {result['factors']}")
    print(f"Recommendations: {result['recommendations']}")
