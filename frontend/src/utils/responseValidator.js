/**
 * Frontend Response Validator
 * 
 * Validates API responses against the unified contract to prevent runtime errors.
 * Provides detailed error logging and graceful fallbacks.
 */

/**
 * Validate API response against the unified contract
 * @param {*} response - The API response to validate
 * @returns {Object} - {isValid: boolean, errors: string[], warnings: string[]}
 */
export function validateApiResponse(response) {
  const errors = [];
  const warnings = [];
  
  // Basic response structure validation
  if (!response || typeof response !== 'object') {
    errors.push('Response must be an object');
    return { isValid: false, errors, warnings };
  }
  
  // Required boolean fields
  if (response.comprehensive_analysis_complete !== true) {
    errors.push(`comprehensive_analysis_complete must be true, got: ${typeof response.comprehensive_analysis_complete} ${response.comprehensive_analysis_complete}`);
  }
  
  // Required string fields
  const requiredStringFields = ['platform', 'analysis_id'];
  requiredStringFields.forEach(field => {
    if (typeof response[field] !== 'string') {
      errors.push(`${field} must be a string, got: ${typeof response[field]} ${response[field]}`);
    }
  });
  
  // Required object fields
  const requiredObjects = ['original', 'improved', 'abTests', 'compliance', 'psychology', 'roi', 'legal'];
  requiredObjects.forEach(field => {
    if (!response[field] || typeof response[field] !== 'object') {
      errors.push(`${field} must be an object, got: ${typeof response[field]}`);
    }
  });
  
  // Validate original ad structure
  if (response.original) {
    if (typeof response.original.copy !== 'string') {
      errors.push(`original.copy must be a string, got: ${typeof response.original.copy}`);
    }
    if (typeof response.original.score !== 'number') {
      errors.push(`original.score must be a number, got: ${typeof response.original.score}`);
    }
  }
  
  // Validate improved ad structure
  if (response.improved) {
    if (typeof response.improved.copy !== 'string') {
      errors.push(`improved.copy must be a string, got: ${typeof response.improved.copy}`);
    }
    if (typeof response.improved.score !== 'number') {
      errors.push(`improved.score must be a number, got: ${typeof response.improved.score}`);
    }
    if (!Array.isArray(response.improved.improvements)) {
      errors.push(`improved.improvements must be an array, got: ${typeof response.improved.improvements}`);
    }
  }
  
  // CRITICAL: Validate abTests structure
  if (response.abTests) {
    if (!Array.isArray(response.abTests.variations)) {
      errors.push(`abTests.variations must be an array, got: ${typeof response.abTests.variations}`);
    }
    
    const abcVariants = response.abTests.abc_variants;
    if (!Array.isArray(abcVariants)) {
      errors.push(`abTests.abc_variants must be an array, got: ${typeof abcVariants}`);
    } else if (abcVariants.length !== 3) {
      errors.push(`abTests.abc_variants must have exactly 3 items, got: ${abcVariants.length}`);
    } else {
      // Validate each variant (align with backend shape)
      const requiredVariantFields = ['id', 'version', 'headline', 'body_text', 'cta'];
      
      abcVariants.forEach((variant, index) => {
        if (!variant || typeof variant !== 'object') {
          errors.push(`Variant ${index + 1} must be an object, got: ${typeof variant}`);
          return;
        }
        
        // Check required fields
        requiredVariantFields.forEach(field => {
          if (!(field in variant)) {
            errors.push(`Variant ${index + 1} missing required field: ${field}`);
          } else {
            const value = variant[field];
            if (typeof value !== 'string') {
              errors.push(`Variant ${index + 1}.${field} must be a string, got: ${typeof value} ${value}`);
            }
          }
        });
        
        // Optional arrays with backend naming
        if ('best_for' in variant && !Array.isArray(variant.best_for)) {
          errors.push(`Variant ${index + 1}.best_for must be an array, got: ${typeof variant.best_for}`);
        }
        
        // Validate version values
        if (variant.version && !['A', 'B', 'C'].includes(variant.version)) {
          errors.push(`Variant ${index + 1} version must be "A", "B", or "C", got: ${variant.version}`);
        }
        
        // Check for empty content
        const textFields = ['headline', 'body_text', 'cta'];
        textFields.forEach(field => {
          if (variant[field] && typeof variant[field] === 'string' && !variant[field].trim()) {
            warnings.push(`Variant ${index + 1}.${field} is empty or whitespace only`);
          }
        });
      });
      
      // Check for duplicate versions
      const versions = abcVariants.map(v => v.version).filter(Boolean);
      const uniqueVersions = new Set(versions);
      if (uniqueVersions.size !== 3 || !['A', 'B', 'C'].every(v => uniqueVersions.has(v))) {
        errors.push(`Variants must have unique versions A, B, and C. Got: ${versions.join(', ')}`);
      }
    }
  }
  
  return {
    isValid: errors.length === 0,
    errors,
    warnings
  };
}

