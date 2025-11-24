# Fix API Endpoint Issues - Deployment Steps

## Problem
The app is returning errors because `REACT_APP_API_URL` has a duplicate `/api` prefix causing:
- ❌ 404 errors: `https://adcopysurge.com/api/api/user/profile`
- ❌ HTML responses instead of JSON: "unexpected content type: text/html"

## Solution
Change `REACT_APP_API_URL` from `https://adcopysurge.com/api` to `https://adcopysurge.com` (remove the `/api` suffix).

---

## Deployment Instructions

### Step 1: SSH into your VPS

```bash
ssh root@your-vps-ip
# or
ssh root@v44954
```

### Step 2: Navigate to project directory

```bash
cd /var/www/acs-clean
```

### Step 3: Pull latest changes (includes deploy-fix.sh script)

```bash
git pull origin main
```

### Step 4: Edit the frontend .env file on VPS

```bash
nano frontend/.env
```

**Find and change this line:**
```bash
# OLD (incorrect - has duplicate /api):
REACT_APP_API_URL=https://adcopysurge.com/api

# NEW (correct - no /api suffix):
REACT_APP_API_URL=https://adcopysurge.com
```

**Save and exit:**
- Press `Ctrl + O` to save
- Press `Enter` to confirm
- Press `Ctrl + X` to exit

### Step 5: Run the deployment script

```bash
chmod +x deploy-fix.sh
./deploy-fix.sh
```

The script will automatically:
- ✅ Verify the .env fix
- ✅ Rebuild the frontend with correct API URL
- ✅ Restart the backend
- ✅ Reload Nginx

### Step 6: Verify the fix

Test these endpoints to confirm everything works:

```bash
# Test health check (should return JSON)
curl https://adcopysurge.com/health

# Test API endpoint (should return JSON, not HTML)
curl -I https://adcopysurge.com/api/credits/balance
```

**Expected output:**
```
HTTP/2 200
content-type: application/json  ← Should be JSON, not text/html
```

---

## Alternative: Manual Deployment (if script fails)

If the `deploy-fix.sh` script doesn't work, run these commands manually:

```bash
# 1. Navigate to frontend directory
cd /var/www/acs-clean/frontend

# 2. Verify .env is correct
grep REACT_APP_API_URL .env
# Should output: REACT_APP_API_URL=https://adcopysurge.com
# If it has /api at the end, edit with: nano .env

# 3. Install dependencies and rebuild
npm install
npm run build

# 4. Restart backend
cd /var/www/acs-clean/backend
pm2 restart acs-backend

# 5. Check PM2 status
pm2 status
pm2 logs acs-backend --lines 50

# 6. Reload Nginx
sudo nginx -t
sudo nginx -s reload
```

---

## Troubleshooting

### Issue: Still getting 404 errors

**Check if backend is running:**
```bash
pm2 status
pm2 logs acs-backend --lines 50
```

**Check if backend is accessible:**
```bash
curl http://localhost:8000/health
```

### Issue: Still getting HTML instead of JSON

**Check Nginx configuration:**
```bash
sudo nginx -t
sudo cat /etc/nginx/sites-enabled/adcopysurge.com
```

**Look for proxy_pass directive - should be:**
```nginx
location /api/ {
    proxy_pass http://localhost:8000/api/;
    # ... other settings
}
```

### Issue: Frontend not showing changes

**Clear browser cache:**
- Hard refresh: `Ctrl + Shift + R` (Windows/Linux) or `Cmd + Shift + R` (Mac)
- Or open in incognito/private browsing mode

**Verify build has new .env:**
```bash
cd /var/www/acs-clean/frontend
grep -r "adcopysurge.com/api/api" build/
# Should return nothing (empty)
```

---

## Post-Deployment Checklist

- [ ] Frontend .env updated: `REACT_APP_API_URL=https://adcopysurge.com`
- [ ] Frontend rebuilt: `npm run build` completed successfully
- [ ] Backend running: `pm2 status` shows `acs-backend` as `online`
- [ ] Nginx reloaded: `sudo nginx -s reload` completed
- [ ] Health check works: `curl https://adcopysurge.com/health` returns JSON
- [ ] API endpoints work: No more `/api/api/` double prefix errors
- [ ] Browser console: No more "404 Not Found" or "unexpected content type" errors
- [ ] Credit balance loads: CreditsWidget shows balance without errors

---

## Why .env wasn't in git commit

The `.env` files are intentionally excluded from git (listed in `.gitignore`) because they contain:
- API keys
- Database passwords
- Secrets and tokens

**This is correct and secure!**

You must manually update `.env` files on each deployment environment (development, staging, production) rather than committing them to version control.
