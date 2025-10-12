#!/bin/bash

# AdCopySurge Frontend VPS Deployment Script
# This script builds and deploys the React frontend to the VPS

set -e  # Exit on any error

echo "🚀 Starting AdCopySurge Frontend VPS Deployment..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
VPS_HOST="46.247.108.207"
VPS_USER="root"
FRONTEND_DIR="/srv/adcopysurge/frontend"
NGINX_SITES="/etc/nginx/sites-available"
NGINX_ENABLED="/etc/nginx/sites-enabled"

echo -e "${BLUE}📋 Configuration:${NC}"
echo -e "  VPS Host: ${VPS_HOST}"
echo -e "  Frontend Dir: ${FRONTEND_DIR}"
echo -e "  User: ${VPS_USER}"
echo ""

# Step 1: Build the frontend locally
echo -e "${YELLOW}🔨 Step 1: Building frontend locally...${NC}"
cd frontend

# Copy VPS environment file to production
echo -e "📝 Setting up VPS environment variables..."
cp .env.vps .env.production

# Install dependencies and build
echo -e "📦 Installing dependencies..."
npm install

echo -e "🏗️ Building production bundle..."
npm run build

if [ ! -d "build" ]; then
    echo -e "${RED}❌ Build failed - no build directory found${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Frontend build completed successfully${NC}"

# Step 2: Upload to VPS
echo -e "${YELLOW}🚀 Step 2: Uploading to VPS...${NC}"

# Create frontend directory on VPS
echo -e "📁 Creating directories on VPS..."
ssh ${VPS_USER}@${VPS_HOST} "mkdir -p ${FRONTEND_DIR}"

# Upload build files
echo -e "📤 Uploading build files..."
rsync -avz --delete build/ ${VPS_USER}@${VPS_HOST}:${FRONTEND_DIR}/

echo -e "${GREEN}✅ Files uploaded successfully${NC}"

# Step 3: Configure Nginx
echo -e "${YELLOW}🔧 Step 3: Configuring Nginx...${NC}"

# Create Nginx configuration
cat > /tmp/adcopysurge-frontend.conf << 'EOF'
# AdCopySurge Frontend Nginx Configuration
server {
    listen 80;
    listen [::]:80;
    server_name adcopysurge.com www.adcopysurge.com;
    
    # Redirect HTTP to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    listen [::]:443 ssl http2;
    server_name adcopysurge.com www.adcopysurge.com;
    
    # SSL Configuration (assuming Let's Encrypt)
    ssl_certificate /etc/letsencrypt/live/adcopysurge.com/fullchain.pem;
    ssl_private_key /etc/letsencrypt/live/adcopysurge.com/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    
    # Frontend static files
    root /srv/adcopysurge/frontend;
    index index.html;
    
    # Gzip compression
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_types
        text/plain
        text/css
        text/xml
        text/javascript
        application/javascript
        application/xml+rss
        application/json;
    
    # Cache static assets
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
        try_files $uri =404;
    }
    
    # API proxy to backend
    location /api/ {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # CORS headers
        add_header Access-Control-Allow-Origin * always;
        add_header Access-Control-Allow-Methods "GET, POST, PUT, DELETE, OPTIONS" always;
        add_header Access-Control-Allow-Headers "DNT,User-Agent,X-Requested-With,If-Modified-Since,Cache-Control,Content-Type,Range,Authorization" always;
        
        # Handle preflight requests
        if ($request_method = 'OPTIONS') {
            add_header Access-Control-Allow-Origin * always;
            add_header Access-Control-Allow-Methods "GET, POST, PUT, DELETE, OPTIONS" always;
            add_header Access-Control-Allow-Headers "DNT,User-Agent,X-Requested-With,If-Modified-Since,Cache-Control,Content-Type,Range,Authorization" always;
            add_header Access-Control-Max-Age 1728000;
            add_header Content-Type 'text/plain charset=UTF-8';
            add_header Content-Length 0;
            return 204;
        }
    }
    
    # React Router - serve index.html for all non-API routes
    location / {
        try_files $uri $uri/ /index.html;
        add_header Cache-Control "no-cache, no-store, must-revalidate";
        add_header Pragma "no-cache";
        add_header Expires "0";
    }
    
    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;
    
    # Optional: Content Security Policy
    add_header Content-Security-Policy "default-src 'self'; script-src 'self' 'unsafe-inline' 'unsafe-eval'; style-src 'self' 'unsafe-inline'; font-src 'self' data:; img-src 'self' data: https:; connect-src 'self' https://tqzlsajhhtkhljdbjkyg.supabase.co https://api.adcopysurge.com;" always;
}
EOF

