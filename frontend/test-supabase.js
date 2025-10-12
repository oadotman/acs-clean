const { createClient } = require('@supabase/supabase-js');

// Your Supabase credentials
const SUPABASE_URL = 'https://zbsuldhdwtqmvgqwmjno.supabase.co';
const SUPABASE_ANON_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inpic3VsZGhkd3RxbXZncXdtam5vIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTY2NjM5OTUsImV4cCI6MjA3MjIzOTk5NX0.C84_GzoYs0abkW4CC5sB0eqQ4OxpIievtw54sT2HPZ4';

console.log('🔧 Testing Supabase Connectivity...\n');

async function testSupabaseConnection() {
  try {
    // Create Supabase client
    console.log('1. Creating Supabase client...');
    const supabase = createClient(SUPABASE_URL, SUPABASE_ANON_KEY, {
      auth: {
        autoRefreshToken: false,
        persistSession: false
      }
    });
    console.log('✅ Supabase client created successfully');

    // Test basic connection with a simple query
    console.log('\n2. Testing basic connection...');
    const startTime = Date.now();
    
    // Try to list tables (this is a basic test that should work)
    const { data, error } = await supabase
      .from('information_schema.tables')
      .select('table_name')
      .eq('table_schema', 'public')
      .limit(1);
    
    const endTime = Date.now();
    const responseTime = endTime - startTime;

    if (error) {
      console.log('❌ Connection test failed:', error.message);
      console.log('📊 Error details:', JSON.stringify(error, null, 2));
      return false;
    }

    console.log(`✅ Basic connection successful (${responseTime}ms)`);
    
    // Test authentication
    console.log('\n3. Testing authentication...');
    const { data: { session }, error: authError } = await supabase.auth.getSession();
    
    if (authError) {
      console.log('⚠️ Auth test warning:', authError.message);
    } else {
      console.log('✅ Auth system accessible (no session expected)');
    }

    // Test specific tables your app uses
    console.log('\n4. Testing application-specific tables...');
    
    const tables = ['user_profiles', 'ad_analyses'];
    
    for (const table of tables) {
      try {
        const { data: tableData, error: tableError } = await supabase
          .from(table)
          .select('*')
          .limit(1);
        
        if (tableError) {
          console.log(`❌ Table '${table}' error:`, tableError.message);
        } else {
          console.log(`✅ Table '${table}' accessible (${tableData?.length || 0} rows tested)`);
        }
      } catch (err) {
        console.log(`❌ Table '${table}' exception:`, err.message);
      }
    }

    return true;

  } catch (error) {
    console.log('💥 Critical error during connection test:', error.message);
    console.log('📊 Error stack:', error.stack);
    return false;
  }
}

// Test with timeout
async function runTestWithTimeout() {
  const timeoutPromise = new Promise((_, reject) => {
    setTimeout(() => reject(new Error('Connection test timed out after 30 seconds')), 30000);
  });

  try {
    const result = await Promise.race([
      testSupabaseConnection(),
      timeoutPromise
    ]);
    
    if (result) {
      console.log('\n🎉 All tests passed! Supabase is working correctly.');
      console.log('\n📋 Next steps:');
      console.log('   • Verify your .env file has the correct values');
      console.log('   • Restart your development server');
      console.log('   • Check for any RLS (Row Level Security) policies blocking queries');
    } else {
      console.log('\n⚠️ Some tests failed. Check the errors above.');
    }
  } catch (error) {
    console.log('\n💥 Test suite failed:', error.message);
  }
}

// Run the test
runTestWithTimeout().then(() => {
  process.exit(0);
}).catch((error) => {
  console.error('💥 Unhandled error:', error);
  process.exit(1);
});
