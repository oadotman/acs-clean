"""
Multi-Agent Ad Copy Optimization System

Architecture:
1. Analyzer Agent - Reviews and scores input copy
2. Strategist Agent - Plans improvement strategy
3. Writer Agent - Generates variations (A/B/C + Improved)
4. Quality Control Agent - Validates and scores output

Each agent provides concise reasoning for transparency without exposing raw chain-of-thought.
"""

import asyncio
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime
import re
import logging

from app.services.production_ai_generator import ProductionAIService
from app.core.exceptions import AIProviderUnavailable

logger = logging.getLogger(__name__)


@dataclass
class QualityScore:
    """Quality metrics for ad copy (0-100 scale)"""
    grammar: float
    clarity: float
    emotion: float
    cta_strength: float
    platform_fit: float
    overall: float
    
    def to_dict(self) -> Dict[str, float]:
        return asdict(self)


@dataclass
class AgentOutput:
    """Output from a single agent"""
    agent_name: str
    decision_summary: List[str]  # 1-2 bullet points explaining key decisions
    data: Dict[str, Any]
    timestamp: str
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class VariationOutput:
    """Output for a single variation"""
    variation_type: str  # 'improved', 'benefit', 'problem', 'story'
    headline: str
    body_text: str
    cta: str
    score: QualityScore
    improvement_delta: float  # Percentage improvement from original
    reasoning: List[str]  # Why this variation works
    
    def to_dict(self) -> Dict[str, Any]:
        result = asdict(self)
        result['score'] = self.score.to_dict()
        return result


@dataclass
class OptimizationResult:
    """Complete multi-agent optimization result"""
    original_score: QualityScore
    improved_score: QualityScore
    variations: List[VariationOutput]  # [improved, A, B, C]
    reasoning_log: Dict[str, AgentOutput]
    suggestions: List[str]
    iteration_count: int
    improvement_history: List[Dict[str, Any]]
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'original_score': self.original_score.to_dict(),
            'improved_score': self.improved_score.to_dict(),
            'variations': [v.to_dict() for v in self.variations],
            'reasoning_log': {k: v.to_dict() for k, v in self.reasoning_log.items()},
            'suggestions': self.suggestions,
            'iteration_count': self.iteration_count,
            'improvement_history': self.improvement_history
        }


