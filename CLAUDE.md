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

## Quick Reference

### Most Common Tasks
```bash
# Start backend development server
cd backend && uvicorn main:app --reload

# Start frontend development server
cd frontend && npm start

# Run backend tests
cd backend && pytest

# Create database migration
cd backend && alembic revision --autogenerate -m "description"

# Apply migrations
cd backend && alembic upgrade head

# Start Celery worker (for background tasks)
cd backend && celery -A app.celery_app worker --loglevel=info
```

### Critical Files for Ad Analysis
- **Main workflow:** `frontend/src/pages/NewAnalysis.jsx` → `backend/app/api/ads.py` → `backend/app/services/ad_analysis_service_enhanced.py`
- **Tools SDK:** `backend/packages/tools_sdk/tool_orchestrator.py` (runs 9 tools in parallel)
- **Platform config:** `backend/app/constants/platform_limits.py` (650+ lines of platform intelligence)
- **AI generation:** `backend/app/services/production_ai_generator.py`

### Quick Troubleshooting
- **Backend won't start:** Check `SECRET_KEY` in `backend/.env` (min 32 chars)
- **Database errors:** Verify `DATABASE_URL` format, run `alembic upgrade head`
- **Analysis fails:** Check OpenAI API key, verify 120s timeout in `apiClient.js`
- **Tests fail:** Ensure SQLite available, run `pytest -v` for details
- **CORS errors:** Add frontend URL to `CORS_ORIGINS` in backend `.env`

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

1. **Tools SDK (⚡ Critical):** Unified orchestration system for ad analysis tools. Located in `backend/packages/tools_sdk/`.
   - **ToolOrchestrator** runs 9 analysis tools in **parallel** (not sequential)
   - Performance: 60-120 seconds total vs 5-10 minutes if sequential
   - **The 9 Tools:**
     1. Ad Copy Analyzer - Platform fit, character limits, tone (ONLY tool with platform logic currently)
     2. Compliance Checker - Platform policies, prohibited words, legal compliance
     3. Psychology Scorer - 16 psychological triggers, cognitive biases
     4. A/B Test Generator - Variations based on 6 psychological frameworks
     5. ROI Copy Generator - 5 ROI strategies (investment, cost savings, time value, premium, scarcity)
     6. Industry Optimizer - 6 industry vocabularies, jargon optimization, role-based targeting
     7. Performance Forensics - Industry benchmarks, correlation patterns, failure detection
     8. Brand Voice Engine - 5 tones, 5 personality traits, learns from past ads
     9. Legal Risk Scanner - 6 legal risk categories, safer alternatives
   - Standardized interfaces via `ToolInput`/`ToolOutput`
   - Easy to add new tools without modifying existing code
   - **IMPORTANT:** Most tools are currently platform-agnostic and don't leverage `platform_limits.py` config

2. **Multi-Agent System:** AI optimization uses multiple specialized agents (persuasion expert, emotion expert, CTA specialist) coordinated by `MultiAgentOptimizer` in `agent_system.py`.
   - Agents run in parallel for consensus-based recommendations
   - Fallback strategy: OpenAI GPT-4 → Google Gemini → Retry with backoff

3. **Service Layer:** All business logic lives in `services/`. API routes are thin controllers that call services.
   - Routes validate and delegate → Services contain all logic → Models are ORM entities

4. **Dual Entrypoints:**
   - **Development:** `main.py` - Use `uvicorn main:app --reload` (API docs enabled)
   - **Production:** `main_production.py` - Use `uvicorn main_production:app` (API docs disabled, systemd uses this)

### Frontend Structure

React SPA with component-based architecture:

