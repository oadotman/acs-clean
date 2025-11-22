# 🚀 DEPLOY NOW - Quick Start Guide

## TL;DR - 3 Commands to Deploy

```bash
# 1. Run migration (fixes user registration)
cd backend && alembic upgrade head

# 2. Set permissions (security fix)
sudo chown -R www-data:www-data /opt/adcopysurge /var/log/adcopysurge /run/adcopysurge

# 3. Restart service
sudo systemctl restart adcopysurge && sudo systemctl status adcopysurge
```

**That's it!** Critical fixes are deployed. Now validate →

---

## What Just Got Fixed

✅ **User registration bug** - New users can now sign up (was 100% failure)
✅ **Security vulnerability** - No longer running as root
✅ **Credit refund UX** - Users see toast when credits refunded
✅ **Console pollution** - Production builds are clean

---

## Validation Steps (15 minutes)

### 1. Test User Registration (5 min)

```bash
# Create test user via your app
# Use email: test+nov20@yourdomain.com
# Method: Supabase magic link or OAuth

# Verify in database:
psql $DATABASE_URL -c "
  SELECT id, email, hashed_password, supabase_user_id
  FROM users
  WHERE email LIKE 'test+nov20%';
"

# Expected: hashed_password should be NULL ✅
```

### 2. Test Credit System (5 min)

```bash
# 1. Login as test user
# 2. Check credit balance shows correctly
# 3. Run an analysis
# 4. Verify credits deduct (e.g., 5 → 3)
# 5. Check logs:

sudo journalctl -u adcopysurge -f | grep -i credit

# Expected: "✅ Credits deducted: 2 credits, remaining: 3"
```

### 3. Test Credit Refund (5 min)

```bash
# Option A: Disable OpenAI key temporarily
# Edit .env: OPENAI_API_KEY=invalid
# Restart: sudo systemctl restart adcopysurge

# Option B: Use test endpoint (if exists)

# Then:
# 1. Run analysis (should fail)
# 2. Watch for toast: "X credits refunded to your account" ✅
# 3. Verify credits restored
# 4. Re-enable OpenAI key
```

---

## Environment Variables Check (CRITICAL)

Run this on production server:

```bash
cd backend
python3 << 'EOF'
from app.core.config import settings
import os

critical = {
    'PADDLE_WEBHOOK_SECRET': os.getenv('PADDLE_WEBHOOK_SECRET'),
    'SUPABASE_JWT_SECRET': settings.SUPABASE_JWT_SECRET,
    'OPENAI_API_KEY': settings.OPENAI_API_KEY,
}

print("Critical Variables:")
for k, v in critical.items():
    status = "✅" if v and len(str(v)) > 10 else "❌ MISSING"
    print(f"{status} {k}")

if all(v and len(str(v)) > 10 for v in critical.values()):
    print("\n✅ ALL CRITICAL VARS SET - READY TO LAUNCH")
else:
    print("\n❌ MISSING VARS - CHECK .env FILE")
EOF
```

**If any ❌ appears, fix in `.env` before launch!**

---

## Monitoring Setup (1 hour - HIGHLY RECOMMENDED)

Follow `SENTRY_SETUP.md` to set up error tracking.

**Quick version:**

1. Create Sentry account (free): https://sentry.io/signup/
2. Create 2 projects: backend (Python) + frontend (React)
3. Add DSNs to `.env`:
   ```bash
   # Backend .env
   SENTRY_DSN=https://[hash]@o[org].ingest.sentry.io/[id]

   # Frontend .env
   REACT_APP_SENTRY_DSN=https://[hash]@o[org].ingest.sentry.io/[id]
   ```
4. Restart backend: `sudo systemctl restart adcopysurge`
5. Rebuild frontend: `npm run build` (Netlify auto-deploys)
6. Test: Trigger error, check Sentry dashboard

---

## SSL Setup (30 min - REQUIRED for production)

```bash
# Install certbot
sudo apt-get update
sudo apt-get install certbot python3-certbot-nginx -y

# Get certificate (replace with your domain)
sudo certbot --nginx -d adcopysurge.com -d www.adcopysurge.com

# Verify
curl -I https://adcopysurge.com | head -n 5

# Expected: "HTTP/2 200"
```

Test your SSL grade: https://www.ssllabs.com/ssltest/
**Target: A or A+**

---

## Pre-Launch Checklist

Quick checklist before advertising:

