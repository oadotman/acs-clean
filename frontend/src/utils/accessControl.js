import { SUBSCRIPTION_TIERS, PLAN_LIMITS, isUnlimited } from '../constants/plans';

/**
 * Access Control Utilities for subscription-based feature gating
 */

// Helper function to get user's subscription tier
export const getUserTier = (user) => {
  if (!user || !user.subscription_tier) {
    return SUBSCRIPTION_TIERS.FREE;
  }
  return user.subscription_tier;
};

// Helper function to get plan limits for a tier
export const getPlanLimits = (tier) => {
  return PLAN_LIMITS[tier] || PLAN_LIMITS[SUBSCRIPTION_TIERS.FREE];
};

/**
 * Check if user can use a specific feature
 * @param {Object} user - User object with subscription info
 * @param {string} feature - Feature name (psychologyAnalysis, whiteLabel, integrations, apiAccess)
 * @returns {boolean}
 */
export const canUseFeature = (user, feature) => {
  const tier = getUserTier(user);
  const limits = getPlanLimits(tier);
  
  return limits[feature] || false;
};

/**
 * Check if user can generate reports
 * @param {Object} user - User object with subscription info
 * @param {number} currentUsage - Current number of reports used this month
 * @returns {boolean}
 */
export const canGenerateReport = (user, currentUsage = 0) => {
  const tier = getUserTier(user);
  const limits = getPlanLimits(tier);
  
  if (limits.reports === 0) return false;
  if (isUnlimited(limits.reports)) return true;
  
  return currentUsage < limits.reports;
};

/**
 * Get remaining quota for a specific resource
 * @param {Object} user - User object with subscription info
 * @param {string} resource - Resource name (adAnalyses, reports)
 * @param {number} currentUsage - Current usage this month
 * @returns {number|string} - Remaining quota or 'unlimited'
 */
export const getRemainingQuota = (user, resource, currentUsage = 0) => {
  const tier = getUserTier(user);
  const limits = getPlanLimits(tier);
  
  const limit = limits[resource];
  
  if (isUnlimited(limit)) return 'unlimited';
  if (typeof limit !== 'number') return 0;
  
  return Math.max(0, limit - currentUsage);
};

/**
 * Check if user has reached their quota limit
 * @param {Object} user - User object with subscription info
 * @param {string} resource - Resource name (adAnalyses, reports)
 * @param {number} currentUsage - Current usage this month
 * @returns {boolean}
 */
export const hasReachedLimit = (user, resource, currentUsage = 0) => {
  const remaining = getRemainingQuota(user, resource, currentUsage);
  return remaining !== 'unlimited' && remaining <= 0;
};

/**
 * Get support level for user's tier
 * @param {Object} user - User object with subscription info
 * @returns {string} - Support level
 */
export const getSupportLevel = (user) => {
  const tier = getUserTier(user);
  const limits = getPlanLimits(tier);
  return limits.support;
};

/**
 * Check if user can perform an action (considers both feature access and quota)
 * @param {Object} user - User object with subscription info
 * @param {string} action - Action to check
 * @param {Object} usage - Current usage stats
 * @returns {Object} - { canPerform: boolean, reason?: string, upgradeRequired?: string }
 */
export const canPerformAction = (user, action, usage = {}) => {
  const tier = getUserTier(user);
  const limits = getPlanLimits(tier);
  
  switch (action) {
    case 'analyzeAd':
      if (hasReachedLimit(user, 'adAnalyses', usage.adAnalyses || 0)) {
        return {
          canPerform: false,
          reason: 'Monthly ad analysis limit reached',
          upgradeRequired: getNextTierWithFeature('adAnalyses', limits.adAnalyses + 1)
        };
      }
      return { canPerform: true };
      
    case 'usePsychologyAnalysis':
      if (!canUseFeature(user, 'psychologyAnalysis')) {
        return {
          canPerform: false,
          reason: '15-Point Psychology Analysis not available in your plan',
          upgradeRequired: getNextTierWithFeature('psychologyAnalysis', true)
        };
      }
      return { canPerform: true };
      
    case 'generateReport':
      if (!canGenerateReport(user, usage.reports || 0)) {
        return {
          canPerform: false,
          reason: 'Monthly report limit reached',
          upgradeRequired: getNextTierWithFeature('reports', (usage.reports || 0) + 1)
        };
      }
      return { canPerform: true };
      
    case 'useWhiteLabel':
      if (!canUseFeature(user, 'whiteLabel')) {
        return {
          canPerform: false,
          reason: 'White-label branding not available in your plan',
          upgradeRequired: getNextTierWithFeature('whiteLabel', true)
        };
      }
      return { canPerform: true };
      
    case 'useIntegrations':
      if (!canUseFeature(user, 'integrations')) {
        return {
          canPerform: false,
          reason: 'Integrations not available in your plan',
          upgradeRequired: getNextTierWithFeature('integrations', true)
        };
      }
      return { canPerform: true };
      
    case 'useAPI':
      if (!canUseFeature(user, 'apiAccess')) {
        return {
          canPerform: false,
          reason: 'API access not available in your plan',
          upgradeRequired: getNextTierWithFeature('apiAccess', true)
        };
      }
      return { canPerform: true };
      
    default:
      return { canPerform: false, reason: 'Unknown action' };
  }
};

