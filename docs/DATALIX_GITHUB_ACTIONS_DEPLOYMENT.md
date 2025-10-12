# 🚀 AdCopySurge Datalix VPS GitHub Actions Deployment Guide

**Updated:** September 15, 2025  
**Status:** Ready for production deployment  
**VPS:** v44954.datalix.de (46.247.108.207)  
**Domain:** api.adcopysurge.com  

## 📋 Overview

This guide covers the complete setup and configuration for automated deployment to your Datalix VPS using GitHub Actions. The deployment pipeline has been updated to remove all Digital Ocean dependencies and deploy directly to your Datalix server.

## 🔧 GitHub Repository Secrets Required

Before the deployment can work, you need to set up the following secrets in your GitHub repository:

### Navigate to: `Settings` → `Secrets and variables` → `Actions` → `New repository secret`

**Required Secrets:**

| Secret Name | Description | Example Value |
|------------|-------------|---------------|
| `DATALIX_SSH_KEY` | Private SSH key for deployment | `-----BEGIN OPENSSH PRIVATE KEY-----\n...` |
| `DATALIX_HOST` | VPS IP address | `46.247.108.207` |
| `DATALIX_USER` | SSH user for deployment | `deploy` |
| `DATALIX_DOMAIN` | Your production domain | `api.adcopysurge.com` |

## 🔐 SSH Key Setup (One-time setup)

### Step 1: Generate SSH Key Pair

```bash
# Generate SSH key pair for GitHub Actions
ssh-keygen -t ed25519 -C "gh-actions@adcopysurge" -f ~/.ssh/adcopysurge_deploy

# This creates two files:
# ~/.ssh/adcopysurge_deploy (private key) - goes to GitHub Secrets
# ~/.ssh/adcopysurge_deploy.pub (public key) - goes to VPS
```

### Step 2: Install Public Key on VPS

```bash
# Copy public key to VPS
ssh-copy-id -i ~/.ssh/adcopysurge_deploy.pub deploy@46.247.108.207

# Or manually append to authorized_keys:
cat ~/.ssh/adcopysurge_deploy.pub | ssh deploy@46.247.108.207 "mkdir -p ~/.ssh && cat >> ~/.ssh/authorized_keys"
```

### Step 3: Test SSH Connection

```bash
# Test the connection
ssh -i ~/.ssh/adcopysurge_deploy deploy@46.247.108.207

# You should be able to log in without a password
```

### Step 4: Add Private Key to GitHub Secrets

```bash
# Display the private key (copy this entire output)
cat ~/.ssh/adcopysurge_deploy

# Copy the entire key including the BEGIN and END lines
# Add this as the DATALIX_SSH_KEY secret in GitHub
```

## 🚀 Deployment Workflows

### Automatic Deployments

1. **Staging**: Automatically deploys when you push to `develop` branch
2. **Production**: Automatically deploys when you push to `main` branch

### Manual Deployments

You can also trigger deployments manually:

1. Go to `Actions` tab in GitHub
2. Select `Deploy Backend to Datalix VPS`
3. Click `Run workflow`
4. Choose environment: `staging` or `production`

## 📁 VPS Directory Structure

The deployment creates this structure on your VPS:

```
/home/deploy/
├── adcopysurge/                    # Production deployment
│   ├── backend/
│   │   ├── venv/                   # Python virtual environment
│   │   ├── .env                    # Environment configuration
│   │   └── ... (backend files)
│   └── deploy/                     # Deployment configurations
│       ├── nginx.conf
│       └── gunicorn.service
├── adcopysurge-staging/            # Staging deployment (develop branch)
└── ...

/var/backups/adcopysurge/           # Automatic backups
├── backup-20250915-180000/
└── ...

/etc/systemd/system/
├── gunicorn.service                # Backend service

/etc/nginx/sites-available/
├── adcopysurge                     # Nginx configuration
```

## ⚙️ Environment Configuration

### Production Environment File

The deployment automatically creates `.env` from your template. Make sure your VPS has the following configured:

```bash
# SSH into your VPS
ssh deploy@46.247.108.207

# Navigate to backend directory
cd /home/deploy/adcopysurge/backend

# Edit environment file
nano .env
```

**Required environment variables:**

```env
# Application
SECRET_KEY=your-super-secure-32-character-secret-key
DEBUG=false
ENVIRONMENT=production

# Database (Supabase)
DATABASE_URL=postgresql+psycopg2://postgres.YOUR_REF:YOUR_PASSWORD@aws-0-us-west-1.pooler.supabase.com:6543/postgres

# Supabase
SUPABASE_URL=https://tqzlsajhhtkhljdbjkyg.supabase.co
SUPABASE_ANON_KEY=your-supabase-anon-key
SUPABASE_SERVICE_ROLE_KEY=your-supabase-service-role-key

# AI Services
OPENAI_API_KEY=your-openai-api-key

# Server Configuration
SERVER_NAME=api.adcopysurge.com
CORS_ORIGINS=https://adcopysurge.netlify.app
HOST=0.0.0.0
PORT=8000
```

## 🔄 Deployment Process Flow

### What happens during deployment:

