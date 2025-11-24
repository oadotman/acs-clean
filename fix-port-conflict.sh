#!/bin/bash
# Fix the port 8000 conflict by killing old Gunicorn

echo "=========================================="
echo "Fixing Port 8000 Conflict"
echo "=========================================="
echo ""

echo "PROBLEM FOUND:"
echo "----------------------------------------"
echo "Old Gunicorn process (started Nov 22) is holding port 8000"
echo "PM2 can't start because port is already in use"
echo "Gunicorn is running OLD CODE without credit routes"
echo ""

echo "STEP 1: Stop PM2 backend..."
echo "----------------------------------------"
pm2 stop acs-backend
echo "✅ PM2 stopped"
echo ""

echo "STEP 2: Kill all Gunicorn processes..."
echo "----------------------------------------"
ps aux | grep "[g]unicorn.*main_production"
echo ""
echo "Killing processes..."
sudo pkill -f "gunicorn.*main_production"
sleep 2
echo ""

# Verify they're dead
REMAINING=$(ps aux | grep "[g]unicorn.*main_production" | wc -l)
if [ "$REMAINING" -eq 0 ]; then
    echo "✅ All Gunicorn processes killed"
else
    echo "⚠️  Some processes still running, forcing kill..."
    sudo pkill -9 -f "gunicorn.*main_production"
    sleep 1
fi
echo ""

echo "STEP 3: Verify port 8000 is free..."
echo "----------------------------------------"
PORT_CHECK=$(sudo netstat -tlnp | grep :8000 || echo "")
if [ -z "$PORT_CHECK" ]; then
    echo "✅ Port 8000 is now free"
else
    echo "❌ Port 8000 still in use:"
    sudo netstat -tlnp | grep :8000
    echo ""
    echo "Finding process..."
    sudo lsof -i :8000
    echo ""
    echo "You may need to manually kill: sudo kill -9 <PID>"
    exit 1
fi
echo ""

echo "STEP 4: Start PM2 backend with fresh code..."
echo "----------------------------------------"
cd /var/www/acs-clean/backend
pm2 start acs-backend
sleep 3
pm2 describe acs-backend | grep -E "status|restarts|uptime"
echo ""

echo "STEP 5: Test backend endpoints..."
echo "----------------------------------------"

echo "Test: GET /health"
curl -s http://localhost:8000/health
echo ""
echo ""

echo "Test: GET /api/credits/costs"
RESPONSE=$(curl -s -w "\nHTTP:%{http_code}" http://localhost:8000/api/credits/costs)
echo "$RESPONSE"
echo ""

if echo "$RESPONSE" | grep -q "HTTP:200"; then
    echo "✅ SUCCESS! Credit routes are working!"
else
    echo "❌ Still getting 404"
    echo ""
    echo "Checking PM2 logs for errors..."
    pm2 logs acs-backend --lines 20 --nostream
fi
echo ""

echo "=========================================="
echo "Fix Complete"
echo "=========================================="
echo ""
echo "If successful, test in browser:"
echo "https://adcopysurge.com/analysis/new"
