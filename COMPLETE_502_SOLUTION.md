# Complete 502 Error Solution - End-to-End

## Root Cause Analysis

The 502 Bad Gateway error on `/api/ads/analyze` is caused by **Gunicorn worker timeout**.

### The Problem Chain

```
User clicks "Analyze"
    ↓
Frontend sends POST to /api/ads/analyze (120s timeout)
    ↓
Nginx proxies request to backend (300s timeout) ✅
    ↓
Gunicorn receives request (60s timeout) ❌ TOO SHORT
    ↓
Analysis starts - runs 9 AI tools in parallel
    ↓
[60 seconds pass]
    ↓
Gunicorn kills worker with SIGTERM (timeout exceeded)
    ↓
Nginx receives no response from backend
    ↓
Nginx returns 502 Bad Gateway to frontend
    ↓
Frontend shows: "Request failed with status code 502"
```

**Analysis takes 60-120 seconds, but Gunicorn times out at 60 seconds!**

---

## The Fix

Change Gunicorn timeout from 60s to 180s (3 minutes).

**File**: `backend/gunicorn.conf.py` line 16

```python
# BEFORE
timeout = 60  # Increased for AI processing

# AFTER
timeout = 180  # 3 minutes - AI analysis takes 60-120 seconds, need buffer
```

---

## Deployment to Production (Choose One Method)

### Method 1: Git Pull (Recommended)

```bash
# SSH into VPS
ssh user@your-vps-ip

# Navigate to backend
cd /opt/adcopysurge/backend

# Pull latest changes (includes the timeout fix)
git pull origin main

# Verify the change
grep "timeout" gunicorn.conf.py
# Should show: timeout = 180

# Restart backend
sudo systemctl restart adcopysurge

# Check status
sudo systemctl status adcopysurge

# Monitor startup
sudo journalctl -u adcopysurge -f
# (Press Ctrl+C to exit)
```

### Method 2: Manual Edit (If Git Fails)

```bash
# SSH into VPS
ssh user@your-vps-ip

# Edit the config file
sudo nano /opt/adcopysurge/backend/gunicorn.conf.py

# Find line 16 and change:
# FROM: timeout = 60
# TO:   timeout = 180  # 3 minutes - AI analysis takes 60-120 seconds, need buffer

# Save: Ctrl+X, Y, Enter

# Restart backend
sudo systemctl restart adcopysurge

# Verify
sudo systemctl status adcopysurge
```

---

## Verification Steps

### 1. Check Backend is Running

```bash
sudo systemctl status adcopysurge
```

Expected output:
```
● adcopysurge.service - AdCopySurge Backend API
   Active: active (running) since [timestamp]
```

### 2. Verify Timeout Setting

```bash
cat /opt/adcopysurge/backend/gunicorn.conf.py | grep timeout
```

Expected output:
```
timeout = 180  # 3 minutes - AI analysis takes 60-120 seconds, need buffer
```

### 3. Check Workers are Running

```bash
ps aux | grep gunicorn | grep -v grep
```

Expected: Should see 2-4 worker processes

### 4. Test Health Endpoint

```bash
curl http://localhost:8000/health
```

Expected output:
```json
{"status":"healthy","timestamp":1234567890}
```

### 5. Monitor Logs for Errors

```bash
sudo journalctl -u adcopysurge -n 50 --no-pager
```

Look for:
- ✅ "Application startup completed successfully"
- ✅ "Worker spawned"
- ❌ NO "Worker timeout" errors
- ❌ NO import errors or crashes

### 6. Test Analysis Endpoint

From your browser:
1. Go to https://adcopysurge.com
2. Enter ad copy to analyze
3. Click "Analyze"
4. Wait 60-120 seconds
5. ✅ Should return results (NOT 502 error)

---

## Detailed Troubleshooting

### Issue 1: Backend Service Won't Start

**Symptoms:**
```bash
sudo systemctl status adcopysurge
# Shows: Active: failed or inactive
```

**Diagnosis:**
```bash
# Check recent errors
sudo journalctl -u adcopysurge -n 100 --no-pager

# Common errors to look for:
# - ModuleNotFoundError: Missing Python dependencies
# - Database connection failed: Check DATABASE_URL
# - Port already in use: Kill old processes
# - Permission denied: Check file ownership
```

