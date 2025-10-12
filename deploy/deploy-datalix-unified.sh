#!/bin/bash
# AdCopySurge Unified Deployment Script for Datalix VPS
# Deploys both React frontend and FastAPI backend on single server
# Domain: v44954.datalix.de
# 
# Run this script as root on your Ubuntu 22.04 Datalix VPS

set -e  # Exit on any error

echo "🚀 AdCopySurge Unified VPS Deployment Starting..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
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

print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

# Configuration
DOMAIN="v44954.datalix.de"
APP_DIR="/srv/adcopysurge"
BACKEND_DIR="$APP_DIR/app/backend"
FRONTEND_DIR="$APP_DIR/app/frontend"
DEPLOY_USER="deploy"
NGINX_SITE="adcopysurge"

# =============================================================================
# STEP 1: System Updates and Security
# =============================================================================
print_step "1. Updating system and configuring security..."

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

if ! id "$DEPLOY_USER" &>/dev/null; then
    adduser --disabled-password --gecos "" $DEPLOY_USER
    usermod -aG sudo $DEPLOY_USER
    
    # Create SSH directory for deploy user
    mkdir -p /home/$DEPLOY_USER/.ssh
    chmod 700 /home/$DEPLOY_USER/.ssh
    chown $DEPLOY_USER:$DEPLOY_USER /home/$DEPLOY_USER/.ssh
    
    print_info "Deploy user '$DEPLOY_USER' created"
else
    print_info "Deploy user '$DEPLOY_USER' already exists"
fi

print_step "2. ✅ Deploy user configured"

# =============================================================================
# STEP 3: Install System Dependencies
# =============================================================================
print_step "3. Installing system packages..."

# Install Node.js 18 LTS (for React build)
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
apt install -y nodejs

# Install other dependencies
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
    tree \
    redis-server

# Add deadsnakes PPA for Python 3.11
add-apt-repository ppa:deadsnakes/ppa -y
apt update

# Install Python 3.11
apt install -y python3.11 python3.11-venv python3.11-dev python3.11-distutils

# Install pip for Python 3.11
curl -sS https://bootstrap.pypa.io/get-pip.py | python3.11

# Verify installations
print_info "Node.js version: $(node --version)"
print_info "npm version: $(npm --version)"
print_info "Python version: $(python3.11 --version)"

print_step "3. ✅ System packages installed"

# =============================================================================
# STEP 4: Configure Redis
# =============================================================================
print_step "4. Configuring Redis..."

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

mkdir -p $APP_DIR/{logs,run}
chown -R $DEPLOY_USER:$DEPLOY_USER $APP_DIR

# Clone repository as deploy user
sudo -u $DEPLOY_USER bash << EOF
cd $APP_DIR

if [ -d "app" ]; then
    print_info "Updating existing repository..."
    cd app
    git pull origin main
else
    print_info "Cloning repository..."
    git clone https://github.com/yourusername/adcopysurge.git app
fi

print_info "Repository cloned/updated successfully"
EOF

print_step "5. ✅ Application directory structure created"

# =============================================================================
# STEP 6: Setup Backend (Python Environment)
# =============================================================================
print_step "6. Setting up Python backend environment..."

sudo -u $DEPLOY_USER bash << EOF
cd $BACKEND_DIR

# Create virtual environment
python3.11 -m venv venv

# Activate and upgrade pip
source venv/bin/activate
pip install --upgrade pip wheel

# Install dependencies
pip install -r requirements.txt

# Install additional production dependencies
pip install gunicorn

# Verify key packages
python -c "import fastapi, uvicorn, gunicorn, celery, redis; print('✅ All packages installed successfully')"

print_info "Python environment configured successfully"
EOF

print_step "6. ✅ Python environment configured"

# =============================================================================
# STEP 7: Setup Frontend (React Build)
# =============================================================================
print_step "7. Building React frontend..."

sudo -u $DEPLOY_USER bash << EOF
cd $FRONTEND_DIR

# Install dependencies
npm install

# Build for production
NODE_ENV=production npm run build

# Verify build
if [ -d "build" ] && [ -f "build/index.html" ]; then
    print_info "React build completed successfully"
    ls -la build/
