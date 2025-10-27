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

// Create a minimal Supabase client
export const supabase = createClient(supabaseUrl, supabaseAnonKey, {
  auth: {
    persistSession: true,
    storageKey: 'adcopysurge-supabase-auth-token',
    storage: typeof window !== 'undefined' ? window.localStorage : undefined
  }
});

// Export auth helper functions for backward compatibility
export const signIn = async (email, password) => {
  return await supabase.auth.signInWithPassword({ email, password });
};

export const signUp = async (email, password, options = {}) => {
  return await supabase.auth.signUp({ email, password, options });
};

export const signOut = async () => {
  return await supabase.auth.signOut();
};

export const getCurrentUser = async () => {
  const { data: { user } } = await supabase.auth.getUser();
  return user;
};

export default supabase;