**Solutions:**

**A. Missing Dependencies**
```bash
cd /opt/adcopysurge/backend
source venv/bin/activate  # If using venv
pip install -r requirements.txt
sudo systemctl restart adcopysurge
```

**B. Database Connection Issues**
```bash
# Test database connection
cd /opt/adcopysurge/backend
python3 << EOF
from app.core.database import engine
from sqlalchemy import text
with engine.connect() as conn:
    result = conn.execute(text("SELECT 1"))
    print("Database OK:", result.scalar())
EOF
```

**C. Port Already in Use**
```bash
# Find process using port 8000
sudo netstat -tlnp | grep 8000
# or
sudo lsof -i :8000

# Kill the process (replace PID)
sudo kill -9 PID

# Restart service
sudo systemctl restart adcopysurge
```

**D. Permission Issues**
```bash
# Check ownership
ls -la /opt/adcopysurge/backend/

# Fix if needed (replace www-data with your user)
sudo chown -R www-data:www-data /opt/adcopysurge/backend/
```

### Issue 2: Workers Keep Dying/Restarting

**Symptoms:**
```bash
# Logs show repeated worker restarts
sudo journalctl -u adcopysurge -f
# Shows: Worker exiting, Worker spawned, Worker exiting...
```

**Diagnosis:**
```bash
# Check for out-of-memory errors
dmesg | grep -i "out of memory"

# Check memory usage
free -h

# Check worker errors
sudo journalctl -u adcopysurge --since "10 min ago" | grep -i "error\|exception\|traceback"
```

**Solutions:**

**A. Memory Issues**
```bash
# Check total memory
free -h

# If low memory, reduce workers
sudo nano /opt/adcopysurge/backend/gunicorn.conf.py
# Change: workers = 2  # Reduce from 4

sudo systemctl restart adcopysurge
```

**B. Import/Code Errors**
```bash
# Test if Python code loads
cd /opt/adcopysurge/backend
python3 -c "from app.api import ads; print('OK')"

# If error, check the specific import
python3 -c "from app.services.ad_analysis_service_enhanced import EnhancedAdAnalysisService"
```

### Issue 3: Still Getting 502 After Timeout Fix

**Symptoms:**
- Timeout is set to 180
- Backend is running
- Still getting 502 errors

**Possible Causes:**

**A. Workers Crashing During Analysis**

```bash
# Monitor logs while testing
sudo journalctl -u adcopysurge -f

# In another terminal, trigger analysis
# Watch for crash/exception messages
```

**B. OpenAI API Issues**

```bash
# Check if OpenAI key is set
cd /opt/adcopysurge/backend
grep OPENAI_API_KEY .env

# Test OpenAI connection
python3 << EOF
import os
from openai import OpenAI
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
try:
    client.models.list()
    print("OpenAI API: OK")
except Exception as e:
    print(f"OpenAI API Error: {e}")
EOF
```

**C. Database Query Timeout**

```bash
# Check database query performance
# Look for slow query logs in:
sudo journalctl -u adcopysurge | grep -i "database\|query.*slow"
```

**D. Nginx Not Forwarding Correctly**

```bash
# Test backend directly (bypass Nginx)
curl -X POST http://localhost:8000/api/ads/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "ad": {
      "headline": "Test",
      "body_text": "Test body",
      "cta": "Learn More",
      "platform": "facebook"
    },
    "competitor_ads": [],
    "user_id": "test-user"
  }' \
  --max-time 180

# If this works but browser still gets 502, issue is with Nginx
# Check Nginx config
sudo nginx -t
sudo systemctl reload nginx
```

### Issue 4: Timeout Happens at Exactly 60 Seconds

**This confirms Gunicorn timeout is the issue**

```bash
# Verify timeout setting
grep timeout /opt/adcopysurge/backend/gunicorn.conf.py

# Should be 180, not 60
# If still showing 60, the change wasn't applied

# Edit manually
sudo nano /opt/adcopysurge/backend/gunicorn.conf.py

# Restart
sudo systemctl restart adcopysurge

# Verify workers restarted with new config
ps aux | grep gunicorn
# Note the start time (should be recent)
```

---

## Complete System Health Check

