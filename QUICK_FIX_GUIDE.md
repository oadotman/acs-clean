# Quick Fix Guide - 5 Minute Summary

## What You Need to Do

Execute 2 SQL scripts in Supabase SQL Editor to fix critical bugs.

---

## Step 1: Fix Unlimited Credit Bug (5 min)

### What to Do:
1. Go to Supabase → SQL Editor
2. Open file: **`backend/scripts/fix_unlimited_credit_user.sql`**
3. Copy STEP 1 queries → Run → See what's wrong
4. Copy STEP 2 → Uncomment the right fix (Option A or B) → Run
5. Review results → Run `COMMIT;`

### Quick Check:
User `oadatascientist@gmail.com` should have:
- `is_unlimited = true`
- `current_credits = 999999`
- `subscription_tier = agency_unlimited`

---

## Step 2: Fix RLS Security (5 min)

### What to Do:
1. Still in Supabase SQL Editor
2. Open file: **`backend/scripts/fix_rls_security.sql`**
3. Copy STEP 1 → Run → See which tables need fixing
4. Copy STEP 2 → Run → Review → Run `COMMIT;`
5. Copy STEP 3 → Run → Should show `0` issues remaining

### Quick Check:
All 13 tables should show `rls_enabled = true`

---

## Test It Works

### Test 1: Credit Fix
- User logs in → Goes to New Analysis → Runs analysis
- ✓ Should work without "Not enough credits" error

### Test 2: RLS Fix
- Different users log in → Try accessing data
- ✓ Users see only their own/team data
- ✗ Users blocked from other agencies' data

---

## Files Created

Location: `backend/scripts/`

**Execute These:**
- `fix_unlimited_credit_user.sql` ← Run first
- `fix_rls_security.sql` ← Run second

**Read These:**
- `SUPABASE_FIX_INSTRUCTIONS.md` ← Detailed guide
- `ISSUE_ANALYSIS_SUMMARY.md` ← Full analysis

---

## If Something Goes Wrong

Both scripts include rollback commands:

```sql
-- Undo changes
ROLLBACK;
```

Just run `ROLLBACK;` instead of `COMMIT;` if results don't look right.

---

## Summary

| Issue | File | Time | Risk |
|-------|------|------|------|
| Credit Bug | fix_unlimited_credit_user.sql | 5 min | LOW |
| RLS Security | fix_rls_security.sql | 5 min | MEDIUM |

**Total:** ~10 minutes to fix both issues

**Next:** Execute the SQL scripts in Supabase!
