# AdCopySurge - Production Deployment Guide

## 🚀 Quick Start

### Prerequisites
- Node.js 18+ and npm
- Python 3.9+
- PostgreSQL or Supabase account
- OpenAI API key

### Environment Setup

#### Backend Configuration
1. Copy the template:
   ```bash
   cd backend
   cp .env.example .env
   ```

2. Configure required variables in `backend/.env`:
   ```env
   # Environment
   ENVIRONMENT=production
   DEBUG=false
   
   # Security (CHANGE THESE!)
   SECRET_KEY=your-super-secret-key-min-32-chars
   
   # Database
   DATABASE_URL=postgresql://user:password@host:5432/dbname
   
   # Supabase (Required for auth)
   SUPABASE_URL=https://your-project.supabase.co
   SUPABASE_ANON_KEY=your-anon-key
   SUPABASE_SERVICE_ROLE_KEY=your-service-role-key
   
   # AI API Keys (Required)
   OPENAI_API_KEY=sk-...
   
   # Optional: Additional AI providers
   ANTHROPIC_API_KEY=sk-ant-...
   HUGGINGFACE_API_KEY=hf_...
   ```

#### Frontend Configuration
1. Copy the template:
   ```bash
   cd frontend
   cp .env.example .env.production
   ```

2. Configure `frontend/.env.production`:
   ```env
   REACT_APP_SUPABASE_URL=https://your-project.supabase.co
   REACT_APP_SUPABASE_ANON_KEY=your-anon-key
   REACT_APP_API_URL=https://api.yourdomain.com/api
   REACT_APP_ENV=production
   ```

### Installation

#### Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

#### Frontend
```bash
cd frontend
npm install
```

### Running the Application

#### Development Mode
```bash
# Terminal 1 - Backend
cd backend
python main_launch_ready.py

# Terminal 2 - Frontend
cd frontend
npm start
```

#### Production Build
```bash
# Backend
cd backend
uvicorn main_production:app --host 0.0.0.0 --port 8000

# Frontend
cd frontend
npm run build
# Serve the build folder with nginx or your preferred web server
```

## 🔒 Security Checklist

- [ ] Changed all default SECRET_KEY values
- [ ] Using environment-specific `.env` files (not committed to git)
- [ ] API keys are stored securely
- [ ] CORS origins are properly configured
- [ ] HTTPS is enabled in production
- [ ] Database credentials are secure
- [ ] Rate limiting is configured
- [ ] Input validation is enabled

## 📊 Key Features

### Comprehensive AI Analysis
- **9 AI-Powered Tools**: Ad copy analyzer, compliance checker, psychology scorer, A/B test generator, ROI copy generator, industry optimizer, performance forensics, brand voice engine, and legal risk scanner
- **Multi-Platform Support**: Facebook, Instagram, LinkedIn, Google Ads, Twitter
- **Real-time Analysis**: Complete analysis in 30-60 seconds

### Credit System
- Flexible credit-based pricing
- Unlimited plans available
- Agency support with team management

### Integrations
- Webhook support for external systems
- API for third-party integrations
- Export capabilities (PDF, CSV)

## 🐛 Troubleshooting

### Backend Won't Start
- Check Python version: `python --version` (need 3.9+)
- Verify all environment variables are set
- Check database connection
- Review logs for errors

### Frontend Build Fails
- Clear node_modules: `rm -rf node_modules && npm install`
- Check Node version: `node --version` (need 18+)
- Verify API_URL is correct

### Analysis Timing Out
- The comprehensive analysis runs 9 AI tools and may take 30-60 seconds
- Increase timeout in `simple_test.py` if needed
- Check OpenAI API key is valid and has credits
- Monitor backend logs for progress

## 📚 API Documentation

Once running, access API docs at:
- Swagger UI: `http://localhost:8000/api/docs`
- ReDoc: `http://localhost:8000/api/redoc`

## 🆘 Support

For issues or questions:
1. Check existing issues on GitHub
2. Review the troubleshooting section
3. Contact support with detailed error logs

## 📝 License

Proprietary - All rights reserved
