# 🧪 Testing Guide - Credit System Security Fixes

## Quick Start: Test User Setup

### Step 1: Get Supabase User UUID

1. Go to Supabase Dashboard → Authentication → Users
2. Find `adeliyio@yahoo.com`
3. Copy the UUID (looks like: `12345678-1234-1234-1234-123456789abc`)

### Step 2: Run SQL Script

```bash
# Connect to your database
psql -U postgres -d adcopysurge

# Or via Supabase SQL Editor

# Then run:
\i backend/scripts/setup_test_user.sql
```

**OR** manually run this SQL (replace UUID):

```sql
BEGIN;

-- Update user
INSERT INTO users (
    email,
    full_name,
    supabase_user_id,
    subscription_tier,
    subscription_active,
    is_active,
    email_verified
) VALUES (
    'adeliyio@yahoo.com',
    'Test User - Agency Standard',
    'YOUR-SUPABASE-UUID-HERE',  -- ⚠️ REPLACE
    'agency_standard',
    TRUE,
    TRUE,
    TRUE
)
ON CONFLICT (email)
DO UPDATE SET
    subscription_tier = 'agency_standard',
    subscription_active = TRUE,
    supabase_user_id = 'YOUR-SUPABASE-UUID-HERE';  -- ⚠️ REPLACE

-- Get user ID and set credits
DO $$
DECLARE
    v_user_id INTEGER;
BEGIN
    SELECT id INTO v_user_id FROM users WHERE email = 'adeliyio@yahoo.com';

    INSERT INTO user_credits (
        user_id,
        current_credits,
        monthly_allowance,
        bonus_credits,
        subscription_tier
    ) VALUES (
        v_user_id::TEXT,
        600,  -- 500 monthly + 100 bonus
        500,
        100,
        'agency_standard'
    )
    ON CONFLICT (user_id)
    DO UPDATE SET
        current_credits = 600,
        monthly_allowance = 500,
        bonus_credits = 100,
        subscription_tier = 'agency_standard';
END $$;

COMMIT;
```

### Step 3: Verify Setup

```sql
SELECT
    u.id,
    u.email,
    u.subscription_tier,
    uc.current_credits,
    uc.monthly_allowance
FROM users u
LEFT JOIN user_credits uc ON u.id::TEXT = uc.user_id
WHERE u.email = 'adeliyio@yahoo.com';
```

**Expected output:**
```
id  | email                  | subscription_tier   | current_credits | monthly_allowance
----|------------------------|---------------------|-----------------|------------------
123 | adeliyio@yahoo.com     | agency_standard     | 600             | 500
```

---

## Testing Credit Deduction

### Test 1: Normal Analysis (Should Succeed)

1. Login as `adeliyio@yahoo.com` in frontend
2. Start a new analysis
3. Watch backend logs:

```bash
sudo journalctl -u adcopysurge -f | grep -i credit
```

**Expected logs:**
```
✅ Credits deducted: 2 credits, remaining: 598
```

4. Verify in database:

```sql
SELECT current_credits FROM user_credits
WHERE user_id = (SELECT id::TEXT FROM users WHERE email = 'adeliyio@yahoo.com');
-- Should show: 598
```

### Test 2: Insufficient Credits (Should Fail)

1. Drain credits to 1:

```sql
UPDATE user_credits
SET current_credits = 1
WHERE user_id = (SELECT id::TEXT FROM users WHERE email = 'adeliyio@yahoo.com');
```

2. Try to start analysis (costs 2 credits)
3. **Expected:** Frontend shows "Insufficient credits" error
4. **Expected:** Backend returns 403 error
5. **Expected:** Credits remain at 1 (not deducted)

### Test 3: Race Condition Test

```bash
# Run concurrent tests
cd backend
pytest tests/test_credit_service_security.py::test_atomic_credit_deduction_prevents_race_condition -v
```

**Expected:** Only 2 out of 10 concurrent requests succeed

### Test 4: Credit Refund on Failure

1. Start analysis
2. Kill backend mid-analysis:

```bash
sudo systemctl stop adcopysurge
```

3. Restart:

```bash
sudo systemctl restart adcopysurge
```

4. Check logs for refund:

```bash
sudo journalctl -u adcopysurge | grep "Refunding credits"
```

