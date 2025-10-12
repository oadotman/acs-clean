"""
Cliché detection and filtering service for ad copy.

Identifies overused marketing phrases and provides fresh alternatives to ensure
ad copy sounds original and engaging rather than generic and tired.
"""

import re
from typing import Dict, List, Set, Tuple, Optional
from dataclasses import dataclass
from app.constants.creative_controls import (
    MARKETING_CLICHES, CLICHE_ALTERNATIVES, get_cliche_alternatives
)

@dataclass
class ClicheDetection:
    """Individual cliché detection result"""
    phrase: str
    position: int
    length: int
    alternatives: List[str]
    severity: str  # "mild", "moderate", "severe"
    context: str   # Surrounding text for context

@dataclass
class ClicheAnalysisResult:
    """Complete cliché analysis result"""
    total_cliches: int
    cliches_found: List[ClicheDetection]
    originality_score: float  # 0-100, higher is more original
    severity_breakdown: Dict[str, int]
    auto_fix_available: bool
    recommendations: List[str]

class ClicheFilter:
    """Service for detecting and filtering marketing clichés"""
    
    def __init__(self):
        # Severity classification for different types of clichés
        self.severity_map = {
            # Severe - extremely overused and should be avoided
            "game-changer": "severe",
            "next-level": "severe", 
            "revolutionary": "severe",
            "paradigm shift": "severe",
            "transform your life": "severe",
            "change everything": "severe",
            "best-in-class": "severe",
            "world-class": "severe",
            
            # Moderate - overused but sometimes acceptable
            "cutting-edge": "moderate",
            "innovative": "moderate",
            "optimize": "moderate",
            "streamline": "moderate",
            "leverage": "moderate",
            "amazing results": "moderate",
            "incredible value": "moderate",
            
            # Mild - slightly overused but less problematic
            "efficiently": "mild",
            "effectively": "mild",
            "significantly": "mild",
            "outstanding": "mild",
            "exceptional": "mild"
        }
        
        # Context-aware replacements
        self.context_replacements = {
            "business": {
                "game-changer": ["transforms operations", "shifts strategy", "improves efficiency"],
                "leverage": ["use", "apply", "utilize", "employ"],
                "optimize": ["improve", "enhance", "refine", "perfect"],
                "streamline": ["simplify", "organize", "coordinate", "structure"]
            },
            "consumer": {
                "game-changer": ["makes life easier", "changes how you think", "transforms your routine"],
                "amazing results": ["real improvements", "noticeable changes", "meaningful progress"],
                "incredible value": ["great worth", "smart purchase", "worthwhile investment"]
            },
            "tech": {
                "cutting-edge": ["latest", "modern", "current", "advanced"],
                "state-of-the-art": ["newest", "current-generation", "modern", "up-to-date"],
                "revolutionary": ["innovative", "breakthrough", "pioneering", "groundbreaking"]
            }
        }
        
        # Industry-specific cliché tolerance
        self.industry_tolerance = {
            "technology": 0.1,      # Tech can be slightly more tolerant of "innovative" language
            "finance": 0.05,        # Finance should be very conservative
            "healthcare": 0.03,     # Healthcare must be extremely careful
            "legal": 0.02,          # Legal must avoid all clichés
            "education": 0.08,      # Education can use some motivational language
            "retail": 0.12,         # Retail can be more expressive
            "general": 0.07         # General default
        }
    
    def analyze_text(self, text: str, industry: str = "general") -> ClicheAnalysisResult:
        """
        Analyze text for marketing clichés and provide detailed feedback.
        """
        if not text.strip():
            return self._empty_result()
        
        cliches_found = []
        text_lower = text.lower()
        
        # Search for each known cliché
        for cliche in MARKETING_CLICHES:
            positions = self._find_all_positions(text_lower, cliche)
            
            for position in positions:
                # Get surrounding context
                context_start = max(0, position - 20)
                context_end = min(len(text), position + len(cliche) + 20)
                context = text[context_start:context_end].strip()
                
                # Get severity
                severity = self.severity_map.get(cliche, "moderate")
                
                # Get alternatives
                alternatives = get_cliche_alternatives(cliche)
                if not alternatives:
                    alternatives = self._generate_generic_alternatives(cliche)
                
                detection = ClicheDetection(
                    phrase=cliche,
                    position=position,
                    length=len(cliche),
                    alternatives=alternatives,
                    severity=severity,
                    context=context
                )
                cliches_found.append(detection)
        
        # Calculate originality score
        originality_score = self._calculate_originality_score(
            text, cliches_found, industry
        )
        
        # Severity breakdown
        severity_breakdown = {
            "severe": len([c for c in cliches_found if c.severity == "severe"]),
            "moderate": len([c for c in cliches_found if c.severity == "moderate"]),
            "mild": len([c for c in cliches_found if c.severity == "mild"])
        }
        
        # Check if auto-fix is available
        auto_fix_available = all(
            len(c.alternatives) > 0 for c in cliches_found
        ) and len(cliches_found) <= 5  # Don't auto-fix if too many clichés
        
        # Generate recommendations
        recommendations = self._generate_recommendations(
            cliches_found, originality_score, industry
        )
        
        return ClicheAnalysisResult(
            total_cliches=len(cliches_found),
            cliches_found=cliches_found,
            originality_score=round(originality_score, 1),
            severity_breakdown=severity_breakdown,
            auto_fix_available=auto_fix_available,
            recommendations=recommendations
        )
    
    def auto_fix_text(self, text: str, analysis: ClicheAnalysisResult) -> str:
        """
        Automatically replace clichés with fresh alternatives.
        """
        if not analysis.auto_fix_available or not analysis.cliches_found:
            return text
        
        fixed_text = text
        
        # Sort by position (reverse order to maintain positions)
        cliches_sorted = sorted(
            analysis.cliches_found, 
            key=lambda x: x.position, 
            reverse=True
        )
        
        for cliche in cliches_sorted:
            if cliche.alternatives:
                # Choose the best alternative (first one is usually best)
                replacement = cliche.alternatives[0]
                
                # Preserve original capitalization
                original_phrase = text[cliche.position:cliche.position + cliche.length]
                if original_phrase.isupper():
                    replacement = replacement.upper()
                elif original_phrase.istitle():
                    replacement = replacement.title()
                
                # Replace the cliché
                fixed_text = (
                    fixed_text[:cliche.position] + 
                    replacement + 
                    fixed_text[cliche.position + cliche.length:]
                )
        
        return fixed_text
    
    def get_fresh_alternatives(self, cliche: str, context: str = "general") -> List[str]:
        """
        Get context-aware fresh alternatives for a specific cliché.
        """
        # First check predefined alternatives
        alternatives = get_cliche_alternatives(cliche)
        
        if alternatives:
            return alternatives
        
        # Check context-specific alternatives
        context_key = self._detect_context(context)
        if context_key in self.context_replacements:
            context_alts = self.context_replacements[context_key].get(cliche, [])
            if context_alts:
                return context_alts
        
        # Generate generic alternatives
        return self._generate_generic_alternatives(cliche)
    
    def _find_all_positions(self, text: str, phrase: str) -> List[int]:
        """Find all positions where a phrase occurs in text."""
        positions = []
        start = 0
        
        while True:
            pos = text.find(phrase, start)
            if pos == -1:
                break
            positions.append(pos)
            start = pos + 1
        
        return positions
    
    def _calculate_originality_score(
        self, 
        text: str, 
        cliches: List[ClicheDetection], 
        industry: str
    ) -> float:
        """
        Calculate originality score based on cliché density and severity.
        """
        if not text:
            return 0.0
        
        base_score = 100.0
        text_length = len(text)
        
        # Deduct points for each cliché based on severity
        for cliche in cliches:
            if cliche.severity == "severe":
                base_score -= 15
            elif cliche.severity == "moderate":
                base_score -= 10
            else:  # mild
                base_score -= 5
        
        # Additional deduction for cliché density
        cliche_density = len(cliches) / max(1, text_length / 100)  # Per 100 characters
        if cliche_density > 0.05:  # More than 5% clichés
            base_score -= (cliche_density - 0.05) * 100
        
        # Industry-specific adjustments
        tolerance = self.industry_tolerance.get(industry, 0.07)
        if cliche_density <= tolerance:
            base_score += 5  # Bonus for staying within industry tolerance
        
        return max(0, min(100, base_score))
    
    def _detect_context(self, text: str) -> str:
        """
        Detect the context/domain of the text to provide better alternatives.
        """
        text_lower = text.lower()
        
        # Business context indicators
        business_words = ["roi", "revenue", "profit", "enterprise", "corporate", "b2b"]
        if any(word in text_lower for word in business_words):
            return "business"
        
        # Consumer context indicators
        consumer_words = ["lifestyle", "family", "home", "personal", "everyday"]
        if any(word in text_lower for word in consumer_words):
            return "consumer"
        
        # Tech context indicators
        tech_words = ["software", "app", "platform", "digital", "cloud", "ai"]
        if any(word in text_lower for word in tech_words):
            return "tech"
        
        return "general"
    
    def _generate_generic_alternatives(self, cliche: str) -> List[str]:
        """
        Generate generic alternatives when specific ones aren't available.
        """
        # Simple word mappings for common patterns
        word_mappings = {
            "amazing": ["impressive", "notable", "remarkable"],
            "incredible": ["outstanding", "exceptional", "striking"],
            "revolutionary": ["innovative", "groundbreaking", "pioneering"],
            "ultimate": ["complete", "comprehensive", "thorough"],
            "perfect": ["ideal", "excellent", "optimal"],
            "guaranteed": ["reliable", "dependable", "assured"],
            "exclusive": ["special", "unique", "limited"],
            "premium": ["high-quality", "superior", "top-tier"]
        }
        
        # Look for mappings within the cliché
        for word, alternatives in word_mappings.items():
            if word in cliche.lower():
                return alternatives
        
        # Fallback generic alternatives
        return ["effective", "helpful", "valuable", "beneficial", "worthwhile"]
    
    def _generate_recommendations(
        self, 
        cliches: List[ClicheDetection], 
        originality_score: float,
        industry: str
    ) -> List[str]:
        """Generate actionable recommendations for improving originality."""
        recommendations = []
        
        if not cliches:
            recommendations.append("✅ Great! No marketing clichés detected.")
            recommendations.append("💡 Your copy sounds fresh and original.")
            return recommendations
        
        # Severity-based recommendations
        severe_cliches = [c for c in cliches if c.severity == "severe"]
        moderate_cliches = [c for c in cliches if c.severity == "moderate"]
        
        if severe_cliches:
            recommendations.append("🚨 CRITICAL: Replace these severely overused phrases:")
            for cliche in severe_cliches[:3]:  # Show top 3
                alt_text = f" → Try: '{cliche.alternatives[0]}'" if cliche.alternatives else ""
                recommendations.append(f"  • '{cliche.phrase}'{alt_text}")
        
        if moderate_cliches:
            recommendations.append("⚠️ MODERATE: Consider replacing these common phrases:")
            for cliche in moderate_cliches[:3]:  # Show top 3
                alt_text = f" → Try: '{cliche.alternatives[0]}'" if cliche.alternatives else ""
                recommendations.append(f"  • '{cliche.phrase}'{alt_text}")
        
        # Score-based recommendations
        if originality_score < 50:
            recommendations.append("📝 ORIGINALITY: Your copy relies heavily on clichés")
            recommendations.append("   Try writing in your own voice instead of using marketing speak")
        elif originality_score < 70:
            recommendations.append("📝 GOOD PROGRESS: Reduce a few more clichés for better impact")
        else:
            recommendations.append("✨ EXCELLENT: Your copy sounds original and engaging!")
        
        # Industry-specific advice
        industry_advice = {
            "finance": "For financial services, avoid any exaggerated claims",
            "healthcare": "Healthcare copy must be especially careful about promises",
            "legal": "Legal advertising should be conservative and factual",
            "technology": "Tech audiences appreciate specificity over hype",
            "education": "Educational content should be inspiring but realistic"
        }
        
        if industry in industry_advice:
            recommendations.append(f"🏢 INDUSTRY: {industry_advice[industry]}")
        
        # General writing tips
        recommendations.extend([
            "💡 TIP: Use specific benefits instead of generic superlatives",
            "💡 TIP: Replace clichés with concrete, measurable outcomes",
            "💡 TIP: Write like you're explaining to a friend, not selling to a crowd"
        ])
        
        return recommendations
    
    def _empty_result(self) -> ClicheAnalysisResult:
        """Return empty result for invalid input."""
        return ClicheAnalysisResult(
            total_cliches=0,
            cliches_found=[],
            originality_score=0.0,
            severity_breakdown={"severe": 0, "moderate": 0, "mild": 0},
            auto_fix_available=False,
            recommendations=["Please provide text to analyze for clichés"]
        )
    
    def is_text_original(self, text: str, threshold: float = 70.0) -> bool:
        """
        Quick check if text meets originality threshold.
        """
        analysis = self.analyze_text(text)
        return analysis.originality_score >= threshold
    
    def get_cliche_summary(self, analysis: ClicheAnalysisResult) -> Dict[str, any]:
        """
        Get a summary of cliché analysis for API responses.
        """
        return {
            "total_cliches": analysis.total_cliches,
            "originality_score": analysis.originality_score,
            "is_original": analysis.originality_score >= 70,
            "severity_breakdown": analysis.severity_breakdown,
            "auto_fix_available": analysis.auto_fix_available,
            "needs_attention": analysis.total_cliches > 0,
            "risk_level": (
                "high" if analysis.severity_breakdown["severe"] > 0 else
                "medium" if analysis.severity_breakdown["moderate"] > 2 else
                "low"
            )
        }