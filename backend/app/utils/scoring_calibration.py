#!/usr/bin/env python3
"""
Enhanced scoring calibration system for AdCopySurge
Implements stricter baseline scoring to make 90%+ scores rare and meaningful.
"""

import re
import yaml
from typing import Dict, List, Any
from pathlib import Path


class BaselineScoreCalibrator:
    """Enhanced scoring system with stricter baselines and penalty systems."""
    
    def __init__(self):
        """Initialize with penalty phrases and scoring thresholds."""
        self.penalty_phrases = self._load_penalty_phrases()
        self.baseline_score = 50.0  # Start from median instead of high baseline
        
    def _load_penalty_phrases(self) -> Dict[str, List[str]]:
        """Load overused phrases and clichés that should be penalized."""
        penalty_data = {
            "generic_phrases": [
                "best in class", "world class", "industry leading", "cutting edge",
                "state of the art", "revolutionary", "game changing", "next level",
                "take your business to the next level", "unlock your potential",
                "transform your life", "change everything", "amazing results",
                "incredible opportunity", "unbelievable savings", "limited time only",
                "act now", "don't wait", "while supplies last", "one time offer"
            ],
            "vague_claims": [
                "guaranteed results", "instant success", "effortless", "foolproof",
                "secret formula", "hidden technique", "insider knowledge",
                "proven system", "tested method", "works every time"
            ],
            "overused_ctas": [
                "click here", "learn more", "find out more", "read more",
                "discover more", "see more", "get info", "more info"
            ],
            "weak_modifiers": [
                "very good", "really great", "pretty amazing", "quite nice",
                "fairly decent", "somewhat better", "kind of special"
            ]
        }
        return penalty_data
        
    def calculate_calibrated_score(self, 
                                 clarity_score: float,
                                 persuasion_score: float, 
                                 emotion_score: float,
                                 cta_score: float,
                                 platform_fit_score: float,
                                 full_text: str) -> Dict[str, Any]:
        """
        Calculate calibrated overall score with stricter baseline.
        Target: 40-60% for typical ads, 90%+ reserved for truly exceptional content.
        """
        
        # Apply penalties for overused phrases
        penalty_details = self._calculate_penalties(full_text)
        total_penalty = penalty_details['total_penalty']
        
        # Stricter weighting system
        weights = {
            'clarity': 0.20,
            'persuasion': 0.30,  # Higher weight for persuasion
            'emotion': 0.25,     # Higher weight for emotion  
            'cta': 0.20,
            'platform_fit': 0.05  # Lower weight for platform fit
        }
        
        # Calculate base weighted score
        weighted_score = (
            clarity_score * weights['clarity'] +
            persuasion_score * weights['persuasion'] +
            emotion_score * weights['emotion'] +
            cta_score * weights['cta'] +
            platform_fit_score * weights['platform_fit']
        )
        
        # Apply calibration curve (makes scores more realistic)
        calibrated_score = self._apply_calibration_curve(weighted_score)
        
        # Apply penalties
        final_score = max(10.0, calibrated_score - total_penalty)
        
        # Apply excellence bonus for truly exceptional content
        excellence_bonus = self._calculate_excellence_bonus(full_text, final_score)
        final_score = min(100.0, final_score + excellence_bonus)
        
        return {
            'overall_score': round(final_score, 1),
            'calibrated_base': round(calibrated_score, 1),
            'penalties_applied': penalty_details,
            'excellence_bonus': excellence_bonus,
            'score_breakdown': {
                'clarity': clarity_score,
                'persuasion': persuasion_score,
                'emotion': emotion_score,
                'cta': cta_score,
                'platform_fit': platform_fit_score
            }
        }
    
    def _apply_calibration_curve(self, raw_score: float) -> float:
        """
        Apply calibration curve to make scores more realistic.
        Maps 0-100 input to a curve where:
        - 50-70 input → 40-60 output (typical range)
        - 80+ input → 70+ output (good ads)
        - 90+ input → 85+ output (excellent ads)
        """
        if raw_score <= 30:
            return raw_score * 0.8  # Very poor ads: 0-24
        elif raw_score <= 50:
            return 24 + (raw_score - 30) * 0.9  # Poor ads: 24-42
        elif raw_score <= 70:
            return 42 + (raw_score - 50) * 0.9  # Typical ads: 42-60
        elif raw_score <= 85:
            return 60 + (raw_score - 70) * 1.0  # Good ads: 60-75
        else:
            return 75 + (raw_score - 85) * 1.5  # Excellent ads: 75-97.5
    
    def _calculate_penalties(self, full_text: str) -> Dict[str, Any]:
        """Calculate penalties for overused phrases and weak copy."""
        penalties = {}
        total_penalty = 0.0
        
        text_lower = full_text.lower()
        
        for category, phrases in self.penalty_phrases.items():
            category_penalty = 0.0
            found_phrases = []
            
            for phrase in phrases:
                if phrase.lower() in text_lower:
                    found_phrases.append(phrase)
                    # Different penalty weights by category
                    if category == "generic_phrases":
                        category_penalty += 8.0  # Heavy penalty
                    elif category == "vague_claims":
                        category_penalty += 6.0
                    elif category == "overused_ctas":
                        category_penalty += 4.0
                    elif category == "weak_modifiers":
                        category_penalty += 3.0
            
            if found_phrases:
                penalties[category] = {
                    'phrases': found_phrases,
                    'penalty': category_penalty
                }
                total_penalty += category_penalty
        
        # Additional penalties
        # Excessive exclamation marks
        exclamation_count = text_lower.count('!')
        if exclamation_count > 2:
            exclamation_penalty = (exclamation_count - 2) * 2.0
            total_penalty += exclamation_penalty
            penalties['excessive_exclamations'] = {
                'count': exclamation_count,
                'penalty': exclamation_penalty
            }
        
        # All caps penalty
        caps_words = len([word for word in full_text.split() if word.isupper() and len(word) > 2])
        if caps_words > 0:
            caps_penalty = caps_words * 3.0
            total_penalty += caps_penalty
            penalties['excessive_caps'] = {
                'count': caps_words, 
                'penalty': caps_penalty
            }
        
        return {
            'total_penalty': min(40.0, total_penalty),  # Cap penalties at 40 points
            'categories': penalties
        }
    
    def _calculate_excellence_bonus(self, full_text: str, current_score: float) -> float:
        """Calculate bonus for truly exceptional content elements."""
        if current_score < 70:  # Only apply to already good content
            return 0.0
            
        bonus = 0.0
        text_lower = full_text.lower()
        
        # Excellence indicators
        excellence_phrases = [
            "specific number", "proven track record", "case study",
            "measurable results", "roi", "conversion rate", "data-driven",
            "testimonial", "before and after", "guarantee", "risk-free"
        ]
        
        # Bonus for specific numbers (not just vague claims)
        number_pattern = r'\b\d+%|\$\d+|\d+x|\d+\+\b'
        specific_numbers = len(re.findall(number_pattern, full_text))
        if specific_numbers > 0:
            bonus += specific_numbers * 2.0
        
        # Bonus for social proof elements
        social_proof_keywords = ["customers", "clients", "users", "reviews", "rated"]
        social_proof_count = sum(1 for word in social_proof_keywords if word in text_lower)
        if social_proof_count > 0:
            bonus += social_proof_count * 1.5
        
        # Bonus for clear value proposition
        value_keywords = ["save", "increase", "reduce", "improve", "boost", "optimize"]
        value_count = sum(1 for word in value_keywords if word in text_lower)
        if value_count >= 2:  # Multiple value indicators
            bonus += 3.0
        
        return min(15.0, bonus)  # Cap excellence bonus at 15 points

    def generate_score_explanation(self, score_data: Dict[str, Any]) -> str:
        """Generate human-readable explanation of the scoring."""
        overall = score_data['overall_score']
        penalties = score_data['penalties_applied']
        
        explanation = []
        
        # Overall assessment
        if overall >= 85:
            explanation.append("🎯 Excellent ad copy! This content demonstrates strong persuasion and clarity.")
        elif overall >= 70:
            explanation.append("✅ Good ad copy with solid fundamentals.")
        elif overall >= 55:
            explanation.append("⚠️ Average ad copy. This has potential but needs optimization.")
        else:
            explanation.append("❌ Below average ad copy that needs significant improvement.")
        
        # Penalty explanations
        if penalties['total_penalty'] > 0:
            explanation.append(f"\n⚡ {penalties['total_penalty']:.1f} points deducted for:")
            
            for category, details in penalties['categories'].items():
                if category == 'generic_phrases':
                    explanation.append(f"   • Overused phrases: {', '.join(details['phrases'][:3])}")
                elif category == 'vague_claims':
                    explanation.append(f"   • Vague claims: {', '.join(details['phrases'][:2])}")
                elif category == 'excessive_exclamations':
                    explanation.append(f"   • Too many exclamation marks ({details['count']})")
                elif category == 'excessive_caps':
                    explanation.append(f"   • Excessive capitalization ({details['count']} words)")
        
        # Bonus explanations
        if score_data['excellence_bonus'] > 0:
            explanation.append(f"\n⭐ +{score_data['excellence_bonus']:.1f} bonus for exceptional elements")
        
        return "\n".join(explanation)


