# 🚨 RUN THIS NOW - Fixed for Your Live Database

## What Happened

You ran the script and got an error about 'basic' tier not existing. **This means your database already has some of the new tier structure!**

I've fixed the scripts to work with your actual database state.

---

## ✅ Step 1: Check What You Have (30 seconds)

**Run this in Supabase SQL Editor:**

```sql
SELECT enumlabel as tier_value
FROM pg_enum
WHERE enumtypid = 'subscriptiontier'::regtype
ORDER BY enumsortorder;
```

**This shows your current tiers.** Make a note of what you see.

---

## ✅ Step 2: Add Missing Tiers (1 minute)

**Copy and paste this entire file into Supabase SQL Editor:**
```
backend/scripts/add_new_subscription_tiers.sql
```

**What it does:**
- Checks if each tier exists before adding it
- Only adds missing tiers (won't error on existing ones)
- Safely migrates any legacy data (only if old tiers exist)
- Shows you before/after comparison

**Expected output:**
```
→ Tier already exists: free
✓ Added tier: growth
✓ Added tier: agency_standard
✓ Added tier: agency_premium
✓ Added tier: agency_unlimited
→ Legacy tier "basic" does not exist (already migrated or never used)
→ Legacy tier "pro" does not exist (already migrated or never used)
✓ Your database now matches your pricing page!
```

---

## ✅ Step 3: Create Test User (30 seconds)

**Copy and paste this entire file into Supabase SQL Editor:**
```
backend/scripts/setup_test_user_final.sql
```

**Expected output:**
```
Tier check passed: agency_standard exists ✓
User ID: [number]
Tier: AGENCY STANDARD
Credits: 600 (500 monthly + 100 bonus)
Price: $99/month
```

---

## ✅ Step 4: Test It Works

**Login to your app:**
- Email: `adeliyio@yahoo.com`
- UUID: `5ee6a8be-6739-41d5-85d8-b735c61b31f0`

**Run an analysis:**
- Credits should go: **600 → 598** ✅

**Check backend logs:**
```bash
# If running locally
tail -f backend/logs/app.log | grep -i credit

# If on VPS
sudo journalctl -u adcopysurge -f | grep -i credit
```

**You should see:**
```
✅ Credits deducted: 2 credits, remaining: 598
```

---

## 🎯 What's Different Now

**The Fixed Script:**
- ✅ Checks if enum values exist BEFORE trying to query users with that tier
- ✅ Gracefully handles databases that never had 'basic'/'pro'
- ✅ Works on fresh databases, partially migrated databases, and fully migrated databases
- ✅ No more errors!

---

## Your Pricing Page Structure (5 Tiers)

| Tier | Price | Credits/Month | Enum Value |
|------|-------|---------------|------------|
| Free | $0 | 5 | `free` |
| Growth | $39/mo | 100 | `growth` |
| Agency Standard | $99/mo | 500 | `agency_standard` |
| Agency Premium | $199/mo | 1000 | `agency_premium` |
| Agency Unlimited | $249/mo | Unlimited | `agency_unlimited` |

**After Step 2, your database will have all 5 of these tiers.** ✅

---

## Troubleshooting

**Error: "already exists"**
- That's GOOD! It means the tier is already in your database. The script will skip it and continue.

**Error: "agency_standard does not exist" (in Step 3)**
- Step 2 didn't complete successfully. Re-run Step 2 and check for errors.

**Error: "permission denied"**
- Make sure you're using the correct database credentials in Supabase SQL Editor.

---

## Files Reference

| File | Purpose | When to Use |
|------|---------|-------------|
| `backend/scripts/check_what_tiers_exist.sql` | See current tiers | Before Step 2 (optional) |
| `backend/scripts/add_new_subscription_tiers.sql` | Add missing tiers | Step 2 (REQUIRED) |
| `backend/scripts/setup_test_user_final.sql` | Create test user | Step 3 (REQUIRED) |

---

## Bottom Line

1. **Check current tiers** (optional): Run `check_what_tiers_exist.sql`
2. **Add missing tiers** (required): Run `add_new_subscription_tiers.sql`
3. **Create test user** (required): Run `setup_test_user_final.sql`
4. **Test credits** (required): Login and run analysis

**You're 4 steps away from testing your payment system!** 🚀
