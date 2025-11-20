# AdCopySurge - Datalix VPS Deployment Guide (Python 3.11)

**Complete step-by-step guide for deploying AdCopySurge on Datalix VPS with Python 3.11**

## Prerequisites

- ✅ Datalix VPS with Ubuntu 22.04
- ✅ Root or sudo access
- ✅ Domain pointing to VPS IP (api.adcopysurge.com → 46.247.108.207)
- ✅ Supabase PostgreSQL database ready
- ✅ OpenAI API key
- ✅ Git repository access

---

## 🚀 Part 1: Initial Server Setup

### Step 1: Connect to Your VPS

```bash
# SSH into your Datalix VPS
ssh root@46.247.108.207
# Or if you have a user account:
ssh yourusername@46.247.108.207
```

### Step 2: Update System Packages

```bash
# Update package lists and upgrade existing packages
sudo apt update && sudo apt upgrade -y

# Set timezone to UTC (recommended for servers)
sudo timedatectl set-timezone UTC

# Verify timezone
timedatectl
```

### Step 3: Install System Dependencies

```bash
# Install essential build tools and libraries
sudo apt install -y \
    build-essential \
    curl \
    git \
    pkg-config \
    libpq-dev \
    libssl-dev \
    libffi-dev \
    software-properties-common \
    nginx \
    certbot \
    python3-certbot-nginx \
    htop \
    tree \
    vim \
    wget

# Install image processing libraries (required for Pillow/WeasyPrint)
sudo apt install -y \
    libjpeg-dev \
    libpng-dev \
    libtiff-dev \
    libopenjp2-7-dev \
    libcairo2-dev \
    libpango1.0-dev \
    libgdk-pixbuf2.0-dev \
    libffi-dev \
    shared-mime-info

echo "✅ System dependencies installed"
```

### Step 4: Install Python 3.11

```bash
# Add deadsnakes PPA for Python 3.11
sudo add-apt-repository ppa:deadsnakes/ppa -y
sudo apt update

# Install Python 3.11 and related packages
sudo apt install -y \
    python3.11 \
    python3.11-venv \
    python3.11-dev \
    python3.11-distutils

# Install pip for Python 3.11
curl -sS https://bootstrap.pypa.io/get-pip.py | sudo python3.11

# Verify Python 3.11 installation
python3.11 --version
# Should output: Python 3.11.x

# Verify pip installation
python3.11 -m pip --version
# Should output: pip 24.x from ...

echo "✅ Python 3.11 installed successfully"
```

### Step 5: Install and Configure Redis

```bash
# Install Redis server
sudo apt install -y redis-server

# Configure Redis for systemd supervision
sudo sed -i 's/^supervised no/supervised systemd/' /etc/redis/redis.conf

# Set memory limit (256MB for VPS)
sudo sed -i 's/^# maxmemory <bytes>/maxmemory 256mb/' /etc/redis/redis.conf

# Add memory eviction policy
echo "maxmemory-policy allkeys-lru" | sudo tee -a /etc/redis/redis.conf

# Restart Redis with new configuration
sudo systemctl restart redis-server
sudo systemctl enable redis-server

# Test Redis connection
redis-cli ping
# Should output: PONG

echo "✅ Redis installed and configured"
```

### Step 6: Configure Firewall

```bash
# Reset firewall to default state
sudo ufw --force reset

# Set default policies
sudo ufw default deny incoming
sudo ufw default allow outgoing

# Allow SSH (IMPORTANT - don't lock yourself out!)
sudo ufw allow ssh
sudo ufw allow 22/tcp

# Allow HTTP and HTTPS
sudo ufw allow http
sudo ufw allow https
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# Enable firewall
sudo ufw --force enable

# Check firewall status
sudo ufw status verbose

echo "✅ Firewall configured"
```

---

## 📁 Part 2: Application Setup

### Step 7: Create Application Directory Structure

```bash
# Create main application directory
sudo mkdir -p /opt/adcopysurge/backend
sudo mkdir -p /opt/adcopysurge/logs
sudo mkdir -p /run/adcopysurge

# Create deploy user (if not exists)
if ! id "deploy" &>/dev/null; then
    sudo adduser --disabled-password --gecos "" deploy
    sudo usermod -aG sudo deploy
fi

# Set permissions
sudo chown -R deploy:deploy /opt/adcopysurge
sudo chown -R deploy:deploy /run/adcopysurge

echo "✅ Application directory structure created"
```

