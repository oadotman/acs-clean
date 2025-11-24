#!/bin/bash
# Fix PM2 backend startup

echo "=========================================="
echo "Fix PM2 Backend Startup"
echo "=========================================="
echo ""

cd /var/www/acs-clean/backend

echo "STEP 1: Check if uvicorn is installed..."
echo "----------------------------------------"
source venv/bin/activate
python -c "import uvicorn; print('✅ uvicorn installed:', uvicorn.__version__)" 2>&1 || echo "❌ uvicorn not installed"
deactivate
echo ""

echo "STEP 2: Stop current PM2 process..."
echo "----------------------------------------"
pm2 stop acs-backend
pm2 delete acs-backend
echo "✅ Stopped and deleted"
echo ""

echo "STEP 3: Start with correct command..."
echo "----------------------------------------"
echo "Starting backend with uvicorn directly..."

pm2 start venv/bin/uvicorn \
  --name acs-backend \
  --cwd /var/www/acs-clean/backend \
  -- main_production:app \
  --host 0.0.0.0 \
  --port 8000 \
  --workers 1

echo ""
echo "Waiting for startup..."
sleep 5
echo ""

echo "STEP 4: Check status..."
echo "----------------------------------------"
pm2 status
echo ""

echo "STEP 5: Test endpoints..."
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
    echo "✅ SUCCESS! Backend is working!"
    echo ""
    echo "STEP 6: Save PM2 configuration..."
    pm2 save
    echo "✅ Configuration saved"
else
    echo "❌ Still not working. Checking logs..."
    pm2 logs acs-backend --lines 30 --nostream
fi

echo ""
echo "=========================================="
echo "Fix Complete"
echo "=========================================="
echo ""
echo "If successful, test in browser:"
echo "https://adcopysurge.com/analysis/new"