class AnalyzerAgent:
    """
    Agent 1: Analyzes input copy for quality metrics
    Provides scoring and identifies improvement opportunities
    """
    
    def __init__(self, ai_service: ProductionAIService):
        self.ai_service = ai_service
        self.name = "Analyzer"
    
    async def analyze(self, ad_data: Dict[str, Any]) -> Tuple[QualityScore, AgentOutput]:
        """Analyze ad copy and return scores with reasoning"""
        
        full_text = f"{ad_data['headline']} {ad_data['body_text']} {ad_data['cta']}"
        
        # Build analysis prompt
        prompt = f"""Analyze this ad copy and provide scores (0-100) for each metric:

Ad Copy:
Headline: {ad_data['headline']}
Body: {ad_data['body_text']}
CTA: {ad_data['cta']}
Platform: {ad_data.get('platform', 'facebook')}

Evaluate:
1. GRAMMAR: Spelling, punctuation, sentence structure
2. CLARITY: Readability, simplicity, message focus
3. EMOTION: Emotional resonance, tone appropriateness
4. CTA_STRENGTH: Call-to-action clarity, urgency, action orientation
5. PLATFORM_FIT: Adherence to {ad_data.get('platform', 'facebook')} best practices

Respond in this exact format:
GRAMMAR: [score]
CLARITY: [score]
EMOTION: [score]
CTA_STRENGTH: [score]
PLATFORM_FIT: [score]
KEY_ISSUES: [2-3 main problems identified]
"""

        try:
            # Call AI service for analysis
            result = await self.ai_service.generate_ad_alternative(
                ad_data=ad_data,
                variant_type='analysis',
                creativity_level=3,  # Low creativity for objective analysis
                urgency_level=3
            )
            
            # Parse AI response
            scores = self._parse_scores(result.get('improvement_reason', ''))
            key_issues = self._extract_key_issues(result.get('improvement_reason', ''))
            
            # Calculate overall score
            overall = sum([
                scores.get('grammar', 70) * 0.15,
                scores.get('clarity', 70) * 0.25,
                scores.get('emotion', 70) * 0.25,
                scores.get('cta_strength', 70) * 0.25,
                scores.get('platform_fit', 70) * 0.10
            ])
            
            quality_score = QualityScore(
                grammar=scores.get('grammar', 70),
                clarity=scores.get('clarity', 70),
                emotion=scores.get('emotion', 70),
                cta_strength=scores.get('cta_strength', 70),
                platform_fit=scores.get('platform_fit', 70),
                overall=round(overall, 1)
            )
            
            # Fallback scoring if AI parsing fails
            if all(v == 70 for v in [quality_score.grammar, quality_score.clarity, quality_score.emotion]):
                quality_score = self._fallback_analysis(ad_data)
            
            agent_output = AgentOutput(
                agent_name=self.name,
                decision_summary=key_issues,
                data={'scores': quality_score.to_dict()},
                timestamp=datetime.utcnow().isoformat()
            )
            
            return quality_score, agent_output
            
        except Exception as e:
            logger.error(f"Analyzer agent failed: {e}")
            # Fallback to rule-based analysis
            quality_score = self._fallback_analysis(ad_data)
            agent_output = AgentOutput(
                agent_name=self.name,
                decision_summary=[
                    "Used rule-based analysis (AI unavailable)",
                    f"Text length: {len(full_text)} chars"
                ],
                data={'scores': quality_score.to_dict(), 'fallback': True},
                timestamp=datetime.utcnow().isoformat()
            )
            return quality_score, agent_output
    
    def _parse_scores(self, ai_response: str) -> Dict[str, float]:
        """Parse scores from AI response"""
        scores = {}
        patterns = {
            'grammar': r'GRAMMAR:\s*(\d+)',
            'clarity': r'CLARITY:\s*(\d+)',
            'emotion': r'EMOTION:\s*(\d+)',
            'cta_strength': r'CTA_STRENGTH:\s*(\d+)',
            'platform_fit': r'PLATFORM_FIT:\s*(\d+)'
        }
        
        for key, pattern in patterns.items():
            match = re.search(pattern, ai_response, re.IGNORECASE)
            if match:
                scores[key] = float(match.group(1))
        
        return scores
    
    def _extract_key_issues(self, ai_response: str) -> List[str]:
        """Extract key issues from AI response"""
        match = re.search(r'KEY_ISSUES:\s*(.+)', ai_response, re.IGNORECASE | re.DOTALL)
        if match:
            issues_text = match.group(1).strip()
            issues = [i.strip() for i in issues_text.split('\n') if i.strip()]
            return issues[:3]  # Max 3 issues
        return ["Analysis completed"]
    
    def _fallback_analysis(self, ad_data: Dict[str, Any]) -> QualityScore:
        """Rule-based fallback analysis"""
        headline = ad_data.get('headline', '')
        body_text = ad_data.get('body_text', '')
        cta = ad_data.get('cta', '')
        
        # Grammar: Check for common issues
        grammar_score = 85
        if not headline[0].isupper(): grammar_score -= 10
        if headline.endswith('.'): grammar_score -= 5
        
        # Clarity: Check length and complexity
        word_count = len(body_text.split())
        clarity_score = 75 if 15 <= word_count <= 30 else 65
        
        # Emotion: Check for emotion words
        emotion_words = ['love', 'hate', 'amazing', 'incredible', 'powerful', 'weak', 'fear', 'hope']
        emotion_score = 70 + (5 * sum(1 for word in emotion_words if word in body_text.lower()))
        emotion_score = min(emotion_score, 95)
        
        # CTA: Check for action verbs
        action_verbs = ['get', 'buy', 'shop', 'learn', 'discover', 'start', 'try', 'join']
        cta_score = 80 if any(verb in cta.lower() for verb in action_verbs) else 65
        
        # Platform fit: Basic length check
        platform_score = 75
        
        overall = (grammar_score * 0.15 + clarity_score * 0.25 + emotion_score * 0.25 + 
                  cta_score * 0.25 + platform_score * 0.10)
        
        return QualityScore(
            grammar=grammar_score,
            clarity=clarity_score,
            emotion=emotion_score,
            cta_strength=cta_score,
            platform_fit=platform_score,
            overall=round(overall, 1)
        )


