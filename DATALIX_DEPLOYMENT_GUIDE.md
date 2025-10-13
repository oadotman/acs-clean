# 🚀 AdCopySurge Datalix Deployment Guide

## 📋 Pre-Deployment Checklist

### ✅ Credit System Security Confirmed
- **Your user (92f3f140-ddb5-4e21-a6d7-814982b55ebc)** has unlimited agency plan ✅
- **Other users** are restricted to their plan limits by Row Level Security ✅
- **Database permissions** are properly secured ✅

---

## 🔧 Environment Configuration

### 1. Frontend Environment Variables (.env.production)

Copy the `.env.production.template` and fill in these **CRITICAL** variables:

```bash
# REQUIRED - Replace with your actual values
REACT_APP_API_URL=https://your-datalix-backend-url.com/api
REACT_APP_DOMAIN=your-domain.com

# KEEP THESE - Your working Supabase credentials
REACT_APP_SUPABASE_URL=https://tqzlsajhhtkhljdbjkyg.supabase.co
REACT_APP_SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InRxemxzYWpoaHRraGxqZGJqa3lnIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTY5OTYzOTMsImV4cCI6MjA3MjU3MjM5M30.0uI56qJGE5DQwEvcfYlcOIz2NGC-msMVrTRw6d-RQuI

# OPTIONAL but recommended
REACT_APP_OPENAI_API_KEY=sk-your-openai-key-here
REACT_APP_GA_MEASUREMENT_ID=G-YOUR-GA-ID
REACT_APP_PADDLE_VENDOR_ID=your_paddle_vendor_id
```

### 2. Backend Environment Variables (.env)

Copy the `backend/.env.production.template` and fill in these **CRITICAL** variables:

```bash
# SECURITY - Generate new keys!
SECRET_KEY=your-super-secret-production-key-2024
ENVIRONMENT=production
DEBUG=false

# DATABASE - Use PostgreSQL for production
DATABASE_URL=postgresql://user:password@host:port/database_name

# KEEP THESE - Your working Supabase credentials  
SUPABASE_URL=https://tqzlsajhhtkhljdbjkyg.supabase.co
SUPABASE_SERVICE_ROLE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InRxemxzYWpoaHRraGxqZGJqa3lnIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1Njk5NjM5MywiZXhwIjoyMDcyNTcyMzkzfQ.I4Bs0UL5UD3eGAXQmxmTa6zof17XHgl1AyeN-p4fyYg

# REQUIRED for AI functionality
OPENAI_API_KEY=sk-your-actual-openai-api-key-here

# CORS - Replace with your actual domains
ALLOWED_HOSTS=["https://your-domain.com", "https://your-datalix-app.com"]

# EMAIL - Required for user notifications
RESEND_API_KEY=re_your_resend_api_key_here
# OR use Gmail:
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
```

---

## 🛠️ Datalix Deployment Steps

### Step 1: Prepare Your Repository
```bash
# Ensure your changes are committed
git add .
git commit -m "Production environment configuration"
git push origin main
```

### Step 2: Datalix Configuration

1. **Frontend Deployment**:
   - Deploy from: `/frontend` directory
   - Build command: `npm run build`
   - Environment: Copy from `.env.production.template`

2. **Backend Deployment**:
   - Deploy from: `/backend` directory  
   - Start command: `python main.py` or `uvicorn main:app --host 0.0.0.0 --port 8000`
   - Environment: Copy from `backend/.env.production.template`

3. **Database Setup**:
   - Use PostgreSQL (not SQLite)
   - Import your schema if needed
   - **Your Supabase database is already configured and working!**

---

## ⚠️ IMPORTANT SECURITY NOTES

### 🔒 What's Already Secure
- ✅ **Only your user has unlimited credits**
- ✅ **Row Level Security policies protect user data**
- ✅ **Credit system properly restricts other users**
- ✅ **Database permissions are correctly configured**

### 🛡️ Production Security Checklist
- [ ] Generate new `SECRET_KEY` (never use development keys)
- [ ] Set `DEBUG=false`
- [ ] Set `BYPASS_AUTH_IN_DEV=false`
- [ ] Use HTTPS only (`https://` URLs)
- [ ] Enable CORS for your domain only
- [ ] Set up proper SSL certificates

---

## 🧪 Testing After Deployment

### Test Credit System:
1. **Create a test user account**
2. **Verify they get 5 credits (free plan)**
3. **Verify they can't access agency features**
4. **Test logo upload with your unlimited account**

### Test Core Features:
- [ ] User registration/login
- [ ] Ad copy analysis 
- [ ] Credit consumption
- [ ] Agency features (for your account)
- [ ] Logo upload functionality

---

## 📞 Support

If you encounter issues:

1. **Check logs** for error messages
2. **Verify environment variables** are set correctly
3. **Test database connection** 
4. **Confirm Supabase connectivity**

---

## 📁 File Checklist for Datalix

Upload these files to your Datalix deployment:

### Frontend:
- [ ] All files in `/frontend` directory
- [ ] `.env.production` (configured)
- [ ] `package.json` and `package-lock.json`

### Backend:
- [ ] All files in `/backend` directory  
- [ ] `.env` (from production template)
- [ ] `requirements.txt`
- [ ] `main.py`

---

## 🎉 Post-Deployment Verification

Once deployed, test these URLs:

- `https://your-domain.com` - Frontend loads
- `https://your-domain.com/api/health` - Backend health check
- `https://your-domain.com/api/credits/debug/user/92f3f140-ddb5-4e21-a6d7-814982b55ebc` - Your credits

**Your unlimited credits should show: 999999**
**New users should show: 5 credits**

---

## 🔗 Repository
**GitHub**: https://github.com/oadotman/acs-clean.git  
**Latest Commit**: a4b48a9 - Fix critical issues