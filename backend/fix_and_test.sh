#!/bin/bash
set -e  # Exit on any error

echo "==========================================="
echo "AdCopySurge Backend End-to-End Fix & Test"
echo "==========================================="
echo ""

# Step 1: Check current status
echo "Step 1: Current PM2 status"
pm2 list

# Step 2: Stop backend
echo ""
echo "Step 2: Stopping backend..."
pm2 stop acs-backend || true

# Step 3: Activate venv and install missing packages
echo ""
echo "Step 3: Installing Python dependencies..."
cd /var/www/acs-clean/backend
source venv/bin/activate

echo "Installing resend..."
pip install resend==0.7.0

echo "Installing jinja2..."
pip install jinja2>=3.1.2

echo "Installing supabase..."
pip install supabase

echo "Verifying all critical imports..."
python -c "import fastapi; print('✓ fastapi')"
python -c "import uvicorn; print('✓ uvicorn')"
python -c "import supabase; print('✓ supabase')"
python -c "import resend; print('✓ resend')"
python -c "import jinja2; print('✓ jinja2')"
python -c "from pydantic_settings import BaseSettings; print('✓ pydantic_settings')"
python -c "from pydantic import BaseModel, Field; print('✓ pydantic')"

# Step 4: Test import of main application
echo ""
echo "Step 4: Testing main application import..."
python -c "
import sys
sys.path.insert(0, '/var/www/acs-clean/backend')
try:
    from app.routers import team, support
    print('✓ Routers imported successfully')
    from app.services.email_service import EmailService
    print('✓ Email service imported successfully')
    from app.core.config import settings
    print('✓ Settings loaded successfully')
    print('  - RESEND_API_KEY configured:', bool(settings.RESEND_API_KEY))
    print('  - SUPABASE_URL configured:', bool(settings.REACT_APP_SUPABASE_URL))
except Exception as e:
    print('✗ Import failed:', str(e))
    import traceback
    traceback.print_exc()
    sys.exit(1)
"

# Step 5: Test full main.py import
echo ""
echo "Step 5: Testing full main.py import..."
python -c "
import sys
sys.path.insert(0, '/var/www/acs-clean/backend')
try:
    import main
    print('✓ Main application loaded successfully')
except Exception as e:
    print('✗ Main import failed:', str(e))
    import traceback
    traceback.print_exc()
    sys.exit(1)
"

# Step 6: Start backend via PM2
echo ""
echo "Step 6: Starting backend via PM2..."
cd /var/www/acs-clean/backend
pm2 restart acs-backend

# Step 7: Wait and check if server is running
echo ""
echo "Step 7: Waiting for server startup (10 seconds)..."
sleep 10

echo ""
echo "Checking PM2 status..."
pm2 list

# Step 8: Test health endpoint
echo ""
echo "Step 8: Testing health endpoint..."
for i in {1..5}; do
    echo "Attempt $i/5..."
    if curl -s http://localhost:8000/health > /dev/null 2>&1; then
        echo "✓ Health check passed!"
        curl http://localhost:8000/health | python -m json.tool
        break
    else
        echo "  Server not responding yet..."
        if [ $i -eq 5 ]; then
            echo "✗ Health check failed after 5 attempts"
            echo ""
            echo "Checking PM2 logs for errors..."
            pm2 logs acs-backend --lines 50 --nostream
            exit 1
        fi
        sleep 2
    fi
done

# Step 9: Test API endpoints
echo ""
echo "Step 9: Testing API endpoints..."

echo "Testing root endpoint..."
curl -s http://localhost:8000/ | python -m json.tool

echo ""
echo "Testing team invitation endpoint (OPTIONS for CORS)..."
curl -X OPTIONS -s http://localhost:8000/api/team/invite -H "Access-Control-Request-Method: POST"

echo ""
echo "Testing support endpoint (OPTIONS for CORS)..."
curl -X OPTIONS -s http://localhost:8000/api/support/send -H "Access-Control-Request-Method: POST"

# Success
echo ""
echo "==========================================="
echo "✓ All checks passed!"
echo "==========================================="
echo ""
echo "Backend is running and healthy."
echo "- Health: http://localhost:8000/health"
echo "- Team API: http://localhost:8000/api/team/invite"
echo "- Support API: http://localhost:8000/api/support/send"
echo ""
echo "To view logs: pm2 logs acs-backend"
echo "To monitor: pm2 monit"
