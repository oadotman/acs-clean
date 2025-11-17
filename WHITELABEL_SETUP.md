# White-Label Workflow Setup Guide

## Overview
The white-label workflow has been fully implemented end-to-end with:
- ✅ Backend API with database persistence
- ✅ Supabase Storage integration for logo uploads
- ✅ Frontend API integration (no more localStorage-only)
- ✅ Fixed logo upload field name mismatch
- ✅ Complete CRUD operations for agency settings

## Backend Setup

### 1. Install Dependencies

The white-label functionality requires the `supabase` Python package:

```bash
cd backend
pip install supabase
```

### 2. Configure Environment Variables

Add these to your `backend/.env` file:

```env
# Supabase Configuration (already configured for auth)
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key

# These should already exist from your Supabase auth setup
REACT_APP_SUPABASE_URL=https://your-project.supabase.co
REACT_APP_SUPABASE_ANON_KEY=your-anon-key
SUPABASE_JWT_SECRET=your-jwt-secret
```

### 3. Run Database Migration

Create the `agencies` table:

```bash
cd backend
alembic upgrade head
```

This will create:
- `agencies` table with JSONB settings column
- `agencystatus` enum type
- Proper indexes for performance

### 4. Create Supabase Storage Bucket

Go to your Supabase dashboard:

1. Navigate to **Storage** → **Create Bucket**
2. Bucket name: `whitelabel-assets`
3. Make it **public** (for CDN access)
4. Optional: Configure allowed MIME types (image/png, image/jpeg, image/svg+xml, image/webp)

Alternatively, the bucket will be auto-created on first logo upload.

### 5. Start Backend Server

```bash
cd backend
uvicorn main:app --reload
```

The API will be available at: `http://localhost:8000`

**New endpoints:**
- `POST /api/whitelabel/agency` - Create agency
- `GET /api/whitelabel/settings?agency_id=xxx` - Get settings
- `PUT /api/whitelabel/settings?agency_id=xxx` - Update settings
- `POST /api/whitelabel/logo/upload` - Upload logo to Supabase Storage
- `POST /api/whitelabel/domain/verify?agency_id=xxx` - Verify domain

API docs: http://localhost:8000/api/docs

## Frontend Setup

### 1. Verify API URL

Check `frontend/.env`:

```env
REACT_APP_API_URL=http://localhost:8000
```

### 2. Start Frontend

```bash
cd frontend
npm install
npm start
```

Frontend will be available at: `http://localhost:3000`

## Testing the Workflow

### Step 1: Access White-Label Settings

Navigate to: `http://localhost:3000/agency/whitelabel`

### Step 2: Complete Setup Wizard

**Step 1 - Company Branding:**
1. Enter company name (required)
2. Enter support email (optional)
3. Upload logo:
   - Click "Upload Logo" button
   - Select an image file (PNG, JPG, SVG, WebP)
   - Max size: 5MB
   - File will upload to Supabase Storage
   - Logo URL will be saved to database
4. Click "Next"

**Step 2 - Color Scheme:**
1. Choose primary color (buttons, links)
2. Choose secondary color (accents)
3. Preview colors in the color swatch
4. Click "Next"

**Step 3 - Custom Domain (Optional):**
1. Enter custom domain (e.g., `app.yourcompany.com`)
2. Click "Verify" to generate DNS records
3. Copy DNS records to your domain provider:
   - CNAME record pointing to `adcopysurge-app.adcopysurge.com`
   - TXT record for verification
4. Note: Full DNS verification requires additional implementation (see Production Notes)
5. Click "Next"

**Step 4 - Preview & Launch:**
1. Review configuration summary
2. Check that logo is uploaded
3. Click "Launch Platform"
4. Settings are saved to database

### Step 3: Verify Data Persistence

**Check Database:**
```sql
-- In Supabase SQL Editor
SELECT * FROM agencies;

-- View settings JSONB
SELECT
  id,
  name,
  settings->>'company_name' as company_name,
  settings->>'logo_url' as logo_url,
  settings->>'primary_color' as primary_color
FROM agencies;
```

**Check Supabase Storage:**
1. Go to Supabase Dashboard → Storage → `whitelabel-assets`
2. You should see uploaded logo files organized by agency ID
3. Files are publicly accessible via CDN

**Check Frontend:**
1. Refresh the page
2. Settings should load from backend (not localStorage)
3. Logo should display from Supabase Storage URL
4. Console should show: "✅ Loaded settings from backend"

## Architecture

### Data Flow

