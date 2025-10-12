#!/bin/bash
# AdCopySurge Direct VPS Deployment Script
# Run this script ON THE VPS to deploy the latest changes

set -e

echo "🚀 Starting AdCopySurge VPS Deployment..."

# Variables
VPS_DIR="/srv/adcopysurge"
REPO_URL="https://github.com/Adeliyio/acsurge.git"
BACKUP_DIR="/root/backups"

# Create backup directory
mkdir -p $BACKUP_DIR

echo "📦 Creating backup of current deployment..."
if [ -d "$VPS_DIR" ]; then
    tar -czf "$BACKUP_DIR/adcopysurge_backup_$(date +%Y%m%d_%H%M%S).tar.gz" -C /srv adcopysurge
    echo "✅ Backup created in $BACKUP_DIR"
fi

echo "📥 Stopping services..."
systemctl stop adcopysurge-api.service || echo "⚠️ Service not running or doesn't exist"

echo "🔄 Updating codebase..."
if [ -d "$VPS_DIR" ]; then
    cd $VPS_DIR
    git fetch --all
    git reset --hard origin/main
    git pull origin main
else
    git clone $REPO_URL $VPS_DIR
    cd $VPS_DIR
fi

echo "🏗️ Building frontend..."
cd $VPS_DIR/frontend
npm install --legacy-peer-deps
npm run build

echo "🐍 Setting up backend..."
cd $VPS_DIR/backend
python3 -m pip install --upgrade pip
python3 -m pip install -r requirements.txt

echo "🔧 Setting up environment..."
# Create production environment file
cat > /srv/adcopysurge/.env << EOF
# Production Environment Variables - Updated to use nginx proxy routing
REACT_APP_API_URL=/api
REACT_APP_SUPABASE_URL=https://tqzlsajhhtkhljdbjkyg.supabase.co
REACT_APP_SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InRxemxzYWpoaHRraGxqZGJqa3lnIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTY5OTYzOTMsImV4cCI6MjA3MjU3MjM5M30.0uI56qJGE5DQwEvcfYlcOIz2NGC-msMVrTRw6d-RQuI
NODE_ENV=production
REACT_APP_ENV=production
REACT_APP_ENABLE_DEBUG=false
REACT_APP_ENABLE_MOCK_DATA=false

# Backend Variables (you'll need to set these)
DATABASE_URL=postgresql://postgres:[password]@db.[project-id].supabase.co:5432/postgres
SUPABASE_SERVICE_ROLE_KEY=[your-service-key]
OPENAI_API_KEY=[your-openai-key]
SECRET_KEY=$(python3 -c 'import secrets; print(secrets.token_hex(32))')
DEBUG=false
SCORE_BASELINE=50
EOF

echo "⚙️ Creating systemd service..."
cat > /etc/systemd/system/adcopysurge-api.service << EOF
[Unit]
Description=AdCopySurge API Server
After=network.target

[Service]
Type=simple
User=www-data
Group=www-data
WorkingDirectory=/srv/adcopysurge/backend
Environment=PATH=/srv/adcopysurge/backend/.venv/bin
EnvironmentFile=/srv/adcopysurge/.env
ExecStart=/srv/adcopysurge/backend/.venv/bin/python -m uvicorn main_launch_ready:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

echo "🔄 Creating Python virtual environment..."
cd /srv/adcopysurge/backend
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

echo "🗂️ Setting up Nginx configuration..."
cat > /etc/nginx/sites-available/adcopysurge << 'EOF'
server {
    listen 80;
    server_name adcopysurge.com www.adcopysurge.com api.adcopysurge.com;
    root /srv/adcopysurge/frontend/build;
    index index.html;

    # Frontend - serve React app (for main domain and www)
    location / {
        try_files $uri $uri/ /index.html;
        add_header Cache-Control "no-cache";
    }

    # Backend API proxy (for all domains)
    location /api/ {
        proxy_pass http://localhost:8000/api/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_connect_timeout 30s;
        proxy_send_timeout 30s;
        proxy_read_timeout 30s;
    }

    # Static files caching
    location /static/ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
EOF

# Enable the site
ln -sf /etc/nginx/sites-available/adcopysurge /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default

echo "🔧 Setting permissions..."
chown -R www-data:www-data /srv/adcopysurge
chmod +x /srv/adcopysurge/backend/.venv/bin/*

echo "🔄 Starting services..."
systemctl daemon-reload
systemctl enable adcopysurge-api.service
systemctl start adcopysurge-api.service

# Test nginx config and reload
nginx -t && systemctl reload nginx

echo "🏥 Running health checks..."
sleep 5

# Check if backend is responding
if curl -f http://localhost:8000/health > /dev/null 2>&1; then
    echo "✅ Backend health check passed"
else
    echo "❌ Backend health check failed"
    systemctl status adcopysurge-api.service
fi

# Check if nginx is serving the frontend
if curl -f http://localhost/ > /dev/null 2>&1; then
    echo "✅ Frontend health check passed"
else
    echo "❌ Frontend health check failed"
    nginx -t
fi

echo "🎉 Deployment completed!"
echo ""
echo "📝 Next steps:"
echo "1. Update the .env file with your actual API keys"
echo "2. Run SSL certificate setup: certbot --nginx -d adcopysurge.com -d www.adcopysurge.com -d api.adcopysurge.com"
echo "3. Test the application at https://adcopysurge.com"
echo ""
echo "📊 Service status:"
systemctl is-active adcopysurge-api.service
echo ""
echo "📋 To check logs:"
echo "sudo journalctl -u adcopysurge-api.service -f"