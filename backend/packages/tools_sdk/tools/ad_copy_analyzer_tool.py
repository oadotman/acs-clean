"""
Enhanced Ad Copy Analyzer Tool - Comprehensive marketing copy evaluation
Uses NLP and marketing frameworks to evaluate copy effectiveness
"""

import time
import re
from typing import Dict, Any, List, Optional
from ..core import ToolRunner, ToolInput, ToolOutput, ToolConfig, ToolType
from ..exceptions import ToolValidationError, ToolDependencyError

# Import analysis dependencies
try:
    import textstat
    TEXTSTAT_AVAILABLE = True
except ImportError:
    TEXTSTAT_AVAILABLE = False

# Sentiment analysis fallback
try:
    from transformers import pipeline
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False


class AdCopyAnalyzerToolRunner(ToolRunner):
    """
    Comprehensive Ad Copy Analyzer
    
    Evaluates copy effectiveness using NLP and marketing frameworks:
    - Sentiment analysis and readability scoring
    - Hook strength evaluation (first 3-5 words impact)
    - Call-to-action effectiveness rating
    - Emotional trigger identification
    - Length optimization for platform
    - Generates scored report (0-100) with specific improvement suggestions
    """
    
    def __init__(self, config: ToolConfig):
        super().__init__(config)
        
        # Initialize NLP components
        self.sentiment_analyzer = None
        if TRANSFORMERS_AVAILABLE:
            try:
                self.sentiment_analyzer = pipeline(
                    "sentiment-analysis",
                    model="cardiffnlp/twitter-roberta-base-sentiment-latest",
                    return_all_scores=True
                )
            except Exception:
                # Fallback to simpler model
                try:
                    self.sentiment_analyzer = pipeline("sentiment-analysis")
                except Exception:
                    pass
        
        # Marketing frameworks and patterns
        self.emotional_triggers = {
            'urgency': ['now', 'today', 'limited', 'expires', 'deadline', 'hurry', 'quick', 'immediate'],
            'scarcity': ['exclusive', 'limited', 'rare', 'only', 'few', 'last', 'remaining', 'sold out'],
            'social_proof': ['trusted', 'proven', 'thousands', 'millions', 'customers', 'testimonial', 'reviews'],
            'fear': ['avoid', 'prevent', 'protect', 'risk', 'danger', 'threat', 'warning', 'mistake'],
            'desire': ['want', 'love', 'dream', 'wish', 'desire', 'crave', 'amazing', 'incredible'],
            'authority': ['expert', 'professional', 'certified', 'approved', 'endorsed', 'recommended'],
            'curiosity': ['secret', 'hidden', 'discover', 'reveal', 'mystery', 'unknown', 'surprising'],
            'benefit': ['save', 'gain', 'improve', 'increase', 'boost', 'enhance', 'transform']
        }
        
        self.power_words = [
            'free', 'instant', 'guaranteed', 'proven', 'secret', 'discover',
            'amazing', 'incredible', 'ultimate', 'exclusive', 'limited',
            'breakthrough', 'revolutionary', 'new', 'save', 'now', 'today',
            'transform', 'boost', 'unlock', 'master', 'dominate', 'crush'
        ]
        
        self.weak_words = [
            'maybe', 'perhaps', 'might', 'could', 'possibly', 'try',
            'hope', 'think', 'believe', 'seem', 'appear', 'sort of'
        ]
        
        # Platform optimization guidelines
        self.platform_guidelines = {
            'facebook': {
                'headline_ideal': (5, 7),  # words
                'body_ideal': (90, 125),   # characters
                'total_limit': 2200,
                'cta_ideal': (2, 4),
                'tone': 'conversational'
            },
            'google': {
                'headline_ideal': (25, 30),  # characters
                'body_ideal': (80, 90),      # characters
                'total_limit': 90,
                'cta_ideal': (2, 3),
                'tone': 'direct'
            },
            'linkedin': {
                'headline_ideal': (8, 12),   # words
                'body_ideal': (150, 300),    # characters
                'total_limit': 3000,
                'cta_ideal': (3, 5),
                'tone': 'professional'
            },
            'tiktok': {
                'headline_ideal': (3, 6),    # words
                'body_ideal': (50, 80),      # characters
                'total_limit': 100,
                'cta_ideal': (1, 3),
                'tone': 'casual'
            },
            'instagram': {
                'headline_ideal': (4, 8),    # words
                'body_ideal': (125, 250),    # characters
                'total_limit': 2200,
                'cta_ideal': (2, 4),
                'tone': 'visual'
            }
        }
    
    async def run(self, input_data: ToolInput) -> ToolOutput:
        """Execute comprehensive ad copy analysis"""
        start_time = time.time()
        
        try:
            # Combine all text for analysis
            full_text = f"{input_data.headline} {input_data.body_text} {input_data.cta}".strip()
            
            # Core analysis components
            readability_scores = self._analyze_readability(full_text)
            sentiment_scores = await self._analyze_sentiment(full_text)
            hook_analysis = self._analyze_hook_strength(input_data.headline)
            cta_analysis = self._analyze_cta_effectiveness(input_data.cta)
            emotional_triggers = self._identify_emotional_triggers(full_text)
            platform_optimization = self._analyze_platform_fit(input_data, full_text)
            
            # Calculate overall scores
            clarity_score = readability_scores['clarity_score']
            sentiment_score = sentiment_scores['overall_sentiment_score']
            hook_score = hook_analysis['hook_strength_score']
            cta_score = cta_analysis['cta_effectiveness_score']
            emotion_score = emotional_triggers['emotional_impact_score']
            platform_score = platform_optimization['platform_fit_score']
            
            # Weighted overall score
            overall_score = self._calculate_overall_score(
                clarity_score, sentiment_score, hook_score, 
                cta_score, emotion_score, platform_score
            )
            
            # Generate comprehensive recommendations
            recommendations = self._generate_recommendations(
                readability_scores, sentiment_scores, hook_analysis,
                cta_analysis, emotional_triggers, platform_optimization
            )
            
            # Prepare output scores
            scores = {
                'overall_score': overall_score,
                'clarity_score': clarity_score,
                'sentiment_score': sentiment_score,
                'hook_strength_score': hook_score,
                'cta_effectiveness_score': cta_score,
                'emotional_impact_score': emotion_score,
                'platform_fit_score': platform_score
            }
            
            # Prepare detailed insights
            insights = {
                'readability_analysis': readability_scores,
                'sentiment_analysis': sentiment_scores,
                'hook_analysis': hook_analysis,
                'cta_analysis': cta_analysis,
                'emotional_triggers': emotional_triggers,
                'platform_optimization': platform_optimization,
                'text_metrics': {
                    'total_length': len(full_text),
                    'word_count': len(full_text.split()),
                    'sentence_count': len(re.split(r'[.!?]+', full_text)),
                    'headline_words': len(input_data.headline.split()),
                    'body_words': len(input_data.body_text.split())
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
                error_message=f"Ad copy analysis failed: {str(e)}"
            )
    
    def _analyze_readability(self, text: str) -> Dict[str, Any]:
        """Analyze text readability and clarity"""
        if not TEXTSTAT_AVAILABLE:
            # Basic fallback analysis
            word_count = len(text.split())
            sentence_count = len(re.split(r'[.!?]+', text))
            avg_words_per_sentence = word_count / max(sentence_count, 1)
            
            # Simple clarity score based on word/sentence metrics
            clarity_score = max(0, min(100, 
                100 - (avg_words_per_sentence - 10) * 2 - (word_count - 20) * 0.5
            ))
            
            return {
                'clarity_score': clarity_score,
                'word_count': word_count,
                'sentence_count': sentence_count,
                'avg_words_per_sentence': avg_words_per_sentence,
                'flesch_reading_ease': None,
                'grade_level': None
            }
        
        # Full textstat analysis
        flesch_score = textstat.flesch_reading_ease(text)
        grade_level = textstat.flesch_kincaid_grade(text)
        word_count = len(text.split())
        sentence_count = len(re.split(r'[.!?]+', text))
        avg_words_per_sentence = word_count / max(sentence_count, 1)
        
        # Calculate clarity score with marketing optimization
        base_score = min(flesch_score, 100)
        
        # Penalties for ad copy
        if grade_level > 8:  # Ads should be 8th grade or lower
            base_score *= 0.85
        if avg_words_per_sentence > 15:  # Short sentences for ads
            base_score *= 0.9
        if word_count > 50:  # Conciseness bonus for ads
            base_score *= 0.95
        
        clarity_score = max(0, base_score)
        
        return {
            'clarity_score': clarity_score,
            'flesch_reading_ease': flesch_score,
            'grade_level': grade_level,
            'word_count': word_count,
            'sentence_count': sentence_count,
            'avg_words_per_sentence': avg_words_per_sentence
        }
    
    async def _analyze_sentiment(self, text: str) -> Dict[str, Any]:
        """Analyze sentiment and emotional tone"""
        if self.sentiment_analyzer:
            try:
                results = self.sentiment_analyzer(text)
                if isinstance(results[0], list):
                    # Multiple scores returned
                    sentiment_data = results[0]
                    sentiment_scores = {item['label'].lower(): item['score'] for item in sentiment_data}
                else:
                    # Single score returned
                    sentiment_scores = {results[0]['label'].lower(): results[0]['score']}
                
                # Calculate overall sentiment score (positive bias for ads)
                positive_score = sentiment_scores.get('positive', 0)
                negative_score = sentiment_scores.get('negative', 0)
                neutral_score = sentiment_scores.get('neutral', 0)
                
                # Ads should lean positive
                overall_sentiment_score = (positive_score * 100) + (neutral_score * 50)
                
                return {
                    'overall_sentiment_score': min(100, overall_sentiment_score),
                    'sentiment_breakdown': sentiment_scores,
                    'dominant_sentiment': max(sentiment_scores, key=sentiment_scores.get),
                    'sentiment_confidence': max(sentiment_scores.values())
                }
            except Exception:
                pass
        
        # Fallback sentiment analysis
        positive_words = ['great', 'amazing', 'excellent', 'fantastic', 'wonderful', 'love', 'perfect', 'best']
        negative_words = ['bad', 'terrible', 'awful', 'hate', 'worst', 'problem', 'issue', 'difficult']
        
        text_lower = text.lower()
        positive_count = sum(1 for word in positive_words if word in text_lower)
        negative_count = sum(1 for word in negative_words if word in text_lower)
        
        sentiment_score = max(0, min(100, 50 + (positive_count * 10) - (negative_count * 10)))
        
        return {
            'overall_sentiment_score': sentiment_score,
            'sentiment_breakdown': {
                'positive_indicators': positive_count,
                'negative_indicators': negative_count
            },
            'dominant_sentiment': 'positive' if positive_count > negative_count else 'neutral',
            'sentiment_confidence': 0.6
        }
    
    def _analyze_hook_strength(self, headline: str) -> Dict[str, Any]:
        """Analyze hook strength - first 3-5 words impact"""
        if not headline.strip():
            return {
                'hook_strength_score': 0,
                'hook_words': [],
                'hook_analysis': 'No headline provided'
            }
        
        words = headline.split()
        hook_words = words[:min(5, len(words))]
        hook_text = ' '.join(hook_words)
        
        score = 50  # Base score
        
        # Check for strong opening patterns
        strong_openers = {
            'question': ['how', 'what', 'why', 'when', 'where', 'which', 'who'],
            'urgency': ['now', 'today', 'immediately', 'instant'],
            'curiosity': ['secret', 'hidden', 'discover', 'revealed'],
            'benefit': ['get', 'save', 'earn', 'gain', 'increase'],
            'social_proof': ['proven', 'trusted', 'millions', 'thousands'],
            'numbers': [str(i) for i in range(1, 101)]
        }
        
        hook_lower = hook_text.lower()
        patterns_found = []
        
        for pattern_type, words_list in strong_openers.items():
            if any(word in hook_lower for word in words_list):
                patterns_found.append(pattern_type)
                score += 10
        
        # Check for power words in hook
        power_words_in_hook = [word for word in self.power_words if word in hook_lower]
        score += len(power_words_in_hook) * 5
        
        # Check for weak words (penalty)
        weak_words_in_hook = [word for word in self.weak_words if word in hook_lower]
        score -= len(weak_words_in_hook) * 10
        
        # Length optimization
        if len(hook_words) < 2:
            score -= 15
        elif len(hook_words) > 6:
            score -= 10
        
        hook_strength_score = max(0, min(100, score))
        
        return {
            'hook_strength_score': hook_strength_score,
            'hook_words': hook_words,
            'hook_text': hook_text,
            'patterns_found': patterns_found,
            'power_words_in_hook': power_words_in_hook,
            'weak_words_in_hook': weak_words_in_hook,
            'hook_analysis': self._generate_hook_analysis(patterns_found, power_words_in_hook, weak_words_in_hook)
        }
    
    def _analyze_cta_effectiveness(self, cta: str) -> Dict[str, Any]:
        """Analyze call-to-action effectiveness"""
        if not cta.strip():
            return {
                'cta_effectiveness_score': 0,
                'cta_analysis': 'No CTA provided'
            }
        
        score = 50  # Base score
        cta_lower = cta.lower()
        
        # Strong action verbs
        action_verbs = ['get', 'start', 'try', 'discover', 'claim', 'grab', 'unlock', 'access', 'download', 'join']
        has_action_verb = any(verb in cta_lower for verb in action_verbs)
        if has_action_verb:
            score += 20
        
        # Urgency indicators
        urgency_words = ['now', 'today', 'immediately', 'instant']
        has_urgency = any(word in cta_lower for word in urgency_words)
        if has_urgency:
            score += 15
        
        # Value proposition
        value_words = ['free', 'save', 'discount', 'bonus', 'exclusive']
        has_value = any(word in cta_lower for word in value_words)
        if has_value:
            score += 10
        
        # Check for weak CTAs
        weak_ctas = ['click here', 'learn more', 'read more', 'find out', 'submit']
        is_weak = any(weak in cta_lower for weak in weak_ctas)
        if is_weak:
            score -= 20
        
        # Length optimization
        word_count = len(cta.split())
        if word_count < 2:
            score -= 10
        elif word_count > 5:
            score -= 15
        
        cta_effectiveness_score = max(0, min(100, score))
        
        return {
            'cta_effectiveness_score': cta_effectiveness_score,
            'has_action_verb': has_action_verb,
            'has_urgency': has_urgency,
            'has_value_proposition': has_value,
            'is_weak_cta': is_weak,
            'word_count': word_count,
            'cta_analysis': self._generate_cta_analysis(has_action_verb, has_urgency, has_value, is_weak)
        }
    
    def _identify_emotional_triggers(self, text: str) -> Dict[str, Any]:
        """Identify and score emotional triggers in the copy"""
        text_lower = text.lower()
        
        trigger_scores = {}
        total_triggers = 0
        
        for trigger_type, trigger_words in self.emotional_triggers.items():
            found_words = [word for word in trigger_words if word in text_lower]
            trigger_count = len(found_words)
            trigger_scores[trigger_type] = {
                'count': trigger_count,
                'words_found': found_words,
                'score': min(100, trigger_count * 25)
            }
            total_triggers += trigger_count
        
        # Calculate overall emotional impact
        emotional_impact_score = min(100, total_triggers * 12)
        
        # Identify dominant emotional approach
        dominant_trigger = max(trigger_scores, key=lambda k: trigger_scores[k]['count'])
        
        return {
            'emotional_impact_score': emotional_impact_score,
            'total_triggers_found': total_triggers,
            'trigger_breakdown': trigger_scores,
            'dominant_emotional_approach': dominant_trigger,
            'emotional_balance': self._analyze_emotional_balance(trigger_scores)
        }
    
    def _analyze_platform_fit(self, input_data: ToolInput, full_text: str) -> Dict[str, Any]:
        """Analyze how well the copy fits the target platform"""
        platform = input_data.platform.lower()
        guidelines = self.platform_guidelines.get(platform, self.platform_guidelines['facebook'])
        
        score = 75  # Base score
        
        # Headline length check
        headline_words = len(input_data.headline.split())
        if isinstance(guidelines['headline_ideal'], tuple):
            min_words, max_words = guidelines['headline_ideal']
            if min_words <= headline_words <= max_words:
                score += 10
            elif headline_words < min_words or headline_words > max_words:
                score -= 10
        
        # Body text length check
        body_chars = len(input_data.body_text)
        if isinstance(guidelines['body_ideal'], tuple):
            min_chars, max_chars = guidelines['body_ideal']
            if min_chars <= body_chars <= max_chars:
                score += 10
            elif body_chars > max_chars:
                score -= 15
        
        # CTA length check
        cta_words = len(input_data.cta.split())
        if isinstance(guidelines['cta_ideal'], tuple):
            min_cta, max_cta = guidelines['cta_ideal']
            if min_cta <= cta_words <= max_cta:
                score += 5
        
        # Platform-specific tone analysis
        tone_score = self._analyze_tone_for_platform(full_text, guidelines['tone'])
        score += tone_score
        
        platform_fit_score = max(0, min(100, score))
        
        return {
            'platform_fit_score': platform_fit_score,
            'platform': platform,
            'platform_guidelines': guidelines,
            'optimization_suggestions': self._generate_platform_suggestions(
                input_data, guidelines, platform
            )
        }
    
    def _analyze_tone_for_platform(self, text: str, expected_tone: str) -> int:
        """Analyze if the tone matches platform expectations"""
        text_lower = text.lower()
        
        tone_indicators = {
            'conversational': ['you', 'your', 'we', 'us', 'our', 'hey', 'hi'],
            'professional': ['company', 'business', 'solution', 'service', 'professional'],
            'direct': ['get', 'now', 'today', 'start', 'buy'],
            'casual': ['awesome', 'cool', 'hey', 'super', 'totally'],
            'visual': ['see', 'look', 'watch', 'view', 'image']
        }
        
        indicators = tone_indicators.get(expected_tone, [])
        found_indicators = sum(1 for indicator in indicators if indicator in text_lower)
        
        return min(10, found_indicators * 2)
    
    def _calculate_overall_score(self, clarity: float, sentiment: float, hook: float, 
                                cta: float, emotion: float, platform: float) -> float:
        """Calculate weighted overall score"""
        weights = {
            'clarity': 0.15,
            'sentiment': 0.10,
            'hook': 0.25,      # Hook is very important
            'cta': 0.25,       # CTA is very important
            'emotion': 0.15,
            'platform': 0.10
        }
        
        overall = (
            clarity * weights['clarity'] +
            sentiment * weights['sentiment'] +
            hook * weights['hook'] +
            cta * weights['cta'] +
            emotion * weights['emotion'] +
            platform * weights['platform']
        )
        
        return round(overall, 1)
    
    def _generate_recommendations(self, readability: Dict, sentiment: Dict, hook: Dict,
                                 cta: Dict, emotions: Dict, platform: Dict) -> List[str]:
        """Generate specific improvement recommendations"""
        recommendations = []
        
        # Readability recommendations
        if readability['clarity_score'] < 60:
            recommendations.append("Simplify language and use shorter sentences for better readability")
        
        # Hook recommendations
        if hook['hook_strength_score'] < 70:
            recommendations.append("Strengthen your headline hook with a question, number, or curiosity gap")
        
        # CTA recommendations
        if cta['cta_effectiveness_score'] < 70:
            if not cta.get('has_action_verb', False):
                recommendations.append("Use a strong action verb in your CTA (get, start, claim, unlock)")
            if not cta.get('has_urgency', False):
                recommendations.append("Add urgency to your CTA with words like 'now' or 'today'")
        
        # Emotional trigger recommendations
        if emotions['emotional_impact_score'] < 60:
            recommendations.append("Incorporate more emotional triggers like scarcity, social proof, or urgency")
        
        # Platform optimization
        if platform['platform_fit_score'] < 80:
            recommendations.extend(platform.get('optimization_suggestions', []))
        
        # Sentiment recommendations
        if sentiment['overall_sentiment_score'] < 70:
            recommendations.append("Increase positive language and emotional appeal")
        
        return recommendations[:8]  # Limit to top 8 recommendations
    
    def _generate_hook_analysis(self, patterns: List[str], power_words: List[str], weak_words: List[str]) -> str:
        """Generate hook analysis summary"""
        if not patterns and not power_words:
            return "Hook lacks strong opening patterns and power words"
        
        analysis = []
        if patterns:
            analysis.append(f"Uses {', '.join(patterns)} pattern(s)")
        if power_words:
            analysis.append(f"Contains power words: {', '.join(power_words)}")
        if weak_words:
            analysis.append(f"Warning: weak words detected: {', '.join(weak_words)}")
        
        return "; ".join(analysis)
    
    def _generate_cta_analysis(self, has_action: bool, has_urgency: bool, 
                              has_value: bool, is_weak: bool) -> str:
        """Generate CTA analysis summary"""
        strengths = []
        weaknesses = []
        
        if has_action:
            strengths.append("strong action verb")
        else:
            weaknesses.append("missing action verb")
        
        if has_urgency:
            strengths.append("urgency indicator")
        else:
            weaknesses.append("no urgency")
        
        if has_value:
            strengths.append("value proposition")
        
        if is_weak:
            weaknesses.append("uses weak CTA phrase")
        
        analysis_parts = []
        if strengths:
            analysis_parts.append(f"Strengths: {', '.join(strengths)}")
        if weaknesses:
            analysis_parts.append(f"Areas for improvement: {', '.join(weaknesses)}")
        
        return "; ".join(analysis_parts)
    
    def _analyze_emotional_balance(self, trigger_scores: Dict) -> Dict[str, Any]:
        """Analyze the balance of emotional approaches"""
        total_score = sum(scores['score'] for scores in trigger_scores.values())
        
        if total_score == 0:
            return {'balance': 'none', 'recommendation': 'Add emotional triggers'}
        
        # Calculate emotional approach distribution
        emotional_distribution = {}
        for trigger, data in trigger_scores.items():
            if data['score'] > 0:
                emotional_distribution[trigger] = round(data['score'] / total_score * 100, 1)
        
        # Determine balance quality
        if len(emotional_distribution) == 1:
            balance = 'single_focus'
        elif len(emotional_distribution) <= 3:
            balance = 'balanced'
        else:
            balance = 'scattered'
        
        return {
            'balance': balance,
            'distribution': emotional_distribution,
            'recommendation': self._get_balance_recommendation(balance)
        }
    
    def _get_balance_recommendation(self, balance: str) -> str:
        """Get recommendation based on emotional balance"""
        recommendations = {
            'none': 'Add emotional triggers to increase engagement',
            'single_focus': 'Consider adding complementary emotional triggers',
            'balanced': 'Good emotional balance maintained',
            'scattered': 'Focus on 2-3 main emotional approaches for clarity'
        }
        return recommendations.get(balance, 'Review emotional strategy')
    
    def _generate_platform_suggestions(self, input_data: ToolInput, 
                                     guidelines: Dict, platform: str) -> List[str]:
        """Generate platform-specific optimization suggestions"""
        suggestions = []
        
        # Headline length suggestions
        headline_words = len(input_data.headline.split())
        min_words, max_words = guidelines['headline_ideal']
        
        if headline_words < min_words:
            suggestions.append(f"Expand headline to {min_words}-{max_words} words for {platform}")
        elif headline_words > max_words:
            suggestions.append(f"Shorten headline to {min_words}-{max_words} words for {platform}")
        
        # Body text suggestions
        body_chars = len(input_data.body_text)
        min_chars, max_chars = guidelines['body_ideal']
        
        if body_chars > max_chars:
            suggestions.append(f"Reduce body text to under {max_chars} characters for {platform}")
        elif body_chars < min_chars:
            suggestions.append(f"Expand body text to {min_chars}-{max_chars} characters for {platform}")
        
        # Platform-specific tips
        platform_tips = {
            'facebook': ["Use conversational tone", "Consider emoji usage", "Focus on engagement"],
            'google': ["Be direct and specific", "Include clear value prop", "Optimize for search intent"],
            'linkedin': ["Use professional language", "Focus on business outcomes", "Include industry context"],
            'tiktok': ["Keep it short and punchy", "Use trending language", "Create urgency"],
            'instagram': ["Make it visual-friendly", "Use storytelling", "Include hashtag strategy"]
        }
        
        suggestions.extend(platform_tips.get(platform, []))
        
        return suggestions[:5]  # Limit suggestions
    
    def _calculate_confidence(self, insights: Dict[str, Any]) -> float:
        """Calculate confidence score based on analysis quality"""
        confidence_factors = []
        
        # Text length factor
        word_count = insights['text_metrics']['word_count']
        if word_count >= 10:
            confidence_factors.append(95)
        elif word_count >= 5:
            confidence_factors.append(80)
        else:
            confidence_factors.append(60)
        
        # Analysis completeness factor
        if insights.get('sentiment_analysis', {}).get('sentiment_confidence', 0) > 0.8:
            confidence_factors.append(90)
        else:
            confidence_factors.append(75)
        
        # Platform guidelines factor
        if insights.get('platform_optimization', {}).get('platform') in self.platform_guidelines:
            confidence_factors.append(85)
        else:
            confidence_factors.append(70)
        
        return sum(confidence_factors) / len(confidence_factors)
    
    def validate_input(self, input_data: ToolInput) -> bool:
        """Validate input data for ad copy analysis"""
        missing_fields = []
        
        if not input_data.headline.strip():
            missing_fields.append('headline')
        if not input_data.body_text.strip():
            missing_fields.append('body_text')
        if not input_data.cta.strip():
            missing_fields.append('cta')
        if not input_data.platform.strip():
            missing_fields.append('platform')
        
        if missing_fields:
            raise ToolValidationError(
                self.name,
                f"Missing required fields for comprehensive analysis: {missing_fields}",
                missing_fields
            )
        
        return True
    
    def get_output_scores(self) -> List[str]:
        """Get list of scores this tool outputs"""
        return [
            'overall_score', 'clarity_score', 'sentiment_score',
            'hook_strength_score', 'cta_effectiveness_score',
            'emotional_impact_score', 'platform_fit_score'
        ]
    
    @classmethod
    def default_config(cls) -> ToolConfig:
        """Get default configuration for this tool"""
        return ToolConfig(
            name="ad_copy_analyzer",
            tool_type=ToolType.ANALYZER,
            timeout=30.0,
            parameters={
                'min_text_length': 10,
                'max_recommendations': 8,
                'sentiment_threshold': 0.7
            }
        )