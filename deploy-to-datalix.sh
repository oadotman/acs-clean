#!/bin/bash
# AdCopySurge Deployment Script for Datalix VPS
# IP: 46.247.108.207
# Domain: api.adcopysurge.com
# 
# Run this script as root on your Ubuntu 22.04 VPS

set -e  # Exit on any error

echo "🚀 AdCopySurge VPS Deployment Starting..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

print_step() {
    echo -e "${GREEN}[STEP]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# =============================================================================
# STEP 1: System Updates and Security
# =============================================================================
print_step "1. Updating system and installing security tools..."

apt update && apt upgrade -y

# Set timezone
timedatectl set-timezone UTC

# Install security packages
apt install -y ufw fail2ban unattended-upgrades

# Configure firewall
ufw --force reset
ufw default deny incoming
ufw default allow outgoing
ufw allow ssh
ufw allow http
ufw allow https
ufw --force enable

print_step "1. ✅ System security configured"

# =============================================================================
# STEP 2: Create Deploy User
# =============================================================================
print_step "2. Creating deploy user..."

# Create deploy user with home directory
adduser --disabled-password --gecos "" deploy
usermod -aG sudo deploy

# Create SSH directory for deploy user
mkdir -p /home/deploy/.ssh
chmod 700 /home/deploy/.ssh
chown deploy:deploy /home/deploy/.ssh

print_step "2. ✅ Deploy user created"

# =============================================================================
# STEP 3: Install System Dependencies
# =============================================================================
print_step "3. Installing system packages..."

apt install -y \
    build-essential \
    curl \
    git \
    pkg-config \
    libpq-dev \
    software-properties-common \
    nginx \
    certbot \
    python3-certbot-nginx \
    htop \
    tree

# Add deadsnakes PPA for Python 3.11
add-apt-repository ppa:deadsnakes/ppa -y
apt update

# Install Python 3.11
apt install -y python3.11 python3.11-venv python3.11-dev python3.11-distutils

# Install pip for Python 3.11
curl -sS https://bootstrap.pypa.io/get-pip.py | python3.11

# Create symlinks for convenience
update-alternatives --install /usr/bin/python python /usr/bin/python3.11 1

print_step "3. ✅ System packages installed"

# =============================================================================
# STEP 4: Install and Configure Redis
# =============================================================================
print_step "4. Installing and configuring Redis..."

apt install -y redis-server

# Configure Redis
sed -i 's/^supervised no/supervised systemd/' /etc/redis/redis.conf
sed -i 's/^# maxmemory <bytes>/maxmemory 256mb/' /etc/redis/redis.conf
echo "maxmemory-policy allkeys-lru" >> /etc/redis/redis.conf

# Restart and enable Redis
systemctl restart redis-server
systemctl enable redis-server

# Test Redis
redis-cli ping

print_step "4. ✅ Redis configured and running"

# =============================================================================
# STEP 5: Create Application Directory Structure
# =============================================================================
print_step "5. Setting up application directory..."

mkdir -p /srv/adcopysurge/{logs,run}
chown -R deploy:deploy /srv/adcopysurge

# Switch to deploy user for application setup
sudo -u deploy bash << 'EOF'
cd /srv/adcopysurge

# Clone repository
git clone https://github.com/Adeliyio/acsurge.git app
# Repository is public, so no additional authentication needed

cd app
EOF

print_step "5. ✅ Application directory structure created"

# =============================================================================
# STEP 6: Python Virtual Environment and Dependencies
# =============================================================================
print_step "6. Setting up Python environment..."

sudo -u deploy bash << 'EOF'
cd /srv/adcopysurge

# Create virtual environment
python3.11 -m venv venv

# Activate and upgrade pip
source venv/bin/activate
pip install --upgrade pip wheel

# Install dependencies
cd app/backend
pip install -r requirements.txt

# Verify key packages
python -c "import fastapi, uvicorn, gunicorn, celery, redis; print('✅ All packages installed successfully')"
EOF

print_step "6. ✅ Python environment configured"

# =============================================================================
# STEP 7: Configure Environment Variables
# =============================================================================
print_step "7. Setting up environment configuration..."

cat > /etc/adcopysurge.env << 'EOF'
# AdCopySurge Production Environment
ENVIRONMENT=production
DEBUG=false
APP_NAME=AdCopySurge
HOST=0.0.0.0
PORT=8000

# Security
SECRET_KEY=your-super-secure-secret-key-change-this-32-chars-minimum
ACCESS_TOKEN_EXPIRE_MINUTES=30
ALGORITHM=HS256

# Server Configuration
SERVER_NAME=api.adcopysurge.com
CORS_ORIGINS=https://adcopysurge.netlify.app,https://adcopysurge.com

# Database (Supabase)
DATABASE_URL=postgresql://postgres:qvF0YRAfKjnVVvLd@db.tqzlsajhhtkhljdbjkyg.supabase.co:5432/postgres

# Supabase Configuration
SUPABASE_URL=https://tqzlsajhhtkhljdbjkyg.supabase.co
SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InRxemxzYWpoaHRraGxqZGJqa3lnIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTY5OTYzOTMsImV4cCI6MjA3MjU3MjM5M30.0uI56qJGE5DQwEvcfYlcOIz2NGC-msMVrTRw6d-RQuI
SUPABASE_SERVICE_ROLE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InRxemxzYWpoaHRraGxqZGJqa3lnIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1Njk5NjM5MywiZXhwIjoyMDcyNTcyMzkzfQ.I4Bs0UL5UD3eGAXQmxmTa6zof17XHgl1AyeN-p4fyYg

# Redis Configuration
REDIS_URL=redis://localhost:6379/0

# AI Services
OPENAI_API_KEY=${OPENAI_API_KEY:?Please set OPENAI_API_KEY environment variable}

# Feature Flags
ENABLE_ANALYTICS=true
ENABLE_PDF_REPORTS=true
ENABLE_RATE_LIMITING=true

# Performance Settings (optimized for VPS)
WORKERS=2
CELERY_WORKERS=2
MAX_CONNECTIONS=50

# Monitoring
LOG_LEVEL=info
EOF

# Set proper permissions
chmod 640 /etc/adcopysurge.env
chown root:deploy /etc/adcopysurge.env

print_step "7. ✅ Environment variables configured"

# =============================================================================
# STEP 8: Run Database Migrations
# =============================================================================
print_step "8. Running database migrations..."

sudo -u deploy bash << 'EOF'
cd /srv/adcopysurge/app/backend
source /srv/adcopysurge/venv/bin/activate
source /etc/adcopysurge.env

# Run Alembic migrations
alembic upgrade head
EOF

print_step "8. ✅ Database migrations completed"

# =============================================================================
# STEP 9: Create Systemd Services
# =============================================================================
print_step "9. Creating systemd services..."

# AdCopySurge API Service (Gunicorn + Uvicorn)
cat > /etc/systemd/system/adcopysurge-api.service << 'EOF'
[Unit]
Description=AdCopySurge FastAPI Application
After=network.target redis-server.service
Requires=redis-server.service

[Service]
Type=notify
User=deploy
Group=deploy
WorkingDirectory=/srv/adcopysurge/app/backend
Environment=PATH=/srv/adcopysurge/venv/bin
EnvironmentFile=/etc/adcopysurge.env
ExecStart=/srv/adcopysurge/venv/bin/gunicorn main:app \
    --worker-class uvicorn.workers.UvicornWorker \
    --workers 2 \
    --bind unix:/srv/adcopysurge/run/gunicorn.sock \
    --timeout 30 \
    --keep-alive 2 \
    --max-requests 1000 \
    --max-requests-jitter 50 \
    --preload \
    --access-logfile /srv/adcopysurge/logs/gunicorn.access.log \
    --error-logfile /srv/adcopysurge/logs/gunicorn.error.log \
    --log-level info
ExecReload=/bin/kill -s HUP $MAINPID
KillMode=mixed
TimeoutStopSec=5
PrivateTmp=true
Restart=always
RestartSec=3

# Security settings
NoNewPrivileges=true
ProtectSystem=strict
ProtectHome=true
ReadWritePaths=/srv/adcopysurge/run /srv/adcopysurge/logs /tmp
PrivateDevices=true
ProtectKernelTunables=true
ProtectControlGroups=true
RestrictRealtime=true

[Install]
WantedBy=multi-user.target
EOF

# Celery Worker Service
cat > /etc/systemd/system/adcopysurge-celery.service << 'EOF'
[Unit]
Description=AdCopySurge Celery Worker
After=network.target redis-server.service
Requires=redis-server.service

[Service]
Type=forking
User=deploy
Group=deploy
WorkingDirectory=/srv/adcopysurge/app/backend
Environment=PATH=/srv/adcopysurge/venv/bin
EnvironmentFile=/etc/adcopysurge.env
ExecStart=/srv/adcopysurge/venv/bin/celery -A app.celery_app worker \
    --loglevel=info \
    --concurrency=2 \
    --detach \
    --pidfile=/srv/adcopysurge/run/celery.pid \
    --logfile=/srv/adcopysurge/logs/celery.log
ExecStop=/srv/adcopysurge/venv/bin/celery -A app.celery_app control shutdown
ExecReload=/srv/adcopysurge/venv/bin/celery -A app.celery_app control reload
PIDFile=/srv/adcopysurge/run/celery.pid
Restart=always
RestartSec=3

# Security settings
NoNewPrivileges=true
ProtectSystem=strict
ProtectHome=true
ReadWritePaths=/srv/adcopysurge/run /srv/adcopysurge/logs /tmp
PrivateDevices=true

[Install]
WantedBy=multi-user.target
EOF

# Reload systemd and enable services
systemctl daemon-reload
systemctl enable adcopysurge-api.service
systemctl enable adcopysurge-celery.service

print_step "9. ✅ Systemd services created and enabled"

# =============================================================================
# STEP 10: Configure Nginx
# =============================================================================
print_step "10. Configuring Nginx reverse proxy..."

cat > /etc/nginx/sites-available/adcopysurge << 'EOF'
# AdCopySurge Nginx Configuration

# Rate limiting zones
limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;
limit_req_zone $binary_remote_addr zone=auth:10m rate=5r/s;

# Upstream backend
upstream adcopysurge_backend {
    server unix:/srv/adcopysurge/run/gunicorn.sock;
}

server {
    listen 80;
    server_name api.adcopysurge.com;

    # Logs
    access_log /var/log/nginx/adcopysurge_access.log;
    error_log /var/log/nginx/adcopysurge_error.log;

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;

    # Client settings
    client_max_body_size 10M;

    # Gzip compression
    gzip on;
    gzip_vary on;
    gzip_min_length 1000;
    gzip_comp_level 6;
    gzip_types
        text/plain
        text/css
        text/xml
        text/javascript
        application/json
        application/javascript
        application/xml+rss
        application/atom+xml;

    # API routes with rate limiting
    location /api/auth {
        limit_req zone=auth burst=10 nodelay;
        proxy_pass http://adcopysurge_backend;
        proxy_set_header Host $http_host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_redirect off;
    }

    location /api {
        limit_req zone=api burst=20 nodelay;
        proxy_pass http://adcopysurge_backend;
        proxy_set_header Host $http_host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_redirect off;
    }

    # Health check endpoint
    location /health {
        proxy_pass http://adcopysurge_backend;
        proxy_set_header Host $http_host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_redirect off;
        access_log off;
    }

    # API Documentation
    location /docs {
        proxy_pass http://adcopysurge_backend;
        proxy_set_header Host $http_host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_redirect off;
    }

    location /openapi.json {
        proxy_pass http://adcopysurge_backend;
        proxy_set_header Host $http_host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_redirect off;
    }

    # Root and other routes
    location / {
        proxy_pass http://adcopysurge_backend;
        proxy_set_header Host $http_host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_redirect off;
    }
}
EOF

# Enable the site
ln -sf /etc/nginx/sites-available/adcopysurge /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default

# Test Nginx configuration
nginx -t

# Restart Nginx
systemctl restart nginx
systemctl enable nginx

print_step "10. ✅ Nginx configured"

# =============================================================================
# STEP 11: Start Services
# =============================================================================
print_step "11. Starting AdCopySurge services..."

# Start services
systemctl start adcopysurge-api.service
systemctl start adcopysurge-celery.service

# Check service status
sleep 5
systemctl is-active adcopysurge-api.service
systemctl is-active adcopysurge-celery.service

print_step "11. ✅ Services started"

# =============================================================================
# STEP 12: SSL Certificate
# =============================================================================
print_step "12. Setting up SSL certificate..."

print_warning "Make sure your domain api.adcopysurge.com points to this server (46.247.108.207) before running SSL setup"

# Obtain SSL certificate (non-interactive)
certbot --nginx -d api.adcopysurge.com --non-interactive --agree-tos --email admin@adcopysurge.com --redirect

print_step "12. ✅ SSL certificate configured"

# =============================================================================
# STEP 13: Configure Log Rotation
# =============================================================================
print_step "13. Setting up log rotation..."

cat > /etc/logrotate.d/adcopysurge << 'EOF'
/srv/adcopysurge/logs/*.log {
    weekly
    rotate 12
    compress
    delaycompress
    missingok
    notifempty
    copytruncate
    create 644 deploy deploy
}

/var/log/nginx/adcopysurge_*.log {
    daily
    rotate 14
    compress
    delaycompress
    missingok
    notifempty
    create 644 www-data adm
    postrotate
        systemctl reload nginx
    endscript
}
EOF

print_step "13. ✅ Log rotation configured"

# =============================================================================
# FINAL CHECKS
# =============================================================================
print_step "Running final health checks..."

echo "Checking service status:"
systemctl status adcopysurge-api.service --no-pager -l
systemctl status adcopysurge-celery.service --no-pager -l
systemctl status nginx --no-pager -l
systemctl status redis-server --no-pager -l

echo ""
echo "Checking network connectivity:"
ss -tlnp | grep :80
ss -tlnp | grep :443
ss -lx | grep gunicorn

echo ""
echo "Testing API endpoints:"
sleep 3
curl -f http://localhost/health || echo "Health check failed - check logs"
curl -f http://api.adcopysurge.com/health || echo "External health check failed - check DNS"

echo ""
echo "🎉 AdCopySurge deployment completed!"
echo ""
echo "Next steps:"
echo "1. Verify your domain api.adcopysurge.com points to 46.247.108.207"
echo "2. Test the API: https://api.adcopysurge.com/docs"
echo "3. Check logs: journalctl -u adcopysurge-api.service -f"
echo "4. Monitor services: systemctl status adcopysurge-api adcopysurge-celery"
echo ""
echo "Useful commands:"
echo "- View logs: tail -f /srv/adcopysurge/logs/gunicorn.access.log"
echo "- Restart API: systemctl restart adcopysurge-api.service"
echo "- Update code: cd /srv/adcopysurge/app && git pull && systemctl restart adcopysurge-api"
echo ""