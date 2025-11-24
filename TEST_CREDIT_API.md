# Test Credit API Response

The user shows `hasEnoughCredits: false` but we need to see what the API is returning.

## Quick Test

Have the user open Browser DevTools:

1. **Open DevTools** (F12)
2. **Go to Network tab**
3. **Filter by "balance"**
4. **Refresh the page**
5. **Click on the `/api/credits/balance` request**
6. **Look at the Response**

### What to check:

```json
{
  "credits": 999999,  // ← Should be this
  "is_unlimited": true,  // ← MUST be true
  "subscription_tier": "agency_unlimited"  // ← Should be this
}
```

## The Problem

If `is_unlimited` is **false** or **missing**, that's the bug!

## Why It Might Still Fail

1. **Backend not restarted** - PM2 might not have restarted properly
2. **Cached response** - Frontend might be showing cached data
3. **Wrong user** - User might be logged in as different account

## Commands to Run on Server

```bash
# 1. Check PM2 status
pm2 status

# 2. Check actual running process
pm2 logs acs-backend --lines 50

# 3. Force restart
pm2 restart acs-backend --update-env

# 4. Verify code is deployed
cd /var/www/acs-clean/backend
git log -1 --oneline
grep -n "supabase_user_id" app/api/credits.py | head -2

# 5. Test the API directly
curl -H "Authorization: Bearer <USER_TOKEN>" \
  https://adcopysurge.com/api/credits/balance
```

## Frontend Debug

Add this to `NewAnalysis.jsx` line 364:

```javascript
console.log('💳 Credit system state:', credits);  // ← Should show full object
console.log('💳 credits.isUnlimited:', credits?.isUnlimited);  // ← Should be true
console.log('💳 credits.credits:', credits?.credits);  // ← Should be 999999
```

Then check the browser console when clicking Analyze.