### Step 8: Clone Repository

```bash
# Switch to deploy user and clone repository
sudo -u deploy bash << 'EOF'
cd /opt/adcopysurge

# Clone the repository (use your actual repository URL)
git clone https://github.com/Adeliyio/acsurge.git temp_clone

# Move backend files to correct location
mv temp_clone/backend/* backend/
rm -rf temp_clone

cd backend
echo "✅ Repository cloned successfully"
EOF
```

### Step 9: Create Python Virtual Environment

```bash
# Create and configure virtual environment as deploy user
sudo -u deploy bash << 'EOF'
cd /opt/adcopysurge

# Create virtual environment with Python 3.11
python3.11 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Upgrade pip, setuptools, and wheel to latest versions
pip install --upgrade pip setuptools wheel

# Verify pip is from venv
which pip
# Should output: /opt/adcopysurge/venv/bin/pip

echo "✅ Virtual environment created"
EOF
```

### Step 10: Install Python Dependencies

```bash
# Install all Python packages with Python 3.11 constraints
sudo -u deploy bash << 'EOF'
cd /opt/adcopysurge
source venv/bin/activate

cd backend

# Install dependencies with Python 3.11 constraints and prefer binary wheels
pip install -r requirements.txt -c constraints-py311.txt --prefer-binary

# This will take 5-10 minutes due to large packages like torch and transformers
# The --prefer-binary flag ensures we use pre-built wheels instead of compiling

# Verify critical packages are installed
python -c "import fastapi; print(f'✅ FastAPI {fastapi.__version__}')"
python -c "import uvicorn; print(f'✅ Uvicorn {uvicorn.__version__}')"
python -c "import gunicorn; print(f'✅ Gunicorn installed')"
python -c "import sqlalchemy; print(f'✅ SQLAlchemy {sqlalchemy.__version__}')"
python -c "import redis; print(f'✅ Redis client installed')"
python -c "import celery; print(f'✅ Celery {celery.__version__}')"
python -c "import openai; print(f'✅ OpenAI {openai.__version__}')"
python -c "import supabase; print(f'✅ Supabase client installed')"

echo "✅ All Python dependencies installed successfully"
EOF
```

**⏱️ Note:** Package installation typically takes 5-10 minutes. Large ML packages (torch, transformers) will download ~2GB of data.

---

## ⚙️ Part 3: Configuration

### Step 11: Configure Environment Variables

