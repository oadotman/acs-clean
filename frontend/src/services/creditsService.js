/**
 * Credits management service for tracking usage and limits
 */

class CreditsService {
  constructor() {
    this.storageKey = 'adcopysurge_credits';
    this.defaultCredits = {
      current: 100,
      total: 100,
      tier: 'basic',
      resetDate: this.getNextResetDate(),
      dailyUsage: 0,
      weeklyUsage: 0,
      monthlyUsage: 0,
      lastUsed: null
    };
  }

  getNextResetDate() {
    const now = new Date();
    const nextMonth = new Date(now.getFullYear(), now.getMonth() + 1, 1);
    return nextMonth;
  }

  // Get current credits data
  getCredits() {
    try {
      const stored = localStorage.getItem(this.storageKey);
      if (stored) {
        const credits = JSON.parse(stored);
        // Check if reset date has passed
        const now = new Date();
        const resetDate = new Date(credits.resetDate);
        
        if (now >= resetDate) {
          // Reset credits for new period
          return this.resetCredits(credits);
        }
        
        return credits;
      }
    } catch (error) {
      console.error('Error reading credits:', error);
    }
    
    // Return default credits if no stored data or error
    return this.initializeCredits();
  }

  // Initialize credits for new user
  initializeCredits() {
    const credits = { ...this.defaultCredits };
    this.saveCredits(credits);
    return credits;
  }

  // Reset credits for new billing period
  resetCredits(oldCredits) {
    const newCredits = {
      ...oldCredits,
      current: oldCredits.total, // Reset to full amount
      resetDate: this.getNextResetDate(),
      dailyUsage: 0,
      weeklyUsage: 0,
      monthlyUsage: 0
    };
    
    this.saveCredits(newCredits);
    return newCredits;
  }

  // Use credits for analysis
  useCredits(amount = 1, analysisType = 'single') {
    const credits = this.getCredits();
    
    console.log(`💰 CreditsService: Using ${amount} credits for ${analysisType}`);
    console.log(`💳 Current credits before:`, credits.current);
    
    // Handle unlimited tier
    if (credits.tier === 'agency_unlimited' || credits.current >= 999999) {
      console.log('♾️ Unlimited tier, not consuming credits');
      return credits;
    }
    
    if (credits.current < amount) {
      console.error(`❌ Insufficient credits: ${credits.current} < ${amount}`);
      throw new Error('Insufficient credits');
    }

    const now = new Date();
    const updatedCredits = {
      ...credits,
      current: credits.current - amount,
      dailyUsage: credits.dailyUsage + amount,
      weeklyUsage: credits.weeklyUsage + amount,
      monthlyUsage: credits.monthlyUsage + amount,
      lastUsed: now.toISOString()
    };

    console.log(`💳 Credits after usage:`, updatedCredits.current);
    this.saveCredits(updatedCredits);
    
    // Analytics
    this.trackUsage(analysisType, amount);
    
    return updatedCredits;
  }

  // Track usage analytics
  trackUsage(type, amount) {
    const usage = this.getUsageStats();
    const today = new Date().toDateString();
    
    if (!usage[today]) {
      usage[today] = {
        single: 0,
        batch: 0,
        total: 0
      };
    }
    
    usage[today][type] = (usage[today][type] || 0) + amount;
    usage[today].total += amount;
    
    // Keep only last 30 days of data
    const thirtyDaysAgo = new Date();
    thirtyDaysAgo.setDate(thirtyDaysAgo.getDate() - 30);
    
    Object.keys(usage).forEach(date => {
      if (new Date(date) < thirtyDaysAgo) {
        delete usage[date];
      }
    });
    
    localStorage.setItem('adcopysurge_usage', JSON.stringify(usage));
  }

  // Get usage statistics
  getUsageStats() {
    try {
      const stored = localStorage.getItem('adcopysurge_usage');
      return stored ? JSON.parse(stored) : {};
    } catch (error) {
      console.error('Error reading usage stats:', error);
      return {};
    }
  }

