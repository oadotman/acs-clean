# Production Verification Checklist

## Pre-Launch Verification Steps

Run these commands on your VPS to verify production readiness:

### 1. Backend Service Health ✓
```bash
# Check service is running
sudo systemctl status adcopysurge --no-pager | grep "Active:"
# Expected: Active: active (running)

# Test health endpoint
curl -s http://localhost:8000/health | head -1
# Expected: {"status":"healthy"} or similar

# Check for recent errors
sudo journalctl -u adcopysurge --since "1 hour ago" | grep -c ERROR
# Expected: 0 or very low number
```

### 2. Database Verification ✓
Run in Supabase SQL Editor:
```sql
-- Verify hashed_password is nullable
SELECT
    column_name,
    is_nullable,
    CASE
        WHEN is_nullable = 'YES' THEN '✅ READY'
        ELSE '❌ NOT READY'
    END as status
FROM information_schema.columns
WHERE table_name = 'users'
AND column_name = 'hashed_password';

-- Check subscription tiers exist
SELECT COUNT(*) as tier_count
FROM pg_enum
WHERE enumtypid = 'subscriptiontier'::regtype;
-- Expected: 5 or more tiers
```

### 3. Critical Environment Variables ✓
```bash
cd /var/www/acs-clean/backend

# Check all critical vars are set (don't show values for security)
for var in SECRET_KEY DATABASE_URL SUPABASE_URL SUPABASE_SERVICE_ROLE_KEY SUPABASE_JWT_SECRET OPENAI_API_KEY PADDLE_WEBHOOK_SECRET; do
    if grep -q "^$var=" .env 2>/dev/null && [ $(grep "^$var=" .env | cut -d'=' -f2 | wc -c) -gt 10 ]; then
        echo "✅ $var is set"
    else
        echo "❌ $var is missing or too short"
    fi
done
```

### 4. File Permissions ✓
```bash
# Check log directory ownership
ls -ld /var/log/adcopysurge/ | grep -q www-data && echo "✅ Log dir owned by www-data" || echo "❌ Fix log dir ownership"

# Check app directory ownership
ls -ld /var/www/acs-clean/ | grep -q www-data && echo "✅ App dir owned by www-data" || echo "❌ Fix app dir ownership"

# Check service user
grep "User=www-data" /etc/systemd/system/adcopysurge.service && echo "✅ Service runs as www-data" || echo "❌ Service not running as www-data"
```

### 5. Worker Configuration ✓
```bash
# Verify sync workers (not UvicornWorker)
grep 'worker_class = "sync"' /var/www/acs-clean/backend/gunicorn.conf.py && echo "✅ Using sync workers" || echo "❌ Wrong worker class"

# Check timeout is sufficient
grep "timeout = 300" /var/www/acs-clean/backend/gunicorn.conf.py && echo "✅ Timeout is 300s" || echo "⚠️ Check timeout setting"
```

### 6. Port Availability ✓
```bash
# Check port 8000
if sudo lsof -i :8000 | grep -q gunicorn; then
    echo "✅ Gunicorn running on port 8000"
else
    echo "❌ Port 8000 issue - check service"
fi
```

### 7. Nginx Configuration ✓
```bash
# Test Nginx config
sudo nginx -t 2>&1 | grep -q successful && echo "✅ Nginx config valid" || echo "❌ Nginx config error"

# Check upstream backend
grep -q "proxy_pass http://localhost:8000" /etc/nginx/sites-enabled/* && echo "✅ Nginx proxy configured" || echo "❌ Nginx proxy not configured"
```

## Functional Testing Checklist

### 8. Test User Registration
1. Go to your application frontend
2. Click "Sign Up" or "Register"
3. Enter a test email (e.g., `test@example.com`)
4. Complete registration via Supabase (magic link or OAuth)
5. ✅ Registration should succeed (no constraint violation error)

### 9. Test Credit System
1. Log in as a test user
2. Check credit balance displays
3. Note: Credit deduction happens BEFORE analysis (known issue)
4. ✅ Credits should be visible

