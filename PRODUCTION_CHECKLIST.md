# 🚀 Production Launch Checklist

## Critical Fixes Completed ✅

### 1. Database Schema Fix
- [x] Changed `hashed_password` from `nullable=False` to `nullable=True` in User model
- [x] Created Alembic migration `20251120_make_hashed_password_nullable.py`
- [ ] **ACTION REQUIRED:** Run migration on production database
  ```bash
  cd backend
  alembic upgrade head
  ```

### 2. Deployment Security
- [x] Changed Gunicorn to run as `www-data` (not root)
- [x] Increased timeout from 180s to 300s
- [ ] **ACTION REQUIRED:** Update file permissions on VPS
  ```bash
  sudo chown -R www-data:www-data /opt/adcopysurge
  sudo chown -R www-data:www-data /var/log/adcopysurge
  sudo chown -R www-data:www-data /run/adcopysurge
  ```

### 3. Frontend Logging
- [x] Created production-safe logger utility (`frontend/src/utils/logger.js`)
- [x] Replaced console.log in critical files (useCredits.js)
- [ ] **RECOMMENDED:** Replace remaining console.log statements across codebase

### 4. Credit Refund UX
- [x] Added toast notifications when credits are refunded
- [x] Improved error handling in `executeWithCredits` function

---

## Environment Variables Validation

### Backend `.env` (REQUIRED)

Run this validation script on your production server:

```bash
cd backend
python3 << 'EOF'
import os
from app.core.config import settings

print("=" * 80)
print("PRODUCTION ENVIRONMENT VALIDATION")
print("=" * 80)
print()

# Critical variables
critical_vars = {
    'SECRET_KEY': (settings.SECRET_KEY, lambda v: len(v) >= 32, "Must be at least 32 characters"),
    'DATABASE_URL': (settings.DATABASE_URL, lambda v: v and v.startswith('postgresql://'), "Must be valid PostgreSQL URL"),
    'SUPABASE_URL': (settings.SUPABASE_URL, lambda v: v and 'supabase.co' in v, "Must be valid Supabase URL"),
    'SUPABASE_SERVICE_ROLE_KEY': (settings.SUPABASE_SERVICE_ROLE_KEY, lambda v: v and len(v) > 100, "Must be valid service role key"),
    'SUPABASE_JWT_SECRET': (settings.SUPABASE_JWT_SECRET, lambda v: v and len(v) > 32, "Must be valid JWT secret"),
    'OPENAI_API_KEY': (settings.OPENAI_API_KEY, lambda v: v and v.startswith('sk-'), "Must be valid OpenAI API key"),
    'PADDLE_WEBHOOK_SECRET': (os.getenv('PADDLE_WEBHOOK_SECRET'), lambda v: v and len(v) > 10, "CRITICAL: Must be configured for payments"),
}

all_good = True
for var_name, (value, validator, description) in critical_vars.items():
    status = "✅" if value and validator(value) else "❌"
    if not (value and validator(value)):
        all_good = False
    print(f"{status} {var_name}: {description}")
    if not value:
        print(f"   → NOT SET!")
    elif not validator(value):
        print(f"   → INVALID VALUE!")

print()
print("=" * 80)
if all_good:
    print("✅ ALL CRITICAL ENVIRONMENT VARIABLES CONFIGURED")
else:
    print("❌ MISSING OR INVALID ENVIRONMENT VARIABLES - SEE ABOVE")
print("=" * 80)
EOF
```

### Required Environment Variables Checklist

#### Authentication & Database
- [ ] `SECRET_KEY` - At least 32 characters, random string
- [ ] `DATABASE_URL` - PostgreSQL connection string
- [ ] `SUPABASE_URL` - Your Supabase project URL
- [ ] `SUPABASE_SERVICE_ROLE_KEY` - From Supabase dashboard
- [ ] `SUPABASE_JWT_SECRET` - From Supabase dashboard → Settings → API → JWT Secret
- [ ] `SUPABASE_ANON_KEY` - Public anon key

#### AI Services
- [ ] `OPENAI_API_KEY` - For GPT-4 analysis (starts with `sk-`)
- [ ] `HUGGINGFACE_API_KEY` - For sentiment analysis (starts with `hf_`)
- [ ] `GEMINI_API_KEY` - Fallback AI service (optional but recommended)

