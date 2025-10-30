# Google Analytics & Search Console Setup Guide

## 1. Google Analytics 4 Setup

### Step 1: Create GA4 Property
1. Go to [Google Analytics](https://analytics.google.com/)
2. Click **Admin** (gear icon)
3. Click **Create Property**
4. Enter property name: `AdCopySurge`
5. Select timezone and currency
6. Click **Create**

### Step 2: Set Up Data Stream
1. Under **Property** → **Data Streams**
2. Click **Add stream** → **Web**
3. Enter:
   - Website URL: `https://adcopysurge.com`
   - Stream name: `AdCopySurge Production`
4. Click **Create stream**
5. **Copy the Measurement ID** (format: `G-XXXXXXXXXX`)

### Step 3: Add Measurement ID to Your App
Add to `frontend/.env`:
```bash
REACT_APP_GA_MEASUREMENT_ID=G-XXXXXXXXXX
```

### Step 4: Add GoogleAnalytics Component to App.js
```jsx
import GoogleAnalytics from './components/Analytics/GoogleAnalytics';

function App() {
  return (
    <BrowserRouter>
      <GoogleAnalytics />
      {/* ... rest of your app */}
    </BrowserRouter>
  );
}
```

### Step 5: Track Events (Optional)
Import tracking functions where needed:
```jsx
import { trackSignup, trackLogin, trackAdAnalysis } from './components/Analytics/GoogleAnalytics';

// In your signup handler:
trackSignup('email');

// In your ad analysis handler:
trackAdAnalysis('facebook');
```

---

## 2. Google Search Console Setup

### Step 1: Add Property
1. Go to [Google Search Console](https://search.google.com/search-console/)
2. Click **Add property**
3. Select **URL prefix**
4. Enter: `https://adcopysurge.com`
5. Click **Continue**

### Step 2: Verify Ownership
Choose one verification method:

#### Option A: DNS Verification (Recommended)
1. Copy the TXT record provided
2. Add to your domain's DNS settings
3. Wait 5-10 minutes for DNS propagation
4. Click **Verify**

#### Option B: HTML File Upload
1. Download the verification file
2. Upload to `frontend/public/` folder
3. Deploy the site
4. Click **Verify**

### Step 3: Submit Sitemap
1. Once verified, go to **Sitemaps** in the left menu
2. Enter: `https://adcopysurge.com/sitemap.xml`
3. Click **Submit**

### Step 4: Monitor Indexing
- Check **Coverage** report after 24-48 hours
- Fix any errors Google finds
- Monitor search performance in **Performance** report

---

## 3. Deployment Steps

### Build and Deploy Frontend
```bash
cd frontend
npm run build
```

### Copy sitemap.xml and robots.txt
These files are in `frontend/public/` and will be included in the build automatically.

### Verify Files Are Accessible
After deployment, check:
- https://adcopysurge.com/sitemap.xml
- https://adcopysurge.com/robots.txt

Both should return 200 OK.

---

## 4. Important Notes

### Privacy & GDPR Compliance
- Add cookie consent banner if targeting EU users
- Update privacy policy to mention Google Analytics
- Consider IP anonymization:
  ```js
  gtag('config', 'G-XXXXXXXXXX', {
    anonymize_ip: true
  });
  ```

### Events to Track
Key events already configured:
- ✅ `sign_up` - User registration
- ✅ `login` - User login
- ✅ `analyze_ad` - Ad analysis performed
- ✅ `purchase` - Subscription purchase
- ✅ `invite_team_member` - Team invitation sent
- ✅ `contact_support` - Support ticket created

### GA4 Enhanced Measurement
Enable automatically tracked events in GA4:
1. Go to **Admin** → **Data Streams** → Your stream
2. Click **Enhanced measurement**
3. Enable:
   - ✅ Page views
   - ✅ Scrolls
   - ✅ Outbound clicks
   - ✅ Site search
   - ✅ Form interactions

---

## 5. Testing

### Test Analytics Locally
1. Add GA Measurement ID to `.env`
2. Run `npm start`
3. Open browser with GA Debugger extension
4. Navigate through your app
5. Check [GA Real-Time reports](https://analytics.google.com/) to see events

### Test Sitemap
```bash
curl https://adcopysurge.com/sitemap.xml
```

Should return valid XML with all your URLs.

---

## 6. Monitoring

### Weekly Checks
- [ ] Review GA4 user growth
- [ ] Check Search Console coverage errors
- [ ] Monitor core web vitals
- [ ] Review conversion funnel

### Monthly Reports
- [ ] Traffic sources analysis
- [ ] User behavior flow
- [ ] Conversion rate by channel
- [ ] Search queries performance

---

## Support

If you have issues:
1. Check browser console for GA errors
2. Use [GA Debug Mode](https://support.google.com/analytics/answer/7201382)
3. Verify measurement ID is correct
4. Check network tab for gtag requests
