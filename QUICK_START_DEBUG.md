# 🚀 Quick Start: Debug Ad Analysis Workflow

## Immediate Action Steps

### 1. Start Both Services (2 minutes)

**Terminal 1 - Backend:**
```powershell
cd C:\Users\User\Desktop\Eledami\adsurge\acs-clean\backend
uvicorn main:app --reload --port 8000
```

**Terminal 2 - Frontend:**
```powershell
cd C:\Users\User\Desktop\Eledami\adsurge\acs-clean\frontend
npm start
```

### 2. Access Debug Page (30 seconds)

1. Open browser: `http://localhost:3000`
2. Log in if required
3. Navigate to: `http://localhost:3000/debug/analysis`

### 3. Run Comprehensive Test (1 minute)

1. Click the big **"Run Complete Test"** button
2. Watch the phases execute (5 colored status cards will update)
3. Expand the "Test Logs" accordion to see details

### 4. Interpret Results

#### ✅ All Phases Pass (Green Checks)
**Status**: Workflow is working correctly!  
**Action**: Test the actual Dashboard at `/dashboard`

#### ❌ Phase 1 Fails (Red X)
**Issue**: Frontend or authentication problem  
**Check**:
- Is user logged in? (Check Supabase session)
- Is API baseURL configured? (Should start with `http://`)

**Quick Fix**:
```javascript
// Check in browser console:
console.log('API baseURL:', window.apiService?.baseURL);
```

#### ❌ Phase 2 Fails
**Issue**: API service method problem  
**Check**: Console logs for "apiService.analyzeAd is not a function"

#### ❌ Phase 3 Fails
**Issue**: Network request not initiated  
**Check**:
- Open DevTools → Network tab
- Look for failed/blocked requests
- Check CORS errors in console

**Quick Fix**:
```python
# In backend/main.py, ensure CORS includes your frontend:
allow_origins=["http://localhost:3000"]
```

#### ❌ Phase 4 Fails
**Issue**: Backend processing error  
**Check Backend Terminal** for error messages

**Common causes**:
- Missing `OPENAI_API_KEY` in `.env`
- Database connection issues
- Python exceptions

**Quick Fix**:
```bash
# Check if backend is running:
curl http://localhost:8000/health
# Should return: {"status":"healthy"}
```

---

## Manual Dashboard Test (If Debug Page Passes)

### Step-by-Step:

1. **Go to Dashboard**:
   ```
   http://localhost:3000/dashboard
   ```

2. **Open Browser Console** (F12):
   - Make sure Console tab is selected
   - Clear any existing logs

3. **Select Platform**:
   - Click any platform card (Facebook, Instagram, etc.)
   - **Expected**: Console shows `✅ Platform selected: facebook`

4. **Click "Analyze Ad"**:
   - Button should be enabled (not gray)
   - **Expected Console Logs**:
     ```
     🔄 QuickActions: Analyze button clicked
     ✅ QuickActions: Calling onAnalyzeClick
     🔄 Dashboard: handleAnalyzeClick called
     ✅ Dashboard: Setting showInputPanel to true
     ```

5. **Input Panel Should Appear**:
   - Large panel with form fields
   - If not visible → **ISSUE FOUND** → State not updating

6. **Fill Form**:
   - Headline: "Test Ad"
   - Body: "This is test body text"
   - CTA: "Click Here"

7. **Click "Analyze" in Panel**:
   - **Expected Console Logs**:
     ```
     🔄 EnhancedAdInputPanel: handleSubmit called
     ✅ EnhancedAdInputPanel: Calling onAnalyze
     🚀 Starting ad analysis...
     📤 Sending data to API
     ```

8. **Check Network Tab**:
   - Filter by "analyze"
   - Should see: `POST /api/ads/analyze` with status 200
   - If status 4xx/5xx → Click to see error details

9. **Wait 2-5 seconds**:
   - **Expected**: Results appear on screen
   - **Expected Console**: `📥 Received result from API`

---

## 🔥 Most Likely Issues

### Issue #1: Nothing Happens When Clicking "Analyze Ad"
**Diagnosis**: Platform not selected or button disabled  
**Fix**: Click a platform card first (Facebook, Google, etc.)

### Issue #2: Input Panel Shows But No API Call
**Diagnosis**: Form validation failing or handler not wired  
**Check Console** for error messages  
**Look For**: `❌ EnhancedAdInputPanel: NOT calling onAnalyze - conditions not met`

### Issue #3: API Call Fails with 403/CORS Error
**Diagnosis**: CORS misconfiguration  
**Fix in backend/main.py**:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # ← Add your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Issue #4: API Call Returns 500 Error
**Diagnosis**: Backend crash or missing environment variable  
**Check Backend Terminal** for Python traceback  
**Common Causes**:
- Missing `OPENAI_API_KEY` in `backend/.env`
- Database connection failure
- Invalid request format

**Quick Fix**:
```bash
# In backend directory, create/edit .env file:
echo "OPENAI_API_KEY=sk-your-key-here" >> .env
# Restart backend
```

---

## 🎯 Success Checklist

- [ ] Backend running on port 8000
- [ ] Frontend running on port 3000
- [ ] Debug page accessible at `/debug/analysis`
- [ ] All 5 phases pass in debug test
- [ ] Dashboard loads without errors
- [ ] Platform selection works (button enabled)
- [ ] "Analyze Ad" opens input panel
- [ ] Form submission triggers API call
- [ ] Network request returns 200 OK
- [ ] Results display on screen

---

## 📱 Quick Commands Reference

```powershell
# Start backend
cd backend
uvicorn main:app --reload

# Start frontend  
cd frontend
npm start

# Check backend health
curl http://localhost:8000/health

# Test backend directly
curl -X POST http://localhost:8000/api/ads/analyze `
  -H "Content-Type: application/json" `
  -d '{"ad":{"headline":"Test","body_text":"Test","cta":"Click","platform":"facebook"},"competitor_ads":[]}'

# View backend logs (if logging to file)
tail -f backend/logs/app.log
```

---

## 🆘 Still Not Working?

1. **Collect Logs**:
   - Copy all console logs (Ctrl+A in Console tab → Ctrl+C)
   - Copy all backend terminal output
   - Export Network tab as HAR file

2. **Check Existing Logs**:
   - Console already has comprehensive logging implemented
   - QuickActions, EnhancedAdInputPanel, Dashboard all log extensively
   - Look for 🔄, ✅, ❌ prefixes

3. **Review Full Audit Doc**:
   - See `ANALYSIS_WORKFLOW_AUDIT.md` for detailed troubleshooting
   - Contains common issues, fixes, and complete workflow explanation

4. **Use Debug Page for Systematic Testing**:
   - Tests each phase independently
   - Provides detailed error messages
   - Shows exactly where the flow breaks

---

**Next**: After confirming the issue location, refer to `ANALYSIS_WORKFLOW_AUDIT.md` Section "🐛 Common Issues & Fixes" for detailed resolution steps.
