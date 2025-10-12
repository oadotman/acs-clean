import { SUBSCRIPTION_TIERS, PLAN_LIMITS } from '../constants/plans';
import { getUserCredits, initializeUserCredits } from './creditSystem';

/**
 * Utility to manage user subscription tiers for testing
 */
export class UserTierManager {
  
  /**
   * Set user to a specific subscription tier
   */
  static async setUserTier(userId, tier) {
    try {
      console.log(`🔄 Setting user ${userId} to tier: ${tier}`);
      
      // Validate tier
      if (!Object.values(SUBSCRIPTION_TIERS).includes(tier)) {
        throw new Error(`Invalid tier: ${tier}`);
      }
      
      const planLimits = PLAN_LIMITS[tier];
      const credits = planLimits.adAnalyses === -1 ? 999999 : planLimits.adAnalyses;
      
      const userCredits = {
        credits: credits,
        monthlyAllowance: planLimits.adAnalyses,
        subscriptionTier: tier,
        lastReset: new Date().toISOString(),
        totalUsed: 0,
        bonusCredits: 0
      };
      
      // Save to localStorage (fallback)
      localStorage.setItem(`credits_${userId}`, JSON.stringify(userCredits));
      
      console.log(`✅ User tier set to ${tier}:`, userCredits);
      return userCredits;
      
    } catch (error) {
      console.error('❌ Error setting user tier:', error);
      throw error;
    }
  }
  
  /**
   * Get current user tier information
   */
  static async getUserTierInfo(userId) {
    try {
      const credits = await getUserCredits(userId);
      const tier = credits.subscriptionTier || SUBSCRIPTION_TIERS.FREE;
      const planLimits = PLAN_LIMITS[tier];
      
      return {
        tier,
        tierName: tier.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase()),
        credits: credits.credits,
        monthlyAllowance: credits.monthlyAllowance,
        isUnlimited: credits.monthlyAllowance === -1 || credits.credits >= 999999,
        planLimits,
        ...credits
      };
      
    } catch (error) {
      console.error('❌ Error getting user tier info:', error);
      return null;
    }
  }
  
  /**
   * Quick tier setters for testing
   */
  static async setFree(userId) {
    return this.setUserTier(userId, SUBSCRIPTION_TIERS.FREE);
  }
  
  static async setGrowth(userId) {
    return this.setUserTier(userId, SUBSCRIPTION_TIERS.GROWTH);
  }
  
  static async setAgencyStandard(userId) {
    return this.setUserTier(userId, SUBSCRIPTION_TIERS.AGENCY_STANDARD);
  }
  
  static async setAgencyPremium(userId) {
    return this.setUserTier(userId, SUBSCRIPTION_TIERS.AGENCY_PREMIUM);
  }
  
  static async setAgencyUnlimited(userId) {
    return this.setUserTier(userId, SUBSCRIPTION_TIERS.AGENCY_UNLIMITED);
  }
  
  /**
   * Add credits to a user (for testing)
   */
  static async addCredits(userId, amount) {
    try {
      const currentCredits = await getUserCredits(userId);
      const updatedCredits = {
        ...currentCredits,
        credits: currentCredits.credits + amount
      };
      
      localStorage.setItem(`credits_${userId}`, JSON.stringify(updatedCredits));
      console.log(`✅ Added ${amount} credits to user. New balance: ${updatedCredits.credits}`);
      
      return updatedCredits;
    } catch (error) {
      console.error('❌ Error adding credits:', error);
      throw error;
    }
  }
  
  /**
   * Reset user credits to default for their tier
   */
  static async resetCredits(userId) {
    try {
      const tierInfo = await this.getUserTierInfo(userId);
      if (!tierInfo) throw new Error('Could not get user tier info');
      
      return this.setUserTier(userId, tierInfo.tier);
    } catch (error) {
      console.error('❌ Error resetting credits:', error);
      throw error;
    }
  }
}

// Global helper for console access
if (typeof window !== 'undefined') {
  window.UserTierManager = UserTierManager;
  
  // Console helpers
  window.setUserFree = (userId) => UserTierManager.setFree(userId);
  window.setUserGrowth = (userId) => UserTierManager.setGrowth(userId);
  window.setUserAgencyStandard = (userId) => UserTierManager.setAgencyStandard(userId);
  window.setUserAgencyPremium = (userId) => UserTierManager.setAgencyPremium(userId);
  window.setUserAgencyUnlimited = (userId) => UserTierManager.setAgencyUnlimited(userId);
  window.addUserCredits = (userId, amount) => UserTierManager.addCredits(userId, amount);
  window.getUserTier = (userId) => UserTierManager.getUserTierInfo(userId);
  
  console.log(`
🎯 User Tier Management Console Commands Available:

// Set subscription tiers:
setUserFree('your-user-id')
setUserGrowth('your-user-id') 
setUserAgencyStandard('your-user-id')
setUserAgencyPremium('your-user-id')
setUserAgencyUnlimited('your-user-id')

// Add credits:
addUserCredits('your-user-id', 10)

// Check user info:
getUserTier('your-user-id')

Available tiers:
- FREE: 5 analyses per month
- GROWTH: 100 analyses per month  
- AGENCY_STANDARD: 500 analyses per month
- AGENCY_PREMIUM: 1000 analyses per month
- AGENCY_UNLIMITED: ∞ unlimited analyses
`);
}

export default UserTierManager;