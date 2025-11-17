# Team Invitation System Fix - Deployment Guide

## Problem Summary
The team invitation system was failing with a 502 Bad Gateway error because it was trying to send emails via Resend API, but the Resend API key was not configured in production, causing the backend to crash.

## Solution Implemented
Converted the team invitation system to use **6-character codes** that don't require email delivery. This makes the system more reliable and works immediately without any external dependencies.

## Changes Made

### 1. Backend Fix (`backend/app/routers/team.py`)
- **Removed**: Email sending dependency via Resend
- **Added**: 6-character code generation (e.g., `A3B7K9`)
- **Behavior**: Returns invitation code immediately for manual sharing
- **Fallback**: Gracefully handles both code and token fields for compatibility

### Key Features:
- Generates human-friendly 6-character codes (uppercase letters + digits)
- Avoids confusing characters (O/0, I/1)
- 7-day expiration
- No email required - works immediately
- Backwards compatible with existing database

### 2. New Endpoints

#### Create Invitation
```bash
POST /api/team/invite
{
  "email": "newmember@example.com",
  "agency_id": "agency-123",
  "inviter_user_id": "user-456",
  "role": "viewer"
}

Response:
{
  "success": true,
  "message": "Invitation created for newmember@example.com. Share this code: A3B7K9",
  "invitation_id": "inv-789",
  "invitation_code": "A3B7K9"
}
```

#### Accept Invitation (New)
```bash
POST /api/team/invite/accept-code
{
  "code": "A3B7K9",
  "user_id": "accepting-user-id"
}
```

## Deployment Steps

### 1. Apply Database Migration (Optional but Recommended)

If your database doesn't have the `invitation_code` column, run this SQL:

```sql
-- Run this in your Supabase SQL editor
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1
        FROM information_schema.columns
        WHERE table_name='agency_invitations'
        AND column_name='invitation_code'
    ) THEN
        ALTER TABLE agency_invitations
        ADD COLUMN invitation_code VARCHAR(10);

        CREATE INDEX idx_agency_invitations_code
        ON agency_invitations(invitation_code)
        WHERE status = 'pending';
    END IF;
END $$;
```

**Note**: The system will work even without this column by storing the code in the existing `invitation_token` field.

### 2. Deploy Backend

```bash
# On your VPS
cd /opt/adcopysurge/backend

# Backup current version
cp app/routers/team.py app/routers/team_backup_$(date +%Y%m%d).py

# Pull latest changes
git pull

# Restart the service
sudo systemctl restart adcopysurge
```

### 3. Update Frontend (Required)

The frontend needs to be updated to:
1. Display the invitation code to the user after creating an invitation
2. Provide a UI for entering invitation codes
3. Call the new `/api/team/invite/accept-code` endpoint

#### Example Frontend Changes:

**When creating invitation:**
```javascript
// In TeamManagement.jsx or similar
const response = await teamService.sendInvitation(invitationData);
if (response.success) {
  // Show the code prominently
  setInvitationCode(response.invitation_code);
  showModal({
    title: "Invitation Created",
    message: `Share this code with ${email}: ${response.invitation_code}`,
    info: "They can enter this code on the 'Join Team' page"
  });
}
```

**For accepting invitations:**
```javascript
// New component or page for code entry
const acceptInvitation = async (code) => {
  const response = await fetch('/api/team/invite/accept-code', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      code: code.toUpperCase(),
      user_id: currentUser.id
    })
  });
  // Handle response
};
```

## Testing

### Quick Test (After Deployment)
```bash
# Test the endpoint directly
curl -X POST https://adcopysurge.com/api/team/invite \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "email": "test@example.com",
    "agency_id": "your-agency-id",
    "inviter_user_id": "your-user-id",
    "role": "viewer"
  }'
```

You should receive a response with an invitation code instead of a 502 error.

## Benefits of This Approach

1. **No External Dependencies**: No need for Resend API key or SMTP configuration
2. **Immediate Availability**: Works instantly without waiting for email delivery
3. **User Flexibility**: Users can share codes via their preferred method (Slack, WhatsApp, etc.)
4. **Better Reliability**: No issues with spam filters or email delivery failures
5. **Simpler Debugging**: Fewer moving parts means easier troubleshooting

## Rollback Plan (If Needed)

If you need to rollback:
```bash
# On VPS
cd /opt/adcopysurge/backend
cp app/routers/team_backup_[DATE].py app/routers/team.py
sudo systemctl restart adcopysurge
```

## Files Changed

1. `backend/app/routers/team.py` - Main fix implementation
2. `backend/app/routers/team_original_backup.py` - Backup of original
3. `backend/add_invitation_code_column.sql` - Optional database migration
4. `backend/test_team_invitation_fixed.py` - Test script

## Next Steps

1. **Immediate**: Deploy the backend fix to resolve the 502 error
2. **Soon**: Update frontend to display and accept invitation codes
3. **Optional**: Add the invitation_code column to database for cleaner storage
4. **Future**: Consider adding QR codes for easier code sharing

## Support

If you encounter any issues:
1. Check backend logs: `journalctl -u adcopysurge -f`
2. Verify the endpoint works: Test with curl as shown above
3. Ensure database connectivity is working
4. Check that the user has permission to invite (role-based access)