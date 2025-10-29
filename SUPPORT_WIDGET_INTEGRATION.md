# Support Widget Integration Guide

Complete guide for integrating the support contact system into your AdCopy Surge app.

## 📋 Overview

The support system includes:
- **Backend API**: Python/FastAPI endpoint with rate limiting
- **Frontend Widget**: React component with floating button and modal
- **Database**: Supabase table for storing tickets
- **Email**: Resend integration for notifications

---

## 🚀 Setup Instructions

### 1. Database Migration

Run the SQL migration in your Supabase dashboard:

```bash
# Navigate to Supabase Dashboard > SQL Editor
# Copy and paste the contents of:
database/migrations/add_support_tickets_table.sql
```

Or use the Supabase CLI:
```bash
supabase db push database/migrations/add_support_tickets_table.sql
```

This creates:
- `support_tickets` table
- Indexes for performance
- Row Level Security (RLS) policies
- Auto-update triggers
- Statistics view for admins

### 2. Backend Integration

#### Register the Router

Add the support router to your main FastAPI application:

**File: `backend/app/main.py` or `backend/main_launch_ready.py`**

```python
from app.routers import support  # Add this import

# In your FastAPI app setup:
app.include_router(support.router)
```

#### Verify Dependencies

Ensure these packages are in `backend/requirements.txt`:
```txt
fastapi
pydantic[email]
supabase
resend
```

Install if needed:
```bash
cd backend
pip install -r requirements.txt
```

### 3. Environment Variables

Ensure these are set in your `.env` file or environment:

```env
# Supabase (already configured)
REACT_APP_SUPABASE_URL=your_supabase_url
SUPABASE_SERVICE_ROLE_KEY=your_service_role_key

# Resend Email (already configured per email_service.py)
RESEND_API_KEY=your_resend_api_key
RESEND_FROM_EMAIL=support@adcopysurge.com
RESEND_FROM_NAME=AdCopy Surge Support

# Backend API URL (for frontend)
REACT_APP_API_URL=http://localhost:8000  # or your production URL
```

### 4. Frontend Integration

#### Add SupportWidget to App.js

**File: `frontend/src/App.js`**

Add the import at the top:
```javascript
import SupportWidget from './components/SupportWidget';
```

Add the widget inside your main App component, just before the closing tags:

**Option A: Inside `<Router>` (recommended - shows on all pages)**
```javascript
function App() {
  return (
    <NoWallet>
      <QueryClientProvider client={queryClient}>
        <WhiteLabelProvider>
          <ThemeModeProvider>
            <CssBaseline />
            <SettingsProvider>
              <AuthProvider>
                <BlogProvider>
                  <Router>
                    <Routes>
                      {/* ... your routes ... */}
                    </Routes>
                    <Toaster position="top-right" />
                    <SupportWidget />  {/* Add this line */}
                  </Router>
                </BlogProvider>
              </AuthProvider>
            </SettingsProvider>
          </ThemeModeProvider>
        </WhiteLabelProvider>
      </QueryClientProvider>
    </NoWallet>
  );
}
```

**Option B: Only on authenticated pages**
```javascript
// Inside ProtectedRoute or AppLayout component
<Route element={<ProtectedRoute><AppLayout /></ProtectedRoute>}>
  {/* your protected routes */}
  <SupportWidget />
</Route>
```

#### Fix Radio Button Import

The component uses `FormControlRadio` which should be `FormControlLabel`. Update line 14 in `SupportWidget.jsx`:

```javascript
// Change this:
FormControlRadio,

// To this:
FormControlLabel,
```

And update lines 380 and 390:
```javascript
// Change:
<FormControlRadio

// To:
<FormControlLabel
```

---

## 🎨 Customization

### Change Support Email

Edit `backend/app/routers/support.py` line 234:
```python
to=settings.RESEND_FROM_EMAIL,  # Change to your support email
```

Or set environment variable:
```env
RESEND_FROM_EMAIL=your-support@yourcompany.com
```

### Modify FAQ Items

Edit `frontend/src/components/SupportWidget.jsx` lines 41-58:
```javascript
const FAQ_ITEMS = [
  {
    question: 'Your question?',
    answer: 'Your answer...'
  },
  // Add more FAQ items
];
```

### Change Subject Options

Edit line 60-67 in `SupportWidget.jsx`:
```javascript
const SUBJECT_OPTIONS = [
  'Bug Report',
  'Feature Request',
  // Add your custom subjects
];
```

### Adjust Rate Limiting

Edit `backend/app/routers/support.py` lines 23-24:
```python
RATE_LIMIT_REQUESTS = 3  # Change to desired number
RATE_LIMIT_WINDOW = timedelta(hours=1)  # Change time window
```