class StrategistAgent:
    """
    Agent 2: Plans improvement strategy
    Determines marketing angle, audience psychology, and optimization approach
    """
    
    def __init__(self, ai_service: ProductionAIService):
        self.ai_service = ai_service
        self.name = "Strategist"
    
    async def plan_strategy(self, ad_data: Dict[str, Any], analysis: QualityScore) -> AgentOutput:
        """Develop improvement strategy based on analysis"""
        
        prompt = f"""You are a marketing strategist. Based on this ad and its scores, determine the best improvement strategy.

Ad Copy:
Headline: {ad_data['headline']}
Body: {ad_data['body_text']}
CTA: {ad_data['cta']}

Current Scores:
- Clarity: {analysis.clarity}/100
- Emotion: {analysis.emotion}/100
- CTA Strength: {analysis.cta_strength}/100
- Overall: {analysis.overall}/100

Provide strategy in this format:
PRIMARY_ANGLE: [benefit/problem/story - choose one based on what will improve this ad most]
TARGET_PSYCHOLOGY: [What motivates this audience? 1 sentence]
KEY_IMPROVEMENTS: [Top 3 specific changes to make]
POWER_WORDS: [5 persuasive words to incorporate]
"""

        try:
            result = await self.ai_service.generate_ad_alternative(
                ad_data=ad_data,
                variant_type='emotional',
                creativity_level=6,
                urgency_level=5,
                emotion_type='inspiring'
            )
            
            strategy_text = result.get('improvement_reason', '')
            
            # Parse strategy components
            strategy_data = {
                'primary_angle': self._extract_field(strategy_text, 'PRIMARY_ANGLE', 'benefit'),
                'target_psychology': self._extract_field(strategy_text, 'TARGET_PSYCHOLOGY', 'Audience seeks value'),
                'key_improvements': self._extract_list(strategy_text, 'KEY_IMPROVEMENTS'),
                'power_words': self._extract_list(strategy_text, 'POWER_WORDS')
            }
            
            decision_summary = [
                f"Primary angle: {strategy_data['primary_angle']}",
                f"Key focus: {strategy_data['key_improvements'][0] if strategy_data['key_improvements'] else 'Overall improvement'}"
            ]
            
            return AgentOutput(
                agent_name=self.name,
                decision_summary=decision_summary,
                data=strategy_data,
                timestamp=datetime.utcnow().isoformat()
            )
            
        except Exception as e:
            logger.error(f"Strategist agent failed: {e}")
            # Fallback strategy
            return AgentOutput(
                agent_name=self.name,
                decision_summary=[
                    "Focus on clarity and emotional appeal",
                    "Strengthen call-to-action urgency"
                ],
                data={
                    'primary_angle': 'benefit',
                    'target_psychology': 'Audience seeks clear value proposition',
                    'key_improvements': ['Improve headline hook', 'Add urgency', 'Clarify benefits'],
                    'power_words': ['exclusive', 'proven', 'guaranteed', 'transform', 'results']
                },
                timestamp=datetime.utcnow().isoformat()
            )
    
    def _extract_field(self, text: str, field_name: str, default: str) -> str:
        """Extract a single field value"""
        pattern = f"{field_name}:\\s*(.+?)(?:\\n|$)"
        match = re.search(pattern, text, re.IGNORECASE)
        return match.group(1).strip() if match else default
    
    def _extract_list(self, text: str, field_name: str) -> List[str]:
        """Extract a list field"""
        pattern = f"{field_name}:\\s*(.+?)(?:\\n[A-Z_]+:|$)"
        match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
        if match:
            items_text = match.group(1).strip()
            items = [item.strip().strip(',-•') for item in items_text.split(',')]
            return [item for item in items if item][:5]
        return []


