# 🎯 TIER ALIGNMENT GUIDE - Fix Pricing Mismatch

## The Problem

Your database has **OLD** tier values (`basic`, `pro`) but your pricing page shows **NEW** tier values (`growth`, `agency_standard`, `agency_premium`, `agency_unlimited`).

This causes the error:
```
ERROR: invalid input value for enum subscriptiontier: "agency_standard"
```

## ✅ The Solution (3 Steps)

### Step 1: Run the Alignment Migration

This adds the new tier values and migrates existing users:

```bash
cd backend
alembic upgrade head
```

**What it does:**
- ✅ Adds `growth`, `agency_standard`, `agency_premium`, `agency_unlimited` to database
- ✅ Migrates `basic` → `growth`
- ✅ Migrates `pro` → `agency_unlimited`
- ✅ Keeps `basic`, `pro` for backward compatibility
- ✅ Updates user_credits table

**Expected output:**
```
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
   Migrating 0 users from 'basic' → 'growth'...
   Migrating 0 users from 'pro' → 'agency_unlimited'...

MIGRATION COMPLETE
✓ Your database now matches your pricing page! 🎉
```

---

### Step 2: Setup Test User

Now run the test user script:

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

### Step 3: Verify Alignment

```sql
-- Check all tiers exist
SELECT enumlabel FROM pg_enum
WHERE enumtypid = 'subscriptiontier'::regtype
ORDER BY enumsortorder;
```

**Expected:**
```
free
basic (legacy)
pro (legacy)
growth
agency_standard
agency_premium
agency_unlimited
```

---

## 📊 Your Pricing Page Structure

Here's what your pricing page shows (from `frontend/src/constants/plans.js`):

| Tier | Price | Credits/Month | Database Value |
|------|-------|---------------|----------------|
| Free | $0 | 5 | `free` |
| Growth | $39/mo | 100 | `growth` |
| Agency Standard | $99/mo | 500 | `agency_standard` |
| Agency Premium | $199/mo | 1000 | `agency_premium` |
| Agency Unlimited | $249/mo | Unlimited | `agency_unlimited` |

**Legacy (deprecated but kept for compatibility):**
| Old Value | Maps To | Notes |
|-----------|---------|-------|
| `basic` | `growth` | Automatically migrated |
| `pro` | `agency_unlimited` | Automatically migrated |

---

## 🎯 Test User Details

After migration + setup:

- **Email:** adeliyio@yahoo.com
- **UUID:** 5ee6a8be-6739-41d5-85d8-b735c61b31f0
- **Tier:** Agency Standard ($99/mo)
- **Credits:** 600 (500 monthly + 100 bonus)
- **Team Members:** 5
- **Reports:** 20/month
- **White Label:** ✅ Yes
- **API Access:** ❌ No (Premium+ only)

**This perfectly matches your pricing page!** ✅

---

## 🧪 Test Credit Deduction

1. **Login** as adeliyio@yahoo.com
2. **Start analysis**
3. **Watch credits:** 600 → 598 ✅

```bash
# Watch logs
sudo journalctl -u adcopysurge -f | grep -i credit
```

**Expected:**
```
✅ Credits deducted: 2 credits, remaining: 598
```

---

## 🔍 Verify Everything Matches

Run this query to see your current state:

```sql
-- Show tier alignment status
SELECT
    tier,
    EXISTS (
        SELECT 1 FROM pg_enum
        WHERE enumtypid = 'subscriptiontier'::regtype
        AND enumlabel = tier
    ) as exists_in_db,
    CASE
        WHEN tier = 'free' THEN '$0 - 5 analyses/mo'
        WHEN tier = 'growth' THEN '$39/mo - 100 analyses/mo'
        WHEN tier = 'agency_standard' THEN '$99/mo - 500 analyses/mo'
        WHEN tier = 'agency_premium' THEN '$199/mo - 1000 analyses/mo'
        WHEN tier = 'agency_unlimited' THEN '$249/mo - unlimited'
    END as pricing_page
FROM (
    VALUES
        ('free'),
        ('growth'),
        ('agency_standard'),
        ('agency_premium'),
        ('agency_unlimited')
) AS tiers(tier);
```

**All should show `exists_in_db = true`** ✅

---

## 🚨 Troubleshooting

### Issue: "Tier does not exist in database"

**Cause:** Migration not run yet

**Fix:**
```bash
cd backend
alembic upgrade head
```

---

### Issue: "No module named 'alembic'"

**Cause:** Not in virtual environment

**Fix:**
```bash
cd backend
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate     # Windows
pip install alembic
```

---

### Issue: "Can't locate revision"

**Cause:** Migration files not found

**Fix:**
```bash
# Verify migration files exist
ls backend/alembic/versions/20250120*

# Should see:
# 20250120_security_fixes_credit_system.py
# 20250120_align_subscription_tiers_with_pricing.py
```

---

## 📋 Complete Checklist

### Pre-Flight
- [ ] Backend virtual environment activated
- [ ] Database connection working
- [ ] Migration files in alembic/versions/

### Migration
- [ ] Run: `alembic upgrade head`
- [ ] See: "MIGRATION COMPLETE" message
- [ ] Verify: All 7 tier values exist

### Test User Setup
- [ ] Run: `setup_test_user_final.sql`
- [ ] See: "Tier check passed" message
- [ ] Verify: User has 600 credits

### Testing
- [ ] Login as adeliyio@yahoo.com
- [ ] Start analysis
- [ ] Credits: 600 → 598
- [ ] Logs show credit deduction
- [ ] Database confirms new balance

---

## 💡 Why This Matters

**Before fix:**
- Database: `basic`, `pro` (2 paid tiers)
- Pricing page: `growth`, `agency_standard`, `agency_premium`, `agency_unlimited` (4 paid tiers)
- ❌ **Mismatch!** Causes errors, confusion, lost revenue

**After fix:**
- Database: All 5 tiers + 2 legacy (7 total)
- Pricing page: 5 tiers
- ✅ **Perfect match!** Everything works correctly

---

## 🎯 Summary

**Problem:** Database enums don't match pricing page
**Solution:** Run 2 commands:
```bash
alembic upgrade head
psql < setup_test_user_final.sql
```

**Result:** Everything aligned, test user ready, payments working! 🎉

---

**Next:** Once working, follow `SECURITY_FIXES_DEPLOYMENT.md` for full deployment.
