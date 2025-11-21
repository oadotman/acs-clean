# 🎯 SUPABASE SETUP STEPS - Copy/Paste SQL Scripts

## Your Situation

You need to run SQL scripts directly in Supabase SQL Editor (no alembic command line).

**This is the complete step-by-step guide.**

---

## ✅ Step 1: Fix User Registration Bug (CRITICAL - 2 minutes)

### Why This is Critical
**Without this fix, 100% of new user registrations will fail.**

Supabase creates users with `hashed_password=NULL`, but your database requires it to be NOT NULL. This causes a constraint violation.

### What to Do

1. **Open Supabase Dashboard** → **SQL Editor**
2. **Copy the entire contents** of this file:
   ```
   backend/scripts/fix_hashed_password_nullable.sql
   ```
3. **Paste into SQL Editor**
4. **Click "Run"**

### Expected Output

```
✅ SUCCESS! User registration will now work!

What this fixes:
  - Supabase users can register (OAuth, magic links)
  - No more constraint violation errors
  - 100% user registration success rate
```

### Verify It Worked

```sql
-- Run this to verify:
SELECT
    column_name,
    is_nullable,
    data_type
FROM information_schema.columns
WHERE table_name = 'users'
AND column_name = 'hashed_password';

-- Expected result:
-- column_name      | is_nullable | data_type
-- hashed_password  | YES         | character varying
```

**✅ Once you see "YES" for is_nullable, this fix is complete!**

---

## ✅ Step 2: Add New Subscription Tiers (5 minutes)

### Why This Matters

Your pricing page has 5 tiers (free, growth, agency_standard, agency_premium, agency_unlimited), but your database might only have the old tiers (free, basic, pro).

This script adds the missing tiers and migrates existing users.

### What to Do

1. **Still in Supabase SQL Editor**
2. **Copy the entire contents** of this file:
   ```
   backend/scripts/add_new_subscription_tiers.sql
   ```
3. **Paste into SQL Editor**
4. **Click "Run"**

### Expected Output

```
✓ Added tier: growth
✓ Added tier: agency_standard
✓ Added tier: agency_premium
✓ Added tier: agency_unlimited
→ Legacy tier "basic" does not exist (already migrated or never used)
→ Legacy tier "pro" does not exist (already migrated or never used)
✓ Your database now matches your pricing page!
```

### Verify It Worked

```sql
-- Check all tiers exist:
SELECT enumlabel as tier
FROM pg_enum
WHERE enumtypid = 'subscriptiontier'::regtype
ORDER BY enumsortorder;

-- Expected: You should see at least these 5:
-- free
-- growth
-- agency_standard
-- agency_premium
-- agency_unlimited
```

**✅ Once you see all 5 tiers, this step is complete!**

---

## ✅ Step 3: Create Test User (OPTIONAL - 2 minutes)

### Why You Might Want This

Creates a test user with Agency Standard tier (600 credits) so you can test credit deduction and refunds.

### What to Do

1. **Still in Supabase SQL Editor**
2. **Copy the entire contents** of this file:
   ```
   backend/scripts/setup_test_user_final.sql
   ```
3. **Paste into SQL Editor**
4. **Click "Run"**

### Expected Output

```
Tier check passed: agency_standard exists ✓
User ID: 123
Tier: AGENCY STANDARD
Credits: 600 (500 monthly + 100 bonus)
Price: $99/month
```

### Test User Details

- **Email:** adeliyio@yahoo.com
- **UUID:** 5ee6a8be-6739-41d5-85d8-b735c61b31f0
- **Tier:** Agency Standard ($99/mo)
- **Credits:** 600

### Verify It Worked

```sql
-- Check user exists:
SELECT
    id,
    email,
    subscription_tier,
    hashed_password
FROM users
WHERE email = 'adeliyio@yahoo.com';

-- Expected:
-- hashed_password should be NULL ✓
-- subscription_tier should be 'agency_standard' ✓
```

**✅ Once you see the user with NULL hashed_password, this step is complete!**

---

## 🎯 Quick Summary - 3 Scripts to Run

