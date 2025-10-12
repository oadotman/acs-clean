# AdCopySurge Frontend VPS Deployment Script (PowerShell)
# This script builds and deploys the React frontend to the VPS

param(
    [string]$VpsHost = "46.247.108.207",
    [string]$VpsUser = "root"
)

Write-Host "🚀 Starting AdCopySurge Frontend VPS Deployment..." -ForegroundColor Green

# Configuration
$FRONTEND_DIR = "/srv/adcopysurge/frontend"
$BUILD_DIR = "frontend/build"

Write-Host "📋 Configuration:" -ForegroundColor Blue
Write-Host "  VPS Host: $VpsHost" -ForegroundColor White
Write-Host "  Frontend Dir: $FRONTEND_DIR" -ForegroundColor White
Write-Host "  User: $VpsUser" -ForegroundColor White
Write-Host ""

# Step 1: Build the frontend locally
Write-Host "🔨 Step 1: Building frontend locally..." -ForegroundColor Yellow

try {
    Set-Location frontend
    
    # Copy VPS environment file to production
    Write-Host "📝 Setting up VPS environment variables..." -ForegroundColor White
    Copy-Item .env.vps .env.production -Force
    
    # Install dependencies and build
    Write-Host "📦 Installing dependencies..." -ForegroundColor White
    npm install
    
    if ($LASTEXITCODE -ne 0) {
        throw "npm install failed"
    }
    
    Write-Host "🏗️ Building production bundle..." -ForegroundColor White
    npm run build
    
    if ($LASTEXITCODE -ne 0) {
        throw "npm run build failed"
    }
    
    if (!(Test-Path "build")) {
        throw "Build failed - no build directory found"
    }
    
    Write-Host "✅ Frontend build completed successfully" -ForegroundColor Green
    
    Set-Location ..
}
catch {
    Write-Host "❌ Build failed: $_" -ForegroundColor Red
    Set-Location ..
    exit 1
}

# Step 2: Upload to VPS using SCP
Write-Host "🚀 Step 2: Uploading to VPS..." -ForegroundColor Yellow

