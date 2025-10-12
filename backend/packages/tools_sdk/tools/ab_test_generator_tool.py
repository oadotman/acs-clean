"""
A/B Test Generator Tool - Systematic variation testing with psychological frameworks
Creates 5-10 variations with single variable changes and testing hypotheses
"""

import time
import random
from typing import Dict, Any, List, Optional, Tuple
from ..core import ToolRunner, ToolInput, ToolOutput, ToolConfig, ToolType
from ..exceptions import ToolValidationError


class ABTestGeneratorToolRunner(ToolRunner):
    """
    A/B Test Generator Tool
    
    Creates systematic variations for testing:
    - Single variable changes for clean testing
    - Different psychological frameworks (fear, desire, logic)
    - Various headline approaches (question, statement, benefit)
    - Different CTA styles (urgent, soft, direct)
    - Provides testing hypothesis for each variation
    - Recommends traffic allocation strategies
    """
    
    def __init__(self, config: ToolConfig):
        super().__init__(config)
        
        # Psychological frameworks for testing
        self.psychological_frameworks = {
            'fear': {
                'triggers': ['avoid', 'prevent', 'protect', 'risk', 'danger', 'mistake', 'lose'],
                'headlines': [
                    "Don't Let {pain_point} Ruin Your {desired_outcome}",
                    "Avoid the #{number} {pain_point} That's Costing You {loss}",
                    "Stop {pain_point} Before It's Too Late",
                    "The Hidden {threat} Nobody Talks About"
                ],
                'cta_style': 'protective',
                'tone': 'urgent/warning'
            },
            'desire': {
                'triggers': ['achieve', 'get', 'unlock', 'discover', 'gain', 'transform', 'become'],
                'headlines': [
                    "Finally! Get {desired_outcome} in Just {timeframe}",
                    "Discover the {benefit} You've Been Missing",
                    "Transform Your {area} with {solution}",
                    "Unlock {benefit} Starting {timeframe}"
                ],
                'cta_style': 'aspirational',
                'tone': 'positive/inspiring'
            },
            'logic': {
                'triggers': ['proven', 'data', 'study', 'research', 'facts', 'evidence', 'results'],
                'headlines': [
                    "{percentage}% of {audience} Use This {solution}",
                    "Study Proves: {solution} Delivers {benefit}",
                    "Data Shows {solution} Outperforms {alternative} by {multiplier}x",
                    "Research-Backed {solution} for {outcome}"
                ],
                'cta_style': 'factual',
                'tone': 'authoritative/credible'
            },
            'social_proof': {
                'triggers': ['customers', 'users', 'clients', 'thousands', 'millions', 'trusted'],
                'headlines': [
                    "{number}+ {audience} Trust {solution}",
                    "Join Thousands Who've Achieved {outcome}",
                    "Why {audience} Choose {solution} Over {alternative}",
                    "Trusted by {number} {audience} Worldwide"
                ],
                'cta_style': 'community',
                'tone': 'inclusive/social'
            },
            'urgency': {
                'triggers': ['limited', 'deadline', 'expires', 'now', 'today', 'hurry', 'fast'],
                'headlines': [
                    "Last Chance: {offer} Expires {deadline}",
                    "Only {number} {offer} Left",
                    "{offer} Ends in {countdown}",
                    "Act Fast - {benefit} Won't Last"
                ],
                'cta_style': 'immediate',
                'tone': 'urgent/pressing'
            },
            'curiosity': {
                'triggers': ['secret', 'hidden', 'revealed', 'insider', 'unknown', 'surprising'],
                'headlines': [
                    "The Secret {audience} Use to {outcome}",
                    "Hidden {solution} {authority} Don't Want You to Know",
                    "Surprising {fact} About {topic}",
                    "What {audience} Know That You Don't"
                ],
                'cta_style': 'discovery',
                'tone': 'mysterious/intriguing'
            }
        }
        
        # Headline approach variations
        self.headline_approaches = {
            'question': {
                'patterns': [
                    "What if {outcome} was possible in {timeframe}?",
                    "Why do {audience} struggle with {pain_point}?",
                    "How would {benefit} change your {area}?",
                    "Are you ready to {action} like never before?"
                ],
                'psychology': 'engagement/curiosity'
            },
            'statement': {
                'patterns': [
                    "{solution} delivers {benefit} for {audience}",
                    "The {adjective} way to {outcome}",
                    "{audience} are achieving {outcome} with {solution}",
                    "Revolutionary {solution} changes {industry}"
                ],
                'psychology': 'authority/confidence'
            },
            'benefit': {
                'patterns': [
                    "Get {benefit} in just {timeframe}",
                    "Achieve {outcome} without {pain_point}",
                    "Double your {metric} with {solution}",
                    "Save {time/money} while getting {benefit}"
                ],
                'psychology': 'value/outcome'
            },
            'number': {
                'patterns': [
                    "{number} ways to {outcome}",
                    "The {number}-step system for {benefit}",
                    "{number} secrets {authority} use for {outcome}",
                    "In just {number} {timeframe}, you'll {outcome}"
                ],
                'psychology': 'specificity/structure'
            },
            'how_to': {
                'patterns': [
                    "How to {outcome} in {timeframe}",
                    "How {audience} {action} without {pain_point}",
                    "How to get {benefit} even if {objection}",
                    "The complete guide to {outcome}"
                ],
                'psychology': 'education/solution'
            }
        }
        
        # CTA style variations
        self.cta_styles = {
            'urgent': {
                'patterns': [
                    "Get {benefit} Now",
                    "Start {action} Today",
                    "Claim Your {offer} Now",
                    "Act Fast - Get {benefit}"
                ],
                'urgency_level': 'high',
                'tone': 'immediate'
            },
            'soft': {
                'patterns': [
                    "Learn More About {solution}",
                    "Discover {benefit}",
                    "See How {solution} Works",
                    "Explore {opportunity}"
                ],
                'urgency_level': 'low',
                'tone': 'educational'
            },
            'direct': {
                'patterns': [
                    "Get {solution}",
                    "Start {action}",
                    "Try {solution}",
                    "Buy {product} Now"
                ],
                'urgency_level': 'medium',
                'tone': 'straightforward'
            },
            'benefit_focused': {
                'patterns': [
                    "Get {benefit} Today",
                    "Unlock {outcome}",
                    "Achieve {goal}",
                    "Access {solution}"
                ],
                'urgency_level': 'medium',
                'tone': 'outcome_oriented'
            },
            'risk_free': {
                'patterns': [
                    "Try {solution} Risk-Free",
                    "Get {benefit} - Guaranteed",
                    "Test {solution} Today",
                    "Start Your Free {trial}"
                ],
                'urgency_level': 'low',
                'tone': 'reassuring'
            }
        }
        
        # Testing priorities and variables
        self.testing_variables = {
            'headline': ['approach', 'psychological_framework', 'length', 'specificity'],
            'body_text': ['pain_point_emphasis', 'benefit_order', 'social_proof_placement', 'detail_level'],
            'cta': ['style', 'urgency', 'wording', 'placement'],
            'psychological_angle': ['fear_vs_desire', 'logic_vs_emotion', 'individual_vs_social'],
            'format': ['long_vs_short', 'bullet_vs_paragraph', 'question_vs_statement']
        }
        
        # Traffic allocation strategies
        self.traffic_allocation = {
            'equal_split': 'Equal traffic to all variations',
            'winner_focus': 'More traffic to best performing variation',
            'champion_challenger': 'Control vs best challenger',
            'multi_armed_bandit': 'Dynamic allocation based on performance',
            'staged_testing': 'Sequential testing with early winners'
        }
    
    async def run(self, input_data: ToolInput) -> ToolOutput:
        """Generate A/B test variations with hypotheses"""
        start_time = time.time()
        
        try:
            # Extract testing parameters
            base_copy = {
                'headline': input_data.headline,
                'body_text': input_data.body_text,
                'cta': input_data.cta
            }
            
            # Parse campaign goals and priorities from additional data
            campaign_goals = self._extract_campaign_goals(input_data)
            testing_priorities = self._extract_testing_priorities(input_data)
            audience_insights = self._extract_audience_insights(input_data)
            
            # Generate control version (original copy)
            control_variation = self._create_control_variation(base_copy)
            
            # Generate test variations
            variations = [control_variation]
            
            # Create variations based on testing priorities
            if 'headline' in testing_priorities:
                variations.extend(self._generate_headline_variations(base_copy, campaign_goals, 3))
            
            if 'psychological_angle' in testing_priorities:
                variations.extend(self._generate_psychology_variations(base_copy, campaign_goals, 3))
            
            if 'cta' in testing_priorities:
                variations.extend(self._generate_cta_variations(base_copy, campaign_goals, 2))
            
            # Ensure we have 5-10 variations total
            while len(variations) < 5:
                variations.extend(self._generate_additional_variations(base_copy, campaign_goals, 1))
            
            variations = variations[:10]  # Cap at 10 variations
            
            # Generate testing hypotheses for each variation
            for i, variation in enumerate(variations):
                if i > 0:  # Skip control
                    variation['hypothesis'] = self._generate_hypothesis(variation, control_variation)
            
            # Create test strategy
            test_strategy = self._create_test_strategy(variations, campaign_goals, testing_priorities)
            
            # Calculate test design scores
            design_quality = self._calculate_design_quality(variations, testing_priorities)
            hypothesis_strength = self._calculate_hypothesis_strength(variations)
            statistical_power = self._estimate_statistical_power(variations, campaign_goals)
            
            # Prepare scores
            scores = {
                'test_design_quality': design_quality,
                'hypothesis_strength': hypothesis_strength,
                'statistical_power_estimate': statistical_power,
                'overall_ab_test_score': (design_quality + hypothesis_strength + statistical_power) / 3
            }
            
            # Generate recommendations
            recommendations = self._generate_test_recommendations(
                variations, test_strategy, campaign_goals
            )
            
            # Detailed insights
            insights = {
                'variation_count': len(variations),
                'testing_framework': self._analyze_testing_framework(variations),
                'psychological_coverage': self._analyze_psychological_coverage(variations),
                'variable_isolation': self._analyze_variable_isolation(variations),
                'test_strategy': test_strategy,
                'campaign_optimization': {
                    'primary_goal': campaign_goals.get('primary', 'conversion'),
                    'testing_priorities': testing_priorities,
                    'audience_considerations': audience_insights,
                    'recommended_duration': self._estimate_test_duration(campaign_goals),
                    'minimum_sample_size': self._calculate_sample_size(campaign_goals)
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
                error_message=f"A/B test generation failed: {str(e)}"
            )
    
    def _extract_campaign_goals(self, input_data: ToolInput) -> Dict[str, Any]:
        """Extract campaign goals from input data"""
        # In a real implementation, this would parse from input_data.additional_data
        return {
            'primary': 'conversion',
            'secondary': 'engagement',
            'kpi': 'click_through_rate',
            'target_improvement': 0.15,  # 15% improvement target
            'budget_constraints': 'medium',
            'timeline': 'standard'
        }
    
    def _extract_testing_priorities(self, input_data: ToolInput) -> List[str]:
        """Extract testing priorities from input"""
        # Default priorities if not specified
        return ['headline', 'psychological_angle', 'cta']
    
    def _extract_audience_insights(self, input_data: ToolInput) -> Dict[str, Any]:
        """Extract audience insights for test design"""
        return {
            'demographics': 'mixed',
            'psychographics': 'analytical',
            'behavior_pattern': 'research_heavy',
            'decision_style': 'cautious',
            'pain_points': ['time_constraints', 'budget_concerns', 'complexity_fear']
        }
    
    def _create_control_variation(self, base_copy: Dict[str, str]) -> Dict[str, Any]:
        """Create control variation from original copy"""
        return {
            'id': 'control',
            'type': 'control',
            'headline': base_copy['headline'],
            'body_text': base_copy['body_text'],
            'cta': base_copy['cta'],
            'changes_made': [],
            'variable_tested': 'none',
            'psychological_framework': 'original',
            'hypothesis': 'Baseline performance measurement',
            'traffic_allocation': 20,  # 20% to control
            'expected_outcome': 'baseline',
            'test_priority': 'high'
        }
    
    def _generate_headline_variations(self, base_copy: Dict, goals: Dict, count: int) -> List[Dict[str, Any]]:
        """Generate headline-focused variations"""
        variations = []
        approaches = list(self.headline_approaches.keys())
        
        for i in range(count):
            approach = approaches[i % len(approaches)]
            approach_config = self.headline_approaches[approach]
            
            # Extract key elements from original
            elements = self._extract_copy_elements(base_copy)
            
            # Generate new headline using approach pattern
            pattern = random.choice(approach_config['patterns'])
            new_headline = self._fill_pattern(pattern, elements)
            
            variation = {
                'id': f'headline_test_{i+1}',
                'type': 'headline_test',
                'headline': new_headline,
                'body_text': base_copy['body_text'],
                'cta': base_copy['cta'],
                'changes_made': [f'Changed headline approach to {approach}'],
                'variable_tested': 'headline_approach',
                'psychological_framework': approach_config['psychology'],
                'traffic_allocation': 15,  # 15% each
                'expected_outcome': f'Test if {approach} headlines improve {goals["primary"]}',
                'test_priority': 'high' if 'headline' in ['headline'] else 'medium',
                'approach_type': approach
            }
            
            variations.append(variation)
        
        return variations
    
    def _generate_psychology_variations(self, base_copy: Dict, goals: Dict, count: int) -> List[Dict[str, Any]]:
        """Generate psychological framework variations"""
        variations = []
        frameworks = list(self.psychological_frameworks.keys())
        
        for i in range(count):
            framework = frameworks[i % len(frameworks)]
            framework_config = self.psychological_frameworks[framework]
            
            # Extract key elements
            elements = self._extract_copy_elements(base_copy)
            
            # Generate headline using psychological framework
            pattern = random.choice(framework_config['headlines'])
            new_headline = self._fill_pattern(pattern, elements)
            
            # Adjust body text to match framework
            new_body = self._adjust_body_for_framework(base_copy['body_text'], framework, elements)
            
            # Generate CTA matching framework
            cta_pattern = random.choice(self.cta_styles[framework_config['cta_style']]['patterns'])
            new_cta = self._fill_pattern(cta_pattern, elements)
            
            variation = {
                'id': f'psychology_test_{i+1}',
                'type': 'psychology_test',
                'headline': new_headline,
                'body_text': new_body,
                'cta': new_cta,
                'changes_made': [f'Applied {framework} psychological framework'],
                'variable_tested': 'psychological_framework',
                'psychological_framework': framework,
                'traffic_allocation': 12,  # 12% each
                'expected_outcome': f'Test if {framework} psychology improves conversion',
                'test_priority': 'high',
                'framework_type': framework,
                'tone': framework_config['tone']
            }
            
            variations.append(variation)
        
        return variations
    
    def _generate_cta_variations(self, base_copy: Dict, goals: Dict, count: int) -> List[Dict[str, Any]]:
        """Generate CTA-focused variations"""
        variations = []
        styles = list(self.cta_styles.keys())
        
        for i in range(count):
            style = styles[i % len(styles)]
            style_config = self.cta_styles[style]
            
            # Extract elements
            elements = self._extract_copy_elements(base_copy)
            
            # Generate new CTA
            pattern = random.choice(style_config['patterns'])
            new_cta = self._fill_pattern(pattern, elements)
            
            variation = {
                'id': f'cta_test_{i+1}',
                'type': 'cta_test',
                'headline': base_copy['headline'],
                'body_text': base_copy['body_text'],
                'cta': new_cta,
                'changes_made': [f'Changed CTA style to {style}'],
                'variable_tested': 'cta_style',
                'psychological_framework': 'original',
                'traffic_allocation': 10,  # 10% each
                'expected_outcome': f'Test if {style} CTAs improve click-through',
                'test_priority': 'medium',
                'cta_style': style,
                'urgency_level': style_config['urgency_level']
            }
            
            variations.append(variation)
        
        return variations
    
    def _generate_additional_variations(self, base_copy: Dict, goals: Dict, count: int) -> List[Dict[str, Any]]:
        """Generate additional variations to reach minimum count"""
        variations = []
        
        # Format variations
        for i in range(count):
            # Create a format variation (e.g., bullet points vs paragraphs)
            elements = self._extract_copy_elements(base_copy)
            
            if 'benefits' in elements:
                # Convert to bullet format
                new_body = f"Here's what you get:\n• {elements['benefit']}\n• Proven results\n• Easy implementation\n• Money-back guarantee"
            else:
                new_body = base_copy['body_text']
            
            variation = {
                'id': f'format_test_{i+1}',
                'type': 'format_test',
                'headline': base_copy['headline'],
                'body_text': new_body,
                'cta': base_copy['cta'],
                'changes_made': ['Changed body format to bullet points'],
                'variable_tested': 'content_format',
                'psychological_framework': 'original',
                'traffic_allocation': 8,  # 8% each
                'expected_outcome': 'Test if bullet format improves readability',
                'test_priority': 'low',
                'format_type': 'bullet_points'
            }
            
            variations.append(variation)
        
        return variations
    
    def _extract_copy_elements(self, base_copy: Dict[str, str]) -> Dict[str, str]:
        """Extract key elements from copy for pattern filling"""
        # Simple extraction - in practice would use NLP
        elements = {
            'outcome': 'better results',
            'benefit': 'increased performance',
            'pain_point': 'wasted time',
            'solution': 'our system',
            'timeframe': '30 days',
            'audience': 'professionals',
            'number': str(random.randint(3, 10)),
            'percentage': str(random.randint(75, 95)),
            'multiplier': str(random.randint(2, 10)),
            'offer': 'special deal',
            'deadline': 'this week',
            'countdown': '48 hours',
            'authority': 'experts',
            'fact': 'proven method',
            'topic': 'productivity',
            'area': 'business',
            'action': 'improve',
            'goal': 'success',
            'trial': 'trial period',
            'product': 'solution'
        }
        
        return elements
    
    def _fill_pattern(self, pattern: str, elements: Dict[str, str]) -> str:
        """Fill pattern template with extracted elements"""
        result = pattern
        for key, value in elements.items():
            result = result.replace(f'{{{key}}}', value)
        
        # Clean up any remaining placeholders
        import re
        result = re.sub(r'\{[^}]+\}', 'solution', result)
        
        return result
    
    def _adjust_body_for_framework(self, original_body: str, framework: str, elements: Dict[str, str]) -> str:
        """Adjust body text to match psychological framework"""
        framework_adjustments = {
            'fear': f"Don't let {elements['pain_point']} hold you back. {original_body} Avoid the mistakes that cost others their {elements['outcome']}.",
            'desire': f"Imagine achieving {elements['outcome']} in just {elements['timeframe']}. {original_body} Join thousands who've already transformed their {elements['area']}.",
            'logic': f"Research shows that {elements['percentage']}% of {elements['audience']} who use {elements['solution']} achieve {elements['outcome']}. {original_body} The data speaks for itself.",
            'social_proof': f"Over {elements['number']}000 {elements['audience']} trust {elements['solution']} for {elements['outcome']}. {original_body} See why industry leaders choose us.",
            'urgency': f"Time is running out! {original_body} This {elements['offer']} expires {elements['deadline']} - don't miss your chance.",
            'curiosity': f"There's a secret {elements['authority']} use to {elements['action']} that most people don't know. {original_body} Discover what they're not telling you."
        }
        
        return framework_adjustments.get(framework, original_body)
    
    def _generate_hypothesis(self, variation: Dict[str, Any], control: Dict[str, Any]) -> str:
        """Generate testing hypothesis for variation"""
        variable = variation['variable_tested']
        change = variation['changes_made'][0] if variation['changes_made'] else 'Modified copy'
        
        hypothesis_templates = {
            'headline_approach': f"If we change the headline approach to {variation.get('approach_type', 'alternative')}, then {variation['expected_outcome']} because it appeals to different cognitive preferences.",
            'psychological_framework': f"If we apply {variation.get('framework_type', 'different')} psychological triggers, then conversion rate will improve because it addresses specific emotional motivations.",
            'cta_style': f"If we use a {variation.get('cta_style', 'different')} CTA style, then click-through rate will increase because it matches user intent better.",
            'content_format': f"If we change the content format to {variation.get('format_type', 'alternative')}, then engagement will improve because it's easier to scan and digest."
        }
        
        return hypothesis_templates.get(variable, f"If we implement {change.lower()}, then performance will improve due to better audience alignment.")
    
    def _create_test_strategy(self, variations: List[Dict], goals: Dict, priorities: List[str]) -> Dict[str, Any]:
        """Create comprehensive test strategy"""
        return {
            'test_type': 'multivariate' if len(priorities) > 1 else 'ab_test',
            'primary_metric': goals.get('kpi', 'conversion_rate'),
            'secondary_metrics': ['click_through_rate', 'engagement_rate', 'cost_per_conversion'],
            'traffic_split': self._calculate_traffic_split(variations),
            'statistical_significance': 95,
            'minimum_detectable_effect': 15,  # 15% improvement
            'recommended_allocation': 'equal_split',
            'testing_sequence': self._determine_testing_sequence(variations, priorities),
            'winner_criteria': {
                'significance_level': 0.05,
                'minimum_sample_size': 1000,
                'test_duration_days': 14
            }
        }
    
    def _calculate_traffic_split(self, variations: List[Dict]) -> Dict[str, float]:
        """Calculate recommended traffic split"""
        total_variations = len(variations)
        control_allocation = 20  # 20% to control
        remaining = 80
        
        split = {'control': control_allocation}
        per_variation = remaining / (total_variations - 1)
        
        for i, variation in enumerate(variations[1:], 1):
            split[variation['id']] = round(per_variation, 1)
        
        return split
    
    def _determine_testing_sequence(self, variations: List[Dict], priorities: List[str]) -> List[str]:
        """Determine optimal testing sequence"""
        high_priority = [v['id'] for v in variations if v.get('test_priority') == 'high']
        medium_priority = [v['id'] for v in variations if v.get('test_priority') == 'medium']
        low_priority = [v['id'] for v in variations if v.get('test_priority') == 'low']
        
        return high_priority + medium_priority + low_priority
    
    def _calculate_design_quality(self, variations: List[Dict], priorities: List[str]) -> float:
        """Calculate test design quality score"""
        score = 70  # Base score
        
        # Variable isolation bonus
        isolated_variables = set(v.get('variable_tested', 'none') for v in variations)
        if len(isolated_variables) >= 3:
            score += 15
        elif len(isolated_variables) >= 2:
            score += 10
        
        # Priority coverage
        covered_priorities = 0
        for priority in priorities:
            if any(priority in v.get('variable_tested', '') for v in variations):
                covered_priorities += 1
        
        score += (covered_priorities / len(priorities)) * 15
        
        return min(100, score)
    
    def _calculate_hypothesis_strength(self, variations: List[Dict]) -> float:
        """Calculate hypothesis strength score"""
        score = 60  # Base score
        
        # Check for clear hypotheses
        variations_with_hypotheses = [v for v in variations if v.get('hypothesis') and len(v['hypothesis']) > 50]
        if variations_with_hypotheses:
            score += (len(variations_with_hypotheses) / len(variations)) * 25
        
        # Check for expected outcomes
        variations_with_outcomes = [v for v in variations if v.get('expected_outcome')]
        if variations_with_outcomes:
            score += (len(variations_with_outcomes) / len(variations)) * 15
        
        return min(100, score)
    
    def _estimate_statistical_power(self, variations: List[Dict], goals: Dict) -> float:
        """Estimate statistical power of test design"""
        score = 75  # Base score
        
        variation_count = len(variations)
        
        # Optimal variation count (5-8 for good power)
        if 5 <= variation_count <= 8:
            score += 15
        elif variation_count < 5:
            score -= 10
        elif variation_count > 10:
            score -= 5
        
        # Traffic allocation efficiency
        control_variation = next((v for v in variations if v.get('type') == 'control'), None)
        if control_variation and control_variation.get('traffic_allocation', 0) >= 15:
            score += 10
        
        return min(100, score)
    
    def _analyze_testing_framework(self, variations: List[Dict]) -> Dict[str, Any]:
        """Analyze the testing framework structure"""
        return {
            'framework_types': list(set(v.get('psychological_framework', 'none') for v in variations)),
            'variable_types': list(set(v.get('variable_tested', 'none') for v in variations)),
            'test_types': list(set(v.get('type', 'unknown') for v in variations)),
            'priority_distribution': {
                'high': len([v for v in variations if v.get('test_priority') == 'high']),
                'medium': len([v for v in variations if v.get('test_priority') == 'medium']),
                'low': len([v for v in variations if v.get('test_priority') == 'low'])
            }
        }
    
    def _analyze_psychological_coverage(self, variations: List[Dict]) -> Dict[str, Any]:
        """Analyze psychological framework coverage"""
        frameworks = [v.get('psychological_framework') for v in variations if v.get('psychological_framework')]
        
        return {
            'frameworks_tested': list(set(frameworks)),
            'framework_count': len(set(frameworks)),
            'coverage_percentage': (len(set(frameworks)) / len(self.psychological_frameworks)) * 100,
            'missing_frameworks': list(set(self.psychological_frameworks.keys()) - set(frameworks))
        }
    
    def _analyze_variable_isolation(self, variations: List[Dict]) -> Dict[str, Any]:
        """Analyze how well variables are isolated"""
        variables = [v.get('variable_tested', 'none') for v in variations if v.get('variable_tested') != 'none']
        
        return {
            'isolated_variables': list(set(variables)),
            'variable_count': len(set(variables)),
            'clean_isolation': all(len(v.get('changes_made', [])) == 1 for v in variations[1:]),  # Skip control
            'multi_variable_tests': len([v for v in variations if len(v.get('changes_made', [])) > 1])
        }
    
    def _estimate_test_duration(self, goals: Dict) -> str:
        """Estimate recommended test duration"""
        if goals.get('budget_constraints') == 'low':
            return '7-10 days'
        elif goals.get('timeline') == 'urgent':
            return '5-7 days'
        else:
            return '14-21 days'
    
    def _calculate_sample_size(self, goals: Dict) -> int:
        """Calculate minimum sample size needed"""
        base_size = 1000
        target_improvement = goals.get('target_improvement', 0.15)
        
        # Smaller improvements need larger samples
        if target_improvement < 0.1:
            return base_size * 2
        elif target_improvement < 0.2:
            return base_size
        else:
            return int(base_size * 0.7)
    
    def _generate_test_recommendations(self, variations: List[Dict], strategy: Dict, goals: Dict) -> List[str]:
        """Generate testing recommendations"""
        recommendations = []
        
        # Duration recommendations
        recommendations.append(f"Run test for {strategy['winner_criteria']['test_duration_days']} days minimum for statistical significance")
        
        # Sample size recommendations
        min_sample = strategy['winner_criteria']['minimum_sample_size']
        recommendations.append(f"Ensure minimum {min_sample} conversions per variation for reliable results")
        
        # Traffic allocation
        if len(variations) > 8:
            recommendations.append("Consider reducing variation count to 5-8 for better statistical power")
        
        # Variable isolation
        multi_var_count = sum(1 for v in variations if len(v.get('changes_made', [])) > 1)
        if multi_var_count > 2:
            recommendations.append("Isolate variables better - test one element change per variation")
        
        # Framework coverage
        psychological_coverage = self._analyze_psychological_coverage(variations)
        if psychological_coverage['coverage_percentage'] < 50:
            recommendations.append("Consider testing more diverse psychological frameworks")
        
        # Priority focus
        high_priority_count = len([v for v in variations if v.get('test_priority') == 'high'])
        if high_priority_count < 3:
            recommendations.append("Focus more variations on high-priority elements (headlines, CTAs)")
        
        return recommendations[:6]
    
    def _calculate_confidence(self, variations: List[Dict], insights: Dict) -> float:
        """Calculate confidence score for A/B test design"""
        confidence_factors = []
        
        # Variation quality factor
        if len(variations) >= 5:
            confidence_factors.append(90)
        else:
            confidence_factors.append(75)
        
        # Variable isolation factor
        variable_isolation = insights.get('variable_isolation', {})
        if variable_isolation.get('clean_isolation', False):
            confidence_factors.append(95)
        else:
            confidence_factors.append(80)
        
        # Hypothesis strength factor
        variations_with_hypotheses = len([v for v in variations if v.get('hypothesis')])
        if variations_with_hypotheses >= len(variations) - 1:  # All except control
            confidence_factors.append(90)
        else:
            confidence_factors.append(75)
        
        # Test strategy completeness
        strategy = insights.get('test_strategy', {})
        if strategy.get('traffic_split') and strategy.get('winner_criteria'):
            confidence_factors.append(85)
        else:
            confidence_factors.append(70)
        
        return sum(confidence_factors) / len(confidence_factors)
    
    def validate_input(self, input_data: ToolInput) -> bool:
        """Validate input data for A/B test generation"""
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
                f"Missing required fields for A/B test generation: {missing_fields}",
                missing_fields
            )
        
        return True
    
    def get_output_scores(self) -> List[str]:
        """Get list of scores this tool outputs"""
        return [
            'test_design_quality', 'hypothesis_strength',
            'statistical_power_estimate', 'overall_ab_test_score'
        ]
    
    @classmethod
    def default_config(cls) -> ToolConfig:
        """Get default configuration for this tool"""
        return ToolConfig(
            name="ab_test_generator",
            tool_type=ToolType.GENERATOR,
            timeout=40.0,
            parameters={
                'variation_count_range': (5, 10),
                'include_control': True,
                'statistical_significance': 95,
                'minimum_effect_size': 0.15
            }
        )