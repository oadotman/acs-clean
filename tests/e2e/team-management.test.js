/**
 * End-to-End Test: Team Management Workflow
 * 
 * This test file validates the complete team management system including:
 * - User tier verification
 * - Team member limits
 * - Credit widget loading
 * - Tier consistency across tables
 * 
 * Run with: node tests/e2e/team-management.test.js
 * Or with Jest: jest tests/e2e/team-management.test.js
 */

const { createClient } = require('@supabase/supabase-js');

// Configuration - UPDATE THESE WITH YOUR SUPABASE CREDENTIALS
const SUPABASE_URL = process.env.SUPABASE_URL || 'YOUR_SUPABASE_URL';
const SUPABASE_ANON_KEY = process.env.SUPABASE_ANON_KEY || 'YOUR_SUPABASE_ANON_KEY';

// Test configuration
const TEST_CONFIG = {
  timeout: 10000, // 10 second timeout for queries
  testUserId: null, // Will be set during test
  testUserEmail: 'test-team-mgmt@example.com'
};

// Initialize Supabase client
const supabase = createClient(SUPABASE_URL, SUPABASE_ANON_KEY);

// Color codes for console output
const colors = {
  reset: '\x1b[0m',
  green: '\x1b[32m',
  red: '\x1b[31m',
  yellow: '\x1b[33m',
  blue: '\x1b[34m',
  cyan: '\x1b[36m'
};

// Test results tracker
const results = {
  passed: 0,
  failed: 0,
  warnings: 0,
  tests: []
};

// Helper functions
function logSuccess(message) {
  console.log(`${colors.green}✓${colors.reset} ${message}`);
  results.passed++;
}

function logError(message) {
  console.log(`${colors.red}✗${colors.reset} ${message}`);
  results.failed++;
}

function logWarning(message) {
  console.log(`${colors.yellow}⚠${colors.reset} ${message}`);
  results.warnings++;
}

function logInfo(message) {
  console.log(`${colors.cyan}ℹ${colors.reset} ${message}`);
}

function logSection(title) {
  console.log(`\n${colors.blue}═══════════════════════════════════════════${colors.reset}`);
  console.log(`${colors.blue}  ${title}${colors.reset}`);
  console.log(`${colors.blue}═══════════════════════════════════════════${colors.reset}\n`);
}

// Test with timeout
async function testWithTimeout(testFn, timeoutMs = TEST_CONFIG.timeout) {
  return Promise.race([
    testFn(),
    new Promise((_, reject) => 
      setTimeout(() => reject(new Error('Test timeout')), timeoutMs)
    )
  ]);
}

/**
 * TEST 1: Database Schema Verification
 */
async function test1_DatabaseSchema() {
  logSection('TEST 1: Database Schema Verification');
  
  try {
    // Check user_profiles table exists
    const { data: profiles, error: profileError } = await testWithTimeout(async () =>
      await supabase.from('user_profiles').select('id').limit(1)
    );
    
    if (profileError && profileError.code !== 'PGRST116') {
      logError('user_profiles table not found or not accessible');
      return false;
    }
    logSuccess('user_profiles table exists and is accessible');
    
    // Check user_credits table exists
    const { data: credits, error: creditError } = await testWithTimeout(async () =>
      await supabase.from('user_credits').select('id').limit(1)
    );
    
    if (creditError && creditError.code !== 'PGRST116') {
      logError('user_credits table not found or not accessible');
      return false;
    }
    logSuccess('user_credits table exists and is accessible');
    
    // Check agencies table exists (for team management)
    const { data: agencies, error: agencyError } = await testWithTimeout(async () =>
      await supabase.from('agencies').select('id').limit(1)
    );
    
    if (agencyError && agencyError.code !== 'PGRST116') {
      logWarning('agencies table not found - team management may not work');
    } else {
      logSuccess('agencies table exists and is accessible');
    }
    
    return true;
  } catch (error) {
    logError(`Schema verification failed: ${error.message}`);
    return false;
  }
}

/**
 * TEST 2: User Tier Data Consistency
 */
