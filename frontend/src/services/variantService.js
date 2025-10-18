import api from './apiService';

export const variantService = {
  // Generate new variants
  generateVariants: async (adCopy, platform = 'facebook', count = 3) => {
    try {
      const response = await api.post('/api/variants/generate', {
        ad_copy: adCopy,
        platform,
        count
      });
      return response.data;
    } catch (error) {
      console.error('Error generating variants:', error);
      throw error;
    }
  },

  // Regenerate a specific variant
  regenerateVariant: async (variantId, variantData) => {
    try {
      const response = await api.put(`/api/variants/${variantId}`, variantData);
      return response.data;
    } catch (error) {
      console.error('Error regenerating variant:', error);
      throw error;
    }
  },

  // Improve an existing variant
  improveVariant: async (variantId, instructions) => {
    try {
      const response = await api.post(`/api/variants/${variantId}/improve`, {
        instructions
      });
      return response.data;
    } catch (error) {
      console.error('Error improving variant:', error);
      throw error;
    }
  },

  // Get performance metrics for a variant
  getVariantMetrics: async (variantId) => {
    try {
      const response = await api.get(`/api/variants/${variantId}/metrics`);
      return response.data;
    } catch (error) {
      console.error('Error fetching variant metrics:', error);
      return null;
    }
  }
};

export default variantService;
