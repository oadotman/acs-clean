/**
 * Paddle billing service for frontend subscription management
 * Handles Paddle.js integration and API calls
 */

class PaddleService {
  constructor() {
    this.loaded = false;
    this.paddleInstance = null;
    this.vendorId = process.env.REACT_APP_PADDLE_VENDOR_ID || null;
    this.environment = process.env.REACT_APP_PADDLE_ENVIRONMENT || 'sandbox';
    this.apiUrl = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';
    
    // Log configuration status for debugging
    console.log('🏗️ PaddleService initialized:', {
      vendorId: this.vendorId ? 'Set' : 'Not configured',
      environment: this.environment,
      apiUrl: this.apiUrl
    });
    
    if (!this.vendorId) {
      console.warn('⚠️ REACT_APP_PADDLE_VENDOR_ID not set. Paddle checkout will not work until configured.');
    }
  }

  /**
   * Load Paddle.js script dynamically
   */
  async loadPaddleScript() {
    if (!this.vendorId) {
      throw new Error('Paddle Vendor ID not configured. Please set REACT_APP_PADDLE_VENDOR_ID in your environment variables.');
    }
    
    if (this.loaded && window.Paddle) {
      return window.Paddle;
    }

    return new Promise((resolve, reject) => {
      // Check if already loaded
      if (window.Paddle) {
        this.loaded = true;
        this.paddleInstance = window.Paddle;
        resolve(window.Paddle);
        return;
      }

      // Create script element
      const script = document.createElement('script');
      script.src = this.environment === 'sandbox' 
        ? 'https://cdn.paddle.com/paddle/paddle.js'
        : 'https://cdn.paddle.com/paddle/paddle.js';
      
      script.onload = () => {
        if (window.Paddle) {
          // Initialize Paddle
          window.Paddle.Setup({ 
            vendor: this.vendorId,
            eventCallback: this.handlePaddleEvent.bind(this)
          });
          
          this.loaded = true;
          this.paddleInstance = window.Paddle;
          resolve(window.Paddle);
        } else {
          reject(new Error('Failed to load Paddle'));
        }
      };

      script.onerror = () => {
        reject(new Error('Failed to load Paddle script'));
      };

      document.head.appendChild(script);
    });
  }

  /**
   * Handle Paddle events
   */
  handlePaddleEvent(event) {
    console.log('Paddle Event:', event);
    
    switch(event.event) {
      case 'Checkout.Close':
        console.log('Checkout closed');
        break;
      case 'Checkout.Complete':
        console.log('Checkout completed:', event.eventData);
        this.handleCheckoutComplete(event.eventData);
        break;
      case 'Checkout.Loaded':
        console.log('Checkout loaded');
        break;
      case 'Checkout.PaymentFailed':
        console.log('Payment failed:', event.eventData);
        this.handlePaymentFailed(event.eventData);
        break;
      default:
        console.log('Unhandled Paddle event:', event);
    }
  }

  /**
   * Handle successful checkout completion
   */
  handleCheckoutComplete(data) {
    // Redirect to success page or refresh subscription data
    const urlParams = new URLSearchParams();
    urlParams.set('success', 'true');
    urlParams.set('checkout_id', data.checkout_id);
    
    window.location.href = `/dashboard?${urlParams.toString()}`;
  }

  /**
   * Handle payment failure
   */
  handlePaymentFailed(data) {
    // Show error message or redirect to retry
    console.error('Payment failed:', data);
    // You could show a toast notification here
  }

  /**
   * Open Paddle checkout overlay
   */
  async openCheckout(options) {
    try {
      await this.loadPaddleScript();
      
      if (!this.paddleInstance) {
        throw new Error('Paddle not loaded');
      }

      // Open checkout overlay
      this.paddleInstance.Checkout.open({
        method: 'overlay',
        product: options.productId,
        email: options.email || '',
        passthrough: JSON.stringify({
          user_id: options.userId,
          plan: options.planName,
          source: 'web_app'
        }),
        successCallback: options.successCallback || this.handleCheckoutComplete.bind(this),
        closeCallback: options.closeCallback || (() => console.log('Checkout closed'))
      });
      
    } catch (error) {
      console.error('Failed to open Paddle checkout:', error);
      throw error;
    }
  }

