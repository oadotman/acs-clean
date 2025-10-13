/**
 * Clean Supabase Client - Minimal configuration to avoid issues
 */
import { createClient } from '@supabase/supabase-js';

const supabaseUrl = process.env.REACT_APP_SUPABASE_URL;
const supabaseAnonKey = process.env.REACT_APP_SUPABASE_ANON_KEY;

if (!supabaseUrl || !supabaseAnonKey) {
  throw new Error('Missing Supabase environment variables');
}

// Create client with minimal config
const supabase = createClient(supabaseUrl, supabaseAnonKey);

console.log('✅ Clean Supabase client ready');

export { supabase };
export default supabase;