import re
from typing import Dict, Any, List

class CTAAnalyzer:
    """Analyzes Call-to-Action strength and effectiveness"""
    
    def __init__(self):
        # Strong CTA patterns and words
        self.strong_cta_words = [
            'get', 'start', 'try', 'download', 'claim', 'grab', 'discover',
            'unlock', 'access', 'join', 'register', 'subscribe', 'buy',
            'order', 'book', 'schedule', 'request', 'apply', 'upgrade'
        ]
        
        self.weak_cta_words = [
            'learn', 'read', 'see', 'view', 'check', 'browse', 'explore',
            'find', 'search', 'look', 'click', 'visit'
        ]
        
        self.urgency_words = [
            'now', 'today', 'immediately', 'instantly', 'quick', 'fast',
            'limited', 'expires', 'deadline', 'hurry', 'soon', 'while'
        ]
        
        # Platform-specific CTA best practices
        self.platform_cta_guidelines = {
            'facebook': {
                'ideal_length': (2, 4),  # words
                'preferred_style': 'action_oriented',
                'avoid': ['click here', 'learn more']
            },
            'google': {
                'ideal_length': (2, 3),
                'preferred_style': 'benefit_focused',
                'avoid': ['submit', 'send']
            },
            'linkedin': {
                'ideal_length': (2, 5),
                'preferred_style': 'professional',
                'avoid': ['buy now', 'limited time']
            },
            'tiktok': {
                'ideal_length': (1, 3),
                'preferred_style': 'casual_urgent',
                'avoid': ['learn more', 'find out']
            }
        }
    
    def analyze_cta(self, cta: str, platform: str = 'facebook') -> Dict[str, Any]:
        """Analyze CTA strength and effectiveness"""
        cta_clean = cta.strip().lower()
        words = cta_clean.split()
        
        # Basic analysis
        word_count = len(words)
        has_action_verb = any(word in cta_clean for word in self.strong_cta_words)
        has_weak_words = any(word in cta_clean for word in self.weak_cta_words)
        has_urgency = any(word in cta_clean for word in self.urgency_words)
        
        # Platform-specific analysis
        platform_analysis = self._analyze_platform_fit(cta_clean, platform)
        
        # Calculate CTA strength score
        strength_score = self._calculate_cta_strength(
            has_action_verb, has_weak_words, has_urgency, 
            word_count, platform_analysis
        )
        
        # Generate recommendations
        recommendations = self._get_cta_recommendations(
            cta_clean, has_action_verb, has_weak_words, 
            has_urgency, platform, platform_analysis
        )
        
        return {
            'cta_strength_score': strength_score,
            'word_count': word_count,
            'has_action_verb': has_action_verb,
            'has_urgency': has_urgency,
            'platform_fit': platform_analysis['fit_score'],
            'recommendations': recommendations,
            'suggested_improvements': self._suggest_cta_improvements(cta, platform)
        }
    
    def _analyze_platform_fit(self, cta: str, platform: str) -> Dict[str, Any]:
        """Analyze how well CTA fits platform guidelines"""
        guidelines = self.platform_cta_guidelines.get(platform, self.platform_cta_guidelines['facebook'])
        words = cta.split()
        
        # Length fit
        min_words, max_words = guidelines['ideal_length']
        length_fit = 100 if min_words <= len(words) <= max_words else 70
        
        # Avoid words check
        has_avoid_words = any(avoid_word in cta for avoid_word in guidelines['avoid'])
        avoid_penalty = -20 if has_avoid_words else 0
        
        fit_score = length_fit + avoid_penalty
        fit_score = max(0, min(100, fit_score))
        
        return {
            'fit_score': fit_score,
            'length_appropriate': min_words <= len(words) <= max_words,
            'has_avoid_words': has_avoid_words,
            'style_match': guidelines['preferred_style']
        }
    
    def _calculate_cta_strength(self, has_action_verb: bool, has_weak_words: bool, 
                               has_urgency: bool, word_count: int, platform_analysis: Dict) -> float:
        """Calculate overall CTA strength score"""
        base_score = 50
        
        # Action verb bonus
        if has_action_verb:
            base_score += 25
        
        # Weak words penalty
        if has_weak_words:
            base_score -= 15
        
        # Urgency bonus
        if has_urgency:
            base_score += 15
        
        # Length penalty/bonus
        if 1 <= word_count <= 4:
            base_score += 10
        elif word_count > 6:
            base_score -= 10
        
        # Platform fit bonus
        base_score += platform_analysis['fit_score'] * 0.2
        
        return max(0, min(100, base_score))
    
    def _get_cta_recommendations(self, cta: str, has_action_verb: bool, 
                                has_weak_words: bool, has_urgency: bool, 
                                platform: str, platform_analysis: Dict) -> List[str]:
        """Generate CTA improvement recommendations"""
        recommendations = []
        
        if not has_action_verb:
            recommendations.append("Use a strong action verb like 'Get', 'Start', 'Try', or 'Claim'")
        
        if has_weak_words:
            recommendations.append("Replace weak words like 'learn more' with stronger action words")
        
        if not has_urgency:
            recommendations.append("Add urgency with words like 'now', 'today', or 'limited time'")
        
        if len(cta.split()) > 5:
            recommendations.append("Shorten your CTA to 2-4 words for better impact")
        
        if platform_analysis['has_avoid_words']:
            recommendations.append(f"Avoid generic phrases for {platform} - use platform-specific best practices")
        
        return recommendations
    
    def _suggest_cta_improvements(self, original_cta: str, platform: str) -> List[str]:
        """Suggest specific CTA improvements"""
        suggestions = []
        
        if platform == 'facebook':
            suggestions = [
                "Get Started Free",
                "Claim Your Spot",
                "Try Risk-Free",
                "Start Today"
            ]
        elif platform == 'google':
            suggestions = [
                "Get Quote Now",
                "Start Free Trial",
                "Request Demo",
                "Buy Now"
            ]
        elif platform == 'linkedin':
            suggestions = [
                "Request Consultation",
                "Download Guide",
                "Schedule Demo",
                "Contact Sales"
            ]
        elif platform == 'tiktok':
            suggestions = [
                "Try Now",
                "Get It",
                "Start Free",
                "Go!"
            ]
        
        return suggestions[:3]  # Return top 3 suggestions
