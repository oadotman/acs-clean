#!/usr/bin/env python3
"""
Ad Content Extractor

Extracts core offer details from ad copy to ensure variants are specific and relevant.
This prevents generic "solution" variants that don't mention the actual product/offer.
"""

import re
from typing import Dict, List, Optional
from dataclasses import dataclass

@dataclass
class AdOfferDetails:
    """Extracted details from the original ad"""
    main_offer: str = ""  # e.g., "50% off", "free trial", "buy 2 get 1"
    product_service: str = ""  # e.g., "all products", "software", "shoes"
    urgency_factor: str = ""  # e.g., "today only", "limited time", "ends midnight"
    price_mention: str = ""  # e.g., "$19.99", "starting at $50", "under $100"
    unique_value: str = ""  # e.g., "free shipping", "money back guarantee", "exclusive"
    action_keywords: List[str] = None  # e.g., ["shop", "buy", "get", "save"]
    
    def __post_init__(self):
        if self.action_keywords is None:
            self.action_keywords = []

def extract_offer_details(ad_copy: str) -> AdOfferDetails:
    """
    Extract specific offer details from ad copy to ensure variants stay relevant
    """
    ad_copy_lower = ad_copy.lower()
    details = AdOfferDetails()
    
    # Extract discount/offer patterns
    discount_patterns = [
        r'(\d+%?\s*off)',  # "50% off", "20 off"
        r'(save\s+\$?\d+)',  # "save $50", "save 20"
        r'(half\s+price)',  # "half price"
        r'(buy\s+\d+\s+get\s+\d+)',  # "buy 2 get 1"
        r'(free\s+\w+)',  # "free shipping", "free trial"
        r'(\$\d+[\.\d]*\s*off)',  # "$20 off", "$5.99 off"
        r'(up\s+to\s+\d+%?\s*off)',  # "up to 50% off"
        r'(starting\s+at\s+\$\d+)',  # "starting at $19"
    ]
    
    for pattern in discount_patterns:
        match = re.search(pattern, ad_copy_lower)
        if match:
            details.main_offer = match.group(1).strip()
            break
    
    # If no discount found, look for other offer types
    if not details.main_offer:
        offer_patterns = [
            r'(free)',
            r'(exclusive)',
            r'(limited\s+edition)',
            r'(premium)',
            r'(new\s+\w+)',
        ]
        
        for pattern in offer_patterns:
            match = re.search(pattern, ad_copy_lower)
            if match:
                details.main_offer = match.group(1).strip()
                break
    
    # Extract product/service mentions
    product_patterns = [
        r'(all\s+products?)',  # "all products"
        r'(everything)',  # "everything" 
        r'(entire\s+\w+)',  # "entire store", "entire collection"
        r'(shoes?)',  # "shoes", "shoe"
        r'(clothing)',  # "clothing"
        r'(software)',  # "software"
        r'(service)',  # "service" 
        r'(subscription)',  # "subscription"
        r'(course)',  # "course"
        r'(book)',  # "book"
        r'(app)',  # "app"
        r'(tool)',  # "tool"
        r'(solution)',  # "solution" - but we want to be more specific
        r'(items?)',  # "items", "item"
    ]
    
    for pattern in product_patterns:
        match = re.search(pattern, ad_copy_lower)
        if match:
            details.product_service = match.group(1).strip()
            break
    
    # Extract urgency factors
    urgency_patterns = [
        r'(today\s+only)',  # "today only"
        r'(limited\s+time)',  # "limited time"
        r'(ends\s+\w+)',  # "ends tonight", "ends today"
        r'(expires\s+\w+)',  # "expires soon"
        r'(while\s+supplies\s+last)',  # "while supplies last"
        r'(24\s+hours?)',  # "24 hours", "24 hour"
        r'(this\s+week\s+only)',  # "this week only"
        r'(don\'t\s+wait)',  # "don't wait"
        r'(hurry)',  # "hurry"
        r'(act\s+now)',  # "act now"
        r'(now\s+or\s+never)',  # "now or never"
    ]
    
    for pattern in urgency_patterns:
        match = re.search(pattern, ad_copy_lower)
        if match:
            details.urgency_factor = match.group(1).strip()
            break
    
    # Extract price mentions
    price_patterns = [
        r'(\$\d+[\.\d]*)',  # "$19.99", "$50"
        r'(under\s+\$\d+)',  # "under $100"
        r'(starting\s+at\s+\$\d+)',  # "starting at $50"
        r'(only\s+\$\d+)',  # "only $19"
        r'(just\s+\$\d+)',  # "just $29"
    ]
    
    for pattern in price_patterns:
        match = re.search(pattern, ad_copy_lower)
        if match:
            details.price_mention = match.group(1).strip()
            break
    
    # Extract unique value props
    value_patterns = [
        r'(free\s+shipping)',  # "free shipping"
        r'(money\s+back\s+guarantee)',  # "money back guarantee"
        r'(no\s+risk)',  # "no risk"
        r'(satisfaction\s+guaranteed)',  # "satisfaction guaranteed"
        r'(lifetime\s+\w+)',  # "lifetime warranty", "lifetime access"
        r'(exclusive)',  # "exclusive"
        r'(premium)',  # "premium"
        r'(professional)',  # "professional"
    ]
    
    for pattern in value_patterns:
        match = re.search(pattern, ad_copy_lower)
        if match:
            details.unique_value = match.group(1).strip()
            break
    
    # Extract action keywords
    action_words = ['shop', 'buy', 'get', 'save', 'order', 'purchase', 'grab', 'claim', 'start', 'join', 'try']
    details.action_keywords = [word for word in action_words if word in ad_copy_lower]
    
    return details

