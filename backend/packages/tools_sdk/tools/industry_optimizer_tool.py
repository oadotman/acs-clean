"""
Industry Optimizer Tool - Adapts generic copy using industry-specific language and pain points
Replaces generic terms with industry jargon and incorporates sector-specific frameworks
"""

import time
from typing import Dict, Any, List, Optional, Tuple
from ..core import ToolRunner, ToolInput, ToolOutput, ToolConfig, ToolType
from ..exceptions import ToolValidationError


class IndustryOptimizerToolRunner(ToolRunner):
    """
    Industry Optimizer Tool
    
    Adapts generic copy for specific industries:
    - Replaces generic terms with industry jargon
    - Incorporates sector-specific pain points
    - Uses proven frameworks for that industry
    - Adjusts tone for B2B vs B2C
    - References industry standards/certifications
    - Adapts messaging to audience role/seniority
    """
    
    def __init__(self, config: ToolConfig):
        super().__init__(config)
        
        # Industry-specific vocabularies and jargon
        self.industry_vocabularies = {
            'healthcare': {
                'generic_terms': {
                    'customers': 'patients',
                    'users': 'healthcare providers',
                    'solution': 'treatment solution',
                    'system': 'healthcare system',
                    'efficiency': 'patient outcomes',
                    'results': 'clinical results',
                    'improvement': 'patient care improvement',
                    'service': 'healthcare service',
                    'quality': 'clinical quality',
                    'cost': 'cost of care'
                },
                'industry_jargon': [
                    'EHR', 'EMR', 'HIPAA compliance', 'patient safety', 'clinical workflow',
                    'interoperability', 'population health', 'value-based care', 'care coordination',
                    'clinical decision support', 'patient engagement', 'care quality metrics'
                ],
                'pain_points': [
                    'clinician burnout', 'documentation burden', 'regulatory compliance',
                    'patient safety risks', 'workflow inefficiencies', 'data fragmentation',
                    'rising healthcare costs', 'staff shortages', 'technology adoption'
                ],
                'certifications': ['HIPAA', 'FDA', 'CCHIT', 'NCQA', 'Joint Commission'],
                'tone': 'professional/clinical'
            },
            'finance': {
                'generic_terms': {
                    'customers': 'investors',
                    'users': 'financial professionals',
                    'solution': 'financial solution',
                    'system': 'trading platform',
                    'efficiency': 'portfolio performance',
                    'results': 'returns',
                    'improvement': 'alpha generation',
                    'service': 'financial service',
                    'quality': 'investment grade',
                    'cost': 'expense ratio'
                },
                'industry_jargon': [
                    'ROI', 'alpha', 'beta', 'volatility', 'liquidity', 'compliance',
                    'risk management', 'portfolio optimization', 'asset allocation',
                    'derivatives', 'hedge', 'arbitrage', 'yield', 'duration'
                ],
                'pain_points': [
                    'market volatility', 'regulatory changes', 'compliance costs',
                    'risk exposure', 'performance pressure', 'technology disruption',
                    'margin compression', 'client acquisition', 'data quality'
                ],
                'certifications': ['CFA', 'FRM', 'CAIA', 'SEC', 'FINRA', 'SOX'],
                'tone': 'analytical/authoritative'
            },
            'technology': {
                'generic_terms': {
                    'customers': 'developers',
                    'users': 'end users',
                    'solution': 'software solution',
                    'system': 'platform',
                    'efficiency': 'performance optimization',
                    'results': 'outcomes',
                    'improvement': 'enhancement',
                    'service': 'SaaS',
                    'quality': 'reliability',
                    'cost': 'total cost of ownership'
                },
                'industry_jargon': [
                    'API', 'SDK', 'cloud-native', 'microservices', 'DevOps', 'CI/CD',
                    'scalability', 'latency', 'throughput', 'containerization',
                    'serverless', 'machine learning', 'blockchain', 'edge computing'
                ],
                'pain_points': [
                    'technical debt', 'scalability challenges', 'security vulnerabilities',
                    'integration complexity', 'legacy systems', 'talent shortage',
                    'rapid technology change', 'deployment issues', 'performance bottlenecks'
                ],
                'certifications': ['AWS', 'Azure', 'Google Cloud', 'CISSP', 'PMP', 'Agile'],
                'tone': 'technical/innovative'
            },
            'manufacturing': {
                'generic_terms': {
                    'customers': 'production teams',
                    'users': 'operators',
                    'solution': 'manufacturing solution',
                    'system': 'production system',
                    'efficiency': 'operational efficiency',
                    'results': 'production output',
                    'improvement': 'process improvement',
                    'service': 'manufacturing service',
                    'quality': 'production quality',
                    'cost': 'production cost'
                },
                'industry_jargon': [
                    'OEE', 'lean manufacturing', 'Six Sigma', 'just-in-time', 'kaizen',
                    'supply chain', 'predictive maintenance', 'quality control',
                    'automation', 'IoT sensors', 'digital twin', 'smart factory'
                ],
                'pain_points': [
                    'equipment downtime', 'quality defects', 'supply chain disruptions',
                    'safety incidents', 'regulatory compliance', 'skilled worker shortage',
                    'energy costs', 'waste reduction', 'production planning'
                ],
                'certifications': ['ISO 9001', 'ISO 14001', 'OSHA', 'AS9100', 'TS 16949'],
                'tone': 'practical/results-focused'
            },
            'education': {
                'generic_terms': {
                    'customers': 'educators',
                    'users': 'students',
                    'solution': 'educational solution',
                    'system': 'learning management system',
                    'efficiency': 'learning outcomes',
                    'results': 'student achievement',
                    'improvement': 'academic improvement',
                    'service': 'educational service',
                    'quality': 'educational quality',
                    'cost': 'cost per student'
                },
                'industry_jargon': [
                    'LMS', 'pedagogy', 'curriculum', 'assessment', 'differentiated instruction',
                    'student engagement', 'learning analytics', 'adaptive learning',
                    'competency-based', 'blended learning', 'personalized learning'
                ],
                'pain_points': [
                    'student engagement', 'achievement gaps', 'teacher workload',
                    'technology integration', 'budget constraints', 'assessment challenges',
                    'differentiated instruction', 'parent communication', 'compliance requirements'
                ],
                'certifications': ['FERPA', 'COPPA', 'Title IX', 'IEP', '504 Plan'],
                'tone': 'supportive/educational'
            },
            'retail': {
                'generic_terms': {
                    'customers': 'shoppers',
                    'users': 'consumers',
                    'solution': 'retail solution',
                    'system': 'point of sale system',
                    'efficiency': 'conversion rate',
                    'results': 'sales performance',
                    'improvement': 'sales improvement',
                    'service': 'customer service',
                    'quality': 'product quality',
                    'cost': 'cost of goods'
                },
                'industry_jargon': [
                    'SKU', 'inventory turnover', 'merchandising', 'omnichannel',
                    'customer lifetime value', 'basket size', 'foot traffic',
                    'conversion rate', 'same-store sales', 'loss prevention'
                ],
                'pain_points': [
                    'inventory management', 'customer acquisition', 'online competition',
                    'supply chain issues', 'seasonal fluctuations', 'staff turnover',
                    'customer retention', 'margin pressure', 'technology integration'
                ],
                'certifications': ['PCI DSS', 'SOX', 'GDPR', 'CCPA'],
                'tone': 'customer-focused/commercial'
            }
        }
        
        # Role-specific language adjustments
        self.role_adjustments = {
            'c_level': {
                'focus': ['strategic impact', 'ROI', 'competitive advantage', 'business transformation'],
                'language_style': 'executive/strategic',
                'decision_factors': ['bottom-line impact', 'market positioning', 'shareholder value'],
                'timeframe': 'quarterly/annual'
            },
            'vp_director': {
                'focus': ['operational efficiency', 'team productivity', 'process improvement', 'budget optimization'],
                'language_style': 'managerial/results-oriented',
                'decision_factors': ['department performance', 'resource allocation', 'team success'],
                'timeframe': 'monthly/quarterly'
            },
            'manager': {
                'focus': ['team performance', 'workflow optimization', 'day-to-day operations', 'problem-solving'],
                'language_style': 'practical/hands-on',
                'decision_factors': ['team efficiency', 'operational smooth running', 'immediate results'],
                'timeframe': 'weekly/monthly'
            },
            'individual_contributor': {
                'focus': ['personal productivity', 'skill development', 'task efficiency', 'career growth'],
                'language_style': 'personal/benefit-focused',
                'decision_factors': ['ease of use', 'personal benefit', 'skill enhancement'],
                'timeframe': 'daily/weekly'
            }
        }
        
        # Industry-specific frameworks
        self.industry_frameworks = {
            'healthcare': {
                'value_proposition': 'Improve patient outcomes while reducing costs',
                'framework': 'Triple Aim (Cost, Quality, Experience)',
                'metrics': ['patient satisfaction', 'clinical outcomes', 'cost per episode'],
                'regulatory_focus': 'HIPAA compliance and patient safety'
            },
            'finance': {
                'value_proposition': 'Maximize returns while managing risk',
                'framework': 'Risk-Return Optimization',
                'metrics': ['Sharpe ratio', 'alpha generation', 'drawdown'],
                'regulatory_focus': 'SEC compliance and fiduciary responsibility'
            },
            'technology': {
                'value_proposition': 'Accelerate innovation while ensuring reliability',
                'framework': 'DevOps/Agile methodologies',
                'metrics': ['time to market', 'system uptime', 'developer productivity'],
                'regulatory_focus': 'Data privacy and security compliance'
            },
            'manufacturing': {
                'value_proposition': 'Optimize production efficiency and quality',
                'framework': 'Lean Six Sigma',
                'metrics': ['OEE', 'defect rate', 'cycle time'],
                'regulatory_focus': 'Safety and environmental compliance'
            }
        }
        
        # Market context (B2B vs B2C indicators)
        self.market_context = {
            'b2b_indicators': [
                'decision committee', 'procurement process', 'enterprise', 'organization',
                'stakeholders', 'implementation', 'integration', 'scalability',
                'compliance', 'vendor', 'partnership', 'contract'
            ],
            'b2c_indicators': [
                'personal', 'individual', 'family', 'lifestyle', 'convenience',
                'affordable', 'easy to use', 'instant', 'mobile', 'subscription'
            ]
        }
    
    async def run(self, input_data: ToolInput) -> ToolOutput:
        """Optimize copy for specific industry and role"""
        start_time = time.time()
        
        try:
            # Extract base copy and parameters
            base_copy = {
                'headline': input_data.headline,
                'body_text': input_data.body_text,
                'cta': input_data.cta
            }
            
            industry = input_data.industry.lower() if input_data.industry else 'technology'
            target_role = self._extract_target_role(input_data)
            market_type = self._determine_market_type(base_copy, industry)
            
            # Get industry-specific configuration
            industry_config = self.industry_vocabularies.get(industry, self.industry_vocabularies['technology'])
            role_config = self.role_adjustments.get(target_role, self.role_adjustments['manager'])
            framework_config = self.industry_frameworks.get(industry, self.industry_frameworks['technology'])
            
            # Perform industry optimization
            optimized_copy = self._optimize_for_industry(base_copy, industry_config, role_config, framework_config)
            
            # Generate variations with different industry approaches
            variations = self._generate_industry_variations(base_copy, industry_config, role_config, framework_config)
            
            # Calculate optimization scores
            industry_alignment = self._calculate_industry_alignment(optimized_copy, industry_config)
            role_targeting = self._calculate_role_targeting(optimized_copy, role_config)
            jargon_integration = self._calculate_jargon_integration(optimized_copy, industry_config)
            framework_utilization = self._calculate_framework_utilization(optimized_copy, framework_config)
            
            # Prepare scores
            scores = {
                'industry_alignment_score': industry_alignment,
                'role_targeting_score': role_targeting,
                'jargon_integration_score': jargon_integration,
                'framework_utilization_score': framework_utilization,
                'overall_optimization_score': (industry_alignment + role_targeting + jargon_integration + framework_utilization) / 4
            }
            
            # Generate recommendations
            recommendations = self._generate_optimization_recommendations(
                base_copy, optimized_copy, industry_config, role_config
            )
            
            # Detailed insights
            insights = {
                'industry_analysis': {
                    'target_industry': industry,
                    'market_type': market_type,
                    'industry_framework': framework_config['framework'],
                    'key_metrics': framework_config['metrics'],
                    'regulatory_focus': framework_config['regulatory_focus']
                },
                'role_analysis': {
                    'target_role': target_role,
                    'decision_factors': role_config['decision_factors'],
                    'language_style': role_config['language_style'],
                    'timeframe_focus': role_config['timeframe']
                },
                'optimization_summary': {
                    'generic_terms_replaced': len(industry_config['generic_terms']),
                    'jargon_terms_added': self._count_jargon_usage(optimized_copy, industry_config),
                    'pain_points_addressed': self._count_pain_points_addressed(optimized_copy, industry_config),
                    'certifications_mentioned': self._count_certifications_mentioned(optimized_copy, industry_config)
                },
                'changes_made': self._analyze_changes_made(base_copy, optimized_copy),
                'variation_count': len(variations)
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
                optimized_copy=optimized_copy,
                execution_time=execution_time,
                request_id=input_data.request_id,
                confidence_score=self._calculate_confidence(insights, scores)
            )
            
        except Exception as e:
            execution_time = time.time() - start_time
            
            return ToolOutput(
                tool_name=self.name,
                tool_type=self.tool_type,
                success=False,
                execution_time=execution_time,
                request_id=input_data.request_id,
                error_message=f"Industry optimization failed: {str(e)}"
            )
    
    def _extract_target_role(self, input_data: ToolInput) -> str:
        """Extract target role from input data or infer from content"""
        # In practice, this would parse from input_data.additional_data
        # For now, return default based on content analysis
        content = f"{input_data.headline} {input_data.body_text}".lower()
        
        if any(word in content for word in ['ceo', 'executive', 'leadership', 'strategic']):
            return 'c_level'
        elif any(word in content for word in ['director', 'vp', 'vice president', 'head of']):
            return 'vp_director'
        elif any(word in content for word in ['manager', 'supervisor', 'team lead']):
            return 'manager'
        else:
            return 'individual_contributor'
    
    def _determine_market_type(self, copy: Dict[str, str], industry: str) -> str:
        """Determine if B2B or B2C based on copy content and industry"""
        full_text = f"{copy['headline']} {copy['body_text']} {copy['cta']}".lower()
        
        b2b_score = sum(1 for indicator in self.market_context['b2b_indicators'] if indicator in full_text)
        b2c_score = sum(1 for indicator in self.market_context['b2c_indicators'] if indicator in full_text)
        
        # Industry bias
        b2b_industries = ['healthcare', 'finance', 'manufacturing', 'technology']
        if industry in b2b_industries:
            b2b_score += 2
        
        return 'b2b' if b2b_score > b2c_score else 'b2c'
    
    def _optimize_for_industry(self, base_copy: Dict[str, str], industry_config: Dict,
                              role_config: Dict, framework_config: Dict) -> Dict[str, str]:
        """Apply industry-specific optimizations to copy"""
        optimized = {}
        
        # Optimize headline
        optimized['headline'] = self._optimize_headline(
            base_copy['headline'], industry_config, role_config, framework_config
        )
        
        # Optimize body text
        optimized['body_text'] = self._optimize_body_text(
            base_copy['body_text'], industry_config, role_config, framework_config
        )
        
        # Optimize CTA
        optimized['cta'] = self._optimize_cta(
            base_copy['cta'], industry_config, role_config
        )
        
        return optimized
    
    def _optimize_headline(self, headline: str, industry_config: Dict,
                          role_config: Dict, framework_config: Dict) -> str:
        """Optimize headline for industry and role"""
        optimized = headline
        
        # Replace generic terms with industry-specific ones
        for generic, specific in industry_config['generic_terms'].items():
            optimized = optimized.replace(generic, specific)
        
        # Add industry framework reference if appropriate
        if len(optimized.split()) < 8:  # Only if headline is short enough
            framework_ref = framework_config['framework']
            if 'improve' in optimized.lower():
                optimized = f"{optimized} Using {framework_ref}"
        
        # Adjust for role level
        if role_config['language_style'] == 'executive/strategic':
            # Add strategic language
            if 'solution' in optimized.lower():
                optimized = optimized.replace('solution', 'strategic solution')
        
        return optimized
    
    def _optimize_body_text(self, body_text: str, industry_config: Dict,
                           role_config: Dict, framework_config: Dict) -> str:
        """Optimize body text for industry and role"""
        optimized = body_text
        
        # Replace generic terms
        for generic, specific in industry_config['generic_terms'].items():
            optimized = optimized.replace(generic, specific)
        
        # Add industry jargon naturally
        jargon_to_add = industry_config['industry_jargon'][:3]  # Add top 3 relevant terms
        
        # Add pain point reference
        relevant_pain_point = industry_config['pain_points'][0]  # Most relevant pain point
        if 'challenge' in optimized.lower() or 'problem' in optimized.lower():
            optimized = optimized.replace('challenge', f'{relevant_pain_point}')
            optimized = optimized.replace('problem', f'{relevant_pain_point}')
        else:
            # Add pain point context
            optimized = f"Address {relevant_pain_point} with {optimized}"
        
        # Add framework reference
        framework_value = framework_config['value_proposition']
        optimized = f"{optimized} {framework_value} through our proven approach."
        
        # Add certification/compliance reference
        if industry_config['certifications']:
            cert = industry_config['certifications'][0]
            optimized = f"{optimized} {cert} compliant and industry-tested."
        
        # Role-specific adjustments
        if role_config['focus']:
            focus_area = role_config['focus'][0]
            optimized = f"Drive {focus_area}: {optimized}"
        
        return optimized
    
    def _optimize_cta(self, cta: str, industry_config: Dict, role_config: Dict) -> str:
        """Optimize CTA for industry and role"""
        optimized = cta
        
        # Replace generic terms
        for generic, specific in industry_config['generic_terms'].items():
            optimized = optimized.replace(generic, specific)
        
        # Role-specific CTA adjustments
        if role_config['language_style'] == 'executive/strategic':
            if 'get' in optimized.lower():
                optimized = optimized.replace('get', 'secure')
        elif role_config['language_style'] == 'practical/hands-on':
            if 'learn' in optimized.lower():
                optimized = optimized.replace('learn', 'see in action')
        
        return optimized
    
    def _generate_industry_variations(self, base_copy: Dict[str, str], industry_config: Dict,
                                     role_config: Dict, framework_config: Dict) -> List[Dict[str, Any]]:
        """Generate multiple industry-optimized variations"""
        variations = []
        
        # Variation 1: Heavy jargon focus
        jargon_heavy = self._create_jargon_heavy_variation(base_copy, industry_config, role_config)
        variations.append({
            'id': 'jargon_heavy',
            'type': 'industry_jargon_focused',
            'headline': jargon_heavy['headline'],
            'body_text': jargon_heavy['body_text'],
            'cta': jargon_heavy['cta'],
            'optimization_focus': 'Maximum industry jargon integration',
            'target_expertise': 'industry_expert'
        })
        
        # Variation 2: Pain point emphasis
        pain_focused = self._create_pain_point_variation(base_copy, industry_config, role_config)
        variations.append({
            'id': 'pain_point_focused',
            'type': 'industry_pain_point_focused',
            'headline': pain_focused['headline'],
            'body_text': pain_focused['body_text'],
            'cta': pain_focused['cta'],
            'optimization_focus': 'Industry-specific pain point addressing',
            'target_expertise': 'problem_aware'
        })
        
        # Variation 3: Framework/methodology emphasis
        framework_focused = self._create_framework_variation(base_copy, industry_config, framework_config)
        variations.append({
            'id': 'framework_focused',
            'type': 'industry_framework_focused',
            'headline': framework_focused['headline'],
            'body_text': framework_focused['body_text'],
            'cta': framework_focused['cta'],
            'optimization_focus': 'Industry framework and methodology emphasis',
            'target_expertise': 'methodology_familiar'
        })
        
        return variations
    
    def _create_jargon_heavy_variation(self, base_copy: Dict[str, str], industry_config: Dict,
                                      role_config: Dict) -> Dict[str, str]:
        """Create variation with heavy industry jargon usage"""
        jargon_terms = industry_config['industry_jargon'][:5]  # Top 5 jargon terms
        
        # Jargon-heavy headline
        headline = base_copy['headline']
        for generic, specific in industry_config['generic_terms'].items():
            headline = headline.replace(generic, specific)
        
        # Add jargon to headline
        if len(jargon_terms) > 0:
            headline = f"{jargon_terms[0]} {headline}"
        
        # Jargon-heavy body text
        body_text = base_copy['body_text']
        for generic, specific in industry_config['generic_terms'].items():
            body_text = body_text.replace(generic, specific)
        
        # Integrate multiple jargon terms
        jargon_sentence = f"Leverage {jargon_terms[0]} and {jargon_terms[1]} for optimal {jargon_terms[2]}."
        body_text = f"{jargon_sentence} {body_text}"
        
        # Simple CTA optimization
        cta = base_copy['cta']
        for generic, specific in industry_config['generic_terms'].items():
            cta = cta.replace(generic, specific)
        
        return {
            'headline': headline,
            'body_text': body_text,
            'cta': cta
        }
    
    def _create_pain_point_variation(self, base_copy: Dict[str, str], industry_config: Dict,
                                    role_config: Dict) -> Dict[str, str]:
        """Create variation focused on industry pain points"""
        pain_points = industry_config['pain_points'][:3]  # Top 3 pain points
        
        # Pain-focused headline
        headline = f"Eliminate {pain_points[0]} - {base_copy['headline']}"
        
        # Pain-focused body text
        body_text = (
            f"Tired of {pain_points[0]} and {pain_points[1]}? "
            f"Our solution addresses the root causes of {pain_points[2]}. "
            f"{base_copy['body_text']} "
            f"Say goodbye to {pain_points[0]} forever."
        )
        
        # Pain-focused CTA
        cta = f"Stop {pain_points[0]} Now"
        
        return {
            'headline': headline,
            'body_text': body_text,
            'cta': cta
        }
    
    def _create_framework_variation(self, base_copy: Dict[str, str], industry_config: Dict,
                                   framework_config: Dict) -> Dict[str, str]:
        """Create variation emphasizing industry frameworks"""
        framework_name = framework_config['framework']
        value_prop = framework_config['value_proposition']
        metrics = framework_config['metrics']
        
        # Framework-focused headline
        headline = f"{framework_name}-Based {base_copy['headline']}"
        
        # Framework-focused body text
        body_text = (
            f"Built on proven {framework_name} methodology. "
            f"{value_prop} with measurable results in {metrics[0]} and {metrics[1]}. "
            f"{base_copy['body_text']} "
            f"Join organizations using {framework_name} principles for superior outcomes."
        )
        
        # Framework-focused CTA
        cta = f"Apply {framework_name} Now"
        
        return {
            'headline': headline,
            'body_text': body_text,
            'cta': cta
        }
    
    def _calculate_industry_alignment(self, copy: Dict[str, str], industry_config: Dict) -> float:
        """Calculate how well copy aligns with industry norms"""
        score = 60  # Base score
        
        full_text = f"{copy['headline']} {copy['body_text']} {copy['cta']}".lower()
        
        # Check for industry term replacements
        industry_terms_used = sum(1 for term in industry_config['generic_terms'].values() if term.lower() in full_text)
        score += min(20, industry_terms_used * 3)
        
        # Check for pain point mentions
        pain_points_mentioned = sum(1 for pain in industry_config['pain_points'] if pain.lower() in full_text)
        score += min(15, pain_points_mentioned * 5)
        
        # Check tone alignment
        expected_tone = industry_config['tone']
        if 'professional' in expected_tone and any(word in full_text for word in ['professional', 'enterprise', 'business']):
            score += 5
        
        return min(100, score)
    
    def _calculate_role_targeting(self, copy: Dict[str, str], role_config: Dict) -> float:
        """Calculate how well copy targets specific role"""
        score = 65  # Base score
        
        full_text = f"{copy['headline']} {copy['body_text']} {copy['cta']}".lower()
        
        # Check for role-specific focus areas
        focus_matches = sum(1 for focus in role_config['focus'] if focus.lower() in full_text)
        score += min(20, focus_matches * 5)
        
        # Check for decision factors
        decision_matches = sum(1 for factor in role_config['decision_factors'] if factor.lower() in full_text)
        score += min(15, decision_matches * 5)
        
        return min(100, score)
    
    def _calculate_jargon_integration(self, copy: Dict[str, str], industry_config: Dict) -> float:
        """Calculate quality of jargon integration"""
        score = 50  # Base score
        
        full_text = f"{copy['headline']} {copy['body_text']} {copy['cta']}".lower()
        
        # Count jargon terms used
        jargon_count = sum(1 for jargon in industry_config['industry_jargon'] if jargon.lower() in full_text)
        score += min(30, jargon_count * 5)
        
        # Bonus for natural integration (not just listing)
        if jargon_count > 0 and jargon_count <= 5:  # Sweet spot
            score += 10
        elif jargon_count > 5:  # Too much jargon penalty
            score -= 5
        
        # Check for certification mentions
        cert_mentions = sum(1 for cert in industry_config['certifications'] if cert.lower() in full_text)
        score += min(10, cert_mentions * 5)
        
        return min(100, score)
    
    def _calculate_framework_utilization(self, copy: Dict[str, str], framework_config: Dict) -> float:
        """Calculate how well industry frameworks are utilized"""
        score = 70  # Base score
        
        full_text = f"{copy['headline']} {copy['body_text']} {copy['cta']}".lower()
        
        # Check for framework mention
        framework_name = framework_config['framework'].lower()
        if framework_name in full_text:
            score += 15
        
        # Check for value proposition alignment
        value_prop_words = framework_config['value_proposition'].lower().split()
        value_matches = sum(1 for word in value_prop_words if word in full_text)
        score += min(15, value_matches * 2)
        
        return min(100, score)
    
    def _count_jargon_usage(self, copy: Dict[str, str], industry_config: Dict) -> int:
        """Count industry jargon terms used in copy"""
        full_text = f"{copy['headline']} {copy['body_text']} {copy['cta']}".lower()
        return sum(1 for jargon in industry_config['industry_jargon'] if jargon.lower() in full_text)
    
    def _count_pain_points_addressed(self, copy: Dict[str, str], industry_config: Dict) -> int:
        """Count pain points addressed in copy"""
        full_text = f"{copy['headline']} {copy['body_text']} {copy['cta']}".lower()
        return sum(1 for pain in industry_config['pain_points'] if pain.lower() in full_text)
    
    def _count_certifications_mentioned(self, copy: Dict[str, str], industry_config: Dict) -> int:
        """Count certifications mentioned in copy"""
        full_text = f"{copy['headline']} {copy['body_text']} {copy['cta']}".lower()
        return sum(1 for cert in industry_config['certifications'] if cert.lower() in full_text)
    
    def _analyze_changes_made(self, original: Dict[str, str], optimized: Dict[str, str]) -> List[str]:
        """Analyze what changes were made during optimization"""
        changes = []
        
        # Headline changes
        if original['headline'] != optimized['headline']:
            changes.append(f"Headline optimized: '{original['headline']}' → '{optimized['headline']}'")
        
        # Body text changes (summary)
        if original['body_text'] != optimized['body_text']:
            changes.append("Body text enhanced with industry-specific language and pain points")
        
        # CTA changes
        if original['cta'] != optimized['cta']:
            changes.append(f"CTA optimized: '{original['cta']}' → '{optimized['cta']}'")
        
        return changes
    
    def _generate_optimization_recommendations(self, base_copy: Dict[str, str], optimized_copy: Dict[str, str],
                                             industry_config: Dict, role_config: Dict) -> List[str]:
        """Generate industry optimization recommendations"""
        recommendations = []
        
        # Jargon integration recommendations
        jargon_count = self._count_jargon_usage(optimized_copy, industry_config)
        if jargon_count < 2:
            recommendations.append(f"Consider adding more industry jargon from: {', '.join(industry_config['industry_jargon'][:3])}")
        elif jargon_count > 5:
            recommendations.append("Reduce jargon density to avoid alienating broader audience")
        
        # Pain point recommendations
        pain_count = self._count_pain_points_addressed(optimized_copy, industry_config)
        if pain_count == 0:
            recommendations.append(f"Address key industry pain point: {industry_config['pain_points'][0]}")
        
        # Certification recommendations
        cert_count = self._count_certifications_mentioned(optimized_copy, industry_config)
        if cert_count == 0:
            recommendations.append(f"Consider mentioning relevant certification: {industry_config['certifications'][0]}")
        
        # Role targeting recommendations
        role_focus = role_config['focus'][0]
        full_text = f"{optimized_copy['headline']} {optimized_copy['body_text']}".lower()
        if role_focus.lower() not in full_text:
            recommendations.append(f"Emphasize {role_focus} for better role targeting")
        
        # Market type recommendations
        recommendations.append("Test variations with different industry framework emphasis")
        recommendations.append("A/B test jargon-heavy vs. simplified versions for audience preferences")
        
        return recommendations[:6]  # Limit to top 6
    
    def _calculate_confidence(self, insights: Dict[str, Any], scores: Dict[str, float]) -> float:
        """Calculate confidence in industry optimization"""
        confidence_factors = []
        
        # Industry coverage factor
        optimization_summary = insights.get('optimization_summary', {})
        if optimization_summary.get('generic_terms_replaced', 0) >= 3:
            confidence_factors.append(90)
        else:
            confidence_factors.append(75)
        
        # Jargon integration factor
        jargon_added = optimization_summary.get('jargon_terms_added', 0)
        if 2 <= jargon_added <= 5:  # Optimal range
            confidence_factors.append(95)
        elif jargon_added > 0:
            confidence_factors.append(80)
        else:
            confidence_factors.append(65)
        
        # Pain point addressing factor
        pain_points = optimization_summary.get('pain_points_addressed', 0)
        if pain_points > 0:
            confidence_factors.append(85)
        else:
            confidence_factors.append(70)
        
        # Overall score factor
        overall_score = scores.get('overall_optimization_score', 0)
        if overall_score >= 80:
            confidence_factors.append(90)
        elif overall_score >= 70:
            confidence_factors.append(85)
        else:
            confidence_factors.append(75)
        
        return sum(confidence_factors) / len(confidence_factors)
    
    def validate_input(self, input_data: ToolInput) -> bool:
        """Validate input data for industry optimization"""
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
                f"Missing required fields for industry optimization: {missing_fields}",
                missing_fields
            )
        
        return True
    
    def get_output_scores(self) -> List[str]:
        """Get list of scores this tool outputs"""
        return [
            'industry_alignment_score', 'role_targeting_score',
            'jargon_integration_score', 'framework_utilization_score',
            'overall_optimization_score'
        ]
    
    @classmethod
    def default_config(cls) -> ToolConfig:
        """Get default configuration for this tool"""
        return ToolConfig(
            name="industry_optimizer",
            tool_type=ToolType.OPTIMIZER,
            timeout=30.0,
            parameters={
                'max_jargon_terms': 5,
                'include_certifications': True,
                'generate_variations': True,
                'target_role_adaptation': True
            }
        )