| # | Script | Purpose | Time | Required? |
|---|--------|---------|------|-----------|
| 1 | `fix_hashed_password_nullable.sql` | Fix user registration | 2 min | **CRITICAL** |
| 2 | `add_new_subscription_tiers.sql` | Add missing tiers | 5 min | **REQUIRED** |
| 3 | `setup_test_user_final.sql` | Create test account | 2 min | Optional |

**Total time: ~10 minutes**

---

## 🧪 Testing After Setup

### Test 1: User Registration (CRITICAL)

1. **Go to your app** (frontend)
2. **Sign up with a new email** (use Supabase auth - magic link or OAuth)
3. **Registration should succeed** ✅

If it fails, check:
```sql
-- Verify hashed_password is nullable:
SELECT is_nullable
FROM information_schema.columns
WHERE table_name = 'users'
AND column_name = 'hashed_password';

-- Should return: YES
```

### Test 2: Check Subscription Tiers

```sql
-- Verify all tiers exist:
SELECT enumlabel FROM pg_enum
WHERE enumtypid = 'subscriptiontier'::regtype
ORDER BY enumsortorder;

-- Should return at least:
-- free
-- growth
-- agency_standard
-- agency_premium
-- agency_unlimited
```

### Test 3: Test User Login (If you created test user)

1. **Login to your app** as `adeliyio@yahoo.com`
2. **Check credit balance** - Should show 600 credits
3. **Run an analysis** - Credits should deduct (600 → 598)
4. **Check backend logs** - Should show credit deduction

---

## 🚨 Troubleshooting

### Error: "column hashed_password does not exist"

**Solution:** Your users table might not have this column. Check your schema:

```sql
SELECT column_name, data_type, is_nullable
FROM information_schema.columns
WHERE table_name = 'users'
ORDER BY ordinal_position;
```

If `hashed_password` is missing entirely, your schema is different than expected.

---

### Error: "type subscriptiontier already has value basic"

**This is OK!** It means that tier already exists. The script will skip it and continue.

---

### Error: "relation users does not exist"

**Solution:** Your database schema is not initialized. You need to run initial migrations first.

Check if users table exists:
```sql
SELECT tablename FROM pg_tables
WHERE schemaname = 'public'
AND tablename = 'users';
```

If it returns nothing, your database needs the initial schema setup.

---

### Error: "Tier does not exist in database" (Step 3)

**Solution:** You need to run Step 2 first (add subscription tiers).

---

## ✅ Success Checklist

After running all scripts, verify:

- [ ] Script 1 completed: `hashed_password` is nullable (is_nullable = YES)
- [ ] Script 2 completed: All 5 tiers exist in database
- [ ] Script 3 completed (optional): Test user created with 600 credits
- [ ] User registration works: Create new account via app
- [ ] No constraint violation errors in logs
- [ ] Subscription tiers display correctly in app

**All checked? You're ready to move to the next phase!**

---

## 📁 File Locations

All SQL scripts are in:
```
backend/scripts/
├── fix_hashed_password_nullable.sql  ← Step 1 (CRITICAL)
├── add_new_subscription_tiers.sql    ← Step 2 (REQUIRED)
└── setup_test_user_final.sql         ← Step 3 (Optional)
```

---

## 🔄 What to Do After These Scripts

1. **Deploy code changes** to production (frontend + backend)
2. **Set file permissions** on VPS (see `DEPLOY_NOW.md`)
3. **Set up Sentry monitoring** (see `SENTRY_SETUP.md`)
4. **Set up SSL/HTTPS** (see `PRODUCTION_CHECKLIST.md`)
5. **Test complete user journey**
6. **Launch advertising!** 🚀

---

## 📚 Related Documentation

- **This file** - Supabase SQL Editor workflow
- `RUN_THIS_NOW.md` - Alternative guide (same content, different format)
- `DEPLOY_NOW.md` - Deployment quick start
- `PRODUCTION_CHECKLIST.md` - Complete validation checklist
- `SENTRY_SETUP.md` - Error monitoring setup
- `PRODUCTION_READINESS_SUMMARY.md` - Full audit report

---

## 💡 Pro Tip

**Save these scripts!** You might need them for:
- Setting up staging environment
- Disaster recovery
- New database instances
- Team member onboarding

Bookmark this file for quick reference! 📌

---

**Ready? Start with Step 1 - Fix User Registration Bug!** 🚀