def validate_variant_specificity(variant_text: str, offer_details: AdOfferDetails) -> List[str]:
    """
    Validate that variant mentions specific offer details, not generic placeholders
    """
    issues = []
    variant_lower = variant_text.lower()
    
    # Check if main offer is mentioned
    if offer_details.main_offer:
        # Look for the offer or related terms
        offer_mentioned = False
        
        if offer_details.main_offer in variant_lower:
            offer_mentioned = True
        else:
            # Check for equivalent terms
            if 'off' in offer_details.main_offer and ('sale' in variant_lower or 'discount' in variant_lower or 'save' in variant_lower):
                offer_mentioned = True
            elif 'free' in offer_details.main_offer and 'free' in variant_lower:
                offer_mentioned = True
        
        if not offer_mentioned:
            issues.append(f"Variant doesn't mention main offer: '{offer_details.main_offer}'")
    
    # Check if product/service is mentioned specifically
    if offer_details.product_service:
        if offer_details.product_service not in variant_lower:
            # Check for synonyms
            synonyms = {
                'all products': ['everything', 'all items', 'entire store'],
                'software': ['app', 'tool', 'platform', 'system'],
                'shoes': ['footwear', 'sneakers', 'boots']
            }
            
            synonym_mentioned = False
            for synonym_list in synonyms.get(offer_details.product_service, []):
                if any(syn in variant_lower for syn in synonym_list):
                    synonym_mentioned = True
                    break
            
            if not synonym_mentioned:
                issues.append(f"Variant doesn't mention product: '{offer_details.product_service}'")
    
    # Check for generic placeholder phrases that should be avoided
    generic_phrases = [
        'this solution',
        'the transformation', 
        'finally works',
        'trust this',
        'incredible results',
        'game changer',
        'life changing',
        'revolutionary',
        'amazing product',
        'our service',
        'this offer' # Too vague
    ]
    
    # Check for context drift - wrong product categories
    context_drift_phrases = [
        'skin', 'acne', 'skincare', 'complexion',
        'fitness', 'workout', 'weight loss', 'muscle',
        'software', 'app', 'digital', 'online course',
        'investment', 'trading', 'crypto', 'stocks'
    ]
    
    # Only flag context drift if original ad has a specific product
    if offer_details.product_service:
        original_category = offer_details.product_service.lower()
        
        # If original is about jackets/clothing but variant mentions skincare
        if 'jacket' in original_category or 'clothing' in original_category:
            skincare_terms = ['skin', 'acne', 'face', 'complexion', 'clear']
            if any(term in variant_lower for term in skincare_terms):
                issues.append("Context drift: Original ad about clothing but variant mentions skincare")
        
        # If original is about skincare but variant mentions clothing  
        elif any(term in original_category for term in ['skin', 'beauty', 'face']):
            clothing_terms = ['jacket', 'shirt', 'clothes', 'wear', 'fashion']
            if any(term in variant_lower for term in clothing_terms):
                issues.append("Context drift: Original ad about skincare but variant mentions clothing")
        
        # Generic check for completely unrelated categories
        for drift_phrase in context_drift_phrases:
            if drift_phrase in variant_lower and drift_phrase not in original_category:
                issues.append(f"Possible context drift: Variant mentions '{drift_phrase}' but original is about '{original_category}'")
    
    for phrase in generic_phrases:
        if phrase in variant_lower:
            issues.append(f"Variant uses generic phrase: '{phrase}' - be more specific about the actual offer")
    
    return issues

def create_variant_context(offer_details: AdOfferDetails, platform: str) -> str:
    """
    Create context string for LLM prompt based on extracted offer details
    """
    context_parts = []
    
    if offer_details.main_offer:
        context_parts.append(f"Main Offer: {offer_details.main_offer}")
    
    if offer_details.product_service:
        context_parts.append(f"Product/Service: {offer_details.product_service}")
    
    if offer_details.urgency_factor:
        context_parts.append(f"Urgency: {offer_details.urgency_factor}")
        
    if offer_details.price_mention:
        context_parts.append(f"Price: {offer_details.price_mention}")
        
    if offer_details.unique_value:
        context_parts.append(f"Value Prop: {offer_details.unique_value}")
    
    return " | ".join(context_parts) if context_parts else "General product/service promotion"

# Test function
def test_extractor():
    """Test the offer details extractor"""
    test_cases = [
        "Get 50% off all products today! Limited time offer - shop now and save big.",
        "Free shipping on orders over $50. Buy now!",
        "Try our premium software free for 30 days. No risk, cancel anytime.",
        "Buy 2 get 1 free on all shoes. This week only!",
        "Save $100 on your subscription. Exclusive offer ends midnight."
    ]
    
    for i, ad_copy in enumerate(test_cases, 1):
        print(f"\n--- Test Case {i} ---")
        print(f"Ad Copy: {ad_copy}")
        
        details = extract_offer_details(ad_copy)
        print(f"Main Offer: '{details.main_offer}'")
        print(f"Product/Service: '{details.product_service}'")
        print(f"Urgency: '{details.urgency_factor}'")
        print(f"Price: '{details.price_mention}'")
        print(f"Value Prop: '{details.unique_value}'")
        print(f"Action Keywords: {details.action_keywords}")
        
        context = create_variant_context(details, "facebook")
        print(f"Context for LLM: {context}")

if __name__ == "__main__":
    test_extractor()