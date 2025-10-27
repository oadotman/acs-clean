# End-to-End Test Suite for Team Management

## Overview

This test suite validates the entire team management workflow including:
- Database schema integrity
- User tier consistency
- Credit system timeout handling
- Team member limits
- Agency access control
- Credit amount accuracy
- Real-time subscriptions
- Missing records detection

---

## Prerequisites

### 1. Install Dependencies

```powershell
# Install Supabase client
npm install @supabase/supabase-js

# Or if using yarn
yarn add @supabase/supabase-js
```

### 2. Get Supabase Credentials

You need two values from your Supabase project:
- **SUPABASE_URL**: Your project URL (e.g., https://xxxxx.supabase.co)
- **SUPABASE_ANON_KEY**: Your anonymous/public key

**Where to find them:**
1. Go to Supabase Dashboard
2. Click on your project
3. Go to Settings → API
4. Copy the "Project URL" and "anon/public" key

---

## Running the Tests

### Method 1: Using Environment Variables (Recommended)

```powershell
# PowerShell (Windows)
$env:SUPABASE_URL="https://your-project.supabase.co"
$env:SUPABASE_ANON_KEY="your-anon-key-here"
node tests/e2e/team-management.test.js
```

```bash
# Bash (Mac/Linux)
export SUPABASE_URL="https://your-project.supabase.co"
export SUPABASE_ANON_KEY="your-anon-key-here"
node tests/e2e/team-management.test.js
```

### Method 2: Edit the Test File

1. Open `tests/e2e/team-management.test.js`
2. Find lines 17-18:
```javascript
const SUPABASE_URL = process.env.SUPABASE_URL || 'YOUR_SUPABASE_URL';
const SUPABASE_ANON_KEY = process.env.SUPABASE_ANON_KEY || 'YOUR_SUPABASE_ANON_KEY';
```
3. Replace `YOUR_SUPABASE_URL` and `YOUR_SUPABASE_ANON_KEY` with your actual values
4. Run: `node tests/e2e/team-management.test.js`

---

## Test Descriptions

### TEST 1: Database Schema Verification
**What it checks:**
- ✅ user_profiles table exists and is accessible
- ✅ user_credits table exists and is accessible
- ✅ agencies table exists (for team management)

**Expected:** All tables should be accessible
**Failure indicates:** Database migration issues or RLS policy problems

---

### TEST 2: User Tier Data Consistency
**What it checks:**
- ✅ subscription_tier matches between user_profiles and user_credits
- ✅ All users have consistent tier data

**Expected:** 100% tier match between tables
**Failure indicates:** Data synchronization issues

---

### TEST 3: Credit System Timeout Test
**What it checks:**
- ✅ Credit queries complete within 10 seconds
- ✅ Timeout mechanism works correctly
- ✅ Credit data is fetched successfully

**Expected:** Query completes in < 10 seconds
**Failure indicates:** Slow database queries or network issues

---

### TEST 4: Team Member Limits Verification
**What it checks:**
- ✅ FREE tier: 0 team members
- ✅ GROWTH tier: 0 team members
- ✅ AGENCY_STANDARD: 5 team members
- ✅ AGENCY_PREMIUM: 10 team members
- ✅ AGENCY_UNLIMITED: 20 team members

**Expected:** Correct limits for each tier
**Failure indicates:** Configuration mismatch

---

### TEST 5: Agency Access Control
**What it checks:**
- ✅ FREE/GROWTH users don't have team management
- ✅ AGENCY tier users have team management access

**Expected:** Correct access control by tier
**Failure indicates:** Authorization issues

---

### TEST 6: Credit Amount Consistency
**What it checks:**
- ✅ FREE: 5 credits
- ✅ GROWTH: 100 credits
- ✅ AGENCY_STANDARD: 500 credits
- ✅ AGENCY_PREMIUM: 1000 credits
- ✅ AGENCY_UNLIMITED: 999999 credits

**Expected:** All users have correct credit amounts
**Failure indicates:** Database trigger misconfiguration

---

### TEST 7: Real-Time Subscription Test
**What it checks:**
- ✅ Supabase real-time connection works
- ✅ Credit updates can be subscribed to
- ✅ Channel subscription/unsubscription works

**Expected:** Successful connection and cleanup
**Failure indicates:** Real-time not enabled in Supabase

---

### TEST 8: Missing Records Check
**What it checks:**
- ✅ All users have corresponding credit records
- ✅ No orphaned user profiles

**Expected:** 0 users with missing records
**Failure indicates:** Database trigger not firing on signup

---

## Understanding Test Output

### Success Output:
```
═══════════════════════════════════════════
  TEST 1: Database Schema Verification
═══════════════════════════════════════════

✓ user_profiles table exists and is accessible
✓ user_credits table exists and is accessible
✓ agencies table exists and is accessible
```

### Failure Output:
```
═══════════════════════════════════════════
  TEST 2: User Tier Data Consistency
═══════════════════════════════════════════

ℹ Found 5 users to check
✓ user1@example.com - tier: free (consistent)
✗ MISMATCH: user2@example.com - profile: growth, credits: free
✓ user3@example.com - tier: agency_unlimited (consistent)
```

### Warning Output:
```
⚠ agencies table not found - team management may not work
```

---

## Test Summary

At the end, you'll see:

```
═══════════════════════════════════════════
  TEST SUMMARY
═══════════════════════════════════════════

Total Tests: 45
Passed: 43
Failed: 2
Warnings: 3
Pass Rate: 95.6%

❌ SOME TESTS FAILED
```

**Exit Codes:**
- `0` = All tests passed
- `1` = Some tests failed

---

## Troubleshooting

### Error: "Supabase credentials not configured"
**Solution:** Set environment variables or edit the test file with your credentials

### Error: "table not found or not accessible"
**Possible causes:**
- Table doesn't exist (run database migrations)
- RLS policy blocking access (check Supabase RLS settings)
- Wrong Supabase URL/key

**Solution:** 
- Verify tables exist in Supabase dashboard
- Check RLS policies allow reads with anon key
- Double-check your credentials

### Error: "Test timeout"
**Possible causes:**
- Slow database queries
- Network issues
- Supabase service issues

**Solution:**
- Check Supabase status
- Test network connection
- Try increasing timeout in TEST_CONFIG

### Warning: "No users found in database"
**This is normal if:**
- Fresh database with no users
- Testing in development environment

**Solution:** Create test users or ignore this warning

### Error: "MISMATCH: user tier inconsistent"
**This means:**
- user_profiles.subscription_tier ≠ user_credits.subscription_tier
- Data synchronization issue

**Solution:**
- Run database fix query to sync tiers
- Check database triggers are working
- See audit/EXECUTIVE_SUMMARY.md for fix recommendations

---

## What to Do If Tests Fail

### 1. Check Database Schema
Run the queries from `audit/01_database_schema_audit.sql` in Supabase SQL Editor

### 2. Review Error Messages
Each test provides specific error messages indicating what's wrong

### 3. Check Audit Documentation
See the `/audit` folder for detailed analysis:
- `EXECUTIVE_SUMMARY.md` - Overview and recommendations
- `02_auth_and_profile_flow_analysis.md` - Auth flow issues
- `03_credit_system_initialization_audit.md` - Credit initialization
- `04_credit_widget_loading_flow_analysis.md` - Loading issues

### 4. Fix Issues
Follow recommendations in audit documents to fix identified issues

### 5. Re-run Tests
After fixing, run tests again to verify fixes worked

---

## Running Individual Tests

You can also import and run specific tests:

```javascript
const { test2_TierConsistency } = require('./team-management.test.js');

// Run just tier consistency test
test2_TierConsistency().then(passed => {
  console.log(passed ? 'PASSED' : 'FAILED');
});
```

---

## Continuous Integration

To use in CI/CD pipelines:

```yaml
# GitHub Actions example
- name: Run Team Management Tests
  env:
    SUPABASE_URL: ${{ secrets.SUPABASE_URL }}
    SUPABASE_ANON_KEY: ${{ secrets.SUPABASE_ANON_KEY }}
  run: node tests/e2e/team-management.test.js
```

---

## Test Frequency Recommendations

**Development:**
- Run after any team management changes
- Run after database migrations
- Run before committing code

**Staging:**
- Run after every deployment
- Run daily as health check

**Production:**
- Run after deployment
- Run weekly as health check
- Run after Supabase maintenance

---

## Expected Results

On a healthy system, you should see:
- ✅ 40-50 passed tests
- ✅ 0-5 warnings (acceptable)
- ✅ 0 failed tests
- ✅ Pass rate: 100%

Warnings are OK if:
- No users exist yet (development)
- Optional features not enabled (agencies table)

---

## Support

If tests consistently fail, check:
1. Audit documentation in `/audit` folder
2. Implementation guide in `audit/IMPLEMENTATION_COMPLETE.md`
3. Database queries in `audit/01_database_schema_audit.sql`

---

**Test Suite Version:** 1.0.0  
**Last Updated:** October 27, 2025  
**Compatible with:** Supabase JS v2.x