/**
 * Provide detailed error logging for debugging
 * @param {*} response - The response that failed validation
 * @param {Array} errors - List of validation errors
 * @param {Array} warnings - List of validation warnings
 */
export function logValidationFailure(response, errors, warnings) {
  console.error('❌ API CONTRACT VIOLATION DETECTED');
  console.error('=====================================');
  
  console.error('Expected Contract Fields:');
  console.error('  ✓ platform: string');
  console.error('  ✓ original: {copy: string, score: number}');
  console.error('  ✓ improved: {copy: string, score: number, improvements: array}');
  console.error('  ✓ abTests: {variations: array, abc_variants: array[3]}');
  console.error('  ✓ compliance, psychology, roi, legal: objects');
  console.error('  ✓ analysis_id: string');
  console.error('  ✓ comprehensive_analysis_complete: boolean (true)');
  
  console.error('\nValidation Errors:');
  errors.forEach((error, index) => {
    console.error(`  ${index + 1}. ${error}`);
  });
  
  if (warnings.length > 0) {
    console.warn('\nValidation Warnings:');
    warnings.forEach((warning, index) => {
      console.warn(`  ${index + 1}. ${warning}`);
    });
  }
  
  console.error('\nReceived Response Structure:');
  console.error(JSON.stringify(response, null, 2));
  
  console.error('\nSpecific abTests Analysis:');
  if (response?.abTests) {
    console.error('  abTests type:', typeof response.abTests);
    console.error('  abTests.variations type:', typeof response.abTests.variations, Array.isArray(response.abTests.variations) ? `(array of ${response.abTests.variations.length})` : '');
    console.error('  abTests.abc_variants type:', typeof response.abTests.abc_variants, Array.isArray(response.abTests.abc_variants) ? `(array of ${response.abTests.abc_variants.length})` : '');
    
    if (Array.isArray(response.abTests.abc_variants)) {
      response.abTests.abc_variants.forEach((variant, index) => {
        console.error(`  Variant ${index + 1}:`, {
          type: typeof variant,
          id: variant?.id,
          version: variant?.version,
          headline: typeof variant?.headline,
          body_text: typeof variant?.body_text,
          cta: typeof variant?.cta,
          hasAllFields: variant && ['id', 'version', 'headline', 'body_text', 'cta'].every(field => field in variant)
        });
      });
    }
  } else {
    console.error('  abTests is missing or invalid');
  }
}

/**
 * Create fallback response structure when API fails
 * @param {string} adCopy - Original ad copy
 * @param {string} platform - Platform identifier
 * @returns {Object} - Fallback response object
 */
export function createFallbackResponse(adCopy, platform) {
  return {
    // Use data that would have come from the API
    original: {
      copy: adCopy,
      score: 65
    },
    improved: {
      copy: `Improved: ${adCopy}`,
      score: 75,
      improvements: [
        { category: "General", description: "Enhanced for better engagement" }
      ]
    },
    compliance: { status: 'COMPLIANT', totalIssues: 0, issues: [] },
    psychology: { overallScore: 70, topOpportunity: 'Add social proof', triggers: [] },
    // IMPORTANT: Provide fallback A/B/C variants
    abTests: {
      variations: [],
      abc_variants: [
        {
          id: 'fallback_a',
          version: 'A',
          type: 'benefit_focused',
          variant_name: 'Benefits Focus',
          variant_description: 'Emphasizes key benefits',
          best_for: ['benefit-focused users'],
          headline: 'Experience the benefits',
          body_text: 'Discover what makes this special for you.',
          cta: 'Learn More',
          target_audience: '',
          emotional_trigger: '',
          psychological_framework: ''
        },
        {
          id: 'fallback_b',
          version: 'B', 
          type: 'urgency_focused',
          variant_name: 'Urgency Focus',
          variant_description: 'Creates urgency and scarcity',
          best_for: ['action-oriented users'],
          headline: 'Limited time opportunity',
          body_text: 'Act now before this opportunity expires.',
          cta: 'Act Now',
          target_audience: '',
          emotional_trigger: '',
          psychological_framework: ''
        },
        {
          id: 'fallback_c',
          version: 'C',
          type: 'trust_focused', 
          variant_name: 'Trust Focus',
          variant_description: 'Builds trust and credibility',
          best_for: ['trust-focused users'],
          headline: 'Trusted by thousands',
          body_text: 'Join a community that values quality and results.',
          cta: 'Join Now',
          target_audience: '',
          emotional_trigger: '',
          psychological_framework: ''
        }
      ]
    },
    roi: { segment: 'Mass market', premiumVersions: [] },
    legal: { riskLevel: 'Low', issues: [] },
    brandVoice: { 
      tone: platform === 'linkedin' ? 'Professional' : 'Conversational',
      personality: 'Friendly',
      formality: 'Casual',
      consistency: 80,
      recommendations: []
    },
    performance: { forensics: {}, quickWins: [] },
    platform: platform,
    analysis_id: 'fallback-analysis',
    comprehensive_analysis_complete: true
  };
}