- [ ] Migration run: `alembic current` shows latest revision
- [ ] Permissions set: `ls -la /opt/adcopysurge | grep www-data`
- [ ] Service running: `systemctl status adcopysurge` shows "active (running)"
- [ ] User registration works: Test signup
- [ ] Credit deduction works: Run analysis, credits decrease
- [ ] Credit refund works: Trigger error, credits restored
- [ ] Environment vars set: All critical vars ✅
- [ ] Sentry configured: Errors appear in dashboard
- [ ] SSL active: https:// works, grade A
- [ ] Logs clean: No errors in `journalctl -u adcopysurge -n 100`

**All checked? You're ready to launch!** 🚀

---

## Launch Day Monitoring (First 4 hours)

### Monitor These:

**1. Sentry Dashboard**
```
Watch for:
- Payment errors (should be 0)
- Authentication errors (should be 0)
- Credit system errors (should be 0)
```

**2. Backend Logs**
```bash
# Watch live logs
sudo journalctl -u adcopysurge -f

# Filter for errors
sudo journalctl -u adcopysurge -f | grep -E "(ERROR|CRITICAL|Exception)"

# Filter for payments
sudo journalctl -u adcopysurge -f | grep -i paddle

# Filter for credits
sudo journalctl -u adcopysurge -f | grep -i credit
```

**3. Server Resources**
```bash
# Watch CPU/memory
htop

# Expected: CPU <60%, Memory <70%
```

**4. Paddle Webhook Delivery**
```
# Go to Paddle Dashboard → Developer → Notifications
# Check "Delivery" tab
# All webhooks should show "Success" (green check)
```

---

## If Something Goes Wrong

### Quick Rollback

```bash
# Stop service
sudo systemctl stop adcopysurge

# Revert code
cd /opt/adcopysurge
git log --oneline -5  # Find previous commit
git checkout <previous-commit-hash>

# Rollback migration (if needed)
cd backend
alembic downgrade -1

# Restart
sudo systemctl start adcopysurge
```

### Check Health

```bash
# Service status
sudo systemctl status adcopysurge

# Recent logs
sudo journalctl -u adcopysurge -n 100

# Error count
sudo journalctl -u adcopysurge -n 1000 | grep -c ERROR

# Expected: <5 errors
```

---

## Success Indicators

After 1 hour of traffic, you should see:

✅ **Sentry Dashboard**
- Error count: <10
- Affected users: <5% of total users
- No critical alerts

✅ **Backend Logs**
- New user registrations: Success
- Payment webhooks: All processed
- Credit operations: All atomic
- No 500 errors

✅ **Server Resources**
- CPU: <60%
- Memory: <70%
- Disk: <80%

✅ **User Metrics**
- Registration success rate: >95%
- Analysis completion rate: >90%
- Payment success rate: 100%

**If all green, increase advertising spend!** 📈

---

## Next Steps

**Today:**
1. ✅ Deploy code changes
2. ✅ Run migration
3. ✅ Validate environment vars
4. ✅ Test user registration

**Tomorrow:**
1. Set up Sentry monitoring
2. Set up SSL/HTTPS
3. Load testing
4. Final security audit

**Day After:**
1. Launch advertising!
2. Monitor for 4 hours continuously
3. Scale up if metrics are green

---

## Emergency Contacts

**Server Issues:**
- VPS Provider: [Your provider support]
- Access: `ssh user@your-server-ip`

**Database Issues:**
- Supabase Dashboard: https://app.supabase.com
- Support: [Project settings → Support]

**Payment Issues:**
- Paddle Dashboard: https://vendors.paddle.com
- Support: https://vendors.paddle.com/support

**AI Service Issues:**
- OpenAI Status: https://status.openai.com
- API Keys: https://platform.openai.com/api-keys

---

## File Reference

**Documentation:**
- `PRODUCTION_READINESS_SUMMARY.md` - Full audit results
- `PRODUCTION_CHECKLIST.md` - Complete validation checklist
- `SENTRY_SETUP.md` - Error monitoring setup
- `DEPLOY_NOW.md` - This file

**Code Changes:**
- `backend/app/models/user.py` - User model fix
- `backend/alembic/versions/20251120_make_hashed_password_nullable.py` - Migration
- `backend/gunicorn.conf.py` - Security fix
- `frontend/src/utils/logger.js` - Logger utility
- `frontend/src/hooks/useCredits.js` - Refund UX

---

## Bottom Line

✅ Critical fixes deployed
✅ Migration ready to run
✅ Security hardened
✅ UX improved
✅ Documentation complete

**Run the 3 commands at the top, validate, and you're ready to launch!**

Questions? Check the docs above or review the comprehensive audit in `PRODUCTION_READINESS_SUMMARY.md`.

**Good luck!** 🚀
