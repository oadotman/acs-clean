/**
 * Creative Controls Service - Phase 4 & 5 Backend Integration
 * 
 * This service handles API communication for advanced creative controls,
 * variant generation, and creative analytics features.
 */

import apiClient from './apiClient';

class CreativeControlsService {
  /**
   * Generate ad variants using Phase 4 & 5 creative controls
   */
  async generateCreativeVariants(adData, options = {}) {
    try {
      const payload = {
        ad_data: {
          headline: adData.headline || '',
          body_text: adData.body_text || adData.text || '',
          cta: adData.cta || '',
          platform: adData.platform || 'facebook',
          industry: adData.industry || '',
          target_audience: adData.target_audience || ''
        },
        creative_controls: {
          creativity_level: options.creativity_level || 5,
          urgency_level: options.urgency_level || 5,
          emotion_type: options.emotion_type || 'inspiring',
          filter_cliches: options.filter_cliches !== false,
          num_variants: options.num_variants || 1,
          variant_strategy: options.variant_strategy || 'diverse'
        },
        generation_options: {
          emoji_level: options.emoji_level || 'moderate',
          human_tone: options.human_tone || 'conversational',
          brand_tone: options.brand_tone || 'casual',
          formality_level: options.formality_level || 5,
          target_audience_description: options.target_audience_description || '',
          brand_voice_description: options.brand_voice_description || '',
          include_cta: options.include_cta !== false,
          cta_style: options.cta_style || 'medium'
        }
      };

      console.log('🎨 CreativeControlsService: Generating variants with payload:', payload);

      const response = await apiClient.post('/api/creative/generate-variants', payload);
      
      if (response.data) {
        console.log('✅ CreativeControlsService: Variants generated successfully:', response.data);
        return {
          success: true,
          data: response.data,
          variants: response.data.variants || [],
          comparison: response.data.comparison || null,
          recommendations: response.data.recommendations || []
        };
      }

      throw new Error('Invalid response from server');
    } catch (error) {
      console.error('❌ CreativeControlsService: Error generating variants:', error);
      
      throw new Error(
        error.response?.data?.message || 
        error.message || 
        'Failed to generate creative variants'
      );
    }
  }

  /**
   * Analyze cliché usage in ad copy
   */
  async analyzeCliches(text) {
    try {
      const response = await apiClient.post('/api/creative/analyze-cliches', {
        text: text
      });

      return {
        success: true,
        data: response.data
      };
    } catch (error) {
      console.error('❌ CreativeControlsService: Error analyzing clichés:', error);
      
      throw new Error(
        error.response?.data?.message || 
        error.message || 
        'Failed to analyze clichés'
      );
    }
  }

  /**
   * Get creative analytics data
   */
  async getCreativeAnalytics(timeRange = '30d', platform = 'all') {
    try {
      const response = await apiClient.get('/api/creative/analytics', {
        params: {
          time_range: timeRange,
          platform: platform
        }
      });

      return {
        success: true,
        data: response.data
      };
    } catch (error) {
      console.error('❌ CreativeControlsService: Error fetching analytics:', error);
      
      throw new Error(
        error.response?.data?.message || 
        error.message || 
        'Failed to fetch creative analytics'
      );
    }
  }

  /**
   * Get platform-specific creative optimization recommendations
   */
  async getPlatformOptimizations(platform, adData) {
    try {
      const response = await apiClient.post('/api/creative/platform-optimizations', {
        platform: platform,
        ad_data: adData
      });

      return {
        success: true,
        data: response.data
      };
    } catch (error) {
      console.error('❌ CreativeControlsService: Error fetching optimizations:', error);
      
      throw new Error(
        error.response?.data?.message || 
        error.message || 
        'Failed to fetch platform optimizations'
      );
    }
  }

  // ============ Phase 6: Preset System ============
  
  /**
   * Get available presets for different industries/use cases
   */
  async getPresets() {
    try {
      const response = await apiClient.get('/api/creative/presets');
      
      return {
        success: true,
        data: response.data
      };
    } catch (error) {
      console.error('❌ CreativeControlsService: Error fetching presets:', error);
      
      throw new Error(
        error.response?.data?.message || 
        error.message || 
        'Failed to fetch presets'
      );
    }
  }

  /**
   * Save a custom preset configuration
   */
  async savePreset(name, settings, userId) {
    try {
      const response = await apiClient.post('/api/creative/presets', {
        name: name,
        settings: settings,
        user_id: userId
      });
      
      return {
        success: true,
        data: response.data
      };
    } catch (error) {
      console.error('❌ CreativeControlsService: Error saving preset:', error);
      
      throw new Error(
        error.response?.data?.message || 
        error.message || 
        'Failed to save preset'
      );
    }
  }

  // ============ Phase 7: Quality Assurance & Feedback ============
  
  /**
   * Validate generated copy for quality issues
   */
  async validateCopy(copyData, platform, rules = {}) {
    try {
      const response = await apiClient.post('/api/creative/validate', {
        copy: copyData,
        platform: platform,
        validation_rules: rules
      });
      
      return {
        success: true,
        data: response.data
      };
    } catch (error) {
      console.error('❌ CreativeControlsService: Error validating copy:', error);
      
      throw new Error(
        error.response?.data?.message || 
        error.message || 
        'Failed to validate copy'
      );
    }
  }

