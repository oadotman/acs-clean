"""
Text parsing utilities for extracting ad copy components from raw text.
Uses regex patterns and simple NLP to identify headlines, body text, and CTAs.
"""
import re
from typing import List, Dict, Any, Optional, Tuple
import logging

logger = logging.getLogger(__name__)

# Common CTA phrases
CTA_PATTERNS = [
    # Action-oriented
    r'\b(?:get|start|try|download|sign up|join|subscribe|learn|discover|find out|explore|see|view|watch|read)\b[^.!?]*(?:now|today|free|here)?\b',
    r'\b(?:buy|shop|order|purchase|book|reserve|claim|grab)\b[^.!?]*(?:now|today)?\b',
    r'\b(?:call|contact|email|text|chat|visit)\b[^.!?]*(?:now|today|us)?\b',
    # Direct CTAs
    r'\b(?:click here|learn more|read more|find out more|get started|sign up|try free|download|subscribe)\b',
    r'\b(?:shop now|buy now|order now|book now|apply now|register now|join now)\b',
    # Question-based CTAs
    r'\b(?:ready to|want to|need to|looking for|interested in)\b[^.!?]*\?'
]

# Headline indicators
HEADLINE_PATTERNS = [
    r'^(?:headline|title|header|h1|subject):\s*(.+)$',
    r'^(.+)(?:\s*-\s*(?:headline|title|header))?$',
    r'^"([^"]+)"(?:\s*-\s*(?:headline|title))?$',
    r'^\*\*([^*]+)\*\*$',  # Bold markdown
    r'^#{1,3}\s*(.+)$',    # Markdown headers
]

# Body text indicators
BODY_PATTERNS = [
    r'^(?:body|description|content|text|copy):\s*(.+)$',
    r'^(?:desc|description):\s*(.+)$',
]

# CTA indicators
CTA_EXPLICIT_PATTERNS = [
    r'^(?:cta|call to action|button|link|action):\s*(.+)$',
    r'^(?:button text|link text|action text):\s*(.+)$',
]

def clean_text(text: str) -> str:
    """Clean and normalize text."""
    if not text:
        return ""
    
    # Remove extra whitespace and normalize line breaks
    text = re.sub(r'\s+', ' ', text.strip())
    text = re.sub(r'\n+', '\n', text)
    
    # Remove common formatting artifacts
    text = re.sub(r'^[•\-\*\+]\s*', '', text)  # List markers
    text = re.sub(r'^\d+[\.\)]\s*', '', text)  # Numbered lists
    
    return text.strip()

def extract_explicit_fields(text: str) -> Dict[str, Optional[str]]:
    """Extract explicitly labeled fields from text."""
    lines = text.split('\n')
    fields = {'headline': None, 'body_text': None, 'cta': None}
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        # Check for explicit headline patterns
        for pattern in HEADLINE_PATTERNS:
            match = re.search(pattern, line, re.IGNORECASE)
            if match:
                fields['headline'] = clean_text(match.group(1))
                break
        
        # Check for explicit body patterns
        for pattern in BODY_PATTERNS:
            match = re.search(pattern, line, re.IGNORECASE)
            if match:
                fields['body_text'] = clean_text(match.group(1))
                break
        
        # Check for explicit CTA patterns
        for pattern in CTA_EXPLICIT_PATTERNS:
            match = re.search(pattern, line, re.IGNORECASE)
            if match:
                fields['cta'] = clean_text(match.group(1))
                break
    
    return fields

def identify_cta_in_text(text: str) -> Optional[str]:
    """Identify potential CTA text using patterns."""
    # Look for explicit CTA patterns
    for pattern in CTA_PATTERNS:
        matches = re.findall(pattern, text, re.IGNORECASE)
        if matches:
            # Return the first match, cleaned up
            cta = clean_text(matches[0])
            if len(cta) <= 50:  # CTAs are usually short
                return cta
    
    # Look for text in quotes or parentheses that might be CTAs
    quote_matches = re.findall(r'"([^"]+)"', text)
    for match in quote_matches:
        if len(match.split()) <= 5 and any(word in match.lower() for word in ['now', 'free', 'get', 'try', 'start']):
            return clean_text(match)
    
    return None

