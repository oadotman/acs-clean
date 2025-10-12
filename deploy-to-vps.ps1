# AdCopySurge Secure Deployment Script for Windows
# This PowerShell script will deploy the secure version to your Datalix VPS

Write-Host "🚀 AdCopySurge Secure Deployment to Datalix VPS" -ForegroundColor Green
Write-Host "=================================================" -ForegroundColor Green

# Configuration
$VPS_HOST = "46.247.108.207"
$VPS_USER = "root"
$SCRIPT_NAME = "deploy-to-datalix-secure.sh"

Write-Host "📝 VPS Configuration:" -ForegroundColor Yellow
Write-Host "   Host: $VPS_HOST" -ForegroundColor White
Write-Host "   User: $VPS_USER" -ForegroundColor White
Write-Host "   Script: $SCRIPT_NAME" -ForegroundColor White
Write-Host ""

# Check if deployment script exists
if (-not (Test-Path $SCRIPT_NAME)) {
    Write-Host "❌ Deployment script not found: $SCRIPT_NAME" -ForegroundColor Red
    Write-Host "Please make sure you're in the correct directory." -ForegroundColor Red
    exit 1
}

# Check if SSH is available
try {
    ssh -V 2>$null
    if ($LASTEXITCODE -ne 0) {
        throw "SSH not found"
    }
} catch {
    Write-Host "❌ SSH is not available. Please install OpenSSH or use WSL." -ForegroundColor Red
    Write-Host "You can install OpenSSH from: https://docs.microsoft.com/en-us/windows-server/administration/openssh/openssh_install_firstuse" -ForegroundColor Yellow
    exit 1
}

Write-Host "🔍 Testing SSH connection to VPS..." -ForegroundColor Yellow
$sshTest = ssh -o ConnectTimeout=10 -o StrictHostKeyChecking=no $VPS_USER@$VPS_HOST "echo 'Connection successful'"
if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ SSH connection successful!" -ForegroundColor Green
} else {
    Write-Host "❌ SSH connection failed. Please check:" -ForegroundColor Red
    Write-Host "   1. VPS is running and accessible" -ForegroundColor Yellow
    Write-Host "   2. SSH keys are properly configured" -ForegroundColor Yellow
    Write-Host "   3. Network connectivity" -ForegroundColor Yellow
    
    $continue = Read-Host "Do you want to continue anyway? (y/N)"
    if ($continue -ne "y" -and $continue -ne "Y") {
        Write-Host "Deployment cancelled." -ForegroundColor Yellow
        exit 1
    }
}

Write-Host "📤 Copying deployment script to VPS..." -ForegroundColor Yellow
try {
    scp -o StrictHostKeyChecking=no $SCRIPT_NAME ${VPS_USER}@${VPS_HOST}:/tmp/
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Script copied successfully!" -ForegroundColor Green
    } else {
        throw "SCP failed"
    }
} catch {
    Write-Host "❌ Failed to copy deployment script to VPS" -ForegroundColor Red
    exit 1
}

Write-Host "🔧 Making script executable..." -ForegroundColor Yellow
ssh -o StrictHostKeyChecking=no $VPS_USER@$VPS_HOST "chmod +x /tmp/$SCRIPT_NAME"

Write-Host ""
Write-Host "⚠️  IMPORTANT NOTICE" -ForegroundColor Red
Write-Host "===================" -ForegroundColor Red
Write-Host "This deployment will:" -ForegroundColor Yellow
Write-Host "  🗑️  COMPLETELY DELETE all existing files on the VPS" -ForegroundColor Red
Write-Host "  📦 Install fresh system dependencies" -ForegroundColor Yellow
Write-Host "  🔐 Deploy all security features" -ForegroundColor Green
Write-Host "  🚀 Set up production environment" -ForegroundColor Green
Write-Host ""

$confirm = Read-Host "Are you sure you want to proceed? Type 'YES' to continue"
if ($confirm -ne "YES") {
    Write-Host "Deployment cancelled for safety." -ForegroundColor Yellow
    exit 0
}

Write-Host ""
Write-Host "🚀 Starting deployment on VPS..." -ForegroundColor Green
Write-Host "This may take 10-15 minutes..." -ForegroundColor Yellow
Write-Host ""

# Execute the deployment script on VPS
try {
    ssh -o StrictHostKeyChecking=no $VPS_USER@$VPS_HOST "cd /tmp && ./$SCRIPT_NAME"
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host ""
        Write-Host "🎉 DEPLOYMENT COMPLETED SUCCESSFULLY!" -ForegroundColor Green
        Write-Host "====================================" -ForegroundColor Green
        Write-Host ""
        Write-Host "🌐 Your application is now available at:" -ForegroundColor Yellow
        Write-Host "   Frontend: http://v44954.datalix.de" -ForegroundColor Cyan
        Write-Host "   API: http://v44954.datalix.de/api" -ForegroundColor Cyan
        Write-Host "   Health: http://v44954.datalix.de/api/health" -ForegroundColor Cyan
        Write-Host ""
        Write-Host "🔐 Security Features Active:" -ForegroundColor Green
        Write-Host "   ✅ Session Management with Device Tracking" -ForegroundColor White
        Write-Host "   ✅ JWT Security with Token Rotation" -ForegroundColor White
        Write-Host "   ✅ Multi-Factor Authentication (MFA)" -ForegroundColor White
        Write-Host "   ✅ Advanced Password Security" -ForegroundColor White
        Write-Host "   ✅ Role-Based Access Control (RBAC)" -ForegroundColor White
        Write-Host "   ✅ GDPR Compliance Framework" -ForegroundColor White
        Write-Host "   ✅ Security Monitoring & Fail2Ban" -ForegroundColor White
        Write-Host ""
        Write-Host "📋 Next Steps:" -ForegroundColor Yellow
        Write-Host "   1. Update API keys in /var/www/adcopysurge/.env" -ForegroundColor White
        Write-Host "   2. Configure SSL certificate (recommended)" -ForegroundColor White
        Write-Host "   3. Test all functionality" -ForegroundColor White
        Write-Host ""
    } else {
        throw "Deployment script failed"
    }
} catch {
    Write-Host ""
    Write-Host "❌ DEPLOYMENT FAILED!" -ForegroundColor Red
    Write-Host "===================" -ForegroundColor Red
    Write-Host "Check the output above for error details." -ForegroundColor Yellow
    Write-Host "You can SSH to the VPS to troubleshoot:" -ForegroundColor Yellow
    Write-Host "   ssh root@46.247.108.207" -ForegroundColor Cyan
    exit 1
}

# Cleanup
Write-Host "🧹 Cleaning up temporary files..." -ForegroundColor Yellow
ssh -o StrictHostKeyChecking=no $VPS_USER@$VPS_HOST "rm -f /tmp/$SCRIPT_NAME"

Write-Host ""
Write-Host "✨ Deployment process complete!" -ForegroundColor Green
Write-Host "Your secure AdCopySurge application is now live!" -ForegroundColor Green