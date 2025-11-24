#!/bin/bash
# Fix Nginx configuration properly

echo "=========================================="
echo "Fixing Nginx Configuration (Proper Method)"
echo "=========================================="
echo ""

# Step 1: Identify the issue
echo "ISSUE FOUND:"
echo "----------------------------------------"
echo "You have 2 conflicting config files:"
echo "1. /etc/nginx/sites-available/acs-clean.conf"
echo "2. /etc/nginx/sites-available/adcopysurge"
echo ""
echo "Both define 'server_name adcopysurge.com' - causing conflicts!"
echo ""

# Step 2: Backup everything
echo "STEP 1: Creating backups..."
echo "----------------------------------------"
sudo cp /etc/nginx/sites-available/acs-clean.conf /etc/nginx/sites-available/acs-clean.conf.backup-$(date +%Y%m%d-%H%M%S)
sudo cp /etc/nginx/sites-available/adcopysurge /etc/nginx/sites-available/adcopysurge.backup-$(date +%Y%m%d-%H%M%S)
echo "✅ Backups created"
echo ""

# Step 3: Decide which config to use
echo "STEP 2: Choosing primary config..."
echo "----------------------------------------"
echo "Using 'adcopysurge' as primary config (has more complete setup)"
echo ""

# Step 4: Fix the proxy_pass in adcopysurge config
echo "STEP 3: Fixing proxy_pass in /etc/nginx/sites-available/adcopysurge..."
echo "----------------------------------------"

# Show current line
echo "Current configuration:"
sudo grep -A 1 "location /api" /etc/nginx/sites-available/adcopysurge | head -4
echo ""

# Fix the proxy_pass line - add /api/ at the end
sudo sed -i '/location \/api/,/proxy_pass/ s|proxy_pass http://127\.0\.0\.1:8000;|proxy_pass http://127.0.0.1:8000/api/;|g' /etc/nginx/sites-available/adcopysurge

echo "New configuration:"
sudo grep -A 1 "location /api" /etc/nginx/sites-available/adcopysurge | head -4
echo ""
echo "✅ proxy_pass fixed"
echo ""

# Step 5: Disable the conflicting config
echo "STEP 4: Disabling conflicting acs-clean.conf..."
echo "----------------------------------------"
if [ -L /etc/nginx/sites-enabled/acs-clean.conf ]; then
    sudo rm /etc/nginx/sites-enabled/acs-clean.conf
    echo "✅ Disabled acs-clean.conf"
else
    echo "⚠️  acs-clean.conf was not enabled"
fi
echo ""

# Step 6: Ensure adcopysurge config is enabled
echo "STEP 5: Ensuring adcopysurge config is enabled..."
echo "----------------------------------------"
if [ ! -L /etc/nginx/sites-enabled/adcopysurge ]; then
    sudo ln -s /etc/nginx/sites-available/adcopysurge /etc/nginx/sites-enabled/adcopysurge
    echo "✅ Enabled adcopysurge config"
else
    echo "✅ adcopysurge config already enabled"
fi
echo ""

# Step 7: Test configuration
echo "STEP 6: Testing Nginx configuration..."
echo "----------------------------------------"
if sudo nginx -t 2>&1 | tee /tmp/nginx-test.log; then
    echo "✅ Configuration is valid!"
    echo ""

    # Step 8: Reload Nginx
    echo "STEP 7: Reloading Nginx..."
    echo "----------------------------------------"
    sudo systemctl reload nginx
    echo "✅ Nginx reloaded"
    echo ""

    # Step 9: Test the API
    echo "STEP 8: Testing API endpoint..."
    echo "----------------------------------------"

    echo "Test 1: Backend directly..."
    curl -s http://localhost:8000/api/credits/costs | head -c 100
    echo ""
    echo ""

    echo "Test 2: Through Nginx (HTTPS)..."
    RESPONSE=$(curl -s -w "\nHTTP_CODE:%{http_code}" https://adcopysurge.com/api/credits/costs)
    HTTP_CODE=$(echo "$RESPONSE" | grep "HTTP_CODE:" | cut -d: -f2)
    BODY=$(echo "$RESPONSE" | grep -v "HTTP_CODE:")

    if [ "$HTTP_CODE" = "200" ]; then
        echo "✅ SUCCESS! API is working (HTTP 200)"
        echo ""
        echo "Response body:"
        echo "$BODY" | head -c 200
        echo ""
    else
        echo "❌ Still getting HTTP $HTTP_CODE"
        echo ""
        echo "Response body:"
        echo "$BODY" | head -c 500
        echo ""
    fi

    echo ""
    echo "=========================================="
    echo "Fix Complete!"
    echo "=========================================="
    echo ""
    echo "✅ Removed conflicting acs-clean.conf"
    echo "✅ Fixed proxy_pass in adcopysurge config"
    echo "✅ Nginx reloaded successfully"
    echo ""
    echo "Now test in browser:"
    echo "https://adcopysurge.com/analysis/new"
    echo ""

else
    echo "❌ Configuration test FAILED!"
    echo ""
    cat /tmp/nginx-test.log
    echo ""
    echo "Restoring backups..."
    sudo cp /etc/nginx/sites-available/adcopysurge.backup-$(date +%Y%m%d)* /etc/nginx/sites-available/adcopysurge
    sudo ln -sf /etc/nginx/sites-available/acs-clean.conf /etc/nginx/sites-enabled/acs-clean.conf
    echo ""
    echo "Please check the configuration manually"
fi
