#!/bin/bash

echo "🔧 Fixing REACT_APP_API_URL Configuration"
echo "=========================================="

cd /var/www/acs-clean/frontend

# Backup current .env
echo "📦 Backing up current .env..."
cp .env .env.backup.$(date +%Y%m%d_%H%M%S)

# Fix the API URL (remove /api suffix)
echo "🔨 Fixing REACT_APP_API_URL..."
sed -i 's|REACT_APP_API_URL=https://adcopysurge.com/api|REACT_APP_API_URL=https://adcopysurge.com|g' .env

# Show the change
echo ""
echo "✅ Updated .env file:"
grep REACT_APP_API_URL .env

# Clean build artifacts
echo ""
echo "🧹 Cleaning build artifacts..."
rm -rf build
rm -rf node_modules/.cache

# Rebuild frontend
echo ""
echo "🔨 Rebuilding frontend..."
export GENERATE_SOURCEMAP=false
npm run build

# Restart backend
echo ""
echo "🔄 Restarting backend..."
cd /var/www/acs-clean/backend
pm2 restart acs-backend

# Reload nginx
echo ""
echo "🔄 Reloading nginx..."
nginx -s reload

echo ""
echo "=========================================="
echo "✅ Fix Applied Successfully!"
echo ""
echo "The URLs are now:"
echo "  ❌ OLD: https://adcopysurge.com/api/api/team/invite"
echo "  ✅ NEW: https://adcopysurge.com/api/team/invite"
echo ""
echo "Clear your browser cache and try again!"
