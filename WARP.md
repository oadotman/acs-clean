# WARP.md

This file provides guidance to WARP (warp.dev) when working with code in this repository.

## Overview

AdCopySurge is an AI-powered ad copy analysis platform that helps agencies, SMBs, and freelance marketers create better-performing ads. The platform provides detailed scoring, competitor benchmarking, and AI-generated alternatives for advertising copy across multiple platforms (Facebook, Google, LinkedIn, TikTok).

## Quick Start

### Prerequisites
- Python 3.11+ with venv support
- Node.js 18+ with npm 9+
- Redis 7+
- PostgreSQL (via Supabase)

### Local Development Setup

1. **Backend Setup**
```bash
cd backend
python -m venv venv
# Windows
venv\Scripts\activate
# Unix/macOS
source venv/bin/activate

pip install -r requirements.txt
```

2. **Frontend Setup**  
```bash
cd frontend
npm install
```

3. **Environment Configuration**
```bash
# Copy and configure environment
cp backend/.env.example backend/.env
# Edit .env with required variables (see Configuration section)
```

4. **Start Development Servers**
```bash
# Backend (from backend/ directory)
uvicorn main:app --reload

# Frontend (from frontend/ directory)  
npm start

# Or both simultaneously (from frontend/ directory)
npm run dev
```

The application will be available at:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/api/docs

## Common Development Commands

### Backend Commands
```bash
cd backend

# Development server with auto-reload
uvicorn main:app --reload

# Production entrypoint (VPS deployment)
uvicorn main_production:app --host 0.0.0.0 --port 8000 --workers 2

# Install missing dependencies (required for all 9 tools)
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
pip install reportlab weasyprint

# Run tests
pytest
pytest --cov  # with coverage

# Test all 9 tools comprehensive analysis
python test_all_9_tools_complete.py

# Database migrations
alembic upgrade head
alembic revision --autogenerate -m "description"

# Linting (if configured)
flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics

# Start Celery worker (background tasks)
celery -A app.celery_app worker --loglevel=info
```

### Frontend Commands
```bash
cd frontend

# Development server
npm start

# Build for production
npm run build

# Run tests
npm test
npm test -- --coverage --watchAll=false  # CI mode

# Linting (if configured)
npm run lint --if-present
```

### Test Individual Components
```bash
# Backend: Test specific tool
cd backend
python test_all_9_tools_complete.py

# Backend: Test authentication
pytest test_auth.py -v

# Frontend: Test with coverage
npm test -- --coverage --testPathPattern=src/components/
```

## Architecture

### Updated Architecture (Tools SDK)
```
Internet → Nginx (Port 80/443) → {
  "/" → React SPA (Static Files)
  "/api/*" → FastAPI Backend (localhost:8000) → Tools SDK (9 Core Tools)
}

Backend Services:
FastAPI (main_production.py) ↔ Tools SDK Orchestrator ↔ 9 Analysis Tools
                             ↔ Supabase PostgreSQL
                             ↔ Redis (caching + Celery broker)
                             ↔ Celery Workers (background tasks)
                             ↔ External APIs (OpenAI, Hugging Face, Resend)

Tools SDK (9 Core Tools):
1. Ad Copy Analyzer - Core effectiveness and scoring
2. Compliance Checker - Platform policy violations
3. Psychology Scorer - 15 psychological triggers
4. A/B Test Generator - 8 test variations
5. ROI Copy Generator - Premium-positioned versions
6. Industry Optimizer - Industry-specific language
7. Performance Forensics - Performance factors analysis
8. Brand Voice Engine - Tone consistency and voice match (supports past ads learning)
9. Legal Risk Scanner - Legally problematic claims
```

### Key Components

**Backend (FastAPI)**
- `backend/app/api/` - API route handlers (auth, ads, analytics, subscriptions)
- `backend/app/services/` - Business logic for ad analysis, AI generation
- `backend/app/models/` - SQLAlchemy database models
- `backend/app/core/` - Configuration, database, error handling
- `backend/main_production.py` - Production ASGI application
- `backend/main.py` - Development ASGI application with debug features

