import toast from 'react-hot-toast';
import { SUBSCRIPTION_TIERS, PRICING_PLANS, PLAN_LIMITS } from '../constants/plans';
import { supabase } from '../lib/supabaseClientClean';

/**
 * Credit System for AdCopySurge
 * Tracks and manages user credits for various operations
 */

export const CREDIT_COSTS = {
  // Analysis operations
  BASIC_ANALYSIS: 1,
  FULL_ANALYSIS: 2,
  PSYCHOLOGY_ANALYSIS: 3,
  FURTHER_IMPROVE: 2,
  BATCH_ANALYSIS_PER_AD: 1,
  
  // Export operations
  BASIC_EXPORT: 0, // Free for all users
  ADVANCED_EXPORT: 1,
  BULK_EXPORT: 2,
  
  // Report generation
  BASIC_REPORT: 1,
  DETAILED_REPORT: 3,
  WHITE_LABEL_REPORT: 5,
  
  // API calls
  API_ANALYSIS_CALL: 1,
  API_BATCH_CALL: 2,
  
  // Premium features
  BRAND_VOICE_TRAINING: 5,
  COMPLIANCE_SCAN: 2,
  LEGAL_RISK_SCAN: 3
};

export const PLAN_CREDITS = {
  [SUBSCRIPTION_TIERS.FREE]: {
    monthly: 5,
    rollover: false,
    bonusCredits: 0
  },
  [SUBSCRIPTION_TIERS.GROWTH]: {
    monthly: 100,
    rollover: true,
    maxRollover: 50, // Can rollover up to 50 credits
    bonusCredits: 20 // Signup bonus
  },
  [SUBSCRIPTION_TIERS.AGENCY_STANDARD]: {
    monthly: 500,
    rollover: true,
    maxRollover: 250,
    bonusCredits: 100
  },
  [SUBSCRIPTION_TIERS.AGENCY_PREMIUM]: {
    monthly: 1000,
    rollover: true,
    maxRollover: 500,
    bonusCredits: 200
  },
  [SUBSCRIPTION_TIERS.AGENCY_UNLIMITED]: {
    monthly: -1, // Unlimited
    rollover: false,
    bonusCredits: 0
  }
};

/**
 * Get user's current credit balance
 */
export const getUserCredits = async (userId) => {
  try {
    console.log('💳 Getting user credits for:', userId);
    
    // Try to get credits from Supabase
    const { data, error } = await supabase
      .from('user_credits')
      .select('*')
      .eq('user_id', userId)
      .single();

    if (error && error.code !== 'PGRST116') {
      console.warn('⚠️ Error fetching user credits from DB:', error);
      // Fallback to localStorage-based credits
      return getLocalCredits(userId);
    }

    // If no record exists, create one
    if (!data) {
      console.log('🆕 No user credits record found, initializing...');
      return await initializeUserCredits(userId);
    }

    console.log('✅ Retrieved user credits from DB:', data);
    return {
      credits: data.current_credits || 0,
      monthlyAllowance: data.monthly_allowance || 0,
      lastReset: data.last_reset,
      totalUsed: data.total_used || 0,
      bonusCredits: data.bonus_credits || 0,
      subscriptionTier: data.subscription_tier || SUBSCRIPTION_TIERS.FREE
    };
  } catch (error) {
    console.error('❌ Error in getUserCredits:', error);
    // Fallback to localStorage-based credits
    return getLocalCredits(userId);
  }
};