# Upload and configure Nginx
echo -e "📤 Uploading Nginx configuration..."
scp /tmp/adcopysurge-frontend.conf ${VPS_USER}@${VPS_HOST}:${NGINX_SITES}/
rm /tmp/adcopysurge-frontend.conf

# Enable site and restart Nginx
echo -e "🔄 Configuring Nginx..."
ssh ${VPS_USER}@${VPS_HOST} << 'ENDSSH'
    # Enable the site
    ln -sf /etc/nginx/sites-available/adcopysurge-frontend.conf /etc/nginx/sites-enabled/
    
    # Test Nginx configuration
    echo "🧪 Testing Nginx configuration..."
    nginx -t
    
    if [ $? -eq 0 ]; then
        echo "✅ Nginx configuration is valid"
        
        # Reload Nginx
        systemctl reload nginx
        echo "🔄 Nginx reloaded successfully"
    else
        echo "❌ Nginx configuration has errors"
        exit 1
    fi
ENDSSH

echo -e "${GREEN}✅ Nginx configured successfully${NC}"

# Step 4: Setup SSL (if not already configured)
echo -e "${YELLOW}🔒 Step 4: Checking SSL configuration...${NC}"
ssh ${VPS_USER}@${VPS_HOST} << 'ENDSSH'
    if [ ! -f "/etc/letsencrypt/live/adcopysurge.com/fullchain.pem" ]; then
        echo "🔒 Setting up SSL certificate..."
        
        # Install certbot if not installed
        if ! command -v certbot &> /dev/null; then
            apt update
            apt install -y certbot python3-certbot-nginx
        fi
        
        # Get SSL certificate
        certbot --nginx -d adcopysurge.com -d www.adcopysurge.com --non-interactive --agree-tos --email admin@adcopysurge.com
        
        if [ $? -eq 0 ]; then
            echo "✅ SSL certificate configured successfully"
        else
            echo "⚠️ SSL certificate setup failed, but deployment continues"
        fi
    else
        echo "✅ SSL certificate already exists"
    fi
ENDSSH

# Step 5: Final verification
echo -e "${YELLOW}🧪 Step 5: Verifying deployment...${NC}"
echo -e "🔍 Checking if files are accessible..."

# Test if the main page loads
if curl -s -I https://adcopysurge.com | grep -q "200 OK"; then
    echo -e "${GREEN}✅ Frontend is accessible at https://adcopysurge.com${NC}"
else
    echo -e "${YELLOW}⚠️ Frontend may not be fully accessible yet (DNS/SSL propagation)${NC}"
fi

# Show deployment summary
echo -e "\n${GREEN}🎉 Frontend Deployment Complete!${NC}"
echo -e "\n${BLUE}📋 Deployment Summary:${NC}"
echo -e "  📁 Frontend deployed to: ${FRONTEND_DIR}"
echo -e "  🌐 Website: https://adcopysurge.com"
echo -e "  🔗 API: https://api.adcopysurge.com"
echo -e "  📝 Nginx config: ${NGINX_SITES}/adcopysurge-frontend.conf"
echo -e "\n${BLUE}🔧 Next Steps:${NC}"
echo -e "  1. Test the website: https://adcopysurge.com"
echo -e "  2. Test file upload functionality"
echo -e "  3. Verify API calls work properly"
echo -e "  4. Update DNS if needed"
echo -e "\n${GREEN}✨ Your frontend is now self-hosted on your VPS!${NC}"

cd ..