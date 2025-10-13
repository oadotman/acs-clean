# AdCopySurge Production Deployment Guide

## Prerequisites

### System Requirements
- Python 3.11 (Datalix VPS compatible)
- PostgreSQL database
- Redis (optional, for caching)
- Nginx (for reverse proxy)

### Required Environment Variables

```bash
# Application
ENVIRONMENT=production
SECRET_KEY=your_32_char_secret_key_here
DEBUG=False
HOST=0.0.0.0
PORT=8000

# Database
DATABASE_URL=postgresql://username:password@localhost:5432/adcopysurge

# Supabase
REACT_APP_SUPABASE_URL=your_supabase_url
REACT_APP_SUPABASE_ANON_KEY=your_supabase_anon_key
SUPABASE_SERVICE_ROLE_KEY=your_supabase_service_role_key
SUPABASE_JWT_SECRET=your_supabase_jwt_secret

# AI Services
OPENAI_API_KEY=your_openai_api_key

# Paddle (Payment)
PADDLE_VENDOR_ID=your_paddle_vendor_id
PADDLE_API_KEY=your_paddle_api_key
PADDLE_WEBHOOK_SECRET=your_paddle_webhook_secret
PADDLE_ENVIRONMENT=production

# Email (Optional)
RESEND_API_KEY=your_resend_api_key
RESEND_FROM_EMAIL=noreply@adcopysurge.com

# Redis (Optional)
REDIS_URL=redis://localhost:6379/0

# Monitoring (Optional)
SENTRY_DSN=your_sentry_dsn
```

## Deployment Steps

### 1. Server Setup

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python 3.11
sudo apt install python3.11 python3.11-venv python3.11-dev python3-pip

# Install system dependencies
sudo apt install postgresql-client nginx supervisor redis-server

# Create deployment user
sudo useradd -m -s /bin/bash deploy
sudo usermod -aG www-data deploy
```

### 2. Application Setup

```bash
# Switch to deploy user
sudo su - deploy

# Clone/upload your application
git clone <your-repo> /home/deploy/adcopysurge
cd /home/deploy/adcopysurge

# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -r backend/requirements.txt
```

### 3. Environment Configuration

```bash
# Create .env file
cp backend/.env.example backend/.env
# Edit backend/.env with your production values
```

### 4. Database Setup

```bash
# Run database migrations
cd backend
python -m alembic upgrade head

# Initialize database (if needed)
python init_database.py
```

### 5. Gunicorn Setup

```bash
# Test Gunicorn configuration
cd /home/deploy/adcopysurge/backend
gunicorn -c gunicorn.conf.py main:app --check-config

# Create systemd service
sudo cp deploy/adcopysurge.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable adcopysurge
sudo systemctl start adcopysurge
```

### 6. Nginx Configuration

```bash
# Copy nginx configuration
sudo cp deploy/nginx.conf /etc/nginx/sites-available/adcopysurge
sudo ln -s /etc/nginx/sites-available/adcopysurge /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

## Health Checks

### Application Health
```bash
# Check if app is responding
curl http://localhost:8000/health

# Detailed health check
curl http://localhost:8000/healthz
```

### Service Status
```bash
# Check Gunicorn service
sudo systemctl status adcopysurge

# Check logs
sudo journalctl -u adcopysurge -f
```

## Monitoring

### Log Files
- Application logs: `/var/log/adcopysurge/`
- Nginx logs: `/var/log/nginx/`
- System logs: `journalctl -u adcopysurge`

### Performance Monitoring
```bash
# Monitor processes
ps aux | grep gunicorn

# Monitor resources
htop
```

## Backup & Maintenance

### Database Backup
```bash
# Daily backup script
pg_dump $DATABASE_URL > backup_$(date +%Y%m%d).sql
```

### Application Updates
```bash
# Stop service
sudo systemctl stop adcopysurge

# Update code
git pull origin main

# Install new dependencies (if any)
source venv/bin/activate
pip install -r backend/requirements.txt

# Run migrations
cd backend
python -m alembic upgrade head

# Start service
sudo systemctl start adcopysurge
```

## Security Checklist

- [ ] Firewall configured (UFW)
- [ ] SSL certificate installed
- [ ] Environment variables secured
- [ ] Database user has minimal permissions
- [ ] Regular security updates scheduled
- [ ] Log rotation configured
- [ ] Monitoring and alerting set up

## Troubleshooting

### Common Issues

1. **Import Errors**
   - Check PYTHONPATH in gunicorn.conf.py
   - Ensure all __init__.py files exist

2. **Database Connection Issues**
   - Verify DATABASE_URL format
   - Check PostgreSQL is running
   - Verify network connectivity

3. **Gunicorn Won't Start**
   - Check gunicorn.conf.py syntax
   - Verify socket permissions
   - Check application imports

4. **Frontend/Backend Communication Issues**
   - Verify CORS settings
   - Check nginx proxy configuration
   - Ensure API endpoints are accessible

### Log Analysis
```bash
# Search for errors
sudo journalctl -u adcopysurge | grep ERROR

# Follow real-time logs
sudo journalctl -u adcopysurge -f

# Check nginx errors
sudo tail -f /var/log/nginx/error.log
```

## Performance Optimization

### Gunicorn Workers
- For VPS: 2-4 workers recommended
- Monitor CPU/memory usage
- Adjust `max_requests` for memory management

### Database
- Regular VACUUM and ANALYZE
- Connection pooling
- Index optimization

### Caching
- Redis for session storage
- API response caching
- Static file caching via nginx

## Contact & Support

For deployment issues, check:
1. Application logs
2. System logs
3. Database connectivity
4. Environment variables

Remember to test in staging environment first!