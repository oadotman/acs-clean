import { createClient } from '@supabase/supabase-js'

// Get environment variables
const supabaseUrl = process.env.REACT_APP_SUPABASE_URL
const supabaseAnonKey = process.env.REACT_APP_SUPABASE_ANON_KEY

// Validate required environment variables
if (!supabaseUrl) {
  throw new Error('Missing env.REACT_APP_SUPABASE_URL')
}
if (!supabaseAnonKey) {
  throw new Error('Missing env.REACT_APP_SUPABASE_ANON_KEY')
}

// Create Supabase client with clean configuration
export const supabase = createClient(supabaseUrl, supabaseAnonKey, {
  auth: {
    autoRefreshToken: true,
    persistSession: true,
    detectSessionInUrl: true
  },
  realtime: {
    params: {
      eventsPerSecond: 2
    }
  }
})

export default supabase