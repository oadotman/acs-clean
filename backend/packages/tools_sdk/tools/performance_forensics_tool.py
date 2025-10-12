"""
Performance Forensics Tool - Reverse-engineers successful/failing ads to identify key performance factors
Analyzes campaign performance and recommends specific optimizations
"""

import time
from typing import Dict, Any, List, Optional, Tuple
from ..core import ToolRunner, ToolInput, ToolOutput, ToolConfig, ToolType
from ..exceptions import ToolValidationError


class PerformanceForensicsToolRunner(ToolRunner):
    """
    Performance Forensics Tool
    
    Reverse-engineers ad performance to identify success/failure factors:
    - Identifies high-performing elements vs industry benchmarks
    - Analyzes correlation between copy elements and metrics
    - Compares against similar successful campaigns
    - Pinpoints failure points in conversion funnel
    - Suggests specific optimizations based on performance gaps
    - Provides detailed performance diagnosis with prioritized recommendations
    """
    
    def __init__(self, config: ToolConfig):
        super().__init__(config)
        
        # Industry benchmark data
        self.industry_benchmarks = {
            'healthcare': {
                'ctr': 0.025,  # 2.5%
                'conversion_rate': 0.035,  # 3.5%
                'engagement_rate': 0.045,
                'cost_per_click': 3.50,
                'cost_per_conversion': 85.00,
                'quality_score': 7.2
            },
            'finance': {
                'ctr': 0.032,  # 3.2%
                'conversion_rate': 0.028,  # 2.8%
                'engagement_rate': 0.038,
                'cost_per_click': 4.25,
                'cost_per_conversion': 95.00,
                'quality_score': 6.8
            },
            'technology': {
                'ctr': 0.038,  # 3.8%
                'conversion_rate': 0.042,  # 4.2%
                'engagement_rate': 0.055,
                'cost_per_click': 2.85,
                'cost_per_conversion': 65.00,
                'quality_score': 7.8
            },
            'retail': {
                'ctr': 0.045,  # 4.5%
                'conversion_rate': 0.052,  # 5.2%
                'engagement_rate': 0.065,
                'cost_per_click': 1.95,
                'cost_per_conversion': 38.00,
                'quality_score': 8.1
            },
            'education': {
                'ctr': 0.028,  # 2.8%
                'conversion_rate': 0.035,  # 3.5%
                'engagement_rate': 0.048,
                'cost_per_click': 2.15,
                'cost_per_conversion': 42.00,
                'quality_score': 7.5
            }
        }
        
        # Performance correlation patterns
        self.performance_patterns = {
            'high_ctr_indicators': {
                'headline_patterns': ['question', 'number', 'urgency', 'benefit'],
                'emotional_triggers': ['curiosity', 'urgency', 'fear', 'desire'],
                'copy_elements': ['power_words', 'specific_numbers', 'time_constraints'],
                'format_elements': ['short_headlines', 'bullet_points', 'clear_value_prop']
            },
            'high_conversion_indicators': {
                'copy_elements': ['social_proof', 'risk_reversal', 'clear_benefits', 'urgency'],
                'cta_patterns': ['action_oriented', 'benefit_focused', 'urgency_driven'],
                'trust_signals': ['testimonials', 'guarantees', 'certifications', 'numbers'],
                'objection_handling': ['risk_reversal', 'faq_addressing', 'benefit_emphasis']
            },
            'engagement_drivers': {
                'content_types': ['storytelling', 'questions', 'controversial', 'educational'],
                'emotional_hooks': ['surprise', 'curiosity', 'inspiration', 'validation'],
                'interaction_prompts': ['questions', 'polls', 'comments', 'shares'],
                'visual_elements': ['infographics', 'videos', 'carousels', 'before_after']
            }
        }
        
        # Common failure patterns
        self.failure_patterns = {
            'low_ctr_causes': [
                'weak_headline', 'no_value_proposition', 'generic_copy', 'poor_targeting',
                'weak_emotional_hook', 'no_urgency', 'confusing_message', 'bland_visuals'
            ],
            'low_conversion_causes': [
                'weak_cta', 'no_social_proof', 'missing_benefits', 'high_friction',
                'trust_issues', 'price_objections', 'poor_landing_page', 'form_issues'
            ],
            'high_cost_causes': [
                'poor_targeting', 'low_quality_score', 'high_competition', 'broad_keywords',
                'irrelevant_copy', 'poor_audience_match', 'wrong_platform', 'timing_issues'
            ]
        }
        
        # Optimization frameworks
        self.optimization_frameworks = {
            'ctr_optimization': {
                'headline_fixes': ['add_numbers', 'create_curiosity', 'add_urgency', 'benefit_focus'],
                'copy_improvements': ['power_words', 'emotional_triggers', 'value_clarity', 'brevity'],
                'targeting_refinements': ['audience_narrowing', 'demographic_focus', 'interest_targeting']
            },
            'conversion_optimization': {
                'trust_building': ['testimonials', 'guarantees', 'certifications', 'social_proof'],
                'objection_handling': ['faq_integration', 'risk_reversal', 'benefit_emphasis'],
                'cta_improvements': ['clarity', 'urgency', 'benefit_focus', 'placement'],
                'funnel_optimization': ['landing_page_match', 'form_simplification', 'load_speed']
            },
            'cost_optimization': {
                'targeting_refinement': ['negative_keywords', 'audience_exclusions', 'geographic_focus'],
                'quality_improvements': ['relevance_boost', 'landing_page_optimization', 'copy_alignment'],
                'bid_strategy': ['automated_bidding', 'dayparting', 'device_optimization']
            }
        }
    
    async def run(self, input_data: ToolInput) -> ToolOutput:
        """Perform comprehensive performance forensics analysis"""
        start_time = time.time()
        
        try:
            # Extract copy and performance data
            copy_data = {
                'headline': input_data.headline,
                'body_text': input_data.body_text,
                'cta': input_data.cta
            }
            
            # Extract performance metrics from input
            performance_metrics = self._extract_performance_metrics(input_data)
            campaign_details = self._extract_campaign_details(input_data)
            industry = input_data.industry.lower() if input_data.industry else 'technology'
            
            # Get industry benchmarks
            benchmarks = self.industry_benchmarks.get(industry, self.industry_benchmarks['technology'])
            
            # Perform forensics analysis
            benchmark_analysis = self._analyze_against_benchmarks(performance_metrics, benchmarks)
            copy_element_analysis = self._analyze_copy_elements(copy_data, performance_metrics)
            funnel_analysis = self._analyze_conversion_funnel(performance_metrics, campaign_details)
            failure_point_analysis = self._identify_failure_points(performance_metrics, benchmarks, copy_data)
            
            # Generate optimization recommendations
            optimization_priorities = self._prioritize_optimizations(
                benchmark_analysis, copy_element_analysis, funnel_analysis, failure_point_analysis
            )
            
            specific_recommendations = self._generate_specific_recommendations(
                performance_metrics, benchmarks, copy_data, optimization_priorities
            )
            
            # Calculate forensics scores
            diagnostic_accuracy = self._calculate_diagnostic_accuracy(
                performance_metrics, benchmarks, copy_element_analysis
            )
            optimization_potential = self._calculate_optimization_potential(
                benchmark_analysis, failure_point_analysis
            )
            implementation_feasibility = self._calculate_implementation_feasibility(
                specific_recommendations, campaign_details
            )
            
            # Prepare scores
            scores = {
                'diagnostic_accuracy_score': diagnostic_accuracy,
                'optimization_potential_score': optimization_potential,
                'implementation_feasibility_score': implementation_feasibility,
                'overall_forensics_score': (diagnostic_accuracy + optimization_potential + implementation_feasibility) / 3
            }
            
            # Detailed insights
            insights = {
                'performance_analysis': {
                    'vs_industry_benchmarks': benchmark_analysis,
                    'copy_element_correlations': copy_element_analysis,
                    'funnel_performance': funnel_analysis,
                    'identified_failure_points': failure_point_analysis
                },
                'optimization_roadmap': {
                    'priority_levels': optimization_priorities,
                    'quick_wins': self._identify_quick_wins(specific_recommendations),
                    'long_term_improvements': self._identify_long_term_improvements(specific_recommendations),
                    'estimated_impact': self._estimate_optimization_impact(performance_metrics, benchmarks)
                },
                'campaign_diagnosis': {
                    'overall_health': self._assess_campaign_health(performance_metrics, benchmarks),
                    'strongest_elements': self._identify_strong_elements(copy_element_analysis),
                    'weakest_elements': self._identify_weak_elements(copy_element_analysis),
                    'improvement_potential': optimization_potential
                }
            }
            
            execution_time = time.time() - start_time
            
            return ToolOutput(
                tool_name=self.name,
                tool_type=self.tool_type,
                success=True,
                scores=scores,
                insights=insights,
                recommendations=specific_recommendations,
                execution_time=execution_time,
                request_id=input_data.request_id,
                confidence_score=self._calculate_confidence(insights, performance_metrics)
            )
            
        except Exception as e:
            execution_time = time.time() - start_time
            
            return ToolOutput(
                tool_name=self.name,
                tool_type=self.tool_type,
                success=False,
                execution_time=execution_time,
                request_id=input_data.request_id,
                error_message=f"Performance forensics failed: {str(e)}"
            )
    
    def _extract_performance_metrics(self, input_data: ToolInput) -> Dict[str, float]:
        """Extract performance metrics from input data"""
        # In practice, this would parse from input_data.additional_data
        # For demo, using sample metrics
        return {
            'ctr': 0.025,  # 2.5%
            'conversion_rate': 0.018,  # 1.8% (below benchmark)
            'engagement_rate': 0.035,
            'cost_per_click': 3.85,
            'cost_per_conversion': 125.00,  # High cost
            'quality_score': 6.2,
            'impressions': 45000,
            'clicks': 1125,
            'conversions': 23,
            'spend': 4331.25
        }
    
    def _extract_campaign_details(self, input_data: ToolInput) -> Dict[str, Any]:
        """Extract campaign details for analysis"""
        return {
            'duration_days': 14,
            'platform': input_data.platform.lower() if input_data.platform else 'facebook',
            'audience_size': 250000,
            'targeting': 'interest_based',
            'bid_strategy': 'automatic',
            'budget_type': 'daily',
            'daily_budget': 300.00
        }
    
    def _analyze_against_benchmarks(self, metrics: Dict[str, float], 
                                   benchmarks: Dict[str, float]) -> Dict[str, Any]:
        """Analyze performance metrics against industry benchmarks"""
        analysis = {
            'performance_vs_benchmark': {},
            'underperforming_metrics': [],
            'overperforming_metrics': [],
            'overall_performance_score': 0
        }
        
        total_score = 0
        metric_count = 0
        
        for metric, benchmark in benchmarks.items():
            if metric in metrics:
                actual = metrics[metric]
                
                # Calculate performance ratio
                if metric in ['cost_per_click', 'cost_per_conversion']:
                    # Lower is better for cost metrics
                    ratio = benchmark / actual if actual > 0 else 0
                    performance = 'good' if ratio >= 1.0 else 'poor'
                else:
                    # Higher is better for rate metrics
                    ratio = actual / benchmark if benchmark > 0 else 0
                    performance = 'good' if ratio >= 1.0 else 'poor'
                
                analysis['performance_vs_benchmark'][metric] = {
                    'actual': actual,
                    'benchmark': benchmark,
                    'ratio': ratio,
                    'performance': performance,
                    'variance_percent': ((actual - benchmark) / benchmark) * 100 if benchmark > 0 else 0
                }
                
                # Track under/over performing metrics
                if performance == 'poor':
                    analysis['underperforming_metrics'].append(metric)
                else:
                    analysis['overperforming_metrics'].append(metric)
                
                # Add to overall score
                score = min(ratio * 100, 150) if ratio >= 1.0 else ratio * 100
                total_score += score
                metric_count += 1
        
        analysis['overall_performance_score'] = total_score / metric_count if metric_count > 0 else 0
        
        return analysis
    
    def _analyze_copy_elements(self, copy_data: Dict[str, str], 
                              metrics: Dict[str, float]) -> Dict[str, Any]:
        """Analyze correlation between copy elements and performance"""
        full_text = f"{copy_data['headline']} {copy_data['body_text']} {copy_data['cta']}".lower()
        
        element_analysis = {
            'ctr_correlations': {},
            'conversion_correlations': {},
            'engagement_correlations': {},
            'strong_elements': [],
            'weak_elements': []
        }
        
        # Analyze CTR correlations
        ctr_score = 0
        for pattern in self.performance_patterns['high_ctr_indicators']['headline_patterns']:
            if self._pattern_present(pattern, copy_data['headline']):
                ctr_score += 25
                element_analysis['strong_elements'].append(f'CTR: {pattern} pattern in headline')
        
        element_analysis['ctr_correlations'] = {
            'score': min(ctr_score, 100),
            'predicted_impact': 'positive' if ctr_score >= 50 else 'neutral' if ctr_score >= 25 else 'negative'
        }
        
        # Analyze conversion correlations
        conversion_score = 0
        for element in self.performance_patterns['high_conversion_indicators']['copy_elements']:
            if self._element_present(element, full_text):
                conversion_score += 25
                element_analysis['strong_elements'].append(f'Conversion: {element} present')
        
        element_analysis['conversion_correlations'] = {
            'score': min(conversion_score, 100),
            'predicted_impact': 'positive' if conversion_score >= 50 else 'neutral' if conversion_score >= 25 else 'negative'
        }
        
        # Analyze engagement correlations
        engagement_score = 0
        for content_type in self.performance_patterns['engagement_drivers']['content_types']:
            if self._content_type_present(content_type, full_text):
                engagement_score += 25
                element_analysis['strong_elements'].append(f'Engagement: {content_type} content')
        
        element_analysis['engagement_correlations'] = {
            'score': min(engagement_score, 100),
            'predicted_impact': 'positive' if engagement_score >= 50 else 'neutral' if engagement_score >= 25 else 'negative'
        }
        
        # Identify weak elements
        if ctr_score < 25:
            element_analysis['weak_elements'].append('Weak CTR indicators in copy')
        if conversion_score < 25:
            element_analysis['weak_elements'].append('Missing conversion elements')
        if engagement_score < 25:
            element_analysis['weak_elements'].append('Low engagement potential')
        
        return element_analysis
    
    def _analyze_conversion_funnel(self, metrics: Dict[str, float], 
                                  campaign_details: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze conversion funnel performance"""
        funnel_analysis = {
            'funnel_stages': {},
            'bottlenecks': [],
            'optimization_opportunities': []
        }
        
        # Calculate funnel metrics
        impressions = metrics.get('impressions', 0)
        clicks = metrics.get('clicks', 0)
        conversions = metrics.get('conversions', 0)
        
        if impressions > 0:
            ctr = clicks / impressions
            funnel_analysis['funnel_stages']['impression_to_click'] = {
                'rate': ctr,
                'volume': clicks,
                'performance': 'good' if ctr >= 0.02 else 'poor'
            }
            
            if ctr < 0.02:
                funnel_analysis['bottlenecks'].append('Low click-through rate')
                funnel_analysis['optimization_opportunities'].append('Improve headline and value proposition')
        
        if clicks > 0:
            conversion_rate = conversions / clicks
            funnel_analysis['funnel_stages']['click_to_conversion'] = {
                'rate': conversion_rate,
                'volume': conversions,
                'performance': 'good' if conversion_rate >= 0.03 else 'poor'
            }
            
            if conversion_rate < 0.03:
                funnel_analysis['bottlenecks'].append('Low conversion rate')
                funnel_analysis['optimization_opportunities'].append('Optimize landing page and CTA')
        
        return funnel_analysis
    
    def _identify_failure_points(self, metrics: Dict[str, float], benchmarks: Dict[str, float],
                               copy_data: Dict[str, str]) -> List[Dict[str, Any]]:
        """Identify specific failure points in campaign performance"""
        failure_points = []
        
        # Check for CTR issues
        if metrics.get('ctr', 0) < benchmarks.get('ctr', 0) * 0.8:  # 20% below benchmark
            failure_points.append({
                'type': 'ctr_failure',
                'severity': 'high',
                'description': 'Click-through rate significantly below industry benchmark',
                'likely_causes': self.failure_patterns['low_ctr_causes'][:3],
                'impact': 'Reduced traffic and higher acquisition costs'
            })
        
        # Check for conversion issues
        if metrics.get('conversion_rate', 0) < benchmarks.get('conversion_rate', 0) * 0.7:  # 30% below benchmark
            failure_points.append({
                'type': 'conversion_failure',
                'severity': 'high',
                'description': 'Conversion rate well below industry standard',
                'likely_causes': self.failure_patterns['low_conversion_causes'][:3],
                'impact': 'Poor ROI and inefficient spend'
            })
        
        # Check for cost efficiency issues
        if metrics.get('cost_per_conversion', 0) > benchmarks.get('cost_per_conversion', 0) * 1.5:  # 50% above benchmark
            failure_points.append({
                'type': 'cost_efficiency_failure',
                'severity': 'medium',
                'description': 'Cost per conversion significantly above benchmark',
                'likely_causes': self.failure_patterns['high_cost_causes'][:3],
                'impact': 'Reduced profitability and budget efficiency'
            })
        
        return failure_points
    
    def _prioritize_optimizations(self, benchmark_analysis: Dict, copy_analysis: Dict,
                                funnel_analysis: Dict, failure_points: List) -> Dict[str, List]:
        """Prioritize optimization opportunities"""
        priorities = {
            'critical': [],
            'high': [],
            'medium': [],
            'low': []
        }
        
        # Critical priorities (severe underperformance)
        for failure in failure_points:
            if failure['severity'] == 'high':
                priorities['critical'].append({
                    'issue': failure['type'],
                    'description': failure['description'],
                    'expected_impact': 'high'
                })
        
        # High priorities (significant improvement opportunities)
        underperforming = benchmark_analysis.get('underperforming_metrics', [])
        for metric in underperforming:
            if metric in ['ctr', 'conversion_rate']:
                priorities['high'].append({
                    'issue': f'{metric}_optimization',
                    'description': f'Improve {metric} to reach industry benchmark',
                    'expected_impact': 'medium_to_high'
                })
        
        # Medium priorities (copy optimizations)
        weak_elements = copy_analysis.get('weak_elements', [])
        for element in weak_elements:
            priorities['medium'].append({
                'issue': 'copy_optimization',
                'description': element,
                'expected_impact': 'medium'
            })
        
        return priorities
    
    def _generate_specific_recommendations(self, metrics: Dict[str, float], benchmarks: Dict[str, float],
                                         copy_data: Dict[str, str], priorities: Dict) -> List[str]:
        """Generate specific, actionable optimization recommendations"""
        recommendations = []
        
        # Critical recommendations
        for critical in priorities.get('critical', []):
            if 'ctr_failure' in critical['issue']:
                recommendations.append("CRITICAL: Rewrite headline with numbers, urgency, or curiosity gap to improve CTR")
            elif 'conversion_failure' in critical['issue']:
                recommendations.append("CRITICAL: Add social proof and risk reversal to landing page to boost conversions")
        
        # High priority recommendations
        ctr_actual = metrics.get('ctr', 0)
        ctr_benchmark = benchmarks.get('ctr', 0)
        if ctr_actual < ctr_benchmark:
            improvement_needed = ((ctr_benchmark - ctr_actual) / ctr_actual) * 100
            recommendations.append(f"Improve CTR by {improvement_needed:.1f}% through headline optimization and value clarity")
        
        conv_actual = metrics.get('conversion_rate', 0)
        conv_benchmark = benchmarks.get('conversion_rate', 0)
        if conv_actual < conv_benchmark:
            recommendations.append("Add testimonials and guarantee to increase trust and conversion rate")
        
        # Copy-specific recommendations
        full_text = f"{copy_data['headline']} {copy_data['body_text']} {copy_data['cta']}".lower()
        
        if 'guarantee' not in full_text and 'risk' not in full_text:
            recommendations.append("Add risk reversal (money-back guarantee) to reduce purchase anxiety")
        
        if not any(num in copy_data['headline'] for num in '0123456789'):
            recommendations.append("Include specific numbers in headline for increased credibility and CTR")
        
        if 'testimonial' not in full_text and 'customer' not in full_text:
            recommendations.append("Integrate customer testimonials or success stories for social proof")
        
        # Cost optimization recommendations
        cost_per_conv = metrics.get('cost_per_conversion', 0)
        cost_benchmark = benchmarks.get('cost_per_conversion', 0)
        if cost_per_conv > cost_benchmark * 1.2:
            recommendations.append("Optimize targeting and landing page relevance to reduce cost per conversion")
        
        return recommendations[:8]  # Limit to top 8 recommendations
    
    def _pattern_present(self, pattern: str, text: str) -> bool:
        """Check if specific pattern is present in text"""
        text_lower = text.lower()
        
        patterns = {
            'question': lambda t: '?' in t,
            'number': lambda t: any(char.isdigit() for char in t),
            'urgency': lambda t: any(word in t for word in ['now', 'today', 'urgent', 'limited']),
            'benefit': lambda t: any(word in t for word in ['get', 'save', 'improve', 'increase'])
        }
        
        return patterns.get(pattern, lambda t: False)(text_lower)
    
    def _element_present(self, element: str, text: str) -> bool:
        """Check if copy element is present"""
        element_indicators = {
            'social_proof': ['customers', 'testimonial', 'reviews', 'trusted', 'thousands'],
            'risk_reversal': ['guarantee', 'money back', 'risk free', 'no risk'],
            'clear_benefits': ['save', 'get', 'improve', 'increase', 'reduce'],
            'urgency': ['now', 'today', 'limited', 'expires', 'deadline']
        }
        
        indicators = element_indicators.get(element, [])
        return any(indicator in text for indicator in indicators)
    
    def _content_type_present(self, content_type: str, text: str) -> bool:
        """Check if content type is present"""
        content_indicators = {
            'storytelling': ['story', 'once', 'journey', 'experience'],
            'questions': ['?', 'what', 'how', 'why', 'when'],
            'controversial': ['shocking', 'surprising', 'truth', 'myth'],
            'educational': ['learn', 'discover', 'guide', 'tips']
        }
        
        indicators = content_indicators.get(content_type, [])
        return any(indicator in text for indicator in indicators)
    
    def _calculate_diagnostic_accuracy(self, metrics: Dict[str, float], benchmarks: Dict[str, float],
                                     copy_analysis: Dict) -> float:
        """Calculate accuracy of performance diagnosis"""
        score = 70  # Base score
        
        # Benchmark comparison accuracy
        underperforming = len([m for m, v in metrics.items() if m in benchmarks and v < benchmarks[m] * 0.9])
        if underperforming > 0:
            score += min(20, underperforming * 5)
        
        # Copy element correlation accuracy
        strong_elements = len(copy_analysis.get('strong_elements', []))
        score += min(10, strong_elements * 2)
        
        return min(100, score)
    
    def _calculate_optimization_potential(self, benchmark_analysis: Dict, 
                                        failure_points: List) -> float:
        """Calculate potential for optimization improvements"""
        score = 60  # Base score
        
        # Performance gaps indicate optimization potential
        overall_performance = benchmark_analysis.get('overall_performance_score', 100)
        if overall_performance < 100:
            gap = 100 - overall_performance
            score += min(30, gap * 0.5)
        
        # Failure points indicate specific optimization areas
        score += min(10, len(failure_points) * 3)
        
        return min(100, score)
    
    def _calculate_implementation_feasibility(self, recommendations: List[str], 
                                            campaign_details: Dict) -> float:
        """Calculate feasibility of implementing recommendations"""
        score = 80  # Base score (most recommendations are implementable)
        
        # More recommendations might indicate complexity
        if len(recommendations) > 6:
            score -= 5
        
        # Platform-specific factors
        platform = campaign_details.get('platform', 'facebook')
        if platform in ['facebook', 'google']:  # More flexible platforms
            score += 10
        
        return min(100, score)
    
    def _identify_quick_wins(self, recommendations: List[str]) -> List[str]:
        """Identify quick-win optimizations"""
        quick_win_keywords = ['headline', 'cta', 'add', 'include', 'number']
        return [rec for rec in recommendations if any(keyword in rec.lower() for keyword in quick_win_keywords)][:3]
    
    def _identify_long_term_improvements(self, recommendations: List[str]) -> List[str]:
        """Identify long-term improvement opportunities"""
        long_term_keywords = ['landing page', 'targeting', 'strategy', 'funnel']
        return [rec for rec in recommendations if any(keyword in rec.lower() for keyword in long_term_keywords)][:3]
    
    def _estimate_optimization_impact(self, metrics: Dict[str, float], 
                                    benchmarks: Dict[str, float]) -> Dict[str, str]:
        """Estimate impact of optimizations"""
        impact = {}
        
        for metric, benchmark in benchmarks.items():
            if metric in metrics:
                current = metrics[metric]
                if metric in ['cost_per_click', 'cost_per_conversion']:
                    # Lower is better
                    if current > benchmark:
                        potential_improvement = ((current - benchmark) / current) * 100
                        impact[metric] = f"{potential_improvement:.1f}% cost reduction possible"
                else:
                    # Higher is better
                    if current < benchmark:
                        potential_improvement = ((benchmark - current) / current) * 100
                        impact[metric] = f"{potential_improvement:.1f}% improvement possible"
        
        return impact
    
    def _assess_campaign_health(self, metrics: Dict[str, float], 
                               benchmarks: Dict[str, float]) -> str:
        """Assess overall campaign health"""
        performance_scores = []
        
        for metric, benchmark in benchmarks.items():
            if metric in metrics:
                actual = metrics[metric]
                if metric in ['cost_per_click', 'cost_per_conversion']:
                    score = benchmark / actual if actual > 0 else 0
                else:
                    score = actual / benchmark if benchmark > 0 else 0
                performance_scores.append(score)
        
        if not performance_scores:
            return 'insufficient_data'
        
        avg_performance = sum(performance_scores) / len(performance_scores)
        
        if avg_performance >= 1.2:
            return 'excellent'
        elif avg_performance >= 1.0:
            return 'good'
        elif avg_performance >= 0.8:
            return 'fair'
        else:
            return 'poor'
    
    def _identify_strong_elements(self, copy_analysis: Dict) -> List[str]:
        """Identify strongest performing copy elements"""
        return copy_analysis.get('strong_elements', [])[:3]
    
    def _identify_weak_elements(self, copy_analysis: Dict) -> List[str]:
        """Identify weakest performing copy elements"""
        return copy_analysis.get('weak_elements', [])[:3]
    
    def _calculate_confidence(self, insights: Dict, metrics: Dict[str, float]) -> float:
        """Calculate confidence in forensics analysis"""
        confidence_factors = []
        
        # Data completeness factor
        metrics_available = len([m for m in metrics.values() if m > 0])
        if metrics_available >= 8:
            confidence_factors.append(95)
        elif metrics_available >= 5:
            confidence_factors.append(85)
        else:
            confidence_factors.append(70)
        
        # Benchmark comparison factor
        performance_analysis = insights.get('performance_analysis', {})
        if performance_analysis.get('vs_industry_benchmarks'):
            confidence_factors.append(90)
        else:
            confidence_factors.append(75)
        
        # Failure point identification factor
        failure_points = performance_analysis.get('identified_failure_points', [])
        if len(failure_points) >= 2:
            confidence_factors.append(85)
        elif len(failure_points) >= 1:
            confidence_factors.append(80)
        else:
            confidence_factors.append(75)
        
        return sum(confidence_factors) / len(confidence_factors)
    
    def validate_input(self, input_data: ToolInput) -> bool:
        """Validate input data for performance forensics"""
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
                f"Missing required fields for performance forensics: {missing_fields}",
                missing_fields
            )
        
        return True
    
    def get_output_scores(self) -> List[str]:
        """Get list of scores this tool outputs"""
        return [
            'diagnostic_accuracy_score', 'optimization_potential_score',
            'implementation_feasibility_score', 'overall_forensics_score'
        ]
    
    @classmethod
    def default_config(cls) -> ToolConfig:
        """Get default configuration for this tool"""
        return ToolConfig(
            name="performance_forensics",
            tool_type=ToolType.ANALYZER,
            timeout=35.0,
            parameters={
                'include_benchmark_comparison': True,
                'analyze_funnel_performance': True,
                'prioritize_recommendations': True,
                'estimate_optimization_impact': True
            }
        )