const { createClient } = require('@supabase/supabase-js');

// Load environment variables manually since this is a Node script
require('dotenv').config();

// Your current Supabase credentials from .env
const SUPABASE_URL = process.env.REACT_APP_SUPABASE_URL || 'https://tqzlsajhhtkhljdbjkyg.supabase.co';
const SUPABASE_ANON_KEY = process.env.REACT_APP_SUPABASE_ANON_KEY || 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InRxemxzYWpoaHRraGxqZGJqa3lnIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTY5OTYzOTMsImV4cCI6MjA3MjU3MjM5M30.0uI56qJGE5DQwEvcfYlcOIz2NGC-msMVrTRw6d-RQuI';

console.log('🔍 AdCopySurge Database Diagnostic Tool\n');
console.log('📋 Configuration:');
console.log(`   • Supabase URL: ${SUPABASE_URL}`);
console.log(`   • Anon Key: ${SUPABASE_ANON_KEY.substring(0, 30)}...`);

async function diagnoseDatabase() {
  try {
    // Create Supabase client
    console.log('\n1. Creating Supabase client...');
    const supabase = createClient(SUPABASE_URL, SUPABASE_ANON_KEY, {
      auth: {
        autoRefreshToken: false,
        persistSession: false
      }
    });
    console.log('   ✅ Client created successfully');

    // Test basic connection
    console.log('\n2. Testing connection...');
    const { data: { session }, error: authError } = await supabase.auth.getSession();
    
    if (authError) {
      console.log('   ⚠️ Auth system warning:', authError.message);
    } else {
      console.log('   ✅ Connection successful');
    }

    // Check what tables exist in the database
    console.log('\n3. Checking existing tables...');
    
    // List of tables your app expects to find
    const expectedTables = [
      'user_profiles',
      'ad_copy_projects',     // This is the one causing 401 errors
      'tool_analysis_results',
      'analysis_pipeline_runs',
      'project_collaborators',
      'ad_analyses',          // Legacy table
      'competitor_benchmarks', // Legacy table  
      'ad_generations'        // Legacy table
    ];

    let existingTables = [];
    let missingTables = [];
    let accessibleTables = [];
    let blockedTables = [];

    for (const tableName of expectedTables) {
      try {
        console.log(`   Checking table: ${tableName}...`);
        
        const { data, error, count } = await supabase
          .from(tableName)
          .select('*', { count: 'exact', head: true });
        
        if (error) {
          if (error.code === '42P01') {
            // Table does not exist
            console.log(`   ❌ Table '${tableName}' does not exist`);
            missingTables.push(tableName);
          } else if (error.code === 'PGRST301') {
            // RLS policy blocking access
            console.log(`   🔒 Table '${tableName}' exists but RLS is blocking access: ${error.message}`);
            existingTables.push(tableName);
            blockedTables.push(tableName);
          } else {
            console.log(`   ❌ Table '${tableName}' error: ${error.code} - ${error.message}`);
            if (error.message.toLowerCase().includes('does not exist')) {
              missingTables.push(tableName);
            } else {
              existingTables.push(tableName);
              blockedTables.push(tableName);
            }
          }
        } else {
          console.log(`   ✅ Table '${tableName}' accessible (${count || 0} rows)`);
          existingTables.push(tableName);
          accessibleTables.push(tableName);
        }
      } catch (err) {
        console.log(`   💥 Table '${tableName}' exception: ${err.message}`);
        missingTables.push(tableName);
      }
    }

    // Summary
    console.log('\n📊 Diagnostic Summary:');
    console.log(`   • Total expected tables: ${expectedTables.length}`);
    console.log(`   • Existing tables: ${existingTables.length}`);
    console.log(`   • Accessible tables: ${accessibleTables.length}`);
    console.log(`   • Blocked by RLS: ${blockedTables.length}`);
    console.log(`   • Missing tables: ${missingTables.length}`);

    if (accessibleTables.length > 0) {
      console.log('\n✅ Accessible Tables:');
      accessibleTables.forEach(table => console.log(`   • ${table}`));
    }

    if (blockedTables.length > 0) {
      console.log('\n🔒 Tables Blocked by RLS:');
      blockedTables.forEach(table => console.log(`   • ${table}`));
    }

    if (missingTables.length > 0) {
      console.log('\n❌ Missing Tables:');
      missingTables.forEach(table => console.log(`   • ${table}`));
    }

    // Specific diagnosis for the 401 error
    console.log('\n🎯 401 Error Analysis:');
    
    if (missingTables.includes('ad_copy_projects')) {
      console.log('   🔍 FOUND THE PROBLEM: The ad_copy_projects table does not exist!');
      console.log('   💡 This explains the 401 errors - your app is trying to access a non-existent table.');
      console.log('   🛠️  SOLUTION: You need to create the ad_copy_projects table and related tables.');
    } else if (blockedTables.includes('ad_copy_projects')) {
      console.log('   🔍 FOUND THE PROBLEM: The ad_copy_projects table exists but RLS is blocking access!');
      console.log('   💡 This explains the 401 errors - Row Level Security policies are preventing access.');
      console.log('   🛠️  SOLUTION: You need to fix the RLS policies to allow authenticated users access.');
    } else if (accessibleTables.includes('ad_copy_projects')) {
      console.log('   ❓ MYSTERY: The ad_copy_projects table seems accessible from here...');
      console.log('   💡 The 401 error might be caused by token expiration or different user context.');
      console.log('   🛠️  SOLUTION: Check token refresh logic and user authentication state.');
    } else {
      console.log('   ❓ Unable to determine the exact cause of 401 errors from this diagnostic.');
    }

    // Recommendations
    console.log('\n💡 Recommendations:');
    
    if (missingTables.length > 0) {
      console.log('   1. 📋 CREATE MISSING TABLES:');
      console.log('      • Go to your Supabase Dashboard: https://supabase.com/dashboard');
      console.log('      • Open your project: tqzlsajhhtkhljdbjkyg');
      console.log('      • Go to SQL Editor');
      console.log('      • Run the setup-missing-tables.sql script (found in src/sql/ folder)');
      console.log('      • Or manually create the missing tables based on your schema');
    }
    
    if (blockedTables.length > 0) {
      console.log('   2. 🔓 FIX RLS POLICIES:');
      console.log('      • Review Row Level Security policies in Supabase Dashboard');
      console.log('      • Ensure authenticated users can access their own data');
      console.log('      • Check that user_id columns match auth.uid() in policies');
    }
    
    console.log('   3. 🔄 RESTART YOUR DEV SERVER:');
    console.log('      • Stop your development server (Ctrl+C)');
    console.log('      • Run: npm start or yarn start');
    console.log('      • Try logging in again');
    
    console.log('   4. 🧪 TEST AUTHENTICATION:');
    console.log('      • Open browser dev tools');
    console.log('      • Try: window.debugAuthState() in console');
    console.log('      • Check if tokens are being stored correctly');

    return {
      status: 'complete',
      existingTables,
      missingTables,
      accessibleTables,
      blockedTables,
      recommendation: missingTables.length > 0 ? 'create_tables' : 
                     blockedTables.length > 0 ? 'fix_rls' : 'check_tokens'
    };

  } catch (error) {
    console.log('\n💥 Critical error during diagnosis:', error.message);
    console.log('📊 Error details:', error);
    
    console.log('\n🔧 Basic troubleshooting:');
    console.log('   • Check your internet connection');
    console.log('   • Verify Supabase project is not paused');
    console.log('   • Check if .env file has correct values');
    console.log('   • Try accessing Supabase dashboard directly');
    
    return {
      status: 'error',
      error: error.message
    };
  }
}

// Auto-fix function
async function createMissingTables() {
  console.log('\n🛠️  Attempting to create missing tables...');
  console.log('⚠️  This requires service role key - currently using anon key');
  console.log('💡 For security, table creation should be done via Supabase Dashboard');
  console.log('📋 Please follow the manual instructions above');
  
  return false;
}

// Main execution
async function main() {
  console.log('🚀 Starting database diagnosis...\n');
  
  const result = await diagnoseDatabase();
  
  if (result.status === 'complete') {
    console.log('\n🎉 Diagnosis completed successfully!');
    console.log(`📋 Next action recommended: ${result.recommendation}`);
    
    if (result.recommendation === 'create_tables') {
      console.log('\n📝 To fix the 401 errors, you need to create the missing database tables.');
      console.log('🔗 Quick fix: Go to https://supabase.com/dashboard and run the SQL schema');
    }
  } else {
    console.log('\n⚠️ Diagnosis encountered errors. See details above.');
  }
  
  console.log('\n🔚 Diagnosis complete. Check the recommendations above to fix your 401 errors.');
}

// Run the diagnostic
main().then(() => {
  process.exit(0);
}).catch((error) => {
  console.error('💥 Unhandled error:', error.message);
  process.exit(1);
});
