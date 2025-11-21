# 🔒 Security Fixes Deployment Guide

## Overview

This document outlines the deployment process for critical security fixes to the AdCopySurge payment and credit system.

**Version:** 1.0.0 (Security Patch)
**Date:** January 20, 2025
**Severity:** CRITICAL - Deploy ASAP

---

## 🚨 What Was Fixed

### Critical Vulnerabilities (Priority 1)

1. **Race Condition in Credit Deduction** ✅ FIXED
   - **Before:** Multiple concurrent requests could bypass credit limits
   - **After:** Atomic PostgreSQL operations with WHERE clause constraints
   - **File:** `backend/app/services/credit_service.py`

2. **No Credit Refunds on Failure** ✅ FIXED
   - **Before:** Users lost credits if analysis failed
   - **After:** Automatic refund mechanism with audit logging
   - **File:** `backend/app/api/ads.py` (lines 213-230)

3. **Anonymous User Bypass** ✅ FIXED
   - **Before:** `/api/ads/analyze` allowed unauthenticated requests
   - **After:** Enforced `require_active_user` authentication
   - **File:** `backend/app/api/ads.py` (line 116)

4. **Paddle Webhook Signature Optional** ✅ FIXED
   - **Before:** Webhooks accepted without signature verification
   - **After:** Required HMAC verification, rejects unsigned webhooks
   - **File:** `backend/app/api/subscriptions.py` (lines 240-253)

5. **JWT Signature Verification Disabled** ✅ FIXED
   - **Before:** Tokens accepted without signature verification
   - **After:** Full JWT validation using Supabase JWT secret
   - **File:** `backend/app/middleware/supabase_auth.py` (lines 67-133)

### Important Improvements (Priority 2)

6. **Backend Credit Service** ✅ ADDED
   - Single source of truth for credit operations
   - Atomic operations prevent race conditions
   - Audit trail for all transactions

7. **Webhook → Credit Sync** ✅ FIXED
   - Subscription creation/updates now reset credits
   - Downgrades/cancellations properly handled

8. **Idempotency for Transactions** ✅ ADDED
   - Prevents duplicate charges from multiple clicks
   - 24-hour key expiration

9. **Monthly Credit Reset Cron** ✅ ADDED
   - Automated monthly credit allocation
   - Handles rollover for paid tiers

---

## 📋 Pre-Deployment Checklist

### Required Environment Variables

Add these to `backend/.env` for **PRODUCTION**:

```bash
# Required for JWT verification
SUPABASE_JWT_SECRET=your-supabase-jwt-secret

# Required for webhook security
PADDLE_WEBHOOK_SECRET=your-paddle-webhook-secret

# Environment flag (CRITICAL)
ENVIRONMENT=production
```

**How to get these:**
- **SUPABASE_JWT_SECRET:** Supabase Dashboard → Project Settings → API → JWT Secret
- **PADDLE_WEBHOOK_SECRET:** Paddle Dashboard → Developer Tools → Webhooks → Create Webhook → Copy Secret

### Database Backup

**BEFORE** running migrations:

```bash
# PostgreSQL backup
pg_dump -U postgres -d adcopysurge -F c -b -v -f backup_$(date +%Y%m%d_%H%M%S).dump

# Or via Supabase Dashboard
# Database → Backups → Create Manual Backup
```

---

## 🚀 Deployment Steps

### Step 1: Pull Latest Code

```bash
cd /opt/adcopysurge/backend
git fetch origin
git checkout main
git pull origin main
```

### Step 2: Install Dependencies

```bash
source venv/bin/activate
pip install -r requirements.txt
```

### Step 3: Run Database Migration

```bash
cd /opt/adcopysurge/backend

# Review migration first
cat alembic/versions/20250120_security_fixes_credit_system.py

# Run migration
alembic upgrade head

# Verify tables created
python -c "
from sqlalchemy import create_engine, inspect
from app.core.config import settings
engine = create_engine(settings.DATABASE_URL)
inspector = inspect(engine)
print('Tables:', inspector.get_table_names())
assert 'paddle_idempotency_keys' in inspector.get_table_names()
print('✅ Migration successful')
"
```

