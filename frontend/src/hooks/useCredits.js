import { useState, useEffect, useCallback } from 'react';
import { useAuth } from '../services/authContext';
import { 
  getUserCredits, 
  consumeCredits, 
  checkCredits,
  formatCredits,
  getCreditColor,
  showInsufficientCreditsToast,
  CREDIT_COSTS 
} from '../utils/creditSystem';
import toast from 'react-hot-toast';

/**
 * Hook for managing user credits
 */
export const useCredits = () => {
  const { user } = useAuth();
  const [credits, setCredits] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Fetch credits
  const fetchCredits = useCallback(async () => {
    if (!user?.id) {
      setLoading(false);
      return;
    }

    try {
      setLoading(true);
      const creditData = await getUserCredits(user.id);
      setCredits(creditData);
      setError(null);
    } catch (err) {
      console.error('Error fetching credits:', err);
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, [user?.id]);

  // Initial fetch
  useEffect(() => {
    fetchCredits();
  }, [fetchCredits]);

  // Consume credits for an operation
  const useCredits = async (operation, quantity = 1, options = {}) => {
    if (!user?.id) {
      return { success: false, error: 'User not authenticated' };
    }

    try {
      const result = await consumeCredits(user.id, operation, quantity);
      
      if (result.success) {
        // Update local state
        setCredits(prev => ({
          ...prev,
          credits: result.remaining === 'unlimited' ? 'unlimited' : result.remaining
        }));

        // Show success toast if requested
        if (options.showSuccessToast) {
          const creditCost = CREDIT_COSTS[operation] * quantity;
          const operationName = operation.toLowerCase().replace(/_/g, ' ');
          toast.success(
            `${operationName} completed! ${creditCost} credit${creditCost !== 1 ? 's' : ''} used.`,
            { duration: 3000 }
          );
        }
      } else if (result.error === 'Insufficient credits') {
        // Show insufficient credits toast
        showInsufficientCreditsToast(operation, result.required, result.available);
      } else {
        toast.error(result.error || 'Failed to consume credits');
      }

      return result;
    } catch (err) {
      console.error('Error consuming credits:', err);
      toast.error('System error occurred');
      return { success: false, error: err.message };
    }
  };

  // Check if user has enough credits for an operation
  const hasEnoughCredits = (operation, quantity = 1) => {
    if (!credits || credits.credits === null) return false;
    return checkCredits(credits.credits, operation, quantity).hasEnough;
  };

  // Get credit requirement for an operation
  const getCreditRequirement = (operation, quantity = 1) => {
    return CREDIT_COSTS[operation] * quantity || 0;
  };

  // Execute operation with credit check and consumption
  const executeWithCredits = async (operation, action, options = {}) => {
    const { quantity = 1, showToasts = true } = options;

    // Check if credits are available
    if (!hasEnoughCredits(operation, quantity)) {
      const required = getCreditRequirement(operation, quantity);
      const available = credits?.credits || 0;
      
      if (showToasts) {
        showInsufficientCreditsToast(operation, required, available);
      }
      return { success: false, error: 'Insufficient credits' };
    }

    try {
      // Consume credits first
      const creditResult = await useCredits(operation, quantity, { 
        showSuccessToast: showToasts 
      });
      
      if (!creditResult.success) {
        return creditResult;
      }

      // Execute the actual operation
      const result = await action();
      
      return { success: true, result, creditsUsed: getCreditRequirement(operation, quantity) };
    } catch (error) {
      console.error('Error in executeWithCredits:', error);
      
      // TODO: In a real implementation, you might want to refund credits here
      // if the operation failed after consuming credits
      
      return { success: false, error: error.message };
    }
  };

  // Get formatted credit display
  const getFormattedCredits = () => {
    if (loading) return 'Loading...';
    if (!credits) return '0';
    return formatCredits(credits.credits);
  };

  // Get credit status color
  const getCreditStatusColor = () => {
    if (!credits) return 'error';
    return getCreditColor(credits.credits, credits.monthlyAllowance);
  };

  // Get credit percentage used
  const getCreditPercentage = () => {
    if (!credits || credits.credits === 'unlimited') return 0;
    if (credits.monthlyAllowance === 0) return 100;
    
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
    CREDIT_COSTS
  };
};

export default useCredits;