#!/bin/bash
# Production 502 Error Diagnostic and Fix Script
# Run this on your VPS to diagnose and fix the analysis 502 error

set -e  # Exit on error

echo "=========================================="
echo "AdCopySurge Production 502 Diagnostic"
echo "=========================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Step 1: Check if backend service is running
echo -e "${YELLOW}[1/8] Checking backend service status...${NC}"
if systemctl is-active --quiet adcopysurge; then
    echo -e "${GREEN}✓ Backend service is running${NC}"
else
    echo -e "${RED}✗ Backend service is NOT running!${NC}"
    echo "Starting backend service..."
    sudo systemctl start adcopysurge
    sleep 3
    if systemctl is-active --quiet adcopysurge; then
        echo -e "${GREEN}✓ Backend service started${NC}"
    else
        echo -e "${RED}✗ Failed to start backend service${NC}"
        echo "Check logs: sudo journalctl -u adcopysurge -n 50"
        exit 1
    fi
fi
echo ""

# Step 2: Check Gunicorn processes
echo -e "${YELLOW}[2/8] Checking Gunicorn worker processes...${NC}"
WORKERS=$(ps aux | grep -E "gunicorn.*main_production" | grep -v grep | wc -l)
if [ "$WORKERS" -gt 0 ]; then
    echo -e "${GREEN}✓ Found $WORKERS Gunicorn worker(s)${NC}"
    ps aux | grep -E "gunicorn.*main_production" | grep -v grep | head -5
else
    echo -e "${RED}✗ No Gunicorn workers found!${NC}"
    echo "Backend may have crashed. Check error logs."
fi
echo ""

# Step 3: Check current Gunicorn timeout setting
echo -e "${YELLOW}[3/8] Checking current Gunicorn timeout...${NC}"
BACKEND_DIR="/opt/adcopysurge/backend"
if [ -f "$BACKEND_DIR/gunicorn.conf.py" ]; then
    CURRENT_TIMEOUT=$(grep -E "^timeout\s*=" "$BACKEND_DIR/gunicorn.conf.py" | head -1)
    echo "Current setting: $CURRENT_TIMEOUT"

    if echo "$CURRENT_TIMEOUT" | grep -q "timeout = 180"; then
        echo -e "${GREEN}✓ Timeout is correctly set to 180 seconds${NC}"
    else
        echo -e "${RED}✗ Timeout is NOT set to 180 seconds${NC}"
        echo "This is likely causing the 502 errors!"
    fi
else
    echo -e "${RED}✗ gunicorn.conf.py not found at $BACKEND_DIR${NC}"
fi
echo ""

# Step 4: Check recent error logs
echo -e "${YELLOW}[4/8] Checking recent error logs...${NC}"
if [ -f "/var/log/adcopysurge/error.log" ]; then
    echo "Last 10 error log entries:"
    tail -10 /var/log/adcopysurge/error.log
else
    echo "Error log not found, checking journalctl..."
    sudo journalctl -u adcopysurge -n 10 --no-pager
fi
echo ""

# Step 5: Check for worker timeout errors
echo -e "${YELLOW}[5/8] Searching for timeout-related errors...${NC}"
TIMEOUT_ERRORS=$(sudo journalctl -u adcopysurge --since "1 hour ago" | grep -i "timeout\|worker.*signal\|502" | wc -l)
if [ "$TIMEOUT_ERRORS" -gt 0 ]; then
    echo -e "${RED}✗ Found $TIMEOUT_ERRORS timeout-related errors in last hour${NC}"
    echo "Recent timeout errors:"
    sudo journalctl -u adcopysurge --since "1 hour ago" | grep -i "timeout\|worker.*signal" | tail -5
else
    echo -e "${GREEN}✓ No timeout errors found in last hour${NC}"
fi
echo ""

# Step 6: Check Nginx configuration
echo -e "${YELLOW}[6/8] Checking Nginx proxy timeout...${NC}"
NGINX_TIMEOUT=$(grep -r "proxy_read_timeout" /etc/nginx/sites-enabled/ | head -1)
if [ -n "$NGINX_TIMEOUT" ]; then
    echo "Nginx timeout: $NGINX_TIMEOUT"
    if echo "$NGINX_TIMEOUT" | grep -q "300"; then
        echo -e "${GREEN}✓ Nginx timeout is set to 300s (good)${NC}"
    else
        echo -e "${YELLOW}⚠ Nginx timeout may need adjustment${NC}"
    fi
else
    echo -e "${YELLOW}⚠ Could not find proxy_read_timeout in Nginx config${NC}"
fi
echo ""

# Step 7: Test backend health endpoint
echo -e "${YELLOW}[7/8] Testing backend health endpoint...${NC}"
HEALTH_RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:8000/health 2>/dev/null || echo "failed")
if [ "$HEALTH_RESPONSE" = "200" ]; then
    echo -e "${GREEN}✓ Backend health check passed (200)${NC}"
    curl -s http://127.0.0.1:8000/health | python3 -m json.tool 2>/dev/null || echo "Response received but not JSON"
elif [ "$HEALTH_RESPONSE" = "failed" ]; then
    echo -e "${RED}✗ Cannot connect to backend on port 8000${NC}"
    echo "Backend may not be listening or is crashed"
else
    echo -e "${RED}✗ Health check returned: $HEALTH_RESPONSE${NC}"
fi
echo ""

# Step 8: Summary and recommendations
echo -e "${YELLOW}[8/8] Summary and Recommendations${NC}"
echo "=========================================="

# Determine if timeout fix is needed
NEEDS_TIMEOUT_FIX=false
if [ -f "$BACKEND_DIR/gunicorn.conf.py" ]; then
    if ! grep -q "timeout = 180" "$BACKEND_DIR/gunicorn.conf.py"; then
        NEEDS_TIMEOUT_FIX=true
    fi
fi

if [ "$NEEDS_TIMEOUT_FIX" = true ]; then
    echo -e "${RED}ACTION REQUIRED: Deploy timeout fix${NC}"
    echo ""
    echo "The Gunicorn timeout is too low and causing 502 errors."
    echo "To fix, run these commands:"
    echo ""
    echo "  cd $BACKEND_DIR"
    echo "  git pull origin main"
    echo "  sudo systemctl restart adcopysurge"
    echo "  sudo systemctl status adcopysurge"
    echo ""
elif [ "$WORKERS" -eq 0 ]; then
    echo -e "${RED}ACTION REQUIRED: Backend is not running${NC}"
    echo ""
    echo "  sudo systemctl restart adcopysurge"
    echo "  sudo journalctl -u adcopysurge -f"
    echo ""
elif [ "$HEALTH_RESPONSE" != "200" ]; then
    echo -e "${RED}ACTION REQUIRED: Backend health check failing${NC}"
    echo ""
    echo "  sudo systemctl restart adcopysurge"
    echo "  sudo journalctl -u adcopysurge -n 50"
    echo ""
else
    echo -e "${GREEN}✓ System looks healthy!${NC}"
    echo ""
    echo "If 502 errors persist:"
    echo "  1. Check frontend logs in browser console"
    echo "  2. Monitor: sudo tail -f /var/log/adcopysurge/error.log"
    echo "  3. Test analysis with: curl -X POST https://adcopysurge.com/api/ads/analyze"
fi

echo ""
echo "=========================================="
echo "Diagnostic complete!"
echo "=========================================="
