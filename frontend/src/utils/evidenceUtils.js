/**
 * Utility functions for handling evidence-based analysis statements
 * Ensures we don't make claims without sufficient evidence
 */

/**
 * Evidence levels for analysis statements
 */
export const EVIDENCE_LEVELS = {
  HIGH: 'high',
  MEDIUM: 'medium', 
  LOW: 'low',
  NONE: 'none'
};

/**
 * Format a statement based on available evidence
 * @param {string} statement - The original statement/claim
 * @param {string} evidenceLevel - Level of evidence supporting the claim
 * @param {object} options - Additional formatting options
 * @returns {string} Formatted statement with appropriate disclaimers
 */
export const formatWithEvidence = (statement, evidenceLevel = EVIDENCE_LEVELS.LOW, options = {}) => {
  if (!statement) return '';
  
  const { showPrefix = true, customPrefix = null } = options;
  
  if (!showPrefix) return statement;
  
  switch (evidenceLevel) {
    case EVIDENCE_LEVELS.HIGH:
      return statement; // No prefix needed for high-evidence claims
      
    case EVIDENCE_LEVELS.MEDIUM:
      return customPrefix || `Likely improvement: ${statement}`;
      
    case EVIDENCE_LEVELS.LOW:
      return customPrefix || `Insufficient evidence: ${statement}`;
      
    case EVIDENCE_LEVELS.NONE:
      return customPrefix || `Speculative: ${statement}`;
      
    default:
      return customPrefix || `Insufficient evidence: ${statement}`;
  }
};

/**
 * Determine evidence level based on data quality and sample size
 * @param {object} analysisData - The analysis data object
 * @returns {string} Evidence level
 */
export const determineEvidenceLevel = (analysisData = {}) => {
  const { 
    sampleSize = 0, 
    confidence = 0, 
    dataQuality = 'low',
    isSimulated = true,
    evidenceLevel = null  // Explicit evidence level from backend
  } = analysisData;
  
  // If explicit evidence level is provided, use it
  if (evidenceLevel && Object.values(EVIDENCE_LEVELS).includes(evidenceLevel)) {
    return evidenceLevel;
  }
  
  // If it's simulated/mock data, evidence is always low
  if (isSimulated) {
    return EVIDENCE_LEVELS.LOW;
  }
  
  // Determine based on sample size and confidence
  if (sampleSize >= 1000 && confidence >= 0.95 && dataQuality === 'high') {
    return EVIDENCE_LEVELS.HIGH;
  } else if (sampleSize >= 100 && confidence >= 0.8 && dataQuality !== 'low') {
    return EVIDENCE_LEVELS.MEDIUM;
  } else if (sampleSize > 0 || confidence > 0) {
    return EVIDENCE_LEVELS.LOW;
  } else {
    return EVIDENCE_LEVELS.NONE;
  }
};

/**
 * Format improvement percentages with evidence disclaimers
 * @param {number} percentage - The improvement percentage
 * @param {string} evidenceLevel - Level of evidence
 * @returns {string} Formatted percentage with disclaimer
 */
export const formatImprovementWithEvidence = (percentage, evidenceLevel = EVIDENCE_LEVELS.LOW) => {
  if (!percentage) return 'No improvement data available';
  
  const baseText = `${percentage}% improvement`;
  
  switch (evidenceLevel) {
    case EVIDENCE_LEVELS.HIGH:
      return `${baseText} (verified)`;
    case EVIDENCE_LEVELS.MEDIUM:
      return `${baseText} (estimated)`;
    case EVIDENCE_LEVELS.LOW:
      return `${baseText} (simulated)`;
    default:
      return `${baseText} (hypothetical)`;
  }
};

/**
 * Get appropriate styling for evidence level
 * @param {string} evidenceLevel - Level of evidence
 * @returns {object} MUI sx styling object
 */
export const getEvidenceStyling = (evidenceLevel) => {
  switch (evidenceLevel) {
    case EVIDENCE_LEVELS.HIGH:
      return { 
        color: 'success.main', 
        fontWeight: 600,
        '&::before': { content: '"✓ "' }
      };
    case EVIDENCE_LEVELS.MEDIUM:
      return { 
        color: 'warning.main', 
        fontWeight: 500,
        '&::before': { content: '"⚡ "' }
      };
    case EVIDENCE_LEVELS.LOW:
      return { 
        color: 'text.secondary', 
        fontWeight: 400,
        fontStyle: 'italic',
        '&::before': { content: '"⚠️ "' }
      };
    default:
      return { 
        color: 'text.disabled', 
        fontWeight: 400,
        fontStyle: 'italic',
        '&::before': { content: '"? "' }
      };
  }
};

/**
 * Validate and sanitize evidence metadata
 * @param {object} metadata - Raw evidence metadata
 * @returns {object} Validated metadata
 */
export const validateEvidenceMetadata = (metadata = {}) => {
  return {
    evidenceLevel: metadata.evidenceLevel || EVIDENCE_LEVELS.LOW,
    sampleSize: Math.max(0, parseInt(metadata.sampleSize) || 0),
    confidence: Math.max(0, Math.min(1, parseFloat(metadata.confidence) || 0)),
    dataQuality: ['high', 'medium', 'low'].includes(metadata.dataQuality) 
      ? metadata.dataQuality 
      : 'low',
    isSimulated: metadata.isSimulated !== false, // Default to true for safety
    disclaimer: metadata.disclaimer || null
  };
};