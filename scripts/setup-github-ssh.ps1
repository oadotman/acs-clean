# AdCopySurge GitHub Actions SSH Key Setup Script (PowerShell)
# 
# This script generates SSH keys and sets them up for GitHub Actions deployment
# Run this on your Windows machine

Write-Host "🔐 AdCopySurge GitHub Actions SSH Key Setup" -ForegroundColor Green
Write-Host "===========================================" -ForegroundColor Green
Write-Host ""

# Configuration
$KEY_NAME = "adcopysurge_deploy"
$VPS_HOST = "46.247.108.207"
$VPS_USER = "deploy"
$DOMAIN = "api.adcopysurge.com"

Write-Host "📋 Configuration:" -ForegroundColor Cyan
Write-Host "   Key name: $KEY_NAME" -ForegroundColor White
Write-Host "   VPS Host: $VPS_HOST" -ForegroundColor White
Write-Host "   VPS User: $VPS_USER" -ForegroundColor White
Write-Host "   Domain: $DOMAIN" -ForegroundColor White
Write-Host ""

# Check if SSH directory exists
$sshDir = "$env:USERPROFILE\.ssh"
if (-not (Test-Path $sshDir)) {
    Write-Host "📁 Creating .ssh directory..." -ForegroundColor Yellow
    New-Item -ItemType Directory -Path $sshDir -Force | Out-Null
}

# Check if ssh-keygen is available
try {
    $null = Get-Command ssh-keygen -ErrorAction Stop
    $sshKeygenAvailable = $true
} catch {
    $sshKeygenAvailable = $false
}

if (-not $sshKeygenAvailable) {
    Write-Host "❌ ssh-keygen not found!" -ForegroundColor Red
    Write-Host "Please install OpenSSH or Git for Windows to get ssh-keygen." -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Options to install ssh-keygen:" -ForegroundColor Cyan
    Write-Host "1. Install Git for Windows: https://git-scm.windows.com/" -ForegroundColor White
    Write-Host "2. Install OpenSSH: Settings → Apps → Optional Features → Add OpenSSH Client" -ForegroundColor White
    Write-Host "3. Use Windows Subsystem for Linux (WSL)" -ForegroundColor White
    Write-Host ""
    Write-Host "After installation, restart PowerShell and run this script again." -ForegroundColor Yellow
    exit 1
}

# Generate SSH key if it doesn't exist
$privateKeyPath = "$sshDir\$KEY_NAME"
$publicKeyPath = "$sshDir\$KEY_NAME.pub"