else
    print_error "React build failed!"
    exit 1
fi
EOF

print_step "7. ✅ React frontend built"

# =============================================================================
# STEP 8: Configure Environment Variables
# =============================================================================
print_step "8. Setting up environment configuration..."

# Create environment file (you'll need to fill in actual values)
cat > $BACKEND_DIR/.env << 'EOF'
# AdCopySurge Production Environment - FILL IN ACTUAL VALUES
ENVIRONMENT=production
DEBUG=false
APP_NAME=AdCopySurge
HOST=127.0.0.1
PORT=8000

# Security - CHANGE THESE VALUES
SECRET_KEY=your-super-secure-secret-key-change-this-32-chars-minimum
ACCESS_TOKEN_EXPIRE_MINUTES=30
ALGORITHM=HS256

# Server Configuration
SERVER_NAME=v44954.datalix.de
CORS_ORIGINS=http://v44954.datalix.de,https://v44954.datalix.de
ALLOWED_HOSTS=v44954.datalix.de,localhost,127.0.0.1

# Database (Supabase) - UPDATE WITH YOUR ACTUAL VALUES
DATABASE_URL=postgresql://postgres:YOUR_PASSWORD@db.tqzlsajhhtkhljdbjkyg.supabase.co:5432/postgres

# Supabase Configuration - UPDATE WITH YOUR ACTUAL VALUES
SUPABASE_URL=https://tqzlsajhhtkhljdbjkyg.supabase.co
SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InRxemxzYWpoaHRraGxqZGJqa3lnIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTY5OTYzOTMsImV4cCI6MjA3MjU3MjM5M30.0uI56qJGE5DQwEvcfYlcOIz2NGC-msMVrTRw6d-RQuI
SUPABASE_SERVICE_ROLE_KEY=YOUR_SERVICE_ROLE_KEY_HERE

# Redis Configuration
REDIS_URL=redis://127.0.0.1:6379/0

# AI Services - ADD YOUR API KEYS
OPENAI_API_KEY=YOUR_OPENAI_API_KEY_HERE
OPENAI_MAX_TOKENS=2000

# Feature Flags
ENABLE_BLOG=true
ENABLE_ANALYTICS=true
ENABLE_PDF_REPORTS=true
ENABLE_RATE_LIMITING=true

# Performance Settings
WORKERS=2
KEEP_ALIVE=2
MAX_CONNECTIONS=50

LOG_LEVEL=info
EOF

chown $DEPLOY_USER:$DEPLOY_USER $BACKEND_DIR/.env
chmod 600 $BACKEND_DIR/.env

print_warning "IMPORTANT: Edit $BACKEND_DIR/.env with your actual values!"
print_warning "Especially: SECRET_KEY, DATABASE_URL, SUPABASE_SERVICE_ROLE_KEY, OPENAI_API_KEY"

print_step "8. ✅ Environment configuration created (needs manual completion)"

# =============================================================================
# STEP 9: Setup Nginx Configuration
# =============================================================================
print_step "9. Configuring Nginx..."

# Copy the unified nginx configuration
cp $APP_DIR/app/deploy/nginx-unified.conf /etc/nginx/sites-available/$NGINX_SITE

# Update domain name if different
sed -i "s/v44954\\.datalix\\.de/$DOMAIN/g" /etc/nginx/sites-available/$NGINX_SITE

# Update frontend build path
sed -i "s|/srv/adcopysurge/app/frontend/build|$FRONTEND_DIR/build|g" /etc/nginx/sites-available/$NGINX_SITE

# Enable the site
ln -sf /etc/nginx/sites-available/$NGINX_SITE /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default

# Test configuration
nginx -t

# Create log directory
mkdir -p /var/log/nginx
chown www-data:www-data /var/log/nginx

print_step "9. ✅ Nginx configured"

# =============================================================================
# STEP 10: Setup Systemd Services
# =============================================================================
print_step "10. Setting up systemd services..."

# Create gunicorn service file
cat > /etc/systemd/system/adcopysurge-backend.service << EOF
[Unit]
Description=AdCopySurge Backend (Gunicorn)
After=network.target

