# 🚀 RENDER DEPLOYMENT CHECKLIST

## ✅ Files Ready
- [x] app.py - Main Flask application with scheduler
- [x] requirements.txt - Python dependencies
- [x] Procfile - Render deployment configuration
- [x] render.yaml - Render service configuration
- [x] .env.example - Environment variables template

## 📋 Step-by-Step Deployment

### Step 1: Create GitHub Repository

1. **Go to GitHub.com** and sign in
2. **Click "New repository"** (green button)
3. **Repository name**: `exotel-call-processor`
4. **Description**: `Exotel Call-Slack Integration with Built-in Scheduler`
5. **Make it Public** (or Private if you prefer)
6. **Click "Create repository"**

### Step 2: Upload Files to GitHub

1. **Click "uploading an existing file"** (or drag and drop)
2. **Upload these files**:
   - `app.py`
   - `requirements.txt`
   - `Procfile`
   - `render.yaml`
   - `README.md`
   - `.env.example`
3. **Commit message**: `Initial deployment files`
4. **Click "Commit changes"**

### Step 3: Deploy on Render

1. **Go to https://render.com**
2. **Sign up/Login** (use GitHub account)
3. **Click "New +"** → **"Web Service"**
4. **Connect GitHub** and select your repository
5. **Configure service**:
   - **Name**: `exotel-call-processor`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app --bind 0.0.0.0:$PORT --workers 1 --timeout 120`
6. **Click "Create Web Service"**

### Step 4: Set Environment Variables

In Render dashboard, go to **Environment** tab and add:

```
EXOTEL_SID=abc6862
EXOTEL_API_KEY=119f006d2b474e28bb0f8cf0c50d7aa832730aef0cd962e8
EXOTEL_API_TOKEN=5b6e0ba111cc82717ffa89cc376d4a6d8e98aff852d03258
SLACK_BOT_TOKEN=xoxb-9603666278855-9651417565664-e3ojaluTEZRHumWwXwwLSl5k
SLACK_CHANNEL=C09K19DFXT2
SLACK_WEBHOOK=https://hooks.slack.com/services/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
```

### Step 5: Test Your Deployment

Once deployed, test these endpoints:

1. **Health Check**: `https://your-app-name.onrender.com/`
2. **Status**: `https://your-app-name.onrender.com/status`
3. **Scheduler**: `https://your-app-name.onrender.com/scheduler`
4. **Manual Trigger**: `https://your-app-name.onrender.com/trigger`

### Step 6: Monitor Your Service

- **Check Render logs** for any errors
- **Monitor Slack** for incoming call summaries
- **Use health endpoints** for monitoring

## 🔧 Quick Test Commands

```bash
# Test health check
curl https://your-app-name.onrender.com/

# Test status
curl https://your-app-name.onrender.com/status

# Test scheduler
curl https://your-app-name.onrender.com/scheduler

# Manual trigger
curl -X POST https://your-app-name.onrender.com/trigger
```

## ⚠️ Important Notes

1. **Free Tier**: Service sleeps after 15 minutes of inactivity
2. **Paid Tier**: $7/month for always-on service
3. **Environment Variables**: Must be set in Render dashboard
4. **Logs**: Check Render dashboard for application logs

## 🎯 What Happens Next

Your service will automatically:
- ✅ Check for new calls every 5 minutes
- ✅ Process completed calls with recordings
- ✅ Transcribe audio using Deepgram
- ✅ Upload recordings to Slack
- ✅ Post formatted summaries to Slack
- ✅ Track processed calls to avoid duplicates

## 🆘 Troubleshooting

### Service Not Starting
- Check environment variables are set
- Verify all files are uploaded to GitHub
- Check Render logs for errors

### Scheduler Not Running
- Check if service is sleeping (free tier)
- Verify `/scheduler` endpoint shows active jobs
- Upgrade to paid plan for always-on service

### API Errors
- Verify Exotel API credentials
- Check Slack webhook URL
- Monitor error logs

## 📞 Support

- **Render Docs**: https://render.com/docs
- **GitHub Issues**: Create issue in your repository
- **Slack API**: https://api.slack.com

---

**Ready to deploy? Follow the steps above!** 🚀
