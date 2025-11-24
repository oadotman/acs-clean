#!/bin/bash
# Install gunicorn and fix the service

set -e

echo "=== Installing Gunicorn and Fixing Service ==="

# Step 1: Activate venv and install gunicorn
echo "1. Installing gunicorn in venv..."
cd /var/www/acs-clean/backend
source /var/www/acs-clean/venv/bin/activate

# Install gunicorn with uvicorn worker
pip install gunicorn uvicorn[standard]

# Verify installation
if [ -f "/var/www/acs-clean/venv/bin/gunicorn" ]; then
    echo "   ✓ Gunicorn installed successfully"
    /var/www/acs-clean/venv/bin/gunicorn --version
else
    echo "   ✗ Gunicorn installation failed!"
    exit 1
fi

# Step 2: Verify gunicorn.conf.py exists and has correct timeout
echo "2. Checking gunicorn configuration..."
if [ -f "/var/www/acs-clean/backend/gunicorn.conf.py" ]; then
    TIMEOUT=$(grep "^timeout" /var/www/acs-clean/backend/gunicorn.conf.py | head -1)
    echo "   Current timeout: $TIMEOUT"

    if echo "$TIMEOUT" | grep -q "180"; then
        echo "   ✓ Timeout is correctly set to 180 seconds"
    else
        echo "   ⚠ WARNING: Timeout is not 180 seconds!"
        echo "   You need to pull the latest code or manually set timeout = 180"
    fi
else
    echo "   ✗ gunicorn.conf.py not found!"
    echo "   Creating basic gunicorn.conf.py..."

    cat > /var/www/acs-clean/backend/gunicorn.conf.py << 'GUNICORN_CONF'
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

# Process naming
proc_name = "adcopysurge-backend"
GUNICORN_CONF

    echo "   ✓ Created gunicorn.conf.py with 180s timeout"
fi

# Step 3: Create log directory
echo "3. Creating log directory..."
sudo mkdir -p /var/log/adcopysurge
sudo chown www-data:www-data /var/log/adcopysurge
echo "   ✓ Log directory created"

# Step 4: Fix systemd service file
echo "4. Updating systemd service file..."
sudo tee /etc/systemd/system/adcopysurge.service > /dev/null << 'EOF'
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
EOF
echo "   ✓ Service file updated"

# Step 5: Reload systemd
echo "5. Reloading systemd..."
sudo systemctl daemon-reload
echo "   ✓ Systemd reloaded"

# Step 6: Start the service
echo "6. Starting AdCopySurge service..."
sudo systemctl enable adcopysurge
sudo systemctl restart adcopysurge

# Wait for startup
sleep 3

# Step 7: Check status
echo "7. Checking service status..."
if sudo systemctl is-active --quiet adcopysurge; then
    echo "   ✓ Service is RUNNING!"
    echo ""
    sudo systemctl status adcopysurge --no-pager | head -20
    echo ""
    echo "=== SUCCESS! ==="
    echo "Backend is now running with Gunicorn and 180s timeout"
else
    echo "   ✗ Service FAILED to start"
    echo ""
    echo "Service status:"
    sudo systemctl status adcopysurge --no-pager
    echo ""
    echo "Recent error logs:"
    sudo journalctl -u adcopysurge -n 50 --no-pager
    exit 1
fi

echo ""
echo "Next steps:"
echo "  1. Test: https://adcopysurge.com"
echo "  2. Monitor: sudo journalctl -u adcopysurge -f"