  /**
   * Auto-fix issues found in copy validation
   */
  async autoFixCopy(copyData, issues, platform) {
    try {
      const response = await apiClient.post('/api/creative/auto-fix', {
        copy: copyData,
        issues: issues,
        platform: platform
      });
      
      return {
        success: true,
        data: response.data
      };
    } catch (error) {
      console.error('❌ CreativeControlsService: Error auto-fixing copy:', error);
      
      throw new Error(
        error.response?.data?.message || 
        error.message || 
        'Failed to auto-fix copy'
      );
    }
  }

  /**
   * Submit user feedback for generated copy
   */
  async submitFeedback(feedbackData) {
    try {
      const response = await apiClient.post('/api/creative/feedback', feedbackData);
      
      return {
        success: true,
        data: response.data
      };
    } catch (error) {
      console.error('❌ CreativeControlsService: Error submitting feedback:', error);
      
      throw new Error(
        error.response?.data?.message || 
        error.message || 
        'Failed to submit feedback'
      );
    }
  }

  /**
   * Get feedback analytics and improvement trends
   */
  async getFeedbackAnalytics(timeRange = '30d') {
    try {
      const response = await apiClient.get('/api/creative/feedback-analytics', {
        params: { time_range: timeRange }
      });
      
      return {
        success: true,
        data: response.data
      };
    } catch (error) {
      console.error('❌ CreativeControlsService: Error fetching feedback analytics:', error);
      
      throw new Error(
        error.response?.data?.message || 
        error.message || 
        'Failed to fetch feedback analytics'
      );
    }
  }

  // ============ A/B/C Testing System ============
  
  /**
   * Generate A/B/C test variants with different psychological approaches
   */
  async generateABCVariants(adData, options = {}) {
    try {
      const payload = {
        ad_data: {
          headline: adData.headline || '',
          body_text: adData.body_text || adData.text || '',
          cta: adData.cta || '',
          platform: adData.platform || 'facebook',
          industry: adData.industry || '',
          target_audience: adData.target_audience || ''
        },
        creative_controls: {
          creativity_level: options.creativity_level || 6,
          urgency_level: options.urgency_level || 5,
          emotion_type: options.emotion_type || 'inspiring',
          filter_cliches: options.filter_cliches !== false,
          brand_voice_description: options.brand_voice_description || ''
        },
        variant_types: [
          {
            type: 'A',
            strategy: 'benefit_focused',
            prompt_modifier: 'Create benefit-focused ad copy. Lead with the positive transformation and outcomes. Use aspirational, forward-looking language. Focus on what the user will gain, achieve, or become.'
          },
          {
            type: 'B', 
            strategy: 'problem_focused',
            prompt_modifier: 'Create problem-focused ad copy. Start by identifying a specific pain point or frustration. Show empathy and understanding. Then position your offer as the direct solution to that problem.'
          },
          {
            type: 'C',
            strategy: 'story_driven',
            prompt_modifier: 'Create story-driven ad copy. Tell a brief, relatable story or scenario. Use a narrative structure with a character your audience can relate to. Make it human, emotional, and conversational.'
          }
        ]
      };

      console.log('🧪 CreativeControlsService: Generating A/B/C variants with payload:', payload);

      const response = await apiClient.post('/api/creative/generate-abc-variants', payload);
      
      if (response.data) {
        console.log('✅ CreativeControlsService: A/B/C variants generated successfully:', response.data);
        return {
          success: true,
          data: response.data,
          variants: response.data.variants || [],
          testing_guide: response.data.testing_guide || null
        };
      }

      throw new Error('Invalid response from server');
    } catch (error) {
      console.error('❌ CreativeControlsService: Error generating A/B/C variants:', error);
      
      throw new Error(
        error.response?.data?.message || 
        error.message || 
        'Failed to generate A/B/C variants'
      );
    }
  }

  /**
   * Regenerate a specific variant (A, B, or C) with same strategy
   */
  async regenerateABCVariant(adData, variantType, options = {}) {
    try {
      const strategies = {
        'A': {
          strategy: 'benefit_focused',
          prompt: 'Create benefit-focused ad copy. Lead with the positive transformation and outcomes. Use aspirational, forward-looking language. Focus on what the user will gain, achieve, or become.'
        },
        'B': {
          strategy: 'problem_focused', 
          prompt: 'Create problem-focused ad copy. Start by identifying a specific pain point or frustration. Show empathy and understanding. Then position your offer as the direct solution to that problem.'
        },
        'C': {
          strategy: 'story_driven',
          prompt: 'Create story-driven ad copy. Tell a brief, relatable story or scenario. Use a narrative structure with a character your audience can relate to. Make it human, emotional, and conversational.'
        }
      };

      const strategy = strategies[variantType];
      if (!strategy) {
        throw new Error(`Invalid variant type: ${variantType}`);
      }

      const payload = {
        ad_data: adData,
        variant_type: variantType,
        strategy: strategy.strategy,
        prompt_modifier: strategy.prompt,
        creative_controls: options
      };

      const response = await apiClient.post('/api/creative/regenerate-variant', payload);
      
      return {
        success: true,
        data: response.data
      };
    } catch (error) {
      console.error(`❌ CreativeControlsService: Error regenerating variant ${variantType}:`, error);
      
      throw new Error(
        error.response?.data?.message || 
        error.message || 
        `Failed to regenerate variant ${variantType}`
      );
    }
  }

}

const creativeControlsService = new CreativeControlsService();
export default creativeControlsService;
