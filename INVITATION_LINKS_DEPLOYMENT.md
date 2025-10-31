# Team Invitation Links - Deployment Guide (ACS-CLEAN)

## ✅ Implementation Complete!

All core components for the shareable invitation link system have been implemented in the **acs-clean** codebase.

---

## 📦 Files Created/Modified

### ✅ Created Files:
1. `database/migrations/005_invitation_link_system.sql` - Supabase migration
2. `frontend/src/pages/InviteAccept.jsx` - Invitation acceptance page
3. `INVITATION_LINKS_DEPLOYMENT.md` - This file
4. `INVITATION_LINKS_QUICKSTART.md` - Quick reference guide

### ✅ Modified Files:
1. `frontend/src/services/teamService.js` - Added new methods:
   - `generateInviteLink()` - Generate shareable invitation links
   - `revokeInvitation()` - Cancel pending invitations
   - `getInvitationDetails()` - Fetch invitation by token
   - `acceptInvitation()` - Accept invitation via link
   - `getAgencyInvitations()` - List all invitations for agency

2. `frontend/src/App.js` - Added route:
   - `/invite/accept/:token` - Public route for invitation acceptance

---

## 🚀 Deployment Steps

### ✅ Step 1: Database Migration (DONE)
You've already run the Supabase migration! The following functions are now available:
- `generate_team_invitation_link()` - Creates secure invitation links
- `get_invitation_details()` - Fetches invitation info by token
- `accept_team_invitation_link()` - Processes invitation acceptance
- `revoke_team_invitation()` - Cancels invitations
- `get_agency_invitations()` - Lists all invitations for an agency
- `expire_old_invitations()` - Maintenance function for cron jobs

### Step 2: Deploy Frontend Changes
```bash
cd C:\Users\User\Desktop\Eledami\adsurge\acs-clean\frontend

# Install dependencies if needed
npm install

# Build for production
npm run build

# Deploy to your hosting (Vercel/Netlify/VPS)
# Follow your normal deployment process
```

### Step 3: Test the Flow
See testing checklist below

---

## 🎯 How It Works Now

### Before (Email-based):
1. Admin clicks "Send Invite"
2. System sends email via SMTP
3. User clicks email link
4. User accepts invitation

### After (Link-based):
1. Admin clicks "Generate Invite Link"  
2. System generates secure token and URL
3. Admin **copies link** and shares via Slack/WhatsApp/etc
4. User clicks link → sees invitation details
5. User accepts → automatically added to team

---

## 💡 Usage Examples

### Generating an Invitation (Frontend)
```javascript
import teamService from './services/teamService';

// Generate invitation link
const invitation = await teamService.generateInviteLink(
  agencyId,
  currentUserId,
  {
    email: 'newmember@example.com',
    role: 'editor',
    message: 'Welcome to the team!' // optional
  }
);

// Copy to clipboard
navigator.clipboard.writeText(invitation.full_url);

// Result:
// https://yoursite.com/invite/accept/abc123def456...
```

### Accepting an Invitation
Users simply click the link and see:
- Agency name
- Role being assigned
- Who invited them
- Expiration date
- Accept/Decline buttons

### Revoking an Invitation
```javascript
await teamService.revokeInvitation(invitationId, adminUserId);
```

---

## 🔒 Security Features

✅ **Cryptographically Secure Tokens**  
- 64-character hex tokens generated from 32 random bytes
- Virtually impossible to guess or brute force

✅ **Single-Use Tokens**  
- Each invitation can only be accepted once
- Marked as "accepted" after use

✅ **Time-Limited Expiration**  
- 7-day expiration (configurable in database function)
- Expired invitations cannot be accepted

✅ **Email Validation**  
- Invitation email must match accepting user's email
- Prevents token sharing/misuse

✅ **Admin-Only Generation**  
- Only agency admins can generate invitations
- Checked at database level via RLS

✅ **Revocation Support**  
- Admins can cancel invitations before acceptance
- Revoked invitations cannot be used

---

## 📋 Testing Checklist

### Basic Flow
- [x] Database migration ran successfully
- [ ] Generate invitation link as admin
- [ ] Copy invitation link to clipboard
- [ ] Open link in incognito/private window
- [ ] Verify invitation details display correctly
- [ ] Sign in with invited email
- [ ] Accept invitation
- [ ] Verify redirect to team dashboard
- [ ] Verify user appears in team members list

### Security Tests
- [ ] Try using same invitation link twice (should fail)
- [ ] Generate new invitation and revoke it
- [ ] Try accepting revoked invitation (should fail)
- [ ] Try accepting with wrong email address (should fail)
- [ ] Wait for invitation to expire OR manually expire in DB
- [ ] Try accepting expired invitation (should fail)

### Edge Cases
- [ ] Try accessing `/invite/accept/invalidtoken` (should show error)
- [ ] Generate invitation while one already exists for same email (should fail gracefully)
- [ ] Verify non-admin users cannot generate invitations

---

## 🔧 Next Steps (Optional Enhancements)

