"""
Recommendation Orchestrator
Resolves conflicts and prioritizes recommendations from multiple tools

Problem: 9 tools × 5-8 recommendations each = 45-72 total recommendations
Solution: Intelligent prioritization → Top 5 actionable recommendations

Features:
- Detects conflicting recommendations (e.g., Legal Scanner says "avoid guaranteed" but ROI Generator suggests it)
- Prioritizes by impact score (CTR improvement potential)
- Considers implementation difficulty (easy vs hard)
- Returns top 5 most valuable recommendations
"""

import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class Priority(Enum):
    """Recommendation priority levels"""
    CRITICAL = 1  # Must fix - blocks conversion
    HIGH = 2      # Should fix - significant impact
    MEDIUM = 3    # Nice to have - moderate impact
    LOW = 4       # Optional - minimal impact


class ImpactLevel(Enum):
    """Expected performance impact"""
    HIGH = 3      # +20%+ improvement
    MEDIUM = 2    # +10-20% improvement
    LOW = 1       # +5-10% improvement


@dataclass
class Recommendation:
    """Structured recommendation with metadata"""
    title: str
    description: str
    tool_source: str  # Which tool generated it
    priority: Priority
    impact: ImpactLevel
    implementation_difficulty: str  # easy, medium, hard
    conflict_with: Optional[List[str]] = None  # List of recommendation IDs that conflict

    def score(self) -> float:
        """
        Calculate priority score for sorting

        Higher score = higher priority
        Formula: (priority_weight × 0.5) + (impact_weight × 0.3) + (difficulty_weight × 0.2)
        """
        priority_weight = {
            Priority.CRITICAL: 10,
            Priority.HIGH: 7,
            Priority.MEDIUM: 4,
            Priority.LOW: 1
        }

        impact_weight = {
            ImpactLevel.HIGH: 3,
            ImpactLevel.MEDIUM: 2,
            ImpactLevel.LOW: 1
        }

        difficulty_weight = {
            'easy': 3,
            'medium': 2,
            'hard': 1
        }

        score = (
            priority_weight[self.priority] * 0.5 +
            impact_weight[self.impact] * 0.3 +
            difficulty_weight.get(self.implementation_difficulty, 2) * 0.2
        )

        return score


