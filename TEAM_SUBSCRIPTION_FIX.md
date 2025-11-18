# Team Member Subscription Tier Inheritance - Fix Documentation

## Problem

Team members who joined an agency were still showing as "FREE" tier instead of inheriting the agency's subscription tier. This prevented them from accessing agency-tier features.

## Root Cause

The system was only checking the user's personal `subscription_tier` field without considering their team membership. When a user joined an agency:
1. They were added to `agency_team_members` table ✅
2. But their personal subscription tier stayed as "FREE" ❌
3. Frontend displayed this FREE tier ❌
4. Backend enforced FREE tier limits ❌

## Solution

Created a comprehensive system to determine **effective subscription tier**:

### Backend Changes

#### 1. New Service: `user_tier_service.py`
**Location:** `backend/app/services/user_tier_service.py`

**Function:** `get_user_effective_subscription(user_id: str)`

**Logic:**
```python
1. Check if user is member of an agency team
   - Query: agency_team_members → agencies
   - If YES and agency is ACTIVE:
     → Return agency's subscription_tier
   - If NO:
     → Return user's personal subscription_tier
```

**Returns:**
- `subscription_tier`: Effective tier (agency tier if team member, personal tier otherwise)
- `is_team_member`: Boolean
- `agency_id`, `agency_name`, `role`: Agency info if team member
- `personal_tier`: User's original personal tier

#### 2. New API Endpoint: `user_profile.py`
**Location:** `backend/app/api/user_profile.py`

**Endpoints:**
- `GET /api/user/profile` - Full profile with effective tier
- `GET /api/user/effective-tier` - Quick tier check

**Authentication:** Uses `get_current_user_id` dependency

#### 3. Updated Auth Dependencies
**Location:** `backend/app/auth/dependencies.py`

**New Function:** `get_current_user_id()`
- Extracts Supabase user ID from JWT token
- No database lookup required
- Fast authentication for tier checks

#### 4. Updated Main Apps
**Files:**
- `backend/main.py` (development)
- `backend/main_production.py` (production)

**Changes:**
- Added import: `from app.api import user_profile`
- Registered router: `app.include_router(user_profile.router, prefix="/api", tags=["user"])`

#### 5. Updated Requirements
**File:** `backend/requirements.txt`

**Added:** `supabase>=2.3.0,<3.0.0  # Supabase Python client`

### Frontend Changes

#### Updated `authContext.js`
**Location:** `frontend/src/services/authContext.js`

**Function:** `fetchUserProfile()`

**Changes:**
1. **Primary Method:** Call backend API `/api/user/profile`
   - Gets effective subscription tier (considers team membership)
   - Returns agency info if team member

2. **Fallback Method:** Query Supabase directly if backend fails
   - Graceful degradation
   - Prevents login disruption

3. **Subscription State:** Now includes:
   ```javascript
   {
     subscription_tier: "agency_standard",  // Effective tier
     tier: "agency_standard",               // Alias for compatibility
     is_team_member: true,
     agency_id: "uuid...",
     agency_name: "Agency Name",
     role: "editor",
     personal_tier: "free"                  // Original personal tier
   }
   ```

## How It Works Now

### User Journey: Joining a Team

1. **Team owner generates invitation code** → `/api/team/invite`
2. **Team member enters code** → `/api/team/invite/accept-code`
   - User added to `agency_team_members` table
   - No change to user's personal subscription_tier (stays "free")
3. **Team member logs in or refreshes**
   - Frontend calls `/api/user/profile`
   - Backend checks `agency_team_members` table
   - Finds agency membership
   - Returns agency's subscription_tier (e.g., "agency_standard")
4. **Frontend updates subscription state**
   - `subscription_tier`: "agency_standard" ✅
   - `is_team_member`: true ✅
   - `agency_name`: "My Agency" ✅
5. **UI reflects agency tier**
   - Top-right profile shows "Agency Standard" ✅
   - Team management page accessible ✅
   - Agency features unlocked ✅

### Flow Diagram

```
User Login
    ↓
Frontend: fetchUserProfile(userId)
    ↓
Backend: GET /api/user/profile
    ↓
get_user_effective_subscription(userId)
    ↓
Check: Is user in agency_team_members? → YES
    ↓
Query: Get agency.subscription_tier
    ↓
Return: {
  subscription_tier: "agency_standard",
  is_team_member: true,
  agency_id: "...",
  agency_name: "...",
  role: "editor"
}
    ↓
Frontend: Update subscription state
    ↓
UI: Display agency tier ✅
```

## Testing Instructions

### Prerequisites
1. Install new dependencies:
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

2. Restart backend server:
   ```bash
   uvicorn main:app --reload
   ```

### Test Scenario 1: Team Member Inherits Tier

1. **Setup:**
   - Have an agency with "agency_standard" tier
   - Have a user account with "free" tier

