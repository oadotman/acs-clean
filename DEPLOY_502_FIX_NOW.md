# Deploy 502 Fix to Production - Step by Step

## Problem
Analysis endpoint returning 502 Bad Gateway because Gunicorn timeout (60s) is too short for AI analysis (60-120s).

## Quick Fix (5 minutes)

### Step 1: SSH into your VPS

```bash
ssh your-username@your-vps-ip
```

### Step 2: Run the diagnostic script

```bash
# Upload and run diagnostic
cd /tmp
curl -O https://raw.githubusercontent.com/your-repo/acs-clean/main/PRODUCTION_502_DIAGNOSTIC.sh
chmod +x PRODUCTION_502_DIAGNOSTIC.sh
./PRODUCTION_502_DIAGNOSTIC.sh
```

**OR** if you don't have the script uploaded yet, manually check:

```bash
# Check if backend is running
sudo systemctl status adcopysurge

# Check current timeout setting
cat /opt/adcopysurge/backend/gunicorn.conf.py | grep timeout

# Check recent errors
sudo journalctl -u adcopysurge -n 50 --no-pager
```

### Step 3: Navigate to backend directory

```bash
cd /opt/adcopysurge/backend

# Verify you're in the right place
pwd
# Should show: /opt/adcopysurge/backend (or your deployment path)
```

### Step 4: Pull latest changes

```bash
# Stash any local changes (if needed)
git stash

# Pull the timeout fix
git pull origin main

# Or if you're on a different branch:
git pull origin clean-security  # Use your main branch name
```

**Expected output:**
```
Updating abc1234..def5678
Fast-forward
 gunicorn.conf.py | 2 +-
 1 file changed, 1 insertion(+), 1 deletion(-)
```

### Step 5: Verify the timeout change

```bash
# Check that timeout is now 180
cat gunicorn.conf.py | grep timeout

# Should show:
# timeout = 180  # 3 minutes - AI analysis takes 60-120 seconds, need buffer
```

### Step 6: Restart the backend service

```bash
sudo systemctl restart adcopysurge

# Wait 3 seconds for startup
sleep 3

# Check status
sudo systemctl status adcopysurge
```

**Expected status:**
```
● adcopysurge.service - AdCopySurge Backend API
   Loaded: loaded
   Active: active (running) since ...
```

### Step 7: Monitor the logs

```bash
# Watch logs in real-time
sudo journalctl -u adcopysurge -f
```

**Look for:**
- ✅ "Worker spawned" messages
- ✅ "Application startup completed successfully"
- ❌ NO "Worker timeout" errors

Press `Ctrl+C` to stop watching logs.

### Step 8: Test the fix

Open a new terminal and test:

```bash
# Test health endpoint
curl http://localhost:8000/health

# Should return:
# {"status":"healthy","timestamp":...}
```

Then test from your browser:
1. Go to https://adcopysurge.com
2. Try running an analysis
3. Wait 60-120 seconds
4. ✅ Should complete successfully (not 502)

---

## If Git Pull Fails

If `git pull` shows conflicts or fails, manually edit the file:

```bash
# Edit gunicorn config directly
sudo nano /opt/adcopysurge/backend/gunicorn.conf.py

# Find line 16 (around line 16):
timeout = 60  # OLD

# Change to:
timeout = 180  # 3 minutes - AI analysis takes 60-120 seconds, need buffer

# Save: Ctrl+X, Y, Enter

# Restart
sudo systemctl restart adcopysurge
```

---

## If Backend Won't Start

```bash
# Check for errors
sudo journalctl -u adcopysurge -n 100 --no-pager

# Common issues:
# 1. Python syntax error - check the file
# 2. Permission issues - check ownership
# 3. Port already in use - kill old process
# 4. Database connection - check DATABASE_URL in .env
```

### Check Python syntax

```bash
cd /opt/adcopysurge/backend
python3 -m py_compile gunicorn.conf.py

# If no output = syntax is OK
# If error = fix syntax error shown
```

### Check file ownership