  /**
   * Get subscription plans from backend
   */
  async getSubscriptionPlans() {
    try {
      const response = await fetch(`${this.apiUrl}/subscriptions/plans`);
      if (!response.ok) {
        throw new Error('Failed to fetch subscription plans');
      }
      return await response.json();
    } catch (error) {
      console.error('Error fetching subscription plans:', error);
      throw error;
    }
  }

  /**
   * Get current user subscription
   */
  async getCurrentSubscription(authToken) {
    try {
      const response = await fetch(`${this.apiUrl}/subscriptions/current`, {
        headers: {
          'Authorization': `Bearer ${authToken}`,
          'Content-Type': 'application/json'
        }
      });
      
      if (!response.ok) {
        throw new Error('Failed to fetch subscription');
      }
      
      return await response.json();
    } catch (error) {
      console.error('Error fetching current subscription:', error);
      throw error;
    }
  }

  /**
   * Create checkout session (alternative to direct overlay)
   */
  async createCheckoutSession(planTier, authToken) {
    try {
      const response = await fetch(`${this.apiUrl}/subscriptions/paddle/checkout`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${authToken}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          tier: planTier
        })
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to create checkout session');
      }

      return await response.json();
    } catch (error) {
      console.error('Error creating checkout session:', error);
      throw error;
    }
  }

  /**
   * Cancel subscription
   */
  async cancelSubscription(authToken) {
    try {
      const response = await fetch(`${this.apiUrl}/subscriptions/paddle/cancel`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${authToken}`,
          'Content-Type': 'application/json'
        }
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to cancel subscription');
      }

      return await response.json();
    } catch (error) {
      console.error('Error cancelling subscription:', error);
      throw error;
    }
  }

  /**
   * Get Paddle product configuration
   * These should match your Paddle dashboard product IDs
   */
  getPaddleProductMapping() {
    const products = {
      // New 5-tier structure with monthly/yearly support
      growth: {
        monthly: {
          productId: 'growth_monthly',
          name: 'Growth Plan (Monthly)',
          price: 39
        },
        yearly: {
          productId: 'growth_yearly',
          name: 'Growth Plan (Yearly)',
          price: Math.floor(39 * 12 * 0.8) // 374
        }
      },
      agency_standard: {
        monthly: {
          productId: 'agency_standard_monthly',
          name: 'Agency Standard Plan (Monthly)',
          price: 99
        },
        yearly: {
          productId: 'agency_standard_yearly',
          name: 'Agency Standard Plan (Yearly)',
          price: Math.floor(99 * 12 * 0.8) // 950
        }
      },
      agency_premium: {
        monthly: {
          productId: 'agency_premium_monthly',
          name: 'Agency Premium Plan (Monthly)',
          price: 199
        },
        yearly: {
          productId: 'agency_premium_yearly',
          name: 'Agency Premium Plan (Yearly)',
          price: Math.floor(199 * 12 * 0.8) // 1910
        }
      },
      agency_unlimited: {
        monthly: {
          productId: 'agency_unlimited_monthly',
          name: 'Agency Unlimited Plan (Monthly)',
          price: 249
        },
        yearly: {
          productId: 'agency_unlimited_yearly',
          name: 'Agency Unlimited Plan (Yearly)',
          price: Math.floor(249 * 12 * 0.8) // 2390
        }
      },
      // Legacy support - keep for backward compatibility (monthly only)
      basic: {
        productId: 'growth_monthly', // Maps to Growth plan
        name: 'Growth Plan',
        price: 39
      },
      pro: {
        productId: 'agency_unlimited_monthly', // Maps to Agency Unlimited plan
        name: 'Agency Unlimited Plan',
        price: 249
      }
    };
    
    console.log('🛍️ Paddle product mapping loaded:', products);
    return products;
  }
}

// Create singleton instance
const paddleService = new PaddleService();

export default paddleService;
