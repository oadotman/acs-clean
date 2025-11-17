# Fix Implementation Guide - Ad Analysis Workflow

**Purpose**: Step-by-step guide to implement the 4 recommended fixes
**Estimated Time**: 5-7 hours total
**Difficulty**: Easy to Medium

---

## 🎯 Overview of Fixes

| Fix | Priority | Time | Difficulty | Impact |
|-----|----------|------|------------|--------|
| 1. Credit Refund Mechanism | High | 2h | Easy | High |
| 2. Credit Deduction Timing | High | 1h | Medium | High |
| 3. Require Authentication | Medium | 1h | Easy | Medium |
| 4. Better CTA Extraction | Low | 30min | Easy | Low |

**Total Time**: 4.5 hours for all fixes

---

## Fix #1: Implement Credit Refund Mechanism

**Time**: 2 hours
**Files**: `frontend/src/hooks/useCredits.js`, `frontend/src/utils/creditSystem.js`

### Step 1: Add Database Function (15 min)

Create Supabase function for adding credits:

```sql
-- In Supabase SQL Editor
CREATE OR REPLACE FUNCTION add_credits(
  user_id_param UUID,
  amount_param INTEGER
)
RETURNS VOID AS $$
BEGIN
  UPDATE user_credits
  SET current_credits = current_credits + amount_param
  WHERE user_id = user_id_param;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;
```

### Step 2: Implement `refundCredits()` (45 min)

**File**: `frontend/src/hooks/useCredits.js`

**Add after line 173** (where the TODO comment is):

```javascript
/**
 * Refund credits to user after failed operation
 */
const refundCredits = async (operation, quantity = 1, reason = 'Operation failed') => {
  if (!user) {
    console.error('Cannot refund credits: No user logged in');
    return false;
  }

  try {
    const cost = CREDIT_COSTS[operation] || 1;
    const amount = cost * quantity;

    // Add credits back using database function
    const { data, error } = await supabase.rpc('add_credits', {
      user_id_param: user.id,
      amount_param: amount
    });

    if (error) {
      console.error('Failed to refund credits:', error);
      throw error;
    }

    // Log refund transaction
    const { error: txError } = await supabase
      .from('credit_transactions')
      .insert({
        user_id: user.id,
        operation: `REFUND_${operation}`,
        amount: amount,  // Positive number for refunds
        description: reason,
        created_at: new Date().toISOString()
      });

    if (txError) {
      console.error('Failed to log refund transaction:', txError);
    }

    // Refresh credit balance
    await refetchCredits();

    // Show success message
    toast.success(
      `${amount} credit${amount > 1 ? 's' : ''} refunded: ${reason}`,
      { duration: 5000 }
    );

    console.log(`Refunded ${amount} credits for ${operation}: ${reason}`);
    return true;
  } catch (error) {
    console.error('Error refunding credits:', error);
    toast.error('Failed to refund credits. Please contact support.', {
      duration: 6000
    });
    return false;
  }
};
```

### Step 3: Export `refundCredits` (5 min)

**File**: `frontend/src/hooks/useCredits.js`

**Update return statement** (around line 251):

```javascript
return {
  credits: creditsData,
  isLoading,
  error: creditsError,
  refetchCredits,
  hasEnoughCredits,
  executeWithCredits,
  refundCredits,  // ADD THIS LINE
  getFeatureUsage,
  CREDIT_COSTS
};
```

### Step 4: Update `creditSystem.js` (15 min)

**File**: `frontend/src/utils/creditSystem.js`

**Add helper function**:

```javascript
/**
 * Refund credits after failed operation
 * Use this wrapper for convenience
 */
export const refundCreditsForFailedOperation = async (
  supabase,
  userId,
  operation,
  quantity = 1,
  reason = 'Operation failed'
) => {
  const cost = CREDIT_COSTS[operation] || 1;
  const amount = cost * quantity;

  try {
    // Add credits back
    const { error: refundError } = await supabase.rpc('add_credits', {
      user_id_param: userId,
      amount_param: amount
    });

    if (refundError) throw refundError;

    // Log transaction
    await supabase.from('credit_transactions').insert({
      user_id: userId,
      operation: `REFUND_${operation}`,
      amount: amount,
      description: reason,
      created_at: new Date().toISOString()
    });

    return { success: true, amount };
  } catch (error) {
    console.error('Refund failed:', error);
    return { success: false, error };
  }
};
```

### Step 5: Test (20 min)

1. Start analysis with 1 credit
2. Manually kill API server mid-analysis
3. Verify analysis fails
4. Check credit balance - should be refunded
5. Check `credit_transactions` table for refund record

---

## Fix #2: Credit Deduction Timing

**Time**: 1 hour
**Files**: `frontend/src/pages/NewAnalysis.jsx`, `frontend/src/components/ComprehensiveAnalysisLoader.jsx`

### Step 1: Remove Immediate Deduction (15 min)

**File**: `frontend/src/pages/NewAnalysis.jsx`

**BEFORE** (lines 321-334):

```javascript
const result = await executeWithCredits(
  'FULL_ANALYSIS',
  async () => {
    setStep('comprehensive-analyzing');
    return { success: true };
  },
  { showToasts: true }
);
```

