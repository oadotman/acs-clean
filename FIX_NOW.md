# 🔧 FIX NOW - Step by Step

## What Just Happened

You tried to create the test user, but got this error:
```
ERROR: Subscription tier "agency_standard" does not exist in database!
```

**This is GOOD!** ✅ The script is protecting you from creating a user with an invalid tier.

---

## ✅ Step 1: Check What You Have (Optional)

See what tier values are currently in your database:

### Via Supabase Dashboard:
```
Supabase → SQL Editor → Paste this → Run
```

```sql
SELECT enumlabel FROM pg_enum
WHERE enumtypid = 'subscriptiontier'::regtype
ORDER BY enumsortorder;
```

**You probably have:**
- free
- basic
- pro

**You need:**
- free
- growth
- agency_standard
- agency_premium
- agency_unlimited

---

## ✅ Step 2: Run the Migration (REQUIRED)

This adds the missing tier values to your database.

### Option A: Command Line (Recommended)

```bash
cd backend
alembic upgrade head
```

**Expected output:**
```
INFO  [alembic.runtime.migration] Running upgrade -> 20250120_tier_alignment
ALIGNING SUBSCRIPTION TIERS WITH PRICING PAGE
============================================
1. Checking current enum values...
   Current values: ['free', 'basic', 'pro']

2. Adding new tier values...
   Adding 'growth'...
   Adding 'agency_standard'...
   Adding 'agency_premium'...
   Adding 'agency_unlimited'...

3. Migrating legacy tier data...
   No 'basic' tier users to migrate ✓
   No 'pro' tier users to migrate ✓

MIGRATION COMPLETE
============================================
✓ Your database now matches your pricing page! 🎉
```

### Option B: Manually via SQL (If alembic fails)

Go to Supabase Dashboard → SQL Editor, paste and run:

```sql
-- Add growth
ALTER TYPE subscriptiontier ADD VALUE IF NOT EXISTS 'growth';

-- Add agency_standard
ALTER TYPE subscriptiontier ADD VALUE IF NOT EXISTS 'agency_standard';

-- Add agency_premium
ALTER TYPE subscriptiontier ADD VALUE IF NOT EXISTS 'agency_premium';

-- Add agency_unlimited
ALTER TYPE subscriptiontier ADD VALUE IF NOT EXISTS 'agency_unlimited';

-- Verify
SELECT enumlabel FROM pg_enum
WHERE enumtypid = 'subscriptiontier'::regtype
ORDER BY enumsortorder;
```

**Note:** PostgreSQL doesn't support `IF NOT EXISTS` for `ALTER TYPE ADD VALUE`, so you might need to run them one by one and ignore errors if they already exist.

Better version (run each separately):

```sql
-- Run these one at a time in Supabase SQL Editor:
ALTER TYPE subscriptiontier ADD VALUE 'growth';
ALTER TYPE subscriptiontier ADD VALUE 'agency_standard';
ALTER TYPE subscriptiontier ADD VALUE 'agency_premium';
ALTER TYPE subscriptiontier ADD VALUE 'agency_unlimited';
```

If you get "already exists" errors, that's fine - just means they're already there!

---

## ✅ Step 3: Verify Migration Worked

Run this to confirm:

```sql
SELECT enumlabel FROM pg_enum
WHERE enumtypid = 'subscriptiontier'::regtype
ORDER BY enumsortorder;
```

**You should now see:**
- free ✓
- basic (legacy)
- pro (legacy)
- growth ✓
- agency_standard ✓
- agency_premium ✓
- agency_unlimited ✓

---

## ✅ Step 4: Now Setup Test User

Now that the tiers exist, run the test user script again:

### Via Supabase Dashboard:
```
Supabase → SQL Editor → Paste entire contents of:
backend/scripts/setup_test_user_final.sql
→ Run
```

### Via Command Line:
```bash
psql -U postgres -d adcopysurge -f backend/scripts/setup_test_user_final.sql
```

**Expected output:**
```
============================================
Tier check passed: agency_standard exists ✓
============================================
User ID: 123
Tier: AGENCY STANDARD
Credits: 600 (500 monthly + 100 bonus)
Price: $99/month
============================================
```

---

## ✅ Step 5: Test It Works

```sql
-- Check user was created
SELECT
    email,
    subscription_tier,
    current_credits,
    monthly_allowance
FROM users u
JOIN user_credits uc ON u.id::TEXT = uc.user_id
WHERE email = 'adeliyio@yahoo.com';
```

**Expected:**
```
email              | subscription_tier | current_credits | monthly_allowance
-------------------|-------------------|-----------------|------------------
adeliyio@yahoo.com | agency_standard   | 600             | 500
```

---

## 🎯 Quick Command Summary

```bash
# If using alembic:
cd backend
alembic upgrade head

# Then:
psql -U postgres -d adcopysurge -f scripts/setup_test_user_final.sql
```

**OR via Supabase Dashboard:**
1. Run the ALTER TYPE commands (Step 2, Option B)
2. Run setup_test_user_final.sql

---

## 🚨 Troubleshooting

### Error: "alembic: command not found"

```bash
cd backend
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install alembic
alembic upgrade head
```

---

### Error: "Can't locate revision"

```bash
# Check migration files exist
ls backend/alembic/versions/20250120*

# Should see:
# 20250120_security_fixes_credit_system.py
# 20250120_align_subscription_tiers_with_pricing.py
```

If missing, they're in your repo. Make sure you're in the right directory.

---

### Error: "value already exists" when adding enum

**This is GOOD!** ✓ It means the value is already there. Just continue to the next one.

---

## 📋 Checklist

- [ ] Step 1: Check current tiers (optional)
- [ ] Step 2: Run migration (`alembic upgrade head`)
- [ ] Step 3: Verify 5 new tiers exist
- [ ] Step 4: Run test user setup script
- [ ] Step 5: Verify user created with 600 credits
- [ ] Step 6: Login and test analysis (600 → 598)

---

## ✅ Success Looks Like

```
Tier check passed: agency_standard exists ✓
User ID: 123
Credits: 600
```

Then when you test:
```
✅ Credits deducted: 2 credits, remaining: 598
```

**That's it!** 🎉