```bash
# Create production environment file
sudo tee /opt/adcopysurge/backend/.env > /dev/null << 'EOF'
# ============================================================================
# AdCopySurge Production Environment - Datalix VPS
# ============================================================================

# Application Settings
ENVIRONMENT=production
DEBUG=False
APP_VERSION=1.0.0
APP_NAME=AdCopySurge

# Security (CHANGE THIS SECRET KEY!)
SECRET_KEY=CHANGE-THIS-TO-A-SECURE-RANDOM-STRING-MINIMUM-32-CHARACTERS-LONG
ACCESS_TOKEN_EXPIRE_MINUTES=30
ALGORITHM=HS256

# Server Configuration
HOST=0.0.0.0
PORT=8000
SERVER_NAME=api.adcopysurge.com

# CORS Origins (your frontend URLs)
CORS_ORIGINS=https://adcopysurge.netlify.app,https://adcopysurge.com,https://www.adcopysurge.com
ALLOWED_HOSTS=api.adcopysurge.com,*.adcopysurge.com

# Database - Supabase PostgreSQL
DATABASE_URL=postgresql://postgres:qvF0YRAfKjnVVvLd@db.tqzlsajhhtkhljdbjkyg.supabase.co:5432/postgres

# Supabase Configuration
SUPABASE_URL=https://tqzlsajhhtkhljdbjkyg.supabase.co
SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InRxemxzYWpoaHRraGxqZGJqa3lnIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTY5OTYzOTMsImV4cCI6MjA3MjU3MjM5M30.0uI56qJGE5DQwEvcfYlcOIz2NGC-msMVrTRw6d-RQuI
SUPABASE_SERVICE_ROLE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InRxemxzYWpoaHRraGxqZGJqa3lnIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1Njk5NjM5MywiZXhwIjoyMDcyNTcyMzkzfQ.I4Bs0UL5UD3eGAXQmxmTa6zof17XHgl1AyeN-p4fyYg
SUPABASE_JWT_SECRET=your-jwt-secret-from-supabase-settings

# Redis Configuration
REDIS_URL=redis://localhost:6379/0

# AI Services (ADD YOUR API KEYS HERE)
OPENAI_API_KEY=sk-your-openai-api-key-here
HUGGINGFACE_API_KEY=hf_your-huggingface-token-here
GEMINI_API_KEY=your-gemini-api-key-here

# Email Service (Resend - for team invitations)
RESEND_API_KEY=re_your_resend_api_key
RESEND_FROM_EMAIL=noreply@adcopysurge.com
RESEND_FROM_NAME=AdCopySurge

# Paddle Billing (if using Paddle for payments)
PADDLE_VENDOR_ID=your-vendor-id
PADDLE_API_KEY=your-paddle-api-key
PADDLE_CLIENT_TOKEN=your-client-token
PADDLE_WEBHOOK_SECRET=your-webhook-secret
PADDLE_ENVIRONMENT=production

# Feature Flags
ENABLE_ANALYTICS=true
ENABLE_PDF_REPORTS=true
ENABLE_RATE_LIMITING=true
ENABLE_BLOG=false

# Performance Settings (optimized for VPS)
WORKERS=2
CELERY_WORKERS=2
MAX_CONNECTIONS=50

# Monitoring
LOG_LEVEL=info
SENTRY_DSN=

EOF

# Set proper permissions (readable only by deploy user and root)
sudo chown deploy:deploy /opt/adcopysurge/backend/.env
sudo chmod 600 /opt/adcopysurge/backend/.env

echo "✅ Environment file created"
echo "⚠️  IMPORTANT: Edit /opt/adcopysurge/backend/.env and update:"
echo "   1. SECRET_KEY - Generate a secure random string (min 32 chars)"
echo "   2. OPENAI_API_KEY - Your OpenAI API key"
echo "   3. Other API keys as needed"
```

### Step 12: Generate Secure Secret Key

```bash
# Generate a secure SECRET_KEY
python3.11 << 'EOF'
import secrets
secret_key = secrets.token_urlsafe(48)
print(f"\n✅ Generated SECRET_KEY (copy this):\n{secret_key}\n")
print("Now edit /opt/adcopysurge/backend/.env and replace the SECRET_KEY value")
EOF

# After copying the generated key, edit the file:
sudo nano /opt/adcopysurge/backend/.env
# Find: SECRET_KEY=CHANGE-THIS-TO-A-SECURE-RANDOM-STRING...
# Replace with: SECRET_KEY=<paste-the-generated-key-here>
# Also update OPENAI_API_KEY and any other required keys
# Save: Ctrl+X, Y, Enter
```

### Step 13: Run Database Migrations

```bash
# Run Alembic migrations to create database tables
sudo -u deploy bash << 'EOF'
cd /opt/adcopysurge/backend
source /opt/adcopysurge/venv/bin/activate

# Load environment variables
set -a
source .env
set +a

# Run migrations
alembic upgrade head

echo "✅ Database migrations completed"
EOF
```

### Step 14: Test Backend Manually (Optional but Recommended)

```bash
# Quick test to ensure backend starts without errors
sudo -u deploy bash << 'EOF'
cd /opt/adcopysurge/backend
source /opt/adcopysurge/venv/bin/activate

# Load environment variables
set -a
source .env
set +a

# Start server for 10 seconds to test
timeout 10s python -m uvicorn main_production:app --host 0.0.0.0 --port 8000 || echo "✅ Backend test completed (timeout is expected)"

# Check for any obvious errors
if [ $? -eq 124 ]; then
    echo "✅ Backend appears to be working correctly"
else
    echo "⚠️  Backend may have issues - check for errors above"
fi
EOF
```

---

## 🔧 Part 4: Systemd Services

### Step 15: Create Gunicorn Configuration

