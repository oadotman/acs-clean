# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

AdCopySurge is a full-stack AI-powered SaaS platform for ad copy analysis and optimization. It analyzes advertising creatives, predicts performance, generates alternatives, and provides competitor benchmarking for agencies and marketers.

**Tech Stack:**
- **Backend:** FastAPI (Python 3.11+), SQLAlchemy, Supabase PostgreSQL, Celery + Redis
- **Frontend:** React 18, Material-UI, React Query, Axios
- **AI/ML:** OpenAI GPT, Hugging Face Transformers, multi-agent optimization system
- **Deployment:** Backend on VPS (Ubuntu 22.04, Nginx, Gunicorn+Uvicorn, systemd), Frontend on Netlify
- **Authentication:** JWT with Supabase Auth
- **Payments:** Paddle Billing integration

## Essential Commands

### Backend Development

```bash
# Navigate to backend directory
cd backend

# Install dependencies (development)
pip install -r requirements.txt

# Install dependencies (production/Python 3.12)
pip install -r requirements.txt -c constraints-py312.txt --prefer-binary

# Run development server with auto-reload
uvicorn main:app --reload

# Run production server (local testing)
uvicorn main_production:app --host 0.0.0.0 --port 8000

# Run with Gunicorn (production-like)
gunicorn main_production:app -c gunicorn.conf.py
```

### Frontend Development

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Start development server (port 3000)
npm start

# Build for production
npm build
```

### Database Migrations

```bash
cd backend

# Generate a new migration
alembic revision --autogenerate -m "description of changes"

# Apply migrations
alembic upgrade head

# Rollback last migration
alembic downgrade -1

# View migration history
alembic history
```

### Testing

```bash
# Backend tests
cd backend
pytest                          # Run all tests
pytest tests/test_auth.py       # Run specific test file
pytest -v                       # Verbose output
pytest -k "test_name"           # Run tests matching pattern

# Frontend tests
cd frontend
npm test                        # Run React tests
```

### Celery (Background Tasks)

```bash
cd backend

# Start Celery worker
celery -A app.celery_app worker --loglevel=info