2. **Actions:**
   - Generate invitation code as agency owner
   - Accept invitation code as free tier user
   - Log out and log back in

3. **Expected Results:**
   - ✅ Profile shows "Agency Standard" (not "Free")
   - ✅ Top-right displays "Agency Standard"
   - ✅ Can access Team Management page
   - ✅ Can access agency-tier features

4. **Verify in Console:**
   ```javascript
   // Check browser console logs:
   "✅ User profile fetched with effective tier:"
   {
     subscription_tier: "agency_standard",
     is_team_member: true,
     agency_name: "Your Agency Name"
   }
   ```

### Test Scenario 2: Non-Team Member Shows Personal Tier

1. **Setup:**
   - User with "growth" personal subscription
   - User is NOT part of any team

2. **Actions:**
   - Log in as this user

3. **Expected Results:**
   - ✅ Profile shows "Growth" tier
   - ✅ is_team_member: false
   - ✅ Agency fields are null

### Test Scenario 3: Fallback to Supabase

1. **Setup:**
   - Backend API temporarily unavailable

2. **Actions:**
   - Log in as user

3. **Expected Results:**
   - ⚠️ Warning in console about backend API failure
   - ✅ Falls back to direct Supabase query
   - ✅ User can still log in (graceful degradation)
   - ⚠️ May not show inherited tier (shows personal tier)

## Debugging

### Backend Logs

**Check if endpoint is working:**
```bash
# In backend directory
uvicorn main:app --reload

# Watch for:
"📋 Fetching profile for user: <uuid>"
"User <uuid> is team member of agency <uuid> - inheriting tier: agency_standard"
```

**Test endpoint directly:**
```bash
# Get auth token from browser (Supabase session)
# Then test:
curl -H "Authorization: Bearer <token>" \
     http://localhost:8000/api/user/profile
```

### Frontend Logs

**Check browser console for:**
```
📋 Fetching user profile for: <uuid>
✅ User profile fetched with effective tier: {
  subscription_tier: "agency_standard",
  is_team_member: true,
  agency_name: "...",
  role: "editor"
}
```

### Database Queries (Run in Supabase SQL Editor)

**Check team membership:**
```sql
SELECT
    atm.user_id,
    atm.role,
    a.name as agency_name,
    a.subscription_tier as agency_tier,
    a.status as agency_status
FROM agency_team_members atm
JOIN agencies a ON a.id = atm.agency_id
WHERE atm.user_id = '<user-uuid>';
```

**Expected result:**
- If user is team member: Shows agency info with subscription_tier
- If not: No rows returned

## Configuration

### Environment Variables

**Backend (.env):**
```env
REACT_APP_SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key
```

**Frontend (.env):**
```env
REACT_APP_API_URL=http://localhost:8000
```

## Rollback Instructions

If issues occur, you can rollback:

1. **Remove new routes from main files:**
   - Comment out `app.include_router(user_profile.router, ...)` in main.py and main_production.py

2. **Revert authContext.js:**
   - Git: `git checkout frontend/src/services/authContext.js`
   - Restores direct Supabase query

3. **System will work as before:**
   - Team members will show personal tier
   - But team invitation still works

## Future Improvements

1. **Cache tier lookups** - Redis cache for performance
2. **Real-time updates** - Supabase real-time when tier changes
3. **Admin override** - Allow manual tier assignment
4. **Analytics** - Track tier inheritance usage
5. **Audit log** - Log when users inherit tiers

## Files Changed

### Backend
- ✅ `backend/app/services/user_tier_service.py` (NEW)
- ✅ `backend/app/api/user_profile.py` (NEW)
- ✅ `backend/app/auth/dependencies.py` (MODIFIED - added get_current_user_id)
- ✅ `backend/main.py` (MODIFIED - registered router)
- ✅ `backend/main_production.py` (MODIFIED - registered router)
- ✅ `backend/requirements.txt` (MODIFIED - added supabase)

### Frontend
- ✅ `frontend/src/services/authContext.js` (MODIFIED - fetchUserProfile function)

### Documentation
- ✅ `TEAM_SUBSCRIPTION_FIX.md` (NEW - this file)

## Deployment Checklist

- [ ] Backend dependencies installed (`pip install -r requirements.txt`)
- [ ] Backend restarted
- [ ] Frontend rebuilt (if deploying)
- [ ] Test with real team member account
- [ ] Verify console logs show effective tier
- [ ] Check that team management pages are accessible
- [ ] Monitor for any errors in production logs

## Support

If issues persist:
1. Check backend logs: `journalctl -u adcopysurge -f` (production)
2. Check browser console for frontend errors
3. Verify Supabase connection and service role key
4. Test SQL queries directly in Supabase
5. Check that `agency_team_members` table has correct data

---

**Date Created:** 2025-01-18
**Issue:** Team members showing FREE tier instead of agency tier
**Status:** ✅ FIXED
**Tested:** ⏳ Pending user testing
