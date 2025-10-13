# AdCopySurge VPS Deployment Script
# This script deploys to your VPS server cleanly

param(
    [string]$ServerIP = "46.247.108.207",
    [string]$Username = "root",
    [switch]$CleanDeploy = $false
)

Write-Host "🚀 AdCopySurge VPS Deployment" -ForegroundColor Green
Write-Host "=============================" -ForegroundColor Green
Write-Host "Server: $ServerIP" -ForegroundColor Cyan
Write-Host "Clean Deploy: $CleanDeploy" -ForegroundColor Cyan

# Build locally first
Write-Host "🔨 Building production version locally..." -ForegroundColor Yellow
Set-Location "frontend"

if (-not (Test-Path "build") -or $CleanDeploy) {
    $env:NODE_ENV = "production"
    npm run build
    
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ Build failed!" -ForegroundColor Red
        exit 1
    }
}

Write-Host "✅ Local build complete!" -ForegroundColor Green

# Create deployment archive
Write-Host "📦 Creating deployment archive..." -ForegroundColor Yellow
if (Test-Path "../adcopysurge-deploy.tar.gz") {
    Remove-Item "../adcopysurge-deploy.tar.gz"
}

# Create tar archive (requires WSL or tar command)
wsl tar -czf ../adcopysurge-deploy.tar.gz build/ ../backend/

Write-Host "📤 Deployment package ready!" -ForegroundColor Green
Write-Host ""
Write-Host "📋 NEXT STEPS:" -ForegroundColor Yellow
Write-Host "1. Upload adcopysurge-deploy.tar.gz to your VPS" -ForegroundColor White
Write-Host "2. Run the deployment commands on your VPS:" -ForegroundColor White
Write-Host ""
Write-Host "   scp adcopysurge-deploy.tar.gz root@${ServerIP}:/var/www/" -ForegroundColor Cyan
Write-Host "   ssh root@${ServerIP}" -ForegroundColor Cyan
Write-Host ""
Write-Host "   # On the VPS:" -ForegroundColor Green
Write-Host "   cd /var/www" -ForegroundColor Cyan
Write-Host "   tar -xzf adcopysurge-deploy.tar.gz" -ForegroundColor Cyan
Write-Host "   rm -rf adcopysurge/frontend/build" -ForegroundColor Cyan
Write-Host "   rm -rf html/*" -ForegroundColor Cyan
Write-Host "   cp -r build/* html/" -ForegroundColor Cyan
Write-Host "   chown -R www-data:www-data html/" -ForegroundColor Cyan
Write-Host "   systemctl restart adcopysurge" -ForegroundColor Cyan
Write-Host ""
Write-Host "✅ Your app will be live at: http://${ServerIP}/" -ForegroundColor Green

Set-Location ".."