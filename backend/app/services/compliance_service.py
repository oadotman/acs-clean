"""
Compliance validation service for ad copy safety and deliverability.

Integrates banned word checking, readability scoring, and platform-specific
compliance rules to ensure generated ad copy meets all requirements.
"""

import re
from typing import Dict, List, Optional, Set, Tuple
from dataclasses import dataclass, field
from enum import Enum

from app.constants.compliance_rules import (
    ComplianceMode, ComplianceSeverity, get_compliance_config,
    get_platform_rules, is_banned_term, check_excessive_punctuation,
    calculate_caps_percentage, get_compliance_instructions
)
from app.services.readability_service import ReadabilityService, ReadabilityScore

@dataclass
class ComplianceViolation:
    """Individual compliance violation"""
    type: str
    severity: ComplianceSeverity
    message: str
    suggestion: Optional[str] = None
    position: Optional[int] = None  # Character position in text
    word_or_phrase: Optional[str] = None

@dataclass
class ComplianceResult:
    """Complete compliance analysis result"""
    overall_score: float  # 0-100, higher is better
    is_compliant: bool
    violations: List[ComplianceViolation] = field(default_factory=list)
    readability: Optional[ReadabilityScore] = None
    banned_words_found: List[str] = field(default_factory=list)
    excessive_punctuation: List[str] = field(default_factory=list)
    caps_percentage: float = 0.0
    platform_issues: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    requires_disclaimers: List[str] = field(default_factory=list)
    auto_fix_available: bool = False

