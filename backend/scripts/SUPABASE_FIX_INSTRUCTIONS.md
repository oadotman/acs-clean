# Supabase Fix Instructions

## Overview
Two SQL scripts have been created to fix critical issues in your Supabase database. Execute these scripts in the Supabase SQL Editor.

---

## Issue 1: Unlimited Plan Credit Bug

**File:** `fix_unlimited_credit_user.sql`

**Problem:**
- User Olutomiwa Adeliyi (oadatascientist@gmail.com) on UNLIMITED plan
- Gets "Not enough credits for analysis" error
- UI shows "CREDITS ∞" and "Resets in Unlimited Plan" but analysis blocked

**Root Cause (Likely):**
- `user_credits` table has incorrect values for this user
- Either `is_unlimited=false` when it should be `true`
- Or `subscription_tier` doesn't match the `users` table
- Or no credit record exists at all

### Execution Steps:

1. **Open Supabase SQL Editor:**
   - Go to https://supabase.com/dashboard
   - Select your project (tqzlsajhhtkhljdbjkyg)
   - Navigate to SQL Editor

2. **Run Diagnostics (STEP 1):**
   - Copy and paste STEP 1 queries from `fix_unlimited_credit_user.sql`
   - Execute to see current state
   - Review output to identify the specific issue

3. **Apply Fix (STEP 2):**
   - Based on diagnostic results, uncomment the appropriate fix:
     - **Option A:** If credit record EXISTS but has wrong values (most likely)
     - **Option B:** If credit record DOES NOT EXIST
   - Execute the BEGIN block
   - Review the "AFTER FIX" results
   - If correct, uncomment and run `COMMIT;`
   - If incorrect, uncomment and run `ROLLBACK;`

4. **Verify (STEP 3):**
   - Run verification query
   - Should show `is_unlimited = true` and `current_credits = 999999`

5. **Optional - Check Other Users (STEP 4 & 5):**
   - Run STEP 4 to see if other unlimited users have similar issues
   - If yes, run STEP 5 bulk fix to fix all unlimited users at once

### Expected Fix:
```sql
UPDATE user_credits
SET
    is_unlimited = true,
    current_credits = 999999,
    subscription_tier = 'agency_unlimited'  -- or whatever tier user has
WHERE user_id = '92f3f140-ddb5-4e21-a6d7-814982b55ebc';
```

---

## Issue 2: RLS Security Errors

**File:** `fix_rls_security.sql`

**Problem:**
- 13 tables have RLS policies defined but RLS is NOT enabled
- This means policies are being IGNORED - **CRITICAL SECURITY VULNERABILITY**
- All users can access all rows in these tables, bypassing access control

**Affected Tables:**
1. agency_invitations
2. agency_team_members
3. integrations
4. user_integrations
5. integration_logs
6. competitor_benchmarks
7. ad_generations
8. ad_analyses
9. projects
10. team_roles
11. team_members
12. team_invitations
13. project_team_access

### Execution Steps:

1. **Open Supabase SQL Editor** (same as above)

2. **Run Audit (STEP 1):**
   - Copy and paste STEP 1 queries
   - Execute to see which tables have the issue
   - Confirm the 13 tables listed above

3. **Enable RLS (STEP 2):**
   - Copy and paste the entire STEP 2 block
   - Execute the BEGIN block
   - Review verification results
   - **IMPORTANT:** Check that all 13 tables show `rls_now_enabled = true`
   - If correct, uncomment and run `COMMIT;`
   - If any issues, uncomment and run `ROLLBACK;`

4. **Final Verification (STEP 3):**
   - Run STEP 3 queries
   - Should show `tables_with_issues = 0`

5. **Optional - Function Fixes (STEP 4):**
   - These are WARNINGS, not critical errors
   - Can be fixed later if needed

### What This Does:
```sql
-- Enables RLS enforcement on all 13 tables
ALTER TABLE public.agency_invitations ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.agency_team_members ENABLE ROW LEVEL SECURITY;
-- ... etc for all 13 tables
```

### Safety Notes:
- **RLS policies already exist** for these tables (that's the problem!)
- Enabling RLS will **START ENFORCING** those policies
- Test your application after enabling to ensure policies work correctly
- If users lose access unexpectedly, you may need to review/update policies
- Rollback commands are included in the script if needed

---

## Testing After Fixes

### Test Issue 1 Fix:
1. Have user oadatascientist@gmail.com log out and log back in
2. Navigate to New Analysis page
3. Try to analyze ad copy
4. Should work without "Not enough credits" error
5. UI should still show "CREDITS ∞"

### Test Issue 2 Fix:
1. Log in as different user roles (owner, admin, member, viewer)
2. Try to access different features:
   - Team invitations
   - Ad analyses history
   - Project access
3. Ensure proper access control is working
4. Users should only see their own data (or team data if authorized)
5. Check for any "permission denied" errors in console

---

## Monitoring

After applying fixes, monitor for:
1. Credit-related errors in logs
2. RLS "permission denied" errors
3. Users reporting access issues
4. Check Supabase logs for any database errors

---

## Rollback (Emergency)

Both scripts include rollback commands if needed:

**Credit Fix Rollback:**
```sql
-- Revert to previous values (you'd need to note them first)
UPDATE user_credits SET ... WHERE user_id = '...';
```

**RLS Fix Rollback:**
```sql
-- Disable RLS again (NOT RECOMMENDED - leaves security vulnerability)
ALTER TABLE public.agency_invitations DISABLE ROW LEVEL SECURITY;
-- ... etc
```

---

## Summary

**Priority:** HIGH - Both issues are critical
**Estimated Time:** 10-15 minutes total
**Risk Level:**
- Issue 1: LOW (affects single user, easy to rollback)
- Issue 2: MEDIUM (security fix, test thoroughly)

**Order of Execution:**
1. Fix Issue 1 first (credit bug) - 5 minutes
2. Test user can now analyze
3. Fix Issue 2 (RLS) - 5 minutes
4. Test application access control - 5 minutes

---

## Questions or Issues?

If you encounter any errors while running these scripts:
1. Note the exact error message
2. Check which step failed
3. Run the ROLLBACK command
4. Share the error for troubleshooting

The scripts are designed to be safe with:
- Read-only diagnostic queries first
- Transaction-based changes (BEGIN/COMMIT/ROLLBACK)
- Verification queries after each change
- Detailed rollback commands
