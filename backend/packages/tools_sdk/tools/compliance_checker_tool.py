"""
Compliance Checker Tool - Platform policy and regulatory compliance scanner
Checks copy against platform policies, legal requirements, and industry regulations
"""

import time
import re
from typing import Dict, Any, List, Optional, Tuple, Set
from ..core import ToolRunner, ToolInput, ToolOutput, ToolConfig, ToolType
from ..exceptions import ToolValidationError


class ComplianceCheckerToolRunner(ToolRunner):
    """
    Compliance Checker Tool
    
    Analyzes copy for compliance with:
    - Platform advertising policies (Facebook, Google, LinkedIn, etc.)
    - Legal requirements and absolute claims
    - Health, finance, and regulated industry claims
    - Flagged words and prohibited content
    - Provides compliant alternatives and risk assessment
    """
    
    def __init__(self, config: ToolConfig):
        super().__init__(config)
        
        # Platform-specific policy rules
        self.platform_policies = {
            'facebook': {
                'prohibited_words': [
                    'guaranteed results', 'miracle', 'cure', 'guaranteed income',
                    'get rich quick', 'work from home guaranteed', 'lose weight fast',
                    'click here', 'you are a winner', 'congratulations'
                ],
                'restricted_claims': [
                    'before and after', 'personal attributes', 'financial state',
                    'health conditions', 'negative body image'
                ],
                'character_limits': {'headline': 40, 'primary_text': 125, 'description': 30},
                'image_text_limit': 0.2,  # 20% rule
                'prohibited_categories': ['adult', 'gambling', 'tobacco', 'weapons']
            },
            'google': {
                'prohibited_words': [
                    'click here', 'download here', 'miracle', 'guaranteed',
                    'free money', 'get rich', 'work from home', 'amazing',
                    'fantastic', 'incredible'
                ],
                'restricted_claims': [
                    'superlative without proof', 'health claims', 'financial promises',
                    'unrealistic expectations'
                ],
                'character_limits': {'headline1': 30, 'headline2': 30, 'description': 90},
                'prohibited_categories': ['adult', 'gambling', 'healthcare', 'financial']
            },
            'linkedin': {
                'prohibited_words': [
                    'get rich quick', 'guaranteed income', 'work from home',
                    'miracle solution', 'instant success'
                ],
                'restricted_claims': [
                    'employment promises', 'unrealistic career growth',
                    'financial guarantees'
                ],
                'character_limits': {'headline': 150, 'description': 300},
                'prohibited_categories': ['mlm', 'get_rich_quick', 'adult']
            },
            'tiktok': {
                'prohibited_words': [
                    'click link in bio', 'follow for follow', 'like for like',
                    'guaranteed viral', 'instant fame'
                ],
                'restricted_claims': [
                    'artificial engagement', 'spam techniques', 'misleading content'
                ],
                'character_limits': {'caption': 150},
                'prohibited_categories': ['adult', 'political', 'dangerous_acts']
            },
            'instagram': {
                'prohibited_words': [
                    'follow for follow', 'like for like', 'dm for info',
                    'link in bio now', 'guaranteed followers'
                ],
                'restricted_claims': [
                    'artificial engagement', 'spam content', 'misleading promises'
                ],
                'character_limits': {'caption': 125, 'bio': 150},
                'prohibited_categories': ['adult', 'spam', 'fake_engagement']
            }
        }
        
        # Legal compliance patterns
        self.legal_flags = {
            'absolute_claims': {
                'patterns': [
                    r'\b(guarantee[d]?|always|never|100%|zero risk|completely safe)\b',
                    r'\b(all|every|everyone|nobody|no one)\s+(will|can|gets)\b',
                    r'\b(instant|immediate|overnight)\s+(success|results|money|cure)\b',
                    r'\b(proven to|scientifically proven|clinically proven)\b'
                ],
                'severity': 'high',
                'message': 'Absolute claims may violate advertising standards'
            },
            'health_claims': {
                'patterns': [
                    r'\b(cure[s]?|heal[s]?|treat[s]?|prevent[s]?|diagnose[s]?)\b',
                    r'\b(lose \d+ pounds|weight loss guaranteed|fat burning)\b',
                    r'\b(anti-aging|fountain of youth|miracle cure)\b',
                    r'\b(fda approved|medical grade|doctor recommended)\b'
                ],
                'severity': 'high',
                'message': 'Health claims require substantiation and may need disclaimers'
            },
            'financial_promises': {
                'patterns': [
                    r'\$\d+\s+(per day|per week|per month|guaranteed)',
                    r'\b(passive income|guaranteed returns|risk-free investment)\b',
                    r'\b(get rich|make money fast|financial freedom)\b',
                    r'\b(\d+% return|guaranteed profit|no risk)\b'
                ],
                'severity': 'high',
                'message': 'Financial promises may violate securities regulations'
            },
            'testimonial_issues': {
                'patterns': [
                    r'\b(results not typical|individual results may vary)\b',
                    r'"[^"]*earned \$\d+[^"]*"',
                    r'\b(typical results|average earnings|income claims)\b'
                ],
                'severity': 'medium',
                'message': 'Testimonials may require disclaimers about typical results'
            }
        }
        
        # Industry-specific compliance
        self.industry_regulations = {
            'healthcare': {
                'required_disclaimers': [
                    'This product has not been evaluated by the FDA',
                    'Individual results may vary',
                    'Consult your doctor before use'
                ],
                'prohibited_claims': ['cure', 'treat', 'diagnose', 'prevent'],
                'risk_level': 'high'
            },
            'finance': {
                'required_disclaimers': [
                    'Past performance does not guarantee future results',
                    'Investments carry risk of loss',
                    'Consult a financial advisor'
                ],
                'prohibited_claims': ['guaranteed returns', 'risk-free', 'sure thing'],
                'risk_level': 'high'
            },
            'supplements': {
                'required_disclaimers': [
                    'These statements have not been evaluated by the FDA',
                    'Not intended to diagnose, treat, cure, or prevent any disease'
                ],
                'prohibited_claims': ['cure', 'miracle', 'guaranteed results'],
                'risk_level': 'high'
            },
            'weight_loss': {
                'required_disclaimers': [
                    'Results not typical',
                    'Individual results may vary',
                    'Combined with diet and exercise'
                ],
                'prohibited_claims': ['lose X pounds guaranteed', 'effortless weight loss'],
                'risk_level': 'medium'
            }
        }
        
        # Common flagged words across platforms
        self.flagged_words = {
            'spam_indicators': [
                'click here', 'click now', 'act now', 'limited time',
                'buy now', 'order now', 'call now', 'don\'t wait'
            ],
            'exaggerated_claims': [
                'amazing', 'incredible', 'unbelievable', 'revolutionary',
                'breakthrough', 'miracle', 'secret', 'hidden'
            ],
            'urgency_overuse': [
                'urgent', 'immediate', 'instant', 'now', 'today',
                'expires', 'deadline', 'last chance', 'final'
            ],
            'financial_red_flags': [
                'get rich', 'make money fast', 'passive income',
                'guaranteed income', 'financial freedom', 'easy money'
            ]
        }
        
        # Compliant alternatives database
        self.alternatives = {
            'guaranteed': ['may help', 'designed to', 'intended to'],
            'miracle': ['innovative', 'advanced', 'effective'],
            'cure': ['support', 'help with', 'designed for'],
            'always': ['often', 'typically', 'generally'],
            'never': ['rarely', 'seldom', 'unlikely to'],
            'instant': ['quick', 'fast', 'rapid'],
            'free money': ['potential earnings', 'income opportunity'],
            'get rich quick': ['financial opportunity', 'earning potential'],
            'click here': ['learn more', 'discover', 'explore'],
            'guaranteed results': ['potential results', 'designed to help']
        }
    
    async def run(self, input_data: ToolInput) -> ToolOutput:
        """Execute comprehensive compliance check"""
        start_time = time.time()
        
        try:
            # Combine all text for analysis
            full_text = f"{input_data.headline} {input_data.body_text} {input_data.cta}".strip()
            platform = input_data.platform.lower()
            industry = input_data.industry.lower() if input_data.industry else 'general'
            
            # Core compliance checks
            platform_violations = self._check_platform_compliance(full_text, platform)
            legal_issues = self._check_legal_compliance(full_text)
            industry_compliance = self._check_industry_compliance(full_text, industry)
            flagged_content = self._check_flagged_words(full_text)
            character_compliance = self._check_character_limits(input_data, platform)
            
            # Calculate risk scores
            overall_risk = self._calculate_overall_risk(
                platform_violations, legal_issues, industry_compliance, flagged_content
            )
            
            # Generate alternatives and recommendations
            alternatives = self._generate_alternatives(
                platform_violations, legal_issues, flagged_content
            )
            
            recommendations = self._generate_recommendations(
                platform_violations, legal_issues, industry_compliance, 
                flagged_content, character_compliance
            )
            
            # Prepare risk scores
            risk_scores = {
                'overall_risk_score': overall_risk,
                'platform_risk_score': platform_violations.get('risk_score', 0),
                'legal_risk_score': legal_issues.get('risk_score', 0),
                'industry_risk_score': industry_compliance.get('risk_score', 0),
                'content_risk_score': flagged_content.get('risk_score', 0)
            }
            
            # Convert risk scores to compliance scores (inverse)
            compliance_scores = {
                key.replace('_risk_', '_compliance_'): max(0, 100 - score)
                for key, score in risk_scores.items()
            }
            
            # Detailed insights
            insights = {
                'platform_analysis': platform_violations,
                'legal_analysis': legal_issues,
                'industry_analysis': industry_compliance,
                'content_flags': flagged_content,
                'character_analysis': character_compliance,
                'risk_assessment': {
                    'overall_risk_level': self._get_risk_level(overall_risk),
                    'primary_concerns': self._identify_primary_concerns(
                        platform_violations, legal_issues, industry_compliance
                    ),
                    'compliance_status': 'compliant' if overall_risk < 30 else 'needs_review'
                },
                'alternatives_provided': len(alternatives),
                'total_flags': sum([
                    len(platform_violations.get('violations', [])),
                    len(legal_issues.get('issues', [])),
                    len(flagged_content.get('flagged_phrases', []))
                ])
            }
            
            execution_time = time.time() - start_time
            
            return ToolOutput(
                tool_name=self.name,
                tool_type=self.tool_type,
                success=True,
                scores=compliance_scores,
                insights=insights,
                recommendations=recommendations,
                alternatives=alternatives,
                execution_time=execution_time,
                request_id=input_data.request_id,
                confidence_score=self._calculate_confidence(insights)
            )
            
        except Exception as e:
            execution_time = time.time() - start_time
            
            return ToolOutput(
                tool_name=self.name,
                tool_type=self.tool_type,
                success=False,
                execution_time=execution_time,
                request_id=input_data.request_id,
                error_message=f"Compliance check failed: {str(e)}"
            )
    
    def _check_platform_compliance(self, text: str, platform: str) -> Dict[str, Any]:
        """Check compliance with platform-specific policies"""
        policy = self.platform_policies.get(platform, self.platform_policies['facebook'])
        text_lower = text.lower()
        
        violations = []
        risk_score = 0
        
        # Check prohibited words
        for word in policy['prohibited_words']:
            if word in text_lower:
                violations.append({
                    'type': 'prohibited_word',
                    'content': word,
                    'severity': 'high',
                    'message': f'"{word}" is prohibited on {platform}',
                    'position': text_lower.find(word)
                })
                risk_score += 25
        
        # Check restricted claims
        for claim in policy['restricted_claims']:
            # Simple keyword matching for claims
            claim_keywords = claim.replace('_', ' ').split()
            if any(keyword in text_lower for keyword in claim_keywords):
                violations.append({
                    'type': 'restricted_claim',
                    'content': claim,
                    'severity': 'medium',
                    'message': f'{claim} may require special approval on {platform}',
                    'position': -1
                })
                risk_score += 15
        
        return {
            'platform': platform,
            'violations': violations,
            'risk_score': min(100, risk_score),
            'violation_count': len(violations),
            'policy_version': '2024'
        }
    
    def _check_legal_compliance(self, text: str) -> Dict[str, Any]:
        """Check for legal compliance issues"""
        text_lower = text.lower()
        issues = []
        risk_score = 0
        
        for category, config in self.legal_flags.items():
            for pattern in config['patterns']:
                matches = re.finditer(pattern, text_lower, re.IGNORECASE)
                for match in matches:
                    issues.append({
                        'type': 'legal_risk',
                        'category': category,
                        'content': match.group(),
                        'severity': config['severity'],
                        'message': config['message'],
                        'position': match.start(),
                        'suggestion': 'Consider adding disclaimers or modifying claim'
                    })
                    
                    # Add risk score based on severity
                    if config['severity'] == 'high':
                        risk_score += 30
                    elif config['severity'] == 'medium':
                        risk_score += 15
                    else:
                        risk_score += 5
        
        return {
            'issues': issues,
            'risk_score': min(100, risk_score),
            'categories_flagged': list(set(issue['category'] for issue in issues)),
            'high_risk_count': len([i for i in issues if i['severity'] == 'high']),
            'requires_disclaimers': risk_score > 50
        }
    
    def _check_industry_compliance(self, text: str, industry: str) -> Dict[str, Any]:
        """Check industry-specific compliance requirements"""
        if industry not in self.industry_regulations:
            return {
                'industry': industry,
                'applicable': False,
                'risk_score': 0,
                'requirements': [],
                'violations': []
            }
        
        regulation = self.industry_regulations[industry]
        text_lower = text.lower()
        violations = []
        risk_score = 0
        
        # Check for prohibited claims
        for claim in regulation['prohibited_claims']:
            if claim in text_lower:
                violations.append({
                    'type': 'prohibited_claim',
                    'content': claim,
                    'severity': 'high',
                    'message': f'"{claim}" is prohibited in {industry} industry',
                    'industry_requirement': True
                })
                risk_score += 35
        
        # Check for missing required disclaimers
        missing_disclaimers = []
        for disclaimer in regulation['required_disclaimers']:
            # Check if disclaimer or similar language exists
            disclaimer_keywords = disclaimer.lower().split()[:3]  # First 3 words
            if not any(keyword in text_lower for keyword in disclaimer_keywords):
                missing_disclaimers.append(disclaimer)
        
        if missing_disclaimers and risk_score > 0:  # Only flag if there are other violations
            risk_score += 20
        
        return {
            'industry': industry,
            'applicable': True,
            'risk_score': min(100, risk_score),
            'risk_level': regulation['risk_level'],
            'violations': violations,
            'missing_disclaimers': missing_disclaimers,
            'required_disclaimers': regulation['required_disclaimers'],
            'compliance_requirements': len(regulation['required_disclaimers'])
        }
    
    def _check_flagged_words(self, text: str) -> Dict[str, Any]:
        """Check for commonly flagged words and phrases"""
        text_lower = text.lower()
        flagged_phrases = []
        risk_score = 0
        
        for category, words in self.flagged_words.items():
            found_words = []
            for word in words:
                if word in text_lower:
                    found_words.append({
                        'word': word,
                        'category': category,
                        'position': text_lower.find(word),
                        'severity': self._get_flag_severity(category)
                    })
                    
                    # Add risk based on category
                    if category == 'financial_red_flags':
                        risk_score += 20
                    elif category in ['spam_indicators', 'exaggerated_claims']:
                        risk_score += 10
                    else:
                        risk_score += 5
            
            if found_words:
                flagged_phrases.extend(found_words)
        
        # Group by category for analysis
        category_breakdown = {}
        for phrase in flagged_phrases:
            category = phrase['category']
            if category not in category_breakdown:
                category_breakdown[category] = []
            category_breakdown[category].append(phrase['word'])
        
        return {
            'flagged_phrases': flagged_phrases,
            'risk_score': min(100, risk_score),
            'category_breakdown': category_breakdown,
            'total_flags': len(flagged_phrases),
            'high_risk_flags': len([f for f in flagged_phrases if f['severity'] == 'high'])
        }
    
    def _check_character_limits(self, input_data: ToolInput, platform: str) -> Dict[str, Any]:
        """Check character limits for platform compliance"""
        policy = self.platform_policies.get(platform, {})
        limits = policy.get('character_limits', {})
        
        compliance = {
            'platform': platform,
            'limits_defined': bool(limits),
            'violations': [],
            'compliance_status': 'compliant'
        }
        
        if not limits:
            return compliance
        
        # Check headline length
        headline_len = len(input_data.headline)
        if 'headline' in limits and headline_len > limits['headline']:
            compliance['violations'].append({
                'field': 'headline',
                'current_length': headline_len,
                'limit': limits['headline'],
                'excess': headline_len - limits['headline'],
                'message': f'Headline exceeds {platform} limit by {headline_len - limits["headline"]} characters'
            })
        
        # Check body text length
        body_len = len(input_data.body_text)
        body_limit_key = 'primary_text' if 'primary_text' in limits else 'description'
        if body_limit_key in limits and body_len > limits[body_limit_key]:
            compliance['violations'].append({
                'field': 'body_text',
                'current_length': body_len,
                'limit': limits[body_limit_key],
                'excess': body_len - limits[body_limit_key],
                'message': f'Body text exceeds {platform} limit by {body_len - limits[body_limit_key]} characters'
            })
        
        if compliance['violations']:
            compliance['compliance_status'] = 'non_compliant'
        
        return compliance
    
    def _calculate_overall_risk(self, platform: Dict, legal: Dict, 
                               industry: Dict, content: Dict) -> float:
        """Calculate overall risk score"""
        # Weight different risk factors
        weights = {
            'platform': 0.3,
            'legal': 0.35,      # Legal has highest weight
            'industry': 0.25,
            'content': 0.1
        }
        
        platform_risk = platform.get('risk_score', 0)
        legal_risk = legal.get('risk_score', 0)
        industry_risk = industry.get('risk_score', 0)
        content_risk = content.get('risk_score', 0)
        
        overall_risk = (
            platform_risk * weights['platform'] +
            legal_risk * weights['legal'] +
            industry_risk * weights['industry'] +
            content_risk * weights['content']
        )
        
        return round(overall_risk, 1)
    
    def _generate_alternatives(self, platform: Dict, legal: Dict, 
                              content: Dict) -> List[Dict[str, Any]]:
        """Generate compliant alternatives for flagged content"""
        alternatives = []
        
        # Platform violations alternatives
        for violation in platform.get('violations', []):
            if violation['type'] == 'prohibited_word':
                word = violation['content']
                if word in self.alternatives:
                    alternatives.append({
                        'original': word,
                        'alternatives': self.alternatives[word],
                        'type': 'platform_compliance',
                        'reason': f"Platform policy violation on {platform.get('platform', '')}"
                    })
        
        # Legal issues alternatives
        for issue in legal.get('issues', []):
            original_text = issue['content']
            category = issue['category']
            
            # Generate category-specific alternatives
            if category == 'absolute_claims':
                alternatives.append({
                    'original': original_text,
                    'alternatives': ['may help', 'designed to', 'intended to support'],
                    'type': 'legal_compliance',
                    'reason': 'Avoid absolute claims without substantiation'
                })
            elif category == 'financial_promises':
                alternatives.append({
                    'original': original_text,
                    'alternatives': ['potential earnings', 'income opportunity', 'financial potential'],
                    'type': 'legal_compliance',
                    'reason': 'Financial promises require disclaimers'
                })
        
        # Content flags alternatives
        for phrase in content.get('flagged_phrases', []):
            word = phrase['word']
            if word in self.alternatives:
                alternatives.append({
                    'original': word,
                    'alternatives': self.alternatives[word],
                    'type': 'content_improvement',
                    'reason': f"Flagged as {phrase['category']}"
                })
        
        return alternatives[:10]  # Limit to top 10 alternatives
    
    def _generate_recommendations(self, platform: Dict, legal: Dict, 
                                 industry: Dict, content: Dict, 
                                 character: Dict) -> List[str]:
        """Generate compliance recommendations"""
        recommendations = []
        
        # High priority recommendations
        if legal.get('risk_score', 0) > 50:
            recommendations.append("High legal risk detected - consult legal counsel before publishing")
        
        if platform.get('risk_score', 0) > 30:
            recommendations.append(f"Review {platform.get('platform', '')} advertising policies before submission")
        
        # Industry-specific recommendations
        if industry.get('applicable', False) and industry.get('risk_score', 0) > 20:
            missing_disclaimers = industry.get('missing_disclaimers', [])
            if missing_disclaimers:
                recommendations.append(f"Add required disclaimer: \"{missing_disclaimers[0]}\"")
        
        # Character limit recommendations
        if character.get('violations', []):
            for violation in character['violations']:
                recommendations.append(
                    f"Reduce {violation['field']} by {violation['excess']} characters for platform compliance"
                )
        
        # Content improvement recommendations
        high_risk_flags = content.get('high_risk_flags', 0)
        if high_risk_flags > 0:
            recommendations.append("Replace flagged high-risk terms with compliant alternatives")
        
        # Specific violation recommendations
        for violation in platform.get('violations', []):
            if violation['severity'] == 'high':
                recommendations.append(f"Remove prohibited term: \"{violation['content']}\"")
        
        for issue in legal.get('issues', []):
            if issue['severity'] == 'high':
                recommendations.append(f"Address legal risk: {issue['message']}")
        
        return recommendations[:8]  # Limit to top 8 recommendations
    
    def _get_risk_level(self, risk_score: float) -> str:
        """Convert risk score to risk level"""
        if risk_score >= 70:
            return 'high'
        elif risk_score >= 40:
            return 'medium'
        elif risk_score >= 15:
            return 'low'
        else:
            return 'minimal'
    
    def _get_flag_severity(self, category: str) -> str:
        """Get severity level for flagged content category"""
        high_severity = ['financial_red_flags']
        medium_severity = ['spam_indicators', 'exaggerated_claims']
        
        if category in high_severity:
            return 'high'
        elif category in medium_severity:
            return 'medium'
        else:
            return 'low'
    
    def _identify_primary_concerns(self, platform: Dict, legal: Dict, 
                                  industry: Dict) -> List[str]:
        """Identify the primary compliance concerns"""
        concerns = []
        
        if legal.get('risk_score', 0) > 50:
            concerns.append('legal_compliance')
        
        if platform.get('risk_score', 0) > 40:
            concerns.append('platform_policy')
        
        if industry.get('applicable', False) and industry.get('risk_score', 0) > 30:
            concerns.append('industry_regulation')
        
        if not concerns:
            concerns.append('minor_content_flags')
        
        return concerns
    
    def _calculate_confidence(self, insights: Dict[str, Any]) -> float:
        """Calculate confidence score for compliance analysis"""
        confidence_factors = []
        
        # Platform coverage factor
        platform_analysis = insights.get('platform_analysis', {})
        if platform_analysis.get('platform') in self.platform_policies:
            confidence_factors.append(90)
        else:
            confidence_factors.append(70)
        
        # Legal analysis completeness
        legal_analysis = insights.get('legal_analysis', {})
        if legal_analysis.get('issues'):
            confidence_factors.append(95)  # High confidence when issues are found
        else:
            confidence_factors.append(85)  # Good confidence for clean content
        
        # Industry applicability
        industry_analysis = insights.get('industry_analysis', {})
        if industry_analysis.get('applicable', False):
            confidence_factors.append(90)
        else:
            confidence_factors.append(80)
        
        # Content analysis depth
        total_flags = insights.get('total_flags', 0)
        if total_flags > 0:
            confidence_factors.append(95)  # High confidence when flags are detected
        else:
            confidence_factors.append(85)  # Good confidence for clean content
        
        return sum(confidence_factors) / len(confidence_factors)
    
    def validate_input(self, input_data: ToolInput) -> bool:
        """Validate input data for compliance checking"""
        missing_fields = []
        
        # Check required fields
        if not input_data.headline.strip():
            missing_fields.append('headline')
        if not input_data.body_text.strip():
            missing_fields.append('body_text')
        if not input_data.platform.strip():
            missing_fields.append('platform')
        
        if missing_fields:
            raise ToolValidationError(
                self.name,
                f"Missing required fields for compliance check: {missing_fields}",
                missing_fields
            )
        
        # Validate platform
        if input_data.platform.lower() not in self.platform_policies:
            # This is a warning, not a blocking error
            pass
        
        return True
    
    def get_output_scores(self) -> List[str]:
        """Get list of scores this tool outputs"""
        return [
            'overall_compliance_score', 'platform_compliance_score',
            'legal_compliance_score', 'industry_compliance_score',
            'content_compliance_score'
        ]
    
    @classmethod
    def default_config(cls) -> ToolConfig:
        """Get default configuration for this tool"""
        return ToolConfig(
            name="compliance_checker",
            tool_type=ToolType.VALIDATOR,
            timeout=25.0,
            parameters={
                'strict_mode': False,
                'include_character_limits': True,
                'max_alternatives': 10
            }
        )