```
frontend/src/
├── pages/                 # Route components (one per page)
│   ├── NewAnalysis.jsx    # Main ad analysis interface (primary workflow)
│   ├── Dashboard.jsx      # User dashboard
│   ├── BillingCredits.jsx # Credit management
│   ├── InviteAccept.jsx   # Team invitation acceptance
│   └── agency/            # Agency-specific pages
│       ├── TeamManagement.jsx
│       ├── WhiteLabelSettings.jsx
│       └── ReportsBranding.jsx
├── components/            # Reusable UI components
│   ├── ComprehensiveAnalysisLoader.jsx  # Analysis progress visualization
│   ├── ComprehensiveResults.jsx         # Results display
│   └── SupportWidget.jsx                # Help/support system
├── services/              # API client modules
│   ├── apiClient.js       # Axios instance with auth (all API calls go here)
│   ├── apiService.js      # Main API methods
│   ├── authContext.js     # Supabase auth context
│   ├── teamService.js     # Team operations
│   ├── paddleService.js   # Paddle payment integration
│   └── whitelabelService.js
├── contexts/              # React contexts for global state
│   ├── ThemeContext.jsx   # Light/dark mode
│   ├── WhiteLabelContext.jsx  # White-label branding
│   └── SettingsContext.jsx
├── hooks/                 # Custom React hooks
│   └── useCredits.js      # Credit management hook
└── utils/                 # Helper functions
```

**Key Patterns:**

- **API Client:** All backend calls go through `apiClient.js` which handles auth tokens, error handling, and 120s timeout for analysis.
- **Supabase Auth:** Authentication managed by `authContext.js` using Supabase client.
- **React Query:** Used for server state management and caching (stale-while-revalidate).
- **Material-UI v5:** Component library for consistent UI.
- **State Management:** React Query (server state) + Context API (app state) + Local hooks (component state)

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

