# 📞 Exotel Call-Slack Integration

Automated call processing system that integrates Exotel calls with Slack notifications. This system automatically processes completed calls, transcribes audio, analyzes concerns, and posts summaries to Slack channels.

## ✨ Features

- **🔄 Automatic Processing**: Built-in scheduler processes calls every 5 minutes
- **🎧 Audio Transcription**: Uses Deepgram for high-quality transcription
- **📊 Smart Analysis**: AI-powered concern detection and mood analysis
- **💬 Slack Integration**: Automatic posting to Slack with rich formatting
- **📁 File Upload**: Automatic upload of call recordings to Slack
- **🚀 Cloud Ready**: Deploy to Render with zero configuration
- **🔧 No Zapier Required**: Completely self-contained solution

## 🏗️ Architecture

```
Exotel API → Render Service → Slack API
     ↓            ↓            ↓
  Call Data → Processing → Notifications
  Recordings → Transcription → File Uploads
  Webhooks → Analysis → Messages
```

## 🚀 Quick Start

### Prerequisites

- Python 3.7+
- Render account
- Exotel API credentials
- Slack API credentials
- Deepgram API key

### Local Development

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd exotel-call-slack-integration
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your actual credentials
   ```

4. **Run locally**
   ```bash
   python app.py
   ```

5. **Test endpoints**
   ```bash
   # Health check
   curl http://localhost:5000/
   
   # Manual trigger
   curl -X POST http://localhost:5000/trigger
   ```

### Render Deployment

1. **Use the deployment helper**
   ```bash
   python deploy_to_render.py
   ```

2. **Follow the instructions** to deploy to Render

3. **Test your deployment**
   ```bash
   python test_render_deployment.py https://your-app.onrender.com
   ```

## 📋 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Health check and service info |
| `/status` | GET | Detailed service status |
| `/scheduler` | GET | Scheduler status and jobs |
| `/trigger` | POST/GET | Manual trigger for processing |
| `/logs` | GET | Log information |

## ⚙️ Configuration

### Environment Variables

```bash
# Exotel Configuration
EXOTEL_SID=your_exotel_sid
EXOTEL_API_KEY=your_exotel_api_key
EXOTEL_API_TOKEN=your_exotel_api_token

# Slack Configuration
SLACK_BOT_TOKEN=xoxb-your-slack-bot-token
SLACK_CHANNEL=your-slack-channel-id
SLACK_WEBHOOK=https://hooks.slack.com/services/your/webhook/url

# Optional: Deepgram API
DEEPGRAM_API_KEY=your_deepgram_api_key
```

### Scheduler Configuration

The built-in scheduler runs every 5 minutes by default. To modify:

```python
# In app.py, change the interval
scheduler.add_job(
    func=scheduled_call_processing,
    trigger=IntervalTrigger(minutes=5),  # Change this
    id='call_processing_job',
    name='Call Processing Job',
    replace_existing=True
)
```

## 🔧 Customization

### Adding New Concern Types

Edit the `analyze_concern` method in `app.py`:

```python
concerns = {
    'Background Verification': ['background verification', 'background check'],
    'Document Submission': ['document submission', 'documents'],
    'Billing Issue': ['bill', 'payment', 'charge'],
    'Technical Problem': ['not working', 'error', 'broken'],
    'Your New Concern': ['keyword1', 'keyword2', 'keyword3']
}
```

### Customizing Slack Messages

Modify the `post_to_slack` method to change message format:

```python
message = f"""🆕 Your Custom Message Format
📞 Support: {support_number}
📱 Customer: {customer_number}
# Add your custom fields here
"""
```

## 📊 Monitoring

### Health Checks

- **Basic**: `GET /` - Service status
- **Detailed**: `GET /status` - Full service information
- **Scheduler**: `GET /scheduler` - Job status and next run times

### Logs

- Check Render dashboard for application logs
- Use `/logs` endpoint for log information
- Monitor Slack for successful postings

## 🚨 Troubleshooting

### Common Issues

1. **Service Not Starting**
   - Check environment variables
   - Verify all dependencies are installed
   - Check Render logs

2. **Scheduler Not Running**
   - Verify service is not sleeping (free tier)
   - Check `/scheduler` endpoint
   - Upgrade to paid plan for always-on service

3. **API Errors**
   - Verify API credentials
   - Check API rate limits
   - Monitor error logs

### Debug Commands

```bash
# Test locally
python app.py

# Check dependencies
pip install -r requirements.txt

# Test specific endpoint
curl -X POST http://localhost:5000/trigger
```

## 📈 Performance

### Optimization Tips

1. **Database Integration**: Add database for call tracking
2. **Caching**: Implement caching for API responses
3. **Worker Scaling**: Increase Gunicorn workers for high volume
4. **Monitoring**: Add comprehensive monitoring and alerting

### Scaling

- **Low Volume**: Free Render tier (750 hours/month)
- **Medium Volume**: Paid Render tier ($7/month)
- **High Volume**: Consider dedicated servers or Kubernetes

## 🔒 Security

- Never commit API keys to code
- Use environment variables for all secrets
- Enable HTTPS (provided by Render)
- Implement rate limiting for production
- Monitor and log all activities

## 📞 Support

- **Documentation**: See `RENDER_DEPLOYMENT_NO_ZAPIER.md`
- **Issues**: Create GitHub issues for bugs
- **Render Support**: [render.com/docs](https://render.com/docs)
- **Slack API**: [api.slack.com](https://api.slack.com)

## 🎯 Roadmap

- [ ] Database integration for call tracking
- [ ] Webhook support for real-time processing
- [ ] Advanced analytics and reporting
- [ ] Multi-channel support (Teams, Discord)
- [ ] Custom AI models for analysis
- [ ] Mobile app for monitoring

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

---

**Made with ❤️ for automated call processing**
