#!/bin/bash
# Check what routes the backend actually has

echo "=========================================="
echo "Backend Route Diagnostics"
echo "=========================================="
echo ""

echo "1. Check if backend is running..."
echo "----------------------------------------"
pm2 describe acs-backend | grep -E "status|restarts|uptime" || echo "Backend not running"
echo ""

echo "2. Test backend health endpoint..."
echo "----------------------------------------"
curl -s http://localhost:8000/health
echo ""
echo ""

echo "3. Test backend root endpoint..."
echo "----------------------------------------"
curl -s http://localhost:8000/
echo ""
echo ""

echo "4. Check if OpenAPI docs are available..."
echo "----------------------------------------"
curl -s http://localhost:8000/api/docs 2>&1 | head -c 200
echo ""
echo ""

echo "5. Try to get OpenAPI JSON..."
echo "----------------------------------------"
curl -s http://localhost:8000/api/openapi.json 2>&1 | head -c 500
echo ""
echo ""

echo "6. Test various credit endpoints..."
echo "----------------------------------------"

echo "Test: GET /api/credits/balance"
curl -s -w "\nHTTP: %{http_code}\n" http://localhost:8000/api/credits/balance
echo ""

echo "Test: GET /api/credits/costs"
curl -s -w "\nHTTP: %{http_code}\n" http://localhost:8000/api/credits/costs
echo ""

echo "Test: GET /credits/balance (without /api prefix)"
curl -s -w "\nHTTP: %{http_code}\n" http://localhost:8000/credits/balance
echo ""

echo "Test: GET /credits/costs (without /api prefix)"
curl -s -w "\nHTTP: %{http_code}\n" http://localhost:8000/credits/costs
echo ""

echo "7. Check PM2 logs for errors..."
echo "----------------------------------------"
pm2 logs acs-backend --lines 30 --nostream
echo ""

echo "8. Check what Python process is running..."
echo "----------------------------------------"
ps aux | grep python | grep -v grep
echo ""

echo "9. Check backend working directory..."
echo "----------------------------------------"
pm2 describe acs-backend | grep -E "cwd|script|exec mode"
echo ""

echo "=========================================="
echo "Diagnostics Complete"
echo "=========================================="
echo ""
echo "Analysis:"
echo "- If routes work without /api prefix, backend routes are mounted at root"
echo "- If routes work with /api prefix, backend routes include /api"
echo "- If nothing works, backend might be crashed or wrong file is running"