---

## 🧪 Testing

### 1. Test Backend API

```bash
# Start backend server
cd backend
uvicorn main_launch_ready:app --reload --port 8000

# Test endpoint (use Postman or curl)
curl -X POST http://localhost:8000/api/support/send \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test User",
    "email": "test@example.com",
    "subject": "Bug Report",
    "message": "This is a test message with more than 20 characters",
    "priority": "normal"
  }'
```

Expected response:
```json
{
  "success": true,
  "message": "Message sent! We'll respond within 24 hours.",
  "ticket_id": "uuid-here"
}
```

### 2. Test Frontend Widget

```bash
# Start frontend
cd frontend
npm start

# Widget should appear as floating button in bottom-right corner
# Click to open modal and test form submission
```

### 3. Verify Database

Check Supabase dashboard:
```sql
SELECT * FROM support_tickets ORDER BY created_at DESC LIMIT 10;
```

### 4. Check Email

- Verify email arrives at your `RESEND_FROM_EMAIL` address
- Check Resend dashboard for delivery logs

---

## 📊 Admin Dashboard (Optional)

Create an admin page to view tickets:

```javascript
// Example: frontend/src/pages/AdminSupport.js
import { useState, useEffect } from 'react';
import { supabase } from '../lib/supabaseClientClean';

function AdminSupport() {
  const [tickets, setTickets] = useState([]);

  useEffect(() => {
    const fetchTickets = async () => {
      const { data } = await supabase
        .from('support_tickets')
        .select('*')
        .order('created_at', { ascending: false });
      setTickets(data);
    };
    fetchTickets();
  }, []);

  return (
    <div>
      <h1>Support Tickets</h1>
      {tickets.map(ticket => (
        <div key={ticket.id}>
          <h3>{ticket.subject}</h3>
          <p>From: {ticket.name} ({ticket.email})</p>
          <p>Priority: {ticket.priority}</p>
          <p>Status: {ticket.status}</p>
          <p>{ticket.message}</p>
        </div>
      ))}
    </div>
  );
}
```

---

## 🔒 Security Notes

1. **Rate Limiting**: Currently in-memory. For production with multiple servers, use Redis:
   ```python
   # TODO: Replace in-memory rate limiting with Redis
   ```

2. **RLS Policies**: Configured in SQL migration. Users can only see their own tickets.

3. **Email Validation**: Backend validates email format using Pydantic.

4. **Input Sanitization**: Message length and content validated on both frontend and backend.

---

## 🐛 Troubleshooting

### Widget doesn't appear
- Check browser console for errors
- Verify `SupportWidget` is imported in App.js
- Check z-index conflicts (widget uses 1300)

### API returns 500 error
- Check backend logs for errors
- Verify Supabase credentials
- Ensure `support_tickets` table exists

### Email not sending
- Check Resend API key is valid
- Verify `RESEND_FROM_EMAIL` is configured
- Check Resend dashboard for error logs
- Ensure email service is initialized correctly

### Rate limit issues
- Clear rate limit: Restart backend (in-memory store clears)
- For production: Implement Redis-based rate limiting

### FormControlRadio error
- Update import to use `FormControlLabel` instead
- See "Fix Radio Button Import" section above

---

## 📈 Analytics & Monitoring

View support ticket stats:
```sql
SELECT * FROM support_ticket_stats;
```

Returns:
- Open tickets
- In-progress tickets
- Closed/resolved tickets
- Urgent tickets
- Tickets in last 24h/7d
- Average resolution time

---

## 🚢 Production Deployment

1. **Update CORS origins** in backend config:
   ```python
   CORS_ORIGINS = "https://yourdomain.com,https://app.yourdomain.com"
   ```

2. **Set production API URL**:
   ```env
   REACT_APP_API_URL=https://api.yourdomain.com
   ```

3. **Enable Resend production mode**:
   - Use production Resend API key
   - Verify sender domain

4. **Implement Redis rate limiting** for multi-server deployments

5. **Monitor email delivery** via Resend dashboard

---

## 📝 Additional Features (Future Enhancements)

- [ ] Real-time status updates using WebSockets
- [ ] File attachments for screenshots
- [ ] Auto-responses for common issues
- [ ] Integration with Slack/Discord for notifications
- [ ] Multi-language support
- [ ] Sentiment analysis on messages
- [ ] AI-powered suggested responses

---

## 🆘 Support

If you need help with integration:
1. Check logs: Backend console and browser console
2. Verify all environment variables are set
3. Test each component individually (DB, API, Widget)
4. Check Supabase and Resend dashboards

---

**Created by:** AdCopy Surge Development Team  
**Last Updated:** 2025
