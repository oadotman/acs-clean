# ⚠️ READ ME FIRST - Critical Alignment Issue

## What Happened

You got this error:
```
ERROR: invalid input value for enum subscriptiontier: "agency_standard"
```

## Why It Happened

Your database has **old** tier values, but your pricing page uses **new** tier values.

### Your Pricing Page Shows:
✅ Free ($0)
✅ Growth ($39/mo)
✅ Agency Standard ($99/mo)  ← **NOT in database yet!**
✅ Agency Premium ($199/mo)  ← **NOT in database yet!**
✅ Agency Unlimited ($249/mo)  ← **NOT in database yet!**

### Your Database Has:
- free
- basic (old)
- pro (old)

**This is a mismatch!** We need to align them.

---

## ✅ How to Fix (2 Commands)

### Command 1: Align Database with Pricing Page

```bash
cd backend
alembic upgrade head
```

**What this does:**
- Adds new tier values to database
- Migrates old users: `basic` → `growth`, `pro` → `agency_unlimited`
- Takes ~30 seconds

**Expected output:**
```
✓ Added: growth, agency_standard, agency_premium, agency_unlimited
✓ Your database now matches your pricing page! 🎉
```

---

### Command 2: Setup Test User

```bash
cd backend
psql -U postgres -d adcopysurge -f scripts/setup_test_user_final.sql
```

**OR via Supabase Dashboard:**
```
Supabase → SQL Editor → Paste contents of setup_test_user_final.sql → Run
```

**Expected output:**
```
Tier check passed: agency_standard exists ✓
User ID: 123
Tier: AGENCY STANDARD
Credits: 600 (500 monthly + 100 bonus)
```

---

## 🎯 Test User Details

| Field | Value |
|-------|-------|
| **Email** | adeliyio@yahoo.com |
| **UUID** | 5ee6a8be-6739-41d5-85d8-b735c61b31f0 |
| **Tier** | Agency Standard ($99/mo) |
| **Credits** | 600 (500 monthly + 100 bonus) |
| **Can Test** | 300 analyses (600 credits ÷ 2 per analysis) |

**This matches your $99/mo Agency Standard plan on the pricing page!** ✅

---

## 🧪 Test It Works

1. **Login** to your app as adeliyio@yahoo.com
2. **Start an analysis** (paste any ad copy)
3. **Watch credits:** 600 → 598 ✅

```bash
# Watch backend logs (optional)
sudo journalctl -u adcopysurge -f | grep -i credit
```

**You should see:**
```
✅ Credits deducted: 2 credits, remaining: 598
```

---

## 📋 Quick Checklist

- [ ] Run: `alembic upgrade head`
- [ ] See: "database now matches your pricing page"
- [ ] Run: `setup_test_user_final.sql`
- [ ] See: "Tier check passed: agency_standard exists"
- [ ] Login as adeliyio@yahoo.com
- [ ] Start analysis
- [ ] Credits: 600 → 598 ✅

---

## 🚨 If You Get Errors

### Error: "alembic: command not found"

**Fix:**
```bash
cd backend
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate  # Windows

pip install alembic
```

---

### Error: "Tier does not exist in database"

**Fix:** You skipped Command 1! Run it first:
```bash
alembic upgrade head
```

---

### Error: "psql: command not found"

**Fix:** Use Supabase Dashboard instead:
1. Go to Supabase → SQL Editor
2. Copy entire contents of `backend/scripts/setup_test_user_final.sql`
3. Paste and click "Run"

---

## 📚 Full Documentation

Once your test user works, read these for more details:

1. **TIER_ALIGNMENT_GUIDE.md** - Detailed alignment explanation
2. **SECURITY_FIXES_DEPLOYMENT.md** - Full security fixes
3. **TESTING_GUIDE.md** - Comprehensive testing
4. **QUICK_START.md** - 5-minute testing guide

---

## 💡 What's Different Now

### Before (Broken):
```
Database: free, basic, pro
Pricing:  free, growth, agency_standard, agency_premium, agency_unlimited
❌ Mismatch → Error!
```

### After (Fixed):
```
Database: free, growth, agency_standard, agency_premium, agency_unlimited
Pricing:  free, growth, agency_standard, agency_premium, agency_unlimited
✅ Perfect match → Works!
```

---

## 🎉 Once It Works

You'll have:
- ✅ Test user with 600 credits
- ✅ Database aligned with pricing page
- ✅ All security fixes working
- ✅ Ready to test payment system

---

## 🎯 Bottom Line

**Run these 2 commands:**

```bash
# 1. Align database (30 seconds)
cd backend && alembic upgrade head

# 2. Setup test user (10 seconds)
psql -U postgres -d adcopysurge -f scripts/setup_test_user_final.sql
```

**Then test:**
Login as adeliyio@yahoo.com → Start analysis → Watch 600 → 598 credits!

**That's it!** 🚀

---

**Status after following this guide:**
- Database: ✅ Aligned with pricing page
- Test User: ✅ 600 credits, Agency Standard tier
- Credit System: ✅ Secure, atomic, with refunds
- Ready to Test: ✅ YES!