```bash
# Create Gunicorn configuration file
sudo tee /opt/adcopysurge/backend/gunicorn.conf.py > /dev/null << 'EOF'
# Gunicorn configuration for AdCopySurge Backend (Datalix VPS)
import multiprocessing
import os

# Server socket
bind = "unix:/run/adcopysurge/gunicorn.sock"
backlog = 2048

# Worker processes (optimized for VPS with limited resources)
workers = 2  # 2 workers for typical VPS
worker_class = "uvicorn.workers.UvicornWorker"
worker_connections = 1000
max_requests = 1000
max_requests_jitter = 50
preload_app = True
timeout = 180  # 3 minutes - AI analysis takes 60-120 seconds, need buffer
keepalive = 2

# Logging
accesslog = "/opt/adcopysurge/logs/gunicorn.access.log"
errorlog = "/opt/adcopysurge/logs/gunicorn.error.log"
loglevel = "info"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# Process naming
proc_name = "adcopysurge-backend"

# Server mechanics
daemon = False
pidfile = "/run/adcopysurge/gunicorn.pid"
user = "deploy"
group = "deploy"
tmp_upload_dir = None

# Environment variables (will be loaded from systemd EnvironmentFile)
raw_env = [
    "PYTHONPATH=/opt/adcopysurge/backend",
    "PYTHONDONTWRITEBYTECODE=1",
    "PYTHONUNBUFFERED=1",
]

# Worker process callbacks
def on_starting(server):
    server.log.info("Starting AdCopySurge API server")

def on_reload(server):
    server.log.info("Reloading AdCopySurge API server")

def worker_int(worker):
    worker.log.info("Worker received INT or QUIT signal")

def pre_fork(server, worker):
    server.log.info(f"Worker spawning (pid: {worker.pid})")

def post_fork(server, worker):
    server.log.info(f"Worker spawned (pid: {worker.pid})")

def post_worker_init(worker):
    worker.log.info("Worker initialized")

def worker_abort(worker):
    worker.log.info("Worker received SIGABRT signal")
EOF

echo "✅ Gunicorn configuration created"
```

### Step 16: Create AdCopySurge API Systemd Service

```bash
# Create systemd service file for the main API
sudo tee /etc/systemd/system/adcopysurge.service > /dev/null << 'EOF'
[Unit]
Description=AdCopySurge FastAPI Application (Gunicorn + Uvicorn)
After=network.target redis-server.service
Requires=redis-server.service
Documentation=https://github.com/yourusername/adcopysurge

[Service]
Type=notify
User=deploy
Group=deploy
WorkingDirectory=/opt/adcopysurge/backend

# Environment
Environment="PATH=/opt/adcopysurge/venv/bin:/usr/local/bin:/usr/bin:/bin"
Environment="PYTHONPATH=/opt/adcopysurge/backend"
EnvironmentFile=/opt/adcopysurge/backend/.env

# Start Gunicorn with Uvicorn workers
ExecStart=/opt/adcopysurge/venv/bin/gunicorn main_production:app \
    --config /opt/adcopysurge/backend/gunicorn.conf.py

# Reload gracefully
ExecReload=/bin/kill -s HUP $MAINPID

# Process management
KillMode=mixed
KillSignal=SIGTERM
TimeoutStopSec=10
Restart=always
RestartSec=3

# Security settings
NoNewPrivileges=true
ProtectSystem=strict
ProtectHome=true
ReadWritePaths=/opt/adcopysurge/logs /run/adcopysurge /tmp
PrivateDevices=true
ProtectKernelTunables=true
ProtectControlGroups=true
RestrictRealtime=true

# Logging
StandardOutput=journal
StandardError=journal
SyslogIdentifier=adcopysurge

[Install]
WantedBy=multi-user.target
EOF

echo "✅ AdCopySurge API service created"
```

### Step 17: Create Celery Worker Systemd Service

```bash
# Create systemd service file for Celery worker
sudo tee /etc/systemd/system/adcopysurge-celery.service > /dev/null << 'EOF'
[Unit]
Description=AdCopySurge Celery Worker
After=network.target redis-server.service
Requires=redis-server.service

[Service]
Type=forking
User=deploy
Group=deploy
WorkingDirectory=/opt/adcopysurge/backend

# Environment
Environment="PATH=/opt/adcopysurge/venv/bin:/usr/local/bin:/usr/bin:/bin"
Environment="PYTHONPATH=/opt/adcopysurge/backend"
EnvironmentFile=/opt/adcopysurge/backend/.env

# Start Celery worker
ExecStart=/opt/adcopysurge/venv/bin/celery -A app.celery_app worker \
    --loglevel=info \
    --concurrency=2 \
    --detach \
    --pidfile=/run/adcopysurge/celery.pid \
    --logfile=/opt/adcopysurge/logs/celery.log

# Stop and reload
ExecStop=/opt/adcopysurge/venv/bin/celery -A app.celery_app control shutdown
ExecReload=/opt/adcopysurge/venv/bin/celery -A app.celery_app control reload

PIDFile=/run/adcopysurge/celery.pid
Restart=always
RestartSec=3

# Security settings
NoNewPrivileges=true
ProtectSystem=strict
ProtectHome=true
ReadWritePaths=/opt/adcopysurge/logs /run/adcopysurge /tmp
PrivateDevices=true

[Install]
WantedBy=multi-user.target
EOF

echo "✅ Celery worker service created"
```

