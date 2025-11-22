import { useState, useEffect, useCallback } from 'react';
import { useAuth } from '../services/authContext';
import {
  getCreditBalance,
  getCreditCosts,
  hasEnoughCredits as checkHasEnough,
  formatCredits as formatCreditAmount
} from '../services/creditService';
import toast from 'react-hot-toast';
import logger from '../utils/logger';

// ✅ MIGRATED: Now uses backend credit service for all operations
// This prevents race conditions and provides automatic refunds

/**
 * Hook for managing user credits via backend API
 */
export const useCredits = () => {
  const { user } = useAuth();
  const [credits, setCredits] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [creditCosts, setCreditCosts] = useState({});

  // Fetch credit costs on mount
  useEffect(() => {
    const loadCosts = async () => {
      const result = await getCreditCosts();
      if (result.success) {
        setCreditCosts(result.costs);
      }
    };
    loadCosts();
  }, []);

  // Fetch credits from backend
  const fetchCredits = useCallback(async () => {
    if (!user?.id) {
      setLoading(false);
      return;
    }

    try {
      setLoading(true);
      const result = await getCreditBalance();

      if (result.success) {
        setCredits({
          credits: result.data.credits,
          monthlyAllowance: result.data.monthly_allowance,
          bonusCredits: result.data.bonus_credits,
          totalUsed: result.data.total_used,
          subscriptionTier: result.data.subscription_tier,
          isUnlimited: result.data.is_unlimited,
          lastReset: result.data.last_reset
        });
        setError(null);
      } else {
        setError(result.error);
      }
    } catch (err) {
      logger.error('Error fetching credits:', err);
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, [user?.id]);

  // Initial fetch - backend handles all updates
  useEffect(() => {
    fetchCredits();

    // ✅ Poll for updates every 30 seconds
    // This replaces real-time subscriptions and ensures we get backend-authoritative data
    const interval = setInterval(() => {
      if (user?.id) {
        fetchCredits();
      }
    }, 30000);

    return () => clearInterval(interval);
  }, [fetchCredits, user?.id]);

  // ⚠️ DEPRECATED: Analysis endpoint handles credit deduction automatically
  // This is kept for backwards compatibility but shouldn't be used
  const useCredits = async (operation, quantity = 1, options = {}) => {
    logger.warn('⚠️ useCredits() is deprecated. Credits are now deducted automatically by the analysis endpoint.');

    // Just refresh credits to get latest balance
    await fetchCredits();

    return { success: true, message: 'Credits managed by backend' };
  };

  // Check if user has enough credits for an operation
  const hasEnoughCredits = (operation, quantity = 1) => {
    if (!credits || credits.credits === null) return false;

    // Check unlimited
    if (credits.isUnlimited || credits.credits === 'unlimited' || credits.credits >= 999999) {
      return true;
    }

    const required = creditCosts[operation] * quantity || 0;
    return credits.credits >= required;
  };

  // Get credit requirement for an operation
  const getCreditRequirement = (operation, quantity = 1) => {
    return creditCosts[operation] * quantity || 0;
  };

  // ⚠️ DEPRECATED: Backend handles credit deduction AND refund automatically
  // Just execute the action - credits are managed server-side
  const executeWithCredits = async (operation, action, options = {}) => {
    const { quantity = 1, showToasts = true } = options;

    logger.debug('📊 Checking credits before operation:', {
      operation,
      quantity,
      currentCredits: credits?.credits,
      required: getCreditRequirement(operation, quantity)
    });

    // Check if credits are available (pre-flight check)
    if (!hasEnoughCredits(operation, quantity)) {
      const required = getCreditRequirement(operation, quantity);
      const available = credits?.credits || 0;

      if (showToasts) {
        toast.error(
          `Insufficient credits: ${operation} requires ${required} credits, but you only have ${available}`,
          { duration: 5000 }
        );
      }
      return { success: false, error: 'Insufficient credits' };
    }

    try {
      // ✅ FIXED: Just execute the action
      // Backend handles credit deduction automatically (see /api/ads/analyze)
      const result = await action();

      // Refresh credits after operation
      await fetchCredits();

      if (showToasts) {
        toast.success(`Operation completed successfully!`, { duration: 3000 });
      }

      return { success: true, result };
    } catch (error) {
      logger.error('Error in executeWithCredits:', error);

      // ✅ Backend automatically refunds credits on failure
      // Refresh to get updated balance and notify user
      const beforeRefund = credits?.credits || 0;
      await fetchCredits();
      const afterRefund = credits?.credits || 0;

      // Show refund notification if credits were restored
      if (showToasts && afterRefund > beforeRefund) {
        const refundedAmount = afterRefund - beforeRefund;
        toast.success(
          `${refundedAmount} credit${refundedAmount > 1 ? 's' : ''} refunded to your account`,
          {
            duration: 5000,
            icon: '💰'
          }
        );
      }

      return { success: false, error: error.message };
    }
  };

  // Get formatted credit display
  const getFormattedCredits = () => {
    if (loading) return 'Loading...';
    if (!credits) return '0';
    return formatCreditAmount(credits.credits);
  };

  // Get credit status color
  const getCreditStatusColor = () => {
    if (!credits) return 'error';

    if (credits.isUnlimited || credits.credits === 'unlimited' || credits.credits >= 999999) {
      return 'success';
    }

    if (credits.monthlyAllowance === 0) return 'error';

    const percentage = (credits.credits / credits.monthlyAllowance) * 100;
    if (percentage > 50) return 'success';
    if (percentage > 20) return 'warning';
    return 'error';
  };

  // Get credit percentage used
  const getCreditPercentage = () => {
    if (!credits) return 100;
    // Check for unlimited credits
    if (credits.credits === 'unlimited' || credits.credits >= 999999) return 0;
    if (credits.monthlyAllowance === 0 || credits.monthlyAllowance >= 999999) return 0;
    
    const used = credits.monthlyAllowance - credits.credits;
    return Math.min(100, Math.max(0, (used / credits.monthlyAllowance) * 100));
  };

  // Get days until reset using actual last_reset date from database
  const getDaysUntilReset = () => {
    if (!credits?.lastReset) {
      // Fallback to next month calculation if no reset date
      const now = new Date();
      const nextMonth = new Date(now.getFullYear(), now.getMonth() + 1, 1);
      const diffTime = nextMonth - now;
      return Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    }
    
    const lastReset = new Date(credits.lastReset);
    const nextReset = new Date(lastReset.getFullYear(), lastReset.getMonth() + 1, 1);
    const now = new Date();
    
    // If we're past the next reset date, calculate from current month
    if (now > nextReset) {
      const currentNextReset = new Date(now.getFullYear(), now.getMonth() + 1, 1);
      const diffTime = currentNextReset - now;
      return Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    }
    
    const diffTime = nextReset - now;
    return Math.ceil(diffTime / (1000 * 60 * 60 * 24));
  };

  return {
    // Credit data
    credits: credits?.credits || 0,
    monthlyAllowance: credits?.monthlyAllowance || 0,
    totalUsed: credits?.totalUsed || 0,
    bonusCredits: credits?.bonusCredits || 0,
    
    // Status
    loading,
    error,
    
    // Actions
    refreshCredits: fetchCredits,
    useCredits,
    executeWithCredits,
    
    // Checks
    hasEnoughCredits,
    getCreditRequirement,
    
    // Display helpers
    getFormattedCredits,
    getCreditStatusColor,
    getCreditPercentage,
    getDaysUntilReset,
    
    // Constants
    CREDIT_COSTS: creditCosts
  };
};

export default useCredits;