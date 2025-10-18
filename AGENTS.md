# Repository Guidelines

## Project Structure & Module Organization

- Root contains deployment scripts, SQL migrations, and docs. Key folders:
  - frontend/ – React SPA source, Dockerfile, tests, and build assets
  - backend/ – FastAPI backend with entrypoints, packages/, app/, tests/, Dockerfile
  - app/ – Policy pages for the web app (api/, privacy/, security/)
  - docs/ and docs_archive/ – Documentation assets
  - database/ and SQL files at root – Supabase schema and audits
  - deploy/ and deployment/ – Service/unit files and deployment helpers
  - scripts/ and infra/, monitoring/, nginx/ – Ops utilities and config

## Build, Test, and Development Commands

```bash
# Frontend dev (React + concurrently back end)
cd frontend
npm install
npm run dev        # runs React and backend together (concurrently)

# Frontend only
npm start          # react-scripts start
npm run build      # production build
npm test           # react-scripts test

# Backend dev (FastAPI)
cd backend
python -m venv venv && source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn main_launch_ready:app --reload --port 8000

# Backend via Docker
cd backend
docker build -t acs-backend .
docker run -p 8000:8000 acs-backend
```

## Coding Style & Naming Conventions

- Indentation: 4 spaces for Python; 2 spaces for JSON; JS/TS follows Prettier defaults used by react-scripts
- File naming:
  - Python modules: snake_case.py (e.g., production_api.py, main_launch_ready.py)
  - JavaScript/React: camelCase files under src/, component files in PascalCase if present
- Function/variable naming:
  - Python: snake_case for functions/variables, PascalCase for classes
  - JS: camelCase for variables/functions
- Linting:
  - Frontend: react-scripts built-in ESLint
  - Backend: no explicit linter config checked in; follow PEP8

## Testing Guidelines

- Frameworks:
  - Backend: pytest (tests under backend/tests/, multiple test_*.py files)
  - Frontend: react-scripts test (Jest under the hood)
- Running tests:
  - Backend: from backend, run `pytest` (if pytest installed)
  - Frontend: from frontend, run `npm test`
- Test files:
  - Python: backend/tests/test_*.py
  - Frontend: tests under frontend/tests/ and react-scripts conventions
- Coverage: not enforced in repo configs

## Commit & Pull Request Guidelines

- Commit messages: No strict conventional commits enforced; use clear imperative messages (e.g., "Fix backend uvicorn command", "Add Paddle E2E test").
- PR process: Open PRs with description of changes; include relevant build/test results.
- Branch naming: Not enforced; recommend feature/<short-desc>, fix/<short-desc>.

---

# Repository Tour

## 🎯 What This Repository Does

AdCopySurge is an AI-powered ad copy analysis and generation platform. It provides analysis scores, compliance checks, psychology insights, and generates optimized ad variants.

Key responsibilities:
- Analyze ad copy and compute multi-dimensional scores
- Generate improved and A/B/C variants
- Provide REST API for frontend and integrate with Supabase and Paddle

---

## 🏗️ Architecture Overview

### System Context
```
[React Frontend (frontend/)] → [FastAPI Backend (backend/)] → [Supabase Postgres/Storage]
                                      ↓
                               [External AI APIs]
```

### Key Components
- Backend FastAPI app (backend/main_launch_ready.py, alternate entrypoints) – exposes REST endpoints under /api
- Tools SDK orchestration (backend/packages/tools_sdk/*) – orchestrates 9 analysis/generation tools [from imports]
- Frontend React SPA (frontend/src) – consumes API, builds with react-scripts, served by Nginx in prod
- Deployment assets (backend/Dockerfile, frontend/Dockerfile, deploy/, nginx/) – containerization and reverse proxy

### Data Flow
1. User submits ad copy from React app
2. Frontend calls FastAPI endpoints (/api/ads/analyze, /api/ads/comprehensive-analyze)
3. Backend validates and runs tool orchestrations for analysis and variants
4. Optionally interacts with Supabase for persistence/metrics
5. Returns structured JSON with scores, recommendations, and variants

---

## 📁 Project Structure [Partial Directory Tree]

```
.
├── frontend/
│   ├── Dockerfile
│   ├── package.json
│   ├── src/            # React app source
│   ├── public/
│   └── tests/
├── backend/
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── main_launch_ready.py
│   ├── production_api.py
│   ├── minimal_server.py
│   ├── ENTRYPOINTS.md
│   ├── app/            # FastAPI modules, utils, routers
│   ├── api/            # (legacy/alt) API code paths
│   ├── packages/       # tools_sdk and orchestrator
│   ├── tests/          # pytest test suites
│   └── deploy/         # systemd and ops helpers
├── app/
│   ├── api/
│   ├── privacy/
│   └── security/
├── docs/
├── nginx/
├── scripts/
└── SQL and deployment scripts at root
```

### Key Files to Know

- frontend/package.json – scripts: start, dev (concurrently), build, test
- frontend/Dockerfile – multi-stage build and Nginx serve
- backend/requirements.txt – backend dependencies (FastAPI, SQLAlchemy, Supabase, OpenAI, etc.)
- backend/Dockerfile – uvicorn main:app default CMD, healthcheck
- backend/main_launch_ready.py – primary dev entrypoint; comprehensive analyze endpoints
- backend/ENTRYPOINTS.md – authoritative guidance on which entrypoints to use
- backend/production_api.py, backend/minimal_server.py – alternate guarded entrypoints
- README.md – project overview and commands

---

## 🔧 Technology Stack

### Core Technologies
- Language: Python 3.11 (backend), JavaScript/React 18 (frontend)
- Framework: FastAPI (backend), React (frontend)
- Database: Supabase Postgres; optional Redis for caching (per README and requirements)
- Web Server: Uvicorn/Gunicorn for backend; Nginx serving frontend build

### Key Libraries
- Backend: fastapi, uvicorn, sqlalchemy, alembic, supabase, openai, transformers, pydantic v2, httpx
- Frontend: react, @mui/material, react-router-dom, @tanstack/react-query, axios

### Development Tools
- react-scripts, concurrently (frontend)
- pytest (tests present), Docker, docker-compose templates

---

## 🌐 External Dependencies

- Supabase (PostgreSQL, Auth, Storage) – used by backend integration modules and production_api
- OpenAI / Hugging Face – for AI generation/analysis (per requirements.txt)
- Redis – caching/broker (optional per README and requirements)

### Environment Variables (selection)
- ENVIRONMENT – controls dev vs production behavior
- SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY, SUPABASE_JWT_SECRET – Supabase integration
- Backend may read standard keys like OPENAI_API_KEY, DATABASE_URL (see README and .env templates)

---

## 🔄 Common Workflows

- Local development with both apps:
  - In one terminal: `cd frontend && npm run dev`
  - Alternatively start backend explicitly: `cd backend && uvicorn main_launch_ready:app --reload`
- Backend only quick check: `python backend/minimal_server.py`
- Production build:
  - Frontend: `cd frontend && npm ci && npm run build`
  - Backend image: `cd backend && docker build -t acs-backend .`

---

## 📈 Performance & Scale

- Uvicorn/Gunicorn workers configurable; health checks present in Dockerfiles
- React served via Nginx for static performance

---

## 🚨 Things to Be Careful About

- Do not use deprecated backend entrypoints in production; follow backend/ENTRYPOINTS.md
- Ensure ENVIRONMENT and Supabase secrets are set in production
- CORS settings differ between dev and prod; verify allowed origins


*Updated at: 2025-10-16*
