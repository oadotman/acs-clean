# Credit System Architecture Documentation

## Overview
AdCopySurge implements a robust, atomic credit system with automatic refunds, comprehensive audit trails, and race condition prevention. This document details the complete architecture as of 2025-11-21.

## Architecture Highlights

### 1. Atomic Operations
- All credit operations use database-level constraints to ensure atomicity
- SQL `WHERE` clauses prevent race conditions: `WHERE current_credits >= :credit_cost`
- Multiple concurrent requests are handled safely without duplicate charges

### 2. Automatic Refunds
- Credits ARE automatically refunded when analysis fails
- Implemented in `backend/app/api/ads.py` lines 217-228
- Refund logic is atomic and logged to audit trail

### 3. Transaction Logging
- Every credit operation is logged to `credit_transactions` table
- Includes: user_id, operation, amount, description, timestamp
- Enables full audit trail and reconciliation

## Credit Flow Diagram

```
1. User initiates analysis (Frontend)
   └─> NewAnalysis.jsx calls executeWithCredits()

2. Frontend pre-flight check (UX only)
   └─> useCredits.js checks hasEnoughCredits()
   └─> This is non-atomic but provides immediate UI feedback

3. API call to backend
   └─> POST /api/ads/analyze

4. Backend atomic credit consumption
   └─> credit_service.consume_credits_atomic()
   └─> Database UPDATE with WHERE constraint
   └─> Returns success/failure immediately

5a. If credits insufficient
    └─> Return 403 error
    └─> No credits deducted

5b. If credits sufficient
    └─> Credits deducted atomically
    └─> Analysis proceeds

6. Analysis execution
   └─> ad_service.analyze_ad()

7a. If analysis succeeds
    └─> Return results
    └─> Credits remain deducted

7b. If analysis fails
    └─> Automatic refund triggered
    └─> credit_service.refund_credits()
    └─> Credits returned to user
    └─> Error returned to frontend

8. Frontend updates
   └─> Polls every 30 seconds for balance updates
   └─> Updates UI with new balance
```

## Credit Costs

| Operation | Credits | Description |
|-----------|---------|-------------|
| FULL_ANALYSIS | 2 | Complete ad analysis with all tools |
| BASIC_ANALYSIS | 1 | Basic analysis without advanced features |
| PSYCHOLOGY_ANALYSIS | 3 | Deep psychological analysis |
| FURTHER_IMPROVE | 2 | Iterative improvement on existing analysis |
| BATCH_ANALYSIS_PER_AD | 1 | Per-ad cost in batch operations |
| ADVANCED_EXPORT | 1 | Export with advanced formatting |
| DETAILED_REPORT | 3 | Comprehensive PDF report |
| WHITE_LABEL_REPORT | 5 | White-labeled report for agencies |
| BRAND_VOICE_TRAINING | 5 | Train brand voice model |
| LEGAL_RISK_SCAN | 3 | Legal compliance analysis |

## Subscription Tiers

| Tier | Monthly Credits | Rollover Limit | Special Features |
|------|-----------------|----------------|------------------|
| FREE | 5 | 0 | Basic features only |
| GROWTH | 100 | 50 | Standard features |
| AGENCY_STANDARD | 500 | 250 | Agency features |
| AGENCY_PREMIUM | 1000 | 500 | Premium features |
| AGENCY_UNLIMITED | Unlimited | N/A | All features, no limits |

## Database Schema

### user_credits Table
```sql
CREATE TABLE user_credits (
    id UUID PRIMARY KEY,
    user_id UUID REFERENCES auth.users(id),
    current_credits INTEGER NOT NULL DEFAULT 0,
    monthly_allowance INTEGER NOT NULL DEFAULT 0,
    bonus_credits INTEGER NOT NULL DEFAULT 0,
    total_used INTEGER NOT NULL DEFAULT 0,
    subscription_tier TEXT NOT NULL DEFAULT 'free',
    last_reset TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);
```

### credit_transactions Table
```sql
CREATE TABLE credit_transactions (
    id UUID PRIMARY KEY,
    user_id UUID REFERENCES auth.users(id),
    operation TEXT NOT NULL,
    amount INTEGER NOT NULL,
    description TEXT,
    analysis_id UUID REFERENCES ad_analyses(id),
    created_at TIMESTAMPTZ DEFAULT NOW()
);
```

