# Simple Setup Steps - Test User Creation

## Your Situation

You tried to create the test user and got this error:
```
ERROR: Subscription tier "agency_standard" does not exist in database!
```

**This is expected!** Your database has old tier values, but your pricing page uses new ones.

## Solution: 2 Simple SQL Scripts

Run these in your **Supabase SQL Editor** (Dashboard → SQL Editor):

---

## Step 1: Add New Tier Values (1 minute)

1. **Open Supabase Dashboard** → **SQL Editor**
2. **Copy the entire contents** of this file:
   ```
   backend/scripts/add_new_subscription_tiers.sql
   ```
3. **Paste into SQL Editor**
4. **Click "Run"**

**Expected output:**
```
✓ Added tier: growth
✓ Added tier: agency_standard
✓ Added tier: agency_premium
✓ Added tier: agency_unlimited
✓ Your database now matches your pricing page!
```

---

## Step 2: Create Test User (30 seconds)

1. **Still in Supabase SQL Editor**
2. **Copy the entire contents** of this file:
   ```
   backend/scripts/setup_test_user_final.sql
   ```
3. **Paste into SQL Editor**
4. **Click "Run"**

**Expected output:**
```
Tier check passed: agency_standard exists ✓
User ID: [number]
Tier: AGENCY STANDARD
Credits: 600 (500 monthly + 100 bonus)
Price: $99/month
```

---

## Step 3: Test It Works

**Login to your app:**
- Email: `adeliyio@yahoo.com`
- UUID: `5ee6a8be-6739-41d5-85d8-b735c61b31f0`

**Run an analysis:**
- Credits should go: **600 → 598** ✅
- Check backend logs for: `"✅ Credits deducted: 2 credits, remaining: 598"`

---

## Quick Verification Query

After Step 1, you can verify all tiers exist:

```sql
SELECT enumlabel as tier
FROM pg_enum
WHERE enumtypid = 'subscriptiontier'::regtype
ORDER BY enumsortorder;
```

**You should see:**
- free ✓
- basic (legacy)
- pro (legacy)
- growth ✓
- agency_standard ✓
- agency_premium ✓
- agency_unlimited ✓

---

## Files You Need

✅ `backend/scripts/add_new_subscription_tiers.sql` (just created)
✅ `backend/scripts/setup_test_user_final.sql` (already exists)

Both files are ready to copy and paste into Supabase SQL Editor!

---

## Why This Works

**Before:**
- Database: `free, basic, pro` (3 tiers)
- Pricing page: `free, growth, agency_standard, agency_premium, agency_unlimited` (5 tiers)
- ❌ Mismatch!

**After:**
- Database: `free, growth, agency_standard, agency_premium, agency_unlimited` (+ legacy tiers for compatibility)
- Pricing page: `free, growth, agency_standard, agency_premium, agency_unlimited`
- ✅ Perfect alignment!

---

## Troubleshooting

**Error: "already exists"**
- That's OK! It means the tier value is already there. Continue to next step.

**Error: "relation 'users' does not exist"**
- Your database schema might not be fully initialized. Check if you've run initial migrations.

**Error: "permission denied"**
- Make sure you're using the Service Role key or Database password, not the Anon key.

---

## Summary

1. ✅ Copy `add_new_subscription_tiers.sql` → Paste in Supabase → Run
2. ✅ Copy `setup_test_user_final.sql` → Paste in Supabase → Run
3. ✅ Login as adeliyio@yahoo.com and test!

**That's it!** 🎉
