"""
Psychology Scorer Tool - Evaluates copy against established psychological persuasion principles
Scores 15+ triggers, cognitive biases, and emotional vs rational appeal balance
"""

import time
import re
from typing import Dict, Any, List, Optional, Tuple
from ..core import ToolRunner, ToolInput, ToolOutput, ToolConfig, ToolType
from ..exceptions import ToolValidationError


class PsychologyScorerToolRunner(ToolRunner):
    """
    Psychology Scorer Tool
    
    Evaluates copy against psychological persuasion principles:
    - Scores 15+ triggers: urgency, scarcity, social proof, authority, reciprocity, etc.
    - Identifies cognitive biases being leveraged
    - Measures emotional vs rational appeal balance
    - Evaluates trust signals and credibility markers
    - Assesses psychological flow and persuasion sequence
    - Provides comprehensive psychology scorecard with trigger-specific recommendations
    """
    
    def __init__(self, config: ToolConfig):
        super().__init__(config)
        
        # Comprehensive psychological triggers and their indicators
        self.psychological_triggers = {
            'scarcity': {
                'indicators': ['limited', 'exclusive', 'rare', 'only', 'few left', 'running out', 'last chance', 'while supplies last'],
                'weight': 8.5,
                'description': 'Creates urgency through limited availability',
                'effectiveness': 'high'
            },
            'urgency': {
                'indicators': ['now', 'today', 'immediate', 'urgent', 'deadline', 'expires', 'hurry', 'act fast', 'don\'t wait'],
                'weight': 8.0,
                'description': 'Motivates immediate action through time pressure',
                'effectiveness': 'high'
            },
            'social_proof': {
                'indicators': ['customers', 'users', 'people', 'thousands', 'millions', 'everyone', 'popular', 'trending', 'bestseller'],
                'weight': 9.0,
                'description': 'Leverages others\' behavior as validation',
                'effectiveness': 'very_high'
            },
            'authority': {
                'indicators': ['expert', 'doctor', 'professor', 'certified', 'endorsed', 'recommended', 'approved', 'official'],
                'weight': 7.5,
                'description': 'Uses credible sources for persuasion',
                'effectiveness': 'high'
            },
            'reciprocity': {
                'indicators': ['free', 'gift', 'bonus', 'complimentary', 'no charge', 'on us', 'give you', 'help you'],
                'weight': 7.0,
                'description': 'Triggers obligation through giving',
                'effectiveness': 'medium_high'
            },
            'commitment_consistency': {
                'indicators': ['promise', 'guarantee', 'commit', 'agree', 'pledge', 'word', 'consistent', 'always'],
                'weight': 6.5,
                'description': 'Leverages desire for consistency',
                'effectiveness': 'medium_high'
            },
            'liking': {
                'indicators': ['like you', 'similar', 'understand', 'relate', 'same', 'share', 'common', 'together'],
                'weight': 6.0,
                'description': 'Builds connection and similarity',
                'effectiveness': 'medium'
            },
            'loss_aversion': {
                'indicators': ['lose', 'miss out', 'don\'t lose', 'avoid', 'prevent', 'protect', 'risk', 'mistake'],
                'weight': 8.0,
                'description': 'Fear of losing something valuable',
                'effectiveness': 'high'
            },
            'anchoring': {
                'indicators': ['normally', 'usually', 'compare', 'vs', 'instead of', 'was', 'retail', 'list price'],
                'weight': 7.0,
                'description': 'Sets reference point for comparison',
                'effectiveness': 'medium_high'
            },
            'bandwagon': {
                'indicators': ['join', 'everyone', 'crowd', 'movement', 'trend', 'wave', 'revolution', 'everyone\'s doing'],
                'weight': 6.5,
                'description': 'Pressure to follow the crowd',
                'effectiveness': 'medium_high'
            },
            'fear_appeal': {
                'indicators': ['danger', 'risk', 'threat', 'warning', 'beware', 'avoid', 'protect', 'secure', 'safe'],
                'weight': 7.5,
                'description': 'Motivates through fear avoidance',
                'effectiveness': 'high'
            },
            'curiosity_gap': {
                'indicators': ['secret', 'hidden', 'revealed', 'discover', 'find out', 'learn', 'mystery', 'unknown'],
                'weight': 7.0,
                'description': 'Creates desire to know more',
                'effectiveness': 'medium_high'
            },
            'exclusivity': {
                'indicators': ['exclusive', 'members only', 'invitation', 'select', 'elite', 'vip', 'private', 'special access'],
                'weight': 6.5,
                'description': 'Appeals to desire for special status',
                'effectiveness': 'medium_high'
            },
            'progress_momentum': {
                'indicators': ['progress', 'momentum', 'building', 'growing', 'advancing', 'moving forward', 'next level'],
                'weight': 6.0,
                'description': 'Leverages desire for advancement',
                'effectiveness': 'medium'
            },
            'novelty_bias': {
                'indicators': ['new', 'latest', 'breakthrough', 'revolutionary', 'innovative', 'cutting-edge', 'advanced'],
                'weight': 6.5,
                'description': 'Attraction to new and innovative',
                'effectiveness': 'medium_high'
            },
            'endowment_effect': {
                'indicators': ['your', 'yours', 'own', 'belongs', 'keep', 'take home', 'possession', 'claim'],
                'weight': 6.0,
                'description': 'Increased value of owned items',
                'effectiveness': 'medium'
            }
        }
        
        # Cognitive biases detection patterns
        self.cognitive_biases = {
            'confirmation_bias': {
                'patterns': [r'you already know', r'confirms what', r'proves that', r'validates your'],
                'description': 'Reinforces existing beliefs'
            },
            'availability_heuristic': {
                'patterns': [r'remember when', r'think about', r'imagine', r'picture this'],
                'description': 'Uses easily recalled examples'
            },
            'halo_effect': {
                'patterns': [r'award-winning', r'#1 rated', r'top choice', r'best in class'],
                'description': 'Overall impression affects specific traits'
            },
            'framing_effect': {
                'patterns': [r'95% success', r'only 5% fail', r'9 out of 10', r'save \$\d+'],
                'description': 'Presentation affects perception'
            },
            'decoy_effect': {
                'patterns': [r'compare to', r'versus', r'choice A or B', r'premium vs standard'],
                'description': 'Third option influences choice'
            },
            'sunk_cost_fallacy': {
                'patterns': [r'invested', r'already spent', r'don\'t waste', r'complete the'],
                'description': 'Continue due to past investment'
            }
        }
        
        # Emotional vs rational indicators
        self.emotional_indicators = {
            'positive_emotions': ['love', 'joy', 'excitement', 'happiness', 'delight', 'amazing', 'incredible', 'wonderful'],
            'negative_emotions': ['fear', 'worry', 'stress', 'anxiety', 'frustration', 'anger', 'disappointed', 'concerned'],
            'emotional_words': ['feel', 'emotion', 'heart', 'soul', 'passion', 'dream', 'desire', 'love', 'hate']
        }
        
        self.rational_indicators = {
            'logical_words': ['because', 'therefore', 'proven', 'data', 'research', 'study', 'evidence', 'fact'],
            'numbers_stats': [r'\d+%', r'\d+x', r'\$\d+', r'\d+ years', r'\d+ customers'],
            'comparison_words': ['compare', 'versus', 'better than', 'more than', 'less than', 'superior']
        }
        
        # Trust signals and credibility markers
        self.trust_signals = {
            'testimonials': ['testimonial', 'review', 'customer says', 'client feedback', 'user review'],
            'guarantees': ['guarantee', 'money back', 'risk free', 'no questions asked', 'satisfaction guaranteed'],
            'certifications': ['certified', 'accredited', 'licensed', 'approved', 'verified', 'badge', 'seal'],
            'security': ['secure', 'safe', 'protected', 'ssl', 'encrypted', 'privacy', 'confidential'],
            'social_validation': ['rated', 'award', 'recognition', 'featured in', 'mentioned in', 'press'],
            'transparency': ['honest', 'transparent', 'open', 'clear', 'upfront', 'no hidden']
        }
        
        # Persuasion sequence patterns
        self.persuasion_sequences = {
            'problem_solution': ['problem → solution', 'pain → relief', 'challenge → answer'],
            'before_after': ['before → after', 'current state → desired state', 'now → future'],
            'feature_benefit': ['feature → benefit', 'what → why', 'how → result'],
            'proof_promise': ['evidence → promise', 'data → outcome', 'proof → guarantee']
        }
    
    async def run(self, input_data: ToolInput) -> ToolOutput:
        """Evaluate copy using comprehensive psychology framework"""
        start_time = time.time()
        
        try:
            # Combine all text for analysis
            full_text = f"{input_data.headline} {input_data.body_text} {input_data.cta}"
            
            # Extract psychographics and campaign intent
            target_psychographics = self._extract_psychographics(input_data)
            campaign_intent = self._extract_campaign_intent(input_data)
            
            # Analyze psychological triggers
            trigger_analysis = self._analyze_psychological_triggers(full_text)
            
            # Analyze cognitive biases
            bias_analysis = self._analyze_cognitive_biases(full_text)
            
            # Analyze emotional vs rational balance
            emotion_ratio_analysis = self._analyze_emotional_rational_balance(full_text)
            
            # Analyze trust signals
            trust_analysis = self._analyze_trust_signals(full_text)
            
            # Analyze persuasion sequence
            sequence_analysis = self._analyze_persuasion_sequence(input_data, full_text)
            
            # Calculate psychology scores
            trigger_effectiveness = self._calculate_trigger_effectiveness(trigger_analysis)
            bias_utilization = self._calculate_bias_utilization(bias_analysis)
            emotional_balance = self._calculate_emotional_balance(emotion_ratio_analysis)
            trust_credibility = self._calculate_trust_credibility(trust_analysis)
            sequence_flow = self._calculate_sequence_flow(sequence_analysis)
            
            # Prepare scores
            scores = {
                'trigger_effectiveness_score': trigger_effectiveness,
                'bias_utilization_score': bias_utilization,
                'emotional_balance_score': emotional_balance,
                'trust_credibility_score': trust_credibility,
                'sequence_flow_score': sequence_flow,
                'overall_psychology_score': (trigger_effectiveness + bias_utilization + emotional_balance + trust_credibility + sequence_flow) / 5
            }
            
            # Generate psychology recommendations
            recommendations = self._generate_psychology_recommendations(
                trigger_analysis, bias_analysis, emotion_ratio_analysis, 
                trust_analysis, sequence_analysis, target_psychographics
            )
            
            # Detailed insights
            insights = {
                'psychological_profile': {
                    'dominant_triggers': self._identify_dominant_triggers(trigger_analysis),
                    'trigger_intensity': self._calculate_trigger_intensity(trigger_analysis),
                    'psychological_approach': self._determine_psychological_approach(trigger_analysis, emotion_ratio_analysis),
                    'target_audience_alignment': self._assess_audience_alignment(trigger_analysis, target_psychographics)
                },
                'cognitive_influence': {
                    'biases_leveraged': bias_analysis,
                    'influence_techniques': self._identify_influence_techniques(trigger_analysis),
                    'persuasion_pathway': sequence_analysis['identified_sequence'],
                    'decision_factors': self._identify_decision_factors(trigger_analysis, trust_analysis)
                },
                'emotional_analysis': {
                    'emotional_ratio': emotion_ratio_analysis,
                    'emotional_journey': self._map_emotional_journey(input_data, emotion_ratio_analysis),
                    'rational_support': self._assess_rational_support(full_text),
                    'appeal_balance': 'emotional' if emotion_ratio_analysis['emotional_score'] > emotion_ratio_analysis['rational_score'] else 'rational'
                },
                'trust_factors': {
                    'credibility_elements': trust_analysis,
                    'risk_reduction': self._assess_risk_reduction(trust_analysis),
                    'authority_establishment': self._assess_authority_establishment(trigger_analysis, trust_analysis),
                    'social_validation': self._assess_social_validation(trigger_analysis, trust_analysis)
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
                execution_time=execution_time,
                request_id=input_data.request_id,
                confidence_score=self._calculate_confidence(insights, trigger_analysis)
            )
            
        except Exception as e:
            execution_time = time.time() - start_time
            
            return ToolOutput(
                tool_name=self.name,
                tool_type=self.tool_type,
                success=False,
                execution_time=execution_time,
                request_id=input_data.request_id,
                error_message=f"Psychology scoring failed: {str(e)}"
            )
    
    def _extract_psychographics(self, input_data: ToolInput) -> Dict[str, Any]:
        """Extract target audience psychographics"""
        # In practice, this would parse from input_data.additional_data
        return {
            'decision_style': 'analytical',
            'risk_tolerance': 'moderate',
            'motivation_type': 'achievement',
            'information_processing': 'detailed',
            'social_influence': 'moderate'
        }
    
    def _extract_campaign_intent(self, input_data: ToolInput) -> str:
        """Extract campaign intent (awareness vs conversion)"""
        # Simple heuristic based on CTA
        cta_lower = input_data.cta.lower()
        
        if any(word in cta_lower for word in ['buy', 'purchase', 'order', 'get now']):
            return 'conversion'
        elif any(word in cta_lower for word in ['learn', 'discover', 'read', 'watch']):
            return 'awareness'
        else:
            return 'consideration'
    
    def _analyze_psychological_triggers(self, text: str) -> Dict[str, Any]:
        """Analyze presence and strength of psychological triggers"""
        text_lower = text.lower()
        trigger_analysis = {}
        
        for trigger_name, trigger_data in self.psychological_triggers.items():
            # Count indicator matches
            matches = []
            for indicator in trigger_data['indicators']:
                if indicator in text_lower:
                    matches.append(indicator)
            
            # Calculate trigger score
            raw_score = len(matches) * 20  # Base score per match
            weighted_score = min(raw_score * (trigger_data['weight'] / 10), 100)
            
            trigger_analysis[trigger_name] = {
                'present': len(matches) > 0,
                'matches': matches,
                'raw_score': raw_score,
                'weighted_score': weighted_score,
                'strength': self._determine_trigger_strength(weighted_score),
                'effectiveness': trigger_data['effectiveness'],
                'description': trigger_data['description']
            }
        
        return trigger_analysis
    
    def _analyze_cognitive_biases(self, text: str) -> Dict[str, Any]:
        """Analyze cognitive biases being leveraged"""
        bias_analysis = {}
        
        for bias_name, bias_data in self.cognitive_biases.items():
            matches = []
            for pattern in bias_data['patterns']:
                if re.search(pattern, text, re.IGNORECASE):
                    matches.append(pattern)
            
            bias_analysis[bias_name] = {
                'present': len(matches) > 0,
                'pattern_matches': len(matches),
                'description': bias_data['description'],
                'strength': 'high' if len(matches) >= 2 else 'medium' if len(matches) == 1 else 'none'
            }
        
        return bias_analysis
    
    def _analyze_emotional_rational_balance(self, text: str) -> Dict[str, Any]:
        """Analyze emotional vs rational appeal balance"""
        text_lower = text.lower()
        
        # Count emotional indicators
        emotional_score = 0
        emotional_matches = []
        
        for emotion_list in self.emotional_indicators.values():
            for word in emotion_list:
                if word in text_lower:
                    emotional_score += 1
                    emotional_matches.append(word)
        
        # Count rational indicators
        rational_score = 0
        rational_matches = []
        
        for word in self.rational_indicators['logical_words']:
            if word in text_lower:
                rational_score += 2  # Logical words get higher weight
                rational_matches.append(word)
        
        for pattern in self.rational_indicators['numbers_stats']:
            matches = re.findall(pattern, text)
            rational_score += len(matches) * 3  # Stats get highest weight
            rational_matches.extend(matches)
        
        for word in self.rational_indicators['comparison_words']:
            if word in text_lower:
                rational_score += 1
                rational_matches.append(word)
        
        # Calculate balance
        total_score = emotional_score + rational_score
        if total_score > 0:
            emotional_ratio = emotional_score / total_score
            rational_ratio = rational_score / total_score
        else:
            emotional_ratio = rational_ratio = 0.5
        
        return {
            'emotional_score': emotional_score,
            'rational_score': rational_score,
            'emotional_ratio': emotional_ratio,
            'rational_ratio': rational_ratio,
            'emotional_matches': emotional_matches,
            'rational_matches': rational_matches,
            'balance_type': 'emotional' if emotional_ratio > 0.6 else 'rational' if rational_ratio > 0.6 else 'balanced'
        }
    
    def _analyze_trust_signals(self, text: str) -> Dict[str, Any]:
        """Analyze trust signals and credibility markers"""
        text_lower = text.lower()
        trust_analysis = {}
        
        for signal_type, indicators in self.trust_signals.items():
            matches = [indicator for indicator in indicators if indicator in text_lower]
            
            trust_analysis[signal_type] = {
                'present': len(matches) > 0,
                'matches': matches,
                'count': len(matches),
                'strength': 'strong' if len(matches) >= 2 else 'moderate' if len(matches) == 1 else 'weak'
            }
        
        return trust_analysis
    
    def _analyze_persuasion_sequence(self, input_data: ToolInput, text: str) -> Dict[str, Any]:
        """Analyze persuasion sequence and flow"""
        sequence_analysis = {
            'headline_approach': self._classify_headline_approach(input_data.headline),
            'body_structure': self._analyze_body_structure(input_data.body_text),
            'cta_alignment': self._analyze_cta_alignment(input_data.cta, text),
            'logical_flow': self._assess_logical_flow(input_data),
            'identified_sequence': None
        }
        
        # Identify persuasion sequence pattern
        full_structure = f"{sequence_analysis['headline_approach']} → {sequence_analysis['body_structure']} → {sequence_analysis['cta_alignment']}"
        
        # Simple pattern matching for common sequences
        if 'problem' in sequence_analysis['headline_approach'] and 'solution' in sequence_analysis['body_structure']:
            sequence_analysis['identified_sequence'] = 'problem_solution'
        elif 'benefit' in sequence_analysis['headline_approach'] and 'proof' in sequence_analysis['body_structure']:
            sequence_analysis['identified_sequence'] = 'promise_proof'
        elif 'curiosity' in sequence_analysis['headline_approach'] and 'reveal' in sequence_analysis['body_structure']:
            sequence_analysis['identified_sequence'] = 'curiosity_satisfaction'
        else:
            sequence_analysis['identified_sequence'] = 'custom'
        
        return sequence_analysis
    
    def _classify_headline_approach(self, headline: str) -> str:
        """Classify the headline approach"""
        headline_lower = headline.lower()
        
        if '?' in headline:
            return 'question'
        elif any(word in headline_lower for word in ['problem', 'struggle', 'challenge']):
            return 'problem'
        elif any(word in headline_lower for word in ['benefit', 'get', 'achieve', 'improve']):
            return 'benefit'
        elif any(word in headline_lower for word in ['secret', 'hidden', 'revealed']):
            return 'curiosity'
        elif any(char.isdigit() for char in headline):
            return 'number'
        else:
            return 'statement'
    
    def _analyze_body_structure(self, body_text: str) -> str:
        """Analyze body text structure"""
        body_lower = body_text.lower()
        
        if any(word in body_lower for word in ['solution', 'answer', 'fix']):
            return 'solution'
        elif any(word in body_lower for word in ['proof', 'evidence', 'data', 'research']):
            return 'proof'
        elif any(word in body_lower for word in ['story', 'experience', 'journey']):
            return 'story'
        elif any(word in body_lower for word in ['features', 'includes', 'offers']):
            return 'features'
        else:
            return 'explanation'
    
    def _analyze_cta_alignment(self, cta: str, full_text: str) -> str:
        """Analyze CTA alignment with content"""
        cta_lower = cta.lower()
        
        if any(word in cta_lower for word in ['buy', 'purchase', 'order']):
            return 'direct_action'
        elif any(word in cta_lower for word in ['learn', 'discover', 'find out']):
            return 'information_seeking'
        elif any(word in cta_lower for word in ['try', 'test', 'experience']):
            return 'trial'
        elif any(word in cta_lower for word in ['get', 'claim', 'access']):
            return 'acquisition'
        else:
            return 'generic'
    
    def _assess_logical_flow(self, input_data: ToolInput) -> str:
        """Assess logical flow of the copy"""
        # Simple assessment based on structure
        headline = input_data.headline.lower()
        body = input_data.body_text.lower()
        cta = input_data.cta.lower()
        
        # Check for logical progression
        if ('problem' in headline or 'challenge' in headline) and 'solution' in body and 'get' in cta:
            return 'strong'
        elif ('benefit' in headline or 'get' in headline) and 'how' in body and 'start' in cta:
            return 'strong'
        else:
            return 'moderate'
    
    def _calculate_trigger_effectiveness(self, trigger_analysis: Dict) -> float:
        """Calculate overall trigger effectiveness score"""
        total_score = 0
        active_triggers = 0
        
        for trigger_name, data in trigger_analysis.items():
            if data['present']:
                total_score += data['weighted_score']
                active_triggers += 1
        
        # Bonus for trigger diversity
        diversity_bonus = min(active_triggers * 2, 20)
        
        # Average score with diversity bonus
        if active_triggers > 0:
            average_score = total_score / active_triggers
            final_score = min(average_score + diversity_bonus, 100)
        else:
            final_score = 0
        
        return final_score
    
    def _calculate_bias_utilization(self, bias_analysis: Dict) -> float:
        """Calculate cognitive bias utilization score"""
        score = 60  # Base score
        
        active_biases = sum(1 for data in bias_analysis.values() if data['present'])
        strong_biases = sum(1 for data in bias_analysis.values() if data['strength'] == 'high')
        
        # Add points for active biases
        score += active_biases * 8
        
        # Bonus for strong biases
        score += strong_biases * 5
        
        return min(score, 100)
    
    def _calculate_emotional_balance(self, emotion_analysis: Dict) -> float:
        """Calculate emotional balance score"""
        balance_type = emotion_analysis['balance_type']
        emotional_score = emotion_analysis['emotional_score']
        rational_score = emotion_analysis['rational_score']
        
        # Base score depends on balance type
        if balance_type == 'balanced':
            base_score = 85  # Balanced is generally good
        elif balance_type == 'emotional':
            base_score = 75  # Emotional can be effective
        else:  # rational
            base_score = 70  # Purely rational might be less engaging
        
        # Bonus for having both elements
        if emotional_score > 0 and rational_score > 0:
            base_score += 10
        
        # Penalty for complete absence of emotion or logic
        if emotional_score == 0:
            base_score -= 15
        if rational_score == 0:
            base_score -= 10
        
        return max(0, min(base_score, 100))
    
    def _calculate_trust_credibility(self, trust_analysis: Dict) -> float:
        """Calculate trust and credibility score"""
        score = 50  # Base score
        
        # Add points for each type of trust signal present
        for signal_type, data in trust_analysis.items():
            if data['present']:
                if data['strength'] == 'strong':
                    score += 12
                elif data['strength'] == 'moderate':
                    score += 8
                else:
                    score += 4
        
        return min(score, 100)
    
    def _calculate_sequence_flow(self, sequence_analysis: Dict) -> float:
        """Calculate persuasion sequence flow score"""
        score = 60  # Base score
        
        # Points for logical flow
        if sequence_analysis['logical_flow'] == 'strong':
            score += 20
        elif sequence_analysis['logical_flow'] == 'moderate':
            score += 10
        
        # Points for identified sequence
        if sequence_analysis['identified_sequence'] in ['problem_solution', 'promise_proof']:
            score += 15
        elif sequence_analysis['identified_sequence'] != 'custom':
            score += 10
        
        # Points for CTA alignment
        if sequence_analysis['cta_alignment'] in ['direct_action', 'acquisition']:
            score += 5
        
        return min(score, 100)
    
    def _determine_trigger_strength(self, score: float) -> str:
        """Determine trigger strength based on score"""
        if score >= 80:
            return 'very_strong'
        elif score >= 60:
            return 'strong'
        elif score >= 40:
            return 'moderate'
        elif score >= 20:
            return 'weak'
        else:
            return 'very_weak'
    
    def _identify_dominant_triggers(self, trigger_analysis: Dict) -> List[Dict[str, Any]]:
        """Identify the most dominant psychological triggers"""
        active_triggers = [(name, data) for name, data in trigger_analysis.items() if data['present']]
        sorted_triggers = sorted(active_triggers, key=lambda x: x[1]['weighted_score'], reverse=True)
        
        return [{
            'trigger': name,
            'score': data['weighted_score'],
            'strength': data['strength'],
            'matches': len(data['matches'])
        } for name, data in sorted_triggers[:5]]
    
    def _calculate_trigger_intensity(self, trigger_analysis: Dict) -> str:
        """Calculate overall trigger intensity"""
        active_count = sum(1 for data in trigger_analysis.values() if data['present'])
        avg_score = sum(data['weighted_score'] for data in trigger_analysis.values() if data['present'])
        avg_score = avg_score / active_count if active_count > 0 else 0
        
        if active_count >= 8 and avg_score >= 60:
            return 'very_high'
        elif active_count >= 5 and avg_score >= 50:
            return 'high'
        elif active_count >= 3 and avg_score >= 40:
            return 'moderate'
        else:
            return 'low'
    
    def _determine_psychological_approach(self, trigger_analysis: Dict, emotion_analysis: Dict) -> str:
        """Determine overall psychological approach"""
        dominant_triggers = self._identify_dominant_triggers(trigger_analysis)
        
        if not dominant_triggers:
            return 'neutral'
        
        top_trigger = dominant_triggers[0]['trigger']
        balance_type = emotion_analysis['balance_type']
        
        if top_trigger in ['fear_appeal', 'loss_aversion'] and balance_type == 'emotional':
            return 'fear_based'
        elif top_trigger in ['social_proof', 'bandwagon'] and balance_type == 'emotional':
            return 'social_influence'
        elif top_trigger in ['authority', 'commitment_consistency'] and balance_type == 'rational':
            return 'logical_authority'
        elif top_trigger in ['scarcity', 'urgency'] and balance_type == 'emotional':
            return 'urgency_driven'
        else:
            return 'mixed_approach'
    
    def _assess_audience_alignment(self, trigger_analysis: Dict, psychographics: Dict) -> str:
        """Assess alignment with target audience psychographics"""
        # Simple alignment assessment
        decision_style = psychographics.get('decision_style', 'analytical')
        dominant_triggers = self._identify_dominant_triggers(trigger_analysis)
        
        if not dominant_triggers:
            return 'unknown'
        
        top_trigger = dominant_triggers[0]['trigger']
        
        if decision_style == 'analytical':
            if top_trigger in ['authority', 'social_proof', 'commitment_consistency']:
                return 'well_aligned'
            else:
                return 'moderately_aligned'
        elif decision_style == 'intuitive':
            if top_trigger in ['emotion', 'curiosity_gap', 'novelty_bias']:
                return 'well_aligned'
            else:
                return 'moderately_aligned'
        else:
            return 'moderately_aligned'
    
    def _identify_influence_techniques(self, trigger_analysis: Dict) -> List[str]:
        """Identify primary influence techniques being used"""
        techniques = []
        
        for trigger_name, data in trigger_analysis.items():
            if data['present'] and data['weighted_score'] >= 50:
                if trigger_name in ['social_proof', 'authority', 'liking']:
                    techniques.append('Cialdini Principles')
                elif trigger_name in ['loss_aversion', 'anchoring', 'endowment_effect']:
                    techniques.append('Behavioral Economics')
                elif trigger_name in ['scarcity', 'urgency', 'exclusivity']:
                    techniques.append('Scarcity Marketing')
                elif trigger_name in ['fear_appeal', 'curiosity_gap']:
                    techniques.append('Emotional Appeals')
        
        return list(set(techniques))
    
    def _identify_decision_factors(self, trigger_analysis: Dict, trust_analysis: Dict) -> List[str]:
        """Identify key decision factors being addressed"""
        factors = []
        
        # From psychological triggers
        for trigger_name, data in trigger_analysis.items():
            if data['present']:
                if trigger_name == 'social_proof':
                    factors.append('Social validation')
                elif trigger_name == 'authority':
                    factors.append('Expert credibility')
                elif trigger_name in ['scarcity', 'urgency']:
                    factors.append('Time sensitivity')
                elif trigger_name == 'loss_aversion':
                    factors.append('Risk mitigation')
        
        # From trust signals
        for signal_type, data in trust_analysis.items():
            if data['present']:
                if signal_type == 'guarantees':
                    factors.append('Risk reversal')
                elif signal_type == 'testimonials':
                    factors.append('User validation')
                elif signal_type == 'certifications':
                    factors.append('Third-party verification')
        
        return list(set(factors))
    
    def _map_emotional_journey(self, input_data: ToolInput, emotion_analysis: Dict) -> Dict[str, str]:
        """Map the emotional journey through the copy"""
        return {
            'headline_emotion': self._detect_primary_emotion(input_data.headline),
            'body_emotion': self._detect_primary_emotion(input_data.body_text),
            'cta_emotion': self._detect_primary_emotion(input_data.cta),
            'overall_trajectory': emotion_analysis['balance_type']
        }
    
    def _detect_primary_emotion(self, text: str) -> str:
        """Detect primary emotion in text segment"""
        text_lower = text.lower()
        
        # Check for specific emotional indicators
        if any(word in text_lower for word in ['exciting', 'amazing', 'incredible', 'love']):
            return 'positive'
        elif any(word in text_lower for word in ['worry', 'fear', 'problem', 'struggle']):
            return 'negative'
        elif any(word in text_lower for word in ['curious', 'discover', 'secret', 'reveal']):
            return 'curiosity'
        elif any(word in text_lower for word in ['urgent', 'now', 'hurry', 'fast']):
            return 'urgency'
        else:
            return 'neutral'
    
    def _assess_rational_support(self, text: str) -> Dict[str, Any]:
        """Assess rational support elements"""
        return {
            'has_statistics': bool(re.search(r'\d+%', text)),
            'has_evidence': any(word in text.lower() for word in ['proven', 'research', 'study']),
            'has_comparisons': any(word in text.lower() for word in ['vs', 'versus', 'compared']),
            'logical_structure': 'because' in text.lower() or 'therefore' in text.lower()
        }
    
    def _assess_risk_reduction(self, trust_analysis: Dict) -> str:
        """Assess risk reduction strength"""
        risk_reducing_signals = ['guarantees', 'security', 'certifications']
        strong_signals = sum(1 for signal in risk_reducing_signals 
                           if trust_analysis.get(signal, {}).get('strength') == 'strong')
        
        if strong_signals >= 2:
            return 'strong'
        elif strong_signals >= 1:
            return 'moderate'
        else:
            return 'weak'
    
    def _assess_authority_establishment(self, trigger_analysis: Dict, trust_analysis: Dict) -> str:
        """Assess authority establishment strength"""
        authority_score = trigger_analysis.get('authority', {}).get('weighted_score', 0)
        cert_strength = trust_analysis.get('certifications', {}).get('strength', 'weak')
        social_strength = trust_analysis.get('social_validation', {}).get('strength', 'weak')
        
        if authority_score >= 60 and cert_strength == 'strong':
            return 'strong'
        elif authority_score >= 40 or cert_strength == 'moderate':
            return 'moderate'
        else:
            return 'weak'
    
    def _assess_social_validation(self, trigger_analysis: Dict, trust_analysis: Dict) -> str:
        """Assess social validation strength"""
        social_score = trigger_analysis.get('social_proof', {}).get('weighted_score', 0)
        testimonial_strength = trust_analysis.get('testimonials', {}).get('strength', 'weak')
        
        if social_score >= 60 and testimonial_strength == 'strong':
            return 'strong'
        elif social_score >= 40 or testimonial_strength == 'moderate':
            return 'moderate'
        else:
            return 'weak'
    
    def _generate_psychology_recommendations(self, trigger_analysis: Dict, bias_analysis: Dict,
                                           emotion_analysis: Dict, trust_analysis: Dict,
                                           sequence_analysis: Dict, psychographics: Dict) -> List[str]:
        """Generate psychology-specific recommendations"""
        recommendations = []
        
        # Trigger recommendations
        dominant_triggers = self._identify_dominant_triggers(trigger_analysis)
        if len(dominant_triggers) < 3:
            recommendations.append("Incorporate more psychological triggers - aim for 3-5 strong triggers for maximum impact")
        
        # Specific trigger suggestions
        if not any(t['trigger'] in ['social_proof', 'authority'] for t in dominant_triggers):
            recommendations.append("Add social proof or authority elements to increase credibility and trust")
        
        if not any(t['trigger'] in ['urgency', 'scarcity'] for t in dominant_triggers):
            recommendations.append("Include urgency or scarcity triggers to motivate immediate action")
        
        # Emotional balance recommendations
        if emotion_analysis['balance_type'] == 'rational' and emotion_analysis['emotional_score'] == 0:
            recommendations.append("Add emotional elements to create stronger connection and engagement")
        elif emotion_analysis['balance_type'] == 'emotional' and emotion_analysis['rational_score'] == 0:
            recommendations.append("Include logical support (stats, evidence) to justify emotional appeals")
        
        # Trust signal recommendations
        trust_gaps = [signal for signal, data in trust_analysis.items() 
                     if data['strength'] == 'weak' and signal in ['guarantees', 'testimonials']]
        if trust_gaps:
            recommendations.append(f"Strengthen trust signals: add {trust_gaps[0]} to reduce purchase anxiety")
        
        # Bias utilization recommendations
        active_biases = sum(1 for data in bias_analysis.values() if data['present'])
        if active_biases < 2:
            recommendations.append("Leverage more cognitive biases - consider anchoring or social proof biases")
        
        # Sequence flow recommendations
        if sequence_analysis['logical_flow'] != 'strong':
            recommendations.append("Improve logical flow: ensure headline problem connects to body solution and CTA action")
        
        return recommendations[:6]  # Limit to top 6 recommendations
    
    def _calculate_confidence(self, insights: Dict, trigger_analysis: Dict) -> float:
        """Calculate confidence in psychology analysis"""
        confidence_factors = []
        
        # Trigger analysis depth
        active_triggers = sum(1 for data in trigger_analysis.values() if data['present'])
        if active_triggers >= 5:
            confidence_factors.append(90)
        elif active_triggers >= 3:
            confidence_factors.append(85)
        else:
            confidence_factors.append(75)
        
        # Analysis completeness
        if insights.get('emotional_analysis') and insights.get('trust_factors'):
            confidence_factors.append(95)
        else:
            confidence_factors.append(80)
        
        # Psychological profile clarity
        psychological_profile = insights.get('psychological_profile', {})
        if psychological_profile.get('dominant_triggers') and psychological_profile.get('psychological_approach'):
            confidence_factors.append(90)
        else:
            confidence_factors.append(75)
        
        return sum(confidence_factors) / len(confidence_factors)
    
    def validate_input(self, input_data: ToolInput) -> bool:
        """Validate input data for psychology scoring"""
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
                f"Missing required fields for psychology scoring: {missing_fields}",
                missing_fields
            )
        
        return True
    
    def get_output_scores(self) -> List[str]:
        """Get list of scores this tool outputs"""
        return [
            'trigger_effectiveness_score', 'bias_utilization_score',
            'emotional_balance_score', 'trust_credibility_score',
            'sequence_flow_score', 'overall_psychology_score'
        ]
    
    @classmethod
    def default_config(cls) -> ToolConfig:
        """Get default configuration for this tool"""
        return ToolConfig(
            name="psychology_scorer",
            tool_type=ToolType.ANALYZER,
            timeout=30.0,
            parameters={
                'analyze_all_triggers': True,
                'include_bias_analysis': True,
                'emotional_balance_analysis': True,
                'trust_signal_evaluation': True
            }
        )