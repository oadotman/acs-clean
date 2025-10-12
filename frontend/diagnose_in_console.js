// ============================================================================
// PASTE THIS ENTIRE SCRIPT IN BROWSER CONSOLE
// ============================================================================

(async function diagnoseProjectsIssue() {
  console.group('🔍 COMPREHENSIVE PROJECTS DIAGNOSTIC');
  
  // Get supabase from window (React apps often expose it)
  let supabase = null;
  
  // Try to find supabase client
  try {
    // Method 1: Check if exposed on window
    if (window.supabase) {
      supabase = window.supabase;
      console.log('✅ Found supabase on window');
    } 
    // Method 2: Try to extract from React DevTools
    else if (window.__REACT_DEVTOOLS_GLOBAL_HOOK__) {
      console.log('⚠️ Supabase not on window, trying React internals...');
      // This is a last resort - usually supabase should be on window
    }
    
    // If still no supabase, we need to manually create it
    if (!supabase) {
      console.log('📝 Creating supabase client manually...');
      
      // Get credentials from localStorage or prompt
      const url = localStorage.getItem('SUPABASE_URL') || 
                 prompt('Enter your Supabase URL (from your .env file):');
      const key = localStorage.getItem('SUPABASE_ANON_KEY') || 
                 prompt('Enter your Supabase Anon Key (from your .env file):');
      
      if (!url || !key) {
        console.error('❌ Cannot proceed without Supabase credentials');
        return;
      }
      
      // Dynamically load Supabase client
      const script = document.createElement('script');
      script.src = 'https://cdn.jsdelivr.net/npm/@supabase/supabase-js@2';
      document.head.appendChild(script);
      
      await new Promise(resolve => {
        script.onload = resolve;
      });
      
      // Create client
      const { createClient } = window.supabase;
      supabase = createClient(url, key);
      console.log('✅ Created Supabase client');
    }
  } catch (e) {
    console.error('Failed to setup Supabase:', e);
  }
  
  const results = {
    auth: false,
    connection: false,
    canSelect: false,
    canInsert: false,
    error: null
  };
  
  try {
    // TEST 1: Auth Session
    console.log('\n━━━ TEST 1: Checking Authentication ━━━');
    const { data: { session }, error: sessionError } = await supabase.auth.getSession();
    
    if (sessionError) {
      console.error('❌ Session error:', sessionError);
      results.error = sessionError;
    } else if (!session) {
      console.error('❌ No active session');
      
      // Try to get session from localStorage
      const storedSession = localStorage.getItem('sb-auth-token');
      if (storedSession) {
        console.log('   Found stored session, trying to restore...');
        const parsed = JSON.parse(storedSession);
        await supabase.auth.setSession(parsed);
        const { data: { session: newSession } } = await supabase.auth.getSession();
        if (newSession) {
          console.log('✅ Session restored');
          results.auth = true;
        }
      }
    } else {
      results.auth = true;
      console.log('✅ Authenticated as:', session.user.id);
      console.log('   Email:', session.user.email);
    }
    
    const userId = session?.user?.id || '5050583b-012e-448b-afef-1e8553b62192'; // Your user ID from logs
    
    // TEST 2: SELECT Test
    console.log('\n━━━ TEST 2: Testing SELECT from projects ━━━');
    try {
      const { data: selectData, error: selectError } = await supabase
        .from('projects')
        .select('*')
        .limit(1);
      
      if (selectError) {
        console.error('❌ SELECT failed:', selectError);
      } else {
        console.log('✅ SELECT successful');
        console.log('   Projects found:', selectData?.length || 0);
        if (selectData?.length > 0) {
          console.log('   Sample project:', selectData[0]);
        }
        results.canSelect = true;
      }
    } catch (e) {
      console.error('❌ SELECT exception:', e);
    }
    
    // TEST 3: INSERT Test with timeout
    console.log('\n━━━ TEST 3: Testing INSERT into projects ━━━');
    
    const testProject = {
      user_id: userId,
      name: `Browser Test ${Date.now()}`,
      description: 'Created from browser console diagnostic',
      client_name: null
    };
    
    console.log('📝 Attempting insert:', testProject);
    
    // Create promises for insert and timeout
    const insertPromise = supabase
      .from('projects')
      .insert(testProject)
      .select()
      .single();
    
    const timeoutPromise = new Promise((_, reject) => 
      setTimeout(() => reject(new Error('TIMEOUT after 5 seconds')), 5000)
    );
    
    try {
      const result = await Promise.race([insertPromise, timeoutPromise]);
      
      if (result.error) {
        console.error('❌ INSERT failed:', result.error);
      } else if (result.data) {
        console.log('✅ INSERT successful!');
        console.log('   Created project:', result.data);
        results.canInsert = true;
        
        // Cleanup
        console.log('🧹 Cleaning up test project...');
        await supabase.from('projects').delete().eq('id', result.data.id);
      }
    } catch (timeoutError) {
      if (timeoutError.message.includes('TIMEOUT')) {
        console.error('❌ INSERT TIMEOUT - Request hanging');
        console.log('   This usually means a constraint or trigger issue');
      } else {
        console.error('❌ INSERT error:', timeoutError);
      }
    }
    
    // TEST 4: Check what's actually in the projects table
    console.log('\n━━━ TEST 4: Checking existing projects ━━━');
    const { data: allProjects, error: allError } = await supabase
      .from('projects')
      .select('id, user_id, name, created_at')
      .order('created_at', { ascending: false })
      .limit(5);
    
    if (allError) {
      console.error('❌ Failed to fetch projects:', allError);
    } else {
      console.log(`✅ Found ${allProjects?.length || 0} projects total`);
      if (allProjects?.length > 0) {
        console.table(allProjects);
      }
    }
    
  } catch (error) {
    console.error('💥 Unexpected error:', error);
    results.error = error;
  }
  
  // FINAL DIAGNOSIS
  console.log('\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
  console.log('📊 DIAGNOSIS SUMMARY');
  console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
  
  console.table({
    'Authentication': results.auth ? '✅ OK' : '❌ Failed',
    'SELECT Works': results.canSelect ? '✅ Yes' : '❌ No',
    'INSERT Works': results.canInsert ? '✅ Yes' : '❌ No'
  });
  
  console.log('\n💡 DIAGNOSIS:');
  
  if (results.canInsert && results.canSelect) {
    console.log('✅ Database is working perfectly!');
    console.log('   The issue is in your frontend code.');
    console.log('   Check projectsService.js after line 167');
  } else if (!results.auth) {
    console.log('🔧 Authentication issue - try logging in again');
  } else if (results.canSelect && !results.canInsert) {
    console.log('🔧 Can read but not write - possible constraint issue');
  } else {
    console.log('🔧 Unknown issue - check the errors above');
  }
  
  console.groupEnd();
})();