### Step 4: Update Environment Variables

```bash
# Edit production .env
nano /opt/adcopysurge/backend/.env

# Add required variables:
# SUPABASE_JWT_SECRET=...
# PADDLE_WEBHOOK_SECRET=...
# ENVIRONMENT=production
```

### Step 5: Restart Backend Service

```bash
# Restart Gunicorn/Uvicorn
sudo systemctl restart adcopysurge

# Check status
sudo systemctl status adcopysurge

# Tail logs for errors
sudo journalctl -u adcopysurge -f
```

### Step 6: Set Up Monthly Credit Reset Cron

```bash
# Make script executable
chmod +x /opt/adcopysurge/backend/run_credit_reset.py

# Add to crontab
crontab -e

# Add this line (runs 1st of each month at midnight):
0 0 1 * * cd /opt/adcopysurge/backend && /opt/adcopysurge/backend/venv/bin/python run_credit_reset.py >> /var/log/adcopysurge/credit_reset.log 2>&1

# Create log directory
sudo mkdir -p /var/log/adcopysurge
sudo chown www-data:www-data /var/log/adcopysurge
```

### Step 7: Update Paddle Webhook URL

1. Go to Paddle Dashboard → Developer Tools → Webhooks
2. Update webhook URL to: `https://yourdomain.com/api/subscriptions/paddle/webhook`
3. Ensure webhook secret matches `PADDLE_WEBHOOK_SECRET` in `.env`
4. Test webhook: Send test event and verify signature validation

---

## ✅ Post-Deployment Verification

### Test 1: Authentication Enforcement

```bash
# This should FAIL with 401 (no auth)
curl -X POST https://yourdomain.com/api/ads/analyze \
  -H "Content-Type: application/json" \
  -d '{"ad":{"headline":"test","body_text":"test","cta":"test","platform":"facebook"}}'

# Expected: {"detail":"Not authenticated"}
```

### Test 2: Race Condition Protection

Run the test suite:

```bash
cd /opt/adcopysurge/backend
pytest tests/test_credit_service_security.py::test_atomic_credit_deduction_prevents_race_condition -v
```

Expected: Test passes with 2 successful deductions out of 10 concurrent attempts.

### Test 3: Webhook Signature Verification

```bash
# Send unsigned webhook (should FAIL)
curl -X POST https://yourdomain.com/api/subscriptions/paddle/webhook \
  -H "Content-Type: application/json" \
  -d '{"event_type":"subscription.created"}'

# Expected: 401 "Missing webhook signature"
```

### Test 4: JWT Verification

```bash
# Try with fake JWT (should FAIL in production)
curl -X GET https://yourdomain.com/api/auth/me \
  -H "Authorization: Bearer fake.jwt.token"

# Expected: 401 "Invalid authentication token"
```

### Test 5: Credit Refund on Failure

1. Start analysis with valid auth
2. Kill backend mid-analysis: `sudo systemctl stop adcopysurge`
3. Restart: `sudo systemctl start adcopysurge`
4. Check user credits - should be refunded (check logs for "🔄 Refunding credits")

### Test 6: Idempotency

```bash
# Send same transaction twice quickly
IDEMPOTENCY_KEY=$(uuidgen)
curl -X POST https://yourdomain.com/api/subscriptions/paddle/checkout \
  -H "Authorization: Bearer YOUR_JWT" \
  -H "Content-Type: application/json" \
  -d "{\"tier\":\"growth\",\"idempotency_key\":\"$IDEMPOTENCY_KEY\"}"

# Send again with same key
curl -X POST https://yourdomain.com/api/subscriptions/paddle/checkout \
  -H "Authorization: Bearer YOUR_JWT" \
  -H "Content-Type: application/json" \
  -d "{\"tier\":\"growth\",\"idempotency_key\":\"$IDEMPOTENCY_KEY\"}"

# Second request should return cached response instantly
```

