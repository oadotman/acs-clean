# 🔍 Sentry Error Tracking Setup Guide

## Why Sentry is Critical for Production

Without Sentry, you're flying blind:
- ❌ No visibility into production errors
- ❌ Can't track payment failures
- ❌ Can't detect authentication issues
- ❌ Can't monitor performance bottlenecks
- ❌ Users experience issues but you never know

With Sentry:
- ✅ Real-time error notifications
- ✅ Full error context (user, browser, API calls)
- ✅ Performance monitoring
- ✅ Release tracking
- ✅ Alert when things break

**Investment in advertising without Sentry = Wasted money on broken experiences**

---

## Step 1: Create Sentry Account (15 minutes)

### 1.1 Sign Up

1. Go to https://sentry.io/signup/
2. Choose **Free Plan** (includes 5,000 errors/month - plenty for starting out)
3. Sign up with GitHub/Google or email

### 1.2 Create Two Projects

You need separate projects for backend and frontend:

**Project 1: Backend (Python)**
- Platform: **Python/FastAPI**
- Name: `adcopysurge-backend`
- Team: Your organization name

**Project 2: Frontend (React)**
- Platform: **JavaScript/React**
- Name: `adcopysurge-frontend`
- Team: Same as backend

### 1.3 Get DSN Keys

After creating each project, you'll get a DSN (Data Source Name):

**Backend DSN:**
```
https://[random-hash]@o[org-id].ingest.sentry.io/[project-id]
```

**Frontend DSN:**
```
https://[random-hash]@o[org-id].ingest.sentry.io/[different-project-id]
```

**Save both DSNs - you'll need them!**

---

## Step 2: Configure Backend Sentry (10 minutes)

### 2.1 Install Sentry SDK (if not already installed)

```bash
cd backend
pip install sentry-sdk[fastapi]==1.39.1
pip freeze > requirements.txt
```

### 2.2 Add DSN to Environment Variables

Edit `backend/.env`:

```bash
# Sentry Error Tracking
SENTRY_DSN=https://[your-backend-hash]@o[org-id].ingest.sentry.io/[backend-project-id]
SENTRY_ENVIRONMENT=production
SENTRY_TRACES_SAMPLE_RATE=0.1  # 10% of transactions for performance monitoring
```

### 2.3 Verify Backend Configuration

Your backend already has Sentry configured in `backend/app/core/logging.py`. Just verify it's active:

```bash
cd backend
python3 << 'EOF'
from app.core.config import settings
import sentry_sdk

if settings.SENTRY_DSN:
    print("✅ Sentry DSN configured:")
    print(f"   DSN: {settings.SENTRY_DSN[:50]}...")
    print(f"   Environment: {settings.ENVIRONMENT}")
else:
    print("❌ Sentry DSN NOT configured")
    print("   Add SENTRY_DSN to your .env file")
EOF
```

### 2.4 Test Backend Sentry

Create a test endpoint to trigger an error:

```bash
# Start your backend locally
cd backend
uvicorn main:app --reload

# In another terminal, trigger test error
curl http://localhost:8000/api/test-sentry

# Check Sentry dashboard - you should see the error within 30 seconds
```

**If you don't see the error in Sentry:**
- Check `SENTRY_DSN` is set correctly
- Check no firewall blocking outbound HTTPS
- Check Sentry dashboard shows correct project

---

## Step 3: Configure Frontend Sentry (15 minutes)

### 3.1 Install Sentry SDK

```bash
cd frontend
npm install @sentry/react @sentry/tracing --save
```

### 3.2 Add DSN to Environment Variables

Edit `frontend/.env`:

```bash
# Sentry Error Tracking
REACT_APP_SENTRY_DSN=https://[your-frontend-hash]@o[org-id].ingest.sentry.io/[frontend-project-id]
REACT_APP_SENTRY_ENVIRONMENT=production
```

### 3.3 Initialize Sentry in React

Edit `frontend/src/index.js` (add at the top, before ReactDOM.render):

```javascript
import React from 'react';
import ReactDOM from 'react-dom/client';
import * as Sentry from "@sentry/react";
import { BrowserTracing } from "@sentry/tracing";
import App from './App';

// Initialize Sentry only in production
if (process.env.NODE_ENV === 'production' && process.env.REACT_APP_SENTRY_DSN) {
  Sentry.init({
    dsn: process.env.REACT_APP_SENTRY_DSN,
    environment: process.env.REACT_APP_SENTRY_ENVIRONMENT || 'production',
    integrations: [
      new BrowserTracing(),
      new Sentry.Replay({
        maskAllText: true,
        blockAllMedia: true,
      }),
    ],

    // Performance Monitoring
    tracesSampleRate: 0.1, // Capture 10% of transactions for performance monitoring

    // Session Replay
    replaysSessionSampleRate: 0.1, // 10% of sessions
    replaysOnErrorSampleRate: 1.0, // 100% of sessions with errors

    // Filter out sensitive data
    beforeSend(event, hint) {
      // Don't send events in development
      if (process.env.NODE_ENV !== 'production') {
        return null;
      }

      // Remove sensitive data from error context
      if (event.request) {
        delete event.request.cookies;
        delete event.request.headers;
      }

      return event;
    },

    // Ignore certain errors
    ignoreErrors: [
      // Browser extensions
      'top.GLOBALS',
      'chrome-extension://',
      'moz-extension://',

      // Network errors (temporary)
      'Network request failed',
      'Failed to fetch',

      // ResizeObserver errors (benign)
      'ResizeObserver loop limit exceeded',
    ],
  });
}

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
  <React.StrictMode>
    <Sentry.ErrorBoundary fallback={<div>An error has occurred</div>}>
      <App />
    </Sentry.ErrorBoundary>
  </React.StrictMode>
);
```

