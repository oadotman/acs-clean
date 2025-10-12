/**
 * Unified Ad Copy Data Types
 * This file defines the standardized data structures used across all input methods
 * and the variation generation system.
 */

/**
 * Represents a single piece of ad copy regardless of how it was created
 * @typedef {Object} AdDraft
 * @property {string} id - Unique identifier for this draft
 * @property {'manual'|'paste'|'file'|'generated'} sourceType - How this ad copy was created
 * @property {string} headline - The main headline text
 * @property {string} body_text - The main body/description text
 * @property {string} cta - Call-to-action text
 * @property {string} platform - Target platform (facebook, google, linkedin, etc.)
 * @property {string} [industry] - Optional industry classification
 * @property {string} [target_audience] - Optional target audience description
 * @property {Object} [metadata] - Additional metadata based on source type
 * @property {Date} created_at - When this draft was created
 * @property {string} [parent_id] - If this is a variation, ID of the original draft
 * @property {boolean} [is_variation] - True if this is a generated variation
 * @property {string} [variation_strategy] - Strategy used for variation (if applicable)
 */

/**
 * Options for generating variations
 * @typedef {Object} VariationOptions
 * @property {number} numVariations - Number of variations to generate (1-8)
 * @property {string} tone - Tone of voice (professional, casual, urgent, etc.)
 * @property {boolean} includeEmojis - Whether to include emojis
 * @property {boolean} includeUrgency - Whether to add urgency elements
 * @property {boolean} includeStats - Whether to include statistics/numbers
 * @property {string[]} [focusAreas] - Specific areas to focus on (headline, emotion, cta, etc.)
 * @property {string} [customInstructions] - Additional custom instructions
 */

/**
 * Result from variation generation
 * @typedef {Object} VariationResult
 * @property {string} original_id - ID of the original draft
 * @property {AdDraft[]} variations - Array of generated variations
 * @property {Object} generation_info - Metadata about the generation process
 * @property {string} generation_info.model_used - AI model used
 * @property {Date} generation_info.generated_at - When variations were generated
 * @property {VariationOptions} generation_info.options - Options used for generation
 */

/**
 * Batch variation request for multiple drafts
 * @typedef {Object} BatchVariationRequest
 * @property {AdDraft[]} drafts - Array of drafts to generate variations for
 * @property {VariationOptions} options - Options to apply to all drafts
 * @property {boolean} [auto_analyze] - Whether to automatically run through analysis tools
 * @property {string[]} [analysis_tools] - Which analysis tools to run (if auto_analyze is true)
 */

/**
 * Creates a new AdDraft with proper defaults
 * @param {Object} data - Draft data
 * @param {'manual'|'paste'|'file'|'generated'} sourceType - How the draft was created
 * @returns {AdDraft}
 */
export const createAdDraft = (data, sourceType) => {
  return {
    id: data.id || `draft_${Date.now()}_${Math.random().toString(36).substring(2)}`,
    sourceType,
    headline: data.headline || '',
    body_text: data.body_text || data.bodyText || '',
    cta: data.cta || '',
    platform: data.platform || 'facebook',
    industry: data.industry || null,
    target_audience: data.target_audience || data.targetAudience || null,
    metadata: data.metadata || {},
    created_at: new Date(),
    parent_id: data.parent_id || null,
    is_variation: data.is_variation || false,
    variation_strategy: data.variation_strategy || null,
    ...data // Allow additional properties to be passed through
  };
};

/**
 * Creates default variation options
 * @returns {VariationOptions}
 */
export const createDefaultVariationOptions = () => {
  return {
    numVariations: 3,
    tone: 'professional',
    includeEmojis: true,
    includeUrgency: false,
    includeStats: true,
    focusAreas: ['headline', 'emotion', 'cta'],
    customInstructions: ''
  };
};

/**
 * Validates that an AdDraft has the minimum required fields
 * @param {AdDraft} draft 
 * @returns {Object} { isValid: boolean, errors: string[] }
 */
export const validateAdDraft = (draft) => {
  const errors = [];
  
  if (!draft.headline?.trim()) {
    errors.push('Headline is required');
  }
  
  if (!draft.body_text?.trim()) {
    errors.push('Body text is required');
  }
  
  if (!draft.cta?.trim()) {
    errors.push('Call-to-action is required');
  }
  
  if (!draft.platform) {
    errors.push('Platform is required');
  }
  
  return {
    isValid: errors.length === 0,
    errors
  };
};

/**
 * Converts legacy ad copy format to AdDraft format
 * @param {Object} legacyAd - Ad in the old format
 * @param {'manual'|'paste'|'file'|'generated'} sourceType
 * @returns {AdDraft}
 */
export const convertLegacyToAdDraft = (legacyAd, sourceType) => {
  return createAdDraft({
    headline: legacyAd.headline,
    body_text: legacyAd.body_text || legacyAd.bodyText,
    cta: legacyAd.cta,
    platform: legacyAd.platform,
    industry: legacyAd.industry,
    target_audience: legacyAd.target_audience || legacyAd.targetAudience,
    metadata: {
      originalFormat: 'legacy',
      ...legacyAd
    }
  }, sourceType);
};

/**
 * Tone options available for variation generation
 */
export const TONE_OPTIONS = [
  { value: 'professional', label: 'Professional' },
  { value: 'casual', label: 'Casual & Friendly' },
  { value: 'urgent', label: 'Urgent & Direct' },
  { value: 'playful', label: 'Playful & Fun' },
  { value: 'authoritative', label: 'Authoritative' },
  { value: 'empathetic', label: 'Empathetic' },
  { value: 'confident', label: 'Confident' },
  { value: 'conversational', label: 'Conversational' }
];

/**
 * Focus areas available for variation generation
 */
export const FOCUS_AREAS = [
  { id: 'headline', name: 'Headlines', description: 'Focus on creating compelling headlines' },
  { id: 'emotion', name: 'Emotional Triggers', description: 'Emphasize emotional appeal' },
  { id: 'cta', name: 'Call-to-Action', description: 'Optimize the call-to-action' },
  { id: 'urgency', name: 'Urgency', description: 'Add time-sensitive elements' },
  { id: 'social_proof', name: 'Social Proof', description: 'Include testimonials/social proof' },
  { id: 'authority', name: 'Authority', description: 'Establish credibility and expertise' },
  { id: 'benefit_focused', name: 'Benefits', description: 'Focus on customer benefits' },
  { id: 'feature_focused', name: 'Features', description: 'Highlight product features' }
];

export default {
  createAdDraft,
  createDefaultVariationOptions,
  validateAdDraft,
  convertLegacyToAdDraft,
  TONE_OPTIONS,
  FOCUS_AREAS
};
