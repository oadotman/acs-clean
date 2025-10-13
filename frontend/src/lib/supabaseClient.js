import { createClient } from '@supabase/supabase-js';

// Get environment variables
const supabaseUrl = process.env.REACT_APP_SUPABASE_URL;
const supabaseAnonKey = process.env.REACT_APP_SUPABASE_ANON_KEY;

// Validate environment variables
if (!supabaseUrl || !supabaseAnonKey) {
  console.error('❌ Supabase configuration missing!');
  console.error('URL:', supabaseUrl ? 'Present' : 'MISSING');
  console.error('Key:', supabaseAnonKey ? 'Present' : 'MISSING');
  throw new Error('Missing Supabase environment variables');
}

// Create a clean Supabase client without any custom configuration that might cause issues
export const supabase = createClient(supabaseUrl, supabaseAnonKey, {
  auth: {
    persistSession: true,
    storageKey: 'adcopysurge-supabase-auth-token',
    storage: typeof window !== 'undefined' ? window.localStorage : undefined
  }
});

console.log('✅ Supabase client initialized successfully');

// Debug auth state changes in development
if (process.env.NODE_ENV === 'development') {
  supabase.auth.onAuthStateChange((event, session) => {
    console.log('🔍 Supabase Auth Event:', event);
    console.log('📊 Session Status:', session ? 'Active' : 'None');
    if (session) {
      console.log('👤 User:', session.user.email);
      console.log('⏰ Expires:', new Date(session.expires_at * 1000).toLocaleString());
    }
  });
}

// Auth helpers
export const signUp = async (email, password, options = {}) => {
  console.log('📝 Supabase signUp called for:', email);
  
  try {
    const { data, error } = await supabase.auth.signUp({
      email,
      password,
      options: {
        data: options
      }
    });
    
    if (error) {
      console.error('❌ Supabase signup error:', error.message);
    } else if (data?.user) {
      console.log('✅ Supabase signup success:', data.user.email);
    }
    
    return { user: data?.user, error };
  } catch (err) {
    console.error('💥 Supabase signup client error:', err);
    return { user: null, error: err };
  }
};

export const signIn = async (email, password) => {
  console.log('🔑 Supabase signIn called for:', email);
  
  try {
    const { data, error } = await supabase.auth.signInWithPassword({
      email,
      password
    });
    
    if (error) {
      console.error('❌ Supabase auth error:', error.message);
    } else if (data?.user) {
      console.log('✅ Supabase auth success:', data.user.email);
    }
    
    return { user: data?.user, error };
  } catch (err) {
    console.error('💥 Supabase client error:', err);
    return { user: null, error: err };
  }
};

export const signOut = async () => {
  const { error } = await supabase.auth.signOut();
  return { error };
};

export const getCurrentUser = async () => {
  try {
    console.log('👤 Getting current user...');
    
    // First try to get session (faster and includes expiry info)
    const { data: { session }, error: sessionError } = await supabase.auth.getSession();
    
    if (sessionError) {
      console.error('❌ Session error:', sessionError);
      return null;
    }
    
    if (session?.user) {
      console.log('✅ Found user from session:', session.user.email);
      
      // Check if session is close to expiring (within 5 minutes)
      const expiresAt = new Date(session.expires_at * 1000);
      const now = new Date();
      const minutesUntilExpiry = (expiresAt.getTime() - now.getTime()) / (1000 * 60);
      
      if (minutesUntilExpiry < 5) {
        console.log('⚠️ Session expires in', Math.round(minutesUntilExpiry), 'minutes, will refresh soon');
      }
      
      return session.user;
    }
    
    // Fallback: try direct user fetch
    const { data: { user }, error: userError } = await supabase.auth.getUser();
    
    if (userError) {
      console.error('❌ User error:', userError);
      return null;
    }
    
    if (user) {
      console.log('✅ Found user from auth:', user.email);
      return user;
    }
    
    console.log('ℹ️ No user found');
    return null;
  } catch (error) {
    console.error('💥 Error getting current user:', error);
    return null;
  }
};

// Utility functions for debugging and session management
export const getSessionStatus = async () => {
  try {
    const { data: { session }, error } = await supabase.auth.getSession();
    
    if (error) {
      return { status: 'error', error: error.message };
    }
    
    if (!session) {
      return { status: 'no_session', user: null };
    }
    
    const expiresAt = new Date(session.expires_at * 1000);
    const now = new Date();
    const isExpired = expiresAt < now;
    const minutesUntilExpiry = (expiresAt.getTime() - now.getTime()) / (1000 * 60);
    
    return {
      status: isExpired ? 'expired' : 'active',
      user: session.user,
      expiresAt: expiresAt.toLocaleString(),
      minutesUntilExpiry: Math.round(minutesUntilExpiry),
      accessToken: session.access_token ? session.access_token.substring(0, 20) + '...' : null
    };
  } catch (error) {
    return { status: 'error', error: error.message };
  }
};

export const debugAuthState = async () => {
  console.log('🔧 === AUTH DEBUG INFO ===');
  
  const sessionStatus = await getSessionStatus();
  console.log('📊 Session Status:', sessionStatus);
  
  // Check localStorage for stored tokens
  const storedKeys = Object.keys(localStorage).filter(key => 
    key.includes('supabase') || key.includes('adcopysurge')
  );
  
  console.log('💾 Stored Keys:', storedKeys);
  
  storedKeys.forEach(key => {
    try {
      const value = localStorage.getItem(key);
      if (value) {
        const parsed = JSON.parse(value);
        if (parsed.expires_at) {
          const expiresAt = new Date(parsed.expires_at * 1000);
          console.log(`🔑 ${key}:`, {
            user: parsed.user?.email || 'No user',
            expires: expiresAt.toLocaleString(),
            expired: expiresAt < new Date()
          });
        }
      }
    } catch (e) {
      console.log(`🔑 ${key}: [Non-JSON value]`);
    }
  });
  
  console.log('🔧 === END AUTH DEBUG ===');
};

// Make debug function available globally in development
if (process.env.NODE_ENV === 'development' && typeof window !== 'undefined') {
  window.debugAuthState = debugAuthState;
  console.log('🔧 Auth debug function available: window.debugAuthState()');
}

export default supabase;
