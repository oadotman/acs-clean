/**
 * Paddle Billing service for frontend subscription management (NEW Paddle Billing API)
 * Handles Paddle.js integration and API calls
 * Documentation: https://developer.paddle.com/paddlejs/overview
 */

class PaddleService {
  constructor() {
    this.loaded = false;
    this.paddleInstance = null;
    // NEW: Use client token instead of vendor ID for Paddle Billing
    this.clientToken = process.env.REACT_APP_PADDLE_CLIENT_TOKEN || null;
    this.vendorId = process.env.REACT_APP_PADDLE_VENDOR_ID || null;  // Still needed for Classic API fallback
    this.environment = process.env.REACT_APP_PADDLE_ENVIRONMENT || 'production';
    this.apiUrl = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';
    
    // Log configuration status for debugging
    console.log('🏗️ PaddleService initialized:', {
      clientToken: this.clientToken ? 'Set' : 'Not configured',
      environment: this.environment,
      apiUrl: this.apiUrl
    });
    
    if (!this.clientToken) {
      console.warn('⚠️ REACT_APP_PADDLE_CLIENT_TOKEN not set. Paddle checkout will not work until configured.');
    }
  }

  /**
   * Load Paddle.js script dynamically (NEW Paddle Billing API)
   */
  async loadPaddleScript() {
    if (!this.clientToken) {
      throw new Error('Paddle Client Token not configured. Please set REACT_APP_PADDLE_CLIENT_TOKEN in your environment variables.');
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

      // Create script element for NEW Paddle Billing
      const script = document.createElement('script');
      script.src = 'https://cdn.paddle.com/paddle/v2/paddle.js';  // NEW Paddle Billing script
      script.type = 'text/javascript';
      
      script.onload = () => {
        if (window.Paddle) {
          // Initialize Paddle with client token (NEW API)
          window.Paddle.Initialize({ 
            token: this.clientToken,
            eventCallback: this.handlePaddleEvent.bind(this)
          });
          
          this.loaded = true;
          this.paddleInstance = window.Paddle;
          console.log('✅ Paddle.js loaded and initialized successfully');
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
   * Open Paddle checkout overlay (Paddle Billing v2 API)
   */
  async openCheckout(options) {
    try {
      // CRITICAL: Validate email before proceeding
      if (!options.email) {
        const error = new Error('User email is required for checkout');
        console.error('❌ Cannot open checkout: Email is missing');
        throw error;
      }
      
      // Validate email format
      const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
      if (!emailRegex.test(options.email)) {
        const error = new Error('Invalid email format');
        console.error('❌ Cannot open checkout: Invalid email format:', options.email);
        throw error;
      }
      
      await this.loadPaddleScript();
      
      if (!this.paddleInstance) {
        throw new Error('Paddle not loaded');
      }
      
      console.log('🛒 Opening Paddle checkout with options:', {
        priceId: options.priceId,
        email: options.email,
        userId: options.userId
      });

      // Open checkout overlay using NEW Paddle Billing v2 API
      this.paddleInstance.Checkout.open({
        items: [{
          priceId: options.priceId,
          quantity: 1
        }],
        customer: {
          email: options.email || undefined
        },
        customData: {
          userId: options.userId,
          planName: options.planName,
          source: 'web_app'
        },
        settings: {
          displayMode: 'overlay',
          theme: 'light',
          locale: 'en',
          allowLogout: false
        }
      });
      
      console.log('✅ Paddle checkout opened successfully');
      
    } catch (error) {
      console.error('❌ Failed to open Paddle checkout:', error);
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
   * Get Paddle Price ID configuration with REAL Paddle Price IDs
   * These are the actual Price IDs from your Paddle dashboard
   */
  getPaddleProductMapping() {
    const products = {
      // New 5-tier structure with monthly/yearly support
      growth: {
        monthly: {
          priceId: 'pri_01k8gd5r03mg7p8gasg95pn105',  // Real Paddle Price ID
          name: 'Growth Plan (Monthly)',
          price: 39
        },
        yearly: {
          priceId: 'pri_01k8gdcc0z9qwz0htks3p6ydan',  // Real Paddle Price ID
          name: 'Growth Plan (Yearly)',
          price: Math.floor(39 * 12 * 0.8) // $374/year
        }
      },
      agency_standard: {
        monthly: {
          priceId: 'pri_01k8gdm6y2zqgcaqdv63ayk94k',  // Real Paddle Price ID
          name: 'Agency Standard Plan (Monthly)',
          price: 99
        },
        yearly: {
          priceId: 'pri_01k8gdk1hzrbf282v2schhg92j',  // Real Paddle Price ID
          name: 'Agency Standard Plan (Yearly)',
          price: Math.floor(99 * 12 * 0.8) // $950/year
        }
      },
      agency_premium: {
        monthly: {
          priceId: 'pri_01k8ge5xmbdga7r7d5qddpnc4b',  // Real Paddle Price ID
          name: 'Agency Premium Plan (Monthly)',
          price: 199
        },
        yearly: {
          priceId: 'pri_01k8ge7f9kqqr5qk1kxt1kerf5',  // Real Paddle Price ID
          name: 'Agency Premium Plan (Yearly)',
          price: Math.floor(199 * 12 * 0.8) // $1,910/year
        }
      },
      agency_unlimited: {
        monthly: {
          priceId: 'pri_01k8geawnz6d88m4m447rtzqp9',  // Real Paddle Price ID
          name: 'Agency Unlimited Plan (Monthly)',
          price: 249
        },
        yearly: {
          priceId: 'pri_01k8geddk1apxh8wrq0k6x2bkk',  // Real Paddle Price ID
          name: 'Agency Unlimited Plan (Yearly)',
          price: Math.floor(249 * 12 * 0.8) // $2,390/year
        }
      },
      // Legacy support - keep for backward compatibility (monthly only)
      basic: {
        priceId: 'pri_01k8gd5r03mg7p8gasg95pn105',  // Maps to Growth Monthly
        name: 'Growth Plan',
        price: 39
      },
      pro: {
        priceId: 'pri_01k8geawnz6d88m4m447rtzqp9',  // Maps to Agency Unlimited Monthly
        name: 'Agency Unlimited Plan',
        price: 249
      }
    };
    
    console.log('🛍️ Paddle Price ID mapping loaded with REAL IDs');
    return products;
  }
}

// Create singleton instance
const paddleService = new PaddleService();

export default paddleService;