## Key Files

### Backend
- `backend/app/services/credit_service.py` - Core credit logic
- `backend/app/api/ads.py` - Analysis endpoint with credit handling
- `backend/app/api/credits.py` - Credit management endpoints
- `backend/tests/test_credit_service_security.py` - Comprehensive tests

### Frontend
- `frontend/src/hooks/useCredits.js` - React hook for credit management
- `frontend/src/services/creditService.js` - API client for credits
- `frontend/src/pages/NewAnalysis.jsx` - Main analysis interface

### Database
- `backend/alembic/versions/*credit*.py` - Migration files
- Row-level security policies in Supabase

## Security Features

### 1. Atomic Database Operations
```python
result = self.db.execute(
    text("""
        UPDATE user_credits
        SET current_credits = current_credits - :credit_cost
        WHERE user_id = :user_id
          AND current_credits >= :credit_cost  # Atomic constraint
        RETURNING current_credits
    """),
    {"user_id": user_id, "credit_cost": credit_cost}
).fetchone()

if not result:
    return False, {"error": "Insufficient credits"}
```

### 2. Race Condition Prevention
- Database-level constraints ensure only one concurrent request succeeds
- Test coverage confirms 10 concurrent requests handled correctly
- No possibility of negative credit balance

### 3. Audit Trail
- Every operation logged with timestamp
- Includes refunds, allocations, and consumption
- Enables reconciliation and dispute resolution

## Testing

### Automated Tests
Located in `backend/tests/test_credit_service_security.py`:

1. **test_atomic_credit_deduction_prevents_race_condition**
   - Simulates 10 concurrent requests
   - Verifies only appropriate number succeed

2. **test_credit_refund_on_failure**
   - Consumes credits then refunds
   - Verifies balance restored correctly

3. **test_unlimited_tier_bypass**
   - Tests unlimited tier doesn't consume credits
   - Verifies operations still logged

4. **test_insufficient_credits_rejection**
   - Attempts to consume more than available
   - Verifies operation rejected

5. **test_credit_transaction_logging**
   - Verifies all operations create audit records

### Manual Testing Checklist
- [ ] Single user consuming credits
- [ ] Multiple tabs consuming simultaneously
- [ ] Network failure during analysis
- [ ] Server error during analysis
- [ ] Subscription tier changes
- [ ] Monthly reset logic
- [ ] Rollover calculations

## Monitoring & Maintenance

### Key Metrics to Monitor
1. Average credits consumed per user per day
2. Refund rate (should be < 5%)
3. Failed transactions in audit log
4. Credit balance discrepancies
5. Response time for credit operations

### Regular Maintenance Tasks
1. **Daily**: Check for negative credit balances (should be impossible)
2. **Weekly**: Review refund patterns for abuse
3. **Monthly**: Reconcile credit_transactions with user_credits
4. **Quarterly**: Analyze credit consumption patterns

## Common Issues & Solutions

### Issue: User reports missing credits
**Solution**: Check credit_transactions table for user_id, verify all operations

### Issue: Analysis succeeded but credits not deducted
**Solution**: Check if user is on unlimited tier or if webhook allocated bonus credits

### Issue: Credits deducted but analysis never ran
**Solution**: Check logs for analysis_id, verify refund was processed

### Issue: Concurrent requests from same user
**Solution**: Atomic operations handle this automatically, check audit trail

## Future Enhancements

1. **Real-time Updates**: Currently polls every 30s, could use WebSocket
2. **Credit Packages**: Allow purchasing credit bundles
3. **Team Credits**: Shared credit pool for organizations
4. **Credit Expiry**: Implement expiration for bonus credits
5. **Credit Transfer**: Allow transferring credits between team members
6. **Usage Analytics**: Detailed dashboard showing credit consumption patterns

## Contact & Support

For credit system issues:
1. Check audit trail in credit_transactions table
2. Review user_credits for current balance
3. Check application logs for error details
4. Contact backend team for database queries

---

*Last Updated: 2025-11-21*
*Version: 1.0.0*
*Status: Production Ready*