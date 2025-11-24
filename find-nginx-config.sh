#!/bin/bash
# Find the actual Nginx configuration file

echo "=========================================="
echo "Finding Nginx Configuration"
echo "=========================================="
echo ""

echo "1. Checking sites-available..."
echo "----------------------------------------"
ls -la /etc/nginx/sites-available/ 2>/dev/null || echo "Directory doesn't exist or is empty"
echo ""

echo "2. Checking sites-enabled..."
echo "----------------------------------------"
ls -la /etc/nginx/sites-enabled/ 2>/dev/null || echo "Directory doesn't exist or is empty"
echo ""

echo "3. Finding all .conf files in nginx directory..."
echo "----------------------------------------"
find /etc/nginx -name "*.conf" -type f 2>/dev/null
echo ""

echo "4. Checking main nginx.conf for included files..."
echo "----------------------------------------"
sudo grep -E "include|server_name.*adcopysurge" /etc/nginx/nginx.conf 2>/dev/null || echo "Not found in nginx.conf"
echo ""

echo "5. Searching for adcopysurge in all nginx configs..."
echo "----------------------------------------"
sudo grep -r "adcopysurge" /etc/nginx/ 2>/dev/null | grep -v "#" | head -20
echo ""

echo "6. Checking nginx -T output for adcopysurge..."
echo "----------------------------------------"
sudo nginx -T 2>/dev/null | grep -A 20 "server_name.*adcopysurge" | head -40
echo ""

echo "=========================================="
echo "Active Configuration Summary"
echo "=========================================="
echo ""

echo "Full active configuration with /api location:"
sudo nginx -T 2>/dev/null | grep -B 5 -A 15 "location /api"
