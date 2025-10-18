/**
 * 🔒 UNIFIED API CONTRACT - Single Source of Truth
 * 
 * This contract defines the EXACT structure that MUST be used by both backend and frontend.
 * ANY changes to this contract MUST be made in BOTH backend AND frontend simultaneously.
 * 
 * ⚠️ CRITICAL: This prevents "Backend did not return valid A/B/C variants" errors
 */

// ===== PLATFORM TYPES =====

export type Platform = 'facebook' | 'instagram' | 'google' | 'linkedin' | 'twitter' | 'tiktok';

// ===== AD STRUCTURES =====

/**
 * Parsed ad structure - used for original and improved ads
 */
export interface ParsedAd {
  /** Main headline (empty string if platform doesn't use headlines) */
  headline: string;
  
  /** Main body text content */
  body: string;
  
  /** Call-to-action text */
  cta: string;
  
  /** Platform identifier */
  platform: Platform;
  
  /** Additional headlines for Google Ads (optional) */
  headline1?: string;
  headline2?: string;
  headline3?: string;
  
  /** Additional descriptions for Google Ads (optional) */
  description1?: string;
  description2?: string;
  
  /** Hashtags for Instagram (optional) */
  hashtags?: string[];
}

/**
 * Ad variant for A/B/C testing
 * MUST contain exactly these fields - no more, no less
 */
export interface AdVariant {
  /** Unique identifier for this variant - REQUIRED by frontend validation */
  id: string;
  
  /** Version identifier - MUST be "A", "B", or "C" */
  version: "A" | "B" | "C";
  
  /** Optimization focus type */
  focus: string;
  
  /** Human-readable variant name */
  name: string;
  
  /** Description of what this variant tests */
  description: string;
  
  /** Array of audience types this variant works best for */
  bestFor: string[];
  
  /** Unique headline for this variant - MUST be different from improved ad */
  headline: string;
  
  /** Unique body copy for this variant - MUST be different from improved ad */
  body: string;
  
  /** Unique CTA for this variant - MUST be different from improved ad */
  cta: string;
  
  /** Platform this variant is optimized for */
  platform: Platform;
}

/**
 * Metadata about the analysis execution
 */
export interface AnalysisMetadata {
  /** ISO datetime when analysis was generated */
  generatedAt: string;
  
  /** Processing time in milliseconds */
  processingTime: number;
  
  /** Number of retries attempted (0 if no retries) */
  retryCount: number;
  
  /** Whether all validation checks passed */
  validationPassed: boolean;
  
  /** Count of quality issues found */
  qualityIssues: number;
  
  /** Whether content is optimized for the specified platform */
  platformOptimized: boolean;
  
  /** Workflow type used (optional) */
  workflow?: string;
  
  /** List of completed processing steps (optional) */
  steps_completed?: string[];
}

// ===== MAIN RESPONSE CONTRACT =====

/**
 * 🔒 MAIN API RESPONSE CONTRACT
 * 
 * This is the EXACT structure that /api/ads/improve MUST return
 * and that ComprehensiveAnalysisLoader.jsx MUST expect.
 * 
 * DO NOT modify without updating BOTH backend and frontend.
 */
export interface AdCopyAnalysisResponse {
  /** Whether the analysis completed successfully - REQUIRED */
  success: boolean;
  
  /** Platform that was analyzed - REQUIRED */
  platform: Platform;
  
  /** Original ad quality score (0-100) - REQUIRED */
  originalScore: number;
  
  /** Improved ad quality score (0-100) - REQUIRED */
  improvedScore: number;
  
  /** Confidence score for the analysis (0-100) - REQUIRED */
  confidenceScore: number;
  
  /** Original ad content and metadata - REQUIRED */
  original: {
    /** Original ad text */
    copy: string;
    /** Quality score for original ad */
    score: number;
  };
  
  /** Improved ad content and metadata - REQUIRED */
  improved: {
    /** Improved ad text */
    copy: string;
    /** Quality score for improved ad */
    score: number;
    /** List of improvements made */
    improvements: Array<{
      category: string;
      description: string;
    }>;
  };
  
  /** A/B/C testing variants - REQUIRED, EXACTLY this structure */
  abTests: {
    /** Legacy variations field (empty array for compatibility) */
    variations: any[];
    /** Strategic A/B/C test variants - MUST be array of exactly 3 AdVariant objects */
    abc_variants: [AdVariant, AdVariant, AdVariant];
  };
  
  /** Compliance information - REQUIRED */
  compliance: {
    status: "COMPLIANT" | "ISSUES";
    totalIssues: number;
    issues: string[];
  };
  
  /** Psychology analysis - REQUIRED */
  psychology: {
    overallScore: number;
    topOpportunity: string;
    triggers: string[];
  };
  
  /** ROI analysis - REQUIRED */
  roi: {
    segment: string;
    premiumVersions: any[];
  };
  
  /** Legal analysis - REQUIRED */
  legal: {
    riskLevel: "Low" | "Medium" | "High";
    issues: string[];
  };
  
  /** Platform-specific tips - REQUIRED */
  tips: string;
  
