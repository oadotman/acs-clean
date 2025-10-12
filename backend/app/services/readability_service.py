"""
Readability scoring service for ad copy analysis.

Implements Flesch Reading Ease and other readability metrics to ensure
ad copy is accessible and easy to understand for target audiences.
"""

import re
from typing import Dict, List, Tuple
from dataclasses import dataclass

@dataclass
class ReadabilityScore:
    """Container for readability analysis results"""
    flesch_score: float
    flesch_grade_level: str
    flesch_interpretation: str
    sentence_count: int
    word_count: int
    syllable_count: int
    average_sentence_length: float
    average_syllables_per_word: float
    recommendations: List[str]
    is_passing: bool
    target_score: float

class ReadabilityService:
    """Service for calculating readability scores and providing improvement recommendations"""
    
    # Flesch Reading Ease score interpretations
    FLESCH_INTERPRETATIONS = [
        (90, 100, "Very Easy", "5th grade", "Very easy to read. Easily understood by an average 11-year-old student."),
        (80, 89, "Easy", "6th grade", "Easy to read. Conversational English for consumers."),
        (70, 79, "Fairly Easy", "7th grade", "Fairly easy to read."),
        (60, 69, "Standard", "8th-9th grade", "Plain English. Easily understood by 13- to 15-year-old students."),
        (50, 59, "Fairly Difficult", "10th-12th grade", "Fairly difficult to read."),
        (30, 49, "Difficult", "College level", "Difficult to read."),
        (0, 29, "Very Difficult", "Graduate level", "Very difficult to read. Best understood by university graduates.")
    ]
    
    def __init__(self):
        self.vowel_pattern = re.compile(r'[aeiouyAEIOUY]')
        self.sentence_pattern = re.compile(r'[.!?]+')
        self.word_pattern = re.compile(r'\b\w+\b')
    
    def calculate_flesch_reading_ease(self, text: str, target_score: float = 60.0) -> ReadabilityScore:
        """
        Calculate Flesch Reading Ease score for the given text.
        
        Formula: 206.835 - (1.015 × ASL) - (84.6 × ASW)
        Where:
        - ASL = Average Sentence Length (words per sentence)
        - ASW = Average Syllables per Word
        """
        if not text.strip():
            return self._empty_score(target_score)
        
        # Count sentences, words, and syllables
        sentence_count = self._count_sentences(text)
        word_count = self._count_words(text)
        syllable_count = self._count_syllables(text)
        
        # Handle edge cases
        if sentence_count == 0 or word_count == 0:
            return self._empty_score(target_score)
        
        # Calculate averages
        average_sentence_length = word_count / sentence_count
        average_syllables_per_word = syllable_count / word_count
        
        # Calculate Flesch Reading Ease score
        flesch_score = 206.835 - (1.015 * average_sentence_length) - (84.6 * average_syllables_per_word)
        
        # Clamp score to valid range
        flesch_score = max(0, min(100, flesch_score))
        
        # Get interpretation
        grade_level, interpretation, description = self._interpret_flesch_score(flesch_score)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(
            flesch_score, target_score, average_sentence_length, 
            average_syllables_per_word, word_count
        )
        
        return ReadabilityScore(
            flesch_score=round(flesch_score, 1),
            flesch_grade_level=grade_level,
            flesch_interpretation=interpretation,
            sentence_count=sentence_count,
            word_count=word_count,
            syllable_count=syllable_count,
            average_sentence_length=round(average_sentence_length, 1),
            average_syllables_per_word=round(average_syllables_per_word, 2),
            recommendations=recommendations,
            is_passing=flesch_score >= target_score,
            target_score=target_score
        )
    
    def _count_sentences(self, text: str) -> int:
        """Count the number of sentences in the text"""
        # Split by sentence ending punctuation
        sentences = self.sentence_pattern.split(text)
        # Filter out empty strings and count
        sentences = [s.strip() for s in sentences if s.strip()]
        return max(1, len(sentences))  # At least 1 sentence
    
    def _count_words(self, text: str) -> int:
        """Count the number of words in the text"""
        words = self.word_pattern.findall(text)
        return len(words)
    
    def _count_syllables(self, text: str) -> int:
        """
        Count syllables in text using a heuristic approach.
        This is an approximation but works well for readability scoring.
        """
        words = self.word_pattern.findall(text.lower())
        total_syllables = 0
        
        for word in words:
            syllables = self._count_syllables_in_word(word)
            total_syllables += syllables
        
        return total_syllables
    
    def _count_syllables_in_word(self, word: str) -> int:
        """
        Count syllables in a single word using heuristic rules.
        """
        word = word.lower()
        
        # Handle empty words
        if not word:
            return 1
        
        # Count vowel groups
        vowel_groups = 0
        prev_was_vowel = False
        
        for char in word:
            is_vowel = bool(self.vowel_pattern.match(char))
            if is_vowel and not prev_was_vowel:
                vowel_groups += 1
            prev_was_vowel = is_vowel
        
        # Apply common English rules
        if word.endswith('e'):
            vowel_groups -= 1
        
        if word.endswith('le') and len(word) > 2 and not self.vowel_pattern.match(word[-3]):
            vowel_groups += 1
        
        if vowel_groups == 0:
            vowel_groups = 1
        
        return vowel_groups
    
    def _interpret_flesch_score(self, score: float) -> Tuple[str, str, str]:
        """Interpret Flesch Reading Ease score"""
        for min_score, max_score, interpretation, grade_level, description in self.FLESCH_INTERPRETATIONS:
            if min_score <= score <= max_score:
                return grade_level, interpretation, description
        
        # Fallback for scores outside normal range
        if score > 100:
            return "Elementary", "Very Easy", "Extremely easy to read"
        else:
            return "Graduate+", "Very Difficult", "Extremely difficult to read"
    
    def _generate_recommendations(
        self, 
        flesch_score: float, 
        target_score: float,
        avg_sentence_length: float,
        avg_syllables_per_word: float,
        word_count: int
    ) -> List[str]:
        """Generate recommendations for improving readability"""
        recommendations = []
        
        if flesch_score < target_score:
            score_gap = target_score - flesch_score
            
            # Sentence length recommendations
            if avg_sentence_length > 20:
                recommendations.append(
                    f"Break up long sentences. Average sentence length is {avg_sentence_length:.1f} words. "
                    "Try to keep sentences under 20 words."
                )
            elif avg_sentence_length > 15:
                recommendations.append(
                    "Consider shortening some sentences for better readability."
                )
            
            # Word complexity recommendations
            if avg_syllables_per_word > 1.6:
                recommendations.append(
                    f"Use simpler words. Average syllables per word is {avg_syllables_per_word:.2f}. "
                    "Replace complex words with shorter alternatives."
                )
            elif avg_syllables_per_word > 1.4:
                recommendations.append(
                    "Consider using some simpler word choices where possible."
                )
            
            # Specific improvement suggestions based on score gap
            if score_gap > 20:
                recommendations.extend([
                    "This text is significantly too complex. Consider major revisions:",
                    "• Use shorter, simpler sentences (10-15 words each)",
                    "• Replace jargon and technical terms with everyday language",
                    "• Break complex ideas into multiple simple sentences"
                ])
            elif score_gap > 10:
                recommendations.extend([
                    "This text could be more accessible:",
                    "• Shorten some longer sentences",
                    "• Replace some complex words with simpler alternatives",
                    "• Use more active voice"
                ])
            else:
                recommendations.append(
                    "Minor improvements needed. Consider simplifying a few words or sentences."
                )
            
            # Ad copy specific recommendations
            if word_count > 50:
                recommendations.append(
                    "For ad copy, consider making the message more concise and punchy."
                )
        
        else:
            recommendations.append(
                f"Good readability! Score of {flesch_score:.1f} meets the target of {target_score}."
            )
            
            # Additional optimization suggestions even for passing scores
            if flesch_score < target_score + 10:
                recommendations.append(
                    "Consider minor improvements to make the text even more accessible."
                )
        
        return recommendations
    
    def _empty_score(self, target_score: float) -> ReadabilityScore:
        """Return a default score for empty or invalid text"""
        return ReadabilityScore(
            flesch_score=0.0,
            flesch_grade_level="Unknown",
            flesch_interpretation="No text provided",
            sentence_count=0,
            word_count=0,
            syllable_count=0,
            average_sentence_length=0.0,
            average_syllables_per_word=0.0,
            recommendations=["Please provide text to analyze"],
            is_passing=False,
            target_score=target_score
        )
    
    def analyze_for_ad_copy(self, text: str, platform: str = "general") -> ReadabilityScore:
        """
        Analyze readability specifically for ad copy with platform-specific targets.
        """
        # Platform-specific readability targets
        platform_targets = {
            "facebook": 65,     # Slightly higher for social media
            "instagram": 70,    # Visual platform, simpler text
            "linkedin": 55,     # Professional audience
            "twitter": 70,      # Character limit encourages brevity
            "tiktok": 75,       # Young audience
            "google": 60,       # Search intent, clearer language
            "general": 60       # Default target
        }
        
        target_score = platform_targets.get(platform, 60)
        return self.calculate_flesch_reading_ease(text, target_score)
    
    def get_improvement_suggestions(self, text: str) -> Dict[str, List[str]]:
        """Get specific suggestions for improving text readability"""
        analysis = self.calculate_flesch_reading_ease(text)
        
        suggestions = {
            "sentence_structure": [],
            "word_choice": [],
            "overall_clarity": [],
            "ad_copy_specific": []
        }
        
        # Analyze sentence structure
        sentences = self.sentence_pattern.split(text)
        long_sentences = [s.strip() for s in sentences if len(s.strip().split()) > 20]
        
        if long_sentences:
            suggestions["sentence_structure"].extend([
                "Break these long sentences into shorter ones:",
                *[f"• {sentence[:60]}..." for sentence in long_sentences[:3]]
            ])
        
        # Analyze word complexity
        words = self.word_pattern.findall(text.lower())
        complex_words = [word for word in words if self._count_syllables_in_word(word) > 2]
        
        if len(complex_words) > len(words) * 0.15:  # More than 15% complex words
            suggestions["word_choice"].append(
                "Consider simpler alternatives for these complex words:"
            )
            # Show a few examples
            unique_complex = list(set(complex_words))[:5]
            suggestions["word_choice"].extend([
                f"• {word} ({self._count_syllables_in_word(word)} syllables)" 
                for word in unique_complex
            ])
        
        # Overall clarity suggestions
        if analysis.flesch_score < 60:
            suggestions["overall_clarity"].extend([
                "Use more conversational language",
                "Prefer active voice over passive voice",
                "Remove unnecessary words and phrases",
                "Use concrete examples instead of abstract concepts"
            ])
        
        # Ad-specific suggestions
        suggestions["ad_copy_specific"].extend([
            "Start with a clear benefit or value proposition",
            "Use 'you' to speak directly to your audience",
            "End with a clear, actionable call-to-action",
            "Test different versions to see what resonates"
        ])
        
        return suggestions