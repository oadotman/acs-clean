# ✅ Paddle Payment Flow - Complete Fix

## Summary of All Issues & Solutions

### 🎯 Issue #1: Users Couldn't Choose Their Plan
**Problem:** Upgrade button went directly to Paddle checkout without showing pricing options  
**Solution:** Changed Upgrade button to navigate to `/pricing` page where users can see all plans

**Changed:**
- `CreditsWidget.js` line 97: Now simply navigates to `/pricing`

---

### 🎯 Issue #2: Paddle 400 Bad Request Error  
**Problem:** Invalid `allowLogout` setting in checkout options  
**Solution:** Removed the invalid setting from Paddle configuration

**Changed:**
- `paddleService.js` line 177: Removed `allowLogout: false`

---

### 🎯 Issue #3: Wrong Property Names
**Problem:** Using `productId` instead of `priceId`, wrong customData field names  
**Solution:** Updated to correct Paddle Billing v2 API structure

**Changed:**
- `Pricing.js` line 116: Changed `productId` → `priceId`
- `paddleService.js` lines 169-170: Changed to `user_id` and `plan_name`

---

### 🎯 Issue #4: Email Undefined/Missing
**Problem:** Email was `undefined` or not validated before checkout  
**Solution:** Added email validation in multiple places

**Changed:**
- `Pricing.js` lines 101-106: Validate email before opening checkout
- `paddleService.js` lines 132-145: Validate email format with regex
- `paddleService.js` line 166: Changed from `email || undefined` to just `email`

---

### 🎯 Issue #5: 406 Error from Supabase
**Problem:** Using `.single()` on user_profiles query  
**Solution:** Changed to `.maybeSingle()` to handle no-results case

**Changed:**
- `authContext.js` line 303: Changed `.single()` → `.maybeSingle()`

---

## Complete Paddle Checkout Flow (Billing v2)

```javascript
// ✅ CORRECT Paddle Billing v2 structure
Paddle.Checkout.open({
  items: [{
    priceId: 'pri_01k8gd5r03mg7p8gasg95pn105',  // ✅ Price ID, not product ID
    quantity: 1
  }],
  customer: {
    email: 'user@example.com'  // ✅ Must be valid email, not undefined
  },
  customData: {
    user_id: 'user-123',       // ✅ Use snake_case for custom data
    plan_name: 'growth',
    source: 'web_app'
  },
  settings: {
    displayMode: 'overlay',
    theme: 'light',
    locale: 'en'
    // ❌ NO allowLogout - causes 400 error
  }
});
```

---

## User Flow Now

1. **User clicks "Upgrade"** → Navigates to `/pricing`
2. **User sees all plans** → Can compare features and prices
3. **User selects a plan** → Pricing page validates email
4. **Paddle checkout opens** → With correct API structure
5. **User completes payment** → Redirected to success page

---

## Files Changed

| File | Lines | Change |
|------|-------|--------|
| `CreditsWidget.js` | 97-101 | Simplified to navigate to /pricing |
| `paddleService.js` | 132-145 | Added email validation |
| `paddleService.js` | 165-177 | Fixed checkout structure, removed allowLogout |
| `Pricing.js` | 101-118 | Added email validation, use priceId |
| `authContext.js` | 303 | Changed .single() to .maybeSingle() |

---

## Environment Variables Required

Make sure these are set on VPS:

```bash
REACT_APP_PADDLE_CLIENT_TOKEN=your_client_token_here
REACT_APP_PADDLE_ENVIRONMENT=production  # or 'sandbox' for testing
REACT_APP_SUPABASE_URL=your_supabase_url
REACT_APP_SUPABASE_ANON_KEY=your_supabase_key
```

---

## Deployment

```bash
# On VPS
git pull origin main
cd frontend
npm run build
sudo cp -r build/* /var/www/adcopysurge/
sudo systemctl reload nginx
```

**Then hard refresh browser: Ctrl+Shift+R**

---

## Testing Checklist

After deployment:

1. ✅ Click "Upgrade" button → Should go to `/pricing` page
2. ✅ See all pricing plans with features
3. ✅ Select a plan → Should validate user is logged in
4. ✅ Console shows: `📝 Opening checkout for: {plan, priceId, email}`
5. ✅ Paddle overlay opens successfully
6. ✅ No 400 errors in Network tab
7. ✅ No 406 errors from Supabase
8. ✅ Email is populated in checkout form

---

## Common Issues & Solutions

### "Email is required for checkout"
**Cause:** User not logged in or email not in session  
**Fix:** User must log in first before accessing pricing

### "Invalid email format"
**Cause:** Email validation regex failed  
**Fix:** Ensure user.email is valid format (has @ and domain)

### 400 Bad Request
**Cause:** Wrong Paddle API structure  
**Fix:** Ensure using `items: [{priceId, quantity}]` format

### 406 Not Acceptable
**Cause:** Supabase query using `.single()` with no results  
**Fix:** Already fixed with `.maybeSingle()`

---

## Paddle Dashboard Configuration

Make sure in your Paddle dashboard:

1. ✅ Products are created with correct Price IDs
2. ✅ Client-side token is generated and copied to env vars
3. ✅ Webhook URL is configured (for subscription updates)
4. ✅ Success/cancel URLs match your domain
5. ✅ Price IDs match those in `getPaddleProductMapping()`

---

## Commits

- `b4347f3` - Fix Paddle 400 error and redirect to Pricing page
- `b64ccc4` - Fix 406 error and email validation
- `7bb5dc9` - Add root cause analysis docs
- `3c7b531` - Fix Paddle Billing v2 API structure

---

## Support

If issues persist after deployment:
1. Check browser console for errors
2. Check Network tab for 400/406 responses
3. Verify environment variables are set
4. Check Paddle dashboard for price ID validity
5. Verify user is logged in with valid email
