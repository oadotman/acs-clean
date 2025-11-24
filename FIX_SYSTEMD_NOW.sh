#!/bin/bash
# Fix the broken systemd service file and switch to gunicorn with proper timeout

echo "=== Fixing AdCopySurge Systemd Service ==="

# Backup the broken file
echo "1. Backing up broken service file..."
sudo cp /etc/systemd/system/adcopysurge.service /etc/systemd/system/adcopysurge.service.broken
echo "   Backup saved to: adcopysurge.service.broken"

# Create the correct service file
echo "2. Creating corrected service file..."
sudo tee /etc/systemd/system/adcopysurge.service > /dev/null << 'EOF'
[Unit]
Description=AdCopySurge FastAPI Application
After=network.target postgresql.service redis.service

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

echo "   ✓ Service file created"

# Reload systemd
echo "3. Reloading systemd daemon..."
sudo systemctl daemon-reload
echo "   ✓ Systemd reloaded"

# Check if the file loads correctly
echo "4. Verifying service file loads correctly..."
if sudo systemctl status adcopysurge 2>&1 | grep -q "Loaded: loaded"; then
    echo "   ✓ Service file loads correctly"
else
    echo "   ✗ Service file has errors:"
    sudo systemctl status adcopysurge 2>&1 | grep -i "error\|loaded"
    exit 1
fi

# Start the service
echo "5. Starting AdCopySurge service..."
sudo systemctl start adcopysurge

# Wait a moment for startup
sleep 3

# Check status
echo "6. Checking service status..."
if sudo systemctl is-active --quiet adcopysurge; then
    echo "   ✓ Service is running!"
    sudo systemctl status adcopysurge --no-pager | head -15
else
    echo "   ✗ Service failed to start"
    echo ""
    echo "Recent logs:"
    sudo journalctl -u adcopysurge -n 30 --no-pager
    exit 1
fi

# Enable auto-start
echo "7. Enabling auto-start on boot..."
sudo systemctl enable adcopysurge
echo "   ✓ Service enabled"

echo ""
echo "=== SUCCESS! ==="
echo "AdCopySurge backend is now running with:"
echo "  - Gunicorn (not uvicorn)"
echo "  - 180 second timeout (from gunicorn.conf.py)"
echo "  - Proper systemd configuration"
echo ""
echo "Next steps:"
echo "  1. Test analysis: https://adcopysurge.com"
echo "  2. Monitor logs: sudo journalctl -u adcopysurge -f"
echo ""
