# 🚀 Emergency Payment Fix Deployment Instructions

## Issues Fixed
1. ✅ **queryTimeout.js promise reference bug** - "Cannot access 'r' before initialization"
2. ✅ **CSP blocking Paddle checkout** - "This content is blocked" error
3. ✅ **Missing auth helper functions** in supabaseClient files

## Deployment Steps on VPS

### 1. Pull Latest Code
```bash
cd /path/to/acs-clean
git pull origin main
```

### 2. Update Frontend
```bash
cd frontend
npm install  # In case dependencies changed
npm run build  # Build production bundle
```

### 3. Update Nginx Configuration
Choose the appropriate nginx config for your setup:

#### Option A: If using `frontend/nginx-production.conf`
```bash
sudo cp frontend/nginx-production.conf /etc/nginx/sites-available/adcopysurge
sudo nginx -t  # Test configuration
sudo systemctl reload nginx
```

#### Option B: If using `nginx/production-secure.conf`
```bash
sudo cp nginx/production-secure.conf /etc/nginx/sites-available/adcopysurge
sudo nginx -t  # Test configuration
sudo systemctl reload nginx
```

### 4. Deploy Frontend Build
```bash
# Copy build files to web root
sudo cp -r frontend/build/* /var/www/adcopysurge/
```

### 5. Verify Environment Variables
Make sure these are set on VPS:
```bash
# Check .env file or environment
echo $REACT_APP_PADDLE_CLIENT_TOKEN
echo $REACT_APP_PADDLE_ENVIRONMENT
echo $REACT_APP_SUPABASE_URL
echo $REACT_APP_SUPABASE_ANON_KEY
```

### 6. Restart Services (if needed)
```bash
sudo systemctl restart nginx
# If you have PM2 or backend service:
pm2 restart all
```

### 7. Clear Browser Cache
After deployment, users should:
- Hard refresh: Ctrl+Shift+R (Windows/Linux) or Cmd+Shift+R (Mac)
- Or clear browser cache completely

## Verification Checklist

1. ✅ Visit site and check browser console - should NOT see:
   - "Cannot access 'r' before initialization"
   - "Refused to load the stylesheet"
   - "This content is blocked"

2. ✅ Click "Upgrade" button as free user:
   - Paddle checkout overlay should open
   - No CSP errors in console
   - Payment form should be visible

3. ✅ Check Credits Widget loads without errors

## Key Changes Made

### File: `frontend/src/utils/queryTimeout.js`
- Fixed promise variable scoping issue
- Added proper timeout cleanup with `.finally()`

### File: `frontend/src/lib/supabaseClient.js`
- Exported `signIn`, `signUp`, `signOut`, `getCurrentUser` helper functions

### File: `frontend/public/index.html`
- Updated CSP meta tag to allow Paddle resources

### File: `frontend/nginx-production.conf`
- Updated CSP header to allow:
  - `https://cdn.paddle.com` (scripts, styles, fonts)
  - `https://*.paddle.com` (all Paddle domains)
  - `https://checkout.paddle.com` (checkout iframe)
  - `https://sandbox-checkout.paddle.com` (sandbox checkout)
  - `unsafe-eval` for Paddle.js
  - `blob:` for workers

### File: `nginx/production-secure.conf`
- Same CSP updates as above

## Troubleshooting

### If "Cannot access 'r'" error persists:
```bash
# Clear build cache and rebuild
cd frontend
rm -rf node_modules/.cache
rm -rf build
npm run build
```

### If CSP errors persist:
```bash
# Check which nginx config is active
ls -la /etc/nginx/sites-enabled/

# View actual nginx config being used
cat /etc/nginx/sites-enabled/adcopysurge

# Check nginx error log
sudo tail -f /var/log/nginx/error.log
```

### If Paddle doesn't load:
1. Check `REACT_APP_PADDLE_CLIENT_TOKEN` is set correctly
2. Verify Paddle environment (sandbox vs production)
3. Check browser Network tab for 404s or CSP blocks

## Contact
If issues persist after deployment, check:
- Browser console for specific errors
- Nginx error logs: `/var/log/nginx/error.log`
- Nginx access logs: `/var/log/nginx/access.log`