# Utility functions for integration
def create_calibrated_scorer() -> BaselineScoreCalibrator:
    """Factory function to create a calibrated scorer instance."""
    return BaselineScoreCalibrator()


def apply_strict_scoring(clarity: float, persuasion: float, emotion: float, 
                        cta: float, platform_fit: float, full_text: str) -> Dict[str, Any]:
    """
    Convenience function to apply strict scoring to ad copy.
    Returns calibrated score with detailed breakdown.
    """
    calibrator = BaselineScoreCalibrator()
    return calibrator.calculate_calibrated_score(
        clarity, persuasion, emotion, cta, platform_fit, full_text
    )


# Test function to validate scoring range
def test_scoring_calibration():
    """Test function to ensure scores fall in the target 40-60% range for typical ads."""
    calibrator = BaselineScoreCalibrator()
    
    test_ads = [
        # Generic/poor ads (should score 30-50%)
        "Best solution ever! Click here to learn more about our amazing product.",
        "Revolutionary new system! Guaranteed results! Don't wait - act now!",
        "INCREDIBLE SAVINGS! Limited time only! Transform your life today!",
        
        # Average ads (should score 50-70%)  
        "Save 30% on marketing software. Streamline your campaigns and boost ROI.",
        "Professional web design services for small businesses. Fast turnaround guaranteed.",
        "Learn digital marketing from industry experts. 12-week online course starts Monday.",
        
        # Good ads (should score 70-85%)
        "Increase sales by 40% with our CRM used by 10,000+ businesses. Free 14-day trial.",
        "Join 50,000 marketers who improved conversion rates by 25%. Data-driven A/B testing platform.",
        "Reduce customer support tickets by 60%. AI chatbot handles 80% of inquiries automatically."
    ]
    
    print("🧪 Testing Scoring Calibration")
    print("=" * 50)
    
    for i, ad in enumerate(test_ads):
        # Mock component scores (typical values)
        result = calibrator.calculate_calibrated_score(
            clarity_score=65.0,
            persuasion_score=70.0, 
            emotion_score=60.0,
            cta_score=65.0,
            platform_fit_score=75.0,
            full_text=ad
        )
        
        print(f"Ad {i+1}: {result['overall_score']}% - {ad[:50]}...")
        if result['penalties_applied']['total_penalty'] > 0:
            print(f"   Penalties: -{result['penalties_applied']['total_penalty']}pts")
        print()


if __name__ == "__main__":
    test_scoring_calibration()