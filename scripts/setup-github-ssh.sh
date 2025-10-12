#!/bin/bash
# AdCopySurge GitHub Actions SSH Key Setup Script
# 
# This script generates SSH keys and sets them up for GitHub Actions deployment
# Run this on your local machine (not on the server)

set -e

echo "🔐 AdCopySurge GitHub Actions SSH Key Setup"
echo "==========================================="
echo ""

# Configuration
KEY_NAME="adcopysurge_deploy"
VPS_HOST="46.247.108.207"
VPS_USER="deploy"
DOMAIN="api.adcopysurge.com"

echo "📋 Configuration:"
echo "   Key name: $KEY_NAME"
echo "   VPS Host: $VPS_HOST"
echo "   VPS User: $VPS_USER"
echo "   Domain: $DOMAIN"
echo ""

# Check if SSH directory exists
if [ ! -d ~/.ssh ]; then
    echo "📁 Creating ~/.ssh directory..."
    mkdir -p ~/.ssh
    chmod 700 ~/.ssh
fi

# Generate SSH key if it doesn't exist
if [ ! -f ~/.ssh/$KEY_NAME ]; then
    echo "🔑 Generating SSH key pair..."
    ssh-keygen -t ed25519 -C "gh-actions@adcopysurge" -f ~/.ssh/$KEY_NAME -N ""
    echo "✅ SSH key pair generated!"
else
    echo "⚠️  SSH key already exists: ~/.ssh/$KEY_NAME"
fi

echo ""
echo "🔑 SSH Key Files Created:"
echo "   Private key: ~/.ssh/$KEY_NAME"
echo "   Public key:  ~/.ssh/$KEY_NAME.pub"
echo ""

# Display public key
echo "📋 Public Key (copy this to your VPS):"
echo "======================================"
cat ~/.ssh/$KEY_NAME.pub
echo ""
echo ""

# Display private key for GitHub secrets
echo "🔒 Private Key (copy this to GitHub Secrets as DATALIX_SSH_KEY):"
echo "================================================================"
cat ~/.ssh/$KEY_NAME
echo ""
echo ""

# Installation instructions
echo "📝 Next Steps:"
echo "1. Copy the PUBLIC key to your VPS:"
echo "   ssh-copy-id -i ~/.ssh/$KEY_NAME.pub $VPS_USER@$VPS_HOST"
echo ""
echo "2. Test SSH connection:"
echo "   ssh -i ~/.ssh/$KEY_NAME $VPS_USER@$VPS_HOST"
echo ""
echo "3. Add these GitHub Repository Secrets:"
echo "   Go to: https://github.com/Adeliyio/acsurge/settings/secrets/actions"
echo ""
echo "   DATALIX_SSH_KEY = [Private key content above]"
echo "   DATALIX_HOST = $VPS_HOST"
echo "   DATALIX_USER = $VPS_USER"
echo "   DATALIX_DOMAIN = $DOMAIN"
echo ""

# Create a setup commands file
echo "🚀 Creating setup commands file..."
cat > ~/adcopysurge-ssh-setup-commands.txt << EOF
# AdCopySurge SSH Setup Commands
# Generated: $(date)

# 1. Copy public key to VPS:
ssh-copy-id -i ~/.ssh/$KEY_NAME.pub $VPS_USER@$VPS_HOST

# 2. Test connection:
ssh -i ~/.ssh/$KEY_NAME $VPS_USER@$VPS_HOST

# 3. GitHub Secrets to add:
DATALIX_SSH_KEY = [Copy private key from ~/.ssh/$KEY_NAME]
DATALIX_HOST = $VPS_HOST
DATALIX_USER = $VPS_USER
DATALIX_DOMAIN = $DOMAIN

# 4. Manual VPS setup (if needed):
ssh $VPS_USER@$VPS_HOST

# On VPS, ensure deploy user has sudo access:
sudo usermod -aG sudo $VPS_USER

# Create required directories:
sudo mkdir -p /home/deploy /var/backups/adcopysurge /run/adcopysurge /var/log/adcopysurge
sudo chown $VPS_USER:$VPS_USER /home/deploy
sudo chown www-data:www-data /run/adcopysurge /var/log/adcopysurge

# Install required packages (if not installed):
sudo apt update
sudo apt install -y python3.11 python3.11-venv python3.11-dev \\
    build-essential git redis-server nginx certbot python3-certbot-nginx \\
    postgresql-client htop curl unzip
EOF

echo "✅ Setup commands saved to: ~/adcopysurge-ssh-setup-commands.txt"
echo ""

# Automated setup option
echo "🤖 Automated Setup (Optional):"
echo "==============================="
read -p "Do you want to automatically copy the public key to your VPS? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "📤 Copying public key to VPS..."
    if ssh-copy-id -i ~/.ssh/$KEY_NAME.pub $VPS_USER@$VPS_HOST; then
        echo "✅ Public key copied successfully!"
        
        echo "🧪 Testing SSH connection..."
        if ssh -i ~/.ssh/$KEY_NAME $VPS_USER@$VPS_HOST "echo 'SSH connection successful!'" >/dev/null 2>&1; then
            echo "✅ SSH connection test passed!"
        else
            echo "❌ SSH connection test failed. Please check your VPS configuration."
        fi
    else
        echo "❌ Failed to copy public key. Please copy it manually:"
        echo "   ssh-copy-id -i ~/.ssh/$KEY_NAME.pub $VPS_USER@$VPS_HOST"
    fi
else
    echo "⏭️  Skipping automated setup. Please follow the manual steps above."
fi

echo ""
echo "🎉 SSH Key setup completed!"
echo ""
echo "📚 Next: Configure your GitHub repository secrets and trigger a deployment."
echo "📖 Full guide: docs/DATALIX_GITHUB_ACTIONS_DEPLOYMENT.md"