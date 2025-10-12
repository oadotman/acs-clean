import toast from 'react-hot-toast';
import { SUBSCRIPTION_TIERS, PLAN_LIMITS, PRICING_PLANS } from '../constants/plans';

/**
 * Feature Access Control System
 * Checks user permissions and shows upgrade notifications
 */

export const FEATURES = {
  // Core features
  FURTHER_IMPROVE: 'further_improve',
  PSYCHOLOGY_ANALYSIS: 'psychology_analysis',
  REPORTS: 'reports',
  WHITE_LABEL: 'white_label',
  INTEGRATIONS: 'integrations',
  API_ACCESS: 'api_access',
  
  // Advanced features
  BATCH_ANALYSIS: 'batch_analysis',
  ADVANCED_EXPORTS: 'advanced_exports',
  PRIORITY_SUPPORT: 'priority_support',
  DEDICATED_SUPPORT: 'dedicated_support',
  
  // Usage limits
  AD_ANALYSIS_LIMIT: 'ad_analysis_limit'
};

/**
 * Feature requirements mapping
 * Defines which tier is required for each feature
 */
export const FEATURE_REQUIREMENTS = {
  [FEATURES.FURTHER_IMPROVE]: SUBSCRIPTION_TIERS.GROWTH,
  [FEATURES.PSYCHOLOGY_ANALYSIS]: SUBSCRIPTION_TIERS.GROWTH,
  [FEATURES.REPORTS]: SUBSCRIPTION_TIERS.AGENCY_STANDARD,
  [FEATURES.WHITE_LABEL]: SUBSCRIPTION_TIERS.AGENCY_STANDARD,
  [FEATURES.INTEGRATIONS]: SUBSCRIPTION_TIERS.AGENCY_STANDARD,
  [FEATURES.API_ACCESS]: SUBSCRIPTION_TIERS.AGENCY_PREMIUM,
  [FEATURES.BATCH_ANALYSIS]: SUBSCRIPTION_TIERS.GROWTH,
  [FEATURES.ADVANCED_EXPORTS]: SUBSCRIPTION_TIERS.GROWTH,
  [FEATURES.PRIORITY_SUPPORT]: SUBSCRIPTION_TIERS.AGENCY_STANDARD,
  [FEATURES.DEDICATED_SUPPORT]: SUBSCRIPTION_TIERS.AGENCY_UNLIMITED
};

/**
 * Feature descriptions for toast messages
 */
export const FEATURE_DESCRIPTIONS = {
  [FEATURES.FURTHER_IMPROVE]: {
    name: 'Further Improve',
    description: 'Iteratively enhance your ad copy with AI-powered optimization',
    benefits: ['Multiple improvement iterations', 'Advanced AI optimization', 'Performance tracking']
  },
  [FEATURES.PSYCHOLOGY_ANALYSIS]: {
    name: 'Psychology Analysis',
    description: 'Deep psychological scoring of your ad copy',
    benefits: ['15 psychological triggers analysis', 'Persuasion scoring', 'Emotional impact metrics']
  },
  [FEATURES.REPORTS]: {
    name: 'Custom Reports',
    description: 'Generate detailed analysis reports',
    benefits: ['PDF/Excel export', 'Client-ready reports', 'Performance analytics']
  },
  [FEATURES.WHITE_LABEL]: {
    name: 'White-label',
    description: 'Brand the platform with your company identity',
    benefits: ['Custom branding', 'Remove AdCopySurge branding', 'Professional client experience']
  },
  [FEATURES.INTEGRATIONS]: {
    name: 'Integrations',
    description: 'Connect with popular marketing platforms',
    benefits: ['Facebook Ads integration', 'Google Ads sync', 'CRM connections']
  },
  [FEATURES.API_ACCESS]: {
    name: 'API Access',
    description: 'Programmatic access to analysis features',
    benefits: ['REST API endpoints', 'Bulk processing', 'Custom integrations']
  },
  [FEATURES.BATCH_ANALYSIS]: {
    name: 'Batch Analysis',
    description: 'Analyze multiple ads simultaneously',
    benefits: ['Process up to 50 ads at once', 'Time-saving bulk operations', 'Campaign-wide optimization']
  },
  [FEATURES.ADVANCED_EXPORTS]: {
    name: 'Advanced Exports',
    description: 'Export analysis data in multiple formats',
    benefits: ['PDF reports', 'Excel spreadsheets', 'CSV data export']
  },
  [FEATURES.PRIORITY_SUPPORT]: {
    name: 'Priority Support',
    description: 'Get faster response times and priority assistance',
    benefits: ['24-hour response time', 'Priority queue', 'Email support']
  },
  [FEATURES.DEDICATED_SUPPORT]: {
    name: 'Dedicated Support',
    description: 'Personal account manager and dedicated support',
    benefits: ['Dedicated account manager', '4-hour response time', 'Phone support']
  }
};

