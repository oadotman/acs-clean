import { supabase } from '../lib/supabaseClient';

/**
 * Supabase Debug Utility
 * Helps diagnose authentication, RLS, and API issues
 */

export const debugSupabaseAuth = async () => {
  console.log('🔍 Debugging Supabase Authentication...');
  
  try {
    // Check current session
    const { data: { session }, error: sessionError } = await supabase.auth.getSession();
    
    console.log('📋 Session Status:');
    console.log('- Session exists:', !!session);
    console.log('- Session error:', sessionError);
    
    if (session) {
      console.log('- User ID:', session.user.id);
      console.log('- User email:', session.user.email);
      console.log('- Access token length:', session.access_token.length);
      console.log('- Token expires at:', new Date(session.expires_at * 1000));
      console.log('- Token valid:', session.expires_at > Date.now() / 1000);
    }
    
    // Check current user
    const { data: { user }, error: userError } = await supabase.auth.getUser();
    
    console.log('👤 User Status:');
    console.log('- User exists:', !!user);
    console.log('- User error:', userError);
    
    if (user) {
      console.log('- User ID:', user.id);
      console.log('- Email verified:', user.email_confirmed_at ? 'Yes' : 'No');
      console.log('- Last sign in:', user.last_sign_in_at);
    }
    
    return { session, user, errors: { sessionError, userError } };
  } catch (error) {
    console.error('❌ Auth debug failed:', error);
    return { error };
  }
};

export const debugSupabaseRLS = async () => {
  console.log('🔍 Debugging Supabase RLS Policies...');
  
  try {
    const { data: { session } } = await supabase.auth.getSession();
    
    if (!session) {
      console.log('❌ No session - cannot test RLS');
      return { error: 'No authenticated session' };
    }
    
    const userId = session.user.id;
    console.log('🧪 Testing RLS with user ID:', userId);
    
    // Test user_profiles access
    console.log('📊 Testing user_profiles table...');
    const { data: profile, error: profileError } = await supabase
      .from('user_profiles')
      .select('*')
      .eq('id', userId)
      .single();
    
    console.log('- Profile data:', profile ? 'Found' : 'Not found');
    console.log('- Profile error:', profileError);
    
    // Test ad_copy_projects access
    console.log('📊 Testing ad_copy_projects table...');
    const { data: projects, error: projectsError } = await supabase
      .from('ad_copy_projects')
      .select('*')
      .limit(5);
    
    console.log('- Projects found:', projects?.length || 0);
    console.log('- Projects error:', projectsError);
    
    // Test ad_analyses access
    console.log('📊 Testing ad_analyses table...');
    const { data: analyses, error: analysesError } = await supabase
      .from('ad_analyses')
      .select('*')
      .limit(5);
    
    console.log('- Analyses found:', analyses?.length || 0);
    console.log('- Analyses error:', analysesError);
    
    return {
      userId,
      tests: {
        profile: { data: profile, error: profileError },
        projects: { data: projects, error: projectsError },
        analyses: { data: analyses, error: analysesError }
      }
    };
    
  } catch (error) {
    console.error('❌ RLS debug failed:', error);
    return { error };
  }
};

export const debugSupabaseHeaders = async () => {
  console.log('🔍 Debugging Supabase Request Headers...');
  
  try {
    const { data: { session } } = await supabase.auth.getSession();
    
    if (!session) {
      console.log('❌ No session - cannot check headers');
      return { error: 'No authenticated session' };
    }
    
    // Get the headers that Supabase should be using
    const headers = {
      'Authorization': `Bearer ${session.access_token}`,
      'apikey': supabase.supabaseKey,
      'Content-Type': 'application/json',
      'Prefer': 'return=minimal'
    };
    
    console.log('📋 Expected headers:');
    console.log('- Authorization:', headers.Authorization ? 'Bearer token present' : 'Missing');
    console.log('- apikey:', headers.apikey ? 'Present' : 'Missing');
    console.log('- Content-Type:', headers['Content-Type']);
    
    // Test a simple request to see what headers are actually sent
    console.log('🧪 Testing actual request...');
    
    const response = await fetch(`${supabase.supabaseUrl}/rest/v1/user_profiles?select=id&limit=1`, {
      headers
    });
    
    console.log('- Response status:', response.status);
    console.log('- Response statusText:', response.statusText);
    
    if (!response.ok) {
      const errorText = await response.text();
      console.log('- Error response:', errorText);
    }
    
    return { headers, response: { status: response.status, ok: response.ok } };
    
  } catch (error) {
    console.error('❌ Headers debug failed:', error);
    return { error };
  }
};

export const fixSupabaseAuth = async () => {
  console.log('🔧 Attempting to fix Supabase authentication issues...');
  
  try {
    // Refresh the session
    const { data, error } = await supabase.auth.refreshSession();
    
    if (error) {
      console.log('❌ Session refresh failed:', error.message);
      
      // Try to re-authenticate if refresh fails
      console.log('🔄 Attempting to restore session...');
      
      // Check if we have session data in localStorage
      const localSession = localStorage.getItem('sb-' + supabase.supabaseUrl.split('://')[1].split('.')[0] + '-auth-token');
      
      if (localSession) {
        try {
          const sessionData = JSON.parse(localSession);
          console.log('📱 Found local session data');
          
          // Set the session manually
          const { error: setError } = await supabase.auth.setSession({
            access_token: sessionData.access_token,
            refresh_token: sessionData.refresh_token
          });
          
          if (setError) {
            console.log('❌ Failed to restore session:', setError.message);
          } else {
            console.log('✅ Session restored successfully');
          }
        } catch (parseError) {
          console.log('❌ Failed to parse local session:', parseError.message);
        }
      }
    } else {
      console.log('✅ Session refreshed successfully');
    }
    
    return { data, error };
    
  } catch (error) {
    console.error('❌ Auth fix failed:', error);
    return { error };
  }
};

export const runFullDiagnostic = async () => {
  console.log('🚀 Running full Supabase diagnostic...');
  console.log('=====================================');
  
  const results = {};
  
  // Test authentication
  results.auth = await debugSupabaseAuth();
  
  console.log(''); // Empty line for readability
  
  // Test RLS if authenticated
  if (results.auth.session) {
    results.rls = await debugSupabaseRLS();
    
    console.log(''); // Empty line for readability
    
    // Test headers
    results.headers = await debugSupabaseHeaders();
  }
  
  console.log(''); // Empty line for readability
  console.log('=====================================');
  console.log('🏁 Diagnostic complete!');
  
  // Provide recommendations
  if (!results.auth.session) {
    console.log('💡 Recommendation: User needs to sign in');
  } else if (results.rls?.tests?.profile?.error) {
    console.log('💡 Recommendation: Check RLS policies for user_profiles table');
  } else if (results.headers?.response?.status === 401) {
    console.log('💡 Recommendation: Authentication token may be invalid or expired');
  } else {
    console.log('✅ Everything looks good!');
  }
  
  return results;
};

// Export a global debug function for browser console
if (typeof window !== 'undefined') {
  window.debugSupabase = runFullDiagnostic;
  window.supabaseAuth = debugSupabaseAuth;
  window.supabaseRLS = debugSupabaseRLS;
  window.fixSupabaseAuth = fixSupabaseAuth;
}