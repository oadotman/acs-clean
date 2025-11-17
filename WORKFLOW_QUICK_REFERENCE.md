# Ad Analysis Workflow - Quick Reference Guide

**For**: Developers, QA, Product Managers
**Purpose**: Quick lookup of how ad analysis works

---

## 🚀 How It Works (30-Second Version)

1. User pastes ad copy → Selects platform
2. Frontend checks if user has 1 credit
3. If yes → Deducts credit → Shows progress screen
4. Backend runs 9 AI tools in parallel (60-120s)
5. AI generates 4 alternative versions
6. Everything saved to database
7. User sees results + alternatives

**Total Time**: 60-120 seconds
**Cost**: 1 credit per analysis

---

## 📁 Key Files Reference

### Frontend
```
NewAnalysis.jsx           → Main entry point (platform selection, ad input)
ComprehensiveAnalysisLoader.jsx → Progress visualization
ComprehensiveResults.jsx  → Results display
useCredits.js             → Credit management hook
apiService.js             → API client (120s timeout)
```

### Backend
```
api/ads.py                → POST /ads/analyze endpoint
services/ad_analysis_service_enhanced.py → Main orchestration
services/production_ai_generator.py → AI generation
models/ad_analysis.py     → Database ORM models
```

### Database
```
ad_analyses               → Main analysis records
ad_generations            → AI-generated alternatives
user_credits              → Credit balances
credit_transactions       → Audit trail
```

---

## 🛠️ 9 Analysis Tools

| # | Tool Name | What It Does | Output |
|---|-----------|--------------|--------|
| 1 | Core Analyzer | Overall copy effectiveness | Scores (0-100) |
| 2 | Compliance Checker | Platform policy violations | Pass/Fail + Issues |
| 3 | Psychology Scorer | 15 psychological triggers | Triggers found + Opportunities |
| 4 | A/B Test Generator | 8 test variations | Alternative headlines/CTAs |
| 5 | ROI Copy Generator | Premium-positioned versions | High-value alternatives |
| 6 | Industry Optimizer | Industry-specific language | Optimized copy |
| 7 | Performance Forensics | Performance factors | Quick wins list |
| 8 | Brand Voice Engine | Tone consistency | Voice match score |
| 9 | Legal Risk Scanner | Legally problematic claims | Risk level + Flagged phrases |

**Execution**: All 9 run in PARALLEL (not sequential)
**Time**: 30-45 seconds for all tools combined

---

## 💳 Credit System Flow

```
User has X credits
    ↓
Checks: X >= 1?
    ↓
YES → Deduct 1 credit
    ↓
    ↓ (If analysis fails)
    ⚠️  ISSUE: Credit not refunded (see audit)
    ↓
    ↓ (If analysis succeeds)
    ✅ Results shown
    ↓
Save transaction to credit_transactions table
```

**Credit Costs**:
- Full Analysis: 1 credit
- A/B Test only: 0.5 credits (not implemented)
- Competitor Benchmark: 2 credits (not implemented)

---

## 🎯 API Endpoint Contract

### POST `/api/ads/analyze`

**Request**:
```json
{
  "ad": {
    "headline": "Get 50% off today!",
    "body_text": "Limited time offer on all products...",
    "cta": "Shop Now",
    "platform": "facebook",
    "target_audience": "Small business owners",
    "brand_voice": {
      "tone": "professional",
      "personality": "confident",
      "formality": 3,
      "past_ads": ["ad1", "ad2"],
      "emoji_preference": "auto"
    }
  },
  "competitor_ads": []
}
```

**Response** (60-120s later):
```json
{
  "analysis_id": "550e8400-e29b-41d4-a716-446655440000",
  "scores": {
    "overall_score": 78.5,
    "clarity_score": 82.0,
    "persuasion_score": 75.0,
    "emotion_score": 70.0,
    "cta_strength_score": 85.0,
    "platform_fit_score": 80.0
  },
  "alternatives": [
    {
      "variant_type": "improved",
      "headline": "Unlock 50% OFF Everything – Today Only!",
      "body_text": "...",
      "cta": "Shop the Sale →",
      "improvement_reason": "Added urgency, stronger CTA",
      "predicted_score": 88.0
    },
    // ... 3 more alternatives
  ],
  "feedback": "Your ad has good clarity but could use more emotional appeal...",
  "tool_results": {
    "compliance_checker": {...},
    "psychology_scorer": {...}
    // ... 9 tools total
  }
}
```

---

## ⚠️ Known Issues (Must Know)

### Issue #1: Credit Deduction Timing
**Problem**: Credits deducted BEFORE analysis completes
**Impact**: User loses credit if analysis fails
**Workaround**: None currently
**Fix ETA**: Next sprint

### Issue #2: No Credit Refunds
**Problem**: `refundCredits()` not implemented
**Impact**: Failed analyses don't return credits
**Workaround**: Manual credit adjustment via database
**Fix ETA**: Next sprint