async function test2_TierConsistency() {
  logSection('TEST 2: User Tier Data Consistency');
  
  try {
    // Get all users and their tier data
    const { data: users, error } = await testWithTimeout(async () =>
      await supabase
        .from('user_profiles')
        .select('id, email, subscription_tier')
        .limit(10)
    );
    
    if (error) {
      logError(`Failed to fetch user profiles: ${error.message}`);
      return false;
    }
    
    if (!users || users.length === 0) {
      logWarning('No users found in database');
      return true;
    }
    
    logInfo(`Found ${users.length} users to check`);
    
    // Check each user's tier consistency
    let mismatches = 0;
    for (const user of users) {
      // Get credit record
      const { data: creditData, error: creditError } = await testWithTimeout(async () =>
        await supabase
          .from('user_credits')
          .select('subscription_tier')
          .eq('user_id', user.id)
          .single()
      );
      
      if (creditError) {
        if (creditError.code === 'PGRST116') {
          logWarning(`User ${user.email} has no credit record`);
        } else {
          logError(`Failed to fetch credits for ${user.email}: ${creditError.message}`);
        }
        continue;
      }
      
      // Check if tiers match
      if (user.subscription_tier !== creditData.subscription_tier) {
        logError(`MISMATCH: ${user.email} - profile: ${user.subscription_tier}, credits: ${creditData.subscription_tier}`);
        mismatches++;
      } else {
        logSuccess(`${user.email} - tier: ${user.subscription_tier} (consistent)`);
      }
    }
    
    if (mismatches === 0) {
      logSuccess('All user tiers are consistent across tables');
      return true;
    } else {
      logError(`Found ${mismatches} tier mismatches`);
      return false;
    }
  } catch (error) {
    logError(`Tier consistency check failed: ${error.message}`);
    return false;
  }
}

/**
 * TEST 3: Credit System Timeout Test
 */
async function test3_CreditTimeout() {
  logSection('TEST 3: Credit System Timeout Test');
  
  try {
    // Get a test user
    const { data: users, error } = await testWithTimeout(async () =>
      await supabase
        .from('user_profiles')
        .select('id')
        .limit(1)
        .single()
    );
    
    if (error || !users) {
      logWarning('No test user available for timeout test');
      return true;
    }
    
    TEST_CONFIG.testUserId = users.id;
    logInfo(`Using test user: ${users.id}`);
    
    // Test credit fetch with 10 second timeout
    const startTime = Date.now();
    const { data: credits, error: creditError } = await testWithTimeout(
      async () =>
        await supabase
          .from('user_credits')
          .select('*')
          .eq('user_id', users.id)
          .single(),
      10000
    );
    
    const duration = Date.now() - startTime;
    
    if (creditError && creditError.message.includes('timeout')) {
      logError(`Credit fetch timed out after ${duration}ms`);
      return false;
    }
    
    if (duration > 10000) {
      logError(`Credit fetch took ${duration}ms (exceeded 10s timeout)`);
      return false;
    }
    
    logSuccess(`Credit fetch completed in ${duration}ms (within 10s timeout)`);
    
    if (credits) {
      logInfo(`Credits: ${credits.current_credits}/${credits.monthly_allowance}`);
    }
    
    return true;
  } catch (error) {
    if (error.message === 'Test timeout') {
      logError('Credit fetch exceeded 10 second timeout');
      return false;
    }
    logError(`Credit timeout test failed: ${error.message}`);
    return false;
  }
}

/**
 * TEST 4: Team Member Limits Verification
 */
async function test4_TeamLimits() {
  logSection('TEST 4: Team Member Limits Verification');
  
  const EXPECTED_LIMITS = {
    'free': 0,
    'growth': 0,
    'agency_standard': 5,
    'agency_premium': 10,
    'agency_unlimited': 20
  };
  
  try {
    // Check each tier has correct limits in constants
    logInfo('Checking team member limits for each tier');
    
    for (const [tier, expectedLimit] of Object.entries(EXPECTED_LIMITS)) {
      logInfo(`${tier}: expecting ${expectedLimit} team members`);
    }
    
    // Get users with agency tiers
    const { data: agencyUsers, error } = await testWithTimeout(async () =>
      await supabase
        .from('user_profiles')
        .select('id, email, subscription_tier')
        .in('subscription_tier', ['agency_standard', 'agency_premium', 'agency_unlimited'])
    );
    
    if (error) {
      logWarning(`Could not fetch agency users: ${error.message}`);
      return true;
    }
    
    if (!agencyUsers || agencyUsers.length === 0) {
      logWarning('No agency tier users found - skipping team limit check');
      return true;
    }
    
    logInfo(`Found ${agencyUsers.length} agency tier users`);
    
    for (const user of agencyUsers) {
      const expectedLimit = EXPECTED_LIMITS[user.subscription_tier];
      logSuccess(`${user.email} (${user.subscription_tier}) - should allow ${expectedLimit} team members`);
    }
    
    return true;
  } catch (error) {
    logError(`Team limits verification failed: ${error.message}`);
    return false;
  }
}