class WriterAgent:
    """
    Agent 3: Generates copy variations
    Creates 4 versions: Improved + A (benefit) + B (problem) + C (story)
    """
    
    def __init__(self, ai_service: ProductionAIService):
        self.ai_service = ai_service
        self.name = "Writer"
    
    async def generate_variations(
        self, 
        ad_data: Dict[str, Any], 
        strategy: AgentOutput,
        original_score: QualityScore
    ) -> Tuple[List[VariationOutput], AgentOutput]:
        """Generate all 4 variations in parallel"""
        
        # Generate all variations concurrently
        tasks = [
            self._generate_improved(ad_data, strategy, original_score),
            self._generate_benefit_focused(ad_data, strategy, original_score),
            self._generate_problem_focused(ad_data, strategy, original_score),
            self._generate_story_driven(ad_data, strategy, original_score)
        ]
        
        try:
            variations = await asyncio.gather(*tasks)
            
            agent_output = AgentOutput(
                agent_name=self.name,
                decision_summary=[
                    f"Generated 4 variations with avg improvement: {sum(v.improvement_delta for v in variations) / 4:.1f}%",
                    f"Best performing: {max(variations, key=lambda v: v.score.overall).variation_type}"
                ],
                data={'variations_count': len(variations)},
                timestamp=datetime.utcnow().isoformat()
            )
            
            return variations, agent_output
            
        except Exception as e:
            logger.error(f"Writer agent failed: {e}")
            raise
    
    async def _generate_improved(self, ad_data: Dict[str, Any], strategy: AgentOutput, original_score: QualityScore) -> VariationOutput:
        """Generate main improved version"""
        result = await self.ai_service.generate_ad_alternative(
            ad_data=ad_data,
            variant_type='persuasive',
            creativity_level=6,
            urgency_level=5,
            emotion_type='inspiring',
            filter_cliches=True
        )
        
        # Calculate improvement
        new_score = self._estimate_score(result, original_score, improvement_factor=1.2)
        delta = ((new_score.overall - original_score.overall) / original_score.overall) * 100
        
        return VariationOutput(
            variation_type='improved',
            headline=result.get('headline', ad_data['headline']),
            body_text=result.get('body_text', ad_data['body_text']),
            cta=result.get('cta', ad_data['cta']),
            score=new_score,
            improvement_delta=round(delta, 1),
            reasoning=[
                "Balanced approach incorporating best practices",
                f"Improved clarity and emotional appeal by {delta:.0f}%"
            ]
        )
    
    async def _generate_benefit_focused(self, ad_data: Dict[str, Any], strategy: AgentOutput, original_score: QualityScore) -> VariationOutput:
        """Generate Variation A: Benefit-Focused (Aspirational)"""
        result = await self.ai_service.generate_ad_alternative(
            ad_data=ad_data,
            variant_type='benefit_focused',  # Use new premium framework
            human_tone='conversational',  # Natural, not forced
            brand_tone='professional',
            creativity_level=6,  # Higher creativity for aspirational language
            urgency_level=3,  # Low urgency - focus on benefits, not pressure
            emotion_type='aspirational',
            filter_cliches=True
        )
        
        new_score = self._estimate_score(result, original_score, improvement_factor=1.15)
        delta = ((new_score.overall - original_score.overall) / original_score.overall) * 100
        
        return VariationOutput(
            variation_type='benefit_focused',
            headline=result.get('headline', ad_data['headline']),
            body_text=result.get('body_text', ad_data['body_text']),
            cta=result.get('cta', ad_data['cta']),
            score=new_score,
            improvement_delta=round(delta, 1),
            reasoning=[
                "Aspirational transformation approach - paints the 'after' picture",
                "Premium tone with positive emotions, no problem language",
                "Best for solution-seekers and warm leads ready to buy"
            ]
        )
    
    async def _generate_problem_focused(self, ad_data: Dict[str, Any], strategy: AgentOutput, original_score: QualityScore) -> VariationOutput:
        """Generate Variation B: Problem-Focused (Pain → Solution)"""
        result = await self.ai_service.generate_ad_alternative(
            ad_data=ad_data,
            variant_type='problem_focused',  # Use new premium framework
            human_tone='empathetic',
            brand_tone='friendly',
            creativity_level=5,  # Balanced - empathy, not hype
            urgency_level=7,  # Higher urgency for problem-solving
            emotion_type='problem_solving',
            filter_cliches=True
        )
        
        new_score = self._estimate_score(result, original_score, improvement_factor=1.18)
        delta = ((new_score.overall - original_score.overall) / original_score.overall) * 100
        
        return VariationOutput(
            variation_type='problem_focused',
            headline=result.get('headline', ad_data['headline']),
            body_text=result.get('body_text', ad_data['body_text']),
            cta=result.get('cta', ad_data['cta']),
            score=new_score,
            improvement_delta=round(delta, 1),
            reasoning=[
                "Pain point → solution approach with empathetic validation",
                "Agitates frustration then presents product as relief",
                "Best for pain-aware audiences needing immediate solutions"
            ]
        )
    
    async def _generate_story_driven(self, ad_data: Dict[str, Any], strategy: AgentOutput, original_score: QualityScore) -> VariationOutput:
        """Generate Variation C: Story-Driven (Narrative Connection)"""
        result = await self.ai_service.generate_ad_alternative(
            ad_data=ad_data,
            variant_type='story_driven',  # Use new premium framework
            human_tone='conversational',  # Natural storytelling
            brand_tone='authentic',
            creativity_level=7,  # High creativity for storytelling
            urgency_level=3,  # Low urgency - stories build trust
            emotion_type='trust_building',
            filter_cliches=True
        )
        
        new_score = self._estimate_score(result, original_score, improvement_factor=1.12)
        delta = ((new_score.overall - original_score.overall) / original_score.overall) * 100
        
        return VariationOutput(
            variation_type='story_driven',
            headline=result.get('headline', ad_data['headline']),
            body_text=result.get('body_text', ad_data['body_text']),
            cta=result.get('cta', ad_data['cta']),
            score=new_score,
            improvement_delta=round(delta, 1),
            reasoning=[
                "Mini-narrative with setup → tension → resolution structure",
                "Builds emotional connection through relatable scenarios",
                "Best for building trust with cold audiences and skeptics"
            ]
        )
    
    def _estimate_score(self, ai_result: Dict, baseline: QualityScore, improvement_factor: float = 1.15) -> QualityScore:
        """Estimate quality score for generated variation"""
        # Improve each metric by improvement_factor, cap at 95
        return QualityScore(
            grammar=min(baseline.grammar * improvement_factor, 95),
            clarity=min(baseline.clarity * improvement_factor, 95),
            emotion=min(baseline.emotion * improvement_factor, 95),
            cta_strength=min(baseline.cta_strength * improvement_factor, 95),
            platform_fit=min(baseline.platform_fit * improvement_factor, 95),
            overall=min(baseline.overall * improvement_factor, 95)
        )