  // Upgrade user tier
  upgradeTier(newTier) {
    const credits = this.getCredits();
    const tierLimits = this.getTierLimits(newTier);
    
    const updatedCredits = {
      ...credits,
      tier: newTier,
      total: tierLimits.monthly,
      current: Math.max(credits.current, tierLimits.monthly - credits.monthlyUsage)
    };
    
    this.saveCredits(updatedCredits);
    return updatedCredits;
  }

  // Get tier-specific limits
  getTierLimits(tier) {
    const limits = {
      basic: {
        monthly: 100,
        daily: 10,
        batch: false
      },
      pro: {
        monthly: 1000,
        daily: 100,
        batch: true
      },
      agency: {
        monthly: 5000,
        daily: 500,
        batch: true
      }
    };
    
    return limits[tier] || limits.basic;
  }

  // Check if user can perform action
  canPerformAction(action, amount = 1) {
    const credits = this.getCredits();
    const limits = this.getTierLimits(credits.tier);
    
    console.log(`🔍 CreditsService: Checking ${action} for ${amount} credits`);
    console.log(`💳 Current credits:`, credits);
    
    // Handle unlimited tier
    if (credits.tier === 'agency_unlimited' || credits.current >= 999999) {
      console.log('♾️ Unlimited tier detected, allowing action');
      return true;
    }
    
    switch (action) {
      case 'single_analysis':
        const canAnalyze = credits.current >= amount;
        console.log(`🔍 Single analysis check: ${canAnalyze} (${credits.current} >= ${amount})`);
        return canAnalyze;
      
      case 'batch_analysis':
        const canBatch = limits.batch && credits.current >= amount;
        console.log(`🔍 Batch analysis check: ${canBatch}`);
        return canBatch;
      
      case 'daily_limit':
        const withinDaily = credits.dailyUsage + amount <= limits.daily;
        console.log(`🔍 Daily limit check: ${withinDaily}`);
        return withinDaily;
      
      default:
        console.log(`✅ Unknown action ${action}, allowing by default`);
        return true;
    }
  }

  // Get days until reset
  getDaysUntilReset() {
    const credits = this.getCredits();
    const now = new Date();
    const resetDate = new Date(credits.resetDate);
    const diffTime = resetDate.getTime() - now.getTime();
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    return Math.max(0, diffDays);
  }

  // Save credits to storage
  saveCredits(credits) {
    try {
      localStorage.setItem(this.storageKey, JSON.stringify(credits));
    } catch (error) {
      console.error('Error saving credits:', error);
    }
  }

  // Get credits percentage
  getCreditsPercentage() {
    const credits = this.getCredits();
    return (credits.current / credits.total) * 100;
  }

  // Get credits status
  getCreditsStatus() {
    const percentage = this.getCreditsPercentage();
    
    if (percentage <= 10) return { status: 'critical', color: 'error' };
    if (percentage <= 25) return { status: 'low', color: 'warning' };
    if (percentage <= 50) return { status: 'medium', color: 'info' };
    return { status: 'good', color: 'success' };
  }

  // Simulate realistic credit variations
  addVariationToCredits(credits) {
    // Add some realistic usage patterns
    const now = new Date();
    const hour = now.getHours();
    
    // Business hours usage (9-17) tends to be higher
    const isBusinessHours = hour >= 9 && hour <= 17;
    const baseUsage = isBusinessHours ? 3 : 1;
    
    // Add some randomness
    const dailyVariation = Math.floor(Math.random() * baseUsage);
    
    return {
      ...credits,
      dailyUsage: Math.min(credits.dailyUsage + dailyVariation, credits.total),
      current: Math.max(0, credits.current - dailyVariation)
    };
  }

  // Reset demo data (for development)
  resetDemoData() {
    localStorage.removeItem(this.storageKey);
    localStorage.removeItem('adcopysurge_usage');
    return this.initializeCredits();
  }
}

// Create singleton instance
const creditsService = new CreditsService();

export default creditsService;