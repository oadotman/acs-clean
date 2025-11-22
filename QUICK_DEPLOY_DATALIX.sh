#!/bin/bash
# ============================================================================
# AdCopySurge - Quick Deployment Script for Datalix VPS
# ============================================================================
# This script automates the deployment process described in
# DATALIX_DEPLOYMENT_GUIDE.md
#
# PREREQUISITES:
# - Fresh Ubuntu 22.04 VPS
# - Root or sudo access
# - Domain pointing to VPS IP
#
# USAGE:
#   1. SSH into your VPS: ssh root@46.247.108.207
#   2. Download this script: curl -O https://raw.githubusercontent.com/yourusername/adcopysurge/main/QUICK_DEPLOY_DATALIX.sh
#   3. Make executable: chmod +x QUICK_DEPLOY_DATALIX.sh
#   4. Run: ./QUICK_DEPLOY_DATALIX.sh
# ============================================================================

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_header() {
    echo -e "${BLUE}============================================================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}============================================================================${NC}"
}

print_step() {
    echo -e "${GREEN}[STEP]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    print_error "Please run as root or with sudo"
    exit 1
fi

print_header "AdCopySurge Deployment Script - Datalix VPS"
echo ""
echo "This script will:"
echo "  1. Install system dependencies (Python 3.11, Redis, Nginx, etc.)"
echo "  2. Clone the repository"
echo "  3. Set up Python virtual environment"
echo "  4. Install Python packages with Python 3.11 constraints"
echo "  5. Configure systemd services"
echo "  6. Set up Nginx reverse proxy"
echo "  7. Configure SSL with Let's Encrypt"
echo ""
read -p "Continue? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    exit 1
fi

# ============================================================================
# PART 1: System Setup
# ============================================================================
print_header "PART 1: System Setup"

print_step "Updating system packages..."
apt update && apt upgrade -y

print_step "Setting timezone to UTC..."
timedatectl set-timezone UTC

print_step "Installing system dependencies..."
apt install -y \
    build-essential curl git pkg-config libpq-dev libssl-dev libffi-dev \
    software-properties-common nginx certbot python3-certbot-nginx htop tree vim wget \
    libjpeg-dev libpng-dev libtiff-dev libopenjp2-7-dev libcairo2-dev \
    libpango1.0-dev libgdk-pixbuf2.0-dev libffi-dev shared-mime-info

print_step "Installing Python 3.11..."
add-apt-repository ppa:deadsnakes/ppa -y
apt update
apt install -y python3.11 python3.11-venv python3.11-dev python3.11-distutils
curl -sS https://bootstrap.pypa.io/get-pip.py | python3.11

print_step "Installing Redis..."
apt install -y redis-server
sed -i 's/^supervised no/supervised systemd/' /etc/redis/redis.conf
sed -i 's/^# maxmemory <bytes>/maxmemory 256mb/' /etc/redis/redis.conf
echo "maxmemory-policy allkeys-lru" >> /etc/redis/redis.conf
systemctl restart redis-server
systemctl enable redis-server

print_step "Configuring firewall..."
ufw --force reset
ufw default deny incoming
ufw default allow outgoing
ufw allow ssh
ufw allow http
ufw allow https
ufw --force enable

print_success "System setup completed"

# ============================================================================
# PART 2: Application Setup
# ============================================================================
print_header "PART 2: Application Setup"

print_step "Creating application directories..."
mkdir -p /opt/adcopysurge/backend
mkdir -p /opt/adcopysurge/logs
mkdir -p /run/adcopysurge

print_step "Creating deploy user..."
if ! id "deploy" &>/dev/null; then
    adduser --disabled-password --gecos "" deploy
    usermod -aG sudo deploy
fi

chown -R deploy:deploy /opt/adcopysurge
chown -R deploy:deploy /run/adcopysurge

print_step "Cloning repository..."
sudo -u deploy bash << 'EOF'
cd /opt/adcopysurge
git clone https://github.com/Adeliyio/acsurge.git temp_clone
mv temp_clone/backend/* backend/
rm -rf temp_clone
EOF

print_step "Creating Python virtual environment..."
sudo -u deploy bash << 'EOF'
cd /opt/adcopysurge
python3.11 -m venv venv
source venv/bin/activate
pip install --upgrade pip setuptools wheel
EOF

print_step "Installing Python dependencies (this will take 5-10 minutes)..."
sudo -u deploy bash << 'EOF'
cd /opt/adcopysurge
source venv/bin/activate
cd backend
pip install -r requirements.txt -c constraints-py311.txt --prefer-binary
EOF

print_success "Application setup completed"

# ============================================================================
# PART 3: Configuration
# ============================================================================
print_header "PART 3: Configuration"

print_step "Creating environment file..."
cat > /opt/adcopysurge/backend/.env << 'EOF'
# AdCopySurge Production Environment
ENVIRONMENT=production
DEBUG=False
APP_VERSION=1.0.0
APP_NAME=AdCopySurge

# Security - CHANGE THIS SECRET KEY!
SECRET_KEY=CHANGE-THIS-TO-A-SECURE-RANDOM-STRING-MINIMUM-32-CHARACTERS-LONG
ACCESS_TOKEN_EXPIRE_MINUTES=30
ALGORITHM=HS256

# Server Configuration
HOST=0.0.0.0
PORT=8000
SERVER_NAME=api.adcopysurge.com

# CORS Origins
CORS_ORIGINS=https://adcopysurge.netlify.app,https://adcopysurge.com
ALLOWED_HOSTS=api.adcopysurge.com,*.adcopysurge.com

# Database - Supabase PostgreSQL
DATABASE_URL=postgresql://postgres:qvF0YRAfKjnVVvLd@db.tqzlsajhhtkhljdbjkyg.supabase.co:5432/postgres

# Supabase Configuration
SUPABASE_URL=https://tqzlsajhhtkhljdbjkyg.supabase.co
SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InRxemxzYWpoaHRraGxqZGJqa3lnIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTY5OTYzOTMsImV4cCI6MjA3MjU3MjM5M30.0uI56qJGE5DQwEvcfYlcOIz2NGC-msMVrTRw6d-RQuI
SUPABASE_SERVICE_ROLE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InRxemxzYWpoaHRraGxqZGJqa3lnIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1Njk5NjM5MywiZXhwIjoyMDcyNTcyMzkzfQ.I4Bs0UL5UD3eGAXQmxmTa6zof17XHgl1AyeN-p4fyYg

# Redis
REDIS_URL=redis://localhost:6379/0

# AI Services - ADD YOUR KEYS HERE
OPENAI_API_KEY=sk-your-key-here
HUGGINGFACE_API_KEY=hf_your-key-here
GEMINI_API_KEY=your-key-here

# Feature Flags
ENABLE_ANALYTICS=true
ENABLE_PDF_REPORTS=true
ENABLE_RATE_LIMITING=true
ENABLE_BLOG=false

# Performance
WORKERS=2
CELERY_WORKERS=2
MAX_CONNECTIONS=50

# Monitoring
LOG_LEVEL=info
EOF

chown deploy:deploy /opt/adcopysurge/backend/.env
chmod 600 /opt/adcopysurge/backend/.env

print_warning "IMPORTANT: Edit /opt/adcopysurge/backend/.env and update:"
print_warning "  1. SECRET_KEY"
print_warning "  2. OPENAI_API_KEY"
print_warning "  3. Other API keys as needed"
echo ""
read -p "Press Enter to continue after editing the .env file..."

print_step "Running database migrations..."
sudo -u deploy bash << 'EOF'
cd /opt/adcopysurge/backend
source /opt/adcopysurge/venv/bin/activate
set -a; source .env; set +a
alembic upgrade head
EOF

print_success "Configuration completed"

# ============================================================================
# PART 4: Systemd Services
# ============================================================================
print_header "PART 4: Systemd Services"

print_step "Creating Gunicorn configuration..."
cat > /opt/adcopysurge/backend/gunicorn.conf.py << 'EOF'
import multiprocessing
bind = "unix:/run/adcopysurge/gunicorn.sock"
backlog = 2048
workers = 2
worker_class = "uvicorn.workers.UvicornWorker"
worker_connections = 1000
max_requests = 1000
max_requests_jitter = 50
preload_app = True
timeout = 180
keepalive = 2
accesslog = "/opt/adcopysurge/logs/gunicorn.access.log"
errorlog = "/opt/adcopysurge/logs/gunicorn.error.log"
loglevel = "info"
proc_name = "adcopysurge-backend"
daemon = False
pidfile = "/run/adcopysurge/gunicorn.pid"
user = "deploy"
group = "deploy"
raw_env = [
    "PYTHONPATH=/opt/adcopysurge/backend",
    "PYTHONDONTWRITEBYTECODE=1",
    "PYTHONUNBUFFERED=1",
]
EOF

print_step "Creating systemd services..."

# API Service
cat > /etc/systemd/system/adcopysurge.service << 'EOF'
[Unit]
Description=AdCopySurge FastAPI Application
After=network.target redis-server.service
Requires=redis-server.service

[Service]
Type=notify
User=deploy
Group=deploy
WorkingDirectory=/opt/adcopysurge/backend
Environment="PATH=/opt/adcopysurge/venv/bin"
Environment="PYTHONPATH=/opt/adcopysurge/backend"
EnvironmentFile=/opt/adcopysurge/backend/.env
ExecStart=/opt/adcopysurge/venv/bin/gunicorn main_production:app --config /opt/adcopysurge/backend/gunicorn.conf.py
ExecReload=/bin/kill -s HUP $MAINPID
KillMode=mixed
TimeoutStopSec=10
Restart=always
RestartSec=3
NoNewPrivileges=true
ProtectSystem=strict
ProtectHome=true
ReadWritePaths=/opt/adcopysurge/logs /run/adcopysurge /tmp

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
Type=forking
User=deploy
Group=deploy
WorkingDirectory=/opt/adcopysurge/backend
Environment="PATH=/opt/adcopysurge/venv/bin"
Environment="PYTHONPATH=/opt/adcopysurge/backend"
EnvironmentFile=/opt/adcopysurge/backend/.env
ExecStart=/opt/adcopysurge/venv/bin/celery -A app.celery_app worker --loglevel=info --concurrency=2 --detach --pidfile=/run/adcopysurge/celery.pid --logfile=/opt/adcopysurge/logs/celery.log
PIDFile=/run/adcopysurge/celery.pid
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable adcopysurge.service adcopysurge-celery.service
systemctl start adcopysurge.service adcopysurge-celery.service

sleep 5

print_success "Services created and started"

# ============================================================================
# PART 5: Nginx Configuration
# ============================================================================
print_header "PART 5: Nginx Configuration"

print_step "Configuring Nginx..."

cat > /etc/nginx/sites-available/adcopysurge << 'EOF'
limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;
limit_req_zone $binary_remote_addr zone=auth:10m rate=5r/s;
limit_req_zone $binary_remote_addr zone=analysis:10m rate=2r/s;

upstream adcopysurge_backend {
    server unix:/run/adcopysurge/gunicorn.sock fail_timeout=0;
}

server {
    listen 80;
    server_name api.adcopysurge.com;

    access_log /var/log/nginx/adcopysurge_access.log;
    error_log /var/log/nginx/adcopysurge_error.log;

    client_max_body_size 10M;

    location /api/ads/analyze {
        limit_req zone=analysis burst=5 nodelay;
        proxy_pass http://adcopysurge_backend;
        proxy_set_header Host $http_host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_connect_timeout 300s;
        proxy_send_timeout 300s;
        proxy_read_timeout 300s;
    }

    location /api {
        limit_req zone=api burst=20 nodelay;
        proxy_pass http://adcopysurge_backend;
        proxy_set_header Host $http_host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /health {
        proxy_pass http://adcopysurge_backend;
        proxy_set_header Host $http_host;
        access_log off;
    }

    location / {
        proxy_pass http://adcopysurge_backend;
        proxy_set_header Host $http_host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
EOF

ln -sf /etc/nginx/sites-available/adcopysurge /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default

nginx -t && systemctl restart nginx && systemctl enable nginx

print_success "Nginx configured"

# ============================================================================
# PART 6: SSL Certificate
# ============================================================================
print_header "PART 6: SSL Certificate"

print_warning "Make sure api.adcopysurge.com points to this server"
read -p "Continue with SSL setup? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    certbot --nginx -d api.adcopysurge.com --non-interactive --agree-tos --email admin@adcopysurge.com --redirect
    print_success "SSL certificate configured"
else
    print_warning "Skipping SSL setup"
fi

# ============================================================================
# Final Verification
# ============================================================================
print_header "Deployment Complete!"

echo ""
echo "✅ AdCopySurge has been deployed successfully!"
echo ""
echo "Next steps:"
echo "  1. Edit /opt/adcopysurge/backend/.env with your API keys"
echo "  2. Restart services: systemctl restart adcopysurge.service"
echo "  3. Test API: curl https://api.adcopysurge.com/health"
echo ""
echo "Useful commands:"
echo "  - View logs: journalctl -u adcopysurge.service -f"
echo "  - Restart: systemctl restart adcopysurge.service"
echo "  - Status: systemctl status adcopysurge.service"
echo ""
echo "Access your API at: https://api.adcopysurge.com"
echo ""
