#!/bin/bash
# Complete fix for API routing issues

set -e

echo "=========================================="
echo "AdCopySurge API Routing Fix"
echo "=========================================="
echo ""

# Step 1: Diagnostic
echo "STEP 1: Running diagnostics..."
echo "----------------------------------------"

echo "Checking backend PM2 status..."
if pm2 describe acs-backend > /dev/null 2>&1; then
    echo "✅ Backend is running"
    pm2 describe acs-backend | grep -E "status|uptime|restarts"
else
    echo "❌ Backend is NOT running!"
fi
echo ""

echo "Checking if backend responds on localhost..."
if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo "✅ Backend health check passed"
    curl -s http://localhost:8000/health
else
    echo "❌ Backend not responding on port 8000!"
fi
echo ""

echo "Checking frontend build..."
if [ -f "/var/www/acs-clean/frontend/build/index.html" ]; then
    echo "✅ Frontend build exists"
else
    echo "❌ Frontend build missing!"
fi
echo ""

# Step 2: Check Nginx configuration
echo "STEP 2: Checking Nginx configuration..."
echo "----------------------------------------"

echo "Looking for /api location block in Nginx config..."
NGINX_CONFIG=$(sudo nginx -T 2>/dev/null | grep -A 5 "location /api")
if [ -n "$NGINX_CONFIG" ]; then
    echo "✅ Found /api location block:"
    echo "$NGINX_CONFIG"
else
    echo "❌ NO /api location block found in Nginx config!"
    echo ""
    echo "This is the problem! Nginx doesn't know how to proxy /api requests to backend."
    echo ""
fi
echo ""

# Step 3: Pull latest code
echo "STEP 3: Pulling latest code..."
echo "----------------------------------------"
cd /var/www/acs-clean
git pull origin main
echo "✅ Code updated"
echo ""

# Step 4: Rebuild frontend
echo "STEP 4: Rebuilding frontend..."
echo "----------------------------------------"
cd /var/www/acs-clean/frontend
npm install
npm run build
echo "✅ Frontend rebuilt"
echo ""

# Step 5: Restart backend
echo "STEP 5: Restarting backend..."
echo "----------------------------------------"
cd /var/www/acs-clean/backend
pm2 restart acs-backend
pm2 save
echo "✅ Backend restarted"
echo ""

# Step 6: Check if correct Nginx config exists
echo "STEP 6: Checking Nginx configuration..."
echo "----------------------------------------"

ACTIVE_CONFIG="/etc/nginx/sites-enabled/adcopysurge.com"
if [ -f "$ACTIVE_CONFIG" ]; then
    echo "Found active config: $ACTIVE_CONFIG"

    # Check if it has /api location block
    if grep -q "location /api" "$ACTIVE_CONFIG"; then
        echo "✅ Config has /api location block"
    else
        echo "❌ Config missing /api location block!"
        echo ""
        echo "MANUAL FIX NEEDED:"
        echo "1. Copy the new nginx-fullstack.conf to /etc/nginx/sites-available/adcopysurge.com"
        echo "2. Run: sudo nginx -t"
        echo "3. Run: sudo systemctl reload nginx"
    fi
else
    echo "❌ No active Nginx config found at $ACTIVE_CONFIG"
    echo ""
    echo "Available configs:"
    ls -l /etc/nginx/sites-available/ | grep adcopysurge || echo "None found"
fi
echo ""

# Step 7: Test endpoints
echo "STEP 7: Testing endpoints..."
echo "----------------------------------------"

echo "Testing backend directly..."
curl -s -o /dev/null -w "HTTP %{http_code}\n" http://localhost:8000/health

echo "Testing backend API endpoint..."
curl -s -o /dev/null -w "HTTP %{http_code}\n" http://localhost:8000/api/credits/costs

echo "Testing through Nginx (if configured)..."
curl -s -o /dev/null -w "HTTP %{http_code}\n" https://adcopysurge.com/api/credits/costs || echo "Failed (expected if Nginx not configured yet)"

echo ""
echo "=========================================="
echo "Fix Complete"
echo "=========================================="
echo ""

echo "NEXT STEPS:"
echo "1. Check the diagnostic output above"
echo "2. If Nginx config is missing /api block:"
echo "   - Use nginx-fullstack.conf as template"
echo "   - Update /etc/nginx/sites-available/adcopysurge.com"
echo "   - Test with: sudo nginx -t"
echo "   - Reload with: sudo systemctl reload nginx"
echo "3. Test in browser: https://adcopysurge.com/analysis/new"
echo ""
echo "For more help, check DEPLOYMENT_STEPS.md"