class ComplianceValidator:
    """Main compliance validation service"""
    
    def __init__(self):
        self.readability_service = ReadabilityService()
        
        # Common word replacements for auto-fixing
        self.spam_word_replacements = {
            "guaranteed": "designed to help",
            "miracle": "effective",
            "amazing": "helpful",
            "incredible": "impressive",
            "revolutionary": "innovative",
            "breakthrough": "advanced",
            "secret": "proven method",
            "click here": "learn more",
            "click now": "get started",
            "act now": "take action",
            "hurry": "don't wait",
            "limited time": "for a short time",
            "instant": "quick",
            "immediate": "fast"
        }
    
    def validate_content(
        self, 
        text: str,
        compliance_mode: ComplianceMode = ComplianceMode.STANDARD,
        platform: str = "facebook",
        custom_banned_words: Optional[Set[str]] = None
    ) -> ComplianceResult:
        """
        Perform comprehensive compliance validation on text content.
        """
        if not text.strip():
            return self._empty_result("No content provided for validation")
        
        violations = []
        recommendations = []
        banned_words_found = []
        
        # Get compliance configuration
        config = get_compliance_config(compliance_mode)
        platform_rules = get_platform_rules(platform)
        
        # 1. Check for banned words
        banned_violations, found_words = self._check_banned_words(
            text, compliance_mode, custom_banned_words
        )
        violations.extend(banned_violations)
        banned_words_found.extend(found_words)
        
        # 2. Check excessive punctuation
        punctuation_violations, punctuation_issues = self._check_punctuation(text)
        violations.extend(punctuation_violations)
        
        # 3. Check capitalization
        caps_percentage = calculate_caps_percentage(text)
        caps_violations = self._check_capitalization(
            caps_percentage, config, platform_rules
        )
        violations.extend(caps_violations)
        
        # 4. Readability analysis
        readability = self.readability_service.analyze_for_ad_copy(text, platform)
        readability_violations = self._check_readability(readability, config)
        violations.extend(readability_violations)
        
        # 5. Platform-specific checks
        platform_violations, platform_issues = self._check_platform_compliance(
            text, platform, platform_rules
        )
        violations.extend(platform_violations)
        
        # 6. Industry-specific requirements
        disclaimer_requirements = self._check_disclaimer_requirements(config)
        
        # Calculate overall compliance score
        overall_score = self._calculate_compliance_score(
            violations, readability, len(text)
        )
        
        # Determine if content is compliant
        is_compliant = (
            overall_score >= 70 and  # Minimum score
            not any(v.severity == ComplianceSeverity.CRITICAL for v in violations) and
            not any(v.severity == ComplianceSeverity.ERROR for v in violations)
        )
        
        # Generate recommendations
        recommendations = self._generate_recommendations(
            violations, readability, compliance_mode, platform
        )
        
        # Check if auto-fix is available
        auto_fix_available = self._can_auto_fix(violations, banned_words_found)
        
        return ComplianceResult(
            overall_score=round(overall_score, 1),
            is_compliant=is_compliant,
            violations=violations,
            readability=readability,
            banned_words_found=banned_words_found,
            excessive_punctuation=punctuation_issues,
            caps_percentage=round(caps_percentage * 100, 1),
            platform_issues=platform_issues,
            recommendations=recommendations,
            requires_disclaimers=disclaimer_requirements,
            auto_fix_available=auto_fix_available
        )
    
    def _check_banned_words(
        self, 
        text: str, 
        compliance_mode: ComplianceMode,
        custom_banned_words: Optional[Set[str]] = None
    ) -> Tuple[List[ComplianceViolation], List[str]]:
        """Check for banned words and phrases"""
        violations = []
        found_words = []
        
        config = get_compliance_config(compliance_mode)
        banned_terms = config.get("banned_terms", set())
        
        # Add custom banned words if provided
        if custom_banned_words:
            banned_terms = banned_terms.union(custom_banned_words)
        
        text_lower = text.lower()
        
        for term in banned_terms:
            if term in text_lower:
                found_words.append(term)
                
                # Determine severity based on compliance mode
                if compliance_mode in [ComplianceMode.HEALTHCARE_SAFE, 
                                     ComplianceMode.FINANCE_SAFE, 
                                     ComplianceMode.LEGAL_SAFE]:
                    severity = ComplianceSeverity.ERROR
                else:
                    severity = ComplianceSeverity.WARNING
                
                # Find position in text
                position = text_lower.find(term)
                
                # Get replacement suggestion if available
                suggestion = self.spam_word_replacements.get(term)
                suggestion_text = f" Consider: '{suggestion}'" if suggestion else ""
                
                violations.append(ComplianceViolation(
                    type="banned_word",
                    severity=severity,
                    message=f"Banned term detected: '{term}'{suggestion_text}",
                    suggestion=suggestion,
                    position=position,
                    word_or_phrase=term
                ))
        
        return violations, found_words
    
    def _check_punctuation(self, text: str) -> Tuple[List[ComplianceViolation], List[str]]:
        """Check for excessive punctuation patterns"""
        violations = []
        punctuation_issues = check_excessive_punctuation(text)
        
        for issue in punctuation_issues:
            violations.append(ComplianceViolation(
                type="excessive_punctuation",
                severity=ComplianceSeverity.WARNING,
                message=issue,
                suggestion="Use single punctuation marks for professional appearance"
            ))
        
        return violations, punctuation_issues
    
    def _check_capitalization(
        self, 
        caps_percentage: float, 
        config: Dict, 
        platform_rules: Dict
    ) -> List[ComplianceViolation]:
        """Check for excessive capitalization"""
        violations = []
        
        max_caps = config.get("max_caps_percentage", 0.2)
        platform_max_caps = platform_rules.get("max_caps_percentage", max_caps)
        
        # Use the stricter limit
        max_allowed = min(max_caps, platform_max_caps)
        
        if caps_percentage > max_allowed:
            severity = ComplianceSeverity.ERROR if caps_percentage > 0.5 else ComplianceSeverity.WARNING
            
            violations.append(ComplianceViolation(
                type="excessive_capitalization",
                severity=severity,
                message=f"Too many capital letters: {caps_percentage*100:.1f}% (max allowed: {max_allowed*100:.1f}%)",
                suggestion="Reduce use of ALL CAPS to avoid appearing spammy"
            ))
        
        return violations
    
    def _check_readability(
        self, 
        readability: ReadabilityScore, 
        config: Dict
    ) -> List[ComplianceViolation]:
        """Check readability requirements"""
        violations = []
        
        min_score = config.get("min_readability_score", 60)
        
        if not readability.is_passing or readability.flesch_score < min_score:
            severity = ComplianceSeverity.WARNING
            if readability.flesch_score < min_score - 20:
                severity = ComplianceSeverity.ERROR
            
            violations.append(ComplianceViolation(
                type="readability",
                severity=severity,
                message=f"Readability score {readability.flesch_score} below target {min_score}",
                suggestion="Simplify language and use shorter sentences"
            ))
        
        return violations
    
    def _check_platform_compliance(
        self, 
        text: str, 
        platform: str, 
        platform_rules: Dict
    ) -> Tuple[List[ComplianceViolation], List[str]]:
        """Check platform-specific compliance rules"""
        violations = []
        issues = []
        
        # Check for before/after claims (Facebook restriction)
        if platform_rules.get("banned_before_after") and "before" in text.lower() and "after" in text.lower():
            violations.append(ComplianceViolation(
                type="platform_violation",
                severity=ComplianceSeverity.ERROR,
                message="Before/after claims not allowed on this platform",
                suggestion="Focus on features and benefits instead of transformation claims"
            ))
            issues.append("Before/after claims detected")
        
        # Check professional language requirement (LinkedIn)
        if platform_rules.get("professional_language_required"):
            informal_words = ["awesome", "cool", "sick", "lit", "fire", "savage"]
            found_informal = [word for word in informal_words if word in text.lower()]
            
            if found_informal:
                violations.append(ComplianceViolation(
                    type="platform_violation",
                    severity=ComplianceSeverity.WARNING,
                    message=f"Informal language detected: {', '.join(found_informal)}",
                    suggestion="Use more professional language for business platform"
                ))
                issues.append("Informal language")
        
        # Check character limits for Twitter
        if platform == "twitter" and len(text) > 280:
            violations.append(ComplianceViolation(
                type="platform_violation",
                severity=ComplianceSeverity.CRITICAL,
                message=f"Content exceeds Twitter's 280 character limit ({len(text)} characters)",
                suggestion="Shorten the message to fit platform requirements"
            ))
            issues.append("Character limit exceeded")
        
        return violations, issues
    
    def _check_disclaimer_requirements(self, config: Dict) -> List[str]:
        """Check if disclaimers are required"""
        if config.get("require_disclaimers", False):
            return config.get("required_disclaimers", [])
        return []
    
    def _calculate_compliance_score(
        self, 
        violations: List[ComplianceViolation], 
        readability: ReadabilityScore,
        text_length: int
    ) -> float:
        """Calculate overall compliance score (0-100)"""
        base_score = 100.0
        
        # Deduct points for violations
        for violation in violations:
            if violation.severity == ComplianceSeverity.CRITICAL:
                base_score -= 25
            elif violation.severity == ComplianceSeverity.ERROR:
                base_score -= 15
            elif violation.severity == ComplianceSeverity.WARNING:
                base_score -= 5
            elif violation.severity == ComplianceSeverity.INFO:
                base_score -= 1
        
        # Readability bonus/penalty
        if readability and readability.is_passing:
            base_score += 5  # Bonus for good readability
        elif readability and readability.flesch_score < 40:
            base_score -= 10  # Extra penalty for very poor readability
        
        # Length consideration (very short or very long content)
        if text_length < 10:
            base_score -= 10  # Too short
        elif text_length > 500:
            base_score -= 5   # Potentially too long for ads
        
        return max(0, min(100, base_score))
    
    def _generate_recommendations(
        self,
        violations: List[ComplianceViolation],
        readability: ReadabilityScore,
        compliance_mode: ComplianceMode,
        platform: str
    ) -> List[str]:
        """Generate actionable recommendations"""
        recommendations = []
        
        # Critical issues first
        critical_violations = [v for v in violations if v.severity == ComplianceSeverity.CRITICAL]
        if critical_violations:
            recommendations.append("🚨 CRITICAL ISSUES MUST BE FIXED:")
            for violation in critical_violations:
                recommendations.append(f"  • {violation.message}")
                if violation.suggestion:
                    recommendations.append(f"    💡 {violation.suggestion}")
        
        # Error-level issues
        error_violations = [v for v in violations if v.severity == ComplianceSeverity.ERROR]
        if error_violations:
            recommendations.append("⚠️ IMPORTANT ISSUES TO FIX:")
            for violation in error_violations:
                recommendations.append(f"  • {violation.message}")
                if violation.suggestion:
                    recommendations.append(f"    💡 {violation.suggestion}")
        
        # Readability recommendations
        if readability and not readability.is_passing:
            recommendations.append("📖 READABILITY IMPROVEMENTS:")
            for rec in readability.recommendations[:3]:  # Top 3 recommendations
                recommendations.append(f"  • {rec}")
        
        # Compliance mode specific advice
        if compliance_mode != ComplianceMode.STANDARD:
            recommendations.append(f"🏥 {compliance_mode.value.upper()} COMPLIANCE:")
            recommendations.append(f"  • Follow strict {compliance_mode.value} guidelines")
            recommendations.append("  • Consider adding appropriate disclaimers")
        
        # Platform-specific advice
        platform_advice = {
            "facebook": "Keep engaging but avoid spam triggers",
            "instagram": "Focus on visual appeal and authentic voice",
            "linkedin": "Maintain professional tone and focus on business value",
            "tiktok": "Use casual, trend-aware language that resonates with younger audiences",
            "twitter": "Be concise and punchy within character limits",
            "google": "Focus on clear value propositions and search intent"
        }
        
        if platform in platform_advice:
            recommendations.append(f"📱 {platform.upper()} PLATFORM:")
            recommendations.append(f"  • {platform_advice[platform]}")
        
        # General best practices
        if not critical_violations and not error_violations:
            recommendations.append("✅ OPTIMIZATION SUGGESTIONS:")
            recommendations.append("  • Test different variations to see what performs best")
            recommendations.append("  • Monitor performance and adjust based on results")
            recommendations.append("  • Consider A/B testing different approaches")
        
        return recommendations
    
    def _can_auto_fix(
        self, 
        violations: List[ComplianceViolation], 
        banned_words: List[str]
    ) -> bool:
        """Determine if content can be automatically fixed"""
        # Can auto-fix if:
        # 1. Only banned word violations that have replacements
        # 2. Only punctuation issues
        # 3. No critical or error-level violations from other sources
        
        auto_fixable_types = {"banned_word", "excessive_punctuation"}
        non_auto_fixable = [
            v for v in violations 
            if v.type not in auto_fixable_types or v.severity == ComplianceSeverity.CRITICAL
        ]
        
        # Check if all banned words have replacements
        replaceable_banned_words = [
            word for word in banned_words 
            if word in self.spam_word_replacements
        ]
        
        return (
            len(non_auto_fixable) == 0 and
            len(replaceable_banned_words) == len(banned_words)
        )
    
    def auto_fix_content(self, text: str, compliance_result: ComplianceResult) -> str:
        """
        Automatically fix common compliance issues where possible.
        """
        if not compliance_result.auto_fix_available:
            return text
        
        fixed_text = text
        
        # Fix banned words
        for word in compliance_result.banned_words_found:
            if word in self.spam_word_replacements:
                replacement = self.spam_word_replacements[word]
                # Case-insensitive replacement
                pattern = re.compile(re.escape(word), re.IGNORECASE)
                fixed_text = pattern.sub(replacement, fixed_text)
        
        # Fix excessive punctuation
        fixed_text = re.sub(r'[!]{2,}', '!', fixed_text)
        fixed_text = re.sub(r'[\?]{2,}', '?', fixed_text)
        fixed_text = re.sub(r'[\.]{4,}', '...', fixed_text)
        
        return fixed_text
    
    def _empty_result(self, message: str) -> ComplianceResult:
        """Return empty compliance result with error message"""
        return ComplianceResult(
            overall_score=0.0,
            is_compliant=False,
            violations=[ComplianceViolation(
                type="validation_error",
                severity=ComplianceSeverity.ERROR,
                message=message
            )],
            recommendations=[message]
        )
    
    def get_compliance_summary(self, result: ComplianceResult) -> Dict[str, any]:
        """Get a summary of compliance results for API responses"""
        return {
            "overall_score": result.overall_score,
            "is_compliant": result.is_compliant,
            "violation_count": len(result.violations),
            "critical_issues": len([v for v in result.violations if v.severity == ComplianceSeverity.CRITICAL]),
            "error_issues": len([v for v in result.violations if v.severity == ComplianceSeverity.ERROR]),
            "warning_issues": len([v for v in result.violations if v.severity == ComplianceSeverity.WARNING]),
            "readability_score": result.readability.flesch_score if result.readability else None,
            "readability_passing": result.readability.is_passing if result.readability else False,
            "banned_words_count": len(result.banned_words_found),
            "caps_percentage": result.caps_percentage,
            "auto_fix_available": result.auto_fix_available,
            "requires_disclaimers": len(result.requires_disclaimers) > 0
        }