class RecommendationOrchestrator:
    """Orchestrates recommendations from multiple tools"""

    def __init__(self):
        self.conflict_rules = self._load_conflict_rules()

    def orchestrate(
        self,
        tool_results: Dict[str, Any],
        max_recommendations: int = 5
    ) -> List[Recommendation]:
        """
        Process tool results and return prioritized recommendations

        Args:
            tool_results: Dict of tool name -> tool output
            max_recommendations: Maximum recommendations to return (default: 5)

        Returns:
            List of top recommendations, sorted by priority score
        """
        # Parse recommendations from all tools
        all_recommendations = self._parse_tool_recommendations(tool_results)

        if not all_recommendations:
            logger.warning("No recommendations parsed from tool results")
            return []

        # Detect conflicts
        all_recommendations = self._detect_conflicts(all_recommendations)

        # Resolve conflicts (keep highest priority)
        resolved = self._resolve_conflicts(all_recommendations)

        # Score and sort
        resolved.sort(key=lambda r: r.score(), reverse=True)

        # Return top N
        top_recommendations = resolved[:max_recommendations]

        logger.info(f"Orchestrated {len(all_recommendations)} recommendations down to {len(top_recommendations)}")

        return top_recommendations

    def _parse_tool_recommendations(self, tool_results: Dict) -> List[Recommendation]:
        """Parse recommendations from tool outputs"""
        recommendations = []

        for tool_name, tool_output in tool_results.items():
            # Skip if no recommendations
            if not hasattr(tool_output, 'recommendations') or not tool_output.recommendations:
                continue

            for rec_text in tool_output.recommendations:
                rec = self._parse_recommendation_text(rec_text, tool_name)
                if rec:
                    recommendations.append(rec)

        return recommendations

    def _parse_recommendation_text(self, text: str, tool_name: str) -> Optional[Recommendation]:
        """
        Parse recommendation text into structured format

        Uses markers in text to determine priority and impact:
        - Priority: ❌ (critical), ⚠️ (high), 💡 (medium), ✓ (low)
        - Keywords: "must", "should", "consider", "try"
        """
        if not text or len(text) < 5:
            return None

        # Determine priority from text markers
        if any(marker in text for marker in ['❌', 'critical', 'must', 'required', 'blocking']):
            priority = Priority.CRITICAL
        elif any(marker in text for marker in ['⚠️', 'important', 'should', 'recommend', 'strongly']):
            priority = Priority.HIGH
        elif any(marker in text for marker in ['💡', 'consider', 'suggest', 'could', 'may want']):
            priority = Priority.MEDIUM
        else:
            priority = Priority.LOW

        # Determine impact from text
        if any(word in text.lower() for word in ['significantly', 'major', 'dramatically', '2x', '20%+', 'double']):
            impact = ImpactLevel.HIGH
        elif any(word in text.lower() for word in ['improve', 'better', 'increase', '10%', 'boost']):
            impact = ImpactLevel.MEDIUM
        else:
            impact = ImpactLevel.LOW

        # Determine difficulty from text
        if any(word in text.lower() for word in ['add', 'include', 'use', 'try', 'simply', 'just']):
            difficulty = 'easy'
        elif any(word in text.lower() for word in ['rewrite', 'change', 'replace', 'rework', 'adjust']):
            difficulty = 'medium'
        else:
            difficulty = 'hard'

        return Recommendation(
            title=self._extract_title(text),
            description=text,
            tool_source=tool_name,
            priority=priority,
            impact=impact,
            implementation_difficulty=difficulty
        )

    def _extract_title(self, text: str) -> str:
        """Extract title from recommendation text"""
        # Remove emoji and markers
        text = re.sub(r'[⚠️❌💡✅🔴]', '', text)

        # Take first sentence or phrase
        sentences = re.split(r'[.!?]', text)
        title = sentences[0].strip() if sentences else text.strip()

        # Limit length
        if len(title) > 60:
            title = title[:57] + '...'

        return title

    def _detect_conflicts(self, recommendations: List[Recommendation]) -> List[Recommendation]:
        """Detect conflicting recommendations"""
        for i, rec1 in enumerate(recommendations):
            for j, rec2 in enumerate(recommendations[i+1:], start=i+1):
                if self._are_conflicting(rec1, rec2):
                    if rec1.conflict_with is None:
                        rec1.conflict_with = []
                    if rec2.conflict_with is None:
                        rec2.conflict_with = []

                    rec1.conflict_with.append(rec2.title)
                    rec2.conflict_with.append(rec1.title)

        return recommendations

    def _are_conflicting(self, rec1: Recommendation, rec2: Recommendation) -> bool:
        """
        Check if two recommendations conflict

        Conflict types:
        1. Predefined conflict rules (e.g., legal vs ROI)
        2. Semantic conflicts (add vs remove same thing)
        """
        # Check predefined conflict rules
        conflict_key = f"{rec1.tool_source}:{rec2.tool_source}"
        reverse_key = f"{rec2.tool_source}:{rec1.tool_source}"

        if conflict_key in self.conflict_rules:
            pattern1, pattern2 = self.conflict_rules[conflict_key]
            if pattern1 in rec1.description.lower() and pattern2 in rec2.description.lower():
                return True

        if reverse_key in self.conflict_rules:
            pattern1, pattern2 = self.conflict_rules[reverse_key]
            if pattern1 in rec2.description.lower() and pattern2 in rec1.description.lower():
                return True

        # Semantic conflicts: add vs remove
        if 'add' in rec1.description.lower() and 'remove' in rec2.description.lower():
            # Check if they're talking about the same thing
            rec1_words = set(rec1.description.lower().split())
            rec2_words = set(rec2.description.lower().split())
            common = rec1_words & rec2_words

            # If they share many words, likely conflicting
            if len(common) > 3:
                return True

        # Opposite recommendations: increase vs decrease
        if ('increase' in rec1.description.lower() and 'decrease' in rec2.description.lower()) or \
           ('decrease' in rec1.description.lower() and 'increase' in rec2.description.lower()):
            rec1_words = set(rec1.description.lower().split())
            rec2_words = set(rec2.description.lower().split())
            common = rec1_words & rec2_words

            if len(common) > 3:
                return True

        return False

    def _resolve_conflicts(self, recommendations: List[Recommendation]) -> List[Recommendation]:
        """
        Resolve conflicts by keeping higher priority recommendation

        Strategy: When recommendations conflict, keep the one with highest score
        """
        resolved = []
        skipped = set()

        for rec in recommendations:
            if rec.title in skipped:
                continue

            if rec.conflict_with:
                # Find conflicting recommendations
                conflicts = [r for r in recommendations if r.title in rec.conflict_with]

                # Keep the one with highest score
                all_conflicting = [rec] + conflicts
                winner = max(all_conflicting, key=lambda r: r.score())

                if winner.title == rec.title:
                    resolved.append(rec)
                    # Skip others
                    for conflict in conflicts:
                        skipped.add(conflict.title)
                else:
                    skipped.add(rec.title)
            else:
                resolved.append(rec)

        return resolved

    def _load_conflict_rules(self) -> Dict[str, tuple]:
        """
        Load predefined conflict rules

        Format: "tool1:tool2": ("pattern1", "pattern2")
        If pattern1 is in tool1's recommendation and pattern2 is in tool2's, they conflict
        """
        return {
            # Legal Risk Scanner vs ROI Generator conflicts
            "legal_risk_scanner:roi_copy_generator": ("guaranteed", "roi"),
            "legal_risk_scanner:roi_copy_generator": ("guarantee", "return"),

            # Psychology vs Compliance conflicts
            "psychology_scorer:compliance_checker": ("urgency", "pressure"),
            "psychology_scorer:legal_risk_scanner": ("claim", "substantiate"),

            # Brand Voice vs Platform Optimizer conflicts
            "brand_voice_engine:ad_copy_analyzer": ("formal", "casual"),
            "brand_voice_engine:ad_copy_analyzer": ("professional", "playful"),

            # Industry Optimizer vs Brand Voice conflicts
            "industry_optimizer:brand_voice_engine": ("jargon", "simple"),
            "industry_optimizer:brand_voice_engine": ("technical", "accessible"),
        }


# Singleton instance for easy import
orchestrator = RecommendationOrchestrator()
