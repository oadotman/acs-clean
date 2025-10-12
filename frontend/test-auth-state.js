// Quick test to check if localStorage has valid authentication data
console.log('🔍 Testing Authentication State...\n');

// Check if we're in browser environment
if (typeof localStorage !== 'undefined') {
  const authKey = 'adcopysurge-supabase-auth-token';
  const storedAuth = localStorage.getItem(authKey);
  
  if (storedAuth) {
    try {
      const parsed = JSON.parse(storedAuth);
      const expiresAt = new Date(parsed.expires_at * 1000);
      const now = new Date();
      const isExpired = expiresAt < now;
      
      console.log('✅ Found stored auth token');
      console.log('📧 User:', parsed.user?.email || 'Unknown');
      console.log('⏰ Expires:', expiresAt.toLocaleString());
      console.log('🔄 Status:', isExpired ? '❌ EXPIRED' : '✅ VALID');
      
      if (isExpired) {
        console.log('\n⚠️  Token is expired - user will need to log in again');
        console.log('💡 Consider clearing localStorage and refreshing');
      } else {
        console.log('\n🎉 Token is valid - authentication should work!');
        console.log('🔧 If dashboard is stuck loading, the issue is in the timeout handling');
      }
      
    } catch (e) {
      console.log('❌ Found auth token but could not parse it:', e.message);
    }
  } else {
    console.log('❌ No auth token found in localStorage');
    console.log('💡 User needs to log in');
  }
} else {
  console.log('❌ Not in browser environment - cannot check localStorage');
}

console.log('\n📋 Next steps:');
console.log('1. If token is valid: The auth context timeout fix should resolve loading issue');
console.log('2. If token is expired: Clear localStorage and log in again');
console.log('3. If no token: User needs to log in');
console.log('\n🔧 To clear localStorage: localStorage.clear(); location.reload();');
