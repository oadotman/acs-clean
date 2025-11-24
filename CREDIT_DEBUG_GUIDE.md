# Credit System Debug Guide

## The Problem

User on UNLIMITED plan gets "Not enough credits" error.

Console shows:
- ✅ `CreditsWidget: Unlimite` - Widget detects unlimited
- ❌ `hasEnoughCredits: false` - useCredits hook says NO

## Root Cause

There are TWO separate credit checkers in the frontend:
1. **CreditsWidget** - Shows ∞ symbol (works!)
2. **useCredits hook** - Used by NewAnalysis (broken!)

## Quick Fix Option 1: Add Logging

**File:** `frontend/src/pages/NewAnalysis.jsx` line 364

Change:
```javascript
console.log('💳 Credit system state:', { hasEnoughCredits, executeWithCredits, getCreditRequirement });
```

To:
```javascript
// Get the actual credits object from useCredits
const { credits } = useCredits();  // Add this import at line 149
console.log('💳 Full credits object:', JSON.stringify(credits, null, 2));
console.log('💳 credits.isUnlimited:', credits?.isUnlimited);
console.log('💳 credits.credits:', credits?.credits);
console.log('💳 credits.subscriptionTier:', credits?.subscriptionTier);
```

## Quick Fix Option 2: Check Network Response

1. **Open DevTools** (F12)
2. **Network tab**
3. **Filter: "balance"**
4. **Refresh page**
5. **Click `/api/credits/balance`**
6. **Check Response tab**

Should show:
```json
{
  "credits": 999999,
  "is_unlimited": true,  // ← THIS MUST BE TRUE
  "subscription_tier": "agency_unlimited"
}
```

If `is_unlimited` is **false** → Backend issue
If `is_unlimited` is **true** → Frontend issue

## Quick Fix Option 3: Hard-Code Test

**File:** `frontend/src/hooks/useCredits.js` line 100

Add temporary debug:
```javascript
// Check unlimited
console.log('🔍 CHECKING UNLIMITED:', {
  'credits.isUnlimited': credits?.isUnlimited,
  'credits.credits': credits?.credits,
  'check1': credits.isUnlimited,
  'check2': credits.credits === 'unlimited',
  'check3': credits.credits >= 999999
});

if (credits.isUnlimited || credits.credits === 'unlimited' || credits.credits >= 999999) {
  console.log('✅ UNLIMITED ACCESS GRANTED');
  return true;
}
```

## Most Likely Issues

### Issue A: API Returns Wrong Field Name
Backend might return `is_unlimited` but frontend expects `isUnlimited` (camelCase vs snake_case).

**Check:** `frontend/src/hooks/useCredits.js` line 54
```javascript
isUnlimited: result.data.is_unlimited,  // ← Does API return this?
```

### Issue B: Credits Object is Null
Frontend might not have fetched credits yet.

**Check:** Line 97
```javascript
if (!credits || credits.credits === null) return false;
```

### Issue C: Wrong User Loaded
Backend might return credits for wrong user (different UUID).

**Check:** Browser → Application → Local Storage → auth token

## Command to Run on Server

```bash
# Check PM2 logs for the actual API response
pm2 logs acs-backend --lines 100 | grep "get_user_credits"

# Test API directly (replace TOKEN)
curl -H "Authorization: Bearer <TOKEN>" \
  https://adcopysurge.com/api/credits/balance \
  | jq '.'
```

## Emergency Bypass (Temporary)

**File:** `frontend/src/pages/NewAnalysis.jsx` line 367

Comment out the credit check:
```javascript
// TEMPORARY: Bypass credit check for unlimited users
if (!hasEnoughCredits('FULL_ANALYSIS')) {
  // Check if this is unlimited tier
  const { user } = useAuth();  // Add import if needed
  if (user?.subscription_tier === 'agency_unlimited') {
    console.warn('⚠️ Bypassing credit check for unlimited user');
    // Continue with analysis
  } else {
    console.error('❌ Not enough credits! Analysis blocked.');
    toast.error('Not enough credits for analysis. Please check your credit balance.');
    return;
  }
}
```

## The Real Fix

The backend IS returning the correct data (we fixed that), but the frontend isn't reading it correctly.

Need to check:
1. Is the API response cached?
2. Is the field name mapping correct?
3. Is the credits state being updated?

**Action:** Have user check Network tab Response to see actual API data.