// Fallback localStorage-based credit system
const getLocalCredits = (userId) => {
  try {
    const stored = localStorage.getItem(`credits_${userId}`);
    if (stored) {
      const credits = JSON.parse(stored);
      console.log('💾 Using localStorage credits:', credits);
      return credits;
    }
  } catch (error) {
    console.error('Error reading localStorage credits:', error);
  }
  
  // Default credits for new user
  const defaultCredits = {
    credits: PLAN_LIMITS[SUBSCRIPTION_TIERS.FREE].adAnalyses,
    monthlyAllowance: PLAN_LIMITS[SUBSCRIPTION_TIERS.FREE].adAnalyses,
    lastReset: new Date().toISOString(),
    totalUsed: 0,
    bonusCredits: 0,
    subscriptionTier: SUBSCRIPTION_TIERS.FREE
  };
  
  localStorage.setItem(`credits_${userId}`, JSON.stringify(defaultCredits));
  console.log('🆕 Initialized localStorage credits:', defaultCredits);
  return defaultCredits;
};

/**
 * Initialize credits for a new user
 */
export const initializeUserCredits = async (userId, subscriptionTier = SUBSCRIPTION_TIERS.FREE) => {
  try {
    const planCredits = PLAN_CREDITS[subscriptionTier];
    const monthlyCredits = planCredits.monthly === -1 ? 999999 : planCredits.monthly;
    
    const creditData = {
      user_id: userId,
      current_credits: monthlyCredits + (planCredits.bonusCredits || 0),
      monthly_allowance: monthlyCredits,
      bonus_credits: planCredits.bonusCredits || 0,
      total_used: 0,
      last_reset: new Date().toISOString(),
      subscription_tier: subscriptionTier
    };

    const { data, error } = await supabase
      .from('user_credits')
      .insert(creditData)
      .select()
      .single();

    if (error) {
      console.error('Error initializing user credits:', error);
      return { credits: 0, monthlyAllowance: 0 };
    }

    return {
      credits: data.current_credits,
      monthlyAllowance: data.monthly_allowance,
      bonusCredits: data.bonus_credits
    };
  } catch (error) {
    console.error('Error initializing credits:', error);
    return { credits: 0, monthlyAllowance: 0 };
  }
};

/**
 * Consume credits for an operation
 */
export const consumeCredits = async (userId, operation, quantity = 1) => {
  try {
    const creditCost = CREDIT_COSTS[operation] * quantity;
    
    console.log(`💰 Consuming ${creditCost} credits for ${operation} (qty: ${quantity})`);
    
    if (!creditCost) {
      console.log('✅ Free operation, no credits needed');
      return { success: true, remaining: null }; // Free operation
    }

    // Get current credits
    const currentCredits = await getUserCredits(userId);
    
    // Check if unlimited plan (Agency Unlimited = -1 ad analyses)
    const isUnlimitedPlan = currentCredits.subscriptionTier === SUBSCRIPTION_TIERS.AGENCY_UNLIMITED ||
                           currentCredits.monthlyAllowance === -1 ||
                           currentCredits.credits >= 999999;
    
    if (isUnlimitedPlan) {
      console.log('♾️ Unlimited plan detected, allowing operation');
      return { success: true, remaining: 'unlimited' };
    }

    // Check if sufficient credits
    if (currentCredits.credits < creditCost) {
      console.log(`❌ Insufficient credits: need ${creditCost}, have ${currentCredits.credits}`);
      return {
        success: false,
        error: 'Insufficient credits',
        required: creditCost,
        available: currentCredits.credits
      };
    }

    // Try to consume credits in database first
    try {
      const { data, error } = await supabase
        .from('user_credits')
        .update({
          current_credits: currentCredits.credits - creditCost,
          total_used: (currentCredits.totalUsed || 0) + creditCost,
          updated_at: new Date().toISOString()
        })
        .eq('user_id', userId)
        .select()
        .single();

      if (!error && data) {
        console.log(`✅ Credits consumed in DB: ${creditCost}, remaining: ${data.current_credits}`);
        await logCreditTransaction(userId, operation, -creditCost, `Used for ${operation}`);
        return {
          success: true,
          remaining: data.current_credits,
          consumed: creditCost
        };
      } else {
        console.warn('⚠️ DB update failed, falling back to localStorage');
      }
    } catch (dbError) {
      console.warn('⚠️ DB error, falling back to localStorage:', dbError);
    }

    // Fallback to localStorage
    const newCredits = currentCredits.credits - creditCost;
    const updatedCredits = {
      ...currentCredits,
      credits: newCredits,
      totalUsed: (currentCredits.totalUsed || 0) + creditCost
    };
    
    localStorage.setItem(`credits_${userId}`, JSON.stringify(updatedCredits));
    console.log(`✅ Credits consumed in localStorage: ${creditCost}, remaining: ${newCredits}`);
    
    return {
      success: true,
      remaining: newCredits,
      consumed: creditCost
    };
    
  } catch (error) {
    console.error('❌ Error in consumeCredits:', error);
    return { success: false, error: 'System error' };
  }
};