#### Payment Processing
- [ ] `PADDLE_VENDOR_ID` - From Paddle dashboard
- [ ] `PADDLE_API_KEY` - From Paddle dashboard
- [ ] `PADDLE_CLIENT_TOKEN` - From Paddle dashboard
- [ ] `PADDLE_WEBHOOK_SECRET` - ⚠️ **CRITICAL** - From Paddle webhook settings
- [ ] `PADDLE_ENVIRONMENT` - Set to `production` (not `sandbox`)

#### Price IDs (All 8 Required)
- [ ] `PADDLE_GROWTH_MONTHLY_PRICE_ID`
- [ ] `PADDLE_GROWTH_YEARLY_PRICE_ID`
- [ ] `PADDLE_AGENCY_STANDARD_MONTHLY_PRICE_ID`
- [ ] `PADDLE_AGENCY_STANDARD_YEARLY_PRICE_ID`
- [ ] `PADDLE_AGENCY_PREMIUM_MONTHLY_PRICE_ID`
- [ ] `PADDLE_AGENCY_PREMIUM_YEARLY_PRICE_ID`
- [ ] `PADDLE_AGENCY_UNLIMITED_MONTHLY_PRICE_ID`
- [ ] `PADDLE_AGENCY_UNLIMITED_YEARLY_PRICE_ID`

#### Email Service (Team Invitations)
- [ ] `RESEND_API_KEY` - From Resend dashboard
- [ ] `RESEND_FROM_EMAIL` - Verified sender email
- [ ] `RESEND_FROM_NAME` - "AdCopySurge" or your company name

#### Production Configuration
- [ ] `ENVIRONMENT=production`
- [ ] `DEBUG=False`
- [ ] `CORS_ORIGINS` - Your frontend URL (e.g., `https://adcopysurge.com`)
- [ ] `ALLOWED_HOSTS` - Your domain (e.g., `adcopysurge.com`)

#### Optional but Recommended
- [ ] `SENTRY_DSN` - For error tracking (highly recommended!)
- [ ] `REDIS_URL` - For rate limiting (defaults to `redis://localhost:6379/0`)

---

## Database Migrations

### Current Migration Status

Check your current migration status:

```bash
cd backend
alembic current
```

### Required Migrations

Run all pending migrations:

```bash
cd backend
alembic upgrade head
```

**Expected migrations to run:**
1. `20251120_make_hashed_password_nullable` - **CRITICAL** - Fixes user registration
2. `20250120_align_subscription_tiers_with_pricing` - Adds new subscription tiers
3. `20250120_security_fixes_credit_system` - Adds paddle_idempotency_keys table

### Verify Migrations

After running migrations, verify:

```sql
-- Check subscription tiers exist
SELECT enumlabel FROM pg_enum
WHERE enumtypid = 'subscriptiontier'::regtype
ORDER BY enumsortorder;

-- Expected: free, growth, agency_standard, agency_premium, agency_unlimited
-- (plus legacy: basic, pro if they existed)

-- Check hashed_password is nullable
SELECT
    column_name,
    is_nullable,
    data_type
FROM information_schema.columns
WHERE table_name = 'users'
AND column_name = 'hashed_password';

-- Expected: is_nullable = 'YES'
```

---

## SSL/HTTPS Setup

### Install Let's Encrypt Certificate

```bash
# Install certbot
sudo apt-get update
sudo apt-get install certbot python3-certbot-nginx

# Obtain certificate (replace with your domain)
sudo certbot --nginx -d adcopysurge.com -d www.adcopysurge.com

# Test auto-renewal
sudo certbot renew --dry-run
```

### Verify SSL Configuration

```bash
# Check Nginx SSL config
sudo nginx -t

# Restart Nginx
sudo systemctl restart nginx
```

### Test SSL Grade

Visit https://www.ssllabs.com/ssltest/ and test your domain. Aim for **A or A+** rating.

---

## Pre-Launch Testing

### 1. Test User Registration Flow

```bash
# Create test account via your app
# Email: test+production@yourdomain.com
# Method: Supabase auth (magic link or OAuth)

# Verify user created successfully
# Check database:
SELECT id, email, hashed_password, supabase_user_id, created_at
FROM users
WHERE email = 'test+production@yourdomain.com';

# hashed_password should be NULL for Supabase users ✅
```

### 2. Test Payment Webhook

```bash
# In Paddle dashboard:
# 1. Go to Developer → Notifications
# 2. Find your production webhook URL
# 3. Click "Send test notification"
# 4. Choose event: subscription.created

# Check backend logs:
sudo journalctl -u adcopysurge -f | grep -i paddle

# Expected: "✅ Webhook signature verified"
# Expected: "✅ Credits allocated for subscription"
```