**AFTER**:

```javascript
// Check credits but DON'T deduct yet
if (!hasEnoughCredits('FULL_ANALYSIS')) {
  showInsufficientCreditsToast('FULL_ANALYSIS', 1, credits?.credits || 0);
  return;
}

// Start analysis WITHOUT deducting
setStep('comprehensive-analyzing');
```

### Step 2: Deduct After Success (30 min)

**File**: `frontend/src/components/ComprehensiveAnalysisLoader.jsx`

**Find** the `handleAnalysisComplete` function (around line 262):

```javascript
const handleAnalysisComplete = (result) => {
  setCurrentStage({ name: 'Done!', status: 'completed' });
  setProgress(100);

  // ADD THIS: Deduct credits after successful completion
  const { consumeCredits } = useCredits();
  consumeCredits('FULL_ANALYSIS', 1).then(() => {
    console.log('Credits deducted after successful analysis');
  }).catch(error => {
    console.error('Failed to deduct credits after analysis:', error);
    toast.error('Analysis completed but credit deduction failed. Please contact support.');
  });

  setTimeout(() => {
    navigate(`/analysis/${result.analysis_id}`);
  }, 1000);
};
```

### Step 3: Add Rollback on Failure (15 min)

**File**: `frontend/src/components/ComprehensiveAnalysisLoader.jsx`

**In the error handler** (around line 304-310):

```javascript
} catch (error) {
  // DON'T need to refund since we never deducted
  // Just show error
  console.error('Analysis error:', error);
  let errorMessage = 'Analysis failed. Please try again.';

  if (error.response?.status === 403) {
    errorMessage = 'Access Denied: CSRF protection or authentication issue';
  } else if (error.response?.status === 500) {
    errorMessage = 'Server Error: Our team has been notified';
  }

  toast.error(errorMessage, { duration: 6000 });
  setStep('comprehensive-form');
}
```

### Step 4: Test (10 min)

1. Start analysis
2. Kill server mid-analysis
3. Verify error shown
4. Check credit balance - should be UNCHANGED
5. Complete successful analysis
6. Check credit balance - should be deducted AFTER completion

---

## Fix #3: Require Authentication

**Time**: 1 hour
**Files**: `backend/app/api/ads.py`, `backend/app/dependencies.py`

### Step 1: Create Auth Dependency (20 min)

**File**: `backend/app/dependencies.py`

**Add**:

```python
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
import os

security = HTTPBearer()

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> dict:
    """
    Validate JWT token and return user info
    """
    try:
        token = credentials.credentials
        secret = os.getenv('SUPABASE_JWT_SECRET')

        if not secret:
            raise HTTPException(
                status_code=500,
                detail="Server configuration error"
            )

        # Decode JWT
        payload = jwt.decode(
            token,
            secret,
            algorithms=['HS256'],
            audience='authenticated'
        )

        user_id = payload.get('sub')
        if not user_id:
            raise HTTPException(
                status_code=401,
                detail="Invalid token: missing user ID"
            )

        return {
            'id': user_id,
            'email': payload.get('email'),
            'role': payload.get('role')
        }

    except JWTError as e:
        raise HTTPException(
            status_code=401,
            detail=f"Invalid token: {str(e)}"
        )
```

### Step 2: Update Analyze Endpoint (20 min)

**File**: `backend/app/api/ads.py`

**BEFORE** (line 91):

```python
@router.post("/analyze")
async def analyze_ad(
    request: AdAnalysisRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    user_id = request.dict().get('user_id', 'anonymous')  # BAD
```

**AFTER**:

```python
from app.dependencies import get_current_user

@router.post("/analyze")
async def analyze_ad(
    request: AdAnalysisRequest,
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(get_current_user),  # REQUIRED
    db: Session = Depends(get_db)
):
    user_id = current_user['id']  # Always authenticated
```

### Step 3: Update All Other Endpoints (15 min)

**File**: `backend/app/api/ads.py`

**Apply same pattern to**:
- `/comprehensive-analyze` (line 166)
- `/history` (line 186)
- `/generate-alternatives` (if exists)

### Step 4: Test (5 min)

```bash
# Test without auth
curl -X POST http://localhost:8000/api/ads/analyze \
  -H "Content-Type: application/json" \
  -d '{"ad": {"headline": "test", "body_text": "test", "cta": "test"}}'
# Should return 401 Unauthorized

# Test with valid JWT
curl -X POST http://localhost:8000/api/ads/analyze \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{"ad": {"headline": "test", "body_text": "test", "cta": "test"}}'
# Should return 200 OK
```

---

## Fix #4: Better CTA Extraction

**Time**: 30 minutes
**Files**: `frontend/src/components/ComprehensiveAnalysisLoader.jsx`

### Step 1: Improve Regex Patterns (15 min)

**File**: `frontend/src/components/ComprehensiveAnalysisLoader.jsx`

**BEFORE** (line 184):

```javascript
const ctaMatches = adCopy.match(/(learn more|get started|shop now|...)/gi);
const extractedCTA = ctaMatches ? ctaMatches[ctaMatches.length - 1] : 'Learn More';
```

