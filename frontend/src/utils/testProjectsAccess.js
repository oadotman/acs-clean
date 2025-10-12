/**
 * Diagnostic utility to test Supabase projects table access
 * Run this from browser console to diagnose RLS issues
 */

import { supabase } from '../config/supabaseClient';

export async function testProjectsAccess() {
  console.group('🔍 Supabase Projects Access Diagnostic');
  
  try {
    // Test 1: Check auth session
    console.log('\n📋 Test 1: Checking auth session...');
    const { data: { session }, error: sessionError } = await supabase.auth.getSession();
    
    if (sessionError) {
      console.error('❌ Session error:', sessionError);
      return;
    }
    
    if (!session) {
      console.error('❌ No active session');
      return;
    }
    
    console.log('✅ Active session found');
    console.log('   User ID:', session.user.id);
    console.log('   Email:', session.user.email);
    console.log('   Token present:', !!session.access_token);
    
    const userId = session.user.id;
    
    // Test 2: Try to select from projects (READ)
    console.log('\n📋 Test 2: Testing SELECT from projects...');
    const { data: selectData, error: selectError } = await supabase
      .from('projects')
      .select('*')
      .limit(1);
    
    if (selectError) {
      console.error('❌ SELECT failed:', {
        message: selectError.message,
        code: selectError.code,
        details: selectError.details,
        hint: selectError.hint
      });
    } else {
      console.log('✅ SELECT successful');
      console.log('   Records found:', selectData?.length || 0);
    }
    
    // Test 3: Try to insert a test project (CREATE)
    console.log('\n📋 Test 3: Testing INSERT into projects...');
    const testProject = {
      user_id: userId,
      name: `Test Project ${Date.now()}`,
      description: 'Diagnostic test project',
      client_name: null
    };
    
    console.log('   Attempting insert:', testProject);
    
    const { data: insertData, error: insertError } = await supabase
      .from('projects')
      .insert(testProject)
      .select()
      .single();
    
    if (insertError) {
      console.error('❌ INSERT failed:', {
        message: insertError.message,
        code: insertError.code,
        details: insertError.details,
        hint: insertError.hint
      });
      
      // Provide helpful diagnosis
      if (insertError.code === '42501') {
        console.warn('💡 DIAGNOSIS: Permission denied (42501)');
        console.warn('   This means RLS is blocking the insert.');
        console.warn('   Solution: Run the RLS fix migration in Supabase SQL Editor');
        console.warn('   File: database/migrations/003_fix_projects_rls_complete.sql');
      } else if (insertError.code === '23503') {
        console.warn('💡 DIAGNOSIS: Foreign key constraint violation (23503)');
        console.warn('   The user_id references a non-existent user.');
        console.warn('   Solution: Check if user exists in auth.users table');
      } else if (insertError.message?.includes('timeout')) {
        console.warn('💡 DIAGNOSIS: Request timeout');
        console.warn('   The database might be hanging on the insert.');
        console.warn('   Solution: Check for foreign key constraints or triggers');
      }
    } else {
      console.log('✅ INSERT successful!');
      console.log('   Created project:', insertData);
      
      // Cleanup: delete the test project
      console.log('\n🧹 Cleaning up test project...');
      const { error: deleteError } = await supabase
        .from('projects')
        .delete()
        .eq('id', insertData.id);
      
      if (deleteError) {
        console.warn('⚠️ Failed to cleanup test project:', deleteError.message);
      } else {
        console.log('✅ Test project cleaned up');
      }
    }
    
    // Test 4: Check RLS status (this requires a custom function or SQL)
    console.log('\n📋 Test 4: Summary');
    console.log('──────────────────────────────────────');
    
    if (!selectError && !insertError) {
      console.log('✅ ALL TESTS PASSED');
      console.log('   Your projects table is accessible and working correctly.');
    } else {
      console.log('❌ SOME TESTS FAILED');
      console.log('   Check the errors above for diagnosis.');
      console.log('\n💡 RECOMMENDED ACTION:');
      console.log('   1. Run the RLS fix migration:');
      console.log('      database/migrations/003_fix_projects_rls_complete.sql');
      console.log('   2. Re-run this diagnostic test');
    }
    
  } catch (error) {
    console.error('💥 Unexpected error:', error);
  } finally {
    console.groupEnd();
  }
}

// Auto-run if loaded directly in browser console
if (typeof window !== 'undefined') {
  window.testProjectsAccess = testProjectsAccess;
  console.log('✅ Diagnostic loaded! Run: testProjectsAccess()');
}

export default testProjectsAccess;