Run all these commands to get full system status:

```bash
#!/bin/bash
echo "=== Backend Service Status ==="
sudo systemctl status adcopysurge --no-pager

echo -e "\n=== Gunicorn Workers ==="
ps aux | grep gunicorn | grep -v grep

echo -e "\n=== Current Timeout Setting ==="
grep timeout /opt/adcopysurge/backend/gunicorn.conf.py

echo -e "\n=== Recent Error Logs ==="
sudo journalctl -u adcopysurge -n 20 --no-pager

echo -e "\n=== Health Check ==="
curl -s http://localhost:8000/health | python3 -m json.tool

echo -e "\n=== Memory Usage ==="
free -h

echo -e "\n=== Disk Usage ==="
df -h | grep -E "Filesystem|/$"

echo -e "\n=== Port 8000 Status ==="
sudo netstat -tlnp | grep 8000

echo -e "\n=== Nginx Status ==="
sudo systemctl status nginx --no-pager | head -10
```

Save as `health_check.sh`, make executable, and run:
```bash
chmod +x health_check.sh
./health_check.sh
```

---

## Expected Timeline

After deploying the fix:

1. **Immediate** (0s): Backend restarts with new timeout
2. **~5s**: Workers spawn and app initializes
3. **~10s**: Health endpoint responds
4. **Test analysis**:
   - Request sent to backend
   - Analysis starts
   - **60-120 seconds** pass ✅ (workers stay alive)
   - Results returned ✅ (no 502)

---

## Success Criteria

✅ You know it's fixed when:

1. Backend service is active and running
2. `grep timeout gunicorn.conf.py` shows `timeout = 180`
3. Multiple Gunicorn workers are running
4. Health endpoint returns 200 OK
5. Analysis completes after 60-120 seconds (no 502)
6. No "Worker timeout" errors in logs
7. Users can successfully analyze ads

---

## If STILL Not Working

After trying everything above and 502 persists:

### Collect Debug Info

```bash
# Create debug report
cat > /tmp/debug_report.txt << 'EOF'
=== System Info ===
EOF
uname -a >> /tmp/debug_report.txt
python3 --version >> /tmp/debug_report.txt

cat >> /tmp/debug_report.txt << 'EOF'

=== Service Status ===
EOF
sudo systemctl status adcopysurge --no-pager >> /tmp/debug_report.txt

cat >> /tmp/debug_report.txt << 'EOF'

=== Gunicorn Config ===
EOF
cat /opt/adcopysurge/backend/gunicorn.conf.py >> /tmp/debug_report.txt

cat >> /tmp/debug_report.txt << 'EOF'

=== Recent Logs ===
EOF
sudo journalctl -u adcopysurge -n 200 --no-pager >> /tmp/debug_report.txt

cat >> /tmp/debug_report.txt << 'EOF'

=== Process List ===
EOF
ps aux | grep -E "gunicorn|python|uvicorn" >> /tmp/debug_report.txt

echo "Debug report saved to /tmp/debug_report.txt"
```

Then review `/tmp/debug_report.txt` or share for further debugging.

### Nuclear Option: Full Restart

```bash
# Stop everything
sudo systemctl stop adcopysurge
sudo systemctl stop nginx

# Kill any lingering processes
sudo pkill -9 gunicorn
sudo pkill -9 uvicorn

# Start fresh
sudo systemctl start adcopysurge
sleep 5
sudo systemctl start nginx

# Check status
sudo systemctl status adcopysurge
sudo systemctl status nginx
```

---

## Prevention

To avoid this in future:

1. **Monitor response times**: Set up alerts for requests >50s
2. **Load testing**: Test analysis with various ad lengths
3. **Proper timeouts**: Always keep timeout hierarchy:
   - Backend (Gunicorn): 1.5x max processing time
   - Proxy (Nginx): 2x backend timeout
   - Client (Frontend): Slightly less than proxy timeout

---

## Summary

**Problem**: Gunicorn timeout (60s) too short for AI analysis (60-120s)
**Solution**: Increase timeout to 180s in `gunicorn.conf.py`
**Deploy**: Git pull + restart backend service
**Verify**: Analysis completes successfully without 502

This is a simple configuration change that will immediately fix the 502 errors.