### 3.4 Wrap App with Sentry Error Boundary

Your existing `ErrorBoundary` can be enhanced. Edit `frontend/src/components/ErrorBoundary.js`:

```javascript
import React from 'react';
import * as Sentry from "@sentry/react";

class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }

  componentDidCatch(error, errorInfo) {
    // Log to Sentry in production
    if (process.env.NODE_ENV === 'production') {
      Sentry.captureException(error, { contexts: { react: errorInfo } });
    } else {
      console.error('Error caught by boundary:', error, errorInfo);
    }
  }

  render() {
    if (this.state.hasError) {
      return (
        <div style={{ padding: '40px', textAlign: 'center' }}>
          <h1>Oops! Something went wrong</h1>
          <p>We've been notified and are working to fix it.</p>
          <button onClick={() => window.location.reload()}>
            Reload Page
          </button>
        </div>
      );
    }

    return this.props.children;
  }
}

export default Sentry.withErrorBoundary(ErrorBoundary);
```

### 3.5 Test Frontend Sentry

Add a test button to trigger an error (in development):

```javascript
// Temporary test component
const TestSentryButton = () => {
  const triggerError = () => {
    Sentry.captureException(new Error("Test error from frontend"));
    throw new Error("This is a test error");
  };

  return (
    <button onClick={triggerError}>
      Test Sentry Error Tracking
    </button>
  );
};

// Add to your app temporarily, click button, check Sentry dashboard
```

---

## Step 4: Configure Alerts (10 minutes)

### 4.1 Backend Alerts

In Sentry dashboard:

1. Go to **adcopysurge-backend** project
2. Click **Alerts** → **Create Alert**

**Alert 1: Payment Webhook Failures**
- Name: `Critical: Payment Webhook Failures`
- Conditions: `error.type contains "paddle" AND count() > 1`
- Timeframe: `5 minutes`
- Action: Send email/Slack notification
- Priority: **Critical**

**Alert 2: Authentication Failures**
- Name: `High: Authentication Failures`
- Conditions: `message contains "authentication" AND count() > 10`
- Timeframe: `15 minutes`
- Action: Send email
- Priority: **High**

**Alert 3: Credit System Errors**
- Name: `Critical: Credit System Errors`
- Conditions: `message contains "credit" AND level = "error" AND count() > 3`
- Timeframe: `10 minutes`
- Action: Send email/Slack
- Priority: **Critical**

### 4.2 Frontend Alerts

In Sentry dashboard:

1. Go to **adcopysurge-frontend** project
2. Click **Alerts** → **Create Alert**

**Alert 1: High Error Rate**
- Name: `Critical: High Error Rate`
- Conditions: `count() > 100`
- Timeframe: `1 hour`
- Action: Send email
- Priority: **Critical**

**Alert 2: Payment Flow Errors**
- Name: `Critical: Payment Flow Errors`
- Conditions: `message contains "payment" OR message contains "subscribe"`
- Timeframe: `5 minutes`
- Action: Send email/Slack
- Priority: **Critical**

---

## Step 5: Set Up Releases (Optional but Recommended)

### 5.1 Backend Releases

