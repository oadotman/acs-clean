const { createClient } = require('@supabase/supabase-js');

// Your Supabase credentials
const SUPABASE_URL = 'https://zbsuldhdwtqmvgqwmjno.supabase.co';
const SUPABASE_ANON_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inpic3VsZGhkd3RxbXZncXdtam5vIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTY2NjM5OTUsImV4cCI6MjA3MjIzOTk5NX0.C84_GzoYs0abkW4CC5sB0eqQ4OxpIievtw54sT2HPZ4';

console.log('🔧 Testing AdCopySurge Supabase Connection with Bun...\n');

async function testAdCopySurgeDB() {
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

    // Test authentication system
    console.log('\n2. Testing authentication system...');
    const { data: { session }, error: authError } = await supabase.auth.getSession();
    
    if (authError) {
      console.log('⚠️ Auth system warning:', authError.message);
    } else {
      console.log('✅ Auth system accessible');
    }

    // Test your application tables
    console.log('\n3. Testing application tables...');
    
    const tablesToTest = [
      'user_profiles',
      'ad_analyses', 
      'competitor_benchmarks',
      'ad_generations'
    ];
    
    let successCount = 0;
    let tableResults = [];
    
    for (const tableName of tablesToTest) {
      try {
        console.log(`   Testing table: ${tableName}...`);
        const startTime = Date.now();
        
        const { data, error, count } = await supabase
          .from(tableName)
          .select('*', { count: 'exact', head: true });
        
        const responseTime = Date.now() - startTime;
        
        if (error) {
          console.log(`   ❌ Table '${tableName}' error: ${error.message}`);
          tableResults.push({ table: tableName, status: 'error', error: error.message, time: responseTime });
        } else {
          console.log(`   ✅ Table '${tableName}' accessible (${count || 0} rows, ${responseTime}ms)`);
          tableResults.push({ table: tableName, status: 'success', count: count || 0, time: responseTime });
          successCount++;
        }
      } catch (err) {
        console.log(`   ❌ Table '${tableName}' exception: ${err.message}`);
        tableResults.push({ table: tableName, status: 'exception', error: err.message });
      }
    }

    // Test a sample query that your dashboard uses
    console.log('\n4. Testing dashboard analytics query...');
    try {
      const testUserId = 'test-user-id'; // This will likely fail, but we can see how it fails
      const startTime = Date.now();
      
      const { data, error } = await supabase
        .from('ad_analyses')
        .select('overall_score, created_at')
        .eq('user_id', testUserId)
        .limit(5);
      
      const responseTime = Date.now() - startTime;
      
      if (error) {
        if (error.code === 'PGRST116') {
          console.log(`   ✅ Dashboard query structure works (no data for test user, ${responseTime}ms)`);
        } else {
          console.log(`   ⚠️ Dashboard query error: ${error.message} (${responseTime}ms)`);
        }
      } else {
        console.log(`   ✅ Dashboard query successful (${data?.length || 0} rows, ${responseTime}ms)`);
      }
    } catch (err) {
      console.log(`   ❌ Dashboard query exception: ${err.message}`);
    }

    // Summary
    console.log('\n📊 Test Results Summary:');
    console.log(`   • Tables tested: ${tablesToTest.length}`);
    console.log(`   • Tables accessible: ${successCount}`);
    console.log(`   • Success rate: ${Math.round((successCount / tablesToTest.length) * 100)}%`);
    
    if (successCount === tablesToTest.length) {
      console.log('\n🎉 All core tables are accessible!');
      console.log('\n📋 Your dashboard should work now. Try:');
      console.log('   • Restart your development server: bun run start');
      console.log('   • Clear browser cache and refresh');
      console.log('   • Check browser network tab for any remaining errors');
      return true;
    } else {
      console.log('\n⚠️ Some tables are missing or inaccessible.');
      console.log('\n📋 Next steps:');
      console.log('   • Check your Supabase dashboard for missing tables');
      console.log('   • Verify Row Level Security (RLS) policies');
      console.log('   • Make sure database migrations have been run');
      
      // Show detailed results
      console.log('\n📊 Detailed Results:');
      tableResults.forEach(result => {
        const icon = result.status === 'success' ? '✅' : '❌';
        console.log(`   ${icon} ${result.table}: ${result.status}${result.count !== undefined ? ` (${result.count} rows)` : ''}${result.error ? ` - ${result.error}` : ''}`);
      });
      
      return false;
    }

  } catch (error) {
    console.log('💥 Critical error during connection test:', error.message);
    return false;
  }
}

// Run the test
testAdCopySurgeDB().then((success) => {
  if (success) {
    console.log('\n🚀 Ready to test your dashboard!');
  } else {
    console.log('\n🔧 Database setup needed before dashboard will work properly.');
  }
  process.exit(success ? 0 : 1);
}).catch((error) => {
  console.error('💥 Unhandled error:', error.message);
  process.exit(1);
});
