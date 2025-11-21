# VPS Deployment Commands for AdCopySurge

## Complete Deployment Checklist

Copy and paste these commands in order on your VPS to deploy the application.

### 1. Connect to VPS and Navigate to Project
```bash
# SSH into your VPS (replace with your actual server details)
ssh root@your-vps-ip

# Navigate to project directory
cd /var/www/acs-clean
```

### 2. Pull Latest Code from GitHub
```bash
# Pull the latest changes
git pull origin main

# If you have local changes that need to be discarded:
# git stash
# git pull origin main
```

### 3. Backend Deployment

#### 3.1 Activate Virtual Environment
```bash
cd /var/www/acs-clean/backend
source ../venv/bin/activate
```

#### 3.2 Install/Update Dependencies
```bash
# For production with Python 3.12+ (with constraints file)
pip install -r requirements.txt -c constraints-py312.txt --prefer-binary

# OR for standard installation
# pip install -r requirements.txt
```

#### 3.3 Run Database Migrations
```bash
# Check current migration status
alembic current

# Apply all pending migrations
alembic upgrade head

# Verify migrations were applied
alembic current
```

#### 3.4 Kill Existing Processes on Port 8000
```bash
# Find and kill any process using port 8000
sudo lsof -t -i:8000 | xargs -r sudo kill -9

# Alternative method if lsof is not available:
# sudo fuser -k 8000/tcp

# Verify port is free
sudo netstat -tlnp | grep 8000
```

#### 3.5 Stop Services (if using systemd)
```bash
# Stop the application service
sudo systemctl stop adcopysurge

# Stop Celery worker if using background tasks
sudo systemctl stop celery-adcopysurge

# Check status
sudo systemctl status adcopysurge --no-pager
```

### 4. Configuration Verification

#### 4.1 Check Environment Variables
```bash
# Verify .env file exists and has required variables
cd /var/www/acs-clean/backend

# Check if .env exists
ls -la .env

# Verify critical environment variables are set (without showing values)
grep -E "^(SECRET_KEY|DATABASE_URL|SUPABASE_URL|OPENAI_API_KEY)=" .env | cut -d= -f1

# Should output:
# SECRET_KEY
# DATABASE_URL
# SUPABASE_URL
# OPENAI_API_KEY
```

#### 4.2 Test Database Connection
```bash
# Test database connection with Python
python -c "
from app.core.database import engine
from sqlalchemy import text
try:
    with engine.connect() as conn:
        result = conn.execute(text('SELECT 1'))
        print('✓ Database connection successful')
except Exception as e:
    print(f'✗ Database connection failed: {e}')
"
```

### 5. Start Services

#### 5.1 Test with Direct Uvicorn (for debugging)
```bash
# Test the application directly (Ctrl+C to stop)
cd /var/www/acs-clean/backend
python -m uvicorn main_production:app --host 0.0.0.0 --port 8000

# If that works, stop it (Ctrl+C) and proceed to production deployment
```

#### 5.2 Start with Gunicorn (Production)
```bash
# Using Gunicorn with the configuration file
cd /var/www/acs-clean/backend
gunicorn main_production:app -c gunicorn.conf.py --daemon

# OR without daemon mode to see output
# gunicorn main_production:app -c gunicorn.conf.py
```

#### 5.3 Start with Systemd (Recommended for Production)
```bash
# Reload systemd if service file was changed
sudo systemctl daemon-reload

# Start the application service
sudo systemctl start adcopysurge

# Enable auto-start on boot
sudo systemctl enable adcopysurge

# Check status
sudo systemctl status adcopysurge

# View logs
sudo journalctl -u adcopysurge -f --lines=50
```

#### 5.4 Start Celery Worker (if using background tasks)
```bash
# Start Celery worker
sudo systemctl start celery-adcopysurge
sudo systemctl enable celery-adcopysurge

# Check status
sudo systemctl status celery-adcopysurge

# View logs
sudo journalctl -u celery-adcopysurge -f --lines=50
```

### 6. Nginx Configuration