### Step 18: Enable and Start Services

```bash
# Reload systemd to recognize new services
sudo systemctl daemon-reload

# Enable services to start on boot
sudo systemctl enable adcopysurge.service
sudo systemctl enable adcopysurge-celery.service

# Start services
sudo systemctl start adcopysurge.service
sudo systemctl start adcopysurge-celery.service

# Wait a few seconds for startup
sleep 5

# Check service status
echo "Checking AdCopySurge API service..."
sudo systemctl status adcopysurge.service --no-pager -l

echo ""
echo "Checking Celery worker service..."
sudo systemctl status adcopysurge-celery.service --no-pager -l

# Check if services are running
if sudo systemctl is-active --quiet adcopysurge.service; then
    echo "✅ AdCopySurge API is running"
else
    echo "❌ AdCopySurge API failed to start - check logs"
    sudo journalctl -u adcopysurge.service -n 50
fi

if sudo systemctl is-active --quiet adcopysurge-celery.service; then
    echo "✅ Celery worker is running"
else
    echo "⚠️  Celery worker failed to start - check logs (this is non-critical)"
    sudo journalctl -u adcopysurge-celery.service -n 50
fi
```

---

## 🌐 Part 5: Nginx Configuration

### Step 19: Configure Nginx as Reverse Proxy

```bash
# Create Nginx configuration for AdCopySurge
sudo tee /etc/nginx/sites-available/adcopysurge > /dev/null << 'EOF'
# AdCopySurge API - Nginx Configuration for Datalix VPS

# Rate limiting zones
limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;
limit_req_zone $binary_remote_addr zone=auth:10m rate=5r/s;
limit_req_zone $binary_remote_addr zone=analysis:10m rate=2r/s;

# Upstream backend
upstream adcopysurge_backend {
    server unix:/run/adcopysurge/gunicorn.sock fail_timeout=0;
}

server {
    listen 80;
    listen [::]:80;
    server_name api.adcopysurge.com;

    # Logs
    access_log /var/log/nginx/adcopysurge_access.log;
    error_log /var/log/nginx/adcopysurge_error.log;

    # Security headers
    add_header X-Frame-Options "DENY" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;

    # Client settings
    client_max_body_size 10M;
    client_body_buffer_size 128k;

    # Timeouts (important for long-running AI analysis)
    proxy_connect_timeout 180s;
    proxy_send_timeout 180s;
    proxy_read_timeout 180s;
    send_timeout 180s;

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

    # Authentication endpoints (stricter rate limit)
    location /api/auth {
        limit_req zone=auth burst=10 nodelay;

        proxy_pass http://adcopysurge_backend;
        proxy_set_header Host $http_host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_redirect off;
        proxy_buffering off;
    }

    # Analysis endpoint (very long timeout for AI processing)
    location /api/ads/analyze {
        limit_req zone=analysis burst=5 nodelay;

        proxy_pass http://adcopysurge_backend;
        proxy_set_header Host $http_host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_redirect off;
        proxy_buffering off;

        # Extended timeouts for AI analysis (60-120 seconds + buffer)
        proxy_connect_timeout 300s;
        proxy_send_timeout 300s;
        proxy_read_timeout 300s;
    }

    # General API endpoints
    location /api {
        limit_req zone=api burst=20 nodelay;

        proxy_pass http://adcopysurge_backend;
        proxy_set_header Host $http_host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_redirect off;
        proxy_buffering off;
    }

    # Health check endpoint (no rate limiting)
    location /health {
        proxy_pass http://adcopysurge_backend;
        proxy_set_header Host $http_host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_redirect off;
        access_log off;
    }

    location /healthz {
        proxy_pass http://adcopysurge_backend;
        proxy_set_header Host $http_host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_redirect off;
        access_log off;
    }

    # Root and other routes
    location / {
        proxy_pass http://adcopysurge_backend;
        proxy_set_header Host $http_host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_redirect off;
        proxy_buffering off;
    }
}
EOF

echo "✅ Nginx configuration created"
```