```
User uploads logo
  ↓
SetupWizard.jsx → FileUploadService.validateFile()
  ↓
WhiteLabelContext.handleLogoUpload()
  ↓
whitelabelService.uploadLogo() → POST /api/whitelabel/logo/upload
  ↓
Backend WhitelabelService.upload_logo()
  ↓
Supabase Storage (bucket: whitelabel-assets)
  ↓
Returns public CDN URL
  ↓
Backend updates agencies.settings JSONB
  ↓
Frontend displays logo from Supabase URL
```

### Storage Structure

**Supabase Storage:**
```
whitelabel-assets/
  ├── {agency-id}/
  │   ├── logo-{uuid}.png
  │   ├── logo-{uuid}.svg
  │   └── favicon-{uuid}.ico
```

**Database:**
```json
// agencies.settings (JSONB)
{
  "white_label_enabled": true,
  "company_name": "Client Company",
  "logo_url": "https://xyz.supabase.co/storage/v1/object/public/whitelabel-assets/agency-id/logo-uuid.png",
  "primary_color": "#7C3AED",
  "secondary_color": "#A855F7",
  "custom_domain": "app.client.com",
  "domain_verified": false,
  "support_email": "support@client.com"
}
```

## What Was Fixed

### 1. Logo Upload Field Name Mismatch ✅
**Before:** Wizard used `logo`, context expected `customLogo`
**After:** Consistent `customLogo` throughout

**Files changed:**
- `frontend/src/components/whiteLabel/SetupWizard.jsx`

### 2. Missing Backend Infrastructure ✅
**Before:** No API endpoints, no database persistence
**After:** Full REST API with database

**Files created:**
- `backend/app/models/agency.py`
- `backend/app/services/whitelabel_service.py`
- `backend/app/schemas/whitelabel.py`
- `backend/app/routers/whitelabel.py`
- `backend/alembic/versions/20250117_add_agencies_table.py`

**Files updated:**
- `backend/main.py` (added whitelabel router)
- `backend/app/models/__init__.py` (export Agency model)

### 3. Logo Storage Implementation ✅
**Before:** Base64 in localStorage (not scalable)
**After:** Supabase Storage with CDN

**Files created:**
- `frontend/src/services/whitelabelService.js`

**Files updated:**
- `frontend/src/contexts/WhiteLabelContext.jsx` (backend integration)

### 4. Frontend API Integration ✅
**Before:** localStorage only
**After:** Backend APIs with localStorage fallback

**Changes:**
- `handleLogoUpload()` now calls backend API
- `saveSettings()` persists to database
- Settings load from backend on mount
- Agency auto-created if needed

## Production Considerations

### 1. Domain Verification (TODO)
Current implementation is simplified. For production:

**Install dnspython:**
```bash
pip install dnspython
```

**Implement real DNS checks:**
```python
import dns.resolver

def verify_dns_records(domain, expected_cname, expected_txt):
    # Check CNAME
    cname_records = dns.resolver.resolve(domain, 'CNAME')
    # Check TXT verification
    txt_records = dns.resolver.resolve(f'_adcopysurge-verification.{domain}', 'TXT')
    # Return verification status
```

**Add to backend:**
- `backend/app/services/dns_verification_service.py`

### 2. SSL Certificate Automation
For custom domains with SSL:

**Option A: Let's Encrypt (Recommended)**
- Use `certbot` for automatic SSL certificates
- Nginx configuration for SSL termination

**Option B: Cloudflare**
- Use Cloudflare's free SSL
- Configure DNS through Cloudflare

### 3. CDN Configuration
Supabase Storage includes CDN, but for optimal performance:

**Configure cache headers:**
```python
file_options={
    "content-type": content_type,
    "cache-control": "public, max-age=31536000",  # 1 year
    "upsert": "true"
}
```

### 4. File Size Limits
Current limit: 5MB

**Adjust Supabase bucket settings:**
- Dashboard → Storage → Bucket Settings
- Set max file size
- Configure allowed MIME types

### 5. Multi-Tenant Isolation
Ensure proper access control:

**Backend checks:**
```python
# Already implemented in WhitelabelService
if str(agency.owner_user_id) != user_id:
    # TODO: Check if user is team member
    raise Exception("Unauthorized")
```

**TODO: Add team member check:**
- Query `agency_team_members` table
- Verify user has required role (admin, editor)

### 6. Rate Limiting
Protect logo upload endpoint:

