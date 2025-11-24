# Fix Summary: Unlimited Credit Bug

## Root Cause Found ✅

**The Problem:**
The backend is passing the wrong user ID to the credit service!

### Database Structure:
```
users table:
  - id: INTEGER (auto-increment, e.g., 1, 2, 3...)
  - supabase_user_id: VARCHAR (UUID, e.g., '92f3f140-ddb5-4e21-a6d7-814982b55ebc')
  - email, subscription_tier, etc.

user_credits table:
  - user_id: UUID (links to users.supabase_user_id)
  - current_credits: 999999 ✅
  - subscription_tier: 'agency_unlimited' ✅
  - NO is_unlimited column (determined by code)
```

### The Bug:
**File:** `backend/app/api/credits.py` (line 61) and `backend/app/api/ads.py` (line 137)

```python
# WRONG - uses integer ID
credit_service.get_user_credits(str(current_user.id))  # e.g., "123"

# Should be - uses UUID
credit_service.get_user_credits(current_user.supabase_user_id)  # e.g., "92f3f140..."
```

The credit service queries `user_credits` table with the integer ID string, but the table expects the Supabase UUID!

## The Fix

Change these files:

### 1. `backend/app/api/credits.py` (line 61)
```python
# BEFORE
credits_info = credit_service.get_user_credits(str(current_user.id))

# AFTER
credits_info = credit_service.get_user_credits(current_user.supabase_user_id)
```

### 2. `backend/app/api/ads.py` (line 137-138)
```python
# BEFORE
success, credit_result = credit_service.consume_credits_atomic(
    user_id=str(current_user.id),

# AFTER
success, credit_result = credit_service.consume_credits_atomic(
    user_id=current_user.supabase_user_id,
```

### 3. Search for ALL occurrences of `str(current_user.id)` in credit-related code

Run this to find all instances:
```bash
cd backend
grep -r "str(current_user.id)" app/
```

Replace ALL with `current_user.supabase_user_id` where credit service is called.

## Why This Fixes It

1. User logs in → Auth sets `current_user` with integer `id` and UUID `supabase_user_id`
2. Backend currently passes integer ID to credit service
3. Credit service queries `user_credits` WHERE `user_id = integer_as_string`
4. No match found (table expects UUID)
5. Returns empty result → initializes new user with FREE tier!
6. User shown as having no credits despite being unlimited

After fix:
1. Backend passes UUID to credit service
2. Credit service queries `user_credits` WHERE `user_id = UUID`
3. Finds record with `subscription_tier = 'agency_unlimited'` ✅
4. Returns `is_unlimited = True` ✅
5. User can analyze! ✅

## NO SQL Changes Needed!

The database is correct:
- User record exists with correct tier
- Credit record exists with 999999 credits
- The code just queries with the wrong ID

This is a pure code fix, no database migration needed!