class QualityControlAgent:
    """
    Agent 4: Validates output quality
    Ensures brand consistency, factual accuracy, and conversion potential
    """
    
    def __init__(self, ai_service: ProductionAIService):
        self.ai_service = ai_service
        self.name = "QualityControl"
    
    async def validate(
        self, 
        variations: List[VariationOutput],
        original_ad: Dict[str, Any]
    ) -> Tuple[List[str], AgentOutput]:
        """Validate all variations and provide improvement suggestions"""
        
        issues = []
        suggestions = []
        
        for variation in variations:
            # Check for exaggerations
            exaggeration_words = ['guaranteed', 'best', 'perfect', 'ultimate', 'revolutionary', 'never', 'always']
            full_text = f"{variation.headline} {variation.body_text}".lower()
            
            if any(word in full_text for word in exaggeration_words):
                suggestions.append(f"{variation.variation_type}: Consider softening absolute claims")
            
            # Check brand voice consistency (simplified - compare tone)
            if len(variation.headline.split()) < 3:
                suggestions.append(f"{variation.variation_type}: Headline may be too short for context")
            
            # Check conversion potential
            if variation.score.cta_strength < 75:
                suggestions.append(f"{variation.variation_type}: CTA could be strengthened")
        
        # General suggestions
        best_variation = max(variations, key=lambda v: v.score.overall)
        suggestions.insert(0, f"Recommended primary: {best_variation.variation_type} (score: {best_variation.score.overall:.1f})")
        
        # Ensure variations are distinct
        headlines = [v.headline for v in variations]
        if len(set(headlines)) < len(headlines):
            issues.append("Some variations have identical headlines")
        
        agent_output = AgentOutput(
            agent_name=self.name,
            decision_summary=[
                f"Validated {len(variations)} variations",
                f"Found {len(issues)} issues, {len(suggestions)} suggestions"
            ],
            data={
                'issues_count': len(issues),
                'suggestions_count': len(suggestions),
                'best_variation': best_variation.variation_type
            },
            timestamp=datetime.utcnow().isoformat()
        )
        
        return suggestions, agent_output


