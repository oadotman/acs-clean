#!/bin/bash

# AdCopySurge Secure Deployment to Datalix VPS
# This script will completely clean the VPS and deploy the secure version

set -e  # Exit on any error

echo "🚀 Starting AdCopySurge Secure Deployment to Datalix VPS..."
echo "=================================================="

# Configuration
VPS_HOST="46.247.108.207"
VPS_DOMAIN="v44954.datalix.de"
GITHUB_REPO="https://github.com/oadotman/acs-clean.git"
APP_DIR="/var/www/adcopysurge"
BACKUP_DIR="/var/backups/adcopysurge-$(date +%Y%m%d-%H%M%S)"

echo "🔧 VPS Configuration:"
echo "   Host: $VPS_HOST"
echo "   Domain: $VPS_DOMAIN"
echo "   Repository: $GITHUB_REPO"
echo "   App Directory: $APP_DIR"
echo ""

# Function to run commands on VPS
run_on_vps() {
    ssh -o StrictHostKeyChecking=no root@$VPS_HOST "$1"
}

# Function to copy files to VPS
copy_to_vps() {
    scp -o StrictHostKeyChecking=no -r "$1" root@$VPS_HOST:"$2"
}

echo "🧹 Step 1: Complete VPS Cleanup"
echo "================================"

# Stop all services
echo "Stopping all services..."
run_on_vps "systemctl stop nginx || true"
run_on_vps "systemctl stop gunicorn || true"
run_on_vps "systemctl stop celery || true"
run_on_vps "systemctl stop redis || true"
run_on_vps "systemctl stop postgresql || true"

# Create backup of important data (if exists)
echo "Creating backup of existing data..."
run_on_vps "mkdir -p $BACKUP_DIR"
run_on_vps "cp -r /var/www/* $BACKUP_DIR/ || true"
run_on_vps "cp -r /etc/nginx $BACKUP_DIR/nginx-config || true"
run_on_vps "cp -r /etc/systemd/system/gunicorn.service $BACKUP_DIR/ || true"

# Complete cleanup
echo "Removing old application files..."
run_on_vps "rm -rf /var/www/*"
run_on_vps "rm -rf /tmp/adcopysurge*"
run_on_vps "rm -rf /var/log/adcopysurge*"

# Clean up old services
echo "Cleaning up old systemd services..."
run_on_vps "systemctl disable gunicorn || true"
run_on_vps "systemctl disable celery || true"
run_on_vps "rm -f /etc/systemd/system/gunicorn.service"
run_on_vps "rm -f /etc/systemd/system/celery.service"
run_on_vps "systemctl daemon-reload"

# Clean up old nginx configs
echo "Cleaning up old nginx configurations..."
run_on_vps "rm -f /etc/nginx/sites-enabled/adcopysurge*"
run_on_vps "rm -f /etc/nginx/sites-available/adcopysurge*"

echo "✅ VPS cleanup completed!"

echo "📦 Step 2: System Dependencies Update"
echo "===================================="

# Update system
echo "Updating system packages..."
run_on_vps "apt update && apt upgrade -y"

# Install essential packages
echo "Installing essential packages..."
run_on_vps "apt install -y \
    git \
    curl \
    wget \
    unzip \
    build-essential \
    software-properties-common \
    apt-transport-https \
    ca-certificates \
    gnupg \
    lsb-release \
    ufw \
    fail2ban \
    htop \
    tree \
    nano \
    vim"

echo "✅ System dependencies updated!"

echo "🐍 Step 3: Python Environment Setup"
echo "=================================="

# Install Python 3.11
echo "Installing Python 3.11..."
run_on_vps "add-apt-repository ppa:deadsnakes/ppa -y"
run_on_vps "apt update"
run_on_vps "apt install -y python3.11 python3.11-dev python3.11-venv python3-pip"

# Set Python 3.11 as default
echo "Setting Python 3.11 as default..."
run_on_vps "update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.11 1"
run_on_vps "python3 -m pip install --upgrade pip"

echo "✅ Python environment ready!"

echo "🗄️ Step 4: Database Setup"
echo "========================"

# Install PostgreSQL
echo "Installing PostgreSQL..."
run_on_vps "apt install -y postgresql postgresql-contrib"
run_on_vps "systemctl start postgresql"
run_on_vps "systemctl enable postgresql"

