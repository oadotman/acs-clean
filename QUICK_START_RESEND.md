# Quick Start: Team Invitations with Resend

## 5-Minute Setup

### Step 1: Get Resend API Key

1. Go to [resend.com](https://resend.com)
2. Sign up or log in
3. Navigate to **API Keys**
4. Click **Create API Key**
5. Copy the key (starts with `re_`)

### Step 2: Configure Environment

Add to `backend/.env`:

```env
RESEND_API_KEY=re_xxxxxxxxxxxxxxxxxxxxx
RESEND_FROM_EMAIL=noreply@yourdomain.com
```

### Step 3: Verify Domain (Important!)

1. Go to [Resend Dashboard → Domains](https://resend.com/domains)
2. Click **Add Domain**
3. Enter your domain (e.g., `yourdomain.com`)
4. Add the provided DNS records to your domain:
   - **TXT record** for verification
   - **MX records** (optional, for receiving)
   - **DKIM records** for authentication
5. Click **Verify** (usually instant)

**Important:** `RESEND_FROM_EMAIL` must match your verified domain!

### Step 4: Test the Integration

```bash
cd backend

# Quick test (standalone)
export RESEND_API_KEY=re_your_key_here
python quick_test_resend.py

# Full test (with app)
python test_team_invitation_resend.py
```

### Step 5: Send Your First Invitation

**Via API:**
```bash
curl -X POST http://localhost:8000/api/team/invite \
  -H "Content-Type: application/json" \
  -d '{
    "email": "colleague@example.com",
    "agency_id": "your-agency-uuid",
    "inviter_user_id": "your-user-uuid",
    "role": "editor",
    "personal_message": "Welcome to the team!"
  }'
```

**Expected Response:**
```json
{
  "success": true,
  "message": "Invitation sent to colleague@example.com",
  "invitation_id": "uuid-here",
  "invitation_code": null
}
```

That's it! Your colleague will receive a professional invitation email.

## What Happens Next?

1. **Email is sent** via Resend to the recipient
2. **Email contains:**
   - Professional branded template
   - Agency name and inviter details
   - Role assignment
   - Personal message (if provided)
   - Secure invitation link
3. **Recipient clicks link** → Directed to signup/login
4. **After signup** → Automatically added to agency

## Troubleshooting

### Email not received?

**Check 1:** Spam folder
**Check 2:** Domain verified in Resend?
**Check 3:** FROM_EMAIL matches verified domain?
**Check 4:** Resend dashboard for delivery status

### Still having issues?

```bash
# Check configuration
cd backend
python -c "from app.core.config import settings; print(f'API Key: {settings.RESEND_API_KEY[:10]}...')"

# Check logs
tail -f backend/logs/app.log

# Run test script
python quick_test_resend.py
```

## API Reference

### Send Invitation

```http
POST /api/team/invite
```

**Request:**
```json
{
  "email": "user@example.com",
  "agency_id": "uuid",
  "inviter_user_id": "uuid",
  "role": "admin|editor|viewer|client",
  "project_access": [],  // optional
  "client_access": [],   // optional
  "personal_message": "string"  // optional
}
```

**Response:**
```json
{
  "success": true,
  "message": "Invitation sent to user@example.com",
  "invitation_id": "uuid",
  "invitation_code": null
}
```

### Resend Invitation

```http
POST /api/team/invite/resend
```

**Request:**
```json
{
  "invitation_id": "uuid",
  "inviter_user_id": "uuid"
}
```

## Development Mode (No API Key)

If `RESEND_API_KEY` is not set:
- System runs in **mock mode**
- Emails logged to console (not sent)
- Full invitation flow works
- Perfect for local development

## Production Checklist

- [ ] Resend account created
- [ ] Domain added and verified
- [ ] `RESEND_API_KEY` set in environment
- [ ] `RESEND_FROM_EMAIL` matches verified domain
- [ ] Test invitation sent successfully
- [ ] Email received and link works
- [ ] Logs show successful delivery

## Next Steps

For more details:
- **Full setup guide:** See `RESEND_SETUP.md`
- **All changes:** See `REFACTOR_SUMMARY.md`
- **Troubleshooting:** See `RESEND_SETUP.md` → Troubleshooting section

## Support

- Resend docs: [resend.com/docs](https://resend.com/docs)
- Resend dashboard: [resend.com/emails](https://resend.com/emails)
- Backend logs: `tail -f backend/logs/app.log`
