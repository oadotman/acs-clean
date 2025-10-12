#!/bin/bash
# AdCopySurge Deployment Script for Debian Buster (Legacy)
# IP: 46.247.108.207
# Domain: api.adcopysurge.com

set -e

echo "🚀 AdCopySurge Deployment on Debian Buster Starting..."

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

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
# STEP 1: Fix Repository Sources for Debian Buster
# =============================================================================
print_step "1. Fixing Debian Buster repositories..."

# Backup current sources
cp /etc/apt/sources.list /etc/apt/sources.list.backup

# Update to archive sources
cat > /etc/apt/sources.list << 'EOF'
deb http://archive.debian.org/debian/ buster main contrib non-free
deb http://archive.debian.org/debian-security buster/updates main contrib non-free
EOF

# Disable signature checking for archived repos
mkdir -p /etc/apt/apt.conf.d
cat > /etc/apt/apt.conf.d/99allow-unauthenticated << 'EOF'
APT::Get::AllowUnauthenticated "true";
Acquire::Check-Valid-Until "false";
EOF

# Update package lists
apt update

print_step "1. ✅ Repository sources fixed"

# =============================================================================
# STEP 2: Install System Dependencies
# =============================================================================
print_step "2. Installing system packages..."

# Install essential packages
apt install -y \
    curl \
    wget \
    gnupg2 \
    software-properties-common \
    apt-transport-https \
    ca-certificates \
    build-essential \
    git \
    pkg-config \
    libffi-dev \
    libssl-dev \
    nginx \
    redis-server \
    ufw \
    fail2ban \
    htop \
    tree

# Install Python build dependencies
apt install -y \
    python3 \
    python3-pip \
    python3-venv \
    python3-dev \
    zlib1g-dev \
    libncurses5-dev \
    libgdbm-dev \
    libnss3-dev \
    libreadline-dev \
    libsqlite3-dev \
    libbz2-dev \
    libpq-dev

print_step "2. ✅ System packages installed"

# =============================================================================
# STEP 3: Install Python 3.11 from Source
# =============================================================================
print_step "3. Installing Python 3.11 from source..."

# Check if Python 3.11 is already installed
if ! command -v python3.11 &> /dev/null; then
    cd /tmp
    
    # Download Python 3.11.9
    wget -q https://www.python.org/ftp/python/3.11.9/Python-3.11.9.tgz
    tar -xf Python-3.11.9.tgz
    cd Python-3.11.9
    
    # Configure and build Python
    ./configure --enable-optimizations --with-ensurepip=install --prefix=/usr/local
    make -j$(nproc) > /dev/null 2>&1
    make altinstall > /dev/null 2>&1
    
    # Clean up
    cd /
    rm -rf /tmp/Python-3.11.9*
    
    print_step "3. ✅ Python 3.11 installed from source"
else
    print_step "3. ✅ Python 3.11 already installed"
fi

# Create convenient symlinks
ln -sf /usr/local/bin/python3.11 /usr/local/bin/python
ln -sf /usr/local/bin/pip3.11 /usr/local/bin/pip

# =============================================================================
# STEP 4: Security Configuration
# =============================================================================
print_step "4. Configuring security..."

# Configure firewall
ufw --force reset
ufw default deny incoming
ufw default allow outgoing
ufw allow ssh
ufw allow http
ufw allow https
ufw --force enable

# Set timezone
timedatectl set-timezone UTC

print_step "4. ✅ Security configured"

# =============================================================================
# STEP 5: Configure Redis
# =============================================================================
print_step "5. Configuring Redis..."

# Configure Redis
sed -i 's/^# supervised no/supervised systemd/' /etc/redis/redis.conf
sed -i 's/^# maxmemory <bytes>/maxmemory 256mb/' /etc/redis/redis.conf
echo "maxmemory-policy allkeys-lru" >> /etc/redis/redis.conf

# Restart and enable Redis
systemctl restart redis-server
systemctl enable redis-server

# Test Redis
redis-cli ping

print_step "5. ✅ Redis configured"

# =============================================================================
# STEP 6: Create Deploy User
# =============================================================================
print_step "6. Creating deploy user..."