/**
 * Add bonus credits
 */
export const addBonusCredits = async (userId, amount, reason = 'Bonus credits') => {
  try {
    const { data, error } = await supabase
      .from('user_credits')
      .select('current_credits, bonus_credits')
      .eq('user_id', userId)
      .single();

    if (error) {
      console.error('Error fetching credits for bonus:', error);
      return { success: false };
    }

    const { error: updateError } = await supabase
      .from('user_credits')
      .update({
        current_credits: (data.current_credits || 0) + amount,
        bonus_credits: (data.bonus_credits || 0) + amount,
        updated_at: new Date().toISOString()
      })
      .eq('user_id', userId);

    if (updateError) {
      console.error('Error adding bonus credits:', updateError);
      return { success: false };
    }

    // Log the transaction
    await logCreditTransaction(userId, 'BONUS_CREDITS', amount, reason);

    return { success: true, added: amount };
  } catch (error) {
    console.error('Error adding bonus credits:', error);
    return { success: false };
  }
};

/**
 * Reset monthly credits (called by cron job)
 */
export const resetMonthlyCredits = async (userId, subscriptionTier) => {
  try {
    const planCredits = PLAN_CREDITS[subscriptionTier];
    const currentCredits = await getUserCredits(userId);
    
    let newCredits = planCredits.monthly === -1 ? 999999 : planCredits.monthly;
    
    // Handle rollover for eligible plans
    if (planCredits.rollover && currentCredits.credits > 0) {
      const rolloverAmount = Math.min(currentCredits.credits, planCredits.maxRollover || 0);
      newCredits += rolloverAmount;
      
      if (rolloverAmount > 0) {
        await logCreditTransaction(userId, 'ROLLOVER_CREDITS', rolloverAmount, 'Monthly rollover');
      }
    }

    const { error } = await supabase
      .from('user_credits')
      .update({
        current_credits: newCredits,
        monthly_allowance: planCredits.monthly === -1 ? 999999 : planCredits.monthly,
        last_reset: new Date().toISOString(),
        updated_at: new Date().toISOString()
      })
      .eq('user_id', userId);

    if (error) {
      console.error('Error resetting monthly credits:', error);
      return { success: false };
    }

    // Log the reset
    await logCreditTransaction(userId, 'MONTHLY_RESET', newCredits, 'Monthly credit reset');

    return { success: true, newBalance: newCredits };
  } catch (error) {
    console.error('Error in resetMonthlyCredits:', error);
    return { success: false };
  }
};

/**
 * Log credit transaction for history
 */
export const logCreditTransaction = async (userId, operation, amount, description) => {
  try {
    await supabase
      .from('credit_transactions')
      .insert({
        user_id: userId,
        operation,
        amount,
        description,
        created_at: new Date().toISOString()
      });
  } catch (error) {
    console.error('Error logging credit transaction:', error);
  }
};

/**
 * Get credit transaction history
 */
export const getCreditHistory = async (userId, limit = 50) => {
  try {
    const { data, error } = await supabase
      .from('credit_transactions')
      .select('*')
      .eq('user_id', userId)
      .order('created_at', { ascending: false })
      .limit(limit);

    if (error) {
      console.error('Error fetching credit history:', error);
      return [];
    }

    return data || [];
  } catch (error) {
    console.error('Error in getCreditHistory:', error);
    return [];
  }
};