if (-not (Test-Path $privateKeyPath)) {
    Write-Host "🔑 Generating SSH key pair..." -ForegroundColor Yellow
    ssh-keygen -t ed25519 -C "gh-actions@adcopysurge" -f $privateKeyPath -N '""'
    Write-Host "✅ SSH key pair generated!" -ForegroundColor Green
} else {
    Write-Host "⚠️  SSH key already exists: $privateKeyPath" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "🔑 SSH Key Files Created:" -ForegroundColor Cyan
Write-Host "   Private key: $privateKeyPath" -ForegroundColor White
Write-Host "   Public key:  $publicKeyPath" -ForegroundColor White
Write-Host ""

# Display public key
Write-Host "📋 Public Key (copy this to your VPS):" -ForegroundColor Green
Write-Host "======================================" -ForegroundColor Green
if (Test-Path $publicKeyPath) {
    Get-Content $publicKeyPath
    Write-Host ""
} else {
    Write-Host "❌ Public key file not found!" -ForegroundColor Red
}

# Display private key for GitHub secrets
Write-Host "🔒 Private Key (copy this to GitHub Secrets as DATALIX_SSH_KEY):" -ForegroundColor Green
Write-Host "================================================================" -ForegroundColor Green
if (Test-Path $privateKeyPath) {
    Get-Content $privateKeyPath
    Write-Host ""
} else {
    Write-Host "❌ Private key file not found!" -ForegroundColor Red
}

# Installation instructions
Write-Host "📝 Next Steps:" -ForegroundColor Cyan
Write-Host "1. Copy the PUBLIC key to your VPS:" -ForegroundColor White
Write-Host "   ssh-copy-id -i `"$publicKeyPath`" $VPS_USER@$VPS_HOST" -ForegroundColor Gray
Write-Host "   OR manually append it to ~/.ssh/authorized_keys on the VPS" -ForegroundColor Gray
Write-Host ""
Write-Host "2. Test SSH connection:" -ForegroundColor White
Write-Host "   ssh -i `"$privateKeyPath`" $VPS_USER@$VPS_HOST" -ForegroundColor Gray
Write-Host ""
Write-Host "3. Add these GitHub Repository Secrets:" -ForegroundColor White
Write-Host "   Go to: https://github.com/Adeliyio/acsurge/settings/secrets/actions" -ForegroundColor Gray
Write-Host ""
Write-Host "   DATALIX_SSH_KEY = [Private key content above]" -ForegroundColor Gray
Write-Host "   DATALIX_HOST = $VPS_HOST" -ForegroundColor Gray
Write-Host "   DATALIX_USER = $VPS_USER" -ForegroundColor Gray
Write-Host "   DATALIX_DOMAIN = $DOMAIN" -ForegroundColor Gray
Write-Host ""

# Create a setup commands file
$setupFile = "$env:USERPROFILE\adcopysurge-ssh-setup-commands.txt"
Write-Host "🚀 Creating setup commands file..." -ForegroundColor Yellow

$setupCommands = @"
# AdCopySurge SSH Setup Commands
# Generated: $(Get-Date)

# 1. Copy public key to VPS:
ssh-copy-id -i "$publicKeyPath" $VPS_USER@$VPS_HOST

# Alternative: Manual copy (if ssh-copy-id doesn't work)
# Copy the public key content and run on VPS:
# echo "PUBLIC_KEY_CONTENT_HERE" >> ~/.ssh/authorized_keys

# 2. Test connection:
ssh -i "$privateKeyPath" $VPS_USER@$VPS_HOST

# 3. GitHub Secrets to add:
DATALIX_SSH_KEY = [Copy private key from $privateKeyPath]
DATALIX_HOST = $VPS_HOST
DATALIX_USER = $VPS_USER
DATALIX_DOMAIN = $DOMAIN

# 4. Manual VPS setup (if needed):
ssh $VPS_USER@$VPS_HOST

# On VPS, ensure deploy user has sudo access:
sudo usermod -aG sudo $VPS_USER

# Create required directories:
sudo mkdir -p /home/deploy /var/backups/adcopysurge /run/adcopysurge /var/log/adcopysurge
sudo chown $VPS_USER`:$VPS_USER /home/deploy
sudo chown www-data:www-data /run/adcopysurge /var/log/adcopysurge

# Install required packages (if not installed):
sudo apt update
sudo apt install -y python3.11 python3.11-venv python3.11-dev \
    build-essential git redis-server nginx certbot python3-certbot-nginx \
    postgresql-client htop curl unzip
"@

$setupCommands | Out-File -FilePath $setupFile -Encoding UTF8

Write-Host "✅ Setup commands saved to: $setupFile" -ForegroundColor Green
Write-Host ""

# Test SSH availability
Write-Host "🧪 Testing SSH availability..." -ForegroundColor Yellow
try {
    $null = Get-Command ssh -ErrorAction Stop
    Write-Host "✅ SSH client is available" -ForegroundColor Green
    
    # Ask if user wants to test connection
    $testConnection = Read-Host "Do you want to test the SSH connection now? (y/N)"
    if ($testConnection -match '^[Yy]') {
        Write-Host "🔗 Testing SSH connection..." -ForegroundColor Yellow
        Write-Host "If this is the first connection, you may need to type 'yes' to accept the host key." -ForegroundColor Cyan
        ssh -i $privateKeyPath -o ConnectTimeout=10 $VPS_USER@$VPS_HOST "echo 'SSH connection successful!'"
    }
} catch {
    Write-Host "❌ SSH client not found. You may need to install OpenSSH or use Git Bash." -ForegroundColor Red
}

Write-Host ""
Write-Host "🎉 SSH Key setup completed!" -ForegroundColor Green
Write-Host ""
Write-Host "📚 Next: Configure your GitHub repository secrets and trigger a deployment." -ForegroundColor Cyan
Write-Host "📖 Full guide: docs/DATALIX_GITHUB_ACTIONS_DEPLOYMENT.md" -ForegroundColor Cyan