### Issue #3: Anonymous Users
**Problem**: Falls back to 'anonymous' user if auth fails
**Impact**: Analysis not linked to user, can't retrieve
**Workaround**: Ensure user is logged in before analyzing
**Fix ETA**: 2 weeks

### Issue #4: Hardcoded CTA
**Problem**: Defaults to "Learn More" if CTA not found
**Impact**: Minor UX issue
**Workaround**: User can manually edit in results
**Fix ETA**: Low priority

---

## 🐛 Common Errors & Solutions

### Error: "Not enough credits"
**Cause**: User has 0 credits
**Solution**: Upgrade subscription or purchase credits
**Code Location**: `useCredits.js` line 156

### Error: "CSRF protection or authentication issue"
**Cause**: JWT token expired or invalid
**Solution**: User needs to log out and back in
**Code Location**: `ComprehensiveAnalysisLoader.jsx` line 304

### Error: "Server Error: Our team has been notified"
**Cause**: 500 error from backend (AI API failure, database issue, etc.)
**Solution**: Check backend logs, retry analysis
**Code Location**: `ComprehensiveAnalysisLoader.jsx` line 306

### Error: "Analysis timed out"
**Cause**: Response took >120 seconds
**Solution**: Retry (rare, usually completes in 60-90s)
**Code Location**: `apiService.js` line 15 (timeout config)

---

## 🧪 Testing Scenarios

### Happy Path
```bash
# 1. User with credits
# 2. Valid ad copy (>10 chars)
# 3. Platform selected
# 4. API returns 200
# 5. All 9 tools succeed
# → Results displayed
```

### Unhappy Paths to Test
```bash
# No credits
→ Should show "Insufficient credits" toast

# Invalid input
→ Should show validation error

# API timeout
→ Should show timeout error (⚠️ credit already deducted)

# One tool fails
→ Should show partial results (currently may fail entire analysis)

# Database connection lost
→ Should retry, then show error

# User closes browser mid-analysis
→ Analysis continues on backend but frontend loses connection
→ ⚠️ No way to resume (see recommendations in audit)
```

---

## 📊 Performance Benchmarks

| Metric | Target | Actual | Status |
|--------|--------|--------|--------|
| Analysis time | <120s | 60-115s | ✅ Good |
| Credit deduction | <1s | <1s | ✅ Good |
| Database save | <3s | 2-3s | ✅ Good |
| Concurrent users | 50+ | ~100 | ✅ Good |
| API success rate | >95% | ~98% | ✅ Great |

**Bottlenecks**:
- AI generation (50% of time) - Acceptable, provides quality results
- Tools SDK (40% of time) - Already optimized with parallel execution

---

## 🔐 Security Checklist

When reviewing code changes:

- [ ] All API endpoints require JWT authentication
- [ ] User ID comes from `current_user`, NOT request body
- [ ] Database queries use ORM (no raw SQL)
- [ ] User input is validated (Pydantic schemas)
- [ ] RLS policies prevent cross-user data access
- [ ] Sensitive data not logged
- [ ] API keys in environment variables
- [ ] CORS restricted to allowed origins

---

## 🚨 Monitoring & Alerts

**What to Monitor**:
1. Average analysis time (should be <120s)
2. Credit deduction errors
3. API 500 error rate
4. Database connection failures
5. AI API rate limit hits

**Alert Thresholds**:
- Error rate >5% → Page on-call
- Analysis time >180s → Investigate
- Credit system failure → Immediate fix
- Database connection lost → Critical alert

---

## 🔄 Deployment Checklist

Before deploying changes to this workflow:

1. **Database**
   - [ ] Run migrations (`npm run db:migrate`)
   - [ ] Verify schema changes don't break existing data
   - [ ] Test RLS policies

2. **Backend**
   - [ ] Test API endpoint manually (Postman/curl)
   - [ ] Verify OpenAI/Gemini API keys are set
   - [ ] Check logs for errors

3. **Frontend**
   - [ ] Build succeeds (`npm run build`)
   - [ ] No TypeScript errors
   - [ ] Test credit system manually

4. **Integration**
   - [ ] Run end-to-end test (create account → analyze ad → view results)
   - [ ] Test with insufficient credits
   - [ ] Test with invalid input
   - [ ] Test analysis timeout scenario

---

## 📞 Who to Contact

| Issue Type | Contact | Location |
|------------|---------|----------|
| Credit system bugs | Backend team | `useCredits.js`, `credit_system_schema.sql` |
| AI generation issues | AI team | `production_ai_generator.py` |
| Tools SDK problems | Platform team | `backend/packages/tools_sdk/` |
| Frontend UI bugs | Frontend team | `NewAnalysis.jsx`, components |
| Database performance | DevOps team | Supabase console |

---

## 📚 Related Documentation

- **Full Audit Report**: `AD_ANALYSIS_AUDIT.md`
- **API Documentation**: `docs/api.md`
- **Database Schema**: `supabase-schema.sql`
- **Tools SDK**: `backend/packages/tools_sdk/README.md`
- **Deployment**: `DEPLOY.md`

---

**Last Updated**: 2025-11-17
**Next Review**: 2025-12-17 (monthly)