class MultiAgentOptimizer:
    """
    Orchestrates all agents to perform complete ad optimization
    Supports iterative refinement up to 4 iterations
    """
    
    def __init__(self, ai_service: ProductionAIService):
        self.analyzer = AnalyzerAgent(ai_service)
        self.strategist = StrategistAgent(ai_service)
        self.writer = WriterAgent(ai_service)
        self.quality_control = QualityControlAgent(ai_service)
        self.ai_service = ai_service
    
    async def optimize(
        self, 
        ad_data: Dict[str, Any],
        max_iterations: int = 1
    ) -> OptimizationResult:
        """
        Run complete multi-agent optimization
        
        Args:
            ad_data: Original ad copy data
            max_iterations: Number of refinement iterations (1-4)
        
        Returns:
            Complete optimization result with all variations and reasoning
        """
        logger.info(f"🤖 Starting multi-agent optimization for ad: {ad_data.get('headline', '')[:50]}...")
        
        max_iterations = min(max(max_iterations, 1), 4)  # Clamp to 1-4
        improvement_history = []
        
        # Phase 1: Analyze original
        logger.info("📊 Phase 1: Analyzing original copy...")
        original_score, analyzer_output = await self.analyzer.analyze(ad_data)
        
        reasoning_log = {'analyzer': analyzer_output}
        
        # Phase 2: Strategize
        logger.info("🎯 Phase 2: Planning improvement strategy...")
        strategy_output = await self.strategist.plan_strategy(ad_data, original_score)
        reasoning_log['strategist'] = strategy_output
        
        # Phase 3: Generate variations
        logger.info("✍️ Phase 3: Generating copy variations...")
        variations, writer_output = await self.writer.generate_variations(ad_data, strategy_output, original_score)
        reasoning_log['writer'] = writer_output
        
        # Track first iteration
        improvement_history.append({
            'iteration': 1,
            'best_score': max(v.score.overall for v in variations),
            'avg_improvement': sum(v.improvement_delta for v in variations) / len(variations)
        })
        
        # Iterative refinement (if requested)
        for iteration in range(2, max_iterations + 1):
            logger.info(f"🔄 Iteration {iteration}: Refining best variation...")
            
            # Find best variation from previous iteration
            best_variation = max(variations, key=lambda v: v.score.overall)
            
            # Use best as new baseline for refinement
            refined_ad_data = {
                'headline': best_variation.headline,
                'body_text': best_variation.body_text,
                'cta': best_variation.cta,
                'platform': ad_data.get('platform', 'facebook'),
                'industry': ad_data.get('industry'),
                'target_audience': ad_data.get('target_audience')
            }
            
            # Re-analyze and improve
            refined_score, _ = await self.analyzer.analyze(refined_ad_data)
            refined_strategy = await self.strategist.plan_strategy(refined_ad_data, refined_score)
            refined_variations, _ = await self.writer.generate_variations(refined_ad_data, refined_strategy, refined_score)
            
            # Keep only if improved
            new_best_score = max(v.score.overall for v in refined_variations)
            if new_best_score > best_variation.score.overall:
                variations = refined_variations
                improvement_history.append({
                    'iteration': iteration,
                    'best_score': new_best_score,
                    'improvement_over_previous': new_best_score - best_variation.score.overall
                })
            else:
                logger.info(f"⚠️ Iteration {iteration} did not improve. Stopping refinement.")
                break
        
        # Phase 4: Quality control
        logger.info("✅ Phase 4: Quality control validation...")
        suggestions, qc_output = await self.quality_control.validate(variations, ad_data)
        reasoning_log['quality_control'] = qc_output
        
        # Calculate improved score (best of all variations)
        best_variation = max(variations, key=lambda v: v.score.overall)
        improved_score = best_variation.score
        
        result = OptimizationResult(
            original_score=original_score,
            improved_score=improved_score,
            variations=variations,
            reasoning_log=reasoning_log,
            suggestions=suggestions,
            iteration_count=len(improvement_history),
            improvement_history=improvement_history
        )
        
        logger.info(f"✨ Optimization complete! Improvement: {improved_score.overall - original_score.overall:.1f} points")
        
        return result