### 3. Test Credit System

```bash
# 1. Login as test user
# 2. Check credit balance (should match subscription tier)
# 3. Run an analysis
# 4. Verify credits deducted (e.g., 600 → 598)
# 5. Check backend logs:

sudo journalctl -u adcopysurge -f | grep -i credit

# Expected: "✅ Credits deducted: 2 credits, remaining: 598"
```

### 4. Test Credit Refund (Error Scenario)

```bash
# 1. Temporarily disable OpenAI API key in .env
# 2. Run an analysis (should fail)
# 3. Verify credits are refunded
# 4. Check toast notification shows refund
# 5. Re-enable OpenAI API key
```

### 5. Load Testing (Optional but Recommended)

```bash
# Install Apache Bench
sudo apt-get install apache2-utils

# Test API endpoint
ab -n 100 -c 10 https://api.adcopysurge.com/health

# Expected: 100% success rate, avg response < 500ms
```

---

## Monitoring Setup (See SENTRY_SETUP.md)

- [ ] Backend Sentry configured
- [ ] Frontend Sentry configured
- [ ] Test error reporting works
- [ ] Set up Sentry alerts for critical errors

---

## Launch Day Checklist

### Before Going Live

- [ ] All environment variables verified
- [ ] All database migrations run successfully
- [ ] SSL certificate installed and A-rated
- [ ] File permissions set to www-data
- [ ] Sentry monitoring active
- [ ] Database backups configured
- [ ] Test user registration works
- [ ] Test payment webhook works
- [ ] Test credit deduction works
- [ ] Test credit refund works

### Go Live

- [ ] Deploy latest code to production
- [ ] Restart backend service: `sudo systemctl restart adcopysurge`
- [ ] Check service status: `sudo systemctl status adcopysurge`
- [ ] Monitor logs for 15 minutes: `sudo journalctl -u adcopysurge -f`
- [ ] Test complete user journey (signup → subscribe → analyze)
- [ ] Monitor Sentry dashboard

### First Hour Monitoring

- [ ] Watch for errors in Sentry
- [ ] Monitor server resources: `htop`
- [ ] Check Paddle webhook delivery
- [ ] Verify credit operations logging correctly
- [ ] Test from multiple devices/browsers

---

## Rollback Plan

If issues occur after launch:

### Quick Rollback

```bash
# Stop service
sudo systemctl stop adcopysurge

# Revert to previous deployment
cd /opt/adcopysurge
git checkout <previous-commit-hash>

# Restart service
sudo systemctl start adcopysurge

# Check status
sudo systemctl status adcopysurge
```

### Database Rollback

```bash
# Only if migration caused issues
cd backend
alembic downgrade -1  # Rollback one migration

# Or rollback to specific revision
alembic downgrade <revision_id>
```

---

## Post-Launch Monitoring (First 7 Days)

### Daily Checks

- [ ] Check Sentry for new errors (target: <10 errors/day)
- [ ] Verify payment webhooks processing (target: 100% success)
- [ ] Monitor credit refund rate (target: <5%)
- [ ] Check API error rate (target: <1%)
- [ ] Review server resource usage (CPU, memory, disk)

### Weekly Checks

- [ ] Review user registration success rate (target: >95%)
- [ ] Analyze payment conversion rate
- [ ] Check database size and backup status
- [ ] Review SSL certificate expiry (auto-renews but verify)
- [ ] Update dependencies if security patches available

---

## Emergency Contacts

**Server Issues:**
- VPS Provider: [Your VPS support]
- SSH Access: [Your server IP/hostname]

**Payment Issues:**
- Paddle Support: https://vendors.paddle.com/support
- Paddle Dashboard: https://vendors.paddle.com

**Database Issues:**
- Supabase Dashboard: https://app.supabase.com
- Supabase Support: [Your project support]

**AI Service Issues:**
- OpenAI Status: https://status.openai.com
- OpenAI Support: https://help.openai.com

---

## Success Metrics

After 1 week, you should see:
- ✅ User registration success rate: >95%
- ✅ Payment webhook success rate: 100%
- ✅ Credit refund rate: <5%
- ✅ API error rate: <1%
- ✅ Average analysis time: 60-120 seconds
- ✅ SSL Labs grade: A or A+
- ✅ Zero services running as root
- ✅ Sentry tracking all errors

**If all metrics are green, you're ready to invest in advertising!** 🚀