**Paddle Billing:**
```env
PADDLE_VENDOR_ID=your-vendor-id
PADDLE_API_KEY=your-api-key
PADDLE_CLIENT_TOKEN=your-client-token
PADDLE_WEBHOOK_SECRET=your-webhook-secret
PADDLE_ENVIRONMENT=sandbox  # or production

# Price IDs for each tier/billing period
PADDLE_GROWTH_MONTHLY_PRICE_ID=pri_...
PADDLE_GROWTH_YEARLY_PRICE_ID=pri_...
PADDLE_AGENCY_STANDARD_MONTHLY_PRICE_ID=pri_...
PADDLE_AGENCY_STANDARD_YEARLY_PRICE_ID=pri_...
PADDLE_AGENCY_PREMIUM_MONTHLY_PRICE_ID=pri_...
PADDLE_AGENCY_PREMIUM_YEARLY_PRICE_ID=pri_...
PADDLE_AGENCY_UNLIMITED_MONTHLY_PRICE_ID=pri_...
PADDLE_AGENCY_UNLIMITED_YEARLY_PRICE_ID=pri_...
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

### Ad Analysis Flow (60-120 seconds total)

**Complete Workflow:**
1. User enters ad copy in `NewAnalysis.jsx`
2. Frontend checks credits via `useCredits.js` hook
3. Deducts 1 credit (⚠️ Note: No refund on failure - known issue)
4. `POST /api/ads/analyze` → `api/ads.py` validates request
5. `EnhancedAdAnalysisService` orchestrates analysis:
   - Uses Tools SDK `ToolOrchestrator` to run 9 tools **in parallel**
   - Tools: Readability, Emotion, CTA strength, Persuasion, Compliance, Brand Voice, etc.
   - Parallel execution: 60-120s total (vs 5-10 min if sequential)
6. Results scored and saved to `ad_analyses` table
7. If AI generation requested, `ProductionAIService` generates 4 alternatives:
   - Persuasive variant
   - Emotional variant
   - Stats-heavy variant
   - Balanced variant
8. Response returned to `ComprehensiveResults.jsx` for display

**Critical Files:**
- Frontend: `frontend/src/pages/NewAnalysis.jsx`
- Backend API: `backend/app/api/ads.py`
- Service: `backend/app/services/ad_analysis_service_enhanced.py`
- Tools SDK: `backend/packages/tools_sdk/tool_orchestrator.py`
- AI Generation: `backend/app/services/production_ai_generator.py`

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

**Paddle Billing Integration:**
- Service: `paddle_service.py` (uses new Paddle Billing API, not Classic)
- Webhook handling at `/api/subscriptions/webhook` with HMAC verification
- Frontend checkout via `paddleService.js` with Paddle.js SDK

**Subscription Tiers:**
- `FREE` - 5 analyses/month
- `GROWTH` - 100 analyses/month
- `AGENCY_STANDARD` - 500 analyses/month
- `AGENCY_PREMIUM` - 1000 analyses/month
- `AGENCY_UNLIMITED` - Unlimited analyses

**Credits System:**
- Tracked in `user_credits` table with real-time Supabase subscriptions
- All transactions logged in `credit_transactions` for audit trail
- Credits allocated based on subscription tier via webhook events

### Team Invitations

**Code-Based System** (refactored from email-based):
- Team owners generate 6-character invitation codes via `POST /api/team/invite`
- Codes stored in `team_invitations` table with 7-day expiration
- Owner shares code manually (Slack, email, etc.)
- Invitee enters code to accept invitation
- Role-based access control (admin, editor, viewer, client)
- More reliable than email delivery, works in all environments

**Why Code-Based:**
- No dependency on email service availability
- Works in development without SMTP configuration
- User-controlled sharing method (Slack, WhatsApp, etc.)
- Simpler implementation and debugging

### White-Label System

**Features:**
- Custom branding per agency (logo, colors, company name)
- Subdomain support
- Custom email templates
- Report branding
- Stored in `whitelabel_settings` table

**Configuration:**
- Agency owners configure via `WhiteLabelSettings.jsx`
- Frontend context: `WhiteLabelContext.jsx`
- Backend service: `whitelabel_service.py`

## Database Schema

**Key Tables:**
- `users` - User accounts (linked to Supabase auth via `supabase_user_id`)
- `ad_analyses` - Analysis results and scores
- `ad_generations` - AI-generated alternative variants
- `agencies` - Agency/team organizations (with JSONB settings column)
- `team_invitations` - Pending team invites (6-character codes, 7-day expiration)
- `user_credits` - Credit balances per user (with real-time Supabase subscriptions)
- `credit_transactions` - Audit trail for all credit operations
- `subscriptions` - Paddle subscription data
- `whitelabel_settings` - Custom branding stored in agencies.settings JSONB
- `support_tickets` - Customer support system

**Database Connection:**
- PostgreSQL via Supabase (managed service)
- Retry logic with tenacity for VPS cold starts
- Connection pooling: size=5, max_overflow=10
- Pool pre-ping enabled to handle connection drops
- Both sync (psycopg2) and async (asyncpg) engines available

Migrations managed by Alembic in `backend/alembic/versions/`.

## Security Considerations

The application implements multiple security layers:

1. **Middleware Stack** (in `backend/app/middleware/` - order matters):
   - Content Security - Validates request content
   - Security Headers - CSP, HSTS, X-Frame-Options, etc.
   - Security Reporting - Handles CSP violation reports
   - CSRF Protection - For state-changing requests
   - Rate Limiting - IP-based (anonymous) and user-based (authenticated)

2. **Rate Limiting Details:**
   - Anonymous users: 20 requests/min (IP-based)
   - Authenticated users: 60 requests/min
   - Analysis endpoint (`/api/ads/analyze`):
     - Free tier: 5/min
     - Growth tier: 10/min
     - Agency tiers: 20/min
   - Implemented via Redis (graceful degradation if Redis unavailable)

3. **Authentication:**
   - JWT tokens from Supabase Auth
   - Token verification using `SUPABASE_JWT_SECRET`
   - Row-Level Security (RLS) in Supabase database for multi-tenancy
   - Middleware: `app/middleware/supabase_auth.py`

4. **API Security:**
   - API docs disabled in production (`docs_url=None` when `ENVIRONMENT=production`)
   - CORS restricted to specific origins
   - Input validation via Pydantic schemas
   - HTTPS redirect enforced in production

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
- `/api/blog/*` - Blog content system (markdown-based, optional feature via `ENABLE_BLOG=True`)

## Known Issues & Important Notes

### Credit System (UPDATED 2025-11-21)
- **Automatic refund on failure**: Credits are deducted atomically at the backend level when analysis starts. If analysis fails, credits ARE automatically refunded.
- **Atomic operations**: The backend uses database-level constraints (`WHERE current_credits >= :credit_cost`) to prevent race conditions
- **Implementation details**:
  - Backend handles all credit operations atomically in `backend/app/services/credit_service.py`
  - Automatic refunds implemented in `backend/app/api/ads.py` lines 217-228
  - Transaction logging to `credit_transactions` table for full audit trail
  - Frontend polls every 30 seconds for balance updates (`frontend/src/hooks/useCredits.js`)
- **Test coverage**: Race conditions and refunds are tested in `backend/tests/test_credit_service_security.py`

### Anonymous User Fallback
- If authentication fails during analysis, system falls back to 'anonymous' user
- Analysis completes but is not linked to user account
- Ensure proper authentication before allowing analysis

### Performance
- Tools SDK parallel execution is critical: 60-120s vs 5-10 min sequential
- Do not modify `execution_mode="parallel"` in `ad_analysis_service_enhanced.py`
- Analysis timeout set to 120s in `apiClient.js`

### Edge Cases & Input Validation
- **Very short copy** (<20 chars): May produce unreliable scores
- **Non-English text**: No language detection implemented, English-only patterns
- **Special characters/emojis**: Some regex patterns may behave unexpectedly with extensive emoji use
- **Missing fields**: Tools assume headline/body/CTA always exist
- **Placeholder text**: No detection for "lorem ipsum" or test content
- Consider implementing comprehensive input validation before analysis

### Development Notes
- Use `main.py` for development (API docs enabled)
- Use `main_production.py` for production testing (API docs disabled)
- Never use `main_launch_ready.py` in production (has guard to exit)
- Migrations: Always review autogenerated migrations before applying
- Testing: SQLite used for tests, PostgreSQL for development/production

### Recent Fixes & Active Development
- **Team Invitations:** Recently refactored from email-based to code-based system (see commits 696bbe3-562c926)
  - 6-character invitation codes with 7-day expiration
  - Fixed Supabase relationship ambiguity issues
  - Frontend-only solution implemented for better reliability
- **Platform Optimization:** Audit completed identifying platform intelligence integration gaps (see `AD_ANALYSIS_AUDIT_REPORT.md`)
- **Implementation Roadmap:** Detailed plans in `IMPLEMENTATION_PLANS.md` for connecting Tools SDK to platform config

### White-Label Asset Storage
- Logos and favicons uploaded to Supabase Storage bucket (`whitelabel-assets`)
- Public CDN URLs returned for assets
- Service: `whitelabel_service.py`
- Frontend context provides branding throughout app via `WhiteLabelContext.jsx`

### Blog System (Optional)
- Enabled via `ENABLE_BLOG=True` in backend config
- Content stored in `backend/content/blog/` as markdown files
- Uses `python-frontmatter` for metadata extraction
- Graceful degradation if blog content missing
- Router mounted at `/api/blog` when enabled

### Platform Intelligence Gap (IMPORTANT)
- **Critical Architecture Issue:** The system has TWO separate platform intelligence sources:
  1. `backend/app/constants/platform_limits.py` - 650+ lines of comprehensive platform config (power words, formality, emoji defaults, CTAs, etc.)
  2. `backend/packages/tools_sdk/tools/` - 9 analysis tools, mostly platform-agnostic
- **The Problem:** Only 1 of 9 tools imports and uses platform_limits.py
- **Impact:** Platform-specific intelligence exists but isn't being leveraged by most analysis tools
- **Solution Path:** Create `platform_adapter.py` bridge to connect Tools SDK with platform config
- See `AD_ANALYSIS_AUDIT_REPORT.md` for detailed analysis

### Language Support
- **Current:** English-only
- **Roadmap:** Spanish, German, French, Portuguese planned
- No language detection implemented yet
- All analysis assumes English input
