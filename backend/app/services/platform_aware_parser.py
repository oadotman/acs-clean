"""
Platform-Aware Ad Parser

Intelligent parsing that understands platform-specific structures and extracts
content appropriately for each platform's requirements.
"""
import re
import logging
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict

from .platform_registry import get_platform_config, resolve_platform_id, PlatformConfig

logger = logging.getLogger(__name__)

@dataclass
class ParsedAd:
    """Parsed ad content structured for a specific platform"""
    platform_id: str
    content: Dict[str, Any]
    parsing_report: Dict[str, Any]
    confidence: str  # high, medium, low

class PlatformAwareParser:
    """Parser that adapts behavior based on target platform"""
    
    def __init__(self):
        self.cta_patterns = [
            r'\b(?:get|start|try|download|sign up|join|subscribe|learn|discover|find out|explore|see|view|watch|read)\b[^.!?]*(?:now|today|free|here)?\b',
            r'\b(?:buy|shop|order|purchase|book|reserve|claim|grab)\b[^.!?]*(?:now|today)?\b',
            r'\b(?:call|contact|email|text|chat|visit)\b[^.!?]*(?:now|today|us)?\b',
            r'\b(?:click here|learn more|read more|find out more|get started|sign up|try free|download|subscribe)\b',
            r'\b(?:shop now|buy now|order now|book now|apply now|register now|join now)\b',
            r'\b(?:ready to|want to|need to|looking for|interested in)\b[^.!?]*\?'
        ]
        
        self.hashtag_pattern = r'#\w+'
    
    def parse_ad(self, text: str, platform_id: str) -> ParsedAd:
        """Parse ad text for specific platform"""
        # Resolve platform ID and get config
        resolved_platform_id = resolve_platform_id(platform_id)
        platform_config = get_platform_config(resolved_platform_id)
        
        if not platform_config:
            logger.error(f"No configuration found for platform: {platform_id}")
            return self._create_fallback_parsed_ad(text, resolved_platform_id)
        
        # Normalize input text
        normalized_text = self._normalize_text(text)
        
        # Parse based on platform type
        if resolved_platform_id == 'facebook':
            return self._parse_facebook(normalized_text, platform_config)
        elif resolved_platform_id == 'instagram':
            return self._parse_instagram(normalized_text, platform_config)
        elif resolved_platform_id == 'google_ads':
            return self._parse_google_ads(normalized_text, platform_config)
        elif resolved_platform_id == 'linkedin':
            return self._parse_linkedin(normalized_text, platform_config)
        elif resolved_platform_id == 'twitter_x':
            return self._parse_twitter_x(normalized_text, platform_config)
        elif resolved_platform_id == 'tiktok':
            return self._parse_tiktok(normalized_text, platform_config)
        else:
            return self._create_fallback_parsed_ad(normalized_text, resolved_platform_id)
    
    def _normalize_text(self, text: str) -> str:
        """Normalize input text"""
        if not text:
            return ""
        
        # Trim whitespace and normalize line breaks
        text = re.sub(r'\s+', ' ', text.strip())
        text = re.sub(r'\n+', '\n', text)
        
        # Remove common formatting artifacts
        text = re.sub(r'^[•\-\*\+]\s*', '', text, flags=re.MULTILINE)
        text = re.sub(r'^\d+[\.\)]\s*', '', text, flags=re.MULTILINE)
        
        return text.strip()
    
    def _split_into_sentences(self, text: str) -> List[str]:
        """Split text into sentences"""
        sentences = re.split(r'[.!?]+', text)
        return [s.strip() for s in sentences if s.strip()]
    
    def _detect_cta(self, text: str, platform_config: PlatformConfig) -> Tuple[Optional[str], float]:
        """Detect CTA in text with confidence score"""
        # First try platform-specific CTA verbs
        platform_cta_patterns = []
        for verb in platform_config.cta_verbs:
            platform_cta_patterns.append(f"\\b{verb}\\b[^.!?]*")
        
        # Check platform-specific patterns first
        for pattern in platform_cta_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                cta = self._clean_cta(matches[0])
                if len(cta) <= 50:  # Reasonable CTA length
                    return cta, 0.9
        
        # Fall back to general patterns
        for pattern in self.cta_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                cta = self._clean_cta(matches[0])
                if len(cta) <= 50:
                    return cta, 0.7
        
        # Look for quoted text that might be CTAs
        quote_matches = re.findall(r'"([^"]+)"', text)
        for match in quote_matches:
            if len(match.split()) <= 5 and any(word in match.lower() for word in ['now', 'free', 'get', 'try', 'start']):
                return self._clean_cta(match), 0.6
        
        return None, 0.0
    
    def _clean_cta(self, cta: str) -> str:
        """Clean and format CTA"""
        cta = cta.strip().strip('"').strip("'")
        cta = re.sub(r'[.!?]+$', '', cta)  # Remove trailing punctuation
        return cta.strip()
    
    def _extract_hashtags(self, text: str, max_count: int = 10) -> List[str]:
        """Extract hashtags from text"""
        hashtags = re.findall(self.hashtag_pattern, text)
        # Deduplicate and limit count
        unique_hashtags = []
        seen = set()
        for tag in hashtags:
            if tag.lower() not in seen and len(unique_hashtags) < max_count:
                unique_hashtags.append(tag)
                seen.add(tag.lower())
        return unique_hashtags
    
    def _smart_trim(self, text: str, max_chars: int, preserve_words: bool = True) -> str:
        """Trim text to character limit without breaking words"""
        if len(text) <= max_chars:
            return text
        
        if not preserve_words:
            return text[:max_chars]
        
        # Find the last space before the limit
        trimmed = text[:max_chars]
        last_space = trimmed.rfind(' ')
        
        if last_space > max_chars * 0.8:  # Only trim at word boundary if it's not too short
            return text[:last_space].strip()
        else:
            return text[:max_chars].strip()
    
    def _parse_facebook(self, text: str, config: PlatformConfig) -> ParsedAd:
        """Parse for Facebook: headline + body + CTA"""
        sentences = self._split_into_sentences(text)
        
        # Detect CTA first (often at the end)
        cta, cta_confidence = self._detect_cta(text, config)
        if not cta:
            cta = "Learn More"  # Default CTA
        
        # Remove CTA from text for further processing
        text_without_cta = text.replace(cta, '').strip() if cta != "Learn More" else text
        sentences_without_cta = [s for s in sentences if cta not in s]
        
        # Identify headline (first sentence or shortest impactful sentence)
        headline = ""
        if sentences_without_cta:
            first_sentence = sentences_without_cta[0]
            if 3 <= len(first_sentence.split()) <= 10:
                headline = first_sentence
            else:
                # Find best headline candidate
                for sentence in sentences_without_cta:
                    words = sentence.split()
                    if 3 <= len(words) <= 10:
                        headline = sentence
                        break
        
        if not headline and sentences:
            headline = sentences[0]  # Fall back to first sentence
        
        headline = self._smart_trim(headline, config.fields['headline'].max_chars)
        
        # Remaining text becomes body
        remaining_sentences = [s for s in sentences_without_cta if s != headline]
        body = ' '.join(remaining_sentences).strip()
        if not body:
            body = text_without_cta
        
        body = self._smart_trim(body, config.fields['body'].max_chars)
        cta = self._smart_trim(cta, config.fields['cta'].max_chars)
        
        content = {
            'headline': headline,
            'body': body,
            'cta': cta
        }
        
        parsing_report = {
            'cta_detected': cta != "Learn More",
            'cta_confidence': cta_confidence,
            'sentences_processed': len(sentences),
            'method': 'facebook_structured'
        }
        
        return ParsedAd(
            platform_id='facebook',
            content=content,
            parsing_report=parsing_report,
            confidence='high' if cta_confidence > 0.7 else 'medium'
        )
    
    def _parse_instagram(self, text: str, config: PlatformConfig) -> ParsedAd:
        """Parse for Instagram: body + hashtags + optional CTA"""
        # Extract hashtags first
        hashtags = self._extract_hashtags(text, config.fields['hashtags'].count)
        
        # Remove hashtags from text
        text_without_hashtags = re.sub(self.hashtag_pattern, '', text).strip()
        
        # Detect CTA
        cta, cta_confidence = self._detect_cta(text_without_hashtags, config)
        
        # Remove CTA from body if found
        if cta:
            text_without_hashtags = text_without_hashtags.replace(cta, '').strip()
        
        # Remaining text is body
        body = self._smart_trim(text_without_hashtags, config.fields['body'].max_chars)
        
        content = {
            'body': body,
            'hashtags': hashtags,
        }
        
        if cta:
            content['cta'] = self._smart_trim(cta, config.fields['cta'].max_chars)
        
        parsing_report = {
            'hashtags_found': len(hashtags),
            'cta_detected': bool(cta),
            'cta_confidence': cta_confidence,
            'hook_length': min(125, len(body)),  # First 125 chars for Instagram hook
            'method': 'instagram_structured'
        }
        
        return ParsedAd(
            platform_id='instagram',
            content=content,
            parsing_report=parsing_report,
            confidence='high' if len(hashtags) >= 3 else 'medium'
        )
    
    def _parse_google_ads(self, text: str, config: PlatformConfig) -> ParsedAd:
        """Parse for Google Ads: 3 unique headlines + 2 descriptions + optional CTA"""
        sentences = self._split_into_sentences(text)
        
        # Extract CTA first
        cta, cta_confidence = self._detect_cta(text, config)
        text_without_cta = text.replace(cta, '').strip() if cta else text
        
        # Try to extract 3 headlines from short phrases
        headlines = []
        headline_candidates = []
        
        # Look for short, punchy phrases
        for sentence in sentences:
            words = sentence.split()
            if 2 <= len(words) <= 5 and len(sentence) <= 30:
                headline_candidates.append(sentence)
        
        # Also look for colon-separated segments
        colon_segments = text_without_cta.split(':')
        for segment in colon_segments:
            segment = segment.strip()
            if 2 <= len(segment.split()) <= 5 and len(segment) <= 30:
                headline_candidates.append(segment)
        
        # Select unique headlines
        seen_headlines = set()
        for candidate in headline_candidates:
            if len(headlines) >= 3:
                break
            if candidate.lower() not in seen_headlines:
                headlines.append(self._smart_trim(candidate, config.fields['headlines'].max_chars))
                seen_headlines.add(candidate.lower())
        
        # Fill remaining headlines with variations if needed
        while len(headlines) < 3:
            base_headline = headlines[0] if headlines else "Professional Service"
            variation = self._create_headline_variation(base_headline, len(headlines))
            if variation.lower() not in seen_headlines:
                headlines.append(variation)
                seen_headlines.add(variation.lower())
            else:
                headlines.append(f"Quality {base_headline}")  # Last resort
        
        # Extract descriptions from longer text
        descriptions = []
        remaining_sentences = [s for s in sentences if s not in headlines and (not cta or cta not in s)]
        
        if remaining_sentences:
            # Split into 2 descriptions
            mid_point = len(remaining_sentences) // 2
            desc1_sentences = remaining_sentences[:mid_point+1]
            desc2_sentences = remaining_sentences[mid_point+1:]
            
            desc1 = ' '.join(desc1_sentences).strip()
            desc2 = ' '.join(desc2_sentences).strip()
            
            if desc1:
                descriptions.append(self._smart_trim(desc1, config.fields['descriptions'].max_chars))
            if desc2:
                descriptions.append(self._smart_trim(desc2, config.fields['descriptions'].max_chars))
        
        # Ensure we have 2 descriptions
        while len(descriptions) < 2:
            base_desc = descriptions[0] if descriptions else text_without_cta
            base_desc = self._smart_trim(base_desc, config.fields['descriptions'].max_chars)
            descriptions.append(base_desc)
        
        content = {
            'headlines': headlines[:3],
            'descriptions': descriptions[:2]
        }
        
        if cta:
            content['cta'] = self._smart_trim(cta, config.fields['cta'].max_chars)
        
        parsing_report = {
            'headlines_extracted': len(headlines),
            'descriptions_extracted': len(descriptions),
            'cta_detected': bool(cta),
            'cta_confidence': cta_confidence,
            'uniqueness_enforced': True,
            'method': 'google_ads_structured'
        }
        
        return ParsedAd(
            platform_id='google_ads',
            content=content,
            parsing_report=parsing_report,
            confidence='medium'  # Google Ads parsing is inherently more complex
        )
    
    def _create_headline_variation(self, base_headline: str, variation_index: int) -> str:
        """Create variations of headlines for Google Ads"""
        if variation_index == 1:
            return f"Best {base_headline}"
        elif variation_index == 2:
            return f"Top {base_headline}"
        else:
            return f"Premium {base_headline}"
    
    def _parse_linkedin(self, text: str, config: PlatformConfig) -> ParsedAd:
        """Parse for LinkedIn: headline + body + CTA (similar to Facebook but longer)"""
        sentences = self._split_into_sentences(text)
        
        # Detect CTA
        cta, cta_confidence = self._detect_cta(text, config)
        if not cta:
            cta = "Learn More"
        
        # Remove CTA from text
        text_without_cta = text.replace(cta, '').strip() if cta != "Learn More" else text
        sentences_without_cta = [s for s in sentences if cta not in s]
        
        # Headline (can be longer for LinkedIn)
        headline = ""
        if sentences_without_cta:
            first_sentence = sentences_without_cta[0]
            if len(first_sentence.split()) <= 15:  # LinkedIn allows longer headlines
                headline = first_sentence
        
        if not headline and sentences:
            headline = sentences[0]
        
        headline = self._smart_trim(headline, config.fields['headline'].max_chars)
        
        # Body (longer for LinkedIn)
        remaining_sentences = [s for s in sentences_without_cta if s != headline]
        body = ' '.join(remaining_sentences).strip()
        if not body:
            body = text_without_cta
        
        body = self._smart_trim(body, config.fields['body'].max_chars)
        cta = self._smart_trim(cta, config.fields['cta'].max_chars)
        
        content = {
            'headline': headline,
            'body': body,
            'cta': cta
        }
        
        parsing_report = {
            'cta_detected': cta != "Learn More",
            'cta_confidence': cta_confidence,
            'sentences_processed': len(sentences),
            'method': 'linkedin_structured'
        }
        
        return ParsedAd(
            platform_id='linkedin',
            content=content,
            parsing_report=parsing_report,
            confidence='high' if cta_confidence > 0.7 else 'medium'
        )
    
    def _parse_twitter_x(self, text: str, config: PlatformConfig) -> ParsedAd:
        """Parse for Twitter/X: single body with embedded CTA"""
        # For Twitter/X, we keep everything as body since CTA is embedded
        body = self._smart_trim(text, config.fields['body'].max_chars)
        
        # Check if CTA is naturally embedded
        cta_detected = any(verb in body.lower() for verb in config.cta_verbs)
        
        content = {
            'body': body
        }
        
        parsing_report = {
            'cta_embedded': cta_detected,
            'char_count': len(body),
            'method': 'twitter_x_simple'
        }
        
        return ParsedAd(
            platform_id='twitter_x',
            content=content,
            parsing_report=parsing_report,
            confidence='high'  # Simple parsing for Twitter
        )
    
    def _parse_tiktok(self, text: str, config: PlatformConfig) -> ParsedAd:
        """Parse for TikTok: short body + CTA"""
        # Detect CTA
        cta, cta_confidence = self._detect_cta(text, config)
        if not cta:
            cta = "Check it out"  # Default Gen-Z style CTA
        
        # Remove CTA from body
        text_without_cta = text.replace(cta, '').strip() if cta != "Check it out" else text
        
        # Short body for TikTok
        body = self._smart_trim(text_without_cta, config.fields['body'].max_chars)
        cta = self._smart_trim(cta, config.fields['cta'].max_chars)
        
        content = {
            'body': body,
            'cta': cta
        }
        
        parsing_report = {
            'cta_detected': cta != "Check it out",
            'cta_confidence': cta_confidence,
            'body_length': len(body),
            'method': 'tiktok_structured'
        }
        
        return ParsedAd(
            platform_id='tiktok',
            content=content,
            parsing_report=parsing_report,
            confidence='high' if len(body) <= 80 else 'medium'
        )
    
    def _create_fallback_parsed_ad(self, text: str, platform_id: str) -> ParsedAd:
        """Create fallback parsed ad when platform config is missing"""
        content = {
            'headline': text[:50] if len(text) > 50 else text,
            'body': text,
            'cta': 'Learn More'
        }
        
        parsing_report = {
            'error': f'No configuration found for platform {platform_id}',
            'method': 'fallback_generic'
        }
        
        return ParsedAd(
            platform_id=platform_id,
            content=content,
            parsing_report=parsing_report,
            confidence='low'
        )

# Convenience function
def parse_ad_for_platform(text: str, platform_id: str) -> ParsedAd:
    """Parse ad text for specific platform"""
    parser = PlatformAwareParser()
    return parser.parse_ad(text, platform_id)