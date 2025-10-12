# 🧪 AdCopySurge Single-Server Testing Guide

This guide helps you verify that your unified Datalix VPS deployment is working correctly after using the localhost:8000 fixes.

## 🎯 Architecture Overview

Your new single-server setup eliminates the localhost:8000 hardcoding issues:

```
Internet → Nginx (Port 80/443) → {
  "/" → React App (Static Files)
  "/api/*" → FastAPI Backend (localhost:8000)
}
```

## ✅ Pre-Deployment Testing (Local)

### 1. Test Frontend Build
```bash
cd frontend
NODE_ENV=production npm run build
# Should create build/ directory with index.html
```

### 2. Test Backend Production Mode
```bash
cd backend
source venv/bin/activate
ENVIRONMENT=production python main_production.py
# Should start on 127.0.0.1:8000 (not 0.0.0.0)
```

### 3. Verify API Service Logic
```javascript
// In browser console after frontend build
console.log(process.env.NODE_ENV); // Should be "production"
// API calls should use "/api" not "http://localhost:8000/api"
```

## 🌐 Post-Deployment Testing (Datalix VPS)

### 1. Service Health Checks

```bash
# Check all services are running
sudo systemctl status adcopysurge-backend.service
sudo systemctl status nginx
sudo systemctl status redis-server

# Check ports
sudo netstat -tlnp | grep :80    # Nginx
sudo netstat -tlnp | grep :8000  # Backend (should only bind to 127.0.0.1)
```

### 2. Backend API Tests

```bash
# Direct backend test (on server)
curl http://127.0.0.1:8000/health
# Expected: {"status": "healthy", "timestamp": "..."}

curl http://127.0.0.1:8000/
# Expected: {"message": "AdCopySurge API is running", "version": "1.0.0", ...}
```

### 3. Nginx Proxy Tests

```bash
# Through Nginx proxy
curl http://v44954.datalix.de/health
curl http://v44954.datalix.de/api/auth/me  # Should get proper error (unauthenticated)

# Frontend serving
curl -I http://v44954.datalix.de/
# Should return 200 and serve React index.html
```

### 4. Frontend-Backend Integration Tests

Open browser to `http://v44954.datalix.de` and test:

#### 4.1 Network Tab Verification
- All API calls should go to `/api/*` (relative URLs)
- No calls should go to `localhost:8000`
- No CORS errors in console

#### 4.2 Authentication Flow
1. Try to access protected page
2. Should redirect to login
3. Login form submission should work
4. After login, API calls should include auth headers

#### 4.3 Core Features Test
1. **Ad Analysis**: Submit ad copy for analysis
2. **File Upload**: Try uploading files
3. **Tool Usage**: Test each of the 9 AI tools
4. **Navigation**: All React Router paths should work

## 🐛 Troubleshooting Common Issues

### Issue 1: "Failed to fetch" Errors
**Symptoms**: Frontend can't reach API
**Checks**:
```bash
# Check backend is running on correct port
sudo netstat -tlnp | grep :8000
curl http://127.0.0.1:8000/health

# Check Nginx proxy configuration
sudo nginx -t
sudo tail -f /var/log/nginx/adcopysurge_error.log
```

### Issue 2: CORS Errors
**Symptoms**: CORS policy errors in browser console  
**Cause**: This shouldn't happen with same-server deployment!
**Fix**: Check that all API calls use relative URLs (`/api/*`)

### Issue 3: 404 for React Routes
**Symptoms**: Direct access to `/dashboard` returns 404
**Check**: Nginx `try_files` configuration should fallback to `index.html`

### Issue 4: Static Assets 404
**Symptoms**: CSS/JS files not loading
**Checks**:
```bash
# Verify React build directory
ls -la /srv/adcopysurge/app/frontend/build/
# Should contain static/ folder and index.html

# Check Nginx root directive
sudo nginx -T | grep "root"
```

## 📊 Performance Verification

### Response Time Tests
```bash
# Backend performance
time curl http://127.0.0.1:8000/health

# Full stack performance
time curl http://v44954.datalix.de/health
time curl http://v44954.datalix.de/
```

### Load Testing (Optional)
```bash
# Install apache bench
sudo apt install apache2-utils

# Test backend
ab -n 100 -c 10 http://127.0.0.1:8000/health

# Test through proxy
ab -n 100 -c 10 http://v44954.datalix.de/health
```

## 🔒 Security Verification

### SSL/HTTPS Setup (After SSL Certificate)
```bash
# Check SSL certificate
sudo certbot certificates

# Test HTTPS redirect
curl -I http://v44954.datalix.de/
# Should return 301 redirect to https://

# Test HTTPS
curl -I https://v44954.datalix.de/
```

### Security Headers
```bash
curl -I http://v44954.datalix.de/ | grep -E "(X-Frame-Options|X-Content-Type-Options|X-XSS-Protection)"
```

## 📝 Test Checklist

### ✅ Pre-Deployment
- [ ] Frontend builds successfully with `NODE_ENV=production`
- [ ] Backend starts with `ENVIRONMENT=production`
- [ ] API service uses relative URLs in production mode
- [ ] All environment variables are configured

### ✅ Post-Deployment  
- [ ] All systemd services are active
- [ ] Backend health check passes (direct)
- [ ] Nginx proxy health check passes
- [ ] Frontend loads correctly
- [ ] No localhost:8000 references in network tab
- [ ] Authentication flow works
- [ ] File upload works
- [ ] All AI tools respond correctly
- [ ] React Router navigation works

### ✅ Production Readiness
- [ ] SSL certificate installed
- [ ] Security headers present
- [ ] Error logging configured
- [ ] Performance is acceptable
- [ ] Database connections work
- [ ] External API keys configured (OpenAI, etc.)

## 🚨 Emergency Rollback

If deployment fails, you can quickly rollback:

```bash
# Stop services
sudo systemctl stop adcopysurge-backend.service
sudo systemctl stop nginx

# Restore default nginx
sudo rm /etc/nginx/sites-enabled/adcopysurge
sudo ln -sf /etc/nginx/sites-available/default /etc/nginx/sites-enabled/

# Start basic nginx
sudo systemctl start nginx

# Check what went wrong
sudo journalctl -u adcopysurge-backend.service -n 50
sudo tail -f /var/log/nginx/adcopysurge_error.log
```

## 📞 Support Commands

```bash
# View live logs
sudo journalctl -u adcopysurge-backend.service -f
sudo tail -f /var/log/nginx/adcopysurge_access.log
sudo tail -f /var/log/nginx/adcopysurge_error.log

# Restart services
sudo systemctl restart adcopysurge-backend.service nginx

# Check service status
sudo systemctl status adcopysurge-backend.service nginx redis-server

# Update and redeploy
cd /srv/adcopysurge/app
git pull origin main
sudo systemctl restart adcopysurge-backend.service
```

---

**✨ Success Criteria**: When all tests pass, you'll have eliminated the localhost:8000 hardcoding issues and have a production-ready single-server deployment!