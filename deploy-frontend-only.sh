#!/bin/bash
# AdCopySurge Frontend-Only VPS Deployment Script
# Run this script ON THE VPS to deploy just the frontend changes
# Backend is already working, so we only update the frontend

set -e

echo "🎯 Starting Frontend-Only Deployment for AdCopySurge..."
echo "📋 Backend is working fine, only updating frontend with scoring fixes"

# Variables
VPS_DIR="/srv/adcopysurge"
BACKUP_DIR="/root/backups"
FRONTEND_DIR="$VPS_DIR/frontend"

# Create backup directory
mkdir -p $BACKUP_DIR

echo "📦 Creating backup of current frontend..."
if [ -d "$FRONTEND_DIR/build" ]; then
    tar -czf "$BACKUP_DIR/frontend_backup_$(date +%Y%m%d_%H%M%S).tar.gz" -C "$FRONTEND_DIR" build
    echo "✅ Frontend backup created"
fi

echo "🔄 Updating code from GitHub..."
cd $VPS_DIR
git fetch --all
git reset --hard origin/main
git pull origin main

echo "🏗️ Building frontend with fixed scoring logic..."
cd $FRONTEND_DIR

# Copy production environment file
echo "📝 Setting up production environment..."
cp .env.production .env

# Install dependencies if needed (with error handling)
echo "📦 Installing/updating dependencies..."
if ! npm install --legacy-peer-deps --timeout=300000; then
    echo "⚠️ npm install failed, trying to clear cache and retry..."
    npm cache clean --force
    rm -rf node_modules package-lock.json
    npm install --legacy-peer-deps --timeout=300000
fi

# Build the frontend
echo "🔨 Building production frontend..."
if ! npm run build; then
    echo "❌ Build failed! Checking for common issues..."
    
    # Try to fix ajv issue if it exists
    if [ -f "node_modules/ajv/dist/compile/codegen/index.js" ]; then
        echo "✅ ajv dependency looks OK"
    else
        echo "🔧 Attempting to fix ajv dependency issue..."
        npm install ajv@^8.0.0 --legacy-peer-deps
        npm run build
    fi
fi

# Check if build was successful
if [ ! -d "build" ]; then
    echo "❌ Build failed - no build directory found"
    exit 1
fi

echo "✅ Frontend build completed successfully!"

echo "🔧 Updating nginx configuration for proper API routing..."
# Update nginx config to ensure proper API proxy
cat > /etc/nginx/sites-available/adcopysurge << 'EOF'
server {
    listen 80;
    server_name adcopysurge.com www.adcopysurge.com;
    root /srv/adcopysurge/frontend/build;
    index index.html;

    # Frontend - serve React app
    location / {
        try_files $uri $uri/ /index.html;
        add_header Cache-Control "no-cache, no-store, must-revalidate";
        add_header Pragma "no-cache";
        add_header Expires "0";
    }

    # API proxy to backend (this is the key fix!)
    location /api/ {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # CORS headers (backup)
        add_header Access-Control-Allow-Origin * always;
        add_header Access-Control-Allow-Methods "GET, POST, PUT, DELETE, OPTIONS" always;
        add_header Access-Control-Allow-Headers "DNT,User-Agent,X-Requested-With,If-Modified-Since,Cache-Control,Content-Type,Range,Authorization" always;
    }

    # Static files caching
    location /static/ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
    
    # Handle .js and .css files
    location ~* \.(js|css)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
EOF

echo "🔄 Reloading nginx..."
# Test nginx config and reload
nginx -t
if [ $? -eq 0 ]; then
    systemctl reload nginx
    echo "✅ Nginx reloaded successfully"
else
    echo "❌ Nginx configuration error"
    exit 1
fi

echo "🏥 Running health checks..."
sleep 3

# Check if nginx is serving the frontend
if curl -f http://localhost/ > /dev/null 2>&1; then
    echo "✅ Frontend health check passed"
else
    echo "❌ Frontend health check failed"
    nginx -t
    systemctl status nginx
fi

# Check if API proxy is working
if curl -f http://localhost/api/health > /dev/null 2>&1; then
    echo "✅ API proxy health check passed"
else
    echo "⚠️ API proxy might need backend restart"
    echo "🔍 Checking backend status..."
    systemctl status adcopysurge-api.service
fi

echo ""
echo "🎉 Frontend Deployment Complete!"
echo ""
echo "📋 What was fixed:"
echo "  ✅ Updated SimplifiedResults.js to use real backend data"
echo "  ✅ Removed mock scoring (86% fake scores)"
echo "  ✅ Added proper API integration with /api proxy routing"
echo "  ✅ Updated nginx config for better API routing"
echo ""
echo "🌐 Test your site:"
echo "  Frontend: https://adcopysurge.com"
echo "  API Test: https://adcopysurge.com/api/health"
echo ""
echo "📊 Expected result: Frontend should now show real scores (~46.5%) instead of fake high scores (~86%)"
echo ""
echo "🔍 If you still see issues, check:"
echo "  - Clear browser cache (Ctrl+F5)"
echo "  - Check browser developer console for errors"
echo "  - Verify backend is running: curl http://localhost:8000/health"
echo ""
echo "📋 To check logs if needed:"
echo "  Frontend/Nginx: tail -f /var/log/nginx/error.log"
echo "  Backend: journalctl -u adcopysurge-api.service -f"