"""
Legal Risk Scanner Tool - Identifies potentially problematic legal claims and provides safer alternatives
Flags absolute claims, health/medical assertions, and financial promises while maintaining persuasive impact
"""

import time
import re
from typing import Dict, Any, List, Optional, Tuple
from ..core import ToolRunner, ToolInput, ToolOutput, ToolConfig, ToolType
from ..exceptions import ToolValidationError


class LegalRiskScannerToolRunner(ToolRunner):
    """
    Legal Risk Scanner Tool
    
    Identifies and mitigates legal risks in copy:
    - Flags absolute claims ("guaranteed," "best," "instant")
    - Identifies health/medical assertions requiring disclaimers
    - Scans for financial promise violations
    - Checks testimonial compliance requirements
    - Suggests legally safer language maintaining persuasive impact
    - Provides risk assessment with color-coded flags and alternative copy
    """
    
    def __init__(self, config: ToolConfig):
        super().__init__(config)
        
        # Legal risk patterns with severity levels
        self.legal_risk_patterns = {
            'absolute_claims': {
                'patterns': [
                    r'\b(guaranteed?|guarantee)\b',
                    r'\b(always|never)\b(?!\s+(?:has|have|had|was|were|been|forget|remember))',
                    r'\b(100%|completely|totally|absolutely)\b',
                    r'\b(zero risk|no risk|risk[- ]?free)\b',
                    r'\b(instant|immediate|overnight)\s+(success|results|cure|fix)',
                    r'\b(best|#1|number one|top)\b(?!\s+(?:seller|rated|choice))',
                    r'\b(proven to|scientifically proven|clinically proven)\b(?!\s+by)',
                    r'\b(all|every|everyone|nobody|no one)\s+(will|can|gets|achieve)'
                ],
                'severity': 'high',
                'legal_area': 'advertising_standards',
                'safer_alternatives': {
                    'guaranteed': ['may help', 'designed to', 'intended to'],
                    'always': ['often', 'typically', 'generally'],
                    'never': ['rarely', 'seldom', 'unlikely to'],
                    '100%': ['up to', 'may achieve', 'designed for'],
                    'best': ['leading', 'among the top', 'highly rated'],
                    'instant': ['quick', 'fast', 'rapid']
                }
            },
            'health_claims': {
                'patterns': [
                    r'\b(cure[sd]?|heal[sd]?|treat[sd]?|prevent[sd]?|diagnose[sd]?)\b',
                    r'\b(lose \d+ pounds?|weight loss guaranteed|fat burning miracle)\b',
                    r'\b(anti[- ]?aging|fountain of youth|miracle cure)\b',
                    r'\b(FDA approved|medical grade|doctor recommended)\b(?!\s+by)',
                    r'\b(reduces? cholesterol|lowers? blood pressure|improves? heart health)\b',
                    r'\b(boosts? immune system|detox|cleanse|purif\w+)\b'
                ],
                'severity': 'high',
                'legal_area': 'health_regulations',
                'required_disclaimers': [
                    'This product has not been evaluated by the FDA',
                    'Individual results may vary',
                    'Consult your healthcare provider'
                ]
            },
            'financial_promises': {
                'patterns': [
                    r'\$\d+(?:,\d{3})*(?:\.\d{2})?\s+(?:per day|per week|per month|guaranteed)',
                    r'\b(passive income|guaranteed returns?|risk[- ]?free investment)\b',
                    r'\b(get rich|make money fast|financial freedom)\b',
                    r'\b(\d+%\s+return|guaranteed profit|no risk investment)\b',
                    r'\b(double your money|triple your income|unlimited earnings)\b'
                ],
                'severity': 'high',
                'legal_area': 'securities_regulations',
                'required_disclaimers': [
                    'Past performance does not guarantee future results',
                    'All investments carry risk of loss',
                    'Individual results may vary'
                ]
            },
            'testimonial_issues': {
                'patterns': [
                    r'"[^"]*(?:earned|made|lost|saved)\s+\$\d+[^"]*"',
                    r'\b(typical results|average earnings|income claims)\b',
                    r'\b(results not typical|individual results may vary)\b',
                    r'"[^"]*(?:lost \d+ pounds|cured my|healed my)[^"]*"'
                ],
                'severity': 'medium',
                'legal_area': 'testimonial_compliance',
                'required_disclaimers': [
                    'Results not typical',
                    'Individual results may vary'
                ]
            },
            'competition_claims': {
                'patterns': [
                    r'\b(better than|superior to|beats?)\s+(?:all\s+)?(?:competitors?|competition)\b',
                    r'\b(only|unique|exclusive)\b(?!\s+(?:to\s+you|for\s+you|offer))',
                    r'\b(no other|nothing else|nobody else)\b',
                    r'\b(first|original|inventor)\b(?!\s+(?:time|step|choice))'
                ],
                'severity': 'medium',
                'legal_area': 'comparative_advertising',
                'safer_alternatives': {
                    'better than all': 'among the leading',
                    'only': 'distinctive',
                    'unique': 'distinctive',
                    'no other': 'few others'
                }
            },
            'regulatory_terms': {
                'patterns': [
                    r'\b(FDA|FTC|SEC|USDA)\s+(?:approved|certified|endorsed)\b',
                    r'\b(patent pending|patented)\b(?!\s+(?:technology|process|method))',
                    r'\b(trademark|trademarked|®|™)\b(?!\s+(?:of|by))',
                    r'\b(government\s+(?:approved|backed|endorsed))\b'
                ],
                'severity': 'high',
                'legal_area': 'regulatory_compliance'
            }
        }
        
        # Industry-specific risk factors
        self.industry_risk_factors = {
            'healthcare': {
                'high_risk_terms': ['cure', 'treat', 'diagnose', 'prevent', 'heal'],
                'required_disclaimers': [
                    'This product has not been evaluated by the FDA',
                    'Not intended to diagnose, treat, cure, or prevent any disease'
                ],
                'compliance_level': 'strict'
            },
            'finance': {
                'high_risk_terms': ['guaranteed returns', 'risk-free', 'passive income'],
                'required_disclaimers': [
                    'Past performance does not guarantee future results',
                    'All investments carry risk'
                ],
                'compliance_level': 'strict'
            },
            'supplements': {
                'high_risk_terms': ['cure', 'miracle', 'FDA approved'],
                'required_disclaimers': [
                    'These statements have not been evaluated by the FDA',
                    'Not intended to diagnose, treat, cure, or prevent any disease'
                ],
                'compliance_level': 'strict'
            },
            'weight_loss': {
                'high_risk_terms': ['guaranteed weight loss', 'lose X pounds', 'miracle'],
                'required_disclaimers': [
                    'Results not typical',
                    'Individual results may vary'
                ],
                'compliance_level': 'moderate'
            }
        }
        
        # Geographic compliance considerations
        self.geographic_regulations = {
            'US': {
                'agencies': ['FTC', 'FDA', 'SEC'],
                'strict_categories': ['health', 'finance', 'supplements'],
                'testimonial_requirements': True
            },
            'EU': {
                'agencies': ['GDPR', 'Consumer Protection'],
                'strict_categories': ['health', 'finance', 'data_privacy'],
                'testimonial_requirements': True
            },
            'CA': {
                'agencies': ['Health Canada', 'Competition Bureau'],
                'strict_categories': ['health', 'supplements'],
                'testimonial_requirements': True
            }
        }
    
    async def run(self, input_data: ToolInput) -> ToolOutput:
        """Scan copy for legal risks and provide safer alternatives"""
        start_time = time.time()
        
        try:
            # Combine all text for analysis
            full_text = f"{input_data.headline} {input_data.body_text} {input_data.cta}"
            
            # Extract campaign context
            industry = input_data.industry.lower() if input_data.industry else 'general'
            platform = input_data.platform.lower() if input_data.platform else 'general'
            target_market = self._extract_target_market(input_data)
            
            # Perform comprehensive legal risk scanning
            risk_assessment = self._scan_legal_risks(full_text, industry, platform, target_market)
            
            # Generate safer alternatives
            safer_alternatives = self._generate_safer_alternatives(risk_assessment, full_text)
            
            # Create risk-mitigated copy variations
            mitigated_variations = self._create_risk_mitigated_variations(
                input_data, risk_assessment, safer_alternatives
            )
            
            # Calculate legal compliance scores
            overall_risk = self._calculate_overall_risk_score(risk_assessment)
            compliance_score = max(0, 100 - overall_risk)
            risk_mitigation_score = self._calculate_risk_mitigation_score(safer_alternatives)
            alternative_quality_score = self._calculate_alternative_quality_score(safer_alternatives)
            
            # Prepare scores
            scores = {
                'legal_compliance_score': compliance_score,
                'risk_mitigation_score': risk_mitigation_score,
                'alternative_quality_score': alternative_quality_score,
                'overall_legal_safety_score': (compliance_score + risk_mitigation_score + alternative_quality_score) / 3
            }
            
            # Generate legal recommendations
            recommendations = self._generate_legal_recommendations(
                risk_assessment, safer_alternatives, industry, target_market
            )
            
            # Detailed insights
            insights = {
                'risk_assessment': risk_assessment,
                'compliance_analysis': {
                    'overall_risk_level': self._determine_risk_level(overall_risk),
                    'industry_specific_risks': self._analyze_industry_risks(risk_assessment, industry),
                    'platform_considerations': self._analyze_platform_risks(risk_assessment, platform),
                    'geographic_compliance': self._analyze_geographic_risks(risk_assessment, target_market)
                },
                'legal_recommendations': {
                    'immediate_actions': self._identify_immediate_actions(risk_assessment),
                    'disclaimer_requirements': self._identify_disclaimer_requirements(risk_assessment, industry),
                    'approval_recommendations': self._identify_approval_needs(risk_assessment),
                    'monitoring_suggestions': self._identify_monitoring_needs(risk_assessment)
                }
            }
            
            execution_time = time.time() - start_time
            
            # Add variations and alternatives to insights
            insights['variations'] = mitigated_variations
            insights['safer_alternatives'] = safer_alternatives
            
            return ToolOutput(
                tool_name=self.name,
                tool_type=self.tool_type,
                success=True,
                scores=scores,
                insights=insights,
                recommendations=recommendations,
                generated_content=mitigated_variations,
                execution_time=execution_time,
                request_id=input_data.request_id,
                confidence_score=self._calculate_confidence(insights, risk_assessment)
            )
            
        except Exception as e:
            execution_time = time.time() - start_time
            
            return ToolOutput(
                tool_name=self.name,
                tool_type=self.tool_type,
                success=False,
                execution_time=execution_time,
                request_id=input_data.request_id,
                error_message=f"Legal risk scanning failed: {str(e)}"
            )
    
    def _extract_target_market(self, input_data: ToolInput) -> str:
        """Extract target geographic market"""
        # In practice, would parse from input_data.additional_data
        return 'US'  # Default to US market
    
    def _scan_legal_risks(self, text: str, industry: str, platform: str, target_market: str) -> Dict[str, Any]:
        """Comprehensive legal risk scanning"""
        risk_results = {
            'high_risk_flags': [],
            'medium_risk_flags': [],
            'low_risk_flags': [],
            'total_risk_score': 0,
            'risk_categories': {},
            'industry_specific_risks': [],
            'required_disclaimers': set()
        }
        
        # Scan each risk category
        for category, config in self.legal_risk_patterns.items():
            category_risks = []
            
            for pattern in config['patterns']:
                matches = list(re.finditer(pattern, text, re.IGNORECASE))
                for match in matches:
                    risk_flag = {
                        'category': category,
                        'matched_text': match.group(),
                        'position': match.start(),
                        'severity': config['severity'],
                        'legal_area': config['legal_area'],
                        'message': f"Potential legal risk: {match.group()}"
                    }
                    
                    category_risks.append(risk_flag)
                    
                    # Add to appropriate risk level
                    if config['severity'] == 'high':
                        risk_results['high_risk_flags'].append(risk_flag)
                        risk_results['total_risk_score'] += 20
                    elif config['severity'] == 'medium':
                        risk_results['medium_risk_flags'].append(risk_flag)
                        risk_results['total_risk_score'] += 10
                    else:
                        risk_results['low_risk_flags'].append(risk_flag)
                        risk_results['total_risk_score'] += 5
                    
                    # Add required disclaimers if available
                    if 'required_disclaimers' in config:
                        risk_results['required_disclaimers'].update(config['required_disclaimers'])
            
            if category_risks:
                risk_results['risk_categories'][category] = category_risks
        
        # Industry-specific risk analysis
        if industry in self.industry_risk_factors:
            industry_config = self.industry_risk_factors[industry]
            for term in industry_config['high_risk_terms']:
                if term.lower() in text.lower():
                    risk_results['industry_specific_risks'].append({
                        'term': term,
                        'industry': industry,
                        'severity': 'high',
                        'message': f"Industry-specific risk: {term} in {industry}"
                    })
                    risk_results['total_risk_score'] += 15
            
            # Add industry disclaimers
            risk_results['required_disclaimers'].update(industry_config['required_disclaimers'])
        
        risk_results['required_disclaimers'] = list(risk_results['required_disclaimers'])
        return risk_results
    
    def _generate_safer_alternatives(self, risk_assessment: Dict, original_text: str) -> List[Dict[str, Any]]:
        """Generate safer alternatives for flagged content"""
        alternatives = []
        
        # Process high-risk flags first
        for risk_flag in risk_assessment['high_risk_flags']:
            category = risk_flag['category']
            matched_text = risk_flag['matched_text']
            
            if category in self.legal_risk_patterns:
                config = self.legal_risk_patterns[category]
                safer_alts = config.get('safer_alternatives', {})
                
                # Find appropriate alternative
                alternative_found = False
                for risky_term, safe_terms in safer_alts.items():
                    if risky_term.lower() in matched_text.lower():
                        alternatives.append({
                            'original': matched_text,
                            'alternatives': safe_terms,
                            'risk_category': category,
                            'severity': 'high',
                            'legal_reasoning': f"Avoid absolute claims in {config['legal_area']}",
                            'persuasion_preservation': 'maintains impact while reducing legal risk'
                        })
                        alternative_found = True
                        break
                
                # Generic alternative if specific not found
                if not alternative_found:
                    alternatives.append({
                        'original': matched_text,
                        'alternatives': self._generate_generic_alternatives(matched_text, category),
                        'risk_category': category,
                        'severity': 'high',
                        'legal_reasoning': f"High risk term in {config['legal_area']}",
                        'persuasion_preservation': 'softens claim while maintaining appeal'
                    })
        
        return alternatives[:10]  # Limit to top 10 alternatives
    
    def _generate_generic_alternatives(self, matched_text: str, category: str) -> List[str]:
        """Generate generic safer alternatives"""
        text_lower = matched_text.lower()
        
        if category == 'absolute_claims':
            if 'guarantee' in text_lower:
                return ['may help', 'designed to', 'intended to support']
            elif 'always' in text_lower:
                return ['often', 'typically', 'generally']
            elif 'best' in text_lower:
                return ['leading', 'top-rated', 'highly regarded']
        elif category == 'health_claims':
            if 'cure' in text_lower:
                return ['support', 'help with', 'designed for']
            elif 'prevent' in text_lower:
                return ['may help reduce risk', 'support against', 'designed to help']
        elif category == 'financial_promises':
            if 'guaranteed' in text_lower:
                return ['potential', 'designed for', 'aimed at']
            elif 'risk-free' in text_lower:
                return ['low-risk', 'conservative', 'carefully managed']
        
        # Default alternatives
        return ['may help', 'designed to', 'intended to']
    
    def _create_risk_mitigated_variations(self, input_data: ToolInput, risk_assessment: Dict,
                                         safer_alternatives: List[Dict]) -> List[Dict[str, Any]]:
        """Create risk-mitigated copy variations"""
        variations = []
        
        # Variation 1: Legal-safe version
        legal_safe = self._create_legal_safe_variation(input_data, safer_alternatives)
        variations.append({
            'id': 'legal_safe',
            'type': 'legal_risk_mitigation',
            'headline': legal_safe['headline'],
            'body_text': legal_safe['body_text'],
            'cta': legal_safe['cta'],
            'optimization_focus': 'Minimized legal risks while preserving persuasion',
            'risk_reduction_score': self._estimate_risk_reduction(legal_safe, risk_assessment)
        })
        
        # Variation 2: Disclaimer-enhanced version
        if risk_assessment.get('required_disclaimers'):
            disclaimer_enhanced = self._create_disclaimer_enhanced_variation(input_data, risk_assessment)
            variations.append({
                'id': 'disclaimer_enhanced',
                'type': 'disclaimer_compliance',
                'headline': disclaimer_enhanced['headline'],
                'body_text': disclaimer_enhanced['body_text'],
                'cta': disclaimer_enhanced['cta'],
                'disclaimers': disclaimer_enhanced['disclaimers'],
                'optimization_focus': 'Added required disclaimers for compliance'
            })
        
        return variations
    
    def _create_legal_safe_variation(self, input_data: ToolInput, safer_alternatives: List[Dict]) -> Dict[str, str]:
        """Create legally safer copy variation"""
        safe_copy = {
            'headline': input_data.headline,
            'body_text': input_data.body_text,
            'cta': input_data.cta
        }
        
        # Apply safer alternatives
        for alt in safer_alternatives:
            original = alt['original']
            replacement = alt['alternatives'][0] if alt['alternatives'] else 'may help'
            
            # Replace in all sections
            for section in safe_copy:
                if original in safe_copy[section]:
                    safe_copy[section] = safe_copy[section].replace(original, replacement)
        
        return safe_copy
    
    def _create_disclaimer_enhanced_variation(self, input_data: ToolInput, risk_assessment: Dict) -> Dict[str, Any]:
        """Create version with required disclaimers"""
        enhanced_copy = {
            'headline': input_data.headline,
            'body_text': input_data.body_text,
            'cta': input_data.cta,
            'disclaimers': risk_assessment.get('required_disclaimers', [])
        }
        
        # Add disclaimer reference to body text
        if enhanced_copy['disclaimers']:
            enhanced_copy['body_text'] += f" *{enhanced_copy['disclaimers'][0]}"
        
        return enhanced_copy
    
    def _calculate_overall_risk_score(self, risk_assessment: Dict) -> float:
        """Calculate overall legal risk score (0-100, higher = more risk)"""
        return min(100, risk_assessment.get('total_risk_score', 0))
    
    def _calculate_risk_mitigation_score(self, safer_alternatives: List[Dict]) -> float:
        """Calculate how well risks are mitigated"""
        if not safer_alternatives:
            return 50  # No alternatives means no mitigation
        
        base_score = 70
        high_risk_mitigated = len([alt for alt in safer_alternatives if alt.get('severity') == 'high'])
        score = base_score + (high_risk_mitigated * 10)
        
        return min(100, score)
    
    def _calculate_alternative_quality_score(self, safer_alternatives: List[Dict]) -> float:
        """Calculate quality of alternative suggestions"""
        if not safer_alternatives:
            return 0
        
        # Score based on alternative availability and quality
        quality_score = 0
        for alt in safer_alternatives:
            if alt.get('alternatives') and len(alt['alternatives']) >= 2:
                quality_score += 15  # Multiple alternatives available
            elif alt.get('alternatives'):
                quality_score += 10  # Single alternative available
            
            if alt.get('persuasion_preservation'):
                quality_score += 5  # Persuasion impact considered
        
        return min(100, quality_score)
    
    def _determine_risk_level(self, risk_score: float) -> str:
        """Determine overall risk level"""
        if risk_score >= 60:
            return 'high'
        elif risk_score >= 30:
            return 'medium'
        elif risk_score >= 10:
            return 'low'
        else:
            return 'minimal'
    
    def _analyze_industry_risks(self, risk_assessment: Dict, industry: str) -> Dict[str, Any]:
        """Analyze industry-specific risk factors"""
        industry_risks = risk_assessment.get('industry_specific_risks', [])
        
        return {
            'industry': industry,
            'risk_count': len(industry_risks),
            'compliance_level': self.industry_risk_factors.get(industry, {}).get('compliance_level', 'standard'),
            'specific_risks': industry_risks
        }
    
    def _analyze_platform_risks(self, risk_assessment: Dict, platform: str) -> Dict[str, Any]:
        """Analyze platform-specific risk considerations"""
        # Platform policies vary - this would include platform-specific analysis
        return {
            'platform': platform,
            'policy_considerations': f"{platform} advertising policies may restrict certain claims",
            'recommendation': 'Review platform-specific advertising guidelines'
        }
    
    def _analyze_geographic_risks(self, risk_assessment: Dict, target_market: str) -> Dict[str, Any]:
        """Analyze geographic compliance requirements"""
        geo_config = self.geographic_regulations.get(target_market, self.geographic_regulations['US'])
        
        return {
            'target_market': target_market,
            'regulatory_agencies': geo_config['agencies'],
            'strict_categories': geo_config['strict_categories'],
            'testimonial_requirements': geo_config['testimonial_requirements']
        }
    
    def _identify_immediate_actions(self, risk_assessment: Dict) -> List[str]:
        """Identify immediate actions needed"""
        actions = []
        
        high_risk_count = len(risk_assessment.get('high_risk_flags', []))
        if high_risk_count > 0:
            actions.append(f"Address {high_risk_count} high-risk legal claims immediately")
        
        if risk_assessment.get('required_disclaimers'):
            actions.append("Add required disclaimers to copy")
        
        return actions
    
    def _identify_disclaimer_requirements(self, risk_assessment: Dict, industry: str) -> List[str]:
        """Identify required disclaimers"""
        return risk_assessment.get('required_disclaimers', [])
    
    def _identify_approval_needs(self, risk_assessment: Dict) -> List[str]:
        """Identify if legal review is needed"""
        approvals = []
        
        if risk_assessment.get('total_risk_score', 0) > 50:
            approvals.append("Legal review recommended before publication")
        
        if any('FDA' in flag.get('matched_text', '') for flag in risk_assessment.get('high_risk_flags', [])):
            approvals.append("FDA compliance review required")
        
        return approvals
    
    def _identify_monitoring_needs(self, risk_assessment: Dict) -> List[str]:
        """Identify ongoing monitoring needs"""
        monitoring = []
        
        if risk_assessment.get('industry_specific_risks'):
            monitoring.append("Monitor industry regulation changes")
        
        monitoring.append("Regular compliance review recommended")
        
        return monitoring
    
    def _estimate_risk_reduction(self, safe_copy: Dict[str, str], original_risk: Dict) -> float:
        """Estimate risk reduction achieved"""
        # Simple estimation - would be more sophisticated in practice
        original_risk_score = original_risk.get('total_risk_score', 0)
        estimated_reduction = min(80, original_risk_score * 0.7)  # Assume 70% reduction
        
        return estimated_reduction
    
    def _generate_legal_recommendations(self, risk_assessment: Dict, safer_alternatives: List[Dict],
                                      industry: str, target_market: str) -> List[str]:
        """Generate legal compliance recommendations"""
        recommendations = []
        
        # High-priority recommendations
        high_risk_count = len(risk_assessment.get('high_risk_flags', []))
        if high_risk_count > 3:
            recommendations.append("URGENT: Multiple high-risk legal claims detected - immediate legal review required")
        elif high_risk_count > 0:
            recommendations.append(f"Address {high_risk_count} high-risk legal claims with suggested alternatives")
        
        # Disclaimer recommendations
        disclaimers = risk_assessment.get('required_disclaimers', [])
        if disclaimers:
            recommendations.append(f"Add required disclaimer: '{disclaimers[0]}'")
        
        # Industry-specific recommendations
        if industry in ['healthcare', 'finance', 'supplements']:
            recommendations.append(f"Consult {industry} compliance specialist for regulatory approval")
        
        # Alternative implementation
        if safer_alternatives:
            recommendations.append("Implement suggested safer alternatives to reduce legal risk")
        
        # General compliance
        recommendations.append("Regular legal compliance audits recommended for ongoing campaigns")
        
        return recommendations[:6]
    
    def _calculate_confidence(self, insights: Dict, risk_assessment: Dict) -> float:
        """Calculate confidence in legal risk analysis"""
        confidence_factors = []
        
        # Risk detection comprehensiveness
        total_flags = len(risk_assessment.get('high_risk_flags', [])) + len(risk_assessment.get('medium_risk_flags', []))
        if total_flags > 0:
            confidence_factors.append(95)  # High confidence when risks are detected
        else:
            confidence_factors.append(85)  # Good confidence for clean content
        
        # Analysis depth
        if insights.get('compliance_analysis') and insights.get('legal_recommendations'):
            confidence_factors.append(90)
        else:
            confidence_factors.append(75)
        
        # Industry-specific analysis
        industry_analysis = insights.get('compliance_analysis', {}).get('industry_specific_risks', {})
        if industry_analysis.get('compliance_level'):
            confidence_factors.append(85)
        else:
            confidence_factors.append(80)
        
        return sum(confidence_factors) / len(confidence_factors)
    
    def validate_input(self, input_data: ToolInput) -> bool:
        """Validate input data for legal risk scanning"""
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
                f"Missing required fields for legal risk scanning: {missing_fields}",
                missing_fields
            )
        
        return True
    
    def get_output_scores(self) -> List[str]:
        """Get list of scores this tool outputs"""
        return [
            'legal_compliance_score', 'risk_mitigation_score',
            'alternative_quality_score', 'overall_legal_safety_score'
        ]
    
    @classmethod
    def default_config(cls) -> ToolConfig:
        """Get default configuration for this tool"""
        return ToolConfig(
            name="legal_risk_scanner",
            tool_type=ToolType.VALIDATOR,
            timeout=30.0,
            parameters={
                'strict_mode': True,
                'include_disclaimers': True,
                'generate_alternatives': True,
                'industry_specific_analysis': True
            }
        )