/**
 * Get user's current subscription tier
 */
export const getUserTier = (subscription) => {
  if (!subscription) return SUBSCRIPTION_TIERS.FREE;
  return subscription.subscription_tier || subscription.tier || SUBSCRIPTION_TIERS.FREE;
};

/**
 * Get user's plan limits
 */
export const getUserLimits = (subscription) => {
  const tier = getUserTier(subscription);
  return PLAN_LIMITS[tier] || PLAN_LIMITS[SUBSCRIPTION_TIERS.FREE];
};

/**
 * Check if user has access to a specific feature
 */
export const hasFeatureAccess = (feature, subscription) => {
  const userTier = getUserTier(subscription);
  const requiredTier = FEATURE_REQUIREMENTS[feature];
  
  if (!requiredTier) return true; // Feature doesn't require upgrade
  
  // Tier hierarchy check
  const tierHierarchy = [
    SUBSCRIPTION_TIERS.FREE,
    SUBSCRIPTION_TIERS.GROWTH,
    SUBSCRIPTION_TIERS.AGENCY_STANDARD,
    SUBSCRIPTION_TIERS.AGENCY_PREMIUM,
    SUBSCRIPTION_TIERS.AGENCY_UNLIMITED
  ];
  
  const userTierIndex = tierHierarchy.indexOf(userTier);
  const requiredTierIndex = tierHierarchy.indexOf(requiredTier);
  
  return userTierIndex >= requiredTierIndex;
};

/**
 * Check usage limits (like ad analysis count)
 */
export const checkUsageLimit = (feature, currentUsage, subscription) => {
  const limits = getUserLimits(subscription);
  
  switch (feature) {
    case FEATURES.AD_ANALYSIS_LIMIT:
      const limit = limits.adAnalyses;
      if (limit === -1) return { allowed: true, remaining: 'unlimited' }; // Unlimited
      return {
        allowed: currentUsage < limit,
        remaining: Math.max(0, limit - currentUsage),
        limit
      };
    default:
      return { allowed: true, remaining: 'unlimited' };
  }
};

/**
 * Get the next tier that would unlock a feature
 */
export const getRequiredTierForFeature = (feature) => {
  return FEATURE_REQUIREMENTS[feature] || SUBSCRIPTION_TIERS.FREE;
};

/**
 * Get plan information for a tier
 */
export const getPlanByTier = (tier) => {
  return PRICING_PLANS.find(plan => plan.tier === tier);
};

/**
 * Show upgrade toast notification
 */
