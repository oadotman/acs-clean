import { useMemo } from 'react';
import { useAuth } from '../services/authContext';
import { 
  FEATURES, 
  hasFeatureAccess, 
  showUpgradeToast, 
  showUsageLimitToast,
  checkUsageLimit,
  getUserLimits,
  getUserTier 
} from '../utils/featureAccess';

/**
 * Hook to provide feature access control throughout the app
 * @param {Object} options - Configuration options
 * @returns {Object} Feature access methods and state
 */
export const useFeatureAccess = (options = {}) => {
  const { subscription } = useAuth();
  
  // Memoize user tier and limits to prevent unnecessary recalculations
  const userTier = useMemo(() => getUserTier(subscription), [subscription]);
  const userLimits = useMemo(() => getUserLimits(subscription), [subscription]);

  /**
   * Check if user has access to a feature
   * @param {string} feature - Feature to check
   * @returns {boolean}
   */
  const hasAccess = (feature) => {
    return hasFeatureAccess(feature, subscription);
  };

  /**
   * Show upgrade toast for a feature
   * @param {string} feature - Feature requiring upgrade
   * @param {Object} toastOptions - Toast customization options
   */
  const showUpgrade = (feature, toastOptions = {}) => {
    showUpgradeToast(feature, subscription, toastOptions);
  };

  /**
   * Check usage limits and show toast if exceeded
   * @param {string} feature - Feature to check
   * @param {number} currentUsage - Current usage count
   * @param {Object} options - Additional options
   * @returns {Object} Usage status
   */
  const checkUsage = (feature, currentUsage, options = {}) => {
    const usageInfo = checkUsageLimit(feature, currentUsage, subscription);
    
    if (!usageInfo.allowed && options.showToast !== false) {
      showUsageLimitToast(feature, usageInfo, subscription);
    }
    
    return usageInfo;
  };

  /**
   * Execute a feature action with access control
   * @param {string} feature - Feature to check
   * @param {Function} action - Function to execute if access granted
   * @param {Object} options - Configuration options
   */
  const executeWithAccess = async (feature, action, options = {}) => {
    if (!hasAccess(feature)) {
      showUpgrade(feature, options.upgradeToastOptions);
      return false;
    }
    
    try {
      await action();
      return true;
    } catch (error) {
      console.error(`Error executing feature ${feature}:`, error);
      return false;
    }
  };

  /**
   * Get feature access status for multiple features
   * @param {string[]} features - Array of features to check
   * @returns {Object} Access status for each feature
   */
  const getAccessStatus = (features) => {
    return features.reduce((acc, feature) => {
      acc[feature] = hasAccess(feature);
      return acc;
    }, {});
  };

  // Pre-computed access status for common features
  const commonAccess = useMemo(() => ({
    furtherImprove: hasAccess(FEATURES.FURTHER_IMPROVE),
    psychologyAnalysis: hasAccess(FEATURES.PSYCHOLOGY_ANALYSIS),
    reports: hasAccess(FEATURES.REPORTS),
    whiteLabel: hasAccess(FEATURES.WHITE_LABEL),
    integrations: hasAccess(FEATURES.INTEGRATIONS),
    apiAccess: hasAccess(FEATURES.API_ACCESS),
    batchAnalysis: hasAccess(FEATURES.BATCH_ANALYSIS),
    advancedExports: hasAccess(FEATURES.ADVANCED_EXPORTS),
    prioritySupport: hasAccess(FEATURES.PRIORITY_SUPPORT),
    dedicatedSupport: hasAccess(FEATURES.DEDICATED_SUPPORT)
  }), [subscription]);

  return {
    // User info
    userTier,
    userLimits,
    subscription,
    
    // Access check methods
    hasAccess,
    getAccessStatus,
    commonAccess,
    
    // Usage methods
    checkUsage,
    
    // Action methods
    executeWithAccess,
    showUpgrade,
    
    // Feature constants
    FEATURES
  };
};

export default useFeatureAccess;