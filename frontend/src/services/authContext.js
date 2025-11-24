import React, { createContext, useContext, useState, useEffect } from 'react';
import toast from 'react-hot-toast';
import { supabase } from '../lib/supabaseClientClean';
import { signIn, signUp, signOut, getCurrentUser } from '../lib/supabaseClient';
import { runAuthDiagnostics } from '../utils/authDebug';

// Global request interceptor for handling 401 errors
let authInterceptor = null;

// Enhanced authentication utilities
const AuthUtils = {
  // Check if user is online
  isOnline: () => navigator.onLine,
  
  // Refresh session with retry logic
  refreshSession: async (retries = 2) => {
    for (let i = 0; i <= retries; i++) {
      try {
        console.log(`🔄 Attempting session refresh (attempt ${i + 1}/${retries + 1})...`);
        const { data, error } = await supabase.auth.refreshSession();
        
        if (error) {
          console.warn(`⚠️ Session refresh attempt ${i + 1} failed:`, error.message);
          if (i === retries) throw error;
          await new Promise(resolve => setTimeout(resolve, 1000 * (i + 1))); // Progressive delay
          continue;
        }
        
        console.log('✅ Session refreshed successfully');
        return data;
      } catch (error) {
        console.error(`❌ Session refresh attempt ${i + 1} failed:`, error);
        if (i === retries) throw error;
      }
    }
  },
  
  // Handle 401 errors with automatic token refresh
  handle401Error: async (originalRequest) => {
    try {
      console.log('🔄 Handling 401 error - attempting token refresh...');
      const refreshData = await AuthUtils.refreshSession();
      
      if (refreshData?.session?.access_token) {
        console.log('✅ Token refreshed, retrying original request...');
        // Return indication that request should be retried
        return { shouldRetry: true, newToken: refreshData.session.access_token };
      } else {
        console.warn('⚠️ No new token received after refresh');
        return { shouldRetry: false };
      }
    } catch (error) {
      console.error('❌ Failed to refresh token:', error);
      return { shouldRetry: false, error };
    }
  },
  
  // Expose debug function globally
  exposeDebugState: () => {
    if (typeof window !== 'undefined' && process.env.NODE_ENV === 'development') {
      window.debugAuthState = async () => {
        console.log('🔧 === AUTH DEBUG STATE ===');
        try {
          const { data: { session }, error } = await supabase.auth.getSession();
          console.log('📊 Session Status:', session ? 'Active' : 'None');
          if (session) {
            console.log('👤 User:', session.user?.email);
            console.log('🔑 Token expires:', new Date(session.expires_at * 1000).toLocaleString());
            console.log('🔍 Token valid:', new Date(session.expires_at * 1000) > new Date() ? 'Yes' : 'No');
          }
          if (error) console.log('❌ Session Error:', error);
          console.log('🌐 Online:', navigator.onLine);
          console.log('💾 LocalStorage keys:', Object.keys(localStorage).filter(k => k.includes('supabase')));
        } catch (err) {
          console.error('💥 Debug failed:', err);
        }
        console.log('🔧 === END DEBUG ===');
      };
      console.log('🔧 Auth debug available: window.debugAuthState()');
    }
  }
};

console.log('🔗 Using Supabase for authentication');

const AuthContext = createContext();

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

