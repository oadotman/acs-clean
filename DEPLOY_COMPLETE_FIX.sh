#!/bin/bash
# Complete deployment script - fixes all issues and starts service

set -e

echo "==================================================="
echo "AdCopySurge Complete Fix Deployment"
echo "==================================================="
echo ""

# Step 1: Pull latest code
echo "[1/7] Pulling latest code from repository..."
cd /var/www/acs-clean/backend
git stash  # Stash any local changes
git pull origin main || git pull origin clean-security
echo "✓ Code updated"
echo ""

# Step 2: Activate venv and install/upgrade dependencies
echo "[2/7] Installing Python dependencies..."
source /var/www/acs-clean/venv/bin/activate

# Install gunicorn if not present
if ! command -v gunicorn &> /dev/null; then
    echo "Installing gunicorn..."
    pip install gunicorn uvicorn[standard]
else
    echo "Gunicorn already installed:"
    gunicorn --version
fi
echo "✓ Dependencies ready"
echo ""

# Step 3: Test that Python code loads
echo "[3/7] Testing Python code loads without errors..."
cd /var/www/acs-clean/backend
if python3 -c "from app.routers import team; print('✓ team.py loads successfully')"; then
    echo "✓ Python code loads successfully"
else
    echo "✗ Python code has import errors!"
    echo "Check the error above and fix before proceeding"
    exit 1
fi
echo ""

# Step 4: Verify gunicorn.conf.py
echo "[4/7] Checking gunicorn configuration..."
if [ -f "gunicorn.conf.py" ]; then
    TIMEOUT=$(grep "^timeout" gunicorn.conf.py | head -1)
    echo "Found: $TIMEOUT"

    if echo "$TIMEOUT" | grep -q "180"; then
        echo "✓ Timeout correctly set to 180 seconds"
    else
        echo "⚠ WARNING: Timeout not set to 180!"
        echo "Creating/updating gunicorn.conf.py..."

        cat > gunicorn.conf.py << 'GCONF'
import multiprocessing

bind = "0.0.0.0:8000"
workers = min(4, multiprocessing.cpu_count() * 2 + 1)
worker_class = "uvicorn.workers.UvicornWorker"
timeout = 180  # 3 minutes - AI analysis takes 60-120 seconds
keepalive = 2
max_requests = 1000
max_requests_jitter = 50
preload_app = True

# Logging
accesslog = "/var/log/adcopysurge/access.log"
errorlog = "/var/log/adcopysurge/error.log"
loglevel = "info"
proc_name = "adcopysurge-backend"
GCONF
        echo "✓ gunicorn.conf.py created with 180s timeout"
    fi
else
    echo "Creating gunicorn.conf.py..."
    cat > gunicorn.conf.py << 'GCONF'
import multiprocessing

bind = "0.0.0.0:8000"
workers = min(4, multiprocessing.cpu_count() * 2 + 1)
worker_class = "uvicorn.workers.UvicornWorker"
timeout = 180  # 3 minutes - AI analysis takes 60-120 seconds
keepalive = 2
max_requests = 1000
max_requests_jitter = 50
preload_app = True

# Logging
accesslog = "/var/log/adcopysurge/access.log"
errorlog = "/var/log/adcopysurge/error.log"
loglevel = "info"
proc_name = "adcopysurge-backend"
GCONF
    echo "✓ gunicorn.conf.py created"
fi
echo ""

# Step 5: Create log directory
echo "[5/7] Setting up log directory..."
sudo mkdir -p /var/log/adcopysurge
sudo chown www-data:www-data /var/log/adcopysurge
echo "✓ Log directory ready"
echo ""

# Step 6: Update systemd service
echo "[6/7] Updating systemd service configuration..."
sudo tee /etc/systemd/system/adcopysurge.service > /dev/null << 'SERVICE'
[Unit]
Description=AdCopySurge FastAPI Application
After=network.target

[Service]
Type=notify
User=www-data
Group=www-data
WorkingDirectory=/var/www/acs-clean/backend
Environment="PATH=/var/www/acs-clean/venv/bin:/usr/local/bin:/usr/bin:/bin"
Environment="PYTHONPATH=/var/www/acs-clean/backend"
EnvironmentFile=/var/www/acs-clean/backend/.env
ExecStart=/var/www/acs-clean/venv/bin/gunicorn main_production:app --config gunicorn.conf.py
ExecReload=/bin/kill -s HUP $MAINPID
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal
KillMode=mixed
TimeoutStopSec=10
PrivateTmp=true

[Install]
WantedBy=multi-user.target
SERVICE
echo "✓ Systemd service file updated"
echo ""

# Step 7: Start the service
echo "[7/7] Starting AdCopySurge backend service..."
sudo systemctl daemon-reload
sudo systemctl enable adcopysurge
sudo systemctl restart adcopysurge

# Wait for startup
sleep 3

# Check status
echo ""
if sudo systemctl is-active --quiet adcopysurge; then
    echo "==================================================="
    echo "✓✓✓ SUCCESS! Backend is running! ✓✓✓"
    echo "==================================================="
    echo ""
    sudo systemctl status adcopysurge --no-pager | head -20
    echo ""
    echo "Service is RUNNING with:"
    echo "  - Gunicorn (proper worker management)"
    echo "  - 180 second timeout (handles long AI analysis)"
    echo "  - Fixed Python code (no syntax errors)"
    echo ""
    echo "Next steps:"
    echo "  1. Test analysis: https://adcopysurge.com"
    echo "  2. Monitor logs: sudo journalctl -u adcopysurge -f"
    echo ""
else
    echo "==================================================="
    echo "✗ SERVICE FAILED TO START"
    echo "==================================================="
    echo ""
    sudo systemctl status adcopysurge --no-pager
    echo ""
    echo "Error logs:"
    sudo journalctl -u adcopysurge -n 50 --no-pager
    exit 1
fi
