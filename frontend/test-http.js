const axios = require('axios');

// Your Supabase credentials
const SUPABASE_URL = 'https://zbsuldhdwtqmvgqwmjno.supabase.co';
const SUPABASE_ANON_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inpic3VsZGhkd3RxbXZncXdtam5vIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTY2NjM5OTUsImV4cCI6MjA3MjIzOTk5NX0.C84_GzoYs0abkW4CC5sB0eqQ4OxpIievtw54sT2HPZ4';

console.log('🔧 Testing Supabase HTTP API directly...\n');

async function testSupabaseHTTP() {
  try {
    // Test basic connectivity to the REST API
    console.log('1. Testing REST API endpoint...');
    
    const restUrl = `${SUPABASE_URL}/rest/v1/`;
    const config = {
      method: 'GET',
      url: restUrl,
      headers: {
        'apikey': SUPABASE_ANON_KEY,
        'Authorization': `Bearer ${SUPABASE_ANON_KEY}`,
        'Content-Type': 'application/json'
      },
      timeout: 10000 // 10 second timeout
    };
    
    const startTime = Date.now();
    const response = await axios(config);
    const responseTime = Date.now() - startTime;
    
    console.log(`✅ REST API responding (${responseTime}ms)`);
    console.log(`📊 Status: ${response.status} ${response.statusText}`);
    
    // Test specific table query
    console.log('\n2. Testing table query...');
    
    const tableUrl = `${SUPABASE_URL}/rest/v1/user_profiles`;
    const tableConfig = {
      ...config,
      url: tableUrl,
      params: {
        select: 'id',
        limit: 1
      }
    };
    
    const tableStart = Date.now();
    const tableResponse = await axios(tableConfig);
    const tableTime = Date.now() - tableStart;
    
    console.log(`✅ Table query successful (${tableTime}ms)`);
    console.log(`📊 Status: ${tableResponse.status}, Rows: ${tableResponse.data?.length || 0}`);
    
    // Test auth endpoint
    console.log('\n3. Testing auth endpoint...');
    
    const authUrl = `${SUPABASE_URL}/auth/v1/user`;
    const authConfig = {
      method: 'GET',
      url: authUrl,
      headers: {
        'apikey': SUPABASE_ANON_KEY,
        'Authorization': `Bearer ${SUPABASE_ANON_KEY}`
      },
      timeout: 5000,
      validateStatus: (status) => status < 500 // Accept 4xx errors as "working"
    };
    
    const authStart = Date.now();
    const authResponse = await axios(authConfig);
    const authTime = Date.now() - authStart;
    
    console.log(`✅ Auth endpoint responding (${authTime}ms)`);
    console.log(`📊 Status: ${authResponse.status} ${authResponse.statusText}`);
    
    console.log('\n🎉 All HTTP tests passed! Supabase API is accessible.');
    return true;
    
  } catch (error) {
    console.log('\n❌ HTTP test failed:');
    
    if (error.code === 'ENOTFOUND') {
      console.log('💥 DNS Resolution failed - cannot find Supabase server');
    } else if (error.code === 'ECONNREFUSED') {
      console.log('💥 Connection refused - server is not accepting connections');
    } else if (error.code === 'ETIMEDOUT') {
      console.log('💥 Connection timeout - server is too slow to respond');
    } else if (error.response) {
      console.log(`💥 HTTP Error: ${error.response.status} ${error.response.statusText}`);
      console.log(`📊 Response data:`, error.response.data);
    } else {
      console.log('💥 Unknown error:', error.message);
    }
    
    console.log('\n🔧 Troubleshooting suggestions:');
    console.log('   • Check your internet connection');
    console.log('   • Verify the Supabase project is not paused in the dashboard');
    console.log('   • Try accessing the Supabase dashboard directly in your browser');
    console.log('   • Check if a firewall or VPN is blocking the connection');
    
    return false;
  }
}

// Run the test
testSupabaseHTTP().then((success) => {
  if (success) {
    console.log('\n📋 Next steps:');
    console.log('   • The issue might be with the Supabase JS client specifically');
    console.log('   • Try updating @supabase/supabase-js to the latest version');
    console.log('   • Restart your development server');
  }
  process.exit(success ? 0 : 1);
}).catch((error) => {
  console.error('💥 Unhandled error:', error.message);
  process.exit(1);
});
