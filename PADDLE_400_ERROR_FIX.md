# 🚨 Paddle 400 Error - Root Cause Analysis & Fix

## Problem
Users clicking "Upgrade" button received:
- ❌ **400 Bad Request** from Paddle API
- ❌ **"Something went wrong"** error message
- ❌ **No payment overlay appearing**

## Root Causes Found

### 1. ❌ Wrong API Structure (CRITICAL)
**File:** `frontend/src/services/paddleService.js` line 141

**What was wrong:**
```javascript
// OLD CODE - WRONG for Paddle Billing v2
this.paddleInstance.Checkout.open({
  product: options.productId,  // ❌ Wrong property name
  email: options.email,        // ❌ Wrong structure
  passthrough: JSON.stringify({...})  // ❌ Old API format
});
```

**Why it failed:**
- Used **Paddle Classic API format** (`product`, `passthrough`)
- Paddle Billing v2 requires **completely different structure**
- `product` doesn't exist in v2 → causes 400 error

**Fixed to:**
```javascript
// NEW CODE - Correct for Paddle Billing v2
this.paddleInstance.Checkout.open({
  items: [{              // ✅ v2 uses 'items' array
    priceId: options.priceId,
    quantity: 1
  }],
  customer: {            // ✅ v2 uses 'customer' object
    email: options.email
  },
  customData: {          // ✅ v2 uses 'customData' not 'passthrough'
    user_id: options.userId,
    plan: options.planName
  },
  settings: {            // ✅ v2 uses 'settings' for display options
    displayMode: 'overlay'
  }
});
```

### 2. ❌ Wrong Product Mapping Access
**File:** `frontend/src/components/CreditsWidget.js` line 110

**What was wrong:**
```javascript
const productMapping = paddleService.getPaddleProductMapping();
const targetPlan = 'pro';

// This returns: {monthly: {...}, yearly: {...}}
await paddleService.openCheckout({
  productId: productMapping[targetPlan].productId,  // ❌ .productId doesn't exist!
});
```

**Why it failed:**
- `productMapping[targetPlan]` returns nested object: `{monthly: {priceId: '...'}, yearly: {priceId: '...'}}`
- Code tried to access `.productId` directly → **undefined**
- Paddle received `undefined` as priceId → **400 error**

**Fixed to:**
```javascript
const targetPlan = credits?.tier === 'free' ? 'growth' : 'agency_unlimited';
const billingPeriod = 'monthly';

// Correctly access nested structure
const priceId = productMapping[targetPlan]?.[billingPeriod]?.priceId;

await paddleService.openCheckout({
  priceId: priceId,  // ✅ Now correctly passes actual price ID
});
```

## API Comparison: Classic vs Billing v2

| Feature | Paddle Classic (Old) | Paddle Billing v2 (New) |
|---------|---------------------|------------------------|
| **Product** | `product: '12345'` | `items: [{priceId: 'pri_xxx', quantity: 1}]` |
| **Customer** | `email: 'user@example.com'` | `customer: {email: 'user@example.com'}` |
| **Metadata** | `passthrough: JSON.stringify({...})` | `customData: {...}` |
| **Display** | `method: 'overlay'` | `settings: {displayMode: 'overlay'}` |

## Files Changed

1. ✅ `frontend/src/services/paddleService.js`
   - Updated `openCheckout()` to use Paddle Billing v2 API structure
   - Changed `product` → `items` with `priceId`
   - Changed `passthrough` → `customData`
   - Added `settings` for display options

2. ✅ `frontend/src/components/CreditsWidget.js`
   - Fixed product mapping access to handle nested structure
   - Added validation for priceId existence
   - Improved error messages
   - Set default plan (growth for free users)

## Testing Checklist

After deploying these fixes, verify:

1. ✅ Click "Upgrade" button
2. ✅ Check browser console shows: "🛒 Opening Paddle checkout with options"
3. ✅ No 400 errors in Network tab
4. ✅ Paddle checkout overlay opens successfully
5. ✅ Can see payment form with correct plan details

## Deployment

```bash
# On VPS
git pull origin main
cd frontend
npm run build
sudo cp -r build/* /var/www/adcopysurge/
sudo systemctl reload nginx
```

Then hard refresh browser (Ctrl+Shift+R).

## Related Documentation

- [Paddle Billing API - Checkout](https://developer.paddle.com/paddlejs/methods/paddle-checkout-open)
- [Migration from Classic to Billing](https://developer.paddle.com/migrate/classic-to-billing)

## Commit History

- `3c7b531` - Fix Paddle Billing v2 API structure and plan mapping
- `71920dc` - Fix CSP and nginx configs
- `41d66c4` - Fix queryTimeout bug
