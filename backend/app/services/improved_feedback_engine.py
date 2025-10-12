#!/usr/bin/env python3
"""
Improved Feedback Engine for AdCopySurge
Replaces generic feedback with specific, actionable advice based on psychology principles.
"""

from typing import Dict, List, Any, Tuple
import re
from dataclasses import dataclass


@dataclass
class FeedbackSuggestion:
    """Structured suggestion with psychology reasoning."""
    category: str
    suggestion: str
    psychology_principle: str
    priority: str  # "high", "medium", "low"
    example: str = ""


class ImprovedFeedbackGenerator:
    """
    Generates specific, actionable feedback based on score analysis.
    Each suggestion includes psychology principles and concrete examples.
    """
    
    def __init__(self):
        self.psychology_principles = self._load_psychology_principles()
        self.improvement_templates = self._load_improvement_templates()
        
    def _load_psychology_principles(self) -> Dict[str, str]:
        """Load psychology principles for explanations."""
        return {
            "social_proof": "People follow others' actions, especially similar peers",
            "scarcity": "Limited availability increases perceived value",
            "urgency": "Time pressure motivates immediate action",
            "authority": "Expert endorsement builds trust and credibility",
            "reciprocity": "People feel obligated to return favors",
            "loss_aversion": "Fear of missing out is stronger than desire to gain",
            "anchoring": "First number sets reference point for all comparisons",
            "cognitive_ease": "Simple, clear messaging is more persuasive",
            "emotional_contagion": "Emotions spread from copy to reader",
            "specificity_bias": "Precise details are more believable than round numbers"
        }
    
    def _load_improvement_templates(self) -> Dict[str, List[Dict[str, str]]]:
        """Load templates for improvement suggestions by category."""
        return {
            "clarity": [
                {
                    "condition": "long_sentences",
                    "suggestion": "Break sentences under 20 words for better readability",
                    "psychology": "cognitive_ease",
                    "example": "Instead of: 'Our comprehensive solution provides...' Try: 'Get more leads. Convert more sales. Grow faster.'"
                },
                {
                    "condition": "complex_words",
                    "suggestion": "Use simpler words your audience uses in conversation",
                    "psychology": "cognitive_ease", 
                    "example": "Replace 'utilize' with 'use', 'facilitate' with 'help'"
                },
                {
                    "condition": "unclear_benefit",
                    "suggestion": "Lead with the specific outcome customers will get",
                    "psychology": "anchoring",
                    "example": "'Save 3 hours daily on reporting' vs 'Streamline your workflow'"
                }
            ],
            "emotion": [
                {
                    "condition": "low_emotional_words",
                    "suggestion": "Add power words that trigger emotion",
                    "psychology": "emotional_contagion",
                    "example": "Add words like 'transform', 'breakthrough', 'exclusive', 'guaranteed'"
                },
                {
                    "condition": "no_customer_story",
                    "suggestion": "Include a relatable customer scenario or outcome",
                    "psychology": "social_proof",
                    "example": "'Sarah increased her team's productivity by 40% in just 2 weeks'"
                },
                {
                    "condition": "missing_pain_point",
                    "suggestion": "Acknowledge the frustration your audience feels",
                    "psychology": "loss_aversion",
                    "example": "'Tired of losing leads because your website is too slow?'"
                }
            ],
            "cta": [
                {
                    "condition": "weak_action_verb",
                    "suggestion": "Use stronger action verbs that create momentum",
                    "psychology": "urgency",
                    "example": "Replace 'Learn More' with 'Get Your Results Now' or 'Start Growing Today'"
                },
                {
                    "condition": "no_value_preview",
                    "suggestion": "Hint at what happens after they click",
                    "psychology": "reciprocity", 
                    "example": "'Get Your Free Analysis' vs 'Click Here'"
                },
                {
                    "condition": "missing_urgency",
                    "suggestion": "Add time-sensitive language to encourage action",
                    "psychology": "scarcity",
                    "example": "'Start Your Free Trial Today' or 'Join 1000+ Companies This Month'"
                }
            ],
            "platform_fit": [
                {
                    "condition": "wrong_length",
                    "suggestion": "Adjust copy length for platform's attention span",
                    "psychology": "cognitive_ease",
                    "example": "Facebook: 125 chars max, Google: 30 char headlines"
                },
                {
                    "condition": "wrong_tone",
                    "suggestion": "Match the platform's conversational style",
                    "psychology": "social_proof", 
                    "example": "LinkedIn: professional, Facebook: casual, TikTok: fun"
                }
            ],
            "persuasion": [
                {
                    "condition": "no_credibility_markers",
                    "suggestion": "Add credibility indicators to build trust",
                    "psychology": "authority",
                    "example": "'Used by 10,000+ companies', 'Featured in Forbes', '99% satisfaction rate'"
                },
                {
                    "condition": "vague_benefits",
                    "suggestion": "Quantify your benefits with specific numbers",
                    "psychology": "specificity_bias", 
                    "example": "'Increase conversions by 23%' vs 'Improve your results'"
                },
                {
                    "condition": "missing_social_proof",
                    "suggestion": "Show others are already succeeding",
                    "psychology": "social_proof",
                    "example": "'Join 50,000 marketers who already...' or include testimonial quote"
                }
            ]
        }
    
    def generate_improved_feedback(self, 
                                 scores: Dict[str, float], 
                                 full_text: str,
                                 platform: str = "facebook") -> Dict[str, Any]:
        """
        Generate comprehensive, actionable feedback with psychology principles.
        
        Returns:
        - summary: Overall assessment
        - suggestions: List of specific improvements
        - quick_wins: Top 3 highest-impact changes  
        - psychology_insights: Explanations of why changes work
        """
        
        suggestions = []
        
        # Analyze each category
        if scores.get('clarity_score', 0) < 70:
            suggestions.extend(self._analyze_clarity_issues(full_text))
            
        if scores.get('emotion_score', 0) < 70:
            suggestions.extend(self._analyze_emotion_issues(full_text))
            
        if scores.get('cta_strength', 0) < 70:
            suggestions.extend(self._analyze_cta_issues(full_text))
            
        if scores.get('platform_fit_score', 0) < 75:
            suggestions.extend(self._analyze_platform_fit_issues(full_text, platform))
            
        if scores.get('persuasion_score', 0) < 70:
            suggestions.extend(self._analyze_persuasion_issues(full_text))
        
        # Generate summary
        overall_score = scores.get('overall_score', 0)
        summary = self._generate_summary(overall_score, len(suggestions))
        
        # Prioritize suggestions
        high_priority = [s for s in suggestions if s.priority == "high"]
        medium_priority = [s for s in suggestions if s.priority == "medium"]
        
        # Select top 3 quick wins
        quick_wins = (high_priority + medium_priority)[:3]
        
        return {
            "summary": summary,
            "suggestions": [
                {
                    "category": s.category,
                    "suggestion": s.suggestion,
                    "psychology_principle": s.psychology_principle,
                    "priority": s.priority,
                    "example": s.example
                } for s in suggestions
            ],
            "quick_wins": [s.suggestion for s in quick_wins],
            "psychology_insights": {
                s.psychology_principle: self.psychology_principles.get(s.psychology_principle, "")
                for s in suggestions
            },
            "improvement_count": len(suggestions)
        }
    
    def _analyze_clarity_issues(self, text: str) -> List[FeedbackSuggestion]:
        """Analyze clarity-specific issues and generate suggestions."""
        suggestions = []
        
        # Check sentence length
        sentences = [s.strip() for s in text.split('.') if s.strip()]
        long_sentences = [s for s in sentences if len(s.split()) > 20]
        
        if long_sentences:
            suggestions.append(FeedbackSuggestion(
                category="clarity",
                suggestion="Break long sentences into shorter, punchier statements",
                psychology_principle="cognitive_ease",
                priority="high",
                example="Instead of: 'Our comprehensive solution provides advanced analytics and reporting.' Try: 'Get advanced analytics. See clear reports. Make better decisions.'"
            ))
        
        # Check for jargon/complex words
        complex_words = ["utilize", "facilitate", "implement", "optimize", "leverage", "synergize"]
        found_complex = [word for word in complex_words if word.lower() in text.lower()]
        
        if found_complex:
            suggestions.append(FeedbackSuggestion(
                category="clarity", 
                suggestion=f"Replace complex words: {', '.join(found_complex[:3])}",
                psychology_principle="cognitive_ease",
                priority="medium",
                example="Use 'use' instead of 'utilize', 'help' instead of 'facilitate'"
            ))
        
        # Check if benefit is unclear
        benefit_words = ["save", "increase", "reduce", "improve", "boost", "grow"]
        has_clear_benefit = any(word in text.lower() for word in benefit_words)
        
        if not has_clear_benefit:
            suggestions.append(FeedbackSuggestion(
                category="clarity",
                suggestion="Start with a specific benefit your audience will receive",
                psychology_principle="anchoring", 
                priority="high",
                example="'Reduce customer support emails by 60%' vs 'Improve customer experience'"
            ))
        
        return suggestions
    
    def _analyze_emotion_issues(self, text: str) -> List[FeedbackSuggestion]:
        """Analyze emotional impact issues."""
        suggestions = []
        
        # Check for emotional power words
        emotion_words = [
            "amazing", "incredible", "exclusive", "breakthrough", "transform",
            "unleash", "powerful", "proven", "guaranteed", "secret", "insider"
        ]
        
        found_emotions = sum(1 for word in emotion_words if word.lower() in text.lower())
        
        if found_emotions < 2:
            suggestions.append(FeedbackSuggestion(
                category="emotion",
                suggestion="Add emotional trigger words to create stronger connection",
                psychology_principle="emotional_contagion",
                priority="high", 
                example="Try words like 'transform', 'breakthrough', 'exclusive', or 'guaranteed'"
            ))
        
        # Check for customer story/social proof
        story_indicators = ["customer", "client", "user", "Sarah", "John", "team", "company"]
        has_story = any(indicator in text.lower() for indicator in story_indicators)
        
        if not has_story:
            suggestions.append(FeedbackSuggestion(
                category="emotion",
                suggestion="Include a brief customer success story or relatable scenario",
                psychology_principle="social_proof",
                priority="medium",
                example="'Like Sarah's team, you can reduce project delays by 50%'"
            ))
        
        # Check for pain point acknowledgment
        pain_words = ["frustrated", "tired", "struggling", "difficult", "problem", "challenge"]
        acknowledges_pain = any(word in text.lower() for word in pain_words)
        
        if not acknowledges_pain:
            suggestions.append(FeedbackSuggestion(
                category="emotion",
                suggestion="Acknowledge a specific frustration your audience faces",
                psychology_principle="loss_aversion",
                priority="medium", 
                example="'Tired of losing leads to slow website loading times?'"
            ))
        
        return suggestions
    
    def _analyze_cta_issues(self, text: str) -> List[FeedbackSuggestion]:
        """Analyze call-to-action strength issues.""" 
        suggestions = []
        
        # Extract likely CTA (usually at the end or has action words)
        cta_pattern = r'(get|start|try|join|download|sign up|book|schedule|claim|grab)[^.!?]*[.!?]?'
        cta_matches = re.findall(cta_pattern, text, re.IGNORECASE)
        
        # Check for weak CTAs
        weak_ctas = ["learn more", "find out more", "click here", "read more", "see more"]
        has_weak_cta = any(weak in text.lower() for weak in weak_ctas)
        
        if has_weak_cta or not cta_matches:
            suggestions.append(FeedbackSuggestion(
                category="cta",
                suggestion="Replace weak CTAs with specific action verbs",
                psychology_principle="urgency",
                priority="high",
                example="Replace 'Learn More' with 'Get Your Free Analysis' or 'Start Growing Today'"
            ))
        
        # Check for value preview in CTA
        value_words = ["free", "instant", "results", "trial", "demo", "consultation"] 
        cta_has_value = any(word in text.lower() for word in value_words)
        
        if not cta_has_value:
            suggestions.append(FeedbackSuggestion(
                category="cta",
                suggestion="Preview the value users get when they click",
                psychology_principle="reciprocity",
                priority="medium",
                example="'Get Your Free Marketing Audit' vs 'Contact Us'"
            ))
        
        # Check for urgency/scarcity
        urgency_words = ["now", "today", "limited", "deadline", "expires", "while", "before"]
        has_urgency = any(word in text.lower() for word in urgency_words)
        
        if not has_urgency:
            suggestions.append(FeedbackSuggestion(
                category="cta", 
                suggestion="Add time-sensitive language to encourage immediate action",
                psychology_principle="scarcity",
                priority="medium",
                example="'Start Your Free Trial Today' or 'Join This Month's Cohort'"
            ))
        
        return suggestions
    
    def _analyze_platform_fit_issues(self, text: str, platform: str) -> List[FeedbackSuggestion]:
        """Analyze platform-specific optimization issues."""
        suggestions = []
        
        platform_specs = {
            "facebook": {"max_chars": 125, "tone": "casual", "ideal_headline_words": (3, 6)},
            "google": {"max_chars": 90, "tone": "direct", "ideal_headline_chars": (25, 30)}, 
            "linkedin": {"max_chars": 150, "tone": "professional", "ideal_headline_words": (5, 10)},
            "tiktok": {"max_chars": 80, "tone": "fun", "ideal_headline_words": (2, 4)}
        }
        
        specs = platform_specs.get(platform, platform_specs["facebook"])
        
        # Check text length
        if len(text) > specs["max_chars"]:
            suggestions.append(FeedbackSuggestion(
                category="platform_fit",
                suggestion=f"Shorten copy to {specs['max_chars']} characters for {platform}",
                psychology_principle="cognitive_ease",
                priority="high",
                example=f"{platform.title()} users scan quickly - keep it concise and impactful"
            ))
        
        # Check tone appropriateness  
        tone_words = {
            "casual": ["hey", "awesome", "cool", "amazing", "love"],
            "professional": ["solution", "professional", "expertise", "results", "optimize"],
            "direct": ["get", "save", "increase", "now", "fast"],
            "fun": ["wow", "epic", "crazy", "insane", "fire"]
        }
        
        expected_tone = specs["tone"]
        tone_matches = sum(1 for word in tone_words[expected_tone] if word in text.lower())
        
        if tone_matches == 0:
            suggestions.append(FeedbackSuggestion(
                category="platform_fit",
                suggestion=f"Adjust tone to be more {expected_tone} for {platform}",
                psychology_principle="social_proof",
                priority="medium", 
                example=f"{platform.title()} users expect {expected_tone} communication style"
            ))
        
        return suggestions
    
    def _analyze_persuasion_issues(self, text: str) -> List[FeedbackSuggestion]:
        """Analyze persuasion and credibility issues."""
        suggestions = []
        
        # Check for numbers/statistics
        number_pattern = r'\b\d+[%$]?|\d+[kK]|\d+\+|\d+x\b'
        numbers = re.findall(number_pattern, text)
        
        if len(numbers) < 1:
            suggestions.append(FeedbackSuggestion(
                category="persuasion",
                suggestion="Add specific numbers to quantify your benefits",
                psychology_principle="specificity_bias", 
                priority="high",
                example="'Increase conversions by 23%' vs 'Improve performance'"
            ))
        
        # Check for credibility markers
        credibility_words = ["trusted", "proven", "verified", "certified", "award", "featured"]
        social_numbers = ["thousand", "million", "users", "customers", "companies"]
        
        has_credibility = any(word in text.lower() for word in credibility_words + social_numbers)
        
        if not has_credibility:
            suggestions.append(FeedbackSuggestion(
                category="persuasion",
                suggestion="Add credibility indicators to build trust",
                psychology_principle="authority",
                priority="medium",
                example="'Trusted by 10,000+ companies' or 'Featured in TechCrunch'"
            ))
        
        # Check for social proof
        social_proof_words = ["customers", "users", "companies", "teams", "people", "join"]
        has_social_proof = any(word in text.lower() for word in social_proof_words)
        
        if not has_social_proof:
            suggestions.append(FeedbackSuggestion(
                category="persuasion",
                suggestion="Show that others are already benefiting from your solution",
                psychology_principle="social_proof",
                priority="medium",
                example="'Join 5,000+ marketers who increased ROI by 40%'"
            ))
        
        return suggestions
    
    def _generate_summary(self, overall_score: float, issue_count: int) -> str:
        """Generate overall feedback summary."""
        if overall_score >= 85:
            return f"🎯 Excellent ad copy! Minor tweaks could push this to perfection."
        elif overall_score >= 70:
            return f"✅ Solid foundation with {issue_count} optimization opportunities identified."
        elif overall_score >= 55:
            return f"⚠️ Good potential but needs work. Focus on the {min(3, issue_count)} highest-priority improvements first."
        else:
            return f"❌ Significant improvements needed. Start with clarity and emotional impact - the foundation for all great ads."


# Integration helper function
def generate_actionable_feedback(scores: Dict[str, float], 
                               full_text: str, 
                               platform: str = "facebook") -> Dict[str, Any]:
    """
    Main function to generate improved feedback.
    Use this to replace the existing generic feedback system.
    """
    generator = ImprovedFeedbackGenerator()
    return generator.generate_improved_feedback(scores, full_text, platform)