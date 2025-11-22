/**
 * Credit Service - Backend API Integration
 *
 * ✅ MIGRATED: Now uses backend credit service instead of direct Supabase access
 * This provides:
 * - Atomic operations (prevents race conditions)
 * - Automatic refunds on failure
 * - Audit trail
 * - Single source of truth
 */

import apiClient from './apiClient';

/**
 * Get user's credit balance from backend
 * @returns {Promise<Object>} Credit balance information
 */
export const getCreditBalance = async () => {
  try {
    const response = await apiClient.get('/credits/balance');
    return {
      success: true,
      data: response.data
    };
  } catch (error) {
    console.error('Error fetching credit balance:', error);
    return {
      success: false,
      error: error.response?.data?.detail || error.message
    };
  }
};

/**
 * Consume credits for an operation
 *
 * ⚠️ NOTE: You usually don't need to call this directly.
 * The /api/ads/analyze endpoint handles credit deduction automatically.
 *
 * @param {string} operation - Operation type (e.g., 'FULL_ANALYSIS')
 * @param {number} quantity - Number of times to perform operation
 * @param {string} description - Optional description
 * @returns {Promise<Object>} Result with remaining credits
 */
export const consumeCredits = async (operation, quantity = 1, description = null) => {
  try {
    const response = await apiClient.post('/credits/consume', {
      operation,
      quantity,
      description
    });

    return {
      success: response.data.success,
      remaining: response.data.remaining,
      consumed: response.data.consumed,
      error: response.data.error
    };
  } catch (error) {
    console.error('Error consuming credits:', error);
    return {
      success: false,
      error: error.response?.data?.detail || error.message
    };
  }
};

/**
 * Get credit transaction history
 * @param {number} limit - Number of transactions to fetch
 * @returns {Promise<Object>} Transaction history
 */
export const getCreditHistory = async (limit = 50) => {
  try {
    const response = await apiClient.get(`/credits/history?limit=${limit}`);
    return {
      success: true,
      transactions: response.data.transactions,
      count: response.data.count
    };
  } catch (error) {
    console.error('Error fetching credit history:', error);
    return {
      success: false,
      error: error.response?.data?.detail || error.message,
      transactions: []
    };
  }
};

/**
 * Get credit costs for all operations
 * @returns {Promise<Object>} Credit costs and tier limits
 */
export const getCreditCosts = async () => {
  try {
    const response = await apiClient.get('/credits/costs');
    return {
      success: true,
      costs: response.data.costs,
      tiers: response.data.tiers
    };
  } catch (error) {
    console.error('Error fetching credit costs:', error);
    return {
      success: false,
      error: error.message,
      costs: {},
      tiers: {}
    };
  }
};

/**
 * Refund credits (admin/internal use)
 * @param {string} operation - Operation to refund
 * @param {number} quantity - Quantity to refund
 * @param {string} reason - Reason for refund
 * @returns {Promise<Object>} Refund result
 */
export const refundCredits = async (operation, quantity = 1, reason = 'Manual refund') => {
  try {
    const response = await apiClient.post('/credits/refund', null, {
      params: { operation, quantity, reason }
    });

    return {
      success: true,
      refunded: response.data.refunded,
      new_balance: response.data.new_balance,
      message: response.data.message
    };
  } catch (error) {
    console.error('Error refunding credits:', error);
    return {
      success: false,
      error: error.response?.data?.detail || error.message
    };
  }
};

/**
 * Check if user has enough credits for an operation
 * @param {number} currentCredits - Current credit balance
 * @param {string} operation - Operation type
 * @param {Object} costs - Credit costs object
 * @returns {boolean} Whether user has enough credits
 */
export const hasEnoughCredits = (currentCredits, operation, costs) => {
  if (currentCredits === 'unlimited' || currentCredits === 999999) {
    return true;
  }

  const required = costs[operation] || 0;
  return currentCredits >= required;
};

/**
 * Format credits for display
 * @param {number|string} credits - Credit amount
 * @returns {string} Formatted credit string
 */
export const formatCredits = (credits) => {
  if (credits === 'unlimited' || credits >= 999999) {
    return 'Unlimited';
  }
  if (credits === null || credits === undefined) {
    return '0';
  }
  return credits.toLocaleString();
};

export default {
  getCreditBalance,
  consumeCredits,
  getCreditHistory,
  getCreditCosts,
  refundCredits,
  hasEnoughCredits,
  formatCredits
};
