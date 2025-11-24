# 🚀 Quick Start - Deploy & Test in 5 Minutes

## Test User: adeliyio@yahoo.com

**UUID:** `5ee6a8be-6739-41d5-85d8-b735c61b31f0`
**Tier:** Agency Standard (500 credits/month)
**Initial Balance:** 600 credits (500 + 100 bonus)

---

## 📋 1-Minute Setup

### Option A: Via Supabase Dashboard (Easiest)

1. Go to Supabase Dashboard → SQL Editor
2. Paste this script:

```sql
\i backend/scripts/setup_adeliyio_test_user.sql
```

3. Click "Run"
4. Done! ✅

### Option B: Via psql

```bash
psql -U postgres -d adcopysurge -f backend/scripts/setup_adeliyio_test_user.sql
```

### Option C: Copy-Paste SQL

Just run the file `backend/scripts/setup_adeliyio_test_user.sql` - it's ready to go with the UUID already filled in!

---

## ✅ Verify Setup

```sql
SELECT
    u.email,
    u.subscription_tier,
    uc.current_credits,
    uc.monthly_allowance
FROM users u
LEFT JOIN user_credits uc ON u.id::TEXT = uc.user_id
WHERE u.email = 'adeliyio@yahoo.com';
```

**Expected:**
```
email                  | subscription_tier | current_credits | monthly_allowance
-----------------------|-------------------|-----------------|------------------
adeliyio@yahoo.com     | agency_standard   | 600             | 500
```

---

## 🧪 Test Credit Deduction

### 1. Login to Frontend

- Email: `adeliyio@yahoo.com`
- Use the password from Supabase Auth

### 2. Start Analysis

1. Paste any ad copy
2. Click "Analyze"
3. Watch the magic! ✨

### 3. Watch Backend Logs

```bash
# Production
sudo journalctl -u adcopysurge -f | grep -i credit

# Development
# Just watch your terminal output
```

**Expected Output:**
```
🔍 Starting analysis for user 123: Test ad copy...
✅ Credits deducted: 2 credits, remaining: 598
✅ Analysis complete. Generated 4 alternatives
```

### 4. Verify in Database

```sql
-- Check credit balance
SELECT current_credits FROM user_credits
WHERE user_id = (SELECT id::TEXT FROM users WHERE email = 'adeliyio@yahoo.com');
-- Should show: 598 (was 600, minus 2 for FULL_ANALYSIS)

-- Check transaction log
SELECT operation, amount, description, created_at
FROM credit_transactions
WHERE user_id = (SELECT id::TEXT FROM users WHERE email = 'adeliyio@yahoo.com')
ORDER BY created_at DESC
LIMIT 5;
-- Should show: FULL_ANALYSIS | -2 | Used for FULL_ANALYSIS
```

---

## 🎯 Test Scenarios

### Scenario 1: Normal Analysis ✅

**Steps:**
1. Credits: 600
2. Start analysis
3. Credits: 598

**Expected:** ✅ Analysis completes, credits deducted

---

### Scenario 2: Insufficient Credits ❌

**Setup:**
```sql
UPDATE user_credits
SET current_credits = 1
WHERE user_id = (SELECT id::TEXT FROM users WHERE email = 'adeliyio@yahoo.com');
```

**Steps:**
1. Credits: 1
2. Try to start analysis (needs 2 credits)

**Expected:**
- ❌ Error: "Insufficient credits"
- Credits remain at 1 (not deducted)

---

### Scenario 3: Race Condition Test 🏁

**Run:**
```bash
cd backend
pytest tests/test_credit_service_security.py::test_atomic_credit_deduction_prevents_race_condition -v
```

**Expected:**
```
✅ test_atomic_credit_deduction_prevents_race_condition PASSED
✅ Race condition test passed: Atomic operations work correctly
```

---

### Scenario 4: Credit Refund on Failure 🔄

**Steps:**
1. Start analysis
2. Kill backend: `sudo systemctl stop adcopysurge`
3. Restart: `sudo systemctl restart adcopysurge`
4. Check logs: `sudo journalctl -u adcopysurge | tail -20`

**Expected:**
```
🔄 Refunding credits to user 123 due to analysis failure
✅ Credits refunded: 2 credits
```

---

## 🔧 Useful Commands

### Check Current Balance

```sql
SELECT current_credits FROM user_credits
WHERE user_id = (SELECT id::TEXT FROM users WHERE email = 'adeliyio@yahoo.com');
```

### Reset Credits to 600

```sql
UPDATE user_credits
SET current_credits = 600, total_used = 0
WHERE user_id = (SELECT id::TEXT FROM users WHERE email = 'adeliyio@yahoo.com');
```

### View Transaction History

```sql
SELECT
    operation,
    amount,
    description,
    created_at
FROM credit_transactions
WHERE user_id = (SELECT id::TEXT FROM users WHERE email = 'adeliyio@yahoo.com')
ORDER BY created_at DESC
LIMIT 10;
```

### Manual Refund (if needed)

```sql
-- Refund 2 credits
UPDATE user_credits
SET current_credits = current_credits + 2
WHERE user_id = (SELECT id::TEXT FROM users WHERE email = 'adeliyio@yahoo.com');

-- Log it
INSERT INTO credit_transactions (user_id, operation, amount, description)
VALUES (
    (SELECT id::TEXT FROM users WHERE email = 'adeliyio@yahoo.com'),
    'MANUAL_REFUND',
    2,
    'Manual refund - testing'
);
```

---

## 🚨 Common Issues

### Issue: "User not found"

**Cause:** User doesn't exist in Supabase Auth

**Fix:**
1. Go to Supabase Dashboard → Authentication → Users
2. Verify `adeliyio@yahoo.com` exists
3. Copy the UUID and verify it matches: `5ee6a8be-6739-41d5-85d8-b735c61b31f0`

---

### Issue: Credits don't update in frontend

**Fix:**
1. Hard refresh browser: `Ctrl+Shift+R` (Windows) or `Cmd+Shift+R` (Mac)
2. Check browser console for errors
3. Logout and login again
4. Verify backend is running: `sudo systemctl status adcopysurge`

---

### Issue: Analysis fails with 500 error

**Debug:**
```bash
# Check recent errors
sudo journalctl -u adcopysurge -n 50

# Check if OpenAI key is set
grep OPENAI_API_KEY backend/.env

# Check database connection
psql -U postgres -d adcopysurge -c "SELECT 1;"
```

---

## 📊 Success Checklist

After running the setup script, verify:

- [x] User exists in database
- [x] `subscription_tier = 'agency_standard'`
- [x] `current_credits = 600`
- [x] `monthly_allowance = 500`
- [x] Can login as adeliyio@yahoo.com
- [x] Can start analysis
- [x] Credits deduct (600 → 598)
- [x] Transaction logged in `credit_transactions`

---

## 🎉 You're Ready!

1. **Setup:** Run the SQL script ✅
2. **Verify:** Check credits = 600 ✅
3. **Test:** Login and analyze ✅
4. **Monitor:** Watch logs and DB ✅

**Need help?** Check:
- `TESTING_GUIDE.md` - Detailed testing instructions
- `SECURITY_FIXES_DEPLOYMENT.md` - Full deployment guide
- `IMPLEMENTATION_SUMMARY.md` - What was built and why

---

**Test User Status:** ✅ READY
**UUID:** `5ee6a8be-6739-41d5-85d8-b735c61b31f0`
**Credits:** 600
**Tier:** Agency Standard

🚀 **Go test your payment system!**