# Start with Redis broker
celery -A app.celery_app worker --broker=redis://localhost:6379/0 --loglevel=info
```

## Architecture Overview

### Backend Structure

The backend follows a service-oriented architecture with clear separation of concerns:

```
backend/app/
├── api/                    # API route handlers
│   ├── auth.py            # Authentication endpoints
│   ├── ads.py             # Ad analysis endpoints
│   ├── creative.py        # Creative controls (advanced features)
│   ├── subscriptions.py   # Paddle subscription management
│   └── analytics.py       # Usage analytics
├── services/              # Business logic layer
│   ├── ad_analysis_service_enhanced.py  # Main analysis service (uses Tools SDK)
│   ├── production_ai_generator.py       # AI content generation
│   ├── agent_system.py                  # Multi-agent AI optimization
│   ├── auth_service.py                  # Authentication logic
│   ├── subscription_service.py          # Subscription management
│   ├── paddle_service.py                # Paddle billing integration
│   └── email_service.py                 # Email notifications
├── models/                # SQLAlchemy ORM models
├── schemas/               # Pydantic request/response schemas
├── core/                  # Configuration, database, logging
│   ├── config.py          # Settings (loads from .env)
│   ├── database.py        # Database connection
│   └── logging.py         # Structured logging setup
├── middleware/            # Security and rate limiting
├── routers/              # Additional route modules
│   ├── team.py           # Team invitation system
│   └── support.py        # Support tickets
└── tasks.py              # Celery background tasks
```

**Key Architecture Patterns:**

1. **Tools SDK:** Unified orchestration system for ad analysis tools (readability, emotion, CTA analysis, etc.). Located in `backend/packages/tools_sdk/`. Services use `ToolOrchestrator` for consistent tool execution.

2. **Multi-Agent System:** AI optimization uses multiple specialized agents (persuasion expert, emotion expert, CTA specialist) coordinated by `MultiAgentOptimizer` in `agent_system.py`.

3. **Service Layer:** All business logic lives in `services/`. API routes are thin controllers that call services.

4. **Dual Entrypoints:**
   - **Development:** `main.py` - Use `uvicorn main:app --reload`
   - **Production:** `main_production.py` - Use `uvicorn main_production:app` (systemd uses this)

### Frontend Structure

React SPA with component-based architecture:

```
frontend/src/
├── pages/                 # Route components (one per page)
│   ├── Dashboard.jsx      # Main dashboard
│   ├── AdAnalysis.js      # Ad analysis interface
│   ├── AnalysisResults.js # Results display
│   ├── ProjectsList.js    # Projects management
│   └── agency/            # Agency-specific pages
├── components/            # Reusable UI components
├── services/              # API client modules
│   ├── apiClient.js       # Axios-based API client
│   ├── authContext.js     # Supabase auth context
│   ├── projectService.js  # Project CRUD operations
│   └── paddleService.js   # Paddle payment integration
├── contexts/              # React contexts for state
├── hooks/                 # Custom React hooks
└── utils/                 # Helper functions
```

**Key Patterns:**

- **API Client:** All backend calls go through `apiClient.js` which handles auth tokens and error handling.
- **Supabase Auth:** Authentication managed by `authContext.js` using Supabase client.
- **React Query:** Used for server state management and caching.
- **Material-UI:** Component library for consistent UI.

## Important Configuration

### Environment Variables

Backend requires these variables in `backend/.env`:

**Required (Minimum):**
```env
SECRET_KEY=your-secret-key-min-32-chars
DATABASE_URL=postgresql://user:pass@host/db
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key
SUPABASE_JWT_SECRET=your-jwt-secret
```

**AI Services (Required for full functionality):**
```env
OPENAI_API_KEY=sk-...
HUGGINGFACE_API_KEY=hf_...
GEMINI_API_KEY=...
```

**Email Service (Resend - for team invitations):**
```env
RESEND_API_KEY=re_your_resend_api_key
RESEND_FROM_EMAIL=noreply@yourdomain.com
RESEND_FROM_NAME=AdCopySurge
```

**Production:**
```env
ENVIRONMENT=production
DEBUG=False
CORS_ORIGINS=https://yourdomain.com
ALLOWED_HOSTS=yourdomain.com
REDIS_URL=redis://localhost:6379/0
```

See `backend/.env.example` for complete list.

Frontend uses `frontend/.env`:
```env
REACT_APP_API_URL=http://localhost:8000
REACT_APP_SUPABASE_URL=https://your-project.supabase.co
REACT_APP_SUPABASE_ANON_KEY=your-anon-key
```

## Key Workflows

### Ad Analysis Flow

1. User submits ad copy via `POST /api/ads/analyze` (handled by `api/ads.py`)
2. Request validated using Pydantic schema (`schemas/ads.py`)
3. `EnhancedAdAnalysisService` orchestrates analysis:
   - Uses Tools SDK to run multiple analysis tools in parallel
   - Tools: Readability, Emotion, CTA strength, Persuasion, Compliance
4. Results scored and saved to database (`models/ad_analysis.py`)
5. If AI generation requested, `ProductionAIService` generates alternatives
6. Response includes scores, suggestions, and alternatives

### AI Content Generation

The system uses a multi-tiered AI approach:

1. **ProductionAIService** (`production_ai_generator.py`): Primary AI interface
   - Handles OpenAI and Gemini API calls
   - Implements retry logic and fallback strategies
   - Rate limiting and token management

2. **MultiAgentOptimizer** (`agent_system.py`): Advanced optimization
   - Multiple specialized AI agents (persuasion, emotion, CTA)
   - Parallel agent execution for faster results
   - Consensus-based scoring and recommendation

3. **Variant Generation**: Creates persuasive, emotional, and stats-heavy alternatives

### Subscription & Payments

- Paddle Billing integration via `paddle_service.py`
- Webhook handling for subscription events at `/api/subscriptions/webhook`
- Usage tracking: Free (5/month), Basic ($49, 100/month), Pro ($99, 500/month)
- Credits system tracked in database

### Team Invitations

- Team owners can invite members via `POST /api/team/invite`
- Automatically sends professional email invitations via **Resend**
- Secure 32-byte URL-safe tokens (`secrets.token_urlsafe(32)`)
- 7-day expiration for invitation links
- Personalized emails with agency branding
- Role-based access control (admin, editor, viewer, client)
- Graceful fallback if email sending fails (invitation still created)

**Resend Integration:**
- Production email delivery via Resend API (`https://api.resend.com/emails`)
- Professional HTML/text email templates in `app/templates/emails/`
- Mock mode for development (logs emails without sending)
- Requires `RESEND_API_KEY` and verified domain
- See `RESEND_SETUP.md` for complete setup guide