**Frontend (React 18)**
- `frontend/src/components/` - Reusable UI components (Material-UI)
- `frontend/src/pages/` - Route-based page components
- `frontend/src/services/` - API client and authentication logic
- Uses React Query for data fetching and state management

**Key Features**
- AI-powered ad copy analysis (readability, persuasion, emotion, CTA strength)
- Multi-platform optimization (Facebook, Google, LinkedIn, TikTok)
- Alternative ad generation with different strategies
- PDF report generation for agencies
- Subscription management with tiered pricing
- Blog system with markdown content

## Configuration & Environment Variables

### Required Environment Variables

```bash
# backend/.env
SECRET_KEY=your-super-secret-key-change-this-min-32-chars
DATABASE_URL=postgresql://user:pass@host:port/dbname  # Supabase
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key
SUPABASE_JWT_SECRET=your-jwt-secret

# Optional but recommended for full functionality
OPENAI_API_KEY=your-openai-api-key
HUGGINGFACE_API_KEY=your-huggingface-api-key
REDIS_URL=redis://localhost:6379/0

# Email (Resend)
RESEND_API_KEY=your-resend-api-key
SMTP_USERNAME=your-email@domain.com
SMTP_PASSWORD=your-smtp-password

# Monitoring
SENTRY_DSN=your-sentry-dsn
```

### Frontend Environment Variables

```bash
# frontend/.env
REACT_APP_API_URL=http://localhost:8000  # or production API URL
REACT_APP_SUPABASE_URL=https://your-project.supabase.co
REACT_APP_SUPABASE_ANON_KEY=your-anon-key
```

## Database Management

### Migrations
```bash
cd backend
source venv/bin/activate

# Create new migration
alembic revision --autogenerate -m "Add new table"

# Apply migrations
alembic upgrade head

# Check migration status
alembic current
alembic history
```

### Database Initialization
The application automatically creates tables on startup via `create_all_tables()` function.

## Deployment (Datalix VPS)

The application is deployed to a Datalix VPS running Ubuntu 22.04 with the following architecture:

### VPS Setup
- **Frontend**: Served by Nginx as static files (React build)
- **Backend**: Gunicorn + Uvicorn workers managed by systemd
- **Database**: Supabase PostgreSQL (external managed service)
- **Cache/Queue**: Redis server on VPS
- **Web Server**: Nginx with SSL termination

### Deployment Process

**Automatic Deployment via GitHub Actions:**
- Push to `main` branch triggers production deployment
- Push to `develop` branch triggers staging deployment
- Workflows defined in `.github/workflows/deploy-backend.yml` and `deploy-frontend.yml`

**Manual Deployment:**
```bash
# On VPS (as deploy user)
cd /home/deploy/adcopysurge
git pull origin main

# Update backend
cd backend
source venv/bin/activate
pip install -r requirements.txt
alembic upgrade head

# Update frontend
cd ../frontend
npm ci
npm run build

# Restart services
sudo systemctl restart adcopysurge-backend.service
sudo systemctl restart nginx
```

### Service Management
```bash
# Check service status
sudo systemctl status adcopysurge-backend.service
sudo systemctl status nginx
sudo systemctl status redis-server

# View logs
sudo journalctl -u adcopysurge-backend.service -f
sudo tail -f /var/log/nginx/adcopysurge_error.log

# Restart services
sudo systemctl restart adcopysurge-backend.service nginx
```

## CI/CD Pipeline

### GitHub Actions Workflows

**Backend Deployment (`.github/workflows/deploy-backend.yml`)**
- Triggers on push to `main`/`develop` branches or manual dispatch
- Runs tests with Python 3.11
- Linting with flake8
- Deploys to Datalix VPS via SSH
- Creates GitHub releases for production deployments

**Frontend Deployment (`.github/workflows/deploy-frontend.yml`)**  
- Triggers on frontend file changes
- Runs tests and builds React application
- Deploys to Netlify (staging/production)
- Node.js 18 with npm caching

