import { useEffect } from 'react';
import { useLocation } from 'react-router-dom';

/**
 * Google Analytics 4 Component
 * Tracks page views and custom events
 */
const GoogleAnalytics = () => {
  const location = useLocation();
  const GA_MEASUREMENT_ID = process.env.REACT_APP_GA_MEASUREMENT_ID || 'G-XXXXXXXXXX';

  useEffect(() => {
    // Load Google Analytics script
    if (!window.gtag && GA_MEASUREMENT_ID !== 'G-XXXXXXXXXX') {
      const script = document.createElement('script');
      script.async = true;
      script.src = `https://www.googletagmanager.com/gtag/js?id=${GA_MEASUREMENT_ID}`;
      document.head.appendChild(script);

      window.dataLayer = window.dataLayer || [];
      function gtag() {
        window.dataLayer.push(arguments);
      }
      window.gtag = gtag;
      gtag('js', new Date());
      gtag('config', GA_MEASUREMENT_ID, {
        send_page_view: false // We'll manually track page views
      });
    }
  }, [GA_MEASUREMENT_ID]);

  useEffect(() => {
    // Track page view on route change
    if (window.gtag) {
      window.gtag('event', 'page_view', {
        page_path: location.pathname + location.search,
        page_location: window.location.href,
        page_title: document.title
      });
    }
  }, [location]);

  return null;
};

/**
 * Track custom events
 * @param {string} eventName - Event name (e.g., 'signup', 'analyze_ad')
 * @param {object} eventParams - Additional parameters
 */
export const trackEvent = (eventName, eventParams = {}) => {
  if (window.gtag) {
    window.gtag('event', eventName, eventParams);
  }
};

/**
 * Track user signup
 */
export const trackSignup = (method = 'email') => {
  trackEvent('sign_up', {
    method: method
  });
};

/**
 * Track user login
 */
export const trackLogin = (method = 'email') => {
  trackEvent('login', {
    method: method
  });
};

/**
 * Track ad analysis
 */
export const trackAdAnalysis = (adType) => {
  trackEvent('analyze_ad', {
    ad_type: adType,
    content_type: 'ad_copy'
  });
};

/**
 * Track subscription start
 */
export const trackSubscription = (planName, value, currency = 'USD') => {
  trackEvent('purchase', {
    transaction_id: Date.now().toString(),
    value: value,
    currency: currency,
    items: [{
      item_name: planName,
      item_category: 'subscription'
    }]
  });
};

/**
 * Track team invitation
 */
export const trackTeamInvite = (role) => {
  trackEvent('invite_team_member', {
    role: role
  });
};

/**
 * Track support ticket
 */
export const trackSupportTicket = (subject) => {
  trackEvent('contact_support', {
    subject: subject
  });
};

export default GoogleAnalytics;