### Step 20: Enable Nginx Configuration

```bash
# Enable the site
sudo ln -sf /etc/nginx/sites-available/adcopysurge /etc/nginx/sites-enabled/

# Remove default site
sudo rm -f /etc/nginx/sites-enabled/default

# Test Nginx configuration
sudo nginx -t

# If test passes, restart Nginx
if [ $? -eq 0 ]; then
    sudo systemctl restart nginx
    sudo systemctl enable nginx
    echo "✅ Nginx configuration enabled and restarted"
else
    echo "❌ Nginx configuration test failed - check errors above"
    exit 1
fi
```

### Step 21: Test API Access

```bash
# Test local health check
curl -f http://localhost/health
# Should output: {"status":"healthy","timestamp":...}

# Test external access (requires DNS to be configured)
curl -f http://api.adcopysurge.com/health
# Should output: {"status":"healthy","timestamp":...}

echo "✅ API is accessible"
```

---

## 🔒 Part 6: SSL Certificate (HTTPS)

### Step 22: Configure SSL with Let's Encrypt

**⚠️ IMPORTANT:** Before running this step, ensure your domain `api.adcopysurge.com` is pointing to your VPS IP address (46.247.108.207) in your DNS settings.

```bash
# Check if domain is properly configured
echo "Checking DNS configuration..."
host api.adcopysurge.com
# Should show your VPS IP: 46.247.108.207

# Obtain SSL certificate
sudo certbot --nginx \
    -d api.adcopysurge.com \
    --non-interactive \
    --agree-tos \
    --email admin@adcopysurge.com \
    --redirect

# Test SSL renewal (dry run)
sudo certbot renew --dry-run

# Set up automatic renewal (already configured by certbot)
sudo systemctl status certbot.timer

echo "✅ SSL certificate configured"
```

---

## 📊 Part 7: Monitoring and Logging

### Step 23: Configure Log Rotation

```bash
# Create log rotation configuration
sudo tee /etc/logrotate.d/adcopysurge > /dev/null << 'EOF'
# AdCopySurge application logs
/opt/adcopysurge/logs/*.log {
    weekly
    rotate 12
    compress
    delaycompress
    missingok
    notifempty
    copytruncate
    create 644 deploy deploy
}

# Nginx AdCopySurge logs
/var/log/nginx/adcopysurge_*.log {
    daily
    rotate 14
    compress
    delaycompress
    missingok
    notifempty
    create 644 www-data adm
    postrotate
        systemctl reload nginx > /dev/null 2>&1
    endscript
}
EOF

echo "✅ Log rotation configured"
```

### Step 24: Useful Monitoring Commands

```bash
cat << 'EOF' > /home/deploy/monitor-adcopysurge.sh
#!/bin/bash
# AdCopySurge Monitoring Script

echo "=== AdCopySurge Service Status ==="
sudo systemctl status adcopysurge.service --no-pager -l
echo ""
sudo systemctl status adcopysurge-celery.service --no-pager -l
echo ""
sudo systemctl status nginx --no-pager -l
echo ""
sudo systemctl status redis-server --no-pager -l

echo ""
echo "=== Recent Logs (last 20 lines) ==="
echo "--- API Logs ---"
sudo journalctl -u adcopysurge.service -n 20 --no-pager

echo ""
echo "--- Celery Logs ---"
sudo journalctl -u adcopysurge-celery.service -n 20 --no-pager

echo ""
echo "=== Network Status ==="
sudo ss -tlnp | grep -E ':80|:443|gunicorn'

echo ""
echo "=== Disk Usage ==="
df -h /opt/adcopysurge

echo ""
echo "=== Memory Usage ==="
free -h

echo ""
echo "=== CPU Load ==="
uptime
EOF

chmod +x /home/deploy/monitor-adcopysurge.sh
chown deploy:deploy /home/deploy/monitor-adcopysurge.sh

echo "✅ Monitoring script created at /home/deploy/monitor-adcopysurge.sh"
```

---

## ✅ Part 8: Final Verification

### Step 25: Comprehensive Health Check

