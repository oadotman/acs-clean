# Nginx Proxy Pass Trailing Slash Issue

## The Problem

Your Nginx config has:
```nginx
location /api/ {
    proxy_pass http://127.0.0.1:8000;
}
```

### What's Wrong?

When a request comes for `/api/credits/balance`:

**Current (broken):**
- Request: `GET /api/credits/balance`
- Nginx forwards to: `http://127.0.0.1:8000/api/credits/balance` ✅
- BUT if proxy_pass doesn't have `/api/`, it might not work correctly

**The issue:** Without the trailing path in `proxy_pass`, the URI might not be correctly forwarded.

## The Fix

Change to:
```nginx
location /api/ {
    proxy_pass http://127.0.0.1:8000/api/;
                                    ^^^^^ Add this!
}
```

OR (alternative - strips /api prefix):
```nginx
location /api/ {
    proxy_pass http://127.0.0.1:8000/;
                                    ^ Just trailing slash
}
```

### Difference:

**Option 1** (recommended for FastAPI with `/api` prefix in routes):
```nginx
location /api/ {
    proxy_pass http://127.0.0.1:8000/api/;
}
```
- Request: `GET /api/credits/balance`
- Forwards to: `http://127.0.0.1:8000/api/credits/balance`

**Option 2** (if FastAPI routes DON'T have `/api` prefix):
```nginx
location /api/ {
    proxy_pass http://127.0.0.1:8000/;
}
```
- Request: `GET /api/credits/balance`
- Forwards to: `http://127.0.0.1:8000/credits/balance` (strips `/api`)

## Quick Fix On VPS

```bash
# 1. Edit Nginx config
sudo nano /etc/nginx/sites-available/adcopysurge.com

# 2. Find this line:
#    proxy_pass http://127.0.0.1:8000;

# 3. Change to:
#    proxy_pass http://127.0.0.1:8000/api/;

# 4. Save and test
sudo nginx -t

# 5. If OK, reload
sudo systemctl reload nginx

# 6. Test
curl https://adcopysurge.com/api/credits/balance
```

## How to Know Which Option?

Check your FastAPI routes in `main_production.py`:

If routes are like:
```python
app.include_router(credits.router, prefix="/api/credits")
```

Then use Option 1 (with `/api/` in proxy_pass).

If routes are like:
```python
app.include_router(credits.router, prefix="/credits")
```

Then use Option 2 (with just `/` in proxy_pass).

## Additional Fix: Remove Duplicate Location Block

Your diagnostic shows TWO location blocks:
```nginx
location /api {     # Block 1 (no trailing slash)
location /api/ {    # Block 2 (with trailing slash)
```

**You should only have ONE!** Remove the one without the trailing slash.