## Database Schema

**Key Tables:**
- `users` - User accounts (linked to Supabase auth)
- `ad_analyses` - Analysis results and scores
- `projects` - User projects (optional grouping)
- `subscriptions` - Paddle subscription data
- `team_invitations` - Pending team invites
- `support_tickets` - Customer support system

Migrations managed by Alembic in `backend/alembic/versions/`.

## Security Considerations

The application implements multiple security layers:

1. **Middleware** (in `backend/app/middleware/`):
   - Rate limiting (configurable per endpoint)
   - CSRF protection for state-changing requests
   - Security headers (CSP, HSTS, X-Frame-Options)
   - Content validation

2. **Authentication:**
   - JWT tokens from Supabase Auth
   - Token verification using `SUPABASE_JWT_SECRET`
   - Row-level security in Supabase database

3. **API Security:**
   - API docs disabled in production (`docs_url=None` when `ENVIRONMENT=production`)
   - CORS restricted to specific origins
   - Input validation via Pydantic schemas

## Deployment

### VPS Backend Deployment

Production backend runs on VPS with:
- **Systemd service:** `backend/deploy/adcopysurge.service` (uses `main_production:app`)
- **Nginx reverse proxy:** Config in `backend/deploy/nginx/`
- **Gunicorn + Uvicorn workers:** `gunicorn.conf.py` for worker configuration
- **Celery worker:** Separate systemd service for background tasks

Deploy command (from VPS):
```bash
cd /opt/adcopysurge/backend
git pull
source venv/bin/activate
pip install -r requirements.txt
alembic upgrade head
sudo systemctl restart adcopysurge
sudo systemctl restart celery-adcopysurge
```

### Frontend Deployment

Frontend deployed on Netlify:
- Build command: `npm run build`
- Publish directory: `build/`
- Environment variables configured in Netlify dashboard
- Automatic deploys from main branch

## Troubleshooting

### Common Issues

**Backend won't start - Missing SECRET_KEY:**
- Ensure `SECRET_KEY` is set in `backend/.env` (minimum 32 characters)

**Database connection errors:**
- Verify `DATABASE_URL` format: `postgresql://user:pass@host:port/dbname`
- For Supabase: Use the connection string from project settings (enable pooling for production)

**AI features not working:**
- Check `OPENAI_API_KEY` is valid and has credits
- AI services gracefully degrade if unavailable (returns mock data in dev)

**CORS errors in browser:**
- Verify frontend URL is in `CORS_ORIGINS` (backend `.env`)
- Check `REACT_APP_API_URL` points to correct backend

**Tests failing:**
- Ensure test database is configured (uses SQLite by default)
- Run `pytest -v` for detailed error messages

### Logs and Debugging

**Backend logs:**
- Development: Console output with structured logging
- Production: Check systemd journal: `journalctl -u adcopysurge -f`

**Database queries:**
- Enable SQL logging: Set `LOG_LEVEL=debug` in `.env`

**Celery tasks:**
- Check worker logs: `journalctl -u celery-adcopysurge -f`
- Inspect Redis: `redis-cli monitor`

## Development Workflow

1. **Create feature branch:** `git checkout -b feature/description`
2. **Backend changes:**
   - Add/modify service logic in `app/services/`
   - Update API routes in `app/api/`
   - Add tests in `tests/`
   - Run `pytest` to verify
3. **Database changes:**
   - Modify models in `app/models/`
   - Generate migration: `alembic revision --autogenerate -m "description"`
   - Apply: `alembic upgrade head`
4. **Frontend changes:**
   - Update components/pages
   - Update API calls in `services/`
   - Test in browser
5. **Commit and push:** Follow commit message conventions
6. **Deploy:** Merge to main triggers Netlify deploy; manually deploy backend to VPS

## API Documentation

When backend is running, interactive API docs available at:
- Swagger UI: `http://localhost:8000/api/docs` (development only)
- ReDoc: `http://localhost:8000/api/redoc` (development only)

Main endpoint groups:
- `/api/auth/*` - Authentication (register, login, password reset)
- `/api/ads/*` - Ad analysis (analyze, history, alternatives)
- `/api/creative/*` - Advanced creative controls
- `/api/subscriptions/*` - Paddle billing integration
- `/api/team/*` - Team management and invitations
- `/api/analytics/*` - Usage analytics
- `/api/blog/*` - Blog content system (markdown-based)
