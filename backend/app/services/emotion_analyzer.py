from typing import Dict, Any, List
import re
import os

# Optional imports for AI models (fallback if not available)
try:
    from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification
    import torch
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False
    # Create dummy objects for type hints
    pipeline = None
    torch = None

class EmotionAnalyzer:
    """Analyzes emotional content and sentiment in ad copy"""
    
    def __init__(self):
        # Initialize emotion classification model
        self.emotion_classifier = None
        self.use_ai_model = False
        
        if TORCH_AVAILABLE:
            try:
                self.emotion_classifier = pipeline(
                    "text-classification",
                    model="j-hartmann/emotion-english-distilroberta-base",
                    device=0 if torch.cuda.is_available() else -1
                )
                self.use_ai_model = True
                print("✅ Emotion AI model loaded successfully")
            except Exception as e:
                print(f"⚠️ Failed to load emotion AI model: {e}")
                try:
                    # Fallback to basic sentiment
                    self.emotion_classifier = pipeline("sentiment-analysis")
                    self.use_ai_model = True
                    print("✅ Fallback sentiment model loaded")
                except Exception as e2:
                    print(f"⚠️ Failed to load fallback model: {e2}")
        else:
            print("⚠️ PyTorch not available - using rule-based emotion analysis")
        
        # Emotion words mapping
        self.emotion_words = {
            'joy': ['happy', 'excited', 'thrilled', 'delighted', 'amazing', 'fantastic'],
            'fear': ['worried', 'concerned', 'afraid', 'risky', 'dangerous', 'problem'],
            'anger': ['frustrated', 'annoyed', 'hate', 'terrible', 'awful', 'worst'],
            'sadness': ['sad', 'disappointed', 'regret', 'sorry', 'unfortunate'],
            'surprise': ['incredible', 'unbelievable', 'shocking', 'stunning', 'wow'],
            'trust': ['trusted', 'reliable', 'proven', 'guaranteed', 'secure', 'safe'],
            'urgency': ['now', 'today', 'limited', 'hurry', 'deadline', 'expires', 'quick']
        }
    
    def analyze_emotion(self, text: str) -> Dict[str, Any]:
        """Analyze emotional content of text"""
        # Always analyze emotion words and intensity (rule-based)
        emotion_word_analysis = self._analyze_emotion_words(text)
        intensity = self._calculate_emotional_intensity(text)
        
        emotions = []
        
        # Try to use AI model if available
        if self.use_ai_model and self.emotion_classifier:
            try:
                emotions = self.emotion_classifier(text)
            except Exception as e:
                print(f"⚠️ AI emotion analysis failed: {e}")
                emotions = []
        
        # Calculate emotion score (works with or without AI)
        emotion_score = self._calculate_emotion_score(emotions, emotion_word_analysis, intensity)
        
        # Determine primary emotion
        if emotions and len(emotions) > 0:
            primary_emotion = emotions[0]['label']
            emotion_confidence = emotions[0]['score']
        else:
            # Use rule-based primary emotion
            primary_emotion = self._get_primary_emotion_from_words(emotion_word_analysis)
            emotion_confidence = 0.7
        
        return {
            'emotion_score': emotion_score,
            'primary_emotion': primary_emotion,
            'emotion_confidence': emotion_confidence,
            'emotion_breakdown': emotion_word_analysis,
            'emotional_intensity': intensity,
            'recommendations': self._get_emotion_recommendations(emotions, emotion_word_analysis),
            'analysis_method': 'ai_model' if (emotions and len(emotions) > 0) else 'rule_based'
        }
    
    def _analyze_emotion_words(self, text: str) -> Dict[str, Any]:
        """Analyze presence of emotion-triggering words"""
        text_lower = text.lower()
        emotion_breakdown = {}
        
        for emotion, words in self.emotion_words.items():
            found_words = [word for word in words if word in text_lower]
            emotion_breakdown[emotion] = {
                'count': len(found_words),
                'words': found_words,
                'score': min(100, len(found_words) * 20)
            }
        
        return emotion_breakdown
    
    def _calculate_emotional_intensity(self, text: str) -> float:
        """Calculate overall emotional intensity"""
        # Count emotional indicators
        exclamation_marks = text.count('!')
        caps_words = len(re.findall(r'\b[A-Z]{2,}\b', text))
        
        # Emotional punctuation and formatting
        intensity_indicators = exclamation_marks + caps_words
        
        # Normalize to 0-100 scale
        intensity = min(100, intensity_indicators * 25)
        
        return intensity
    
    def _get_primary_emotion_from_words(self, emotion_word_analysis: Dict) -> str:
        """Determine primary emotion from word-based analysis"""
        # Find emotion with highest count
        max_count = 0
        primary_emotion = 'neutral'
        
        for emotion, data in emotion_word_analysis.items():
            if data['count'] > max_count:
                max_count = data['count']
                primary_emotion = emotion
        
        return primary_emotion if max_count > 0 else 'neutral'
    
    def _calculate_emotion_score(self, emotions: List[Dict], emotion_words: Dict, intensity: float) -> float:
        """Calculate overall emotion score"""
        base_score = 50  # Neutral baseline
        
        # Add score from AI model
        if emotions and len(emotions) > 0:
            confidence = emotions[0]['score']
            if emotions[0]['label'].lower() not in ['neutral', 'negative']:
                base_score += confidence * 30
        
        # Add score from emotion words
        total_emotion_words = sum(data['count'] for data in emotion_words.values())
        base_score += min(30, total_emotion_words * 5)
        
        # Add intensity bonus
        base_score += min(20, intensity * 0.2)
        
        return min(100, base_score)
    
    def _get_emotion_recommendations(self, emotions: List[Dict], emotion_words: Dict) -> List[str]:
        """Generate emotion improvement recommendations"""
        recommendations = []
        
        # Check if emotions are too weak
        total_emotion_words = sum(data['count'] for data in emotion_words.values())
        
        if total_emotion_words == 0:
            recommendations.append("Add emotional trigger words to create connection with your audience")
        
        if emotion_words['urgency']['count'] == 0:
            recommendations.append("Add urgency words like 'now', 'limited time', or 'today' to drive action")
        
        if emotion_words['trust']['count'] == 0:
            recommendations.append("Include trust indicators like 'proven', 'guaranteed', or 'trusted'")
        
        # Platform-specific recommendations
        recommendations.append("Consider A/B testing emotional vs. rational approaches")
        
        return recommendations
    
    def _fallback_emotion_analysis(self, text: str) -> Dict[str, Any]:
        """Fallback emotion analysis if AI model fails"""
        emotion_word_analysis = self._analyze_emotion_words(text)
        intensity = self._calculate_emotional_intensity(text)
        
        # Determine primary emotion from word analysis
        max_emotion = max(emotion_word_analysis.keys(), 
                         key=lambda x: emotion_word_analysis[x]['count'])
        
        return {
            'emotion_score': 60,  # Default score
            'primary_emotion': max_emotion,
            'emotion_confidence': 0.7,
            'emotion_breakdown': emotion_word_analysis,
            'emotional_intensity': intensity,
            'recommendations': self._get_emotion_recommendations([], emotion_word_analysis)
        }
