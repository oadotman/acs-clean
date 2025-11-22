"""
ROI Copy Generator Tool - Premium positioning and profit-focused copy variants
Creates 3-5 profit-optimized copy variations with ROI messaging and premium positioning
Now with platform-specific ROI types (financial for LinkedIn, experiential for TikTok, etc.)
"""

import time
import random
from typing import Dict, Any, List, Optional, Tuple
from ..core import ToolRunner, ToolInput, ToolOutput, ToolConfig, ToolType
from ..exceptions import ToolValidationError
from ..platform_adapter import platform_adapter


class ROICopyGeneratorToolRunner(ToolRunner):
    """
    ROI Copy Generator Tool
    
    Generates high-converting copy variants focused on:
    - ROI and return on investment messaging
    - Premium positioning and value perception
    - Profit optimization through pricing psychology
    - Financial benefit emphasis
    - Investment framing for higher price points
    - Creates 3-5 variations with different ROI angles
    """
    
    def __init__(self, config: ToolConfig):
        super().__init__(config)
        
        # ROI messaging frameworks
        self.roi_frameworks = {
            'investment_return': {
                'patterns': [
                    "Turn ${price} into ${multiplier}x more results",
                    "Get ${multiplier}x the value for your ${price} investment",
                    "${multiplier}x ROI on your ${price} investment in just {timeframe}",
                    "Your ${price} investment pays for itself {multiplier} times over"
                ],
                'multipliers': [3, 5, 7, 10, 15, 20],
                'focus': 'financial return'
            },
            'cost_savings': {
                'patterns': [
                    "Save ${savings} in {timeframe} - worth every penny of ${price}",
                    "Avoid ${cost_avoided} in mistakes with this ${price} investment",
                    "${price} now saves you ${savings} later - guaranteed ROI",
                    "The ${price} investment that saves ${savings} in wasted time"
                ],
                'savings_multipliers': [5, 10, 20, 50, 100],
                'focus': 'cost avoidance'
            },
            'time_value': {
                'patterns': [
                    "Worth ${time_value} in time savings - only ${price}",
                    "${price} saves you {hours} hours worth ${time_value}",
                    "Your time is worth more than the ${price} investment",
                    "${time_value} value for a ${price} investment - clear winner"
                ],
                'time_ranges': [(10, 20), (20, 50), (50, 100)],
                'focus': 'time efficiency'
            },
            'premium_positioning': {
                'patterns': [
                    "Professional-grade {category} for serious {audience}",
                    "Enterprise-level {category} at {price} - exceptional value",
                    "Premium {category} that pays for itself",
                    "Investment-grade {category} for maximum ROI"
                ],
                'descriptors': ['professional', 'enterprise', 'premium', 'executive'],
                'focus': 'quality positioning'
            },
            'scarcity_value': {
                'patterns': [
                    "Limited {category} - increasing in value",
                    "Exclusive {category} - {price} won't last",
                    "High-demand {category} - secure your ROI now",
                    "Premium {category} - value increases with demand"
                ],
                'urgency_factors': ['limited availability', 'increasing demand', 'exclusive access'],
                'focus': 'exclusivity premium'
            }
        }
        
        # Premium positioning vocabularies
        self.premium_vocabulary = {
            'value_words': [
                'investment', 'returns', 'profit', 'yield', 'payback',
                'value', 'worth', 'savings', 'efficiency', 'optimization'
            ],
            'premium_adjectives': [
                'premium', 'professional', 'enterprise', 'executive', 'elite',
                'advanced', 'sophisticated', 'high-performance', 'cutting-edge'
            ],
            'roi_verbs': [
                'maximize', 'optimize', 'amplify', 'multiply', 'accelerate',
                'generate', 'deliver', 'produce', 'create', 'unlock'
            ],
            'financial_outcomes': [
                'higher profits', 'increased revenue', 'better ROI', 'cost savings',
                'efficiency gains', 'competitive advantage', 'market edge'
            ]
        }
        
        # Psychological pricing triggers
        self.pricing_psychology = {
            'anchoring': {
                'techniques': [
                    "Normally ${anchor}, now only ${price}",
                    "Compare to ${anchor} solutions - ${price} is a steal",
                    "Industry standard: ${anchor}. Our price: ${price}",
                    "Others charge ${anchor}. You pay just ${price}"
                ],
                'anchor_multipliers': [2, 3, 5, 7, 10]
            },
            'loss_aversion': {
                'techniques': [
                    "Don't lose ${loss} - invest ${price} instead",
                    "Avoid ${loss} costs with ${price} solution",
                    "Skip the ${loss} mistake - ${price} prevents it",
                    "Save yourself from ${loss} - ${price} insurance"
                ],
                'loss_multipliers': [5, 10, 20, 50]
            },
            'bundling_value': {
                'techniques': [
                    "Everything included for ${price} - ${value} total value",
                    "${components} bundled - ${value} value for ${price}",
                    "Complete package: ${value} worth for ${price}",
                    "All-inclusive ${price} - saves ${saved} in separate purchases"
                ],
                'bundle_multipliers': [1.5, 2, 3, 4]
            }
        }
        
        # Industry-specific ROI angles
        self.industry_roi_angles = {
            'business': {
                'metrics': ['revenue', 'profit margins', 'operational efficiency', 'customer acquisition cost'],
                'timeframes': ['quarterly', 'annually', 'within 6 months', 'first year'],
                'outcomes': ['increased sales', 'reduced costs', 'improved productivity', 'competitive advantage']
            },
            'finance': {
                'metrics': ['portfolio returns', 'risk reduction', 'yield optimization', 'capital efficiency'],
                'timeframes': ['monthly', 'quarterly', 'annually', '3-5 years'],
                'outcomes': ['higher returns', 'reduced risk', 'diversified income', 'wealth building']
            },
            'health': {
                'metrics': ['time savings', 'health improvements', 'medical cost savings', 'quality of life'],
                'timeframes': ['immediately', 'within weeks', '3 months', 'long-term'],
                'outcomes': ['better health', 'saved time', 'reduced medical bills', 'improved wellbeing']
            },
            'education': {
                'metrics': ['skill development', 'career advancement', 'income potential', 'knowledge retention'],
                'timeframes': ['course completion', '6 months', '1 year', 'career lifetime'],
                'outcomes': ['higher salary', 'better job prospects', 'skill mastery', 'career growth']
            },
            'technology': {
                'metrics': ['efficiency gains', 'automation savings', 'error reduction', 'scalability'],
                'timeframes': ['implementation', 'first month', 'quarterly', 'annually'],
                'outcomes': ['faster processes', 'reduced errors', 'time savings', 'scalable growth']
            }
        }
        
        # Copy variation strategies
        self.variation_strategies = [
            'roi_focused',      # Heavy on ROI calculations
            'premium_brand',    # Premium positioning
            'value_comparison', # Against alternatives
            'time_sensitive',   # Urgency with value
            'results_proof'     # Evidence-based ROI
        ]

    def _generate_platform_roi_variations(self, original_copy: Dict, roi_type: str,
                                         industry: str, platform: str, pricing_info: Dict) -> List[Dict]:
        """
        Generate ROI variations appropriate for platform

        Different platforms emphasize different types of ROI:
        - financial: Traditional financial ROI (LinkedIn, Google)
        - emotional_and_financial: Mix of financial and emotional (Facebook)
        - experiential: Experience-based ROI (TikTok)
        - lifestyle_and_emotional: Lifestyle and aspiration ROI (Instagram)
        - financial_and_strategic: Business and strategic ROI (LinkedIn)
        """
        variations = []

        if roi_type == "financial":
            # Traditional financial ROI (good for LinkedIn, Google)
            variations.append(self._create_financial_roi_variation(original_copy, pricing_info))

        elif roi_type == "emotional_and_financial":
            # Mix of financial and emotional (good for Facebook)
            variations.append(self._create_time_roi_variation(original_copy))
            variations.append(self._create_stress_reduction_variation(original_copy))
            variations.append(self._create_financial_roi_variation(original_copy, pricing_info))

        elif roi_type == "experiential":
            # Experience-based ROI (good for TikTok)
            variations.append(self._create_fun_factor_variation(original_copy))
            variations.append(self._create_lifestyle_upgrade_variation(original_copy))

        elif roi_type == "lifestyle_and_emotional":
            # Lifestyle and aspiration ROI (good for Instagram)
            variations.append(self._create_status_roi_variation(original_copy))
            variations.append(self._create_confidence_roi_variation(original_copy))

        elif roi_type == "financial_and_strategic":
            # Business and strategic ROI (good for LinkedIn)
            variations.append(self._create_financial_roi_variation(original_copy, pricing_info))
            variations.append(self._create_strategic_roi_variation(original_copy))

        return variations

    def _create_time_roi_variation(self, original_copy: Dict) -> Dict:
        """Create variation emphasizing time saved"""
        return {
            "headline": "Save 10+ Hours Per Week",
            "body_text": "Stop wasting time on manual tasks. Reclaim your schedule and focus on what matters.",
            "cta": "Get Your Time Back",
            "roi_type": "time_savings",
            "explanation": "Emotional ROI: Time is valuable - emphasizes time saved",
            "analysis": {"key_elements": ["time_savings", "emotional_appeal"], "tone": "practical",
                        "psychological_triggers": ["loss_aversion", "efficiency"]}
        }

    def _create_stress_reduction_variation(self, original_copy: Dict) -> Dict:
        """Create variation emphasizing stress reduction"""
        return {
            "headline": "Finally, Peace of Mind",
            "body_text": "End the stress of complicated processes. Sleep better knowing it's handled.",
            "cta": "Reduce Your Stress",
            "roi_type": "stress_reduction",
            "explanation": "Emotional ROI: Mental health benefits",
            "analysis": {"key_elements": ["emotional_wellbeing", "stress_reduction"], "tone": "empathetic",
                        "psychological_triggers": ["fear_relief", "emotional_appeal"]}
        }

    def _create_fun_factor_variation(self, original_copy: Dict) -> Dict:
        """Create variation emphasizing fun/entertainment (TikTok)"""
        return {
            "headline": "Make It Fun Again",
            "body_text": "Who says it has to be boring? Join the fun and see why everyone's obsessed.",
            "cta": "Try It For The Vibes",
            "roi_type": "entertainment",
            "explanation": "Experience ROI: Fun and entertainment value for TikTok",
            "analysis": {"key_elements": ["entertainment", "social_currency"], "tone": "playful",
                        "psychological_triggers": ["peer_validation", "trend_relevance"]}
        }

    def _create_status_roi_variation(self, original_copy: Dict) -> Dict:
        """Create variation emphasizing status/appearance (Instagram)"""
        return {
            "headline": "Elevate Your Game",
            "body_text": "Join the inner circle. The upgrade that shows you're ahead of the curve.",
            "cta": "Level Up",
            "roi_type": "status_and_recognition",
            "explanation": "Lifestyle ROI: Social status and recognition for Instagram",
            "analysis": {"key_elements": ["aspiration", "status"], "tone": "aspirational",
                        "psychological_triggers": ["social_proof", "exclusivity"]}
        }

    def _create_confidence_roi_variation(self, original_copy: Dict) -> Dict:
        """Create variation emphasizing confidence boost (Instagram)"""
        return {
            "headline": "Feel Amazing, Look Amazing",
            "body_text": "The confidence boost you've been looking for. Transform how you show up every day.",
            "cta": "Transform Now",
            "roi_type": "confidence_boost",
            "explanation": "Emotional ROI: Self-confidence and transformation",
            "analysis": {"key_elements": ["transformation", "self_improvement"], "tone": "empowering",
                        "psychological_triggers": ["aspiration", "emotional_appeal"]}
        }

    def _create_lifestyle_upgrade_variation(self, original_copy: Dict) -> Dict:
        """Create variation emphasizing lifestyle improvement"""
        return {
            "headline": "Upgrade Your Lifestyle",
            "body_text": "Level up every aspect of your daily routine. The lifestyle change you deserve.",
            "cta": "Start Living Better",
            "roi_type": "lifestyle_improvement",
            "explanation": "Experience ROI: Overall lifestyle enhancement",
            "analysis": {"key_elements": ["lifestyle", "self_improvement"], "tone": "aspirational",
                        "psychological_triggers": ["aspiration", "progress_momentum"]}
        }

    def _create_financial_roi_variation(self, original_copy: Dict, pricing_info: Dict) -> Dict:
        """Create traditional financial ROI variation"""
        price = pricing_info.get('price', 99)
        multiplier = random.choice([3, 5, 7, 10])
        return_value = price * multiplier

        return {
            "headline": f"Turn ${price} Into ${return_value} in Value",
            "body_text": f"{multiplier}x ROI on your investment. Pay for itself and then some.",
            "cta": "Calculate My ROI",
            "roi_type": "financial_return",
            "explanation": "Financial ROI: Direct monetary return on investment",
            "analysis": {"key_elements": ["ROI", "financial_benefit", "numbers"], "tone": "data_driven",
                        "psychological_triggers": ["anchoring", "loss_aversion"]}
        }

    def _create_strategic_roi_variation(self, original_copy: Dict) -> Dict:
        """Create strategic business ROI variation (LinkedIn)"""
        return {
            "headline": "Strategic Advantage for Forward-Thinking Leaders",
            "body_text": "Gain competitive edge through proven strategies. Investment in your business growth.",
            "cta": "Explore Strategic Value",
            "roi_type": "strategic_advantage",
            "explanation": "Strategic ROI: Long-term business positioning",
            "analysis": {"key_elements": ["authority", "strategy", "business_value"], "tone": "professional",
                        "psychological_triggers": ["authority", "credibility"]}
        }

    async def run(self, input_data: ToolInput) -> ToolOutput:
        """Generate ROI-optimized copy variations with platform-specific ROI types"""
        start_time = time.time()

        try:
            # Extract key information
            original_copy = {
                'headline': input_data.headline,
                'body_text': input_data.body_text,
                'cta': input_data.cta
            }

            industry = input_data.industry.lower() if input_data.industry else 'business'
            platform = input_data.platform.lower()

            # Get platform-specific ROI type
            roi_type = platform_adapter.get_platform_roi_type(platform)

            # Parse pricing information if available
            pricing_info = self._extract_pricing_info(original_copy)

            # Generate platform-appropriate ROI variations
            variations = self._generate_platform_roi_variations(
                original_copy, roi_type, industry, platform, pricing_info
            )

            # If not enough variations, add from standard strategies
            if len(variations) < 3:
                for i, strategy in enumerate(self.variation_strategies):
                    if len(variations) >= 5:  # Limit to 5 variations total
                        break

                    variation = await self._generate_variation(
                        original_copy, strategy, industry, platform, pricing_info, len(variations) + 1
                    )
                    variations.append(variation)
            
            # Analyze and score variations
            variation_analysis = self._analyze_variations(variations, original_copy)
            
            # Calculate performance scores
            roi_score = self._calculate_roi_score(variations, pricing_info)
            premium_score = self._calculate_premium_score(variations)
            conversion_score = self._calculate_conversion_score(variations)
            
            # Generate recommendations
            recommendations = self._generate_recommendations(
                variations, variation_analysis, pricing_info
            )
            
            # Prepare scores
            scores = {
                'roi_optimization_score': roi_score,
                'premium_positioning_score': premium_score,
                'conversion_potential_score': conversion_score,
                'overall_generator_score': (roi_score + premium_score + conversion_score) / 3
            }
            
            # Detailed insights
            insights = {
                'variation_count': len(variations),
                'pricing_analysis': pricing_info,
                'industry_optimization': industry,
                'variation_analysis': variation_analysis,
                'roi_elements_used': self._count_roi_elements(variations),
                'premium_positioning_strength': premium_score,
                'best_performing_strategy': variation_analysis.get('top_strategy', 'roi_focused'),
                'conversion_optimization': {
                    'roi_messaging': len([v for v in variations if 'ROI' in v.get('analysis', {}).get('key_elements', [])]),
                    'premium_positioning': len([v for v in variations if 'premium' in v.get('analysis', {}).get('tone', '')]),
                    'urgency_integration': len([v for v in variations if 'urgency' in v.get('analysis', {}).get('psychological_triggers', [])])
                }
            }
            
            execution_time = time.time() - start_time
            
            return ToolOutput(
                tool_name=self.name,
                tool_type=self.tool_type,
                success=True,
                scores=scores,
                insights=insights,
                recommendations=recommendations,
                variations=variations,
                execution_time=execution_time,
                request_id=input_data.request_id,
                confidence_score=self._calculate_confidence(variations, insights)
            )
            
        except Exception as e:
            execution_time = time.time() - start_time
            
            return ToolOutput(
                tool_name=self.name,
                tool_type=self.tool_type,
                success=False,
                execution_time=execution_time,
                request_id=input_data.request_id,
                error_message=f"ROI copy generation failed: {str(e)}"
            )
    
    def _extract_pricing_info(self, copy: Dict[str, str]) -> Dict[str, Any]:
        """Extract pricing information from original copy"""
        import re
        
        full_text = f"{copy['headline']} {copy['body_text']} {copy['cta']}"
        
        # Look for price patterns
        price_patterns = [
            r'\$(\d+(?:,\d{3})*(?:\.\d{2})?)',  # $100, $1,000, $99.99
            r'(\d+)(?:\s*dollars?)',             # 100 dollars
            r'only\s*(\d+)',                     # only 99
            r'just\s*\$?(\d+)',                  # just $50
        ]
        
        prices_found = []
        for pattern in price_patterns:
            matches = re.finditer(pattern, full_text, re.IGNORECASE)
            for match in matches:
                try:
                    price_str = match.group(1).replace(',', '')
                    price = float(price_str)
                    prices_found.append(price)
                except ValueError:
                    continue
        
        # Determine primary price
        primary_price = None
        if prices_found:
            # Use the most common price or the first one found
            primary_price = prices_found[0]
        
        # Look for pricing tiers or ranges
        has_multiple_tiers = len(set(prices_found)) > 1
        price_range = (min(prices_found), max(prices_found)) if len(prices_found) > 1 else None
        
        return {
            'primary_price': primary_price,
            'all_prices': prices_found,
            'has_pricing': bool(prices_found),
            'has_multiple_tiers': has_multiple_tiers,
            'price_range': price_range,
            'estimated_price_tier': self._determine_price_tier(primary_price) if primary_price else 'unknown'
        }
    
    def _determine_price_tier(self, price: float) -> str:
        """Determine price tier for positioning strategy"""
        if price < 50:
            return 'budget'
        elif price < 200:
            return 'mid_market'
        elif price < 500:
            return 'premium'
        elif price < 2000:
            return 'luxury'
        else:
            return 'enterprise'
    
    async def _generate_variation(self, original: Dict, strategy: str, industry: str, 
                                 platform: str, pricing: Dict, variation_id: int) -> Dict[str, Any]:
        """Generate a single copy variation using the specified strategy"""
        
        variation = {
            'id': variation_id,
            'strategy': strategy,
            'headline': '',
            'body_text': '',
            'cta': '',
            'analysis': {
                'key_elements': [],
                'psychological_triggers': [],
                'roi_angle': '',
                'tone': '',
                'target_audience': ''
            }
        }
        
        # Generate based on strategy
        if strategy == 'roi_focused':
            variation = await self._generate_roi_focused_variation(original, industry, pricing, variation)
        elif strategy == 'premium_brand':
            variation = await self._generate_premium_brand_variation(original, industry, pricing, variation)
        elif strategy == 'value_comparison':
            variation = await self._generate_value_comparison_variation(original, industry, pricing, variation)
        elif strategy == 'time_sensitive':
            variation = await self._generate_time_sensitive_variation(original, industry, pricing, variation)
        elif strategy == 'results_proof':
            variation = await self._generate_results_proof_variation(original, industry, pricing, variation)
        
        return variation
    
    async def _generate_roi_focused_variation(self, original: Dict, industry: str, 
                                            pricing: Dict, variation: Dict) -> Dict[str, Any]:
        """Generate ROI-focused variation with financial emphasis"""
        framework = self.roi_frameworks['investment_return']
        
        # Calculate ROI multipliers
        price = pricing.get('primary_price', 100)
        multiplier = random.choice(framework['multipliers'])
        
        # ROI-focused headline
        roi_headlines = [
            f"{multiplier}x ROI in 90 days or your money back",
            f"Turn ${price} into ${price * multiplier} worth of results",
            f"{multiplier}x return on your ${price} investment - guaranteed",
            f"${price} investment → ${price * multiplier} in value creation"
        ]
        
        variation['headline'] = random.choice(roi_headlines)
        
        # ROI-focused body text
        roi_benefits = self.industry_roi_angles.get(industry, self.industry_roi_angles['business'])
        primary_outcome = random.choice(roi_benefits['outcomes'])
        timeframe = random.choice(roi_benefits['timeframes'])
        
        variation['body_text'] = (
            f"Smart businesses invest ${price} to unlock {primary_outcome} {timeframe}. "
            f"Our proven system delivers {multiplier}x returns through {primary_outcome}. "
            f"Every dollar invested generates ${multiplier} in measurable value. "
            f"Join {random.randint(1000, 5000)} businesses already seeing exceptional ROI."
        )
        
        # ROI-focused CTA
        roi_ctas = [
            f"Calculate My {multiplier}x ROI Now",
            f"Start My ${price} → ${price * multiplier} Journey",
            f"Unlock {multiplier}x Returns Today",
            f"Get {multiplier}x ROI Guarantee"
        ]
        
        variation['cta'] = random.choice(roi_ctas)
        
        # Analysis
        variation['analysis'].update({
            'key_elements': ['ROI calculation', 'financial returns', 'measurable outcomes'],
            'psychological_triggers': ['greed', 'social_proof', 'authority'],
            'roi_angle': f"{multiplier}x financial return",
            'tone': 'financial/analytical',
            'target_audience': 'business decision makers'
        })
        
        return variation
    
    async def _generate_premium_brand_variation(self, original: Dict, industry: str, 
                                              pricing: Dict, variation: Dict) -> Dict[str, Any]:
        """Generate premium positioning variation"""
        framework = self.roi_frameworks['premium_positioning']
        
        # Premium vocabulary
        premium_adj = random.choice(self.premium_vocabulary['premium_adjectives'])
        value_word = random.choice(self.premium_vocabulary['value_words'])
        
        # Premium headline
        premium_headlines = [
            f"{premium_adj.title()} Grade Solution - Exceptional {value_word.title()}",
            f"Enterprise-Level Results for Serious Professionals",
            f"Premium {industry.title()} Solution - Worth Every Penny",
            f"Professional-Grade {value_word.title()} - Unmatched Quality"
        ]
        
        variation['headline'] = random.choice(premium_headlines)
        
        # Premium body text
        price = pricing.get('primary_price', 100)
        
        variation['body_text'] = (
            f"Don't settle for amateur solutions. This {premium_adj} system delivers "
            f"enterprise-level results that justify every dollar of your ${price} investment. "
            f"Used by industry leaders who demand excellence and measurable {value_word}. "
            f"The {premium_adj} choice for professionals who understand quality pays for itself."
        )
        
        # Premium CTA
        premium_ctas = [
            "Invest in Premium Quality",
            "Choose Professional Excellence",
            "Access Enterprise Solution",
            "Secure Premium Advantage"
        ]
        
        variation['cta'] = random.choice(premium_ctas)
        
        # Analysis
        variation['analysis'].update({
            'key_elements': ['premium positioning', 'quality emphasis', 'professional targeting'],
            'psychological_triggers': ['authority', 'exclusivity', 'status'],
            'roi_angle': 'quality investment',
            'tone': 'premium/professional',
            'target_audience': 'high-value customers'
        })
        
        return variation
    
    async def _generate_value_comparison_variation(self, original: Dict, industry: str, 
                                                  pricing: Dict, variation: Dict) -> Dict[str, Any]:
        """Generate value comparison variation"""
        price = pricing.get('primary_price', 100)
        anchor_price = price * random.choice([3, 5, 7, 10])
        
        # Comparison headline
        comparison_headlines = [
            f"${anchor_price} Value for Only ${price} - Limited Time",
            f"Compare: Others ${anchor_price}, You Pay ${price}",
            f"${price} Gets You ${anchor_price} Worth of Results",
            f"Industry Standard ${anchor_price} - Your Price ${price}"
        ]
        
        variation['headline'] = random.choice(comparison_headlines)
        
        # Comparison body text
        savings = anchor_price - price
        
        variation['body_text'] = (
            f"Why pay ${anchor_price} elsewhere when you can get the same results for ${price}? "
            f"Our optimized approach delivers identical outcomes at ${savings} savings. "
            f"Compare the value: ${anchor_price} competitors vs. ${price} smart solution. "
            f"Same results, better price, superior ROI - the choice is obvious."
        )
        
        # Comparison CTA
        comparison_ctas = [
            f"Save ${savings} Today",
            f"Choose the ${price} Advantage",
            "Compare Value Now",
            "Get More for Less"
        ]
        
        variation['cta'] = random.choice(comparison_ctas)
        
        # Analysis
        variation['analysis'].update({
            'key_elements': ['price comparison', 'value proposition', 'savings emphasis'],
            'psychological_triggers': ['anchoring', 'loss_aversion', 'scarcity'],
            'roi_angle': f'${savings} cost savings',
            'tone': 'comparative/analytical',
            'target_audience': 'cost-conscious buyers'
        })
        
        return variation
    
    async def _generate_time_sensitive_variation(self, original: Dict, industry: str, 
                                               pricing: Dict, variation: Dict) -> Dict[str, Any]:
        """Generate time-sensitive urgency variation"""
        time_framework = self.roi_frameworks['time_value']
        price = pricing.get('primary_price', 100)
        
        # Time-sensitive headline
        urgency_headlines = [
            f"${price} Today = ${price * 10} Value Tomorrow - Act Fast",
            f"Price Increases Soon - Lock in ${price} ROI Now",
            f"Last Chance: ${price} Investment, Unlimited Returns",
            f"24hrs Left: ${price} For Lifetime Value"
        ]
        
        variation['headline'] = random.choice(urgency_headlines)
        
        # Urgency body text with value
        time_multiplier = random.choice([2, 3, 5, 7])
        
        variation['body_text'] = (
            f"Smart investors act fast. This ${price} opportunity won't last - "
            f"we're raising prices {time_multiplier}x next week. "
            f"Every day you wait costs you potential returns. "
            f"Secure your ${price} investment before it becomes ${price * time_multiplier}. "
            f"Limited availability - increasing demand drives higher prices."
        )
        
        # Urgent CTA
        urgent_ctas = [
            f"Lock in ${price} Price Now",
            "Secure Before Price Increase",
            "Act Fast - Save Big",
            f"Get ${price} Rate Today Only"
        ]
        
        variation['cta'] = random.choice(urgent_ctas)
        
        # Analysis
        variation['analysis'].update({
            'key_elements': ['urgency', 'price increase threat', 'scarcity'],
            'psychological_triggers': ['urgency', 'scarcity', 'loss_aversion'],
            'roi_angle': 'avoid future higher costs',
            'tone': 'urgent/persuasive',
            'target_audience': 'action-oriented buyers'
        })
        
        return variation
    
    async def _generate_results_proof_variation(self, original: Dict, industry: str, 
                                              pricing: Dict, variation: Dict) -> Dict[str, Any]:
        """Generate results-proof variation with evidence"""
        price = pricing.get('primary_price', 100)
        roi_multiplier = random.choice([3, 5, 7, 10])
        
        # Results-proof headline
        proof_headlines = [
            f"Proven: ${price} → ${price * roi_multiplier} Results in 90 Days",
            f"Case Study: ${roi_multiplier}x ROI on ${price} Investment",
            f"Documented: {random.randint(85, 97)}% Get {roi_multiplier}x Returns",
            f"Verified Results: ${price} Generates ${price * roi_multiplier} Value"
        ]
        
        variation['headline'] = random.choice(proof_headlines)
        
        # Evidence-based body text
        success_rate = random.randint(85, 97)
        customer_count = random.choice([500, 1000, 2500, 5000])
        
        variation['body_text'] = (
            f"Don't take our word for it - see the data. {success_rate}% of our "
            f"{customer_count}+ customers achieve {roi_multiplier}x ROI within 90 days. "
            f"Independent analysis confirms: ${price} investment consistently generates "
            f"${price * roi_multiplier} in measurable returns. Documented case studies "
            f"prove this system delivers predictable, profitable results."
        )
        
        # Evidence CTA
        proof_ctas = [
            "See the Proof Yourself",
            f"Join {success_rate}% Success Rate",
            "View Case Studies",
            "Get Documented Results"
        ]
        
        variation['cta'] = random.choice(proof_ctas)
        
        # Analysis
        variation['analysis'].update({
            'key_elements': ['social proof', 'statistics', 'case studies'],
            'psychological_triggers': ['authority', 'social_proof', 'credibility'],
            'roi_angle': f'documented {roi_multiplier}x returns',
            'tone': 'evidence-based/credible',
            'target_audience': 'analytical buyers'
        })
        
        return variation
    
    def _analyze_variations(self, variations: List[Dict], original: Dict) -> Dict[str, Any]:
        """Analyze generated variations for quality and effectiveness"""
        analysis = {
            'strategy_distribution': {},
            'roi_messaging_strength': {},
            'psychological_trigger_usage': {},
            'top_strategy': '',
            'avg_roi_multiplier': 0,
            'premium_positioning_count': 0
        }
        
        # Count strategies
        for variation in variations:
            strategy = variation['strategy']
            analysis['strategy_distribution'][strategy] = analysis['strategy_distribution'].get(strategy, 0) + 1
        
        # Analyze ROI messaging strength
        roi_scores = []
        for variation in variations:
            roi_elements = variation.get('analysis', {}).get('key_elements', [])
            roi_score = len([elem for elem in roi_elements if any(roi_word in elem.lower() 
                           for roi_word in ['roi', 'return', 'investment', 'value', 'profit'])])
            roi_scores.append(roi_score)
            analysis['roi_messaging_strength'][variation['strategy']] = roi_score
        
        # Count psychological triggers
        all_triggers = []
        for variation in variations:
            triggers = variation.get('analysis', {}).get('psychological_triggers', [])
            all_triggers.extend(triggers)
        
        analysis['psychological_trigger_usage'] = {
            trigger: all_triggers.count(trigger) for trigger in set(all_triggers)
        }
        
        # Determine top strategy (highest ROI score)
        if roi_scores:
            top_idx = roi_scores.index(max(roi_scores))
            analysis['top_strategy'] = variations[top_idx]['strategy']
        
        # Count premium positioning
        analysis['premium_positioning_count'] = len([
            v for v in variations if 'premium' in v.get('analysis', {}).get('tone', '').lower()
        ])
        
        return analysis
    
    def _calculate_roi_score(self, variations: List[Dict], pricing: Dict) -> float:
        """Calculate ROI optimization score"""
        score = 60  # Base score
        
        # Has pricing information
        if pricing.get('has_pricing', False):
            score += 15
        
        # ROI elements in variations
        roi_count = 0
        for variation in variations:
            roi_elements = variation.get('analysis', {}).get('key_elements', [])
            if any('roi' in elem.lower() or 'return' in elem.lower() for elem in roi_elements):
                roi_count += 1
        
        score += (roi_count / len(variations)) * 20
        
        # Financial language usage
        financial_terms = ['investment', 'return', 'profit', 'value', 'savings', 'roi']
        financial_usage = 0
        
        for variation in variations:
            full_text = f"{variation['headline']} {variation['body_text']} {variation['cta']}".lower()
            for term in financial_terms:
                if term in full_text:
                    financial_usage += 1
                    break
        
        score += (financial_usage / len(variations)) * 15
        
        return min(100, score)
    
    def _calculate_premium_score(self, variations: List[Dict]) -> float:
        """Calculate premium positioning score"""
        score = 50  # Base score
        
        premium_words = self.premium_vocabulary['premium_adjectives']
        premium_count = 0
        
        for variation in variations:
            full_text = f"{variation['headline']} {variation['body_text']} {variation['cta']}".lower()
            for word in premium_words:
                if word in full_text:
                    premium_count += 1
                    break
        
        score += (premium_count / len(variations)) * 30
        
        # Quality-focused messaging
        quality_terms = ['professional', 'enterprise', 'premium', 'quality', 'excellence']
        quality_usage = 0
        
        for variation in variations:
            full_text = f"{variation['headline']} {variation['body_text']} {variation['cta']}".lower()
            for term in quality_terms:
                if term in full_text:
                    quality_usage += 1
                    break
        
        score += (quality_usage / len(variations)) * 20
        
        return min(100, score)
    
    def _calculate_conversion_score(self, variations: List[Dict]) -> float:
        """Calculate conversion potential score"""
        score = 65  # Base score
        
        # Check for conversion elements
        conversion_elements = {
            'urgency': ['now', 'today', 'limited', 'fast', 'immediate'],
            'social_proof': ['customers', 'proven', 'thousands', 'success'],
            'risk_reversal': ['guarantee', 'money back', 'risk-free', 'try'],
            'benefit_focus': ['get', 'achieve', 'unlock', 'generate', 'create']
        }
        
        element_scores = []
        for variation in variations:
            full_text = f"{variation['headline']} {variation['body_text']} {variation['cta']}".lower()
            variation_score = 0
            
            for element_type, keywords in conversion_elements.items():
                if any(keyword in full_text for keyword in keywords):
                    variation_score += 1
            
            element_scores.append(variation_score)
        
        avg_elements = sum(element_scores) / len(element_scores)
        score += avg_elements * 8  # Up to 32 points for all elements
        
        return min(100, score)
    
    def _count_roi_elements(self, variations: List[Dict]) -> Dict[str, int]:
        """Count ROI elements used across variations"""
        elements = {
            'financial_calculations': 0,
            'roi_multipliers': 0,
            'investment_language': 0,
            'value_propositions': 0,
            'cost_comparisons': 0
        }
        
        for variation in variations:
            full_text = f"{variation['headline']} {variation['body_text']} {variation['cta']}".lower()
            analysis = variation.get('analysis', {})
            
            # Financial calculations (price mentions, multipliers)
            if any(char in full_text for char in ['$', 'x', '%']):
                elements['financial_calculations'] += 1
            
            # ROI multipliers
            if any(f"{i}x" in full_text for i in range(2, 21)):
                elements['roi_multipliers'] += 1
            
            # Investment language
            investment_words = ['investment', 'invest', 'return', 'roi', 'profit']
            if any(word in full_text for word in investment_words):
                elements['investment_language'] += 1
            
            # Value propositions
            if 'value' in analysis.get('roi_angle', '').lower():
                elements['value_propositions'] += 1
            
            # Cost comparisons
            comparison_words = ['compare', 'vs', 'versus', 'others charge', 'elsewhere']
            if any(word in full_text for word in comparison_words):
                elements['cost_comparisons'] += 1
        
        return elements
    
    def _generate_recommendations(self, variations: List[Dict], analysis: Dict, 
                                 pricing: Dict) -> List[str]:
        """Generate recommendations for ROI copy optimization"""
        recommendations = []
        
        # Pricing recommendations
        if not pricing.get('has_pricing', False):
            recommendations.append("Add specific pricing to enable stronger ROI calculations")
        
        # Strategy recommendations
        roi_strength = analysis.get('roi_messaging_strength', {})
        if not roi_strength or max(roi_strength.values()) < 2:
            recommendations.append("Strengthen ROI messaging with specific financial benefits")
        
        # Premium positioning
        if analysis.get('premium_positioning_count', 0) == 0:
            recommendations.append("Add premium positioning language to justify higher prices")
        
        # Psychological triggers
        triggers = analysis.get('psychological_trigger_usage', {})
        if not triggers or len(triggers) < 3:
            recommendations.append("Incorporate more psychological triggers for higher conversion")
        
        # Variation quality
        if len(variations) < 5:
            recommendations.append("Generate additional variations to test different ROI angles")
        
        # Financial emphasis
        financial_terms_used = sum(1 for v in variations if any(
            term in f"{v['headline']} {v['body_text']}".lower() 
            for term in ['roi', 'investment', 'return', 'profit']
        ))
        
        if financial_terms_used < len(variations) * 0.6:
            recommendations.append("Increase financial language usage across all variations")
        
        # Strategy diversity
        strategy_count = len(analysis.get('strategy_distribution', {}))
        if strategy_count < 4:
            recommendations.append("Test additional ROI strategies for better optimization")
        
        return recommendations[:6]  # Limit to top 6 recommendations
    
    def _calculate_confidence(self, variations: List[Dict], insights: Dict) -> float:
        """Calculate confidence score for ROI copy generation"""
        confidence_factors = []
        
        # Variation quality factor
        if len(variations) >= 5:
            confidence_factors.append(95)
        elif len(variations) >= 3:
            confidence_factors.append(85)
        else:
            confidence_factors.append(70)
        
        # ROI optimization factor
        roi_score = insights.get('roi_elements_used', {})
        if sum(roi_score.values()) >= 8:  # Strong ROI elements
            confidence_factors.append(90)
        elif sum(roi_score.values()) >= 5:
            confidence_factors.append(80)
        else:
            confidence_factors.append(70)
        
        # Strategy diversity factor
        strategy_count = len(set(v['strategy'] for v in variations))
        if strategy_count >= 4:
            confidence_factors.append(90)
        elif strategy_count >= 3:
            confidence_factors.append(80)
        else:
            confidence_factors.append(70)
        
        # Content quality factor
        avg_content_length = sum(
            len(v['headline']) + len(v['body_text']) + len(v['cta']) 
            for v in variations
        ) / len(variations)
        
        if avg_content_length >= 200:
            confidence_factors.append(85)
        elif avg_content_length >= 150:
            confidence_factors.append(80)
        else:
            confidence_factors.append(70)
        
        return sum(confidence_factors) / len(confidence_factors)
    
    def validate_input(self, input_data: ToolInput) -> bool:
        """Validate input data for ROI copy generation"""
        missing_fields = []
        
        if not input_data.headline.strip():
            missing_fields.append('headline')
        if not input_data.body_text.strip():
            missing_fields.append('body_text')
        if not input_data.cta.strip():
            missing_fields.append('cta')
        
        if missing_fields:
            raise ToolValidationError(
                self.name,
                f"Missing required fields for ROI copy generation: {missing_fields}",
                missing_fields
            )
        
        return True
    
    def get_output_scores(self) -> List[str]:
        """Get list of scores this tool outputs"""
        return [
            'roi_optimization_score', 'premium_positioning_score',
            'conversion_potential_score', 'overall_generator_score'
        ]
    
    @classmethod
    def default_config(cls) -> ToolConfig:
        """Get default configuration for this tool"""
        return ToolConfig(
            name="roi_copy_generator",
            tool_type=ToolType.GENERATOR,
            timeout=35.0,
            parameters={
                'variation_count': 5,
                'include_pricing_analysis': True,
                'roi_multiplier_range': (3, 20),
                'premium_positioning': True
            }
        )