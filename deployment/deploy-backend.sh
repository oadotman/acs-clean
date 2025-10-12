#!/bin/bash

# AdCopySurge Backend Deployment Script for Ubuntu/Digital Ocean
# Run as root or with sudo privileges

set -e  # Exit on any error

echo "🚀 Starting AdCopySurge Backend Deployment..."

# Configuration
APP_NAME="adcopysurge"
APP_USER="www-data"
APP_DIR="/var/www/${APP_NAME}"
BACKEND_DIR="${APP_DIR}/backend"
LOG_DIR="/var/log/${APP_NAME}"
DOMAIN="api.adcopysurge.com"  # Replace with your domain

# Update system
echo "📦 Updating system packages..."
apt-get update -y
apt-get upgrade -y

# Install required packages
echo "📦 Installing system dependencies..."
apt-get install -y \
    python3 \
    python3-pip \
    python3-venv \
    nginx \
    git \
    curl \
    wget \
    software-properties-common \
    build-essential \
    pkg-config

# Create application directories
echo "📁 Creating application directories..."
mkdir -p ${APP_DIR}
mkdir -p ${BACKEND_DIR}
mkdir -p ${LOG_DIR}

# Create log directory with proper permissions
chown -R ${APP_USER}:${APP_USER} ${LOG_DIR}
chmod 755 ${LOG_DIR}

# Navigate to backend directory
cd ${BACKEND_DIR}

# Create Python virtual environment
echo "🐍 Setting up Python virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install Python dependencies
echo "📦 Installing Python dependencies..."
pip install -r requirements-production.txt

# Download NLTK data (required for text analysis)
echo "📚 Downloading NLTK data..."
python -c "import nltk; nltk.download('punkt')"
python -c "import nltk; nltk.download('stopwords')"

# Set proper ownership
echo "🔐 Setting proper file permissions..."
chown -R ${APP_USER}:${APP_USER} ${APP_DIR}

# Install systemd service
echo "⚙️  Installing systemd service..."
cp /tmp/adcopysurge.service /etc/systemd/system/
systemctl daemon-reload
systemctl enable adcopysurge

# Configure Nginx
echo "🌐 Configuring Nginx..."
cp /tmp/adcopysurge-nginx /etc/nginx/sites-available/adcopysurge
ln -sf /etc/nginx/sites-available/adcopysurge /etc/nginx/sites-enabled/

# Remove default Nginx site
rm -f /etc/nginx/sites-enabled/default

# Test Nginx configuration
nginx -t

# Configure firewall
echo "🔥 Configuring firewall..."
ufw --force enable
ufw allow ssh
ufw allow 'Nginx Full'
ufw allow 80
ufw allow 443

# Start services
echo "🚀 Starting services..."
systemctl restart nginx
systemctl start adcopysurge
systemctl status adcopysurge --no-pager

# Setup log rotation
echo "📝 Setting up log rotation..."
cat > /etc/logrotate.d/adcopysurge << EOF
${LOG_DIR}/*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    create 644 ${APP_USER} ${APP_USER}
    postrotate
        systemctl reload adcopysurge
    endscript
}
EOF

# Setup SSL with Let's Encrypt (optional)
echo "🔒 Setting up SSL certificate..."
read -p "Do you want to setup SSL with Let's Encrypt? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    # Install Certbot
    apt-get install -y certbot python3-certbot-nginx
    
    # Get SSL certificate
    certbot --nginx -d ${DOMAIN} --non-interactive --agree-tos --email admin@${DOMAIN}
    
    # Setup automatic renewal
    (crontab -l 2>/dev/null; echo "0 12 * * * /usr/bin/certbot renew --quiet") | crontab -
fi

# Final status check
echo "✅ Deployment completed!"
echo ""
echo "🔍 Service Status:"
systemctl status adcopysurge --no-pager
echo ""
echo "🌐 Nginx Status:"
systemctl status nginx --no-pager
echo ""
echo "🔗 API Endpoints:"
echo "  Health Check: http://${DOMAIN}/health"
echo "  API Docs: http://${DOMAIN}/api/docs (if DEBUG=true)"
echo "  API Status: http://${DOMAIN}/api/ads/tools/status"
echo ""
echo "📁 Application Directory: ${APP_DIR}"
echo "📝 Logs Directory: ${LOG_DIR}"
echo ""
echo "🚀 AdCopySurge Backend is now deployed and running!"

# Show recent logs
echo "📋 Recent application logs:"
journalctl -u adcopysurge -n 20 --no-pager
