#!/bin/bash
# Deployment script to fix API endpoint issues
# Run this on your VPS server

set -e  # Exit on error

echo "=============================================="
echo "AdCopySurge - Fix API Endpoints Deployment"
echo "=============================================="
echo ""

# Navigate to project root
cd /var/www/acs-clean

echo "Step 1: Pull latest changes from repository..."
git pull origin main

echo ""
echo "Step 2: Update frontend environment (if needed)..."
# Ensure REACT_APP_API_URL is correct (no /api suffix)
if grep -q "REACT_APP_API_URL=https://adcopysurge.com/api" frontend/.env; then
    echo "⚠️  Found incorrect API URL with /api suffix - fixing..."
    sed -i 's|REACT_APP_API_URL=https://adcopysurge.com/api|REACT_APP_API_URL=https://adcopysurge.com|g' frontend/.env
    echo "✅ Fixed REACT_APP_API_URL"
else
    echo "✅ REACT_APP_API_URL is already correct"
fi

echo ""
echo "Step 3: Rebuild frontend..."
cd frontend
npm install
npm run build
echo "✅ Frontend built successfully"

echo ""
echo "Step 4: Check PM2 backend status..."
cd /var/www/acs-clean/backend
pm2 describe acs-backend > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "✅ Backend is running"
    pm2 logs acs-backend --lines 20 --nostream
else
    echo "⚠️  Backend is NOT running - attempting to start..."
    pm2 start ecosystem.config.js
fi

echo ""
echo "Step 5: Restart PM2 backend..."
pm2 restart acs-backend
echo "✅ Backend restarted"

echo ""
echo "Step 6: Reload Nginx..."
sudo nginx -t && sudo nginx -s reload
echo "✅ Nginx reloaded"

echo ""
echo "=============================================="
echo "Deployment complete!"
echo "=============================================="
echo ""
echo "Testing endpoints:"
echo "- User Profile: https://adcopysurge.com/api/user/profile"
echo "- Credit Balance: https://adcopysurge.com/api/credits/balance"
echo "- Health Check: https://adcopysurge.com/health"
echo ""
echo "Check PM2 logs: pm2 logs acs-backend"
echo "Check Nginx logs: sudo tail -f /var/log/nginx/error.log"
