/**
 * Shared pricing plans configuration
 * Single source of truth for all pricing tiers across the application
 */

export const SUBSCRIPTION_TIERS = {
  FREE: 'free',
  GROWTH: 'growth',
  AGENCY_STANDARD: 'agency_standard',
  AGENCY_PREMIUM: 'agency_premium',
  AGENCY_UNLIMITED: 'agency_unlimited'
};

// Features included in EVERY plan
export const EVERY_PLAN_FEATURES = [
  'Ad Copy Analyzer — Core effectiveness scoring & optimization insights',
  'Compliance Checker — Instantly flags policy violations before ad rejection',
  'Psychology Scorer — Evaluates 15 proven psychological triggers for persuasion',
  'Strategic A/B/C Testing — Creates benefit-focused, problem-focused, and story-driven test variations',
  'ROI Copy Generator — Produces premium-positioned, conversion-maximized versions',
  'Industry Optimizer — Adapts language and tone to your specific industry vertical',
  'Performance Forensics — Diagnoses underlying performance bottlenecks',
  'Brand Voice Engine — Ensures tone consistency and learns from past top ads',
  'Legal Risk Scanner — Detects legally risky claims; includes SOC 2 + GDPR compliance'
];

// Access control interface
export const PLAN_LIMITS = {
  [SUBSCRIPTION_TIERS.FREE]: {
    adAnalyses: 5,
    monthlyCredits: 5,
    teamMembers: 0,
    psychologyAnalysis: false,
    reports: 0,
    whiteLabel: false,
    integrations: false,
    support: 'community',
    apiAccess: false,
    strategicAbcTesting: 0
  },
  [SUBSCRIPTION_TIERS.GROWTH]: {
    adAnalyses: 100,
    monthlyCredits: 100,
    teamMembers: 0,
    psychologyAnalysis: true,
    reports: 0,
    whiteLabel: false,
    integrations: false,
    support: 'email',
    apiAccess: false,
    strategicAbcTesting: 33
  },
  [SUBSCRIPTION_TIERS.AGENCY_STANDARD]: {
    adAnalyses: 500,
    monthlyCredits: 500,
    teamMembers: 5,
    psychologyAnalysis: true,
    reports: 20,
    whiteLabel: true,
    integrations: true,
    support: 'priority',
    apiAccess: false,
    strategicAbcTesting: 165
  },
  [SUBSCRIPTION_TIERS.AGENCY_PREMIUM]: {
    adAnalyses: 1000,
    monthlyCredits: 1000,
    teamMembers: 10,
    psychologyAnalysis: true,
    reports: 50,
    whiteLabel: true,
    integrations: true,
    support: 'priority',
    apiAccess: true,
    strategicAbcTesting: 333
  },
  [SUBSCRIPTION_TIERS.AGENCY_UNLIMITED]: {
    adAnalyses: -1, // -1 represents unlimited
    monthlyCredits: -1, // -1 represents unlimited
    teamMembers: 20,
    psychologyAnalysis: true,
    reports: 100,
    whiteLabel: true,
    integrations: true,
    support: 'dedicated',
    apiAccess: true,
    strategicAbcTesting: -1 // unlimited
  }
};

// Helper function to check if a value is unlimited
export const isUnlimited = (value) => value === -1;

// Helper function to format limit display
export const formatLimit = (value) => {
  if (isUnlimited(value)) return 'Unlimited';
  if (value === 0) return '—';
  return value.toString();
};

export const PRICING_PLANS = [
  {
    id: SUBSCRIPTION_TIERS.FREE,
    name: 'Free',
    price: 0,
    period: 'forever',
    description: 'Perfect for getting started',
    buttonText: 'Get Started',
    cta: 'Start Free Scan',
    popular: false,
    tier: 'free',
    limits: PLAN_LIMITS[SUBSCRIPTION_TIERS.FREE]
  },
  {
    id: SUBSCRIPTION_TIERS.GROWTH,
    name: 'Growth',
    price: 39,
    period: 'month',
    description: 'For serious marketers managing $50K–$500K/month',
    buttonText: 'Upgrade to Growth',
    cta: 'Optimize Your ROI',
    popular: true,
    tier: 'growth',
    limits: PLAN_LIMITS[SUBSCRIPTION_TIERS.GROWTH]
  },
  {
    id: SUBSCRIPTION_TIERS.AGENCY_STANDARD,
    name: 'Agency Standard',
    price: 99,
    period: 'month',
    description: 'Avg agency adds $180K/year revenue',
    buttonText: 'Upgrade to Agency Standard',
    cta: 'Scale Your Agency',
    popular: false,
    tier: 'agency_standard',
    limits: PLAN_LIMITS[SUBSCRIPTION_TIERS.AGENCY_STANDARD]
  },
  {
    id: SUBSCRIPTION_TIERS.AGENCY_PREMIUM,
    name: 'Agency Premium',
    price: 199,
    period: 'month',
    description: 'For established agencies with high volume',
    buttonText: 'Upgrade to Agency Premium',
    cta: 'Premium Growth',
    popular: false,
    tier: 'agency_premium',
    limits: PLAN_LIMITS[SUBSCRIPTION_TIERS.AGENCY_PREMIUM]
  },
  {
    id: SUBSCRIPTION_TIERS.AGENCY_UNLIMITED,
    name: 'Agency Unlimited',
    price: 249,
    period: 'month',
    description: 'Risk-free: Land 1 new client in 60 days or we refund + give 3 months free',
    buttonText: 'Upgrade to Agency Unlimited',
    cta: 'Dominate Your Market',
    popular: false,
    tier: 'agency_unlimited',
    limits: PLAN_LIMITS[SUBSCRIPTION_TIERS.AGENCY_UNLIMITED]
  }
];