#### 6.1 Update Nginx Configuration (if needed)
```bash
# Edit Nginx config
sudo nano /etc/nginx/sites-available/adcopysurge

# Test Nginx configuration
sudo nginx -t

# Reload Nginx
sudo systemctl reload nginx
```

#### 6.2 Sample Nginx Configuration
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # Timeouts for long-running analysis
        proxy_connect_timeout 120s;
        proxy_send_timeout 120s;
        proxy_read_timeout 120s;
    }
}
```

### 7. Verification Steps

#### 7.1 Check Application Health
```bash
# Test local connection
curl -I http://localhost:8000/health

# Test API endpoint
curl http://localhost:8000/api/health

# Check if API docs are accessible (dev only)
curl -I http://localhost:8000/api/docs
```

#### 7.2 Monitor Logs
```bash
# Watch application logs
sudo journalctl -u adcopysurge -f

# Check Nginx access logs
sudo tail -f /var/log/nginx/access.log

# Check Nginx error logs
sudo tail -f /var/log/nginx/error.log
```

### 8. Troubleshooting Commands

#### If Application Won't Start:
```bash
# Check for port conflicts
sudo lsof -i:8000

# Check Python version
python --version

# Test imports
python -c "from main_production import app; print('✓ Import successful')"

# Check for missing dependencies
pip list | grep -E "(fastapi|uvicorn|sqlalchemy|supabase)"

# Check disk space
df -h

# Check memory
free -m
```

#### If Database Issues:
```bash
# Test database URL format
python -c "
import os
from dotenv import load_dotenv
load_dotenv()
db_url = os.getenv('DATABASE_URL', '')
if db_url.startswith('postgresql://'):
    print('✓ Database URL format looks correct')
else:
    print('✗ Database URL format may be incorrect')
"

# Reset Alembic if needed (CAREFUL - for dev only)
# alembic downgrade base
# alembic upgrade head
```

#### If Celery/Redis Issues:
```bash
# Check Redis is running
redis-cli ping

# Test Celery connection
cd /var/www/acs-clean/backend
celery -A app.celery_app inspect ping
```

### 9. Quick Restart Script

Create a quick restart script for future deployments:

```bash
# Create restart script
cat > /var/www/acs-clean/restart.sh << 'EOF'
#!/bin/bash
echo "🚀 Starting AdCopySurge deployment..."

# Navigate to project
cd /var/www/acs-clean

# Pull latest code
echo "📥 Pulling latest code..."
git pull origin main

# Backend setup
cd backend
source ../venv/bin/activate

# Update dependencies
echo "📦 Installing dependencies..."
pip install -r requirements.txt -c constraints-py312.txt --prefer-binary -q

# Run migrations
echo "🗄️ Running migrations..."
alembic upgrade head

# Restart services
echo "🔄 Restarting services..."
sudo systemctl restart adcopysurge
sudo systemctl restart celery-adcopysurge
sudo systemctl reload nginx

# Check status
echo "✅ Checking status..."
sudo systemctl status adcopysurge --no-pager
echo ""
echo "🎉 Deployment complete!"
EOF

chmod +x /var/www/acs-clean/restart.sh
```

Then for future deployments, just run:
```bash
/var/www/acs-clean/restart.sh
```

### 10. Security Reminders

```bash
# Ensure proper file permissions
chmod 600 /var/www/acs-clean/backend/.env

# Check firewall rules (if using ufw)
sudo ufw status

# Ensure only necessary ports are open
sudo netstat -tlnp
```

## One-Line Quick Deploy (After Initial Setup)

Once everything is configured, you can use this one-liner for quick updates:

```bash
cd /var/www/acs-clean && git pull && cd backend && source ../venv/bin/activate && pip install -r requirements.txt -q && alembic upgrade head && sudo systemctl restart adcopysurge && sudo systemctl status adcopysurge --no-pager
```

## Notes

- Replace `your-vps-ip` and `your-domain.com` with your actual values
- Ensure your `.env` file on the VPS has all required variables
- The `--daemon` flag runs Gunicorn in background mode
- Use `sudo journalctl -u adcopysurge -f` to monitor logs in real-time
- If using SSL, update Nginx config accordingly with Certbot