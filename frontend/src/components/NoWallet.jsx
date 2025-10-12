/**
 * NoWallet Component
 * 
 * A React component that enforces wallet blocking at the component level.
 * This provides an additional layer of protection against wallet auto-connection.
 */

import { useEffect } from 'react';
import walletBlocker from '../utils/walletBlocker';

const NoWallet = ({ children }) => {
  useEffect(() => {
    // Ensure wallet blocking is active when this component mounts
    console.log('🛡️ NoWallet component mounted - enforcing wallet blocking');
    
    // Force re-initialization of wallet blocking
    walletBlocker.init();
    
    // Check for wallet presence and block if found
    const checkAndBlock = () => {
      const walletPresence = walletBlocker.checkWalletPresence();
      
      if (walletPresence.ethereum || walletPresence.web3 || walletPresence.metamask) {
        console.log('⚠️ Wallet objects detected, re-blocking...');
        walletBlocker.startBlocking();
      }
    };
    
    // Initial check
    checkAndBlock();
    
    // Set up periodic checks while component is mounted
    const intervalId = setInterval(checkAndBlock, 2000);
    
    // Monitor for runtime wallet injection
    const handleFocus = () => {
      setTimeout(checkAndBlock, 100);
    };
    
    const handleVisibilityChange = () => {
      if (document.visibilityState === 'visible') {
        setTimeout(checkAndBlock, 100);
      }
    };
    
    window.addEventListener('focus', handleFocus);
    document.addEventListener('visibilitychange', handleVisibilityChange);
    
    // Cleanup on unmount
    return () => {
      clearInterval(intervalId);
      window.removeEventListener('focus', handleFocus);
      document.removeEventListener('visibilitychange', handleVisibilityChange);
    };
  }, []);
  
  // This component is transparent - it just renders its children
  // while enforcing wallet blocking
  return children;
};

export default NoWallet;