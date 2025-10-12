import { useState, useCallback } from 'react';
import toast from 'react-hot-toast';
import apiService from '../services/apiService';
import { createAdDraft, validateAdDraft } from '../types/adCopy';

/**
 * Custom hook for generating ad copy variations
 * Provides a unified interface for all input methods to generate variations
 */
export const useVariationGenerator = () => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [results, setResults] = useState(null);
  const [lastRequest, setLastRequest] = useState(null);

  /**
   * Generate variations for a single ad draft
   * @param {AdDraft} draft - The ad draft to generate variations for
   * @param {VariationOptions} options - Options for variation generation
   * @returns {Promise<VariationResult>}
   */
  const generateSingle = useCallback(async (draft, options) => {
    setLoading(true);
    setError(null);
    
    try {
      // Validate the draft
      const validation = validateAdDraft(draft);
      if (!validation.isValid) {
        throw new Error(`Invalid ad draft: ${validation.errors.join(', ')}`);
      }

      // Prepare the request
      const requestData = {
        ad: {
          headline: draft.headline,
          body_text: draft.body_text,
          cta: draft.cta,
          platform: draft.platform,
          industry: draft.industry,
          target_audience: draft.target_audience
        },
        options: {
          numVariations: options.numVariations || 3,
          tone: options.tone || 'professional',
          includeEmojis: options.includeEmojis || false,
          includeUrgency: options.includeUrgency || false,
          includeStats: options.includeStats || false,
          focusAreas: options.focusAreas || ['headline', 'emotion', 'cta'],
          customInstructions: options.customInstructions || ''
        }
      };

      setLastRequest(requestData);

      // Make the API call (we'll extend the existing generate-ads endpoint)
      const response = await apiService.generateAdVariations(requestData);

      // Convert response to standardized format
      const variationResult = {
        original_id: draft.id,
        variations: response.ads?.map((ad, index) => 
          createAdDraft({
            ...ad,
            parent_id: draft.id,
            is_variation: true,
            variation_strategy: ad.strategy_type || `variation_${index + 1}`,
            metadata: {
              roi_score: ad.roi_score,
              roi_explanation: ad.roi_explanation,
              pricing_angle: ad.pricing_angle,
              generation_index: index
            }
          }, 'generated')
        ) || [],
        generation_info: {
          model_used: 'gpt-4',
          generated_at: new Date(),
          options: requestData.options,
          original_draft: draft
        }
      };

      setResults(variationResult);
      toast.success(`Generated ${variationResult.variations.length} variations! ✨`);
      
      return variationResult;
    } catch (err) {
      console.error('Variation generation failed:', err);
      const errorMessage = err.response?.data?.detail || err.message || 'Failed to generate variations';
      setError(new Error(errorMessage));
      toast.error(errorMessage);
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  /**
   * Generate variations for multiple ad drafts
   * @param {AdDraft[]} drafts - Array of ad drafts
   * @param {VariationOptions} options - Options for variation generation
   * @returns {Promise<VariationResult[]>}
   */
  const generateBatch = useCallback(async (drafts, options) => {
    setLoading(true);
    setError(null);
    
    try {
      // Validate all drafts
      for (const draft of drafts) {
        const validation = validateAdDraft(draft);
        if (!validation.isValid) {
          throw new Error(`Invalid ad draft "${draft.headline}": ${validation.errors.join(', ')}`);
        }
      }

      // Prepare batch request
      const requestData = {
        ads: drafts.map(draft => ({
          headline: draft.headline,
          body_text: draft.body_text,
          cta: draft.cta,
          platform: draft.platform,
          industry: draft.industry,
          target_audience: draft.target_audience
        })),
        options: {
          numVariations: options.numVariations || 3,
          tone: options.tone || 'professional',
          includeEmojis: options.includeEmojis || false,
          includeUrgency: options.includeUrgency || false,
          includeStats: options.includeStats || false,
          focusAreas: options.focusAreas || ['headline', 'emotion', 'cta'],
          customInstructions: options.customInstructions || ''
        }
      };

      setLastRequest(requestData);

      // Make the API call for batch generation
      const response = await apiService.generateBatchVariations(requestData);

      // Convert response to standardized format
      const batchResults = response.results?.map((result, batchIndex) => {
        const originalDraft = drafts[batchIndex];
        return {
          original_id: originalDraft.id,
          variations: result.ads?.map((ad, index) => 
            createAdDraft({
              ...ad,
              parent_id: originalDraft.id,
              is_variation: true,
              variation_strategy: ad.strategy_type || `variation_${index + 1}`,
              metadata: {
                roi_score: ad.roi_score,
                roi_explanation: ad.roi_explanation,
                pricing_angle: ad.pricing_angle,
                generation_index: index,
                batch_index: batchIndex
              }
            }, 'generated')
          ) || [],
          generation_info: {
            model_used: 'gpt-4',
            generated_at: new Date(),
            options: requestData.options,
            original_draft: originalDraft
          }
        };
      }) || [];

      setResults(batchResults);
      const totalVariations = batchResults.reduce((total, result) => total + result.variations.length, 0);
      toast.success(`Generated ${totalVariations} variations for ${drafts.length} ads! 🚀`);
      
      return batchResults;
    } catch (err) {
      console.error('Batch variation generation failed:', err);
      const errorMessage = err.response?.data?.detail || err.message || 'Failed to generate variations';
      setError(new Error(errorMessage));
      toast.error(errorMessage);
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  /**
   * Regenerate variations with the same parameters as the last request
   * @returns {Promise<VariationResult|VariationResult[]>}
   */
  const regenerate = useCallback(async () => {
    if (!lastRequest) {
      toast.error('No previous generation to repeat');
      return null;
    }

    setLoading(true);
    setError(null);
    
    try {
      let response;
      if (Array.isArray(lastRequest.ads)) {
        // Batch regeneration
        response = await apiService.generateBatchVariations(lastRequest);
      } else {
        // Single regeneration
        response = await apiService.generateAdVariations(lastRequest);
      }

      // Process response similar to original generation
      // This is simplified - you'd want to reuse the logic from above
      toast.success('Variations regenerated! 🔄');
      return response;
    } catch (err) {
      console.error('Regeneration failed:', err);
      const errorMessage = err.response?.data?.detail || err.message || 'Failed to regenerate variations';
      setError(new Error(errorMessage));
      toast.error(errorMessage);
      throw err;
    } finally {
      setLoading(false);
    }
  }, [lastRequest]);

  /**
   * Clear current results and reset state
   */
  const clearResults = useCallback(() => {
    setResults(null);
    setError(null);
    setLastRequest(null);
  }, []);

  /**
   * Retry the last failed request
   */
  const retry = useCallback(async () => {
    if (lastRequest) {
      return await regenerate();
    }
  }, [lastRequest, regenerate]);

  return {
    // State
    loading,
    error,
    results,
    hasResults: Boolean(results),
    
    // Actions
    generateSingle,
    generateBatch,
    regenerate,
    clearResults,
    retry,
    
    // Utilities
    canRegenerate: Boolean(lastRequest),
    isGenerating: loading
  };
};

export default useVariationGenerator;