Edit `backend/deploy/deploy.sh` (or create if doesn't exist):

```bash
#!/bin/bash

# Get git commit hash
RELEASE_VERSION=$(git rev-parse --short HEAD)

# Export for Sentry
export SENTRY_RELEASE="adcopysurge-backend@${RELEASE_VERSION}"

# Create Sentry release
sentry-cli releases new "$SENTRY_RELEASE"
sentry-cli releases set-commits "$SENTRY_RELEASE" --auto
sentry-cli releases finalize "$SENTRY_RELEASE"

# Deploy backend
sudo systemctl restart adcopysurge

# Mark deployment in Sentry
sentry-cli releases deploys "$SENTRY_RELEASE" new -e production
```

### 5.2 Frontend Releases

Edit `frontend/package.json`, add to scripts:

```json
{
  "scripts": {
    "build": "react-scripts build && npm run sentry:sourcemaps",
    "sentry:sourcemaps": "sentry-cli sourcemaps upload --release=$npm_package_version ./build"
  }
}
```

---

## Step 6: Monitoring Dashboard Setup

### 6.1 Create Custom Dashboard

In Sentry:

1. Go to **Dashboards** → **Create Dashboard**
2. Name: `AdCopySurge Production Health`

**Add these widgets:**

1. **Error Rate (Last 24h)**
   - Type: Line chart
   - Metric: `count()`
   - Grouping: By hour

2. **Top 10 Errors**
   - Type: Table
   - Metric: `count()`
   - Grouping: By error message

3. **Affected Users**
   - Type: Number
   - Metric: `count_unique(user)`
   - Filter: Last 24h

4. **Payment Errors**
   - Type: Number
   - Metric: `count()`
   - Filter: `message contains "paddle" OR message contains "payment"`

5. **API Performance (P95)**
   - Type: Line chart
   - Metric: `p95(transaction.duration)`
   - Filter: `transaction.op:http.server`

### 6.2 Daily Monitoring Routine

**Every morning, check:**
1. Open Sentry dashboard
2. Review error count (should be <10/day)
3. Check for any critical alerts
4. Review affected user count
5. Check payment error count (should be 0)

---

## Step 7: Team Integration (Optional)

### Slack Integration

1. In Sentry: **Settings** → **Integrations** → **Slack**
2. Click **Add to Slack**
3. Choose your channel (e.g., `#alerts` or `#engineering`)
4. Configure which alerts go to Slack

### Email Notifications

1. In Sentry: **Settings** → **Notifications**
2. Configure email preferences:
   - Critical alerts: **Immediately**
   - High priority: **Every 15 minutes**
   - Medium priority: **Daily digest**
   - Low priority: **Weekly digest**

---

## Verification Checklist

After setup, verify:

- [ ] Backend DSN configured in `.env`
- [ ] Frontend DSN configured in `.env`
- [ ] Test error appears in backend Sentry project
- [ ] Test error appears in frontend Sentry project
- [ ] Alerts configured for critical errors
- [ ] Email notifications working
- [ ] Slack notifications working (if configured)
- [ ] Dashboard shows real data
- [ ] Session replay working (frontend)
- [ ] Performance monitoring active

---

## Testing Sentry in Production

### Backend Test

```bash
# SSH into production server
ssh user@your-server

# Trigger test error
curl http://localhost:8000/api/test-sentry

# Check Sentry dashboard within 30 seconds
```

### Frontend Test

```javascript
// Add to your app temporarily (development only)
if (process.env.NODE_ENV === 'development') {
  window.testSentry = () => {
    throw new Error("Frontend Sentry test error");
  };

  // Call in browser console: testSentry()
}
```

---

## Sentry Best Practices

### 1. Context is Everything

Add user context to errors:

```javascript
// Frontend
Sentry.setUser({
  id: user.id,
  email: user.email,
  subscription_tier: user.subscription_tier
});

// Backend (already configured in middleware)
```

### 2. Tag Errors for Easy Filtering

```javascript
// Frontend
Sentry.setTag("payment_flow", "checkout");

// Backend
sentry_sdk.set_tag("credit_operation", "deduction");
```

### 3. Add Breadcrumbs

```javascript
// Track user actions leading to error
Sentry.addBreadcrumb({
  category: 'user',
  message: 'User started analysis',
  level: 'info'
});
```

### 4. Filter Sensitive Data

Already configured in `beforeSend` hook - never send:
- Passwords
- API keys
- Credit card numbers
- Personal data (beyond user ID)

---

## Cost Management

**Free Tier Limits:**
- 5,000 errors/month
- 10,000 transactions/month (performance)
- 50 replays/month

**Tips to stay within limits:**
1. Set `tracesSampleRate: 0.1` (10% sampling)
2. Set `replaysSessionSampleRate: 0.1` (10% sessions)
3. Filter out noisy errors with `ignoreErrors`
4. Use `beforeSend` to drop non-critical errors

**If you exceed limits:**
- Upgrade to Team plan ($26/month) for 50,000 errors
- Or reduce sampling rates

---

## Troubleshooting

### No Errors Showing in Sentry

**Check:**
1. DSN is correct in `.env`
2. Environment is `production` not `development`
3. Firewall allows outbound HTTPS to `*.sentry.io`
4. Sentry SDK installed: `pip list | grep sentry` or `npm list @sentry/react`

### Too Many Errors

**Common culprits:**
1. Network errors (temporary) - filter with `ignoreErrors`
2. Browser extension errors - filter with `chrome-extension://`
3. Development mode errors - check `NODE_ENV`

### Errors Not Grouped Properly

1. Go to **Settings** → **Issue Grouping**
2. Enable fingerprinting rules
3. Customize grouping for your error patterns

---

## Success Criteria

After Sentry is fully set up, you should:

✅ See errors in dashboard within seconds of occurrence
✅ Get email alerts for critical errors
✅ Know immediately if payments fail
✅ Track error trends over time
✅ See which users are affected
✅ Have full context to debug issues
✅ Monitor API performance
✅ Track deploy impact on error rates

**Without Sentry, you're debugging in the dark. With Sentry, you have x-ray vision into your production app.** 🔍

---

## Next Steps

1. Complete Sentry setup (1-2 hours)
2. Test error tracking works
3. Set up alerts
4. Monitor for 48 hours before advertising launch
5. Use data to fix any issues found
6. Launch with confidence! 🚀
