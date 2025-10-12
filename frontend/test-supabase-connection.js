// Test Supabase Connection and Create Test User
// Run this in your browser console to test

async function testSupabaseConnection() {
  const { supabase } = await import('./src/lib/supabaseClient');
  
  console.log('🔍 Testing Supabase connection...');
  
  // 1. Test basic connection
  try {
    const { data, error } = await supabase.from('projects').select('count').limit(1);
    if (error) {
      console.error('❌ Database connection failed:', error);
    } else {
      console.log('✅ Database connection successful');
    }
  } catch (e) {
    console.error('❌ Connection error:', e);
  }
  
  // 2. Check current auth status
  const { data: { session }, error: sessionError } = await supabase.auth.getSession();
  if (session) {
    console.log('✅ Current session found:', session.user.email);
    return session;
  } else {
    console.log('❌ No active session');
  }
  
  // 3. Try to create a test account
  const testEmail = 'test@adcopysurge.com';
  const testPassword = 'TestPassword123!';
  
  console.log('🔑 Attempting to create test account...');
  const { data: signUpData, error: signUpError } = await supabase.auth.signUp({
    email: testEmail,
    password: testPassword
  });
  
  if (signUpError) {
    console.log('⚠️ Sign up error (may already exist):', signUpError.message);
    
    // Try to sign in instead
    console.log('🔑 Attempting to sign in with test account...');
    const { data: signInData, error: signInError } = await supabase.auth.signInWithPassword({
      email: testEmail,
      password: testPassword
    });
    
    if (signInError) {
      console.error('❌ Sign in failed:', signInError);
      return null;
    } else {
      console.log('✅ Signed in successfully!');
      console.log('📧 Email:', testEmail);
      console.log('🔑 Password:', testPassword);
      return signInData.session;
    }
  } else {
    console.log('✅ Test account created!');
    console.log('📧 Email:', testEmail);
    console.log('🔑 Password:', testPassword);
    console.log('⚠️ Check your email for verification link if email confirmations are enabled');
    return signUpData.session;
  }
}

// Auto-run the test
testSupabaseConnection().then(session => {
  if (session) {
    console.log('🎉 Authentication successful! Refreshing page...');
    setTimeout(() => window.location.reload(), 2000);
  }
});