# Team Invitation System - Resend Integration

## Overview

The team invitation system has been refactored to use **Resend** for sending invitation emails. The old code-based invitation system has been replaced with a secure token-based system that automatically sends professional email invitations.

## What Changed

### Before (Old System)
- Generated short 6-character codes
- **No emails were sent** - codes had to be shared manually
- 30-day expiration for codes
- Used `generate_invitation_code()` function

### After (New System)
- Generates secure URL-safe tokens (32 bytes)
- **Automatically sends emails via Resend**
- 7-day expiration for email links
- Professional email templates with branding
- Graceful degradation if email fails

## Configuration

### 1. Set up Resend API Key

Add the following to your `backend/.env` file:

```env
# Resend Email Service
RESEND_API_KEY=re_your_actual_resend_api_key_here
RESEND_FROM_EMAIL=noreply@yourdomain.com
RESEND_FROM_NAME=Your Company Name
```

### 2. Verify Domain in Resend

1. Log in to [Resend Dashboard](https://resend.com/domains)
2. Add and verify your sending domain
3. Update DNS records as instructed
4. Wait for verification (usually instant)

### 3. Update Environment Variables

Make sure you have:
- `RESEND_API_KEY` - Your Resend API key (required)
- `RESEND_FROM_EMAIL` - Verified sending email address
- `RESEND_FROM_NAME` - Display name for emails

## Email Templates

The system uses Jinja2 templates located in `backend/app/templates/emails/`:

- **team_invitation.html** - Professional HTML email with branding
- **team_invitation.txt** - Plain text fallback

Templates support:
- Custom branding (colors, logos, company name)
- Personal messages from inviter
- Role-specific content
- Responsive design

## API Endpoints

### Send Team Invitation

```http
POST /api/team/invite
Content-Type: application/json

{
  "email": "user@example.com",
  "agency_id": "agency-uuid",
  "inviter_user_id": "user-uuid",
  "role": "editor",
  "project_access": [],
  "client_access": [],
  "personal_message": "Welcome to our team!"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Invitation sent to user@example.com",
  "invitation_id": "invitation-uuid",
  "invitation_code": null
}
```

### Resend Invitation

```http
POST /api/team/invite/resend
Content-Type: application/json

{
  "invitation_id": "invitation-uuid",
  "inviter_user_id": "user-uuid"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Invitation resent to user@example.com",
  "invitation_id": "invitation-uuid",
  "invitation_code": null
}
```

## How It Works

### Invitation Flow

1. **Create Invitation**
   - User submits invitation via `/api/team/invite`
   - System validates email and agency membership
   - Generates secure token: `secrets.token_urlsafe(32)`
   - Creates database record with 7-day expiration

2. **Fetch Agency & Inviter Details**
   - Queries Supabase for agency name
   - Retrieves inviter's full name/email
   - Prepares personalized email content

3. **Send Email via Resend**
   - Renders HTML and text templates
   - Calls Resend API at `https://api.resend.com/emails`
   - Includes invitation link: `https://app.adcopysurge.com/invite/{token}`
   - Returns message ID on success

4. **Handle Response**
   - Success: Returns invitation ID and success message
   - Failure: Logs error but still creates invitation (allows manual sharing)

### Token Security

- **Generation**: Uses `secrets.token_urlsafe(32)` for cryptographically secure tokens
- **Length**: 32 bytes → ~43 URL-safe characters
- **Uniqueness**: Extremely low collision probability
- **Expiration**: 7 days (configurable)
- **One-time use**: Token invalidated after acceptance

## Testing

### Run the Test Script

```bash
cd backend
python test_team_invitation_resend.py
```

The test script will:
1. ✅ Verify EmailService initialization
2. ✅ Test template rendering
3. ✅ Send a test invitation email (optional)

### Manual Testing

1. **Start the backend:**
   ```bash
   cd backend
   uvicorn main:app --reload
   ```

2. **Send test invitation via API:**
   ```bash
   curl -X POST http://localhost:8000/api/team/invite \
     -H "Content-Type: application/json" \
     -d '{
       "email": "test@example.com",
       "agency_id": "your-agency-id",
       "inviter_user_id": "your-user-id",
       "role": "viewer",
       "personal_message": "Test invitation"
     }'
   ```

3. **Check logs** for email send confirmation
4. **Check email inbox** for invitation

## Mock Mode (Development)

If `RESEND_API_KEY` is not set, the system runs in **mock mode**:

- Emails are logged to console instead of being sent
- Full invitation flow still works
- Database records are created normally
- Useful for local development without Resend account

Example log output:
```
MOCK EMAIL SEND:
To: user@example.com
Subject: You're invited to join Test Agency
From: noreply@adcopysurge.com
```

## Troubleshooting

### Email Not Sending

**Check 1: API Key**
```bash
# Verify RESEND_API_KEY is set
cd backend
python -c "from app.core.config import settings; print(f'API Key: {settings.RESEND_API_KEY[:10]}...')"
```

**Check 2: Domain Verification**
- Log in to Resend Dashboard
- Navigate to Domains
- Ensure your sending domain is verified (green checkmark)

**Check 3: From Email**
- Must match verified domain
- Format: `anything@yourdomain.com`
- Cannot use free email providers (gmail, yahoo, etc.)

### Template Errors

**Missing Templates:**
```bash
# Ensure templates exist
ls backend/app/templates/emails/
# Should show: team_invitation.html, team_invitation.txt
```

**Template Rendering Fails:**
- Check template syntax (Jinja2)
- Verify all variables are provided
- Check logs for specific error

### Database Errors

**Invitation Not Created:**
- Verify Supabase connection
- Check `agency_invitations` table exists
- Ensure user has correct permissions

**User Already Exists:**
- Check if email already in agency
- Remove existing pending invitations
- Verify user_profiles table

## Resend API Limits

- **Free tier:** 100 emails/day, 3,000 emails/month
- **Paid tier:** Starts at $20/month for 50,000 emails
- **Rate limit:** 10 requests/second

See [Resend Pricing](https://resend.com/pricing) for details.

## Migration Notes

### Removed Code

The following have been **removed**:
- `generate_invitation_code()` function
- Short code generation logic
- 30-day expiration for codes

### Updated Code

- `send_team_invitation()` - Now sends emails via Resend
- `resend_team_invitation()` - Regenerates token and resends email
- `EmailService._send_email()` - Uses official Resend API (`https://api.resend.com/emails`)

### Database Changes

**No schema changes required** - the system still uses:
- `agency_invitations.invitation_token` (now stores secure tokens instead of codes)
- `agency_invitations.expires_at` (now 7 days instead of 30)

## White-Label Support

The email system supports custom branding:

```python
white_label_settings = {
    'company_name': 'Your Agency',
    'primary_color': '#FF5722',
    'secondary_color': '#FFC107',
    'logo_url': 'https://yourdomain.com/logo.png',
    'from_email': 'invitations@yourdomain.com',
    'support_email': 'support@yourdomain.com',
    'website_url': 'https://yourdomain.com',
    'custom_domain': 'https://app.yourdomain.com'
}

await email_service.send_team_invitation(
    email=email,
    agency_name=agency_name,
    invitation_token=token,
    invited_by=inviter,
    role_name=role,
    white_label_settings=white_label_settings
)
```

## Next Steps

1. ✅ Set up Resend account and verify domain
2. ✅ Add `RESEND_API_KEY` to `.env`
3. ✅ Run test script to verify integration
4. ✅ Test sending real invitations
5. ✅ Monitor Resend dashboard for delivery stats
6. 🔄 (Optional) Customize email templates for your brand
7. 🔄 (Optional) Set up white-label branding

## Support

For issues or questions:
- Check backend logs: `tail -f backend/logs/app.log`
- Review Resend dashboard for delivery status
- Contact Resend support for API issues
