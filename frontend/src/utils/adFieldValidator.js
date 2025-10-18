/**
 * Smart Ad Field Validator
 * 
 * Validates ad input and prompts users to complete missing required fields
 * instead of throwing errors. Provides intelligent field detection and suggestions.
 */

// Platform-specific field requirements
const PLATFORM_REQUIREMENTS = {
  facebook: {
    required: ['body_text'],
    optional: ['headline', 'cta'],
    limits: { headline: 120, body_text: 125, cta: 50 },
    name: 'Facebook Ads'
  },
  instagram: {
    required: ['body_text'],
    optional: ['headline', 'cta'],
    limits: { headline: 80, body_text: 2200, cta: 30 },
    name: 'Instagram Ads'
  },
  google: {
    required: ['headline', 'body_text'],
    optional: ['cta'],
    limits: { headline: 30, body_text: 90, cta: 20 },
    name: 'Google Ads'
  },
  linkedin: {
    required: ['headline', 'body_text'],
    optional: ['cta'],
    limits: { headline: 70, body_text: 150, cta: 25 },
    name: 'LinkedIn Ads'
  },
  twitter: {
    required: ['body_text'],
    optional: ['headline', 'cta'],
    limits: { headline: 50, body_text: 280, cta: 25 },
    name: 'Twitter/X Ads'
  },
  tiktok: {
    required: ['body_text'],
    optional: ['headline', 'cta'],
    limits: { headline: 100, body_text: 100, cta: 20 },
    name: 'TikTok Ads'
  }
};

/**
 * Smart field detection from pasted text
 */
export function detectAdFields(text, platform = 'facebook') {
  const fields = {
    headline: '',
    body_text: '',
    cta: '',
    detected_fields: [],
    missing_fields: [],
    suggestions: []
  };

  if (!text?.trim()) {
    return {
      ...fields,
      missing_fields: PLATFORM_REQUIREMENTS[platform]?.required || ['body_text'],
      suggestions: ['Please provide ad copy text to analyze']
    };
  }

  // Split text into lines and clean them
  const lines = text.split('\n')
    .map(line => line.trim())
    .filter(line => line.length > 0);

  if (lines.length === 0) {
    return {
      ...fields,
      missing_fields: ['body_text'],
      suggestions: ['Please provide valid ad copy text']
    };
  }

  // Smart field detection logic
  if (lines.length === 1) {
    // Single line - likely the main ad text
    const line = lines[0];
    if (line.length > 100) {
      fields.body_text = line;
      fields.detected_fields.push('body_text');
    } else {
      fields.headline = line;
      fields.detected_fields.push('headline');
    }
  } else if (lines.length === 2) {
    // Two lines - likely headline + body or body + cta
    const [first, second] = lines;
    
    if (first.length <= 120 && second.length > 100) {
      // Short first line + long second line = headline + body
      fields.headline = first;
      fields.body_text = second;
      fields.detected_fields.push('headline', 'body_text');
    } else if (first.length > 100 && second.length <= 50) {
      // Long first line + short second line = body + cta
      fields.body_text = first;
      fields.cta = second;
      fields.detected_fields.push('body_text', 'cta');
    } else {
      // Default: first = headline, second = body
      fields.headline = first;
      fields.body_text = second;
      fields.detected_fields.push('headline', 'body_text');
    }
  } else {
    // Three or more lines - full ad structure
    const [first, ...middle] = lines;
    const last = lines[lines.length - 1];
    
    // First line is usually headline
    if (first.length <= 120) {
      fields.headline = first;
      fields.detected_fields.push('headline');
    }
    
    // Last line is CTA if it's short and action-oriented
    const ctaKeywords = ['learn more', 'sign up', 'get started', 'shop now', 'download', 'try free', 'book now', 'contact us'];
    if (last.length <= 50 && ctaKeywords.some(keyword => last.toLowerCase().includes(keyword))) {
      fields.cta = last;
      fields.detected_fields.push('cta');
      // Body is everything in between
      fields.body_text = lines.slice(fields.headline ? 1 : 0, -1).join(' ');
    } else {
      // All remaining text is body
      fields.body_text = lines.slice(fields.headline ? 1 : 0).join(' ');
    }
    
    if (fields.body_text) {
      fields.detected_fields.push('body_text');
    }
  }

  return fields;
}

/**
 * Validate ad fields against platform requirements
 */