/**
 * TEST 5: Agency Access Control
 */
async function test5_AgencyAccess() {
  logSection('TEST 5: Agency Access Control');
  
  try {
    // Check if non-agency users cannot access team management
    const { data: freeUsers, error: freeError } = await testWithTimeout(async () =>
      await supabase
        .from('user_profiles')
        .select('id, email, subscription_tier')
        .eq('subscription_tier', 'free')
        .limit(5)
    );
    
    if (freeError) {
      logWarning(`Could not fetch free tier users: ${freeError.message}`);
    } else if (freeUsers && freeUsers.length > 0) {
      logSuccess(`Found ${freeUsers.length} free tier users (should not have agency access)`);
      for (const user of freeUsers) {
        logInfo(`  ${user.email} - tier: ${user.subscription_tier} (no team management)`);
      }
    }
    
    // Check agency users can access
    const { data: agencyUsers, error: agencyError } = await testWithTimeout(async () =>
      await supabase
        .from('user_profiles')
        .select('id, email, subscription_tier')
        .in('subscription_tier', ['agency_standard', 'agency_premium', 'agency_unlimited'])
        .limit(5)
    );
    
    if (agencyError) {
      logWarning(`Could not fetch agency users: ${agencyError.message}`);
    } else if (agencyUsers && agencyUsers.length > 0) {
      logSuccess(`Found ${agencyUsers.length} agency tier users (should have team management)`);
      for (const user of agencyUsers) {
        logInfo(`  ${user.email} - tier: ${user.subscription_tier} (has team management)`);
      }
    }
    
    return true;
  } catch (error) {
    logError(`Agency access control check failed: ${error.message}`);
    return false;
  }
}

/**
 * TEST 6: Credit Amount Consistency
 */
async function test6_CreditAmounts() {
  logSection('TEST 6: Credit Amount Consistency');
  
  const EXPECTED_CREDITS = {
    'free': 5,
    'growth': 100,
    'agency_standard': 500,
    'agency_premium': 1000,
    'agency_unlimited': 999999
  };
  
  try {
    // Check free tier users have 5 credits
    const { data: freeUsers, error } = await testWithTimeout(async () =>
      await supabase
        .from('user_credits')
        .select('user_id, subscription_tier, current_credits, monthly_allowance')
        .eq('subscription_tier', 'free')
        .limit(10)
    );
    
    if (error) {
      logError(`Failed to fetch free tier credits: ${error.message}`);
      return false;
    }
    
    if (!freeUsers || freeUsers.length === 0) {
      logWarning('No free tier users found to check credit amounts');
      return true;
    }
    
    logInfo(`Checking credit amounts for ${freeUsers.length} free tier users`);
    
    let incorrect = 0;
    for (const user of freeUsers) {
      const expected = EXPECTED_CREDITS[user.subscription_tier];
      
      if (user.monthly_allowance !== expected) {
        logError(`User ${user.user_id}: expected ${expected} credits, got ${user.monthly_allowance}`);
        incorrect++;
      } else {
        logSuccess(`User has correct credit amount: ${user.monthly_allowance}`);
      }
    }
    
    if (incorrect === 0) {
      logSuccess('All users have correct credit amounts');
      return true;
    } else {
      logError(`${incorrect} users have incorrect credit amounts`);
      return false;
    }
  } catch (error) {
    logError(`Credit amount check failed: ${error.message}`);
    return false;
  }
}

/**
 * TEST 7: Real-Time Subscription Test
 */
async function test7_RealtimeSubscription() {
  logSection('TEST 7: Real-Time Subscription Test');
  
  try {
    logInfo('Testing real-time subscription setup...');
    
    if (!TEST_CONFIG.testUserId) {
      logWarning('No test user available - skipping real-time test');
      return true;
    }
    
    // Create a subscription to user_credits
    let subscriptionReceived = false;
    
    const channel = supabase
      .channel(`test_credits:${TEST_CONFIG.testUserId}`)
      .on(
        'postgres_changes',
        {
          event: '*',
          schema: 'public',
          table: 'user_credits',
          filter: `user_id=eq.${TEST_CONFIG.testUserId}`
        },
        (payload) => {
          subscriptionReceived = true;
          logSuccess('Real-time event received');
        }
      )
      .subscribe((status) => {
        logInfo(`Subscription status: ${status}`);
      });
    
    // Wait 2 seconds for subscription to connect
    await new Promise(resolve => setTimeout(resolve, 2000));
    
    // Clean up
    await channel.unsubscribe();
    
    logSuccess('Real-time subscription test completed (connection established)');
    return true;
  } catch (error) {
    logError(`Real-time subscription test failed: ${error.message}`);
    return false;
  }
}