---

## 📊 Monitoring

### What to Watch

1. **Credit Balance Integrity**
   ```sql
   -- Check for negative balances (should be 0)
   SELECT user_id, current_credits
   FROM user_credits
   WHERE current_credits < 0;
   ```

2. **Failed Refunds**
   ```bash
   # Check logs for manual refund needed
   sudo journalctl -u adcopysurge | grep "MANUAL REFUND NEEDED"
   ```

3. **Webhook Failures**
   ```bash
   # Check Paddle webhook logs
   sudo journalctl -u adcopysurge | grep "Webhook signature verification failed"
   ```

4. **Idempotency Key Buildup**
   ```sql
   -- Should be cleaned up daily
   SELECT COUNT(*) FROM paddle_idempotency_keys;
   ```

### Set Up Alerts

Create alerts for:
- Negative credit balances
- Webhook signature failures > 5/hour
- Manual refund logs
- Idempotency table > 10,000 rows

---

## 🔄 Rollback Plan

If issues occur, rollback immediately:

```bash
# Step 1: Restore database
pg_restore -U postgres -d adcopysurge backup_YYYYMMDD_HHMMSS.dump

# Step 2: Rollback code
cd /opt/adcopysurge/backend
git checkout <previous-commit-hash>

# Step 3: Rollback migration
alembic downgrade -1

# Step 4: Restart service
sudo systemctl restart adcopysurge
```

---

## 📞 Support

**Critical Issues:**
- Create GitHub issue: https://github.com/yourusername/adcopysurge/issues
- Tag with `critical` and `security`

**Manual Refunds:**
If automatic refunds fail, use this SQL:

```sql
-- Find failed analysis
SELECT * FROM credit_transactions
WHERE user_id = 'USER_ID'
ORDER BY created_at DESC
LIMIT 10;

-- Manual refund (replace values)
UPDATE user_credits
SET current_credits = current_credits + 2
WHERE user_id = 'USER_ID';

INSERT INTO credit_transactions (user_id, operation, amount, description)
VALUES ('USER_ID', 'MANUAL_REFUND', 2, 'Manual refund for failed analysis');
```

---

## 📝 Change Log

### Version 1.0.0 (2025-01-20)

**New Files:**
- `backend/app/services/credit_service.py` - Atomic credit operations
- `backend/app/models/paddle_idempotency.py` - Idempotency table model
- `backend/app/tasks/credit_reset.py` - Monthly reset task
- `backend/run_credit_reset.py` - Cron script
- `backend/tests/test_credit_service_security.py` - Security tests
- `backend/alembic/versions/20250120_security_fixes_credit_system.py` - Migration

**Modified Files:**
- `backend/app/api/ads.py` - Added auth + refund logic
- `backend/app/api/subscriptions.py` - Enforced webhook verification
- `backend/app/services/paddle_service.py` - Added idempotency + credit sync
- `backend/app/middleware/supabase_auth.py` - Fixed JWT verification

**Database Changes:**
- Added `paddle_idempotency_keys` table
- Added `paddle_customer_id` column to `users` table

---

## ✨ Success Metrics

**After deployment, you should see:**
- ✅ Zero race condition exploits (concurrent requests properly rejected)
- ✅ Credit refunds appearing in logs for failed analyses
- ✅ 401 errors for unauthenticated analysis attempts
- ✅ Webhook signature failures logged and rejected
- ✅ No duplicate Paddle transactions
- ✅ Monthly credit resets running automatically

**Revenue Protection:**
Estimated 20-50% revenue recovery from closed exploits.

---

**Deployment Status:** [ ] Not Started | [ ] In Progress | [ ] Completed | [ ] Rolled Back

**Deployed By:** ________________
**Date/Time:** ________________
**Verified By:** ________________