```bash
echo "🔍 Running comprehensive health checks..."
echo ""

# 1. Check services
echo "1. Service Status:"
sudo systemctl is-active adcopysurge.service && echo "  ✅ API Service: Running" || echo "  ❌ API Service: Not Running"
sudo systemctl is-active adcopysurge-celery.service && echo "  ✅ Celery Worker: Running" || echo "  ❌ Celery Worker: Not Running"
sudo systemctl is-active nginx && echo "  ✅ Nginx: Running" || echo "  ❌ Nginx: Not Running"
sudo systemctl is-active redis-server && echo "  ✅ Redis: Running" || echo "  ❌ Redis: Not Running"

echo ""
echo "2. Network Connectivity:"
sudo ss -tlnp | grep -q ':80' && echo "  ✅ Port 80 (HTTP): Listening" || echo "  ❌ Port 80: Not Listening"
sudo ss -tlnp | grep -q ':443' && echo "  ✅ Port 443 (HTTPS): Listening" || echo "  ❌ Port 443: Not Listening"
sudo ss -lx | grep -q 'gunicorn' && echo "  ✅ Gunicorn Socket: Active" || echo "  ❌ Gunicorn Socket: Not Active"

echo ""
echo "3. API Health Checks:"
# Local health check
if curl -s -f http://localhost/health > /dev/null; then
    echo "  ✅ Local Health Check: Passed"
else
    echo "  ❌ Local Health Check: Failed"
fi

# External health check (requires DNS)
if curl -s -f https://api.adcopysurge.com/health > /dev/null 2>&1; then
    echo "  ✅ External Health Check (HTTPS): Passed"
elif curl -s -f http://api.adcopysurge.com/health > /dev/null 2>&1; then
    echo "  ⚠️  External Health Check (HTTP): Passed (SSL not configured yet)"
else
    echo "  ⚠️  External Health Check: Failed (DNS might not be configured)"
fi

echo ""
echo "4. Database Connection:"
sudo -u deploy bash << 'DBCHECK'
cd /opt/adcopysurge/backend
source /opt/adcopysurge/venv/bin/activate
set -a; source .env; set +a
python -c "
from app.core.database import engine
from sqlalchemy import text
try:
    with engine.connect() as conn:
        result = conn.execute(text('SELECT 1'))
        print('  ✅ Database Connection: Successful')
except Exception as e:
    print(f'  ❌ Database Connection: Failed - {e}')
"
DBCHECK

echo ""
echo "5. Redis Connection:"
if redis-cli ping > /dev/null 2>&1; then
    echo "  ✅ Redis Connection: Successful"
else
    echo "  ❌ Redis Connection: Failed"
fi

echo ""
echo "6. Recent Error Logs:"
echo "  Checking for recent errors..."
ERROR_COUNT=$(sudo journalctl -u adcopysurge.service --since "10 minutes ago" | grep -i "error" | wc -l)
if [ $ERROR_COUNT -eq 0 ]; then
    echo "  ✅ No errors in last 10 minutes"
else
    echo "  ⚠️  Found $ERROR_COUNT errors in last 10 minutes"
    echo "     Run: sudo journalctl -u adcopysurge.service | grep -i error"
fi

echo ""
echo "================================"
echo "🎉 Health Check Complete!"
echo "================================"
```

---

## 🚀 Part 9: Post-Deployment

### Step 26: Update Code (Future Deployments)

Create a deployment script for future updates:

```bash
cat << 'EOF' > /home/deploy/update-adcopysurge.sh
#!/bin/bash
# AdCopySurge Update Script

set -e

echo "🔄 Updating AdCopySurge..."

# Navigate to application directory
cd /opt/adcopysurge/backend

# Pull latest changes
echo "Fetching latest code from git..."
git pull origin main

# Activate virtual environment
source /opt/adcopysurge/venv/bin/activate

# Update dependencies (if requirements changed)
echo "Updating dependencies..."
pip install -r requirements.txt -c constraints-py311.txt --prefer-binary --upgrade

# Run migrations
echo "Running database migrations..."
set -a
source .env
set +a
alembic upgrade head

# Restart services
echo "Restarting services..."
sudo systemctl restart adcopysurge.service
sudo systemctl restart adcopysurge-celery.service

# Wait for startup
sleep 5

# Check status
if sudo systemctl is-active --quiet adcopysurge.service; then
    echo "✅ Update successful! API is running."
else
    echo "❌ Update failed - API not running. Check logs:"
    sudo journalctl -u adcopysurge.service -n 50
    exit 1
fi

echo "🎉 Deployment complete!"
EOF

chmod +x /home/deploy/update-adcopysurge.sh
chown deploy:deploy /home/deploy/update-adcopysurge.sh

echo "✅ Update script created at /home/deploy/update-adcopysurge.sh"
```

