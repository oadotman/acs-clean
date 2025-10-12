# Backend entrypoints: production vs development

This repository previously had multiple FastAPI entrypoints. To eliminate confusion, use these:

- Production (VPS, Nginx, systemd)
  - Command: uvicorn main_production:app --host 0.0.0.0 --port 8000 --workers 2
  - File: backend/main_production.py (canonical production app)
  - Features: strict security headers, CORS/TrustedHost for prod, health/metrics endpoints, blog router mounted at /api/blog.
  - The systemd unit (backend/deploy/adcopysurge.service) points here.

- Development (local dev with auto-reload)
  - Command: uvicorn main:app --reload
  - File: backend/main.py (dev/staging app)
  - Features: friendly CORS for localhost, conditional blog router, dev docs enabled.

Dev-only file (do NOT use in production)
- backend/main_launch_ready.py
  - Purpose: integrated dev runner used during feature assembly.
  - Guarded to exit if ENVIRONMENT=production.

Deprecated/alternate scripts (kept for reference; guarded in prod)
- backend/production_api.py
- backend/working_api.py
- backend/minimal_server.py
- backend/minimal_test_server.py
All above will exit with a clear message if ENVIRONMENT=production. Use main_production:app instead.

Environment variables (minimum for production)
- ENVIRONMENT=production
- SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY, SUPABASE_JWT_SECRET
- ALLOWED_HOSTS or CORS_ORIGINS (if serving cross-origin)
- BLOG_CONTENT_DIR (optional; defaults to content/blog)

Blog system
- Backend serves markdown posts from BLOG_CONTENT_DIR (/opt/adcopysurge/backend/content/blog in prod).
- Frontend uses relative /api/blog in production via Nginx.

Notes
- For Windows local dev, you can still run: python -m uvicorn main:app --reload
- For VPS, use the provided systemd unit and nginx config in backend/deploy.
