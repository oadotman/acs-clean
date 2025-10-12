import textstat
import re
from typing import Dict, Any

class ReadabilityAnalyzer:
    """Analyzes text readability and clarity"""
    
    def __init__(self):
        self.power_words = [
            'free', 'instant', 'guaranteed', 'proven', 'secret', 'discover',
            'amazing', 'incredible', 'ultimate', 'exclusive', 'limited',
            'breakthrough', 'revolutionary', 'new', 'save', 'now'
        ]
    
    def analyze_clarity(self, text: str) -> Dict[str, Any]:
        """Analyze text clarity and readability"""
        # Basic readability metrics
        flesch_score = textstat.flesch_reading_ease(text)
        grade_level = textstat.flesch_kincaid_grade(text)
        
        # Word and sentence analysis
        word_count = len(text.split())
        sentence_count = len(re.split(r'[.!?]+', text))
        avg_words_per_sentence = word_count / max(sentence_count, 1)
        
        # Calculate clarity score (0-100)
        clarity_score = self._calculate_clarity_score(
            flesch_score, grade_level, avg_words_per_sentence, word_count
        )
        
        # Generate recommendations
        recommendations = self._get_clarity_recommendations(
            flesch_score, grade_level, avg_words_per_sentence, word_count
        )
        
        return {
            'clarity_score': clarity_score,
            'flesch_reading_ease': flesch_score,
            'grade_level': grade_level,
            'word_count': word_count,
            'sentence_count': sentence_count,
            'avg_words_per_sentence': avg_words_per_sentence,
            'recommendations': recommendations
        }
    
    def _calculate_clarity_score(self, flesch_score: float, grade_level: float, 
                                avg_words: float, word_count: int) -> float:
        """Calculate overall clarity score"""
        # Base score from Flesch reading ease
        base_score = min(flesch_score, 100)
        
        # Penalize if grade level is too high (ideal: 6-8th grade)
        if grade_level > 8:
            base_score *= 0.9
        elif grade_level > 10:
            base_score *= 0.8
        
        # Penalize very long sentences
        if avg_words > 20:
            base_score *= 0.85
        elif avg_words > 25:
            base_score *= 0.75
        
        # Penalize very long text for ads
        if word_count > 50:
            base_score *= 0.9
        elif word_count > 75:
            base_score *= 0.8
        
        return max(0, min(100, base_score))
    
    def _get_clarity_recommendations(self, flesch_score: float, grade_level: float, 
                                   avg_words: float, word_count: int) -> list:
        """Generate clarity improvement recommendations"""
        recommendations = []
        
        if flesch_score < 60:
            recommendations.append("Use simpler words and shorter sentences to improve readability")
        
        if grade_level > 8:
            recommendations.append("Lower the reading level to 6th-8th grade for better comprehension")
        
        if avg_words > 20:
            recommendations.append("Break up long sentences into shorter, punchier ones")
        
        if word_count > 75:
            recommendations.append("Consider shortening the text - ads perform better when concise")
        
        return recommendations
    
    def analyze_power_words(self, text: str) -> Dict[str, Any]:
        """Analyze usage of power words in the text"""
        text_lower = text.lower()
        found_power_words = [word for word in self.power_words if word in text_lower]
        
        power_word_density = len(found_power_words) / len(text.split()) if text.split() else 0
        
        return {
            'power_words_found': found_power_words,
            'power_word_count': len(found_power_words),
            'power_word_density': power_word_density,
            'power_score': min(100, len(found_power_words) * 15)  # Max 100
        }
