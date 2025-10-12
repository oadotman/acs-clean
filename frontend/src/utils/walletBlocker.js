/**
 * Enhanced Wallet Blocking Utility
 * 
 * This utility provides comprehensive blocking of MetaMask and other wallet
 * connections at the React application level as a fallback to the HTML-level blocking.
 */

class WalletBlocker {
  constructor() {
    this.isInitialized = false;
    this.originalEthereum = null;
    this.originalWeb3 = null;
    this.blockingActive = false;
  }

  /**
   * Initialize the wallet blocker
   */
  init() {
    if (this.isInitialized) return;

    console.log('🛡️ AdCopySurge: Initializing React-level wallet blocking');

    // Store original objects
    this.originalEthereum = window.ethereum;
    this.originalWeb3 = window.web3;

    // Start blocking
    this.startBlocking();

    // Set up continuous monitoring
    this.setupContinuousBlocking();

    this.isInitialized = true;
    console.log('✅ React-level wallet blocking initialized');
  }

  /**
   * Start the main blocking process
   */
  startBlocking() {
    this.blockingActive = true;

    try {
      // Block ethereum object
      if (window.ethereum) {
        console.log('🚫 React: Blocking ethereum object');
        
        // Override methods first
        const methods = ['connect', 'request', 'send', 'sendAsync', 'enable', 'isConnected'];
        methods.forEach(method => {
          if (window.ethereum[method]) {
            window.ethereum[method] = () => {
              console.log(`🚫 React: ${method} method blocked`);
              return Promise.reject(new Error(`${method} disabled in AdCopySurge`));
            };
          }
        });

        // Remove the object
        try {
          Object.defineProperty(window, 'ethereum', {
            value: undefined,
            writable: false,
            configurable: false
          });
        } catch (e) {
          window.ethereum = undefined;
        }
      }

      // Block web3
      if (window.web3) {
        console.log('🚫 React: Blocking web3 object');
        try {
          Object.defineProperty(window, 'web3', {
            value: undefined,
            writable: false,
            configurable: false
          });
        } catch (e) {
          window.web3 = undefined;
        }
      }

      // Block other wallet globals
      const walletGlobals = [
        'connect', 
        '__METAMASK_PROVIDER__', 
        'metamask', 
        '_metamask',
        'isMetaMask'
      ];

      walletGlobals.forEach(global => {
        if (window[global]) {
          console.log(`🚫 React: Blocking ${global}`);
          try {
            Object.defineProperty(window, global, {
              value: undefined,
              writable: false,
              configurable: false
            });
          } catch (e) {
            window[global] = undefined;
          }
        }
      });

    } catch (error) {
      console.log('🚫 React: Wallet blocking applied with warnings:', error.message);
    }
  }

  /**
   * Set up continuous monitoring and blocking
   */
  setupContinuousBlocking() {
    // Monitor for object recreation
    const monitorInterval = setInterval(() => {
      if (!this.blockingActive) {
        clearInterval(monitorInterval);
        return;
      }

      if (window.ethereum && window.ethereum !== this.originalEthereum) {
        console.log('🚫 React: Ethereum object recreated, blocking again');
        this.startBlocking();
      }

      if (window.web3 && window.web3 !== this.originalWeb3) {
        console.log('🚫 React: Web3 object recreated, blocking again');
        this.startBlocking();
      }
    }, 1000);

    // Handle window focus (wallets sometimes inject on focus)
    window.addEventListener('focus', () => {
      if (this.blockingActive) {
        setTimeout(() => this.startBlocking(), 100);
      }
    });

    // Handle visibility change
    document.addEventListener('visibilitychange', () => {
      if (this.blockingActive && document.visibilityState === 'visible') {
        setTimeout(() => this.startBlocking(), 100);
      }
    });
  }

  /**
   * Suppress wallet-related errors
   */
  suppressWalletErrors() {
    // Global error handler
    window.addEventListener('error', (event) => {
      if (event.message && (
        event.message.includes('MetaMask') ||
        event.message.includes('ethereum') ||
        event.message.includes('web3')
      )) {
        console.log('🚫 React: Suppressed wallet error:', event.message);
        event.preventDefault();
        event.stopPropagation();
        return false;
      }
    }, true);

    // Promise rejection handler
    window.addEventListener('unhandledrejection', (event) => {
      if (event.reason && (
        (event.reason.message && event.reason.message.includes('MetaMask')) ||
        (event.reason.message && event.reason.message.includes('ethereum')) ||
        (event.reason.message && event.reason.message.includes('web3'))
      )) {
        console.log('🚫 React: Suppressed wallet promise rejection:', event.reason.message);
        event.preventDefault();
        return false;
      }
    });
  }

  /**
   * Disable wallet blocking (for cleanup)
   */
  disable() {
    this.blockingActive = false;
    console.log('🛡️ Wallet blocking disabled');
  }

  /**
   * Check if any wallet objects are present
   */
  checkWalletPresence() {
    const walletObjects = {
      ethereum: !!window.ethereum,
      web3: !!window.web3,
      metamask: !!window.metamask,
      connect: !!(window.connect && typeof window.connect === 'function')
    };

    console.log('🔍 Wallet presence check:', walletObjects);
    return walletObjects;
  }
}

// Create a singleton instance
const walletBlocker = new WalletBlocker();

// Auto-initialize when module loads
if (typeof window !== 'undefined') {
  // Small delay to ensure DOM is ready
  setTimeout(() => {
    walletBlocker.init();
    walletBlocker.suppressWalletErrors();
  }, 50);
}

export default walletBlocker;