**Add to `backend/app/middleware/rate_limiting.py`:**
```python
rate_limits = {
    "/api/whitelabel/logo/upload": "10/hour"  # Limit uploads
}
```

### 7. Image Optimization
Consider adding image processing:

**Option A: Pillow (Python)**
```bash
pip install Pillow
```

**Option B: Cloudinary**
- Automatic optimization
- Multiple sizes/formats
- Transformation API

### 8. Monitoring & Logging
Add observability:

**Log important events:**
- Logo uploads
- Settings changes
- Domain verification attempts
- Failed uploads

**Metrics to track:**
- Upload success rate
- Average file size
- Storage usage per agency
- API response times

## Troubleshooting

### Logo Upload Fails

**Check:**
1. Supabase Storage bucket exists and is public
2. `SUPABASE_SERVICE_ROLE_KEY` is set correctly
3. File size < 5MB
4. File type is allowed (PNG, JPG, SVG, WebP)

**Debug:**
```bash
# Check backend logs
cd backend
uvicorn main:app --reload --log-level debug

# Check Supabase logs
# Dashboard → Logs → Storage
```

### Settings Not Persisting

**Check:**
1. Database migration ran successfully: `alembic current`
2. Agency was created: `SELECT * FROM agencies;`
3. Backend API is running: `curl http://localhost:8000/api/whitelabel/settings?agency_id=xxx`

**Debug:**
```javascript
// Frontend console
localStorage.getItem('whiteLabel-agencyId')  // Should have agency UUID
```

### CORS Errors

**Check `backend/.env`:**
```env
CORS_ORIGINS=http://localhost:3000
```

**Or in production:**
```env
CORS_ORIGINS=https://yourdomain.com,https://app.yourdomain.com
```

### Authentication Errors

**Check:**
1. User is logged in (Supabase auth)
2. Auth token is present: `localStorage.getItem('authToken')`
3. Token is valid (not expired)

**Debug:**
```bash
# Check auth middleware
# Backend logs should show: "User authenticated: {user_id}"
```

## API Reference

### Create Agency
```http
POST /api/whitelabel/agency
Content-Type: application/json
Authorization: Bearer {token}

{
  "name": "My Agency",
  "description": "Optional description"
}
```

### Get Settings
```http
GET /api/whitelabel/settings?agency_id={uuid}
Authorization: Bearer {token}
```

### Update Settings
```http
PUT /api/whitelabel/settings?agency_id={uuid}
Content-Type: application/json
Authorization: Bearer {token}

{
  "companyName": "New Name",
  "primaryColor": "#7C3AED",
  "customDomain": "app.example.com"
}
```

### Upload Logo
```http
POST /api/whitelabel/logo/upload
Content-Type: multipart/form-data
Authorization: Bearer {token}

agency_id: {uuid}
logo: {file}
```

### Verify Domain
```http
POST /api/whitelabel/domain/verify?agency_id={uuid}
Content-Type: application/json
Authorization: Bearer {token}

{
  "domain": "app.example.com",
  "verification_token": "optional-token"
}
```

## Security Checklist

- ✅ JWT authentication required for all endpoints
- ✅ User ownership verification (agency.owner_user_id)
- ✅ File type validation (only images)
- ✅ File size limits (5MB)
- ✅ Unique filenames (UUID-based)
- ⚠️ TODO: Rate limiting on upload endpoint
- ⚠️ TODO: Team member access control
- ⚠️ TODO: Malware scanning for uploaded files

## Next Steps

1. **Implement DNS Verification** (see Production Considerations #1)
2. **Add Team Member Access Control** (check if user is in agency_team_members)
3. **Rate Limiting** for logo uploads
4. **Image Optimization** (resize/compress)
5. **Email Template Customization** (use white-label settings in emails)
6. **Custom Domain Routing** (Nginx configuration)
7. **SSL Automation** (Let's Encrypt integration)

## Support

For issues or questions:
1. Check backend logs: `journalctl -u adcopysurge -f`
2. Check Supabase logs: Dashboard → Logs
3. Check browser console for frontend errors
4. Review this documentation

## Changelog

### 2025-01-17 - Complete End-to-End Implementation
- ✅ Fixed frontend field name mismatch (logo → customLogo)
- ✅ Created Agency model with JSONB settings
- ✅ Implemented WhitelabelService with Supabase Storage
- ✅ Created REST API endpoints
- ✅ Integrated frontend with backend APIs
- ✅ Created database migration
- ✅ Tested complete workflow

**Status:** ✅ PRODUCTION READY (with noted TODOs)
