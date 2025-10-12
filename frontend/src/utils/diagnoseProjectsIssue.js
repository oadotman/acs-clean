/**
 * Comprehensive diagnostic to identify why projects can't be created
 * Run this in browser console to diagnose the issue
 */

import { supabase } from '../config/supabaseClient';

export async function diagnoseProjectsIssue() {
  console.group('🔍 COMPREHENSIVE PROJECTS DIAGNOSTIC');
  
  const results = {
    auth: false,
    connection: false,
    tableExists: false,
    canSelect: false,
    canInsert: false,
    rlsStatus: 'unknown',
    error: null
  };
  
  try {
    // ========== TEST 1: Auth Session ==========
    console.log('\n━━━ TEST 1: Checking Authentication ━━━');
    const { data: { session }, error: sessionError } = await supabase.auth.getSession();
    
    if (sessionError) {
      console.error('❌ Session error:', sessionError);
      results.error = sessionError;
      return results;
    }
    
    if (!session) {
      console.error('❌ No active session - Please log in');
      results.error = 'No active session';
      return results;
    }
    
    results.auth = true;
    const userId = session.user.id;
    console.log('✅ Authenticated as:', userId);
    console.log('   Email:', session.user.email);
    console.log('   Role:', session.user.role);
    
    // ========== TEST 2: Supabase Connection ==========
    console.log('\n━━━ TEST 2: Testing Supabase Connection ━━━');
    try {
      // Test with a simple query to system catalog
      const { data: tablesData, error: tablesError } = await supabase
        .from('projects')
        .select('*')
        .limit(0); // Don't fetch data, just test connection
      
      if (tablesError && !tablesError.message.includes('permission')) {
        console.error('❌ Connection issue:', tablesError);
        results.error = tablesError;
      } else {
        console.log('✅ Supabase connection successful');
        results.connection = true;
      }
    } catch (e) {
      console.error('❌ Connection failed:', e);
      results.error = e;
    }
    
    // ========== TEST 3: Table Existence ==========
    console.log('\n━━━ TEST 3: Checking if projects table exists ━━━');
    const { data: tableCheck, error: tableError } = await supabase
      .rpc('get_table_info', { table_name: 'projects' })
      .single();
    
    if (tableError) {
      // Try alternate method
      const { count, error: countError } = await supabase
        .from('projects')
        .select('*', { count: 'exact', head: true });
      
      if (!countError) {
        console.log('✅ Table exists (count check successful)');
        results.tableExists = true;
      } else {
        console.warn('⚠️ Cannot verify table existence:', countError);
      }
    } else {
      console.log('✅ Table exists');
      results.tableExists = true;
    }
    
    // ========== TEST 4: SELECT Permission ==========
    console.log('\n━━━ TEST 4: Testing SELECT permission ━━━');
    const { data: selectData, error: selectError } = await supabase
      .from('projects')
      .select('id, name')
      .limit(1);
    
    if (selectError) {
      console.error('❌ SELECT failed:', {
        code: selectError.code,
        message: selectError.message,
        details: selectError.details
      });
      
      if (selectError.code === '42501') {
        console.warn('   → RLS is blocking SELECT');
        results.rlsStatus = 'blocking_select';
      }
    } else {
      console.log('✅ SELECT permission OK');
      console.log('   Found', selectData?.length || 0, 'projects');
      results.canSelect = true;
    }
    
    // ========== TEST 5: Direct INSERT Test ==========
    console.log('\n━━━ TEST 5: Testing INSERT with timeout protection ━━━');
    
    const testProject = {
      user_id: userId,
      name: `Diagnostic Test ${Date.now()}`,
      description: 'Auto-generated diagnostic test',
      client_name: null
    };
    
    console.log('📝 Attempting insert:', testProject);
    
    // Create insert promise with explicit timeout
    const insertPromise = supabase
      .from('projects')
      .insert(testProject)
      .select()
      .single();
    
    // Create timeout promise
    const timeoutPromise = new Promise((_, reject) => 
      setTimeout(() => reject(new Error('INSERT TIMEOUT - Request took more than 5 seconds')), 5000)
    );
    
    try {
      const { data: insertData, error: insertError } = await Promise.race([
        insertPromise,
        timeoutPromise
      ]);
      
      if (insertError) {
        console.error('❌ INSERT failed:', {
          code: insertError.code,
          message: insertError.message,
          details: insertError.details,
          hint: insertError.hint
        });
        
        // Specific error diagnosis
        if (insertError.code === '42501') {
          console.warn('   → RLS is blocking INSERT');
          results.rlsStatus = 'blocking_insert';
        } else if (insertError.code === '23503') {
          console.warn('   → Foreign key constraint issue (user_id)');
        } else if (insertError.code === '23505') {
          console.warn('   → Unique constraint violation');
        }
        
        results.error = insertError;
      } else {
        console.log('✅ INSERT successful!');
        console.log('   Created project:', insertData);
        results.canInsert = true;
        
        // Cleanup test project
        console.log('🧹 Cleaning up test project...');
        await supabase
          .from('projects')
          .delete()
          .eq('id', insertData.id);
        console.log('✅ Cleanup complete');
      }
    } catch (timeoutError) {
      console.error('❌ INSERT TIMEOUT:', timeoutError.message);
      console.warn('   The request is hanging - likely a constraint or trigger issue');
      results.error = timeoutError;
      results.rlsStatus = 'timeout';
    }
    
    // ========== TEST 6: Check Supabase Client Config ==========
    console.log('\n━━━ TEST 6: Checking Supabase Client Configuration ━━━');
    console.log('📌 Supabase URL:', supabase.supabaseUrl?.substring(0, 30) + '...');
    console.log('📌 Has Anon Key:', !!supabase.supabaseKey);
    console.log('📌 Auth Headers:', supabase.auth.headers);
    
    // Get current headers
    const { data: { session: currentSession } } = await supabase.auth.getSession();
    if (currentSession) {
      console.log('📌 Bearer Token Present:', !!currentSession.access_token);
      console.log('📌 Token first 20 chars:', currentSession.access_token?.substring(0, 20) + '...');
    }
    
  } catch (error) {
    console.error('💥 Unexpected error:', error);
    results.error = error;
  }
  
  // ========== FINAL DIAGNOSIS ==========
  console.log('\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
  console.log('📊 DIAGNOSIS SUMMARY:');
  console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
  
  console.table({
    'Authentication': results.auth ? '✅ OK' : '❌ Failed',
    'Connection': results.connection ? '✅ OK' : '❌ Failed',
    'Table Exists': results.tableExists ? '✅ Yes' : '❌ No',
    'SELECT Works': results.canSelect ? '✅ Yes' : '❌ No',
    'INSERT Works': results.canInsert ? '✅ Yes' : '❌ No',
    'RLS Status': results.rlsStatus
  });
  
  console.log('\n💡 RECOMMENDED ACTION:');
  
  if (results.canInsert) {
    console.log('✅ Everything is working! The issue might be in your frontend code.');
    console.log('   Check if there are any errors after the insert in projectsService.js');
  } else if (results.rlsStatus === 'timeout') {
    console.log('🔧 The INSERT is timing out. Possible causes:');
    console.log('   1. Foreign key constraint on user_id');
    console.log('   2. Database trigger causing infinite loop');
    console.log('   3. Network/firewall issue');
    console.log('\n   SOLUTION: Run this SQL to check constraints:');
    console.log(`
      -- Check foreign keys
      SELECT conname, contype, confrelid::regclass 
      FROM pg_constraint 
      WHERE conrelid = 'projects'::regclass;
      
      -- Check triggers
      SELECT tgname FROM pg_trigger WHERE tgrelid = 'projects'::regclass;
    `);
  } else if (results.rlsStatus?.includes('blocking')) {
    console.log('🔧 RLS is still enabled and blocking operations.');
    console.log('   Run this SQL in Supabase:');
    console.log('   ALTER TABLE projects DISABLE ROW LEVEL SECURITY;');
  } else if (!results.tableExists) {
    console.log('🔧 The projects table does not exist.');
    console.log('   Re-run the setup SQL script.');
  } else if (!results.auth) {
    console.log('🔧 Authentication issue. Please log in again.');
  }
  
  console.groupEnd();
  return results;
}

// Make it available globally
if (typeof window !== 'undefined') {
  window.diagnoseProjectsIssue = diagnoseProjectsIssue;
  console.log('');
  console.log('🚀 Diagnostic ready! Run this in console:');
  console.log('   diagnoseProjectsIssue()');
  console.log('');
}

export default diagnoseProjectsIssue;