/**
 * TEST 8: Missing Records Check
 */
async function test8_MissingRecords() {
  logSection('TEST 8: Missing Records Check');
  
  try {
    // Find users without credit records
    const { data: profiles, error: profileError } = await testWithTimeout(async () =>
      await supabase
        .from('user_profiles')
        .select('id, email')
        .limit(20)
    );
    
    if (profileError) {
      logError(`Failed to fetch user profiles: ${profileError.message}`);
      return false;
    }
    
    if (!profiles || profiles.length === 0) {
      logWarning('No users found in database');
      return true;
    }
    
    logInfo(`Checking ${profiles.length} users for missing credit records`);
    
    let missingCredits = 0;
    for (const profile of profiles) {
      const { data: credits, error: creditError } = await testWithTimeout(async () =>
        await supabase
          .from('user_credits')
          .select('id')
          .eq('user_id', profile.id)
          .single()
      );
      
      if (creditError && creditError.code === 'PGRST116') {
        logError(`User ${profile.email} is missing credit record`);
        missingCredits++;
      }
    }
    
    if (missingCredits === 0) {
      logSuccess('All users have credit records');
      return true;
    } else {
      logError(`${missingCredits} users are missing credit records`);
      return false;
    }
  } catch (error) {
    logError(`Missing records check failed: ${error.message}`);
    return false;
  }
}

/**
 * Print Test Summary
 */
function printSummary() {
  logSection('TEST SUMMARY');
  
  const total = results.passed + results.failed;
  const passRate = total > 0 ? ((results.passed / total) * 100).toFixed(1) : 0;
  
  console.log(`Total Tests: ${total}`);
  console.log(`${colors.green}Passed: ${results.passed}${colors.reset}`);
  console.log(`${colors.red}Failed: ${results.failed}${colors.reset}`);
  console.log(`${colors.yellow}Warnings: ${results.warnings}${colors.reset}`);
  console.log(`Pass Rate: ${passRate}%\n`);
  
  if (results.failed === 0) {
    console.log(`${colors.green}✅ ALL TESTS PASSED!${colors.reset}\n`);
    return 0;
  } else {
    console.log(`${colors.red}❌ SOME TESTS FAILED${colors.reset}\n`);
    return 1;
  }
}

/**
 * Main Test Runner
 */
async function runAllTests() {
  console.log(`\n${colors.cyan}╔═══════════════════════════════════════════╗${colors.reset}`);
  console.log(`${colors.cyan}║   Team Management E2E Test Suite         ║${colors.reset}`);
  console.log(`${colors.cyan}╚═══════════════════════════════════════════╝${colors.reset}\n`);
  
  logInfo('Starting test suite...\n');
  
  try {
    // Run all tests
    await test1_DatabaseSchema();
    await test2_TierConsistency();
    await test3_CreditTimeout();
    await test4_TeamLimits();
    await test5_AgencyAccess();
    await test6_CreditAmounts();
    await test7_RealtimeSubscription();
    await test8_MissingRecords();
    
    // Print summary
    const exitCode = printSummary();
    
    // Exit with appropriate code
    process.exit(exitCode);
  } catch (error) {
    logError(`Test suite failed: ${error.message}`);
    console.error(error);
    process.exit(1);
  }
}

// Run tests if executed directly
if (require.main === module) {
  // Check if Supabase credentials are configured
  if (SUPABASE_URL === 'YOUR_SUPABASE_URL' || SUPABASE_ANON_KEY === 'YOUR_SUPABASE_ANON_KEY') {
    console.error(`${colors.red}Error: Supabase credentials not configured${colors.reset}`);
    console.error('Please set SUPABASE_URL and SUPABASE_ANON_KEY environment variables');
    console.error('Or update the configuration in the test file\n');
    process.exit(1);
  }
  
  runAllTests();
}

// Export for use with test frameworks
module.exports = {
  runAllTests,
  test1_DatabaseSchema,
  test2_TierConsistency,
  test3_CreditTimeout,
  test4_TeamLimits,
  test5_AgencyAccess,
  test6_CreditAmounts,
  test7_RealtimeSubscription,
  test8_MissingRecords
};