5. Verify credits refunded:

```sql
SELECT
    operation,
    amount,
    description,
    created_at
FROM credit_transactions
WHERE user_id = (SELECT id::TEXT FROM users WHERE email = 'adeliyio@yahoo.com')
ORDER BY created_at DESC
LIMIT 5;
```

**Expected to see:**
```
REFUND_FULL_ANALYSIS | 2 | Analysis failed: ...
```

---

## API Testing with curl

### Get Credit Balance

```bash
# Get JWT token from browser (Developer Tools → Application → Local Storage)
JWT="your-jwt-token-here"

curl -X GET https://yourdomain.com/api/credits/balance \
  -H "Authorization: Bearer $JWT"
```

**Expected response:**
```json
{
  "credits": 600,
  "monthly_allowance": 500,
  "bonus_credits": 100,
  "total_used": 0,
  "subscription_tier": "agency_standard",
  "is_unlimited": false,
  "last_reset": "2025-01-20T00:00:00Z"
}
```

### Get Credit History

```bash
curl -X GET https://yourdomain.com/api/credits/history \
  -H "Authorization: Bearer $JWT"
```

### Try Analysis Without Auth (Should Fail)

```bash
curl -X POST https://yourdomain.com/api/ads/analyze \
  -H "Content-Type: application/json" \
  -d '{"ad":{"headline":"test","body_text":"test","cta":"test","platform":"facebook"}}'
```

**Expected:** 401 Unauthorized

---

## Monitoring Queries

### Check for Negative Balances (Should be 0)

```sql
SELECT user_id, current_credits
FROM user_credits
WHERE current_credits < 0;
```

### View Recent Credit Transactions

```sql
SELECT
    ct.user_id,
    u.email,
    ct.operation,
    ct.amount,
    ct.description,
    ct.created_at
FROM credit_transactions ct
JOIN users u ON u.id::TEXT = ct.user_id
ORDER BY ct.created_at DESC
LIMIT 20;
```

### Check Idempotency Key Buildup

```sql
SELECT
    COUNT(*) as total_keys,
    COUNT(*) FILTER (WHERE expires_at > NOW()) as active_keys,
    COUNT(*) FILTER (WHERE expires_at < NOW()) as expired_keys
FROM paddle_idempotency_keys;
```

**Expected:** Should be cleaned up daily

---

## Reset Test User Credits

```sql
UPDATE user_credits
SET current_credits = 600,
    total_used = 0
WHERE user_id = (SELECT id::TEXT FROM users WHERE email = 'adeliyio@yahoo.com');
```

---

## Common Issues

### Issue: "User not found"

**Solution:** Make sure you replaced the Supabase UUID in the SQL script

### Issue: Credits don't update in frontend

**Solution:**
1. Check browser console for errors
2. Verify JWT token is valid
3. Try logging out and back in
4. Check backend is running: `sudo systemctl status adcopysurge`

### Issue: Analysis fails with 500 error

**Solution:**
1. Check backend logs: `sudo journalctl -u adcopysurge -n 100`
2. Verify OpenAI API key is set
3. Check database connection

---

## Success Criteria

✅ **All tests pass if:**

1. Credits deduct correctly (600 → 598 after analysis)
2. Insufficient credits shows error (no deduction)
3. Concurrent requests properly rejected (race condition test passes)
4. Credits refunded on failure
5. Unauthenticated requests return 401
6. No negative credit balances
7. All transactions logged in `credit_transactions`

---

## Manual Refund (If Needed)

```sql
-- Check user's credit situation
SELECT * FROM user_credits
WHERE user_id = (SELECT id::TEXT FROM users WHERE email = 'adeliyio@yahoo.com');

-- Refund 2 credits manually
UPDATE user_credits
SET current_credits = current_credits + 2
WHERE user_id = (SELECT id::TEXT FROM users WHERE email = 'adeliyio@yahoo.com');

-- Log the manual refund
INSERT INTO credit_transactions (user_id, operation, amount, description)
VALUES (
    (SELECT id::TEXT FROM users WHERE email = 'adeliyio@yahoo.com'),
    'MANUAL_REFUND',
    2,
    'Manual refund for failed analysis'
);
```
