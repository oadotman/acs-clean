// Authentication debugging utilities
import { supabase } from '../lib/supabaseClient';

export const runAuthDiagnostics = async () => {
  console.log('🔧 === AUTHENTICATION DIAGNOSTICS ===');
  
  // Check environment variables
  console.log('🔧 Environment Configuration:');
  console.log('- Supabase URL:', process.env.REACT_APP_SUPABASE_URL ? '✅ Set' : '❌ Missing');
  console.log('- Supabase Anon Key:', process.env.REACT_APP_SUPABASE_ANON_KEY ? '✅ Set' : '❌ Missing');
  console.log('- Node Environment:', process.env.NODE_ENV);
  
  // Check network connectivity
  console.log('\n🌐 Network Connectivity:');
  try {
    const startTime = Date.now();
    const response = await fetch('https://httpbin.org/get', { 
      method: 'GET',
      cache: 'no-cache',
      signal: AbortSignal.timeout(5000)
    });
    const endTime = Date.now();
    console.log(`- Basic connectivity: ✅ OK (${endTime - startTime}ms)`);
  } catch (error) {
    console.log('- Basic connectivity: ❌ Failed -', error.message);
  }
  
  // Check Supabase connectivity
  console.log('\n🔗 Supabase Connectivity:');
  try {
    const startTime = Date.now();
    const { data, error } = await supabase.auth.getSession();
    const endTime = Date.now();
    
    if (error) {
      console.log(`- Supabase auth: ❌ Error (${endTime - startTime}ms) -`, error.message);
    } else {
      console.log(`- Supabase auth: ✅ OK (${endTime - startTime}ms)`);
      console.log('- Session status:', data.session ? '✅ Active session' : '🔄 No session');
    }
  } catch (error) {
    console.log('- Supabase auth: ❌ Exception -', error.message);
  }
  
  // Check localStorage
  console.log('\n💾 Local Storage:');
  try {
    const authKeys = Object.keys(localStorage).filter(key => 
      key.includes('supabase') || key.includes('adcopysurge')
    );
    
    if (authKeys.length === 0) {
      console.log('- Auth tokens: 🔄 None found');
    } else {
      console.log('- Auth tokens found:', authKeys.length);
      authKeys.forEach(key => {
        try {
          const value = localStorage.getItem(key);
          const parsed = JSON.parse(value);
          if (parsed.expires_at) {
            const expiresAt = new Date(parsed.expires_at * 1000);
            const isExpired = expiresAt < new Date();
            console.log(`  - ${key}: ${isExpired ? '❌ Expired' : '✅ Valid'} (expires: ${expiresAt.toLocaleString()})`);
          } else {
            console.log(`  - ${key}: 🔄 Non-session data`);
          }
        } catch (e) {
          console.log(`  - ${key}: ❌ Parse error`);
        }
      });
    }
  } catch (error) {
    console.log('- localStorage access: ❌ Failed -', error.message);
  }
  
  // Test authenticated API requests
  console.log('\n🔐 Authenticated API Tests:');
  try {
    const { data: { session }, error: sessionError } = await supabase.auth.getSession();
    
    if (sessionError || !session) {
      console.log('- API tests skipped: ❌ No active session');
    } else {
      console.log('- Session found, testing authenticated requests...');
      
      // Test user_profiles request (the one that's failing according to logs)
      try {
        const startTime = Date.now();
        const { data, error } = await supabase
          .from('user_profiles')
          .select('*')
          .eq('id', session.user.id)
          .limit(1);
        const endTime = Date.now();
        
        if (error) {
          console.log(`- user_profiles query: ❌ Failed (${endTime - startTime}ms)`);
          console.log(`  Error: ${error.message}`);
          console.log(`  Code: ${error.code}`);
          console.log(`  Hint: ${error.hint || 'N/A'}`);
        } else {
          console.log(`- user_profiles query: ✅ Success (${endTime - startTime}ms)`);
        }
      } catch (profileError) {
        console.log('- user_profiles query: ❌ Exception -', profileError.message);
      }
      
      // Test projects request (another failing one from logs)
      try {
        const startTime = Date.now();
        const { data, error } = await supabase
          .from('ad_copy_projects')
          .select('id, project_name, status')
          .eq('user_id', session.user.id)
          .limit(1);
        const endTime = Date.now();
        
        if (error) {
          console.log(`- ad_copy_projects query: ❌ Failed (${endTime - startTime}ms)`);
          console.log(`  Error: ${error.message}`);
          console.log(`  Code: ${error.code}`);
          console.log(`  Hint: ${error.hint || 'N/A'}`);
        } else {
          console.log(`- ad_copy_projects query: ✅ Success (${endTime - startTime}ms)`);
        }
      } catch (projectError) {
        console.log('- ad_copy_projects query: ❌ Exception -', projectError.message);
      }
    }
  } catch (error) {
    console.log('- API tests: ❌ Failed -', error.message);
  }
  
  // Performance check
  console.log('\n⚡ Performance Tests:');
  const tests = [
    { name: 'getSession', fn: () => supabase.auth.getSession() },
    { name: 'getUser', fn: () => supabase.auth.getUser() }
  ];
  
  for (const test of tests) {
    try {
      const startTime = Date.now();
      await test.fn();
      const endTime = Date.now();
      const duration = endTime - startTime;
      
      let status = '✅ Good';
      if (duration > 5000) status = '❌ Very Slow';
      else if (duration > 2000) status = '⚠️ Slow';
      else if (duration > 1000) status = '🔄 Moderate';
      
      console.log(`- ${test.name}: ${status} (${duration}ms)`);
    } catch (error) {
      console.log(`- ${test.name}: ❌ Failed -`, error.message);
    }
  }
  
  console.log('\n🔧 === END DIAGNOSTICS ===');
  
  // Recommendations
  console.log('\n💡 Recommendations:');
  const recommendations = [];
  
  if (!process.env.REACT_APP_SUPABASE_URL || !process.env.REACT_APP_SUPABASE_ANON_KEY) {
    recommendations.push('- Check your .env file contains REACT_APP_SUPABASE_URL and REACT_APP_SUPABASE_ANON_KEY');
  }
  
  // Check if we detected the specific "No API key found" issue
  console.log('\n🕵️ Specific Issue Checks:');
  console.log('If you\'re seeing "No API key found in request" errors:');
  console.log('1. Verify your .env file has the correct REACT_APP_SUPABASE_ANON_KEY');
  console.log('2. Restart your development server after changing .env');
  console.log('3. Check browser DevTools Network tab - requests should have:');
  console.log('   - "apikey" header with your anon key, OR');
  console.log('   - "Authorization: Bearer <jwt>" header for authenticated users');
  console.log('4. Clear browser cache and localStorage if issues persist');
  console.log('\n🔧 Debug commands:');
  console.log('- window.runAuthDiagnostics() - Run this full diagnostic');
  console.log('- window.debugAuthState() - Quick auth state check (if available)');
  
  if (recommendations.length === 0) {
    console.log('\n✅ No specific configuration issues detected.');
    console.log('If problems persist, check:');
    console.log('- Network connectivity and Supabase service status');
    console.log('- Browser console for additional error details');
    console.log('- Supabase dashboard logs for server-side errors');
  } else {
    console.log('\n⚠️ Configuration Issues Found:');
    recommendations.forEach(rec => console.log(rec));
  }
};

// Make it available globally in development
if (process.env.NODE_ENV === 'development' && typeof window !== 'undefined') {
  window.runAuthDiagnostics = runAuthDiagnostics;
  console.log('🔧 Auth diagnostics available: window.runAuthDiagnostics()');
}

export default runAuthDiagnostics;