/**
 * Check if user has enough credits for an operation
 */
export const checkCredits = (currentCredits, operation, quantity = 1) => {
  const required = CREDIT_COSTS[operation] * quantity;
  
  if (!required) return { hasEnough: true, required: 0 };
  if (currentCredits === 'unlimited' || currentCredits >= 999999) {
    return { hasEnough: true, required, remaining: 'unlimited' };
  }
  
  return {
    hasEnough: currentCredits >= required,
    required,
    available: currentCredits,
    shortage: Math.max(0, required - currentCredits)
  };
};

/**
 * Format credits for display
 */
export const formatCredits = (credits) => {
  if (credits === 'unlimited' || credits >= 999999) return 'Unlimited';
  if (credits === null || credits === undefined) return '0';
  return credits.toLocaleString();
};

/**
 * Get credit color based on remaining amount and plan
 */
export const getCreditColor = (current, monthly) => {
  if (current === 'unlimited' || current >= 999999) return 'success';
  if (monthly === 0) return 'error';
  
  const percentage = (current / monthly) * 100;
  if (percentage > 50) return 'success';
  if (percentage > 20) return 'warning';
  return 'error';
};

/**
 * Get team member limits for subscription tier
 */
export const getTeamMemberLimits = (subscriptionTier) => {
  const limits = PLAN_LIMITS[subscriptionTier] || PLAN_LIMITS[SUBSCRIPTION_TIERS.FREE];
  return {
    maxTeamMembers: limits.teamMembers || 0,
    canInviteTeamMembers: (limits.teamMembers || 0) > 0
  };
};

/**
 * Check if user can invite more team members
 */
export const canInviteTeamMembers = (subscriptionTier, currentTeamCount = 0) => {
  const limits = getTeamMemberLimits(subscriptionTier);
  return {
    canInvite: limits.canInviteTeamMembers && currentTeamCount < limits.maxTeamMembers,
    maxAllowed: limits.maxTeamMembers,
    currentCount: currentTeamCount,
    remaining: Math.max(0, limits.maxTeamMembers - currentTeamCount)
  };
};

/**
 * Get monthly credit limit for subscription tier
 */
export const getMonthlyCredits = (subscriptionTier) => {
  const limits = PLAN_LIMITS[subscriptionTier] || PLAN_LIMITS[SUBSCRIPTION_TIERS.FREE];
  return limits.monthlyCredits || limits.adAnalyses || 0;
};

/**
 * Check if subscription tier has unlimited credits
 */
export const hasUnlimitedCredits = (subscriptionTier) => {
  const limits = PLAN_LIMITS[subscriptionTier];
  return limits && (limits.monthlyCredits === -1 || limits.adAnalyses === -1);
};

/**
 * Show credit insufficient toast
 */
export const showInsufficientCreditsToast = (operation, required, available) => {
  const operationName = operation.toLowerCase().replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
  
  toast((t) => (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
      <div>
        <strong>Insufficient Credits</strong>
        <br />
        {operationName} requires {required} credit{required !== 1 ? 's' : ''}, but you only have {available} remaining.
      </div>
      <div style={{ display: 'flex', gap: '8px', justifyContent: 'flex-end' }}>
        <button
          onClick={() => {
            toast.dismiss(t.id);
            window.location.href = '/billing';
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
          Buy Credits
        </button>
        <button
          onClick={() => {
            toast.dismiss(t.id);
            window.location.href = '/pricing';
          }}
          style={{
            background: '#3b82f6',
            border: 'none',
            color: 'white',
            padding: '6px 12px',
            borderRadius: '4px',
            cursor: 'pointer',
            fontSize: '12px'
          }}
        >
          Upgrade Plan
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
  ), {
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
  });
};