// Network connectivity check utility
const checkNetworkConnectivity = async () => {
  try {
    // First check the navigator.onLine status (instant check)
    if (!navigator.onLine) {
      console.warn('⚠️ Browser reports offline status');
      return false;
    }
    
    // Try a simple fetch to a reliable endpoint with careful timeout handling
    const controller = new AbortController();
    let timeoutId;
    
    const timeoutPromise = new Promise((_, reject) => {
      timeoutId = setTimeout(() => {
        // Only abort if the request is still pending
        if (!controller.signal.aborted) {
          controller.abort('Network connectivity check timeout');
        }
        reject(new Error('Network check timeout'));
      }, 2000); // Reduced timeout to 2 seconds
    });
    
    // Use Supabase health check instead of external URL to avoid CORS
    const fetchPromise = supabase.auth.getSession().then(response => {
      // If we get a response (error or not), we have connectivity
      return { ok: true };
    });
    
    try {
      const response = await Promise.race([fetchPromise, timeoutPromise]);
      clearTimeout(timeoutId);
      return response.ok;
    } catch (raceError) {
      clearTimeout(timeoutId);
      // Don't log abort errors as warnings since they're expected
      if (raceError.name === 'AbortError' || (raceError.message && raceError.message.includes('timeout'))) {
        console.log('ℹ️ Network connectivity check timed out (expected behavior)');
      } else {
        console.warn('⚠️ Network connectivity check failed:', raceError.message || 'Unknown error');
      }
      return false;
    }
  } catch (error) {
    // Fallback - assume we have connectivity if the check itself fails
    console.warn('⚠️ Network connectivity check error:', error.message || error.toString(), '- assuming connected');
    return true; // Assume connected on check failure
  }
};

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [loading, setLoading] = useState(true);
  const [subscription, setSubscription] = useState(null);
  const [isOnline, setIsOnline] = useState(navigator.onLine);
  const [lastNetworkCheck, setLastNetworkCheck] = useState(new Date());

  useEffect(() => {
    let mounted = true;
    
    console.log('🔄 AuthProvider initializing...');
    
    // Expose debug functions globally
    AuthUtils.exposeDebugState();
    
    // Set up network monitoring
    const handleOnline = () => {
      console.log('🌐 Network connected');
      setIsOnline(true);
      setLastNetworkCheck(new Date());
    };
    
    const handleOffline = () => {
      console.log('😫 Network disconnected');
      setIsOnline(false);
      setLastNetworkCheck(new Date());
    };
    
    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);
    
    // Simplified auth initialization without complex network checks
    const initializeAuth = async () => {
      console.log('🔍 Initializing authentication...');
      
      // Simple overall timeout as safety net
      const overallTimeoutId = setTimeout(() => {
        console.warn('⏰ Auth timeout - proceeding as unauthenticated');
        if (mounted) {
          setLoading(false);
          setUser(null);
          setIsAuthenticated(false);
        }
      }, 8000); // 8 second timeout
      
      try {
        // Simple direct session check with timeout
        const sessionPromise = supabase.auth.getSession();
        const timeoutPromise = new Promise((_, reject) => {
          setTimeout(() => reject(new Error('Session check timeout')), 5000);
        });
        
        const result = await Promise.race([sessionPromise, timeoutPromise]);
        const { data, error } = result;
        
        if (error) {
          console.warn('⚠️ Session check error:', error.message);
          if (mounted) {
            setLoading(false);
          }
          clearTimeout(overallTimeoutId);
          return;
        }
        
        const session = data?.session;
        
        if (session?.user) {
          console.log('✅ Found active session for:', session.user.email);
          if (mounted) {
            setUser(session.user);
            setIsAuthenticated(true);
            // Fetch profile without awaiting to avoid blocking
            fetchUserProfile(session.user.id).finally(() => {
              if (mounted) setLoading(false);
            });
          }
        } else {
          console.log('ℹ️ No active session found');
          if (mounted) {
            setLoading(false);
          }
        }
        
        clearTimeout(overallTimeoutId);
      } catch (error) {
        console.error('❌ Auth initialization failed:', error.message);
        if (mounted) {
          setLoading(false);
          setUser(null);
          setIsAuthenticated(false);
        }
        clearTimeout(overallTimeoutId);
      }
    };

    // Initialize auth
    initializeAuth();

    // Listen for auth changes - but don't handle INITIAL_SESSION since initializeAuth does it
    const { data: { subscription: authSubscription } } = supabase.auth.onAuthStateChange(async (event, session) => {
      console.log('🔄 Auth state changed:', event, session?.user?.email || 'no user');
      
      if (!mounted) return;
      
      // Skip INITIAL_SESSION - already handled by initializeAuth
      if (event === 'INITIAL_SESSION') {
        console.log('ℹ️ Skipping INITIAL_SESSION (handled by initializeAuth)');
        return;
      }
      
      if (event === 'SIGNED_IN' && session?.user) {
        console.log('✅ User signed in:', session.user.email);
        setUser(session.user);
        setIsAuthenticated(true);
        setLoading(false);
        // Fetch profile without blocking
        fetchUserProfile(session.user.id);
      } else if (event === 'SIGNED_OUT') {
        console.log('👋 User signed out');
        setUser(null);
        setIsAuthenticated(false);
        setSubscription(null);
        setLoading(false);
      } else if (event === 'TOKEN_REFRESHED' && session?.user) {
        console.log('🔄 Token refreshed for:', session.user.email);
        setUser(session.user);
        setIsAuthenticated(true);
      } else if (event === 'USER_UPDATED' && session?.user) {
        console.log('👤 User data updated:', session.user.email);
        setUser(session.user);
        setIsAuthenticated(true);
      }
    });

    return () => {
      mounted = false;
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
      authSubscription?.unsubscribe();
    };
  }, []);


  const fetchUserProfile = async (userId) => {
    try {
      console.log('📋 Fetching user profile for:', userId);

      // Get auth token for backend API call
      const { data: { session } } = await supabase.auth.getSession();
      const token = session?.access_token;

      if (!token) {
        console.warn('⚠️ No auth token available for profile fetch');
        return;
      }

      // Call backend API to get effective subscription tier (considers team membership)
      const timeoutPromise = new Promise((_, reject) => {
        setTimeout(() => reject(new Error('Profile fetch timeout')), 90000); // 90 seconds for long operations
      });

      // Construct API URL consistently: base URL + /api prefix
      const baseUrl = process.env.REACT_APP_API_URL || 'http://127.0.0.1:8000';
      const apiUrl = baseUrl.endsWith('/api') ? baseUrl : `${baseUrl}/api`;

      const fetchPromise = fetch(`${apiUrl}/user/profile`, {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      }).then(async (response) => {
        if (!response.ok) {
          throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        return response.json();
      });

      const profileData = await Promise.race([fetchPromise, timeoutPromise]);

      if (profileData) {
        console.log('✅ User profile fetched with effective tier:', {
          subscription_tier: profileData.subscription_tier,
          is_team_member: profileData.is_team_member,
          agency_name: profileData.agency_name,
          role: profileData.role
        });

        // Set the subscription with the effective tier (agency tier if team member)
        setSubscription({
          subscription_tier: profileData.subscription_tier,
          tier: profileData.subscription_tier,
          is_team_member: profileData.is_team_member,
          agency_id: profileData.agency_id,
          agency_name: profileData.agency_name,
          role: profileData.role,
          personal_tier: profileData.personal_tier
        });
      }
    } catch (error) {
      // Profile fetch timeout is not critical - don't force re-login
      console.warn('⚠️ Error fetching user profile (non-critical):', error.message);
      // Fallback to querying Supabase directly if backend API fails
      try {
        const { data, error: supabaseError } = await supabase
          .from('user_profiles')
          .select('*')
          .eq('id', userId)
          .maybeSingle();

        if (data && !supabaseError) {
          console.log('✅ Fallback: User profile fetched from Supabase');
          setSubscription({
            ...data,
            tier: data?.subscription_tier,
            subscription_tier: data?.subscription_tier
          });
        }
      } catch (fallbackError) {
        console.warn('⚠️ Fallback profile fetch also failed:', fallbackError.message);
      }
    }
  };

  const login = async (email, password, rememberMe = true) => {
    try {
      console.log('🔑 Attempting login for:', email, rememberMe ? '(will remember)' : '(session only)');
      
      const { user, error } = await signIn(email, password);
      
      if (error) {
        console.error('❌ Supabase login error:', error);
        let errorMessage = 'Login failed. Please check your credentials.';
        
        // Provide more specific error messages
        if (error.message.includes('Invalid login credentials')) {
          errorMessage = 'Invalid email or password. Please try again.';
        } else if (error.message.includes('Email not confirmed')) {
          errorMessage = 'Please check your email and confirm your account before signing in.';
        } else if (error.message.includes('Too many requests')) {
          errorMessage = 'Too many login attempts. Please wait a moment and try again.';
        } else if (error.message) {
          errorMessage = error.message;
        }
        
        return { success: false, error: errorMessage };
      }
      
      if (user) {
        console.log('✅ Login successful for user:', user.id);

        // Immediately set auth state to avoid redirect race conditions
        try {
          setUser(user);
          setIsAuthenticated(true);
        } catch (stateError) {
          console.warn('⚠️ Failed to set auth state immediately after login (will rely on onAuthStateChange):', stateError);
        }
        
        // Store remember me preference
        if (rememberMe) {
          localStorage.setItem('adcopysurge-remember-user', 'true');
          console.log('💾 User will be remembered');
        } else {
          localStorage.setItem('adcopysurge-remember-user', 'false');
          console.log('🔄 Session-only login');
        }
        
        toast.success('Successfully logged in!');
        
        // The onAuthStateChange listener will continue to keep state in sync
        return { success: true };
      } else {
        console.warn('⚠️ No user returned from Supabase');
        return { success: false, error: 'Login failed. Please try again.' };
      }
    } catch (error) {
      console.error('💥 Unexpected login error:', error);
      return { success: false, error: 'An unexpected error occurred. Please try again.' };
    }
  };

  const register = async (userData) => {
    try {
      console.log('📝 Attempting registration for:', userData.email);
      const { email, password, full_name, company } = userData;
      const { user, error } = await signUp(email, password, {
        full_name,
        company
      });
      
      if (error) {
        console.error('❌ Supabase registration error:', error);
        let errorMessage = 'Registration failed. Please try again.';
        
        // Provide more specific error messages
        if (error.message.includes('User already registered')) {
          errorMessage = 'An account with this email already exists. Please try signing in instead.';
        } else if (error.message.includes('Password should be')) {
          errorMessage = 'Password must be at least 6 characters long.';
        } else if (error.message.includes('Invalid email')) {
          errorMessage = 'Please enter a valid email address.';
        } else if (error.message) {
          errorMessage = error.message;
        }
        
        return { success: false, error: errorMessage };
      }
      
      // Create user profile
      if (user) {
        console.log('✅ Registration successful for user:', user.id);
        await createUserProfile(user, { full_name, company });
      }
      
      toast.success('Registration successful! Please check your email to verify your account.');
      return { success: true };
    } catch (error) {
      console.error('💥 Unexpected registration error:', error);
      return { success: false, error: 'An unexpected error occurred. Please try again.' };
    }
  };

  const createUserProfile = async (user, userData) => {
    try {
      const { error } = await supabase
        .from('user_profiles')
        .insert({
          id: user.id,
          email: user.email,
          full_name: userData.full_name,
          company: userData.company,
          subscription_tier: 'free',
          monthly_analyses: 0,
          subscription_active: true,
          created_at: new Date().toISOString()
        });
      
      if (error) {
        console.error('Error creating user profile:', error);
      }
    } catch (error) {
      console.error('Error creating user profile:', error);
    }
  };

  const logout = async () => {
    try {
      console.log('👋 Logging out user...');
      
      // Clear remember me preference
      localStorage.removeItem('adcopysurge-remember-user');
      
      await signOut();
      
      // Clear local state immediately
      setUser(null);
      setIsAuthenticated(false);
      setSubscription(null);
      
      console.log('✅ Logout successful');
      toast.success('Successfully logged out!');
    } catch (error) {
      console.error('❌ Logout failed:', error);
      toast.error('Logout failed. Please try again.');
    }
  };

  const value = {
    user,
    isAuthenticated,
    loading,
    subscription,
    login,
    register,
    logout,
    supabase, // Expose supabase client for direct use
    
    // Enhanced features
    isOnline,
    lastNetworkCheck,
    AuthUtils, // Expose auth utilities
    
    // Enhanced methods
    refreshSession: AuthUtils.refreshSession,
    handle401Error: AuthUtils.handle401Error,
    debugAuthState: typeof window !== 'undefined' ? window.debugAuthState : () => console.log('Debug not available')
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};