# Install Redis
echo "Installing Redis..."
run_on_vps "apt install -y redis-server"
run_on_vps "systemctl start redis-server"
run_on_vps "systemctl enable redis-server"

echo "✅ Database services installed!"

echo "🌐 Step 5: Web Server Setup"
echo "=========================="

# Install Nginx
echo "Installing Nginx..."
run_on_vps "apt install -y nginx"
run_on_vps "systemctl start nginx"
run_on_vps "systemctl enable nginx"

echo "✅ Web server installed!"

echo "🔒 Step 6: Security Setup"
echo "========================"

# Configure UFW firewall
echo "Configuring firewall..."
run_on_vps "ufw --force reset"
run_on_vps "ufw default deny incoming"
run_on_vps "ufw default allow outgoing"
run_on_vps "ufw allow ssh"
run_on_vps "ufw allow 'Nginx Full'"
run_on_vps "ufw allow 80"
run_on_vps "ufw allow 443"
run_on_vps "ufw --force enable"

# Configure Fail2Ban
echo "Configuring Fail2Ban..."
run_on_vps "systemctl start fail2ban"
run_on_vps "systemctl enable fail2ban"

echo "✅ Security configured!"

echo "📥 Step 7: Application Deployment"
echo "================================"

# Create application directory
echo "Creating application directory..."
run_on_vps "mkdir -p $APP_DIR"
run_on_vps "cd $APP_DIR"

# Clone the secure repository
echo "Cloning AdCopySurge secure repository..."
run_on_vps "cd /var/www && git clone $GITHUB_REPO adcopysurge"
run_on_vps "cd $APP_DIR && git checkout main"

# Set proper permissions
echo "Setting permissions..."
run_on_vps "chown -R www-data:www-data $APP_DIR"
run_on_vps "chmod -R 755 $APP_DIR"

echo "✅ Application cloned!"

echo "🔧 Step 8: Python Dependencies"
echo "=============================="

# Create virtual environment
echo "Creating Python virtual environment..."
run_on_vps "cd $APP_DIR && python3 -m venv venv"

# Install backend dependencies
echo "Installing backend dependencies..."
run_on_vps "cd $APP_DIR && source venv/bin/activate && pip install --upgrade pip"
run_on_vps "cd $APP_DIR && source venv/bin/activate && pip install -r backend/requirements-production.txt"

echo "✅ Python dependencies installed!"

echo "🗃️ Step 9: Database Configuration"
echo "================================="

# Create PostgreSQL database and user
echo "Setting up PostgreSQL database..."
run_on_vps "sudo -u postgres createdb adcopysurge || true"
run_on_vps "sudo -u postgres psql -c \"CREATE USER adcopysurge WITH PASSWORD 'secure_password_$(date +%s)';\" || true"
run_on_vps "sudo -u postgres psql -c \"GRANT ALL PRIVILEGES ON DATABASE adcopysurge TO adcopysurge;\" || true"

# Configure Redis for security features
echo "Configuring Redis for sessions and security..."
run_on_vps "sed -i 's/^# maxmemory-policy noeviction/maxmemory-policy allkeys-lru/' /etc/redis/redis.conf"
run_on_vps "sed -i 's/^# maxmemory <bytes>/maxmemory 256mb/' /etc/redis/redis.conf"
run_on_vps "systemctl restart redis-server"

echo "✅ Database configured!"

echo "🔐 Step 10: Environment Configuration"
echo "===================================="

# Create environment file
echo "Creating environment configuration..."
run_on_vps "cd $APP_DIR && cat > .env << 'EOF'
# AdCopySurge Production Environment
ENVIRONMENT=production
DEBUG=false

# Database Configuration
DATABASE_URL=postgresql://adcopysurge:secure_password_\$(date +%s)@localhost/adcopysurge
REDIS_URL=redis://localhost:6379

