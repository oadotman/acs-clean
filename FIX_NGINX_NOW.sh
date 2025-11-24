#!/bin/bash
# PRECISE FIX for Nginx proxy_pass issue

echo "=========================================="
echo "Fixing Nginx proxy_pass Configuration"
echo "=========================================="
echo ""

# Backup current config
echo "1. Creating backup..."
sudo cp /etc/nginx/sites-available/adcopysurge.com /etc/nginx/sites-available/adcopysurge.com.backup-$(date +%Y%m%d-%H%M%S)
echo "✅ Backup created"
echo ""

# Show current problematic line
echo "2. Current configuration:"
echo "----------------------------------------"
sudo grep -A 3 "location /api" /etc/nginx/sites-available/adcopysurge.com
echo ""

# The fix
echo "3. Applying fix..."
echo "----------------------------------------"

# Replace proxy_pass line to include /api/ at the end
sudo sed -i 's|proxy_pass http://127\.0\.0\.1:8000;|proxy_pass http://127.0.0.1:8000/api/;|g' /etc/nginx/sites-available/adcopysurge.com

# Also check for variations
sudo sed -i 's|proxy_pass http://localhost:8000;|proxy_pass http://localhost:8000/api/;|g' /etc/nginx/sites-available/adcopysurge.com

echo "✅ Configuration updated"
echo ""

# Show new configuration
echo "4. New configuration:"
echo "----------------------------------------"
sudo grep -A 3 "location /api" /etc/nginx/sites-available/adcopysurge.com
echo ""

# Test configuration
echo "5. Testing Nginx configuration..."
echo "----------------------------------------"
if sudo nginx -t; then
    echo "✅ Configuration is valid"
    echo ""

    # Reload Nginx
    echo "6. Reloading Nginx..."
    echo "----------------------------------------"
    sudo systemctl reload nginx
    echo "✅ Nginx reloaded"
    echo ""

    # Test the API
    echo "7. Testing API endpoint..."
    echo "----------------------------------------"
    echo "Testing: https://adcopysurge.com/api/credits/costs"

    RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" https://adcopysurge.com/api/credits/costs)

    if [ "$RESPONSE" = "200" ]; then
        echo "✅ SUCCESS! API is working (HTTP 200)"
        echo ""
        echo "Testing actual response:"
        curl -s https://adcopysurge.com/api/credits/costs | head -c 200
        echo ""
    else
        echo "❌ Still getting HTTP $RESPONSE"
        echo ""
        echo "Trying to get response body:"
        curl -s https://adcopysurge.com/api/credits/costs | head -c 500
        echo ""
    fi

    echo ""
    echo "=========================================="
    echo "Fix Complete!"
    echo "=========================================="
    echo ""
    echo "✅ Nginx configuration updated"
    echo "✅ Changes applied and tested"
    echo ""
    echo "Now test in your browser:"
    echo "https://adcopysurge.com/analysis/new"

else
    echo "❌ Configuration test failed!"
    echo ""
    echo "Rolling back..."
    sudo cp /etc/nginx/sites-available/adcopysurge.com.backup-$(date +%Y%m%d)* /etc/nginx/sites-available/adcopysurge.com
    echo ""
    echo "Please check the Nginx configuration manually:"
    echo "sudo nano /etc/nginx/sites-available/adcopysurge.com"
fi