// Legacy mapping for backward compatibility
export const LEGACY_TIER_MAPPING = {
  'basic': SUBSCRIPTION_TIERS.GROWTH,
  'pro': SUBSCRIPTION_TIERS.AGENCY_UNLIMITED
};

// Paddle Price ID mapping with REAL Paddle product Price IDs
export const PADDLE_PRODUCT_MAPPING = {
  // Growth Plan
  [SUBSCRIPTION_TIERS.GROWTH]: {
    monthly: {
      priceId: 'pri_01k8gd5r03mg7p8gasg95pn105',  // Real Paddle Price ID
      name: 'Growth Plan (Monthly)',
      price: 39
    },
    yearly: {
      priceId: 'pri_01k8gdcc0z9qwz0htks3p6ydan',  // Real Paddle Price ID
      name: 'Growth Plan (Yearly)',
      price: Math.floor(39 * 12 * 0.8) // 20% discount = $374/year
    }
  },
  // Agency Standard Plan
  [SUBSCRIPTION_TIERS.AGENCY_STANDARD]: {
    monthly: {
      priceId: 'pri_01k8gdm6y2zqgcaqdv63ayk94k',  // Real Paddle Price ID
      name: 'Agency Standard Plan (Monthly)',
      price: 99
    },
    yearly: {
      priceId: 'pri_01k8gdk1hzrbf282v2schhg92j',  // Real Paddle Price ID
      name: 'Agency Standard Plan (Yearly)',
      price: Math.floor(99 * 12 * 0.8) // 20% discount = $950/year
    }
  },
  // Agency Premium Plan
  [SUBSCRIPTION_TIERS.AGENCY_PREMIUM]: {
    monthly: {
      priceId: 'pri_01k8ge5xmbdga7r7d5qddpnc4b',  // Real Paddle Price ID
      name: 'Agency Premium Plan (Monthly)',
      price: 199
    },
    yearly: {
      priceId: 'pri_01k8ge7f9kqqr5qk1kxt1kerf5',  // Real Paddle Price ID
      name: 'Agency Premium Plan (Yearly)',
      price: Math.floor(199 * 12 * 0.8) // 20% discount = $1,910/year
    }
  },
  // Agency Unlimited Plan
  [SUBSCRIPTION_TIERS.AGENCY_UNLIMITED]: {
    monthly: {
      priceId: 'pri_01k8geawnz6d88m4m447rtzqp9',  // Real Paddle Price ID
      name: 'Agency Unlimited Plan (Monthly)',
      price: 249
    },
    yearly: {
      priceId: 'pri_01k8geddk1apxh8wrq0k6x2bkk',  // Real Paddle Price ID
      name: 'Agency Unlimited Plan (Yearly)',
      price: Math.floor(249 * 12 * 0.8) // 20% discount = $2,390/year
    }
  },
  // Legacy support (monthly only for backward compatibility)
  'basic': {
    priceId: 'pri_01k8gd5r03mg7p8gasg95pn105',  // Maps to Growth Monthly
    name: 'Growth Plan',
    price: 39
  },
  'pro': {
    priceId: 'pri_01k8geawnz6d88m4m447rtzqp9',  // Maps to Agency Unlimited Monthly
    name: 'Agency Unlimited Plan',
    price: 249
  }
};

// Helper function to get product Price ID by billing period
export const getPaddleProductByPeriod = (tier, period = 'monthly') => {
  const tierMapping = PADDLE_PRODUCT_MAPPING[tier];
  if (!tierMapping) return null;
  
  // Handle legacy structure (basic/pro)
  if (tierMapping.priceId) {
    return tierMapping;
  }
  
  // Handle new nested structure
  return tierMapping[period] || tierMapping.monthly;
};

// Helper function to get just the Price ID
export const getPaddlePriceId = (tier, period = 'monthly') => {
  const product = getPaddleProductByPeriod(tier, period);
  return product ? product.priceId : null;
};

export default PRICING_PLANS;
