# 🔗 How to Connect AdCopySurge to Zapier

Zapier lets you connect AdCopySurge with 8,000+ apps to automate your ad analysis workflow. Follow this step-by-step guide to set up your connection.

---

## 📋 Prerequisites

- An active Zapier account ([Sign up free](https://zapier.com/sign-up))
- Access to your AdCopySurge integrations page

---

## 🚀 Step-by-Step Setup

### Step 1: Create a New Zap in Zapier

1. Log in to your [Zapier account](https://zapier.com/app/login)
2. Click **"Create Zap"** button (top right)
3. You'll be taken to the Zap editor

### Step 2: Set Up the Webhook Trigger

1. In the **"Trigger"** section, search for **"Webhooks by Zapier"**
2. Click on **"Webhooks by Zapier"** from the results
3. For the **Event**, select **"Catch Hook"**
4. Click **"Continue"**

### Step 3: Get Your Webhook URL

1. Zapier will display a **webhook URL** that looks like:
   ```
   https://hooks.zapier.com/hooks/catch/1234567/abcdefg
   ```
2. Click the **"Copy"** button to copy this URL
3. **Keep this tab open** - you'll need it later!

### Step 4: Connect AdCopySurge to Zapier

1. Go to your **AdCopySurge** dashboard
2. Navigate to **Integrations** page
3. Find the **Zapier** integration card
4. Click the **"Connect"** button
5. In the setup dialog:
   - **Paste your webhook URL** in the "Zapier Webhook URL" field
   - **Select data format**:
     - **Summary (Recommended)**: Key metrics and top insights
     - **Full Analysis Data**: Complete analysis with all details
     - **Scores Only**: Just the scores and platform info
6. Click **"Test"** to verify the connection
7. Click **"Connect"** to save

### Step 5: Test Your Connection in Zapier

1. Go back to your **Zapier tab**
2. Click **"Test trigger"** in Zapier
3. You should see test data from AdCopySurge appear
4. Click **"Continue"** to proceed

### Step 6: Add Actions (What Happens Next)

Now add what you want to do with your AdCopySurge data:

**Popular examples:**
- 📊 Send to **Google Sheets** for tracking
- 💬 Post to **Slack** for team notifications
- 📧 Send via **Email** for reports
- 📝 Add to **Notion** database
- 📈 Track in **Airtable**
- 🎨 Create **Trello** cards for low-performing ads

**To add an action:**
1. Click **"+"** below your trigger
2. Search for the app you want to use
3. Select the action (e.g., "Create Spreadsheet Row")
4. Connect your account
5. Map the data fields from AdCopySurge
6. Test the action
7. Turn on your Zap!

---

## 📊 Data You'll Receive

When AdCopySurge sends analysis data, you'll receive:

### Summary Format (Recommended)
```json
{
  "event": "analysis_completed",
  "timestamp": "2025-01-27T10:30:00Z",
  "data": {
    "score": 8.5,
    "platform": "facebook",
    "improvement": "+15%",
    "top_insights": [
      "Strong headline engagement",
      "Call-to-action needs improvement",
      "Visual appeal is excellent"
    ]
  }
}
```

### Full Format
Complete analysis including all insights, recommendations, scores breakdown, and metadata.

### Scores Only
Just the essential metrics: score, platform, and improvement percentage.

---

## 🎯 Popular Zap Templates

### 1. Track All Analyses in Google Sheets
**Trigger:** AdCopySurge analysis completed  
**Action:** Add row to Google Sheets  
**Use case:** Build a database of all your ad analyses

### 2. Alert Team on Low Scores
**Trigger:** AdCopySurge analysis completed  
**Filter:** Only continue if score < 6.0  
**Action:** Send Slack message  
**Use case:** Get notified when ads need immediate attention

### 3. Email Weekly Reports
**Trigger:** Schedule (every Monday)  
**Action:** Send digest email  
**Use case:** Weekly summary of ad performance

### 4. Create Tasks for Improvements
**Trigger:** AdCopySurge analysis completed  
**Filter:** Score < 7.0  
**Action:** Create Trello card or Asana task  
**Use case:** Turn low scores into actionable tasks

---

## 🔧 Troubleshooting

### "Webhook URL is invalid"
- Make sure you copied the complete URL from Zapier
- URL should start with `https://hooks.zapier.com/hooks/catch/`
- No spaces before or after the URL

### "Test connection failed"
- This is normal if you haven't tested your Zap trigger yet
- You can still connect - the connection will work when you turn on your Zap
- Make sure your Zap is turned ON in Zapier

### "No data appearing in Zapier"
1. Check that your Zap is **turned ON** (not paused)
2. Verify the webhook URL in AdCopySurge matches Zapier
3. Run a test analysis in AdCopySurge
4. Check Zapier's "Task History" for any errors

### "Connection keeps disconnecting"
- Make sure you didn't delete the Zap in Zapier
- Verify the webhook URL hasn't changed
- Try disconnecting and reconnecting in AdCopySurge

---

## 💡 Pro Tips

1. **Use Filters**: Add filter steps in Zapier to only trigger on specific conditions (e.g., score > 8.0 or platform = "facebook")

2. **Multi-Step Zaps**: You can send data to multiple apps in one Zap (e.g., Google Sheets + Slack + Email)

3. **Format Data**: Use Zapier's "Formatter" tool to customize how data appears in destination apps

4. **Paths**: Use Zapier's "Paths" feature to route different scores to different apps

5. **Test First**: Always test your Zap before turning it on to ensure data flows correctly

---

## 🆘 Need Help?

- **Zapier Support**: [https://zapier.com/help](https://zapier.com/help)
- **AdCopySurge Support**: Contact us at support@adcopysurge.com
- **Community Forum**: Share your Zap workflows with other users

---

## 📚 Next Steps

Once your Zapier integration is working:

1. ✅ Run a few test analyses to verify data flows correctly
2. ✅ Create multiple Zaps for different use cases
3. ✅ Share successful Zap templates with your team
4. ✅ Monitor your Zap task usage in Zapier

---

**Last Updated**: January 2025  
**Integration Type**: Webhook-based  
**Difficulty**: Beginner-friendly ⭐⭐☆☆☆