def split_into_sentences(text: str) -> List[str]:
    """Split text into sentences."""
    # Simple sentence splitting
    sentences = re.split(r'[.!?]+', text)
    return [clean_text(s) for s in sentences if clean_text(s)]

def identify_headline_sentence(sentences: List[str]) -> Optional[str]:
    """Identify the most likely headline from sentences."""
    if not sentences:
        return None
    
    # Score sentences for headline likelihood
    scored_sentences = []
    
    for sentence in sentences:
        score = 0
        words = sentence.split()
        
        # Prefer shorter sentences (headlines are usually concise)
        if 3 <= len(words) <= 15:
            score += 2
        elif len(words) <= 3:
            score += 1
        elif len(words) > 20:
            score -= 2
        
        # Prefer sentences with action words or benefits
        action_words = ['get', 'discover', 'transform', 'boost', 'increase', 'improve', 'save', 'win', 'achieve']
        if any(word in sentence.lower() for word in action_words):
            score += 2
        
        # Prefer sentences with numbers or percentages
        if re.search(r'\d+%?', sentence):
            score += 1
        
        # Prefer sentences that don't end with common body text indicators
        body_indicators = ['because', 'since', 'while', 'although', 'however']
        if any(sentence.lower().endswith(word) for word in body_indicators):
            score -= 1
        
        scored_sentences.append((sentence, score))
    
    # Return the highest scoring sentence
    scored_sentences.sort(key=lambda x: x[1], reverse=True)
    return scored_sentences[0][0] if scored_sentences else None

def parse_single_ad_block(text: str, platform: str = 'facebook') -> Dict[str, Any]:
    """Parse a single block of text into ad components."""
    if not text.strip():
        return None
    
    # First try to extract explicitly labeled fields
    explicit_fields = extract_explicit_fields(text)
    
    # If we found explicit fields, use them
    if any(explicit_fields.values()):
        # Fill in missing fields with intelligent guessing
        remaining_text = text
        
        # Remove explicitly found content from remaining text
        for field, value in explicit_fields.items():
            if value:
                remaining_text = remaining_text.replace(value, '', 1)
        
        # Clean up remaining text
        remaining_text = clean_text(remaining_text)
        remaining_lines = [line.strip() for line in remaining_text.split('\n') if line.strip()]
        
        # Try to fill missing fields from remaining content
        if not explicit_fields['headline'] and remaining_lines:
            sentences = split_into_sentences(' '.join(remaining_lines))
            explicit_fields['headline'] = identify_headline_sentence(sentences)
        
        if not explicit_fields['cta']:
            cta = identify_cta_in_text(remaining_text)
            explicit_fields['cta'] = cta
        
        if not explicit_fields['body_text'] and remaining_lines:
            # Use remaining lines as body text
            body_lines = [line for line in remaining_lines 
                         if line != explicit_fields.get('headline') 
                         and line != explicit_fields.get('cta')]
            if body_lines:
                explicit_fields['body_text'] = ' '.join(body_lines)
        
        return {
            'headline': explicit_fields['headline'] or 'Untitled Ad',
            'body_text': explicit_fields['body_text'] or 'Ad content',
            'cta': explicit_fields['cta'] or 'Learn More',
            'platform': platform,
            'confidence': 'high'
        }
    
    # No explicit fields found - use intelligent parsing
    return parse_unstructured_ad_text(text, platform)