```bash
ls -la /opt/adcopysurge/backend/gunicorn.conf.py

# Should be owned by your deploy user or www-data
# If not:
sudo chown www-data:www-data /opt/adcopysurge/backend/gunicorn.conf.py
```

### Kill stuck processes

```bash
# Find Gunicorn processes
ps aux | grep gunicorn

# Kill them (replace PID with actual process IDs)
sudo kill -9 PID

# Restart service
sudo systemctl restart adcopysurge
```

---

## Verification Checklist

After deployment, verify:

- [ ] Backend service is running: `sudo systemctl status adcopysurge`
- [ ] Timeout is 180s: `grep timeout /opt/adcopysurge/backend/gunicorn.conf.py`
- [ ] Workers are running: `ps aux | grep gunicorn | wc -l` (should be > 0)
- [ ] Health check passes: `curl http://localhost:8000/health`
- [ ] No timeout errors: `sudo journalctl -u adcopysurge --since "5 min ago" | grep -i timeout`
- [ ] Analysis completes: Test from browser (should take 60-120s, not fail with 502)

---

## Still Getting 502?

If 502 errors persist after deploying the fix:

### 1. Check if backend is actually running

```bash
# Should show active (running)
sudo systemctl status adcopysurge

# Should show multiple processes
ps aux | grep gunicorn
```

### 2. Test backend directly (bypass Nginx)

```bash
# From VPS, test backend API directly
curl -v http://localhost:8000/health

# Should return 200 OK
```

### 3. Check Nginx is running and configured

```bash
# Check Nginx status
sudo systemctl status nginx

# Check Nginx configuration
sudo nginx -t

# Reload Nginx if needed
sudo systemctl reload nginx
```

### 4. Check backend error logs

```bash
# Watch for crashes or errors
sudo tail -f /var/log/adcopysurge/error.log

# Or journalctl
sudo journalctl -u adcopysurge -f
```

### 5. Check for these specific errors

```bash
# Worker timeout (should NOT see this anymore)
sudo journalctl -u adcopysurge --since "10 min ago" | grep "TERM"

# Import errors
sudo journalctl -u adcopysurge --since "10 min ago" | grep "ImportError\|ModuleNotFoundError"

# Database errors
sudo journalctl -u adcopysurge --since "10 min ago" | grep "database\|sqlalchemy"

# OpenAI API errors
sudo journalctl -u adcopysurge --since "10 min ago" | grep "openai\|api.*key"
```

### 6. Test a minimal analysis

Create a test file:

```bash
cat > /tmp/test_analysis.json << 'EOF'
{
  "ad": {
    "headline": "Test",
    "body_text": "Test body",
    "cta": "Learn More",
    "platform": "facebook"
  },
  "competitor_ads": []
}
EOF

# Test directly to backend (bypass Nginx)
curl -X POST http://localhost:8000/api/ads/analyze \
  -H "Content-Type: application/json" \
  -d @/tmp/test_analysis.json \
  --max-time 180 \
  -v
```

**Expected**: JSON response with analysis (after 60-120s)
**If 502**: Backend is crashing or not responding - check logs

---

## Emergency Rollback

If the fix makes things worse (unlikely):

```bash
cd /opt/adcopysurge/backend

# Revert the change
git revert HEAD

# Or manually edit
sudo nano gunicorn.conf.py
# Change timeout back to 60

# Restart
sudo systemctl restart adcopysurge
```

---

## Success Indicators

You know the fix worked when:

1. ✅ Analysis completes after 60-120 seconds
2. ✅ No more 502 errors on `/api/ads/analyze`
3. ✅ No "Worker timeout" messages in logs
4. ✅ Users can successfully analyze ads

---

## Need Help?

If stuck, gather this info:

```bash
# System info
uname -a
python3 --version

# Service status
sudo systemctl status adcopysurge --no-pager

# Recent logs
sudo journalctl -u adcopysurge -n 100 --no-pager > /tmp/backend_logs.txt

# Gunicorn config
cat /opt/adcopysurge/backend/gunicorn.conf.py

# Process list
ps aux | grep gunicorn

# Port check
sudo netstat -tlnp | grep 8000
```

Then share the output for debugging.