### Testing Strategy
- **Backend**: pytest with async support, API endpoint testing
- **Frontend**: React Testing Library, Jest
- **Integration**: Comprehensive tool testing via `test_all_9_tools_complete.py`
- **Production Readiness**: Health checks and startup validation

## Development Workflows

### Adding New API Endpoints
1. Create route handler in `backend/app/api/`
2. Add business logic in `backend/app/services/`
3. Update database models if needed in `backend/app/models/`
4. Add tests in `backend/tests/`
5. Update frontend API client in `frontend/src/services/`

### Adding New AI Tools
1. Implement service in `backend/app/services/`
2. Add route in `backend/app/api/ads.py`
3. Create frontend interface in `frontend/src/components/`
4. Add comprehensive tests in `backend/test_all_tools.py`

### Blog Content Management
- Markdown files stored in `content/blog/`
- Frontend-matter for metadata
- Backend serves via `/api/blog` endpoints
- Frontend renders with markdown parser

## Troubleshooting

### Common Issues

**"Failed to fetch" errors in frontend:**
- Check if backend is running on correct port
- Verify CORS settings in `main.py`
- Ensure frontend API_URL matches backend host

**Database connection errors:**
- Verify DATABASE_URL format and credentials
- Check Supabase service availability
- Ensure database migrations are up to date

**Authentication issues:**
- Check JWT_SECRET consistency between Supabase and backend
- Verify Supabase configuration and API keys
- Test auth endpoints directly via `/api/docs`

**AI tool failures:**
- Verify OpenAI API key and quota
- Check Hugging Face API connectivity
- Review service-specific error logs

### Monitoring & Health Checks
- Health endpoint: `GET /health`
- Metrics endpoint: `GET /metrics` 
- Service status: Check systemd service logs
- Application logs: Available via structured logging

### Performance Optimization
- Redis caching for frequently accessed data
- Database connection pooling via SQLAlchemy
- Frontend code splitting and lazy loading
- CDN serving for static assets (Netlify)

## Platform Compatibility

### Windows Development
The codebase includes Windows-specific considerations:
- **Emoji Compatibility**: `main_launch_ready.py` uses Windows-compatible symbols ([*], [+], etc.) instead of Unicode emojis
- **Path Handling**: All file operations use proper Windows path separators
- **PowerShell Scripts**: Windows deployment scripts available in `push-and-deploy.bat`

### Tools SDK Architecture (NEW)
The system now uses a modern Tools SDK architecture:
- **9 Core Tools**: All analysis now runs through the Tools SDK orchestrator
- **Parallel Execution**: Tools run in parallel for faster analysis
- **Graceful Degradation**: If tools fail, system falls back to simplified scoring
- **Comprehensive Analysis**: `/api/ads/comprehensive-analyze` uses all 9 tools

### Required Dependencies
For full functionality, install these dependencies:
```bash
# PyTorch (for ML-based tools like Psychology Scorer, Emotion Analysis)
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu

# PDF Generation (for reports)
pip install reportlab weasyprint

# Other dependencies (already in requirements.txt)
pip install -r requirements.txt
```

### Brand Voice Engine Enhancement
The Brand Voice Engine now supports:
- **Past Ads Learning**: Provide past ads samples to learn brand voice patterns
- **Style Consistency**: Analyzes and maintains consistency across campaigns
- **Platform Adaptation**: Automatically adapts voice for different platforms

## Important Files & Directories

- `backend/main_production.py` - Production ASGI app (use in VPS)
- `backend/main.py` - Development ASGI app (local development)
- `backend/main_launch_ready.py` - Legacy dev runner with Windows compatibility fixes
- `backend/ENTRYPOINTS.md` - Explanation of different entry points
- `backend/start.sh` - VPS startup script with health checks
- `deploy/TESTING_GUIDE.md` - Comprehensive deployment testing guide
- `frontend/package.json` - Frontend dependencies and scripts
- `backend/requirements.txt` - Python dependencies
- `.github/workflows/` - CI/CD pipeline definitions
- `backend/packages/tools_sdk/` - Unified analysis tools SDK