/**
 * Find the next tier that supports a specific feature requirement
 * @param {string} feature - Feature name
 * @param {any} requiredValue - Required value for the feature
 * @returns {string} - Recommended tier
 */
export const getNextTierWithFeature = (feature, requiredValue) => {
  const tiers = [
    SUBSCRIPTION_TIERS.FREE,
    SUBSCRIPTION_TIERS.GROWTH,
    SUBSCRIPTION_TIERS.AGENCY_STANDARD,
    SUBSCRIPTION_TIERS.AGENCY_PREMIUM,
    SUBSCRIPTION_TIERS.AGENCY_UNLIMITED
  ];
  
  for (const tier of tiers) {
    const limits = getPlanLimits(tier);
    const featureValue = limits[feature];
    
    if (typeof requiredValue === 'boolean') {
      if (featureValue === requiredValue) return tier;
    } else if (typeof requiredValue === 'number') {
      if (isUnlimited(featureValue) || featureValue >= requiredValue) {
        return tier;
      }
    }
  }
  
  return SUBSCRIPTION_TIERS.AGENCY_UNLIMITED; // Fallback to highest tier
};

/**
 * Get upgrade recommendations based on usage patterns
 * @param {Object} user - User object with subscription info
 * @param {Object} usage - Usage statistics
 * @returns {Object} - Upgrade recommendation
 */
export const getUpgradeRecommendation = (user, usage = {}) => {
  const tier = getUserTier(user);
  const limits = getPlanLimits(tier);
  
  // Check if user is approaching limits
  const warnings = [];
  const blockers = [];
  
  // Check ad analyses
  if (!isUnlimited(limits.adAnalyses)) {
    const used = usage.adAnalyses || 0;
    const remaining = limits.adAnalyses - used;
    const percentUsed = (used / limits.adAnalyses) * 100;
    
    if (remaining <= 0) {
      blockers.push({
        feature: 'Ad Analyses',
        issue: 'Monthly limit reached',
        suggestion: `Upgrade to get ${getNextTierLimit('adAnalyses', tier)} analyses per month`
      });
    } else if (percentUsed >= 80) {
      warnings.push({
        feature: 'Ad Analyses',
        issue: `${Math.round(percentUsed)}% of monthly limit used`,
        suggestion: 'Consider upgrading before you hit the limit'
      });
    }
  }
  
  // Check reports
  if (limits.reports > 0 && !isUnlimited(limits.reports)) {
    const used = usage.reports || 0;
    const remaining = limits.reports - used;
    const percentUsed = (used / limits.reports) * 100;
    
    if (remaining <= 0) {
      blockers.push({
        feature: 'Reports',
        issue: 'Monthly limit reached',
        suggestion: `Upgrade to get ${getNextTierLimit('reports', tier)} reports per month`
      });
    } else if (percentUsed >= 80) {
      warnings.push({
        feature: 'Reports',
        issue: `${Math.round(percentUsed)}% of monthly limit used`,
        suggestion: 'Consider upgrading for more reports'
      });
    }
  }
  
  return {
    currentTier: tier,
    shouldUpgrade: blockers.length > 0 || warnings.length > 1,
    blockers,
    warnings,
    recommendedTier: blockers.length > 0 
      ? getNextTier(tier)
      : warnings.length > 1 
        ? getNextTier(tier)
        : null
  };
};

/**
 * Get the next tier in the hierarchy
 * @param {string} currentTier - Current subscription tier
 * @returns {string} - Next tier
 */
export const getNextTier = (currentTier) => {
  const hierarchy = [
    SUBSCRIPTION_TIERS.FREE,
    SUBSCRIPTION_TIERS.GROWTH,
    SUBSCRIPTION_TIERS.AGENCY_STANDARD,
    SUBSCRIPTION_TIERS.AGENCY_PREMIUM,
    SUBSCRIPTION_TIERS.AGENCY_UNLIMITED
  ];
  
  const currentIndex = hierarchy.indexOf(currentTier);
  if (currentIndex === -1 || currentIndex === hierarchy.length - 1) {
    return currentTier; // Already at highest tier or unknown tier
  }
  
  return hierarchy[currentIndex + 1];
};

/**
 * Get the limit for a feature in the next tier
 * @param {string} feature - Feature name
 * @param {string} currentTier - Current tier
 * @returns {number|string} - Limit in next tier
 */
export const getNextTierLimit = (feature, currentTier) => {
  const nextTier = getNextTier(currentTier);
  const nextLimits = getPlanLimits(nextTier);
  const limit = nextLimits[feature];
  
  return isUnlimited(limit) ? 'Unlimited' : limit;
};

// Export all functions as a default object for easier importing
export default {
  getUserTier,
  getPlanLimits,
  canUseFeature,
  canGenerateReport,
  getRemainingQuota,
  hasReachedLimit,
  getSupportLevel,
  canPerformAction,
  getNextTierWithFeature,
  getUpgradeRecommendation,
  getNextTier,
  getNextTierLimit
};