# Create deploy user
if ! id "deploy" &>/dev/null; then
    adduser --disabled-password --gecos "" deploy
    usermod -aG sudo deploy
    
    # Create SSH directory
    mkdir -p /home/deploy/.ssh
    chmod 700 /home/deploy/.ssh
    chown deploy:deploy /home/deploy/.ssh
fi

print_step "6. ✅ Deploy user created"

# =============================================================================
# STEP 7: Application Setup
# =============================================================================
print_step "7. Setting up application directory..."

# Create application directory
mkdir -p /srv/adcopysurge/{logs,run}
chown -R deploy:deploy /srv/adcopysurge

print_warning "MANUAL STEP REQUIRED: You need to clone your repository"
echo "Run the following commands as deploy user:"
echo "sudo -u deploy bash"
echo "cd /srv/adcopysurge"
echo "git clone https://github.com/yourusername/adcopysurge.git app"
echo "exit"
echo ""
echo "Press Enter when you've completed the git clone..."
read -p ""

print_step "7. ✅ Application directory prepared"

# =============================================================================
# STEP 8: Python Virtual Environment
# =============================================================================
print_step "8. Setting up Python environment..."

sudo -u deploy bash << 'EOF'
cd /srv/adcopysurge

# Create virtual environment with Python 3.11
/usr/local/bin/python3.11 -m venv venv

# Activate and upgrade pip
source venv/bin/activate
pip install --upgrade pip wheel setuptools

# Install dependencies
if [ -f "app/backend/requirements.txt" ]; then
    cd app/backend
    pip install -r requirements.txt
    echo "✅ Dependencies installed successfully"
else
    echo "❌ requirements.txt not found. Make sure you cloned the repository correctly."
    exit 1
fi
EOF

print_step "8. ✅ Python environment configured"

# =============================================================================
# STEP 9: Environment Variables
# =============================================================================
print_step "9. Configuring environment variables..."

cat > /etc/adcopysurge.env << 'EOF'
# AdCopySurge Production Environment
ENVIRONMENT=production
DEBUG=false
APP_NAME=AdCopySurge
HOST=0.0.0.0
PORT=8000

# Security - CHANGE THIS SECRET KEY!
SECRET_KEY=your-super-secure-secret-key-change-this-32-chars-minimum-xyz123
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

# Performance Settings
WORKERS=2
CELERY_WORKERS=2
MAX_CONNECTIONS=50

# Monitoring
LOG_LEVEL=info
EOF

chmod 640 /etc/adcopysurge.env
chown root:deploy /etc/adcopysurge.env

print_step "9. ✅ Environment variables configured"

# =============================================================================
# STEP 10: Database Migrations
# =============================================================================
print_step "10. Running database migrations..."

sudo -u deploy bash << 'EOF'
cd /srv/adcopysurge/app/backend
source /srv/adcopysurge/venv/bin/activate
source /etc/adcopysurge.env

# Run Alembic migrations
if [ -f "alembic.ini" ]; then
    alembic upgrade head
    echo "✅ Database migrations completed"
else
    echo "❌ alembic.ini not found"
fi
EOF

print_step "10. ✅ Database migrations completed"

# =============================================================================
# STEP 11: Systemd Services
# =============================================================================
print_step "11. Creating systemd services..."

# API Service
cat > /etc/systemd/system/adcopysurge-api.service << 'EOF'
[Unit]
Description=AdCopySurge FastAPI Application
After=network.target redis-server.service
Requires=redis-server.service

[Service]
Type=exec
User=deploy
Group=deploy
WorkingDirectory=/srv/adcopysurge/app/backend
Environment=PATH=/srv/adcopysurge/venv/bin:/usr/local/bin
EnvironmentFile=/etc/adcopysurge.env
ExecStart=/srv/adcopysurge/venv/bin/gunicorn main:app \
    --worker-class uvicorn.workers.UvicornWorker \
    --workers 2 \
    --bind unix:/srv/adcopysurge/run/gunicorn.sock \
    --timeout 30 \
    --keep-alive 2 \
    --max-requests 1000 \
    --max-requests-jitter 50 \
    --access-logfile /srv/adcopysurge/logs/gunicorn.access.log \
    --error-logfile /srv/adcopysurge/logs/gunicorn.error.log \
    --log-level info