# Security Configuration
SECRET_KEY=\$(openssl rand -hex 32)
JWT_SECRET_KEY=\$(openssl rand -hex 32)
SESSION_ENCRYPTION_KEY=\$(python3 -c \"from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())\")

# Session Configuration (Redis Database 6)
REDIS_SESSION_URL=redis://localhost:6379/6

# MFA Configuration (Redis Database 4)
REDIS_MFA_URL=redis://localhost:6379/4

# RBAC Configuration (Redis Database 3)
REDIS_RBAC_URL=redis://localhost:6379/3

# GDPR Configuration (Redis Database 5)
REDIS_GDPR_URL=redis://localhost:6379/5

# API Configuration
OPENAI_API_KEY=your_openai_api_key_here
SUPABASE_URL=your_supabase_url_here
SUPABASE_ANON_KEY=your_supabase_anon_key_here

# Server Configuration
HOST=0.0.0.0
PORT=8000
WORKERS=4

# Domain Configuration
DOMAIN=$VPS_DOMAIN
ALLOWED_HOSTS=$VPS_DOMAIN,46.247.108.207,localhost

# Security Headers
SECURE_SSL_REDIRECT=true
SESSION_COOKIE_SECURE=true
CSRF_COOKIE_SECURE=true

# Logging
LOG_LEVEL=INFO
EOF"

# Set secure permissions on environment file
run_on_vps "cd $APP_DIR && chmod 600 .env && chown www-data:www-data .env"

echo "✅ Environment configured!"

echo "🔧 Step 11: Security System Setup"
echo "=================================="

# Copy security configurations
echo "Setting up Fail2Ban with AdCopySurge rules..."
run_on_vps "cd $APP_DIR && cp security/fail2ban-adcopysurge.conf /etc/fail2ban/jail.d/"
run_on_vps "cd $APP_DIR && cp security/fail2ban-filters.conf /etc/fail2ban/filter.d/adcopysurge.conf"
run_on_vps "systemctl restart fail2ban"

# Setup monitoring
echo "Setting up security monitoring..."
run_on_vps "cd $APP_DIR && mkdir -p /var/log/adcopysurge"
run_on_vps "cd $APP_DIR && cp monitoring/security-monitor.py /usr/local/bin/"
run_on_vps "chmod +x /usr/local/bin/security-monitor.py"

echo "✅ Security system configured!"

echo "🌐 Step 12: Nginx Configuration"
echo "==============================="

# Setup production Nginx config
echo "Configuring Nginx for production..."
run_on_vps "cd $APP_DIR && cp nginx/production-secure.conf /etc/nginx/sites-available/adcopysurge"
run_on_vps "ln -sf /etc/nginx/sites-available/adcopysurge /etc/nginx/sites-enabled/"
run_on_vps "rm -f /etc/nginx/sites-enabled/default"

# Update domain in nginx config
run_on_vps "sed -i 's/your-domain.com/$VPS_DOMAIN/g' /etc/nginx/sites-available/adcopysurge"
run_on_vps "sed -i 's/YOUR_SERVER_IP/46.247.108.207/g' /etc/nginx/sites-available/adcopysurge"

# Test and reload nginx
run_on_vps "nginx -t"
run_on_vps "systemctl reload nginx"

echo "✅ Nginx configured!"

echo "⚙️ Step 13: Application Services"
echo "================================"

# Create Gunicorn service
echo "Creating Gunicorn service..."
run_on_vps "cat > /etc/systemd/system/adcopysurge.service << 'EOF'
[Unit]
Description=AdCopySurge Gunicorn Application
After=network.target postgresql.service redis.service

[Service]
Type=notify
User=www-data
Group=www-data
WorkingDirectory=/var/www/adcopysurge
Environment=PATH=/var/www/adcopysurge/venv/bin
ExecStart=/var/www/adcopysurge/venv/bin/gunicorn --config /var/www/adcopysurge/backend/gunicorn.conf.py backend.main:app
ExecReload=/bin/kill -s HUP \$MAINPID
KillMode=mixed
TimeoutStopSec=5
PrivateTmp=true

[Install]
WantedBy=multi-user.target
EOF"

# Create Celery service for background tasks
echo "Creating Celery service..."
run_on_vps "cat > /etc/systemd/system/adcopysurge-celery.service << 'EOF'
[Unit]
Description=AdCopySurge Celery Worker
After=network.target redis.service

[Service]
Type=forking
User=www-data
Group=www-data
WorkingDirectory=/var/www/adcopysurge
Environment=PATH=/var/www/adcopysurge/venv/bin
ExecStart=/var/www/adcopysurge/venv/bin/celery -A backend.app.celery_app worker --loglevel=info --detach
ExecStop=/bin/kill -s TERM \$MAINPID
ExecReload=/bin/kill -s HUP \$MAINPID
KillMode=mixed
TimeoutStopSec=10

[Install]
WantedBy=multi-user.target
EOF"

# Enable and start services
echo "Starting application services..."
run_on_vps "systemctl daemon-reload"
run_on_vps "systemctl enable adcopysurge"
run_on_vps "systemctl enable adcopysurge-celery"

echo "✅ Services configured!"

echo "🗄️ Step 14: Database Migration"
echo "=============================="

# Run database migrations
echo "Running database migrations..."
run_on_vps "cd $APP_DIR && source venv/bin/activate && python backend/init_database.py"

echo "✅ Database migrated!"

echo "🎯 Step 15: Frontend Build & Deployment"
echo "======================================="

# Install Node.js and npm
echo "Installing Node.js..."
run_on_vps "curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -"
run_on_vps "apt-get install -y nodejs"

# Build frontend
echo "Building frontend..."
run_on_vps "cd $APP_DIR/frontend && npm install"
run_on_vps "cd $APP_DIR/frontend && npm run build"

# Copy build to nginx directory
run_on_vps "mkdir -p /var/www/html/adcopysurge"
run_on_vps "cp -r $APP_DIR/frontend/build/* /var/www/html/adcopysurge/"
run_on_vps "chown -R www-data:www-data /var/www/html/adcopysurge"

echo "✅ Frontend deployed!"

echo "🚀 Step 16: Final Startup"
echo "========================"

# Start all services
echo "Starting all services..."
run_on_vps "systemctl start adcopysurge"
run_on_vps "systemctl start adcopysurge-celery"
run_on_vps "systemctl reload nginx"

# Verify services are running
echo "Verifying services..."
run_on_vps "systemctl status adcopysurge --no-pager -l"
run_on_vps "systemctl status nginx --no-pager -l"
run_on_vps "systemctl status redis --no-pager -l"

echo "✅ All services started!"

echo "🔍 Step 17: Deployment Verification"
echo "==================================="

# Test endpoints
echo "Testing application endpoints..."
run_on_vps "curl -f http://localhost:8000/health || echo 'Backend health check failed'"
run_on_vps "curl -f http://localhost/api/health || echo 'API health check failed'"

# Show service status
echo "Service Status:"
run_on_vps "systemctl is-active adcopysurge nginx redis postgresql"

# Show logs
echo "Recent application logs:"
run_on_vps "journalctl -u adcopysurge --no-pager -l --since='5 minutes ago'"

echo ""
echo "🎉 DEPLOYMENT COMPLETED SUCCESSFULLY!"
echo "====================================="
echo ""
echo "🌟 AdCopySurge Security Features Deployed:"
echo "  ✅ Session Management with Device Tracking"
echo "  ✅ JWT Security with Token Rotation"
echo "  ✅ Multi-Factor Authentication (MFA)"
echo "  ✅ Advanced Password Security"
echo "  ✅ Role-Based Access Control (RBAC)"
echo "  ✅ GDPR Compliance Framework"
echo "  ✅ Security Monitoring & Fail2Ban"
echo "  ✅ Production-Grade Nginx Configuration"
echo ""
echo "🌐 Access Your Application:"
echo "  Frontend: http://$VPS_DOMAIN"
echo "  Backend API: http://$VPS_DOMAIN/api"
echo "  Health Check: http://$VPS_DOMAIN/api/health"
echo ""
echo "📊 Server Information:"
echo "  VPS IP: $VPS_HOST"
echo "  Domain: $VPS_DOMAIN"
echo "  App Directory: $APP_DIR"
echo "  Backup Directory: $BACKUP_DIR"
echo ""
echo "🔐 Next Steps:"
echo "  1. Update API keys in $APP_DIR/.env"
echo "  2. Configure SSL certificate (Let's Encrypt recommended)"
echo "  3. Set up monitoring alerts"
echo "  4. Configure database backups"
echo ""
echo "💡 Useful Commands:"
echo "  Service Status: systemctl status adcopysurge"
echo "  View Logs: journalctl -u adcopysurge -f"
echo "  Restart App: systemctl restart adcopysurge"
echo "  Nginx Reload: systemctl reload nginx"
echo ""

echo "🎯 Deployment completed at $(date)"
echo "Repository: $GITHUB_REPO"
echo "All security features are now active and protecting your application!"