export const showUpgradeToast = (feature, subscription, options = {}) => {
  const requiredTier = getRequiredTierForFeature(feature);
  const requiredPlan = getPlanByTier(requiredTier);
  const featureInfo = FEATURE_DESCRIPTIONS[feature];
  const currentTier = getUserTier(subscription);
  
  if (!featureInfo || !requiredPlan) {
    toast.error('This feature is not available in your current plan.');
    return;
  }

  const {
    showBenefits = false,
    customMessage = null,
    duration = 6000,
    actionButton = true
  } = options;

  let message = customMessage || 
    `${featureInfo.name} is available in the ${requiredPlan.name} plan and above.`;

  if (showBenefits && featureInfo.benefits) {
    message += `\n\nBenefits:\n• ${featureInfo.benefits.join('\n• ')}`;
  }

  message += `\n\nUpgrade to unlock this feature!`;

  const toastOptions = {
    duration,
    style: {
      background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
      color: 'white',
      padding: '16px',
      borderRadius: '8px',
      fontSize: '14px',
      maxWidth: '400px',
      textAlign: 'left'
    },
    icon: '⭐'
  };

  if (actionButton) {
    toast(
      (t) => (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
          <div>
            <strong>{featureInfo.name} - Premium Feature</strong>
            <br />
            {message}
          </div>
          <div style={{ display: 'flex', gap: '8px', justifyContent: 'flex-end' }}>
            <button
              onClick={() => {
                toast.dismiss(t.id);
                // Navigate to pricing page
                window.location.href = '/pricing';
              }}
              style={{
                background: 'rgba(255,255,255,0.2)',
                border: '1px solid rgba(255,255,255,0.3)',
                color: 'white',
                padding: '6px 12px',
                borderRadius: '4px',
                cursor: 'pointer',
                fontSize: '12px'
              }}
            >
              Upgrade Now
            </button>
            <button
              onClick={() => toast.dismiss(t.id)}
              style={{
                background: 'transparent',
                border: '1px solid rgba(255,255,255,0.3)',
                color: 'white',
                padding: '6px 12px',
                borderRadius: '4px',
                cursor: 'pointer',
                fontSize: '12px'
              }}
            >
              Dismiss
            </button>
          </div>
        </div>
      ),
      toastOptions
    );
  } else {
    toast.error(message, toastOptions);
  }
};

/**
 * Show usage limit reached toast
 */
export const showUsageLimitToast = (feature, usageInfo, subscription, options = {}) => {
  const requiredTier = getRequiredTierForFeature(feature);
  const requiredPlan = getPlanByTier(requiredTier);
  const currentTier = getUserTier(subscription);
  
  let message;
  
  if (feature === FEATURES.AD_ANALYSIS_LIMIT) {
    if (currentTier === SUBSCRIPTION_TIERS.FREE) {
      message = `You've reached your free plan limit of ${usageInfo.limit} analyses per month.`;
    } else {
      message = `You've reached your plan limit of ${usageInfo.limit} analyses per month.`;
    }
  } else {
    message = `You've reached your plan's usage limit for this feature.`;
  }

  const nextPlan = PRICING_PLANS.find(plan => {
    const tierIndex = Object.values(SUBSCRIPTION_TIERS).indexOf(plan.tier);
    const currentIndex = Object.values(SUBSCRIPTION_TIERS).indexOf(currentTier);
    return tierIndex > currentIndex;
  });

  if (nextPlan) {
    message += ` Upgrade to ${nextPlan.name} for ${nextPlan.limits.adAnalyses === -1 ? 'unlimited' : nextPlan.limits.adAnalyses} analyses.`;
  }

  toast(
    (t) => (
      <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
        <div>
          <strong>Usage Limit Reached</strong>
          <br />
          {message}
        </div>
        <div style={{ display: 'flex', gap: '8px', justifyContent: 'flex-end' }}>
          <button
            onClick={() => {
              toast.dismiss(t.id);
              window.location.href = '/pricing';
            }}
            style={{
              background: '#f59e0b',
              border: 'none',
              color: 'white',
              padding: '6px 12px',
              borderRadius: '4px',
              cursor: 'pointer',
              fontSize: '12px'
            }}
          >
            View Plans
          </button>
          <button
            onClick={() => toast.dismiss(t.id)}
            style={{
              background: 'transparent',
              border: '1px solid #ccc',
              color: '#666',
              padding: '6px 12px',
              borderRadius: '4px',
              cursor: 'pointer',
              fontSize: '12px'
            }}
          >
            Dismiss
          </button>
        </div>
      </div>
    ),
    {
      duration: 8000,
      style: {
        background: '#fff',
        color: '#333',
        padding: '16px',
        borderRadius: '8px',
        fontSize: '14px',
        maxWidth: '400px',
        border: '1px solid #f59e0b'
      }
    }
  );
};