export function validateAdFields(fields, platform = 'facebook') {
  const requirements = PLATFORM_REQUIREMENTS[platform];
  if (!requirements) {
    return {
      isValid: false,
      errors: [`Unsupported platform: ${platform}`],
      warnings: [],
      missing_fields: [],
      suggestions: []
    };
  }

  const errors = [];
  const warnings = [];
  const missing_fields = [];
  const suggestions = [];

  // Check required fields
  requirements.required.forEach(field => {
    if (!fields[field] || !fields[field].trim()) {
      missing_fields.push(field);
      errors.push(`${getFieldDisplayName(field)} is required for ${requirements.name}`);
    }
  });

  // Check field lengths
  Object.keys(requirements.limits).forEach(field => {
    if (fields[field]) {
      const limit = requirements.limits[field];
      const length = fields[field].length;
      
      if (length > limit) {
        errors.push(`${getFieldDisplayName(field)} exceeds ${limit} character limit (${length}/${limit})`);
      } else if (length > limit * 0.8) {
        warnings.push(`${getFieldDisplayName(field)} is approaching character limit (${length}/${limit})`);
      }
    }
  });

  // Generate helpful suggestions
  if (missing_fields.length > 0) {
    suggestions.push(`Complete the missing fields: ${missing_fields.map(getFieldDisplayName).join(', ')}`);
    
    // Platform-specific suggestions
    if (platform === 'google' && missing_fields.includes('headline')) {
      suggestions.push('Google Ads headlines should be concise and include your main keyword');
    }
    if (platform === 'facebook' && missing_fields.includes('cta')) {
      suggestions.push('Facebook ads perform better with clear call-to-action buttons');
    }
    if (missing_fields.includes('body_text')) {
      suggestions.push('Add compelling body text that explains your offer and benefits');
    }
  }

  // Quality suggestions
  if (fields.body_text && fields.body_text.length < 50) {
    suggestions.push('Consider adding more detail to your ad body for better engagement');
  }
  
  if (fields.cta && !containsActionWords(fields.cta)) {
    suggestions.push('Your CTA could be more action-oriented (e.g., "Get Started", "Shop Now", "Learn More")');
  }

  return {
    isValid: errors.length === 0,
    errors,
    warnings,
    missing_fields,
    suggestions,
    platform_name: requirements.name,
    character_limits: requirements.limits
  };
}

/**
 * Generate suggestions for completing missing fields
 */
export function generateFieldSuggestions(detectedFields, platform = 'facebook') {
  const suggestions = {};

  // Generate headline suggestion if missing
  if (!detectedFields.headline && detectedFields.body_text) {
    const bodyWords = detectedFields.body_text.split(' ').slice(0, 8).join(' ');
    suggestions.headline = `${bodyWords}...`.substring(0, 80);
  }

  // Generate CTA suggestion if missing
  if (!detectedFields.cta) {
    const platformCTAs = {
      facebook: 'Learn More',
      google: 'Get Started',
      linkedin: 'Contact Us',
      instagram: 'Shop Now',
      twitter: 'Learn More',
      tiktok: 'Try Now'
    };
    suggestions.cta = platformCTAs[platform] || 'Learn More';
  }

  // Generate body text suggestion if missing
  if (!detectedFields.body_text && detectedFields.headline) {
    suggestions.body_text = `Discover more about ${detectedFields.headline.toLowerCase()}. Experience the benefits and see real results.`;
  }

  return suggestions;
}

/**
 * Create a complete ad object from validated fields
 */
export function createCompleteAd(fields, platform = 'facebook', userSuggestions = {}) {
  const suggestions = generateFieldSuggestions(fields, platform);
  
  return {
    headline: fields.headline || userSuggestions.headline || suggestions.headline || '',
    body_text: fields.body_text || userSuggestions.body_text || suggestions.body_text || '',
    cta: fields.cta || userSuggestions.cta || suggestions.cta || '',
    platform,
    industry: fields.industry || '',
    target_audience: fields.target_audience || ''
  };
}

/**
 * Smart ad text parser that handles various input formats
 */
export function parseAdText(text, platform = 'facebook') {
  // Detect fields from text
  const detectedFields = detectAdFields(text, platform);
  
  // Validate the detected fields
  const validation = validateAdFields(detectedFields, platform);
  
  // Generate suggestions for missing fields
  const suggestions = generateFieldSuggestions(detectedFields, platform);
  
  return {
    detected_fields: detectedFields,
    validation,
    suggestions,
    complete_ad: validation.isValid ? detectedFields : null,
    needs_user_input: !validation.isValid
  };
}

// Helper functions
function getFieldDisplayName(field) {
  const names = {
    headline: 'Headline',
    body_text: 'Body Text',
    cta: 'Call-to-Action',
    target_audience: 'Target Audience',
    industry: 'Industry'
  };
  return names[field] || field;
}

function containsActionWords(text) {
  const actionWords = [
    'get', 'start', 'try', 'buy', 'shop', 'download', 'sign', 'join', 
    'learn', 'discover', 'find', 'book', 'contact', 'call', 'click', 
    'watch', 'see', 'explore', 'claim', 'grab', 'save'
  ];
  return actionWords.some(word => text.toLowerCase().includes(word));
}

export default {
  detectAdFields,
  validateAdFields,
  generateFieldSuggestions,
  createCompleteAd,
  parseAdText,
  PLATFORM_REQUIREMENTS
};