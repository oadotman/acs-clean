# 🔧 Fix: Subscription Tier Enum Error

## The Problem

You got this error:
```
ERROR: invalid input value for enum subscriptiontier: "agency_standard"
```

This means your database's `subscriptiontier` enum doesn't have the new tier values yet.

---

## ✅ Solution (2 Options)

### Option 1: Use Growth Tier (Quick - Works Now!)

Just use this file instead - it uses 'growth' tier which exists in your database:

```bash
# Via Supabase SQL Editor
\i backend/scripts/setup_adeliyio_growth_tier.sql

# OR via psql
psql -U postgres -d adcopysurge -f backend/scripts/setup_adeliyio_growth_tier.sql
```

**Result:**
- **Tier:** Growth (100 credits/month + 20 bonus)
- **Credits:** 120 total
- **Can do:** 60 analyses (120 / 2 per analysis)

This is enough to test the credit system! ✅

---

### Option 2: Add Agency Tiers to Database (Better - More Credits!)

#### Step 1: Fix the enum

Run this SQL to add the missing enum values:

```bash
# Via Supabase SQL Editor
\i backend/scripts/fix_subscription_tier_enum.sql

# OR via psql
psql -U postgres -d adcopysurge -f backend/scripts/fix_subscription_tier_enum.sql
```

#### Step 2: Now setup agency tier

```bash
# This will now work!
psql -U postgres -d adcopysurge -f backend/scripts/setup_adeliyio_test_user.sql
```

**Result:**
- **Tier:** Agency Standard (500 credits/month + 100 bonus)
- **Credits:** 600 total
- **Can do:** 300 analyses

---

## 🎯 Recommended Approach

**For quick testing:** Use **Option 1** (Growth tier - 120 credits)
- Works immediately
- Enough to test credit deduction
- Can test multiple analyses

**For production:** Use **Option 2** (Fix enum + Agency tier)
- Adds proper tier support
- More realistic for testing agencies
- Required before production launch

---

## 📋 Quick Commands

### Check what enum values exist now:

```sql
SELECT enumlabel as tier FROM pg_enum
WHERE enumtypid = 'subscriptiontier'::regtype
ORDER BY enumsortorder;
```

**If you see:**
```
free
basic
pro
growth
```

→ Use **Option 1** (Growth tier script)

**If you see:**
```
free
basic
pro
growth
agency_standard
agency_premium
agency_unlimited
```

→ Use **Option 2** (Original agency tier script)

---

## ✅ Test After Setup

```sql
-- Verify user exists with credits
SELECT
    u.email,
    u.subscription_tier,
    uc.current_credits,
    uc.monthly_allowance
FROM users u
LEFT JOIN user_credits uc ON u.id::TEXT = uc.user_id
WHERE u.email = 'adeliyio@yahoo.com';
```

**Expected for Growth tier:**
```
email              | subscription_tier | current_credits | monthly_allowance
-------------------|-------------------|-----------------|------------------
adeliyio@yahoo.com | growth            | 120             | 100
```

**Expected for Agency tier:**
```
email              | subscription_tier   | current_credits | monthly_allowance
-------------------|---------------------|-----------------|------------------
adeliyio@yahoo.com | agency_standard     | 600             | 500
```

---

## 🧪 Test Credit Deduction

1. Login as adeliyio@yahoo.com
2. Start analysis
3. Credits decrease by 2

**Growth tier:** 120 → 118
**Agency tier:** 600 → 598

Both work the same way! ✅

---

## 🚀 Next Steps

1. **Now:** Run Option 1 (Growth tier) to test immediately
2. **Later:** Run Option 2 to add agency tiers for production
3. **Test:** Follow QUICK_START.md to test credit deduction

---

## 💡 Why This Happened

Your database was created before the new 5-tier pricing system was added. The migration that adds these enum values wasn't run yet.

**Fix:** Run the enum fix script, then you'll have all 7 values:
- free
- basic (legacy)
- pro (legacy)
- growth
- agency_standard (new!)
- agency_premium (new!)
- agency_unlimited (new!)