**AFTER**:

```javascript
/**
 * Extract CTA from ad copy using comprehensive patterns
 * Tries patterns in order of specificity
 */
const extractCTA = (adCopy) => {
  const ctaPatterns = [
    // Action-oriented (highest priority)
    /\b(shop now|buy now|order now|get it now|add to cart)\b/gi,
    /\b(download now|install now|get the app|download free)\b/gi,
    /\b(sign up now|register now|join now|subscribe now)\b/gi,
    /\b(book now|reserve now|schedule now|claim now)\b/gi,

    // Engagement (medium priority)
    /\b(get started|start now|try now|try free|start free trial)\b/gi,
    /\b(learn more|find out more|discover more|see more|read more)\b/gi,
    /\b(explore|discover|see how|watch now)\b/gi,

    // Contact (lower priority)
    /\b(contact us|call now|get in touch|reach out)\b/gi,
    /\b(request demo|get demo|schedule demo)\b/gi,

    // Generic (fallback)
    /\b(click here|tap here|swipe up|see link)\b/gi
  ];

  // Try each pattern in order
  for (const pattern of ctaPatterns) {
    const matches = adCopy.match(pattern);
    if (matches && matches.length > 0) {
      // Return last match (usually the actual CTA)
      return matches[matches.length - 1];
    }
  }

  // If still no match, look for URLs
  const urlMatch = adCopy.match(/https?:\/\/[^\s]+/gi);
  if (urlMatch) {
    return 'Learn More';  // Generic CTA for link-based ads
  }

  // Ultimate fallback
  return 'Learn More';
};

const extractedCTA = extractCTA(adCopy);
```

### Step 2: Add User Confirmation (Optional, 10 min)

If you want users to confirm the extracted CTA:

```javascript
// Show confirmation dialog
const [showCTADialog, setShowCTADialog] = useState(false);
const [confirmedCTA, setConfirmedCTA] = useState(null);

// In runRealAnalysis():
const extractedCTA = extractCTA(adCopy);

// Ask user to confirm
setShowCTADialog(true);
setExtractedCTA(extractedCTA);

// Wait for confirmation...
```

### Step 3: Test (5 min)

Test with various ad copies:

```javascript
// Test cases
const testCases = [
  { ad: "Great product! Shop Now for 50% off", expected: "Shop Now" },
  { ad: "Learn about our service. Sign Up for free trial", expected: "Sign Up" },
  { ad: "Amazing deal! Click the link to save", expected: "Learn More" },
  { ad: "No CTA here just text", expected: "Learn More" }
];

testCases.forEach(test => {
  const result = extractCTA(test.ad);
  console.log(`Expected: ${test.expected}, Got: ${result}`);
});
```

---

## 🧪 Complete Testing Checklist

After implementing all fixes:

### Unit Tests
- [ ] `refundCredits()` adds credits to balance
- [ ] `refundCredits()` logs transaction
- [ ] Credit deduction happens after success
- [ ] No deduction on failure
- [ ] Auth required returns 401
- [ ] CTA extraction finds common patterns

### Integration Tests
- [ ] Full analysis flow (login → analyze → results)
- [ ] Failed analysis doesn't deduct credits
- [ ] Successful analysis deducts 1 credit
- [ ] Unauthenticated request blocked
- [ ] CTA extracted correctly

### Manual Tests
- [ ] Create account with 1 credit
- [ ] Run successful analysis
- [ ] Credit balance is 0
- [ ] Run failed analysis (kill server)
- [ ] Credit balance unchanged
- [ ] Log out and try to analyze (should fail)

---

## 📋 Deployment Checklist

Before deploying:

- [ ] All 4 fixes implemented and tested
- [ ] Database migration run (add_credits function)
- [ ] Environment variables verified
- [ ] Backend tests pass
- [ ] Frontend builds successfully
- [ ] Staging environment tested
- [ ] Rollback plan documented

---

## 🚨 Rollback Plan

If something goes wrong:

### Rollback Database
```sql
DROP FUNCTION IF EXISTS add_credits(UUID, INTEGER);
```

### Rollback Code
```bash
git revert <commit-hash>
git push
```

### Emergency Fix
If credits are stuck:

```sql
-- Manually adjust credits
UPDATE user_credits
SET current_credits = current_credits + 1
WHERE user_id = 'USER_ID_HERE';

-- Log manual adjustment
INSERT INTO credit_transactions (user_id, operation, amount, description)
VALUES ('USER_ID_HERE', 'MANUAL_REFUND', 1, 'Emergency refund due to issue');
```

---

## ✅ Done!

After completing all fixes:

1. Update `AD_ANALYSIS_AUDIT.md` status
2. Mark issues as resolved in issue tracker
3. Deploy to production
4. Monitor for 24-48 hours
5. Celebrate! 🎉

---

**Questions?** Refer to:
- Detailed analysis: `AD_ANALYSIS_AUDIT.md`
- Quick reference: `WORKFLOW_QUICK_REFERENCE.md`
- Summary: `AUDIT_SUMMARY.md`