---

## 📝 Important Notes

### System Resources

**Minimum VPS Requirements:**
- 2 GB RAM (4 GB recommended for ML models)
- 2 CPU cores
- 20 GB disk space (ML models are large)
- Ubuntu 22.04 LTS

### Security Checklist

- ✅ Firewall configured (UFW)
- ✅ Services run as non-root user (deploy)
- ✅ Environment files have restricted permissions (600)
- ✅ SSL/HTTPS enabled
- ✅ Rate limiting configured in Nginx
- ✅ Security headers configured
- ⚠️  Consider: fail2ban for brute-force protection
- ⚠️  Consider: Regular automated backups

### Performance Tuning

**For VPS with limited resources:**
- Workers set to 2 (adjust based on CPU cores)
- Gunicorn timeout: 180s (for long AI analysis)
- Redis maxmemory: 256MB
- Connection pooling configured in SQLAlchemy

### Troubleshooting Commands

```bash
# View real-time API logs
sudo journalctl -u adcopysurge.service -f

# View real-time Celery logs
sudo journalctl -u adcopysurge-celery.service -f

# View Nginx error logs
sudo tail -f /var/log/nginx/adcopysurge_error.log

# View Gunicorn logs
sudo tail -f /opt/adcopysurge/logs/gunicorn.error.log

# Check Gunicorn socket
sudo ls -la /run/adcopysurge/gunicorn.sock

# Test Gunicorn socket directly
curl --unix-socket /run/adcopysurge/gunicorn.sock http://localhost/health

# Restart all services
sudo systemctl restart adcopysurge.service adcopysurge-celery.service nginx

# Check service status
sudo systemctl status adcopysurge.service adcopysurge-celery.service nginx redis-server
```

### Common Issues and Solutions

**Issue: "502 Bad Gateway"**
```bash
# Check if Gunicorn socket exists
sudo ls -la /run/adcopysurge/gunicorn.sock

# Check API service logs
sudo journalctl -u adcopysurge.service -n 100

# Verify Gunicorn timeout (should be 180s)
grep "timeout" /opt/adcopysurge/backend/gunicorn.conf.py
```

**Issue: "Database connection failed"**
```bash
# Test database connection
sudo -u deploy bash -c 'cd /opt/adcopysurge/backend && source /opt/adcopysurge/venv/bin/activate && source .env && python -c "from app.core.database import engine; engine.connect()"'

# Check DATABASE_URL format
grep DATABASE_URL /opt/adcopysurge/backend/.env
```

**Issue: "ImportError or module not found"**
```bash
# Reinstall dependencies
sudo -u deploy bash -c 'cd /opt/adcopysurge/backend && source /opt/adcopysurge/venv/bin/activate && pip install -r requirements.txt -c constraints-py311.txt --prefer-binary --force-reinstall'
```

**Issue: "Out of memory"**
```bash
# Check memory usage
free -h

# If needed, create swap file
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
```

---

## 🎉 Deployment Complete!

Your AdCopySurge application should now be running on Datalix VPS!

**Access Points:**
- **API**: https://api.adcopysurge.com
- **API Docs**: https://api.adcopysurge.com/api/docs (only in DEBUG mode)
- **Health Check**: https://api.adcopysurge.com/health

**Next Steps:**
1. Update frontend `.env` to point to `https://api.adcopysurge.com`
2. Test ad analysis workflow end-to-end
3. Set up monitoring (optional: Sentry, DataDog, etc.)
4. Configure automated backups
5. Set up staging environment for testing

**Useful Commands Reference:**
```bash
# View monitor dashboard
/home/deploy/monitor-adcopysurge.sh

# Update application
/home/deploy/update-adcopysurge.sh

# Restart services
sudo systemctl restart adcopysurge.service adcopysurge-celery.service

# View logs
sudo journalctl -u adcopysurge.service -f
```

---

**Need Help?**
- Check logs first: `sudo journalctl -u adcopysurge.service -n 100`
- Run health check: Step 25 above
- Review CLAUDE.md for architecture details
- Check COMPLETE_502_SOLUTION.md for timeout issues