### 1. Update Team Management UI
The `TeamManagement.jsx` page can be enhanced to show:
- List of all invitations with status badges
- Copy link button for each pending invitation
- Revoke button for pending invitations
- Expiration countdown timers

**Example Enhancement:**
```javascript
// In TeamManagement.jsx
const [invitations, setInvitations] = useState([]);

useEffect(() => {
  if (agency) {
    loadInvitations();
  }
}, [agency]);

const loadInvitations = async () => {
  const invites = await teamService.getAgencyInvitations(agency.id, user.id);
  setInvitations(invites);
};

const handleCopyLink = (url) => {
  navigator.clipboard.writeText(url);
  toast.success('Link copied to clipboard!');
};
```

### 2. Backend API (Optional)
The backend `/team/invite` endpoint can be updated to call the Supabase function instead of sending emails. This is optional since the frontend now calls Supabase directly.

### 3. Rate Limiting (Optional)
Add rate limiting to prevent invitation spam:
- Limit invitations per agency per hour
- Track failed token validation attempts
- Implement cooldown periods

### 4. Analytics (Optional)
Track invitation metrics:
- Invitations generated vs accepted
- Average time to acceptance
- Most common invitation sources

---

## 🐛 Troubleshooting

### Issue: "Failed to generate invitation link"
**Solution:** Check that:
- User is an admin of the agency
- Email doesn't already have a pending invitation
- User with that email isn't already a team member

### Issue: "Invalid invitation link"
**Solution:** Check that:
- Token hasn't been used already
- Invitation hasn't expired
- Invitation hasn't been revoked

### Issue: "This invitation was sent to a different email address"
**Solution:** User must sign in with the exact email the invitation was sent to

### Issue: Database function not found
**Solution:** Re-run the migration SQL in Supabase SQL Editor

---

## 📊 Monitoring

### Check Invitation Status
```sql
-- View all invitations
SELECT 
  email,
  role_id,
  status,
  expires_at,
  created_at
FROM team_invitations
WHERE agency_id = 'YOUR_AGENCY_ID'
ORDER BY created_at DESC;
```

### Manually Expire Old Invitations
```sql
-- Run this periodically or set up as cron job
SELECT expire_old_invitations();
```

### Check Team Members
```sql
SELECT 
  up.email,
  atm.role,
  atm.status,
  atm.created_at
FROM agency_team_members atm
JOIN user_profiles up ON atm.user_id = up.id
WHERE atm.agency_id = 'YOUR_AGENCY_ID';
```

---

## 🎉 Benefits

### For Admins:
- ⚡ **Instant** - No waiting for email delivery
- 🔗 **Flexible** - Share via any channel (Slack, WhatsApp, SMS, etc.)
- 🎯 **Control** - Revoke invitations at any time
- 📊 **Visibility** - See all invitations and their status

### For Users:
- ✨ **Clear** - Beautiful UI showing exactly what they're accepting
- 🔒 **Secure** - Verifiable invitation details before acceptance
- 📱 **Mobile-Friendly** - Works perfectly on all devices

### For System:
- 💰 **Cost-Effective** - No email service costs or configuration
- ⚡ **Fast** - No email delays or spam filter issues
- 🛠️ **Simple** - No SMTP configuration needed
- 🔧 **Maintainable** - Fewer moving parts and dependencies

---

## 📚 API Reference

### teamService.generateInviteLink()
```javascript
/**
 * @param {string} agencyId - Agency ID
 * @param {string} inviterUserId - User ID generating invitation
 * @param {Object} invitationData - { email, role, message? }
 * @returns {Promise<Object>} { invitation_id, invitation_token, invitation_url, full_url, expires_at }
 */
```

### teamService.getInvitationDetails()
```javascript
/**
 * @param {string} token - Invitation token
 * @returns {Promise<Object>} Invitation details with validation status
 */
```

### teamService.acceptInvitation()
```javascript
/**
 * @param {string} token - Invitation token
 * @param {string} userId - User ID accepting
 * @returns {Promise<Object>} { success, message, agency_id, team_member_id }
 */
```

### teamService.revokeInvitation()
```javascript
/**
 * @param {string} invitationId - Invitation ID
 * @param {string} revokerUserId - User ID revoking
 * @returns {Promise<boolean>} Success status
 */
```

### teamService.getAgencyInvitations()
```javascript
/**
 * @param {string} agencyId - Agency ID
 * @param {string} userId - User ID (for permission check)
 * @returns {Promise<Array>} List of invitations with full URLs
 */
```

---

## ✅ Deployment Checklist

- [x] Database migration created
- [x] Database migration run in Supabase
- [x] teamService.js updated with new methods
- [x] InviteAccept.jsx page created
- [x] App.js route added
- [ ] Frontend deployed to production
- [ ] End-to-end testing completed
- [ ] Team notified of new invitation flow
- [ ] Documentation shared with admins

---

**Status:** ✅ Core Implementation Complete  
**Ready for:** Production Deployment & Testing

**Questions?** Check the codebase or test the flow end-to-end!
