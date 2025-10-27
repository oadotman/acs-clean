# 🔄 How to Connect AdCopySurge to n8n

n8n is an open-source workflow automation platform that gives you complete control over your data. Follow this guide to connect AdCopySurge with your n8n instance.

---

## 📋 Prerequisites

- An n8n instance (self-hosted or [n8n.cloud account](https://n8n.io/cloud))
- Access to your AdCopySurge integrations page
- Basic understanding of n8n workflows (helpful but not required)

---

## 🆓 Getting n8n

### Option 1: n8n Cloud (Easiest)
- Sign up at [n8n.cloud](https://n8n.io/cloud)
- Free tier available
- No setup required

### Option 2: Self-Hosted (Most Control)
- Install via Docker: `docker run -it --rm --name n8n -p 5678:5678 n8nio/n8n`
- Or use npm: `npm install n8n -g`
- [Full installation guide](https://docs.n8n.io/hosting/)

---

## 🚀 Step-by-Step Setup

### Step 1: Create a New Workflow in n8n

1. Log in to your n8n instance
2. Click **"+ Create New Workflow"** or **"Add Workflow"**
3. You'll see an empty workflow canvas

### Step 2: Add a Webhook Node

1. Click the **"+"** button to add a node
2. Search for **"Webhook"**
3. Click on **"Webhook"** node to add it
4. The webhook node settings will open

### Step 3: Configure the Webhook Node

1. In the webhook node settings:
   - **HTTP Method**: Select **"POST"**
   - **Path**: Leave as default or customize (e.g., `/adcopysurge`)
   - **Authentication**: Select **"None"** (or set up if needed)
   - **Response Mode**: Select **"On Received"**
   
2. You'll see two URLs:
   - **Test URL**: For testing (temporary)
   - **Production URL**: For live use (permanent)

3. **Copy the Production URL** - it looks like:
   ```
   https://your-n8n-instance.com/webhook/abc123xyz
   ```

### Step 4: Connect AdCopySurge to n8n

1. Go to your **AdCopySurge** dashboard
2. Navigate to **Integrations** page
3. Find the **n8n** integration card
4. Click the **"Connect"** button
5. In the setup dialog:
   - **Paste your webhook URL** in the "n8n Webhook URL" field
   - **Select data format**:
     - **Summary (Recommended)**: Key metrics and top insights
     - **Full Analysis Data**: Complete analysis with all details
     - **Scores Only**: Just the scores and platform info
6. Click **"Test"** to verify the connection
7. Click **"Connect"** to save

### Step 5: Test Your Connection in n8n

1. Go back to your **n8n workflow**
2. Click **"Execute Workflow"** button (play icon)
3. The workflow is now listening for data
4. Run a test analysis in AdCopySurge
5. You should see the data appear in the webhook node
6. Click **"Save"** in n8n (top right)

### Step 6: Add Processing Nodes

Now build your workflow with what you want to do with the data:

**Popular n8n nodes to add:**
- 📊 **Google Sheets** - Add rows with analysis data
- 💬 **Slack** - Send notifications to channels
- 📧 **Email (Send)** - Email reports to team
- 🗄️ **Database** - Store in PostgreSQL/MySQL
- 📝 **Notion** - Create pages with analysis
- 🔔 **Discord/Telegram** - Alert via chat
- ⚙️ **Function** - Process data with JavaScript
- 🌐 **HTTP Request** - Send to your own API

**To add nodes:**
1. Click **"+"** after the webhook node
2. Search for the service/function you need
3. Configure the node with your credentials
4. Map data fields from the webhook
5. Test the node
6. Save and activate your workflow

---

## 📊 Data You'll Receive

When AdCopySurge sends analysis data, your webhook will receive:

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

### Accessing Data in n8n

In your n8n nodes, access the data using expressions:
- `{{ $json.data.score }}` - Get the score
- `{{ $json.data.platform }}` - Get the platform
- `{{ $json.data.top_insights }}` - Get insights array
- `{{ $json.timestamp }}` - Get timestamp

---

## 🎯 Popular n8n Workflow Examples

### 1. Track All Analyses in Google Sheets

**Nodes:**
1. Webhook (trigger from AdCopySurge)
2. Google Sheets (append row)

**Use case:** Build a spreadsheet database of all analyses

### 2. Alert Team on Low Scores

**Nodes:**
1. Webhook (trigger from AdCopySurge)
2. IF node (condition: score < 6.0)
3. Slack (send message if true)

**Use case:** Instant alerts for underperforming ads

### 3. Store in Database + Send Email

**Nodes:**
1. Webhook (trigger from AdCopySurge)
2. PostgreSQL (insert record)
3. Email (send summary to team)

**Use case:** Persist data and notify stakeholders

### 4. Process with JavaScript

**Nodes:**
1. Webhook (trigger from AdCopySurge)
2. Function node (custom JavaScript to process data)
3. HTTP Request (send to your API)

**Use case:** Custom data transformation and routing

### 5. Multi-Channel Notifications

**Nodes:**
1. Webhook (trigger from AdCopySurge)
2. Slack (send to #marketing)
3. Discord (send to dev team)
4. Email (send to manager)

**Use case:** Broadcast analysis results across platforms

---

## 🔧 Troubleshooting

### "Webhook URL is invalid"
- Make sure you copied the complete URL from n8n
- URL should start with `https://` or `http://`
- No spaces before or after the URL
- Use the **Production URL**, not the Test URL

### "Test connection failed"
- Make sure your n8n workflow is **active** (executed/listening)
- Check if your n8n instance is accessible from the internet
- If self-hosted, verify firewall/port settings
- Test URL manually with a tool like Postman

### "No data appearing in n8n"
1. Verify your workflow is **active** (green dot in workflow list)
2. Click "Execute Workflow" to start listening
3. Check that the webhook URL in AdCopySurge matches n8n exactly
4. Run a test analysis in AdCopySurge
5. Check n8n "Executions" tab for any errors

### "Self-hosted n8n not receiving webhooks"
- **Port forwarding**: Make sure port 5678 (or custom) is accessible
- **Firewall**: Allow incoming connections to n8n
- **HTTPS**: Consider using ngrok or tunneling for testing
- **Public IP**: Your n8n instance needs to be reachable from internet

### "Workflow keeps timing out"
- Check "Response Mode" in webhook node (set to "On Received")
- Verify downstream nodes aren't taking too long
- Use "Execute Once" for testing instead of manual trigger

---

## 💡 Pro Tips

1. **Use IF Nodes**: Add conditional logic to route high/low scores differently

2. **JavaScript Functions**: Process data with custom JavaScript code using Function nodes

3. **Error Handling**: Add "Error Trigger" nodes to catch and handle failures

4. **Credentials**: Store API keys securely in n8n's credentials system

5. **Variables**: Use workflow variables to store reusable values

6. **Execution History**: Check the "Executions" tab to see workflow runs and debug issues

7. **Copy Workflows**: Duplicate successful workflows for different use cases

8. **Version Control**: n8n supports Git integration for workflow backups

---

## 🔐 Security Best Practices

### For Self-Hosted n8n:
- ✅ Use HTTPS with valid SSL certificate
- ✅ Set up webhook authentication (header auth or basic auth)
- ✅ Use environment variables for sensitive data
- ✅ Enable rate limiting on your server
- ✅ Keep n8n updated to latest version

### For n8n Cloud:
- ✅ Use strong passwords and 2FA
- ✅ Regularly review active workflows
- ✅ Audit webhook access logs
- ✅ Limit permissions for team members

---

## 📚 Advanced Features

### Custom Code Processing

Add a **Function** node after the webhook:

```javascript
// Access webhook data
const analysisData = $input.first().json;

// Process the data
if (analysisData.data.score < 6.0) {
  return {
    json: {
      alert: 'urgent',
      message: `Low score detected: ${analysisData.data.score}`,
      platform: analysisData.data.platform
    }
  };
}

// Return modified data
return { json: analysisData };
```

### Multiple Environment Support

Create separate workflows for:
- **Production** - Live analysis data
- **Development** - Test data
- **Staging** - QA validation

Each with different webhook URLs configured in AdCopySurge.

---

## 🆘 Need Help?

- **n8n Documentation**: [https://docs.n8n.io](https://docs.n8n.io)
- **n8n Community Forum**: [https://community.n8n.io](https://community.n8n.io)
- **n8n Discord**: Join for real-time help
- **AdCopySurge Support**: Contact us at support@adcopysurge.com

---

## 📚 Next Steps

Once your n8n integration is working:

1. ✅ Run several test analyses to verify data flows correctly
2. ✅ Build additional workflows for different use cases
3. ✅ Explore n8n's 400+ integrations for advanced automation
4. ✅ Set up monitoring and error notifications
5. ✅ Share workflow templates with your team
6. ✅ Contribute your workflows to the n8n community

---

## 🔗 Helpful Resources

- [n8n Workflow Templates](https://n8n.io/workflows)
- [Webhook Node Documentation](https://docs.n8n.io/integrations/builtin/core-nodes/n8n-nodes-base.webhook/)
- [n8n Expression Reference](https://docs.n8n.io/code-examples/expressions/)
- [Self-Hosting Guide](https://docs.n8n.io/hosting/)

---

**Last Updated**: January 2025  
**Integration Type**: Webhook-based  
**Difficulty**: Intermediate ⭐⭐⭐☆☆  
**Best For**: Developers and teams wanting full automation control