ExecReload=/bin/kill -s HUP $MAINPID
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
EOF

# Celery Service
cat > /etc/systemd/system/adcopysurge-celery.service << 'EOF'
[Unit]
Description=AdCopySurge Celery Worker
After=network.target redis-server.service
Requires=redis-server.service

[Service]
Type=exec
User=deploy
Group=deploy
WorkingDirectory=/srv/adcopysurge/app/backend
Environment=PATH=/srv/adcopysurge/venv/bin:/usr/local/bin
EnvironmentFile=/etc/adcopysurge.env
ExecStart=/srv/adcopysurge/venv/bin/celery -A app.celery_app worker \
    --loglevel=info \
    --concurrency=2 \
    --logfile=/srv/adcopysurge/logs/celery.log
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable adcopysurge-api.service
systemctl enable adcopysurge-celery.service

print_step "11. ✅ Systemd services created"

# =============================================================================
# STEP 12: Nginx Configuration
# =============================================================================
print_step "12. Configuring Nginx..."

cat > /etc/nginx/sites-available/adcopysurge << 'EOF'
upstream adcopysurge_backend {
    server unix:/srv/adcopysurge/run/gunicorn.sock;
}

server {
    listen 80;
    server_name api.adcopysurge.com;

    access_log /var/log/nginx/adcopysurge_access.log;
    error_log /var/log/nginx/adcopysurge_error.log;

    client_max_body_size 10M;

    location / {
        proxy_pass http://adcopysurge_backend;
        proxy_set_header Host $http_host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_redirect off;
    }

    location /health {
        proxy_pass http://adcopysurge_backend;
        proxy_set_header Host $http_host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_redirect off;
        access_log off;
    }
}
EOF

ln -sf /etc/nginx/sites-available/adcopysurge /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default

nginx -t
systemctl restart nginx
systemctl enable nginx

print_step "12. ✅ Nginx configured"

# =============================================================================
# STEP 13: Start Services
# =============================================================================
print_step "13. Starting services..."

systemctl start adcopysurge-api.service
systemctl start adcopysurge-celery.service

sleep 3

systemctl is-active adcopysurge-api.service
systemctl is-active adcopysurge-celery.service

print_step "13. ✅ Services started"

# =============================================================================
# STEP 14: SSL Certificate (Certbot for Debian Buster)
# =============================================================================
print_step "14. Setting up SSL certificate..."

# Install certbot from backports or manual
apt install -y python3-certbot-nginx || {
    echo "Installing certbot manually..."
    pip install certbot certbot-nginx
    ln -s /usr/local/bin/certbot /usr/bin/certbot
}

print_warning "Make sure api.adcopysurge.com points to 46.247.108.207 before continuing"
echo "Press Enter to continue with SSL setup or Ctrl+C to skip..."
read -p ""

certbot --nginx -d api.adcopysurge.com --non-interactive --agree-tos --email admin@adcopysurge.com --redirect

print_step "14. ✅ SSL certificate configured"

# =============================================================================
# Final Status Check
# =============================================================================
print_step "Deployment completed! Checking final status..."

echo "Service status:"
systemctl is-active adcopysurge-api.service
systemctl is-active adcopysurge-celery.service
systemctl is-active nginx
systemctl is-active redis-server

echo ""
echo "Testing health endpoint:"
curl -f http://localhost/health || echo "Local health check failed"

echo ""
echo "🎉 AdCopySurge deployment completed!"
echo "API Documentation: https://api.adcopysurge.com/docs"
echo "Health Check: https://api.adcopysurge.com/health"
echo ""
echo "Useful commands:"
echo "- View API logs: journalctl -u adcopysurge-api.service -f"
echo "- View Celery logs: journalctl -u adcopysurge-celery.service -f"
echo "- Restart API: systemctl restart adcopysurge-api.service"
echo "- Check status: systemctl status adcopysurge-api adcopysurge-celery"