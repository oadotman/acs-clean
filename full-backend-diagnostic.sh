#!/bin/bash
# Complete backend diagnostic

echo "=========================================="
echo "Complete Backend Diagnostic"
echo "=========================================="
echo ""

echo "1. PM2 Status..."
echo "----------------------------------------"
pm2 describe acs-backend
echo ""

echo "2. Backend logs (last 50 lines)..."
echo "----------------------------------------"
pm2 logs acs-backend --lines 50 --nostream
echo ""

echo "3. Test backend endpoints..."
echo "----------------------------------------"

echo "Test: GET /health"
curl -s -w "\nHTTP: %{http_code}\n" http://localhost:8000/health
echo ""

echo "Test: GET /"
curl -s -w "\nHTTP: %{http_code}\n" http://localhost:8000/
echo ""

echo "Test: GET /api/credits/costs"
curl -s -w "\nHTTP: %{http_code}\n" http://localhost:8000/api/credits/costs
echo ""

echo "Test: GET /api/credits/balance (needs auth)"
curl -s -w "\nHTTP: %{http_code}\n" http://localhost:8000/api/credits/balance
echo ""

echo "4. Check if main_production.py has credit routes..."
echo "----------------------------------------"
grep -n "credits" /var/www/acs-clean/backend/main_production.py
echo ""

echo "5. Check if credits router file exists..."
echo "----------------------------------------"
ls -la /var/www/acs-clean/backend/app/api/credits.py 2>&1
echo ""

echo "6. Check Python process..."
echo "----------------------------------------"
ps aux | grep "[p]ython.*main_production"
echo ""

echo "7. Check for Python errors..."
echo "----------------------------------------"
pm2 logs acs-backend --err --lines 20 --nostream
echo ""

echo "8. Try starting backend manually to see errors..."
echo "----------------------------------------"
cd /var/www/acs-clean/backend
source venv/bin/activate 2>&1
python3 -c "
import sys
sys.path.insert(0, '/var/www/acs-clean/backend')
try:
    from main_production import app
    print('✅ App imported successfully')
    print(f'✅ App has {len(app.routes)} routes')

    # List all routes
    print('\nRegistered routes:')
    for route in app.routes:
        print(f'  {route.path}')
except Exception as e:
    print(f'❌ Error importing app: {e}')
    import traceback
    traceback.print_exc()
"
echo ""

echo "=========================================="
echo "Diagnostic Complete"
echo "=========================================="