### 10. Test Basic API Call
```bash
# Test from VPS
curl -X GET http://localhost:8000/api/health \
  -H "Content-Type: application/json"
# Expected: {"status":"ok"} or similar
```

## Security Checklist

### 11. Security Verification ✓
```bash
# Service not running as root
ps aux | grep gunicorn | grep -v grep | grep -q root && echo "❌ CRITICAL: Running as root!" || echo "✅ Not running as root"

# Check for exposed secrets in logs
sudo journalctl -u adcopysurge --since "1 day ago" | grep -i "secret\|key\|password" | grep -v "hashed_password" | wc -l
# Expected: 0 (no exposed secrets)
```

### 12. SSL/HTTPS Status
```bash
# Check if SSL is configured (if domain is set up)
if [ -f /etc/letsencrypt/live/*/fullchain.pem ]; then
    echo "✅ SSL certificate exists"
else
    echo "⚠️ No SSL certificate - needed before launch"
fi
```

## Quick Status Summary Script

Create and run this script for a quick overview:

```bash
cat > /tmp/check_production.sh << 'EOF'
#!/bin/bash
echo "=== Production Readiness Check ==="
echo ""

# Service status
if systemctl is-active adcopysurge >/dev/null 2>&1; then
    echo "✅ Backend service: RUNNING"
else
    echo "❌ Backend service: NOT RUNNING"
fi

# Health check
if curl -s http://localhost:8000/health >/dev/null 2>&1; then
    echo "✅ Health endpoint: RESPONDING"
else
    echo "❌ Health endpoint: NOT RESPONDING"
fi

# Worker class
if grep -q 'worker_class = "sync"' /var/www/acs-clean/backend/gunicorn.conf.py; then
    echo "✅ Worker class: sync (stable)"
else
    echo "⚠️ Worker class: Check configuration"
fi

# Permissions
if ls -ld /var/log/adcopysurge/ 2>/dev/null | grep -q www-data; then
    echo "✅ Log permissions: CORRECT"
else
    echo "❌ Log permissions: NEED FIX"
fi

# Critical vars
missing_vars=0
for var in SECRET_KEY SUPABASE_JWT_SECRET PADDLE_WEBHOOK_SECRET OPENAI_API_KEY; do
    if ! grep -q "^$var=" /var/www/acs-clean/backend/.env 2>/dev/null; then
        ((missing_vars++))
    fi
done

if [ $missing_vars -eq 0 ]; then
    echo "✅ Environment vars: ALL SET"
else
    echo "❌ Environment vars: $missing_vars MISSING"
fi

echo ""
echo "=== Summary ==="
echo "Run full checklist above for detailed verification"
EOF

chmod +x /tmp/check_production.sh
/tmp/check_production.sh
```

## Launch Readiness Score

Count your checkmarks:
- 12/12 ✅ = Ready to launch with confidence
- 10-11 ✅ = Ready to launch with monitoring
- 8-9 ✅ = Soft launch with limited traffic
- <8 ✅ = Fix remaining issues before launch

## If All Checks Pass ✅

1. **Monitor for 24 hours** before heavy advertising
2. **Set up Sentry** for error tracking (see SENTRY_SETUP.md)
3. **Configure alerts** for downtime
4. **Test payment flow** with a real card
5. **Launch advertising** gradually

## Common Issues Reference

| Issue | Fix |
|-------|-----|
| Service won't start | Check port 8000, permissions, worker class |
| Users can't register | Verify hashed_password nullable in DB |
| Analysis times out | Ensure timeout=300 in gunicorn.conf.py |
| 502 Bad Gateway | Service not running or wrong port |
| Permission denied | Run chown commands for www-data |

## Emergency Rollback

If something goes wrong after deployment:
```bash
# Quick rollback procedure
sudo systemctl stop adcopysurge
cd /var/www/acs-clean
git checkout <previous-commit>
sudo systemctl start adcopysurge
```

---

**Remember:** The sync worker configuration is working and stable. Don't change back to UvicornWorker without thorough testing!