[Service]
User=$DEPLOY_USER
Group=www-data
WorkingDirectory=$BACKEND_DIR
Environment="PATH=$BACKEND_DIR/venv/bin"
EnvironmentFile=$BACKEND_DIR/.env
ExecStart=$BACKEND_DIR/venv/bin/gunicorn main_production:app \\
    --bind 127.0.0.1:8000 \\
    --workers 2 \\
    --worker-class uvicorn.workers.UvicornWorker \\
    --timeout 300 \\
    --keep-alive 2 \\
    --max-requests 1000 \\
    --max-requests-jitter 100 \\
    --access-logfile /var/log/nginx/adcopysurge_gunicorn_access.log \\
    --error-logfile /var/log/nginx/adcopysurge_gunicorn_error.log \\
    --log-level info
ExecReload=/bin/kill -s HUP \$MAINPID
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
EOF

# Create required directories
mkdir -p /var/log/nginx
chown $DEPLOY_USER:www-data /var/log/nginx

# Reload systemd and enable services
systemctl daemon-reload
systemctl enable adcopysurge-backend.service
systemctl enable nginx

print_step "10. ✅ Systemd services configured"

# =============================================================================
# STEP 11: Start Services
# =============================================================================
print_step "11. Starting services..."

# Start backend
systemctl start adcopysurge-backend.service

# Check backend status
if systemctl is-active --quiet adcopysurge-backend.service; then
    print_info "✅ Backend service is running"
else
    print_error "❌ Backend service failed to start"
    systemctl status adcopysurge-backend.service
    exit 1
fi

# Start nginx
systemctl restart nginx

if systemctl is-active --quiet nginx; then
    print_info "✅ Nginx is running"
else
    print_error "❌ Nginx failed to start"
    systemctl status nginx
    exit 1
fi

print_step "11. ✅ Services started successfully"

# =============================================================================
# STEP 12: Verification Tests
# =============================================================================
print_step "12. Running verification tests..."

# Test backend health
print_info "Testing backend health..."
if curl -f http://127.0.0.1:8000/health > /dev/null 2>&1; then
    print_info "✅ Backend health check passed"
else
    print_warning "⚠️  Backend health check failed (might be starting up)"
fi

# Test nginx proxy
print_info "Testing Nginx proxy..."
if curl -f http://localhost/health > /dev/null 2>&1; then
    print_info "✅ Nginx proxy health check passed"
else
    print_warning "⚠️  Nginx proxy health check failed"
fi

# Test frontend
print_info "Testing frontend..."
if curl -f http://localhost/ > /dev/null 2>&1; then
    print_info "✅ Frontend is accessible"
else
    print_warning "⚠️  Frontend test failed"
fi

print_step "12. ✅ Basic verification completed"

# =============================================================================
# DEPLOYMENT COMPLETE
# =============================================================================

echo ""
echo "🎉 AdCopySurge Deployment Complete!"
echo ""
echo -e "${GREEN}✅ Services Status:${NC}"
echo "   - Backend (FastAPI): $(systemctl is-active adcopysurge-backend.service)"
echo "   - Nginx (Proxy): $(systemctl is-active nginx)"
echo "   - Redis: $(systemctl is-active redis-server)"
echo ""
echo -e "${BLUE}🌐 Access your application:${NC}"
echo "   - Frontend: http://$DOMAIN/"
echo "   - API Health: http://$DOMAIN/health"
echo "   - API Docs: http://$DOMAIN/docs (if debug enabled)"
echo ""
echo -e "${YELLOW}⚠️  IMPORTANT NEXT STEPS:${NC}"
echo "1. Edit $BACKEND_DIR/.env with your actual secret keys and API keys"
echo "2. Restart backend service: sudo systemctl restart adcopysurge-backend.service"
echo "3. Configure SSL certificate:"
echo "   sudo certbot --nginx -d $DOMAIN"
echo "4. Test your application thoroughly"
echo ""
echo -e "${GREEN}📋 Useful commands:${NC}"
echo "   - View backend logs: sudo journalctl -u adcopysurge-backend.service -f"
echo "   - View nginx logs: sudo tail -f /var/log/nginx/adcopysurge_*.log"
echo "   - Restart services: sudo systemctl restart adcopysurge-backend nginx"
echo ""
echo "Happy deploying! 🚀"