# 🎯 START HERE - Setup Test User in 2 Minutes

## The Error You Got

```
ERROR: invalid input value for enum subscriptiontier: "agency_standard"
```

**Translation:** Your database needs to be updated to support the new tier system.

---

## ✅ EASIEST FIX (Works Right Now!)

Run this script - it uses **Growth tier** (100 credits) which already exists in your database:

### Via Supabase Dashboard:
1. Go to Supabase → SQL Editor
2. Copy/paste the entire file: `backend/scripts/setup_adeliyio_growth_tier.sql`
3. Click "Run"
4. Done! ✅

### Via Command Line:
```bash
psql -U postgres -d adcopysurge -f backend/scripts/setup_adeliyio_growth_tier.sql
```

---

## ✅ What You Get

**Email:** adeliyio@yahoo.com
**UUID:** 5ee6a8be-6739-41d5-85d8-b735c61b31f0
**Tier:** Growth (100 credits/month + 20 bonus)
**Credits:** 120 total
**Analyses:** 60 (120 credits ÷ 2 per analysis)

**This is perfect for testing!** ✨

---

## 🧪 Test It

### 1. Verify Setup
```sql
SELECT email, subscription_tier, current_credits
FROM users u
JOIN user_credits uc ON u.id::TEXT = uc.user_id
WHERE email = 'adeliyio@yahoo.com';
```

**Expected:**
```
email              | subscription_tier | current_credits
-------------------|-------------------|----------------
adeliyio@yahoo.com | growth            | 120
```

### 2. Test Credit Deduction

1. **Login** to your app as adeliyio@yahoo.com
2. **Start analysis** (paste any ad copy)
3. **Watch credits:** 120 → 118 ✅

### 3. Check Backend Logs
```bash
sudo journalctl -u adcopysurge -f | grep -i credit
```

**Expected:**
```
✅ Credits deducted: 2 credits, remaining: 118
```

### 4. Verify in Database
```sql
SELECT current_credits FROM user_credits
WHERE user_id = (SELECT id::TEXT FROM users WHERE email = 'adeliyio@yahoo.com');
```

**Expected:** `118`

---

## 🎁 Need More Credits?

If you want **600 credits** (Agency tier) instead of 120:

### Step 1: Fix the enum
```bash
psql -U postgres -d adcopysurge -f backend/scripts/fix_subscription_tier_enum.sql
```

### Step 2: Setup agency tier
```bash
psql -U postgres -d adcopysurge -f backend/scripts/setup_adeliyio_test_user.sql
```

Now you'll have **600 credits** instead of 120! 🚀

---

## 📋 Reset Credits (For Re-Testing)

```sql
UPDATE user_credits
SET current_credits = 120, total_used = 0
WHERE user_id = (SELECT id::TEXT FROM users WHERE email = 'adeliyio@yahoo.com');
```

---

## 🚨 Still Having Issues?

### Issue: "User not found"
```sql
-- Check if user exists
SELECT * FROM users WHERE email = 'adeliyio@yahoo.com';
```

If empty, the user doesn't exist in Supabase Auth. Create the user first!

### Issue: Frontend shows 0 credits
1. Hard refresh: `Ctrl+Shift+R`
2. Logout and login again
3. Check browser console for errors

### Issue: Analysis fails
```bash
# Check backend logs
sudo journalctl -u adcopysurge -n 50

# Check if backend is running
sudo systemctl status adcopysurge
```

---

## 📚 Full Documentation

Once your test user is working:

1. **QUICK_START.md** - Detailed testing guide
2. **TESTING_GUIDE.md** - All test scenarios
3. **SECURITY_FIXES_DEPLOYMENT.md** - Deployment guide
4. **FIX_ENUM_ERROR.md** - Detailed enum fix guide

---

## ✅ Success Checklist

- [ ] Ran `setup_adeliyio_growth_tier.sql`
- [ ] User has 120 credits
- [ ] Can login as adeliyio@yahoo.com
- [ ] Analysis deducts 2 credits (120 → 118)
- [ ] Transaction logged in database

**All checked?** You're ready! 🎉

---

## 🎯 Quick Summary

**Problem:** Database missing new tier enum values
**Solution:** Use Growth tier script (works immediately!)
**Result:** 120 credits, ready to test
**Time:** 2 minutes

🚀 **Run the script and start testing!**