1. **Code Checkout**: Latest code is checked out from GitHub
2. **SSH Setup**: GitHub Actions connects to your VPS using the SSH key
3. **Backup**: Current deployment is backed up (production only)
4. **Code Update**: Repository is cloned/updated on the VPS
5. **Dependencies**: Python packages are installed/updated
6. **Configuration**: Services and Nginx configs are installed
7. **Service Restart**: Backend services are restarted
8. **Health Check**: Deployment is verified with health endpoint
9. **Rollback**: If deployment fails, automatic rollback is attempted

### Services Managed:

- **Gunicorn**: Backend application server
- **Nginx**: Reverse proxy and SSL termination
- **Systemd**: Service management

## 🧪 Testing Deployments

### Health Check Endpoints

After deployment, test these endpoints:

```bash
# Health check (internal)
curl http://localhost/health

# Health check (external)
curl https://api.adcopysurge.com/health

# API documentation
curl https://api.adcopysurge.com/docs

# Root endpoint
curl https://api.adcopysurge.com/
```

### Expected Responses

```json
# Health check should return:
{
  "status": "healthy",
  "timestamp": "2025-09-15T18:00:00Z"
}

# Root endpoint should return:
{
  "message": "AdCopySurge API is running",
  "version": "1.0.0",
  "status": "MVP Ready"
}
```

## 🚨 Troubleshooting

### Common Issues

#### 1. SSH Connection Failed
```bash
# Check if SSH key is correct
ssh -i ~/.ssh/adcopysurge_deploy deploy@46.247.108.207

# Verify key in GitHub secrets matches your private key
```

#### 2. Deployment Health Check Failed
```bash
# SSH into VPS and check service status
ssh deploy@46.247.108.207
sudo systemctl status gunicorn.service
sudo journalctl -u gunicorn.service -n 50
```

#### 3. Service Won't Start
```bash
# Check application logs
sudo journalctl -u gunicorn.service -f

# Check if environment file exists and is properly configured
ls -la /home/deploy/adcopysurge/backend/.env
```

#### 4. Nginx Configuration Issues
```bash
# Test Nginx configuration
sudo nginx -t

# Check Nginx logs
sudo tail -f /var/log/nginx/adcopysurge_error.log
```

### Manual Commands

```bash
# Restart services manually
sudo systemctl restart gunicorn.service
sudo systemctl restart nginx

# Check service status
sudo systemctl status gunicorn.service nginx

# View logs
sudo journalctl -u gunicorn.service -f
sudo tail -f /var/log/nginx/adcopysurge_access.log
```

## 🔧 Maintenance

### Manual Deployment (if needed)

```bash
# SSH into VPS
ssh deploy@46.247.108.207

# Navigate to project
cd /home/deploy/adcopysurge

# Pull latest changes
git pull origin main

# Update dependencies
cd backend
source venv/bin/activate
pip install -r requirements.txt

# Restart services
sudo systemctl restart gunicorn.service
```

### Backup Management

```bash
# View backups
ls -la /var/backups/adcopysurge/

# Restore from backup (if needed)
sudo cp -r /var/backups/adcopysurge/backup-TIMESTAMP/* /home/deploy/adcopysurge/
sudo systemctl restart gunicorn.service
```

### Log Management

```bash
# View deployment logs in GitHub Actions
# Go to: Actions → Your workflow run → View logs

# View server logs
sudo journalctl -u gunicorn.service -n 100
sudo tail -100 /var/log/nginx/adcopysurge_error.log
```

## 📊 Monitoring

### Service Health

```bash
# Check all services are running
sudo systemctl status gunicorn.service nginx redis-server

# Monitor resource usage
htop
df -h
free -m
```

### Automated Monitoring

The deployment includes health checks that will:
- ✅ Verify service startup
- ✅ Test HTTP endpoints
- ✅ Create automatic backups
- ✅ Attempt rollback on failure

## ✅ Deployment Checklist

Before your first deployment, ensure:

- [ ] SSH key is generated and added to GitHub secrets
- [ ] Public key is installed on VPS
- [ ] All required GitHub secrets are configured
- [ ] VPS has required system packages installed
- [ ] Domain DNS is pointing to your VPS
- [ ] Environment file is configured on VPS
- [ ] SSL certificate is installed (optional but recommended)

## 🎯 Success Criteria

Your deployment is successful when:

- ✅ GitHub Actions workflow completes without errors
- ✅ `curl https://api.adcopysurge.com/health` returns `200 OK`
- ✅ API documentation is accessible at `https://api.adcopysurge.com/docs`
- ✅ Services are running: `sudo systemctl status gunicorn nginx`
- ✅ No errors in logs: `sudo journalctl -u gunicorn.service`

## 📞 Support

If you encounter issues:

1. Check the GitHub Actions logs for detailed error messages
2. SSH into your VPS and check service logs
3. Verify all secrets are correctly configured
4. Ensure DNS is pointing to the correct IP address
5. Check that all required environment variables are set

---

**🎉 Your Datalix VPS deployment is now ready!**

Future code pushes to `main` branch will automatically deploy to production, and pushes to `develop` branch will deploy to staging.