  /** Analysis execution metadata - REQUIRED */
  metadata: AnalysisMetadata;
  
  /** Analysis ID for tracking - REQUIRED */
  analysis_id: string;
  
  /** Whether comprehensive analysis is complete - REQUIRED */
  comprehensive_analysis_complete: boolean;
}

// ===== VALIDATION SCHEMAS =====

/**
 * Validation function for backend to check response before sending
 */
export function validateAdCopyAnalysisResponse(response: any): {
  valid: boolean;
  errors: string[];
} {
  const errors: string[] = [];
  
  // Check required top-level fields
  if (typeof response !== 'object' || response === null) {
    errors.push('Response must be an object');
    return { valid: false, errors };
  }
  
  if (response.success !== true) {
    errors.push('success must be true');
  }
  
  if (typeof response.platform !== 'string') {
    errors.push('platform must be a string');
  }
  
  if (typeof response.originalScore !== 'number' || response.originalScore < 0 || response.originalScore > 100) {
    errors.push('originalScore must be a number between 0-100');
  }
  
  if (typeof response.improvedScore !== 'number' || response.improvedScore < 0 || response.improvedScore > 100) {
    errors.push('improvedScore must be a number between 0-100');
  }
  
  if (typeof response.confidenceScore !== 'number' || response.confidenceScore < 0 || response.confidenceScore > 100) {
    errors.push('confidenceScore must be a number between 0-100');
  }
  
  // Check original ad structure
  if (!response.original || typeof response.original !== 'object') {
    errors.push('original must be an object');
  } else {
    if (typeof response.original.copy !== 'string') {
      errors.push('original.copy must be a string');
    }
    if (typeof response.original.score !== 'number') {
      errors.push('original.score must be a number');
    }
  }
  
  // Check improved ad structure
  if (!response.improved || typeof response.improved !== 'object') {
    errors.push('improved must be an object');
  } else {
    if (typeof response.improved.copy !== 'string') {
      errors.push('improved.copy must be a string');
    }
    if (typeof response.improved.score !== 'number') {
      errors.push('improved.score must be a number');
    }
    if (!Array.isArray(response.improved.improvements)) {
      errors.push('improved.improvements must be an array');
    }
  }
  
  // Check abTests structure - THIS IS CRITICAL
  if (!response.abTests || typeof response.abTests !== 'object') {
    errors.push('abTests must be an object');
  } else {
    if (!Array.isArray(response.abTests.variations)) {
      errors.push('abTests.variations must be an array');
    }
    if (!Array.isArray(response.abTests.abc_variants)) {
      errors.push('abTests.abc_variants must be an array');
    } else if (response.abTests.abc_variants.length !== 3) {
      errors.push(`abTests.abc_variants must have exactly 3 items, got ${response.abTests.abc_variants.length}`);
    } else {
      // Validate each variant
      response.abTests.abc_variants.forEach((variant: any, index: number) => {
        if (!variant.id || typeof variant.id !== 'string') {
          errors.push(`Variant ${index + 1} must have an id field (string)`);
        }
        if (!variant.version || !['A', 'B', 'C'].includes(variant.version)) {
          errors.push(`Variant ${index + 1} must have version "A", "B", or "C"`);
        }
        if (!variant.headline || typeof variant.headline !== 'string') {
          errors.push(`Variant ${index + 1} must have a headline field (string)`);
        }
        if (!variant.body || typeof variant.body !== 'string') {
          errors.push(`Variant ${index + 1} must have a body field (string)`);
        }
        if (!variant.cta || typeof variant.cta !== 'string') {
          errors.push(`Variant ${index + 1} must have a cta field (string)`);
        }
      });
    }
  }
  
  // Check required fields
  const requiredStringFields = ['tips', 'analysis_id'];
  requiredStringFields.forEach(field => {
    if (typeof response[field] !== 'string') {
      errors.push(`${field} must be a string`);
    }
  });
  
  const requiredBooleanFields = ['comprehensive_analysis_complete'];
  requiredBooleanFields.forEach(field => {
    if (typeof response[field] !== 'boolean') {
      errors.push(`${field} must be a boolean`);
    }
  });
  
  const requiredObjectFields = ['compliance', 'psychology', 'roi', 'legal', 'metadata'];
  requiredObjectFields.forEach(field => {
    if (!response[field] || typeof response[field] !== 'object') {
      errors.push(`${field} must be an object`);
    }
  });
  
  return {
    valid: errors.length === 0,
    errors
  };
}

/**
 * Text cleaning function to ensure clean output
 */
export function cleanAdText(text: string): string {
  if (!text || typeof text !== 'string') return '';
  
  return text
    .trim() // Remove leading/trailing whitespace
    .replace(/^["']+|["']+$/g, '') // Remove leading/trailing quotes
    .replace(/\\"/g, '"') // Fix escaped quotes
    .replace(/\r?\n/g, ' ') // Replace newlines with spaces
    .replace(/\s+/g, ' ') // Collapse multiple spaces
    .trim(); // Final trim
}

export default AdCopyAnalysisResponse;