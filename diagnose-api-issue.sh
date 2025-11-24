#!/bin/bash
# Diagnostic script to find API routing issues

echo "=========================================="
echo "AdCopySurge API Diagnostics"
echo "=========================================="
echo ""

echo "1. NGINX Configuration Check"
echo "----------------------------------------"
echo "Checking if /api location block exists..."
if sudo grep -A 10 "location /api" /etc/nginx/sites-enabled/adcopysurge* 2>/dev/null; then
    echo "✅ Found /api location block"
else
    echo "❌ NO /api location block found!"
fi
echo ""

echo "2. Backend Status Check"
echo "----------------------------------------"
pm2 describe acs-backend 2>/dev/null || echo "❌ Backend not running in PM2!"
echo ""

echo "3. Backend Port Check"
echo "----------------------------------------"
echo "Checking if backend is listening on port 8000..."
sudo netstat -tlnp | grep :8000 || echo "❌ Nothing listening on port 8000!"
echo ""

echo "4. Direct Backend Test"
echo "----------------------------------------"
echo "Testing backend health endpoint..."
curl -s http://localhost:8000/health || echo "❌ Backend health check failed!"
echo ""

echo "Testing backend API endpoint..."
curl -s http://localhost:8000/api/credits/costs || echo "❌ Backend API test failed!"
echo ""

echo "5. Frontend Build Check"
echo "----------------------------------------"
if [ -d "/var/www/acs-clean/frontend/build" ]; then
    echo "✅ Frontend build directory exists"
    ls -lh /var/www/acs-clean/frontend/build/index.html 2>/dev/null || echo "❌ No index.html in build!"
else
    echo "❌ Frontend build directory missing!"
fi
echo ""

echo "6. PM2 Logs (last 20 lines)"
echo "----------------------------------------"
pm2 logs acs-backend --lines 20 --nostream 2>/dev/null || echo "❌ Cannot read PM2 logs!"
echo ""

echo "7. Test API Through Nginx"
echo "----------------------------------------"
echo "Testing /api/credits/costs through Nginx..."
curl -I -s https://adcopysurge.com/api/credits/costs 2>/dev/null | head -5 || echo "❌ Nginx API test failed!"
echo ""

echo "=========================================="
echo "Diagnostics Complete"
echo "=========================================="