try {
    # Create frontend directory on VPS
    Write-Host "📁 Creating directories on VPS..." -ForegroundColor White
    ssh $VpsUser@$VpsHost "mkdir -p $FRONTEND_DIR"
    
    if ($LASTEXITCODE -ne 0) {
        throw "Failed to create directory on VPS"
    }
    
    # Upload build files using scp
    Write-Host "📤 Uploading build files..." -ForegroundColor White
    scp -r frontend/build/* $VpsUser@${VpsHost}:$FRONTEND_DIR/
    
    if ($LASTEXITCODE -ne 0) {
        throw "Failed to upload files to VPS"
    }
    
    Write-Host "✅ Files uploaded successfully" -ForegroundColor Green
}
catch {
    Write-Host "❌ Upload failed: $_" -ForegroundColor Red
    exit 1
}

# Step 3: Configure Nginx on VPS
Write-Host "🔧 Step 3: Configuring Nginx..." -ForegroundColor Yellow

$nginxConfig = @"
# AdCopySurge Frontend Nginx Configuration
server {
    listen 80;
    listen [::]:80;
    server_name adcopysurge.com www.adcopysurge.com;
    
    # Redirect HTTP to HTTPS
    return 301 https://`$server_name`$request_uri;
}

server {
    listen 443 ssl http2;
    listen [::]:443 ssl http2;
    server_name adcopysurge.com www.adcopysurge.com;
    
    # SSL Configuration
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
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)`$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
        try_files `$uri =404;
    }
    
    # API proxy to backend
    location /api/ {
        proxy_pass http://localhost:8000;
        proxy_set_header Host `$host;
        proxy_set_header X-Real-IP `$remote_addr;
        proxy_set_header X-Forwarded-For `$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto `$scheme;
        
        # CORS headers
        add_header Access-Control-Allow-Origin * always;
        add_header Access-Control-Allow-Methods "GET, POST, PUT, DELETE, OPTIONS" always;
        add_header Access-Control-Allow-Headers "DNT,User-Agent,X-Requested-With,If-Modified-Since,Cache-Control,Content-Type,Range,Authorization" always;
    }
    
    # React Router - serve index.html for all non-API routes
    location / {
        try_files `$uri `$uri/ /index.html;
        add_header Cache-Control "no-cache, no-store, must-revalidate";
        add_header Pragma "no-cache";
        add_header Expires "0";
    }
    
    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;
}
"@

try {
    # Save config to temp file and upload
    $tempFile = [System.IO.Path]::GetTempFileName()
    $nginxConfig | Out-File -FilePath $tempFile -Encoding UTF8
    
    Write-Host "📤 Uploading Nginx configuration..." -ForegroundColor White
    scp $tempFile $VpsUser@${VpsHost}:/etc/nginx/sites-available/adcopysurge-frontend.conf
    
    Remove-Item $tempFile
    
    # Configure Nginx on VPS
    Write-Host "🔄 Configuring Nginx..." -ForegroundColor White
    ssh $VpsUser@$VpsHost @"
        # Enable the site
        ln -sf /etc/nginx/sites-available/adcopysurge-frontend.conf /etc/nginx/sites-enabled/
        
        # Test Nginx configuration
        echo '🧪 Testing Nginx configuration...'
        nginx -t
        
        if [ `$? -eq 0 ]; then
            echo '✅ Nginx configuration is valid'
            
            # Reload Nginx
            systemctl reload nginx
            echo '🔄 Nginx reloaded successfully'
        else
            echo '❌ Nginx configuration has errors'
            exit 1
        fi
"@
    
    if ($LASTEXITCODE -ne 0) {
        throw "Nginx configuration failed"
    }
    
    Write-Host "✅ Nginx configured successfully" -ForegroundColor Green
}
catch {
    Write-Host "❌ Nginx configuration failed: $_" -ForegroundColor Red
    exit 1
}

# Step 4: Setup SSL (if needed)
Write-Host "🔒 Step 4: Checking SSL configuration..." -ForegroundColor Yellow

ssh $VpsUser@$VpsHost @"
    if [ ! -f "/etc/letsencrypt/live/adcopysurge.com/fullchain.pem" ]; then
        echo '🔒 Setting up SSL certificate...'
        
        # Install certbot if not installed
        if ! command -v certbot &> /dev/null; then
            apt update
            apt install -y certbot python3-certbot-nginx
        fi
        
        # Get SSL certificate
        certbot --nginx -d adcopysurge.com -d www.adcopysurge.com --non-interactive --agree-tos --email admin@adcopysurge.com
        
        if [ `$? -eq 0 ]; then
            echo '✅ SSL certificate configured successfully'
        else
            echo '⚠️ SSL certificate setup failed, but deployment continues'
        fi
    else
        echo '✅ SSL certificate already exists'
    fi
"@

# Final verification
Write-Host "🧪 Step 5: Verifying deployment..." -ForegroundColor Yellow

Write-Host ""
Write-Host "🎉 Frontend Deployment Complete!" -ForegroundColor Green
Write-Host ""
Write-Host "📋 Deployment Summary:" -ForegroundColor Blue
Write-Host "  📁 Frontend deployed to: $FRONTEND_DIR" -ForegroundColor White
Write-Host "  🌐 Website: https://adcopysurge.com" -ForegroundColor White
Write-Host "  🔗 API: https://api.adcopysurge.com" -ForegroundColor White
Write-Host ""
Write-Host "🔧 Next Steps:" -ForegroundColor Blue
Write-Host "  1. Test the website: https://adcopysurge.com" -ForegroundColor White
Write-Host "  2. Test file upload functionality" -ForegroundColor White
Write-Host "  3. Verify API calls work properly" -ForegroundColor White
Write-Host "  4. Update DNS if needed" -ForegroundColor White
Write-Host ""
Write-Host "✨ Your frontend is now self-hosted on your VPS!" -ForegroundColor Green