def parse_unstructured_ad_text(text: str, platform: str = 'facebook') -> Dict[str, Any]:
    """Parse unstructured ad text using heuristics."""
    lines = [line.strip() for line in text.split('\n') if line.strip()]
    sentences = split_into_sentences(text)
    
    # Identify CTA first (often at the end)
    cta = identify_cta_in_text(text) or 'Learn More'
    
    # Remove CTA from text for further processing
    text_without_cta = text.replace(cta, '').strip()
    sentences_without_cta = [s for s in sentences if cta not in s]
    
    # Identify headline (usually first line or shortest impactful sentence)
    headline = None
    if lines:
        # Try first line as headline if it's reasonable length
        first_line = clean_text(lines[0])
        if 5 <= len(first_line.split()) <= 15:
            headline = first_line
        else:
            # Try to find best headline sentence
            headline = identify_headline_sentence(sentences_without_cta)
    
    if not headline:
        headline = 'Untitled Ad'
    
    # Remaining text becomes body
    remaining_lines = [line for line in lines if line != headline and cta not in line]
    body_text = ' '.join(remaining_lines) if remaining_lines else 'Ad content'
    
    return {
        'headline': headline,
        'body_text': clean_text(body_text),
        'cta': cta,
        'platform': platform,
        'confidence': 'medium'
    }

def split_text_into_ads(text: str) -> List[str]:
    """Split text into individual ad blocks."""
    # Split on multiple blank lines
    ad_blocks = re.split(r'\n\s*\n\s*\n', text)
    
    if len(ad_blocks) == 1:
        # Try splitting on double line breaks
        ad_blocks = re.split(r'\n\s*\n', text)
    
    if len(ad_blocks) == 1:
        # Try splitting on obvious separators
        separators = [
            r'---+',           # Dashes
            r'={3,}',          # Equal signs
            r'\*{3,}',         # Asterisks
            r'Ad \d+:?',       # "Ad 1:", "Ad 2:", etc.
            r'Advertisement \d+', # "Advertisement 1"
            r'#{2,}\s*\d+',    # "## 1", "### 2", etc.
        ]
        
        for separator in separators:
            blocks = re.split(separator, text, flags=re.IGNORECASE)
            if len(blocks) > 1:
                ad_blocks = blocks
                break
    
    # Clean up blocks
    cleaned_blocks = []
    for block in ad_blocks:
        block = block.strip()
        if len(block) > 20:  # Minimum content threshold
            cleaned_blocks.append(block)
    
    return cleaned_blocks if cleaned_blocks else [text.strip()]

def parse_ad_copy_from_text(text: str, platform: str = 'facebook') -> Dict[str, Any]:
    """
    Main function to parse ad copy from raw text.
    
    Args:
        text: Raw text content
        platform: Target platform for optimization
        
    Returns:
        Dict with parsed ads and metadata
    """
    try:
        if not text.strip():
            return {'ads': [], 'warning': 'No content found'}
        
        # Split text into potential ad blocks
        ad_blocks = split_text_into_ads(text)
        
        parsed_ads = []
        for i, block in enumerate(ad_blocks):
            ad = parse_single_ad_block(block, platform)
            if ad:
                # Add unique ID and source info
                ad['source_index'] = i
                ad['source_text'] = block[:100] + '...' if len(block) > 100 else block
                parsed_ads.append(ad)
        
        if not parsed_ads:
            # Fallback: treat entire text as single ad
            fallback_ad = parse_single_ad_block(text, platform)
            if fallback_ad:
                fallback_ad['confidence'] = 'low'
                fallback_ad['source_index'] = 0
                fallback_ad['source_text'] = text[:100] + '...' if len(text) > 100 else text
                parsed_ads.append(fallback_ad)
        
        warning = None
        if len(parsed_ads) == 1 and len(ad_blocks) > 1:
            warning = f"Detected {len(ad_blocks)} sections but could only parse 1 ad"
        elif any(ad['confidence'] == 'low' for ad in parsed_ads):
            warning = "Some ads were parsed with low confidence - please review"
        
        return {
            'ads': parsed_ads,
            'count': len(parsed_ads),
            'warning': warning
        }
    
    except Exception as e:
        logger.error(f"Error parsing ad copy: {str(e)}")
        return {
            'ads': [],
            'error': str(e),
            'warning': 'Failed to parse ad copy'
        }

class TextParser:
    """Text parser class for API integration."""
    
    def parse_text(self, text: str, platform: str = 'facebook') -> List[Dict[str, Any]]:
        """Parse text and return list of ads."""
        result = parse_ad_copy_from_text(text, platform)
        return result.get('ads', [])
