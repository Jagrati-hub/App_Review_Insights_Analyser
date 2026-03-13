# Streamlit Deployment Guide

## Overview

This guide explains how to deploy the Play Store Review Analyzer as a Streamlit app. The Streamlit version combines both frontend and backend into a single Python application.

## Prerequisites

- Python 3.9 or higher
- Groq API key
- Gmail account with App Password (for email functionality)

## Local Development

### 1. Install Dependencies

```bash
pip install -r requirements-streamlit.txt
```

### 2. Configure Secrets

Create `.streamlit/secrets.toml` from the example:

```bash
cp .streamlit/secrets.toml.example .streamlit/secrets.toml
```

Edit `.streamlit/secrets.toml` and add your credentials:

```toml
[groq]
api_key = "your-groq-api-key-here"

[email]
smtp_server = "smtp.gmail.com"
smtp_port = 587
smtp_username = "your-email@gmail.com"
smtp_password = "your-gmail-app-password"
sender_email = "your-email@gmail.com"
sender_name = "Groww Product Team"

[app]
recipient_email = "default-recipient@gmail.com"
```

### 3. Run Locally

```bash
streamlit run streamlit_app.py
```

The app will open in your browser at `http://localhost:8501`

## Streamlit Cloud Deployment

### 1. Prepare Repository

Ensure these files are in your repository:
- `streamlit_app.py` (main app file)
- `requirements-streamlit.txt` (dependencies)
- `.streamlit/config.toml` (theme configuration)
- All phase folders (phase1, phase3, phase4, phase5)
- `common/` folder (models and config)

### 2. Push to GitHub

```bash
git add streamlit_app.py requirements-streamlit.txt .streamlit/
git commit -m "Add Streamlit deployment files"
git push origin main
```

### 3. Deploy on Streamlit Cloud

1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Sign in with GitHub
3. Click "New app"
4. Select your repository: `Jagrati-hub/App_Review_Insights_Analyser`
5. Set main file path: `streamlit_app.py`
6. Click "Advanced settings"
7. Set Python version: `3.9`
8. Add secrets (copy from your local `.streamlit/secrets.toml`)
9. Click "Deploy"

### 4. Configure Secrets in Streamlit Cloud

In the Streamlit Cloud dashboard:

1. Go to your app settings
2. Click "Secrets"
3. Paste your secrets in TOML format:

```toml
[groq]
api_key = "your-groq-api-key-here"

[email]
smtp_server = "smtp.gmail.com"
smtp_port = 587
smtp_username = "your-email@gmail.com"
smtp_password = "your-gmail-app-password"
sender_email = "your-email@gmail.com"
sender_name = "Groww Product Team"

[app]
recipient_email = "default-recipient@gmail.com"
```

4. Click "Save"

## Environment Variables

The Streamlit app reads configuration from:

1. **Streamlit Secrets** (`.streamlit/secrets.toml` locally, or Streamlit Cloud secrets)
2. **Environment Variables** (fallback)
3. **Default Values** (in `common/config.py`)

### Priority Order:
1. Streamlit secrets (highest priority)
2. Environment variables
3. Default values (lowest priority)

## Features in Streamlit Version

### Included:
- ✅ Review scraping from Google Play Store
- ✅ PII filtering
- ✅ Theme analysis with Groq LLM
- ✅ Report generation
- ✅ Email draft creation
- ✅ Interactive UI with progress tracking
- ✅ Report visualization
- ✅ Statistics display
- ✅ Email preview
- ✅ Download email draft

### Not Included (by design):
- ❌ Automatic email sending (disabled in Streamlit for security)
- ❌ Scheduler (use Streamlit Cloud's scheduled runs instead)
- ❌ Next.js frontend (replaced by Streamlit UI)
- ❌ Flask API (not needed in Streamlit)

## Streamlit Cloud Scheduled Runs

To run analysis automatically:

1. In Streamlit Cloud dashboard, go to app settings
2. Enable "Scheduled runs"
3. Set schedule (e.g., daily at 9 AM)
4. The app will run automatically at scheduled times

## Configuration

### Analysis Settings

Configure in the sidebar:
- **Weeks to analyze**: 8-12 weeks
- **Recipient email**: Email address for reports

### System Settings

Edit `common/config.py` for:
- Max reviews to scrape
- Groq model selection
- Report word limit
- Theme count

## Troubleshooting

### Issue: "Module not found" error

**Solution**: Ensure all dependencies are in `requirements-streamlit.txt`

```bash
pip install -r requirements-streamlit.txt
```

### Issue: "Groq API key not found"

**Solution**: Add Groq API key to secrets:

Local: `.streamlit/secrets.toml`
```toml
[groq]
api_key = "your-key-here"
```

Cloud: App Settings → Secrets

### Issue: Slow performance

**Solution**: 
- Reduce `SCRAPER_MAX_REVIEWS` in `common/config.py`
- Use Streamlit Cloud's higher-tier plans for more resources

### Issue: Memory errors

**Solution**:
- Reduce batch size in scraper
- Process fewer reviews
- Upgrade Streamlit Cloud plan

## Performance Optimization

### For Faster Processing:

1. **Reduce review count**:
   ```python
   # In common/config.py
   SCRAPER_MAX_REVIEWS = 1000  # Instead of 2000
   ```

2. **Adjust batch size**:
   ```python
   SCRAPER_BATCH_SIZE = 100  # Instead of 150
   ```

3. **Use caching**:
   ```python
   @st.cache_data
   def expensive_function():
       # Your code here
   ```

## Monitoring

### Streamlit Cloud Logs

View logs in Streamlit Cloud dashboard:
1. Go to your app
2. Click "Manage app"
3. View "Logs" tab

### Local Logs

When running locally, logs appear in terminal:
```bash
streamlit run streamlit_app.py
```

## Security Best Practices

1. **Never commit secrets**:
   - Add `.streamlit/secrets.toml` to `.gitignore`
   - Use Streamlit Cloud secrets for deployment

2. **Use App Passwords**:
   - For Gmail, use App Passwords instead of account password
   - Enable 2FA on your Google account

3. **Limit API access**:
   - Restrict Groq API key usage
   - Monitor API usage regularly

4. **Validate inputs**:
   - Email validation is built-in
   - Week range is restricted to 8-12

## Cost Considerations

### Streamlit Cloud:
- **Free tier**: 1 app, limited resources
- **Paid tiers**: More apps, better performance

### Groq API:
- Check current pricing at [groq.com](https://groq.com)
- Monitor usage to avoid unexpected costs

### Google Play Scraper:
- Free to use
- Rate limiting may apply

## Support

For issues or questions:
1. Check [Streamlit documentation](https://docs.streamlit.io)
2. Review [Groq documentation](https://console.groq.com/docs)
3. Open an issue on GitHub

## Next Steps

After deployment:
1. Test the app with a small dataset
2. Monitor performance and logs
3. Adjust configuration as needed
4. Set up scheduled runs if desired
5. Share the app URL with your team

## App URL

After deployment, your app will be available at:
```
https://share.streamlit.io/[username]/[repo-name]/[branch]/streamlit_app.py
```

Example:
```
https://share.streamlit.io/jagrati-hub/app_review_insights_analyser/main/streamlit_app.py
```

## Updating the App

To update the deployed app:

```bash
git add .
git commit -m "Update app"
git push origin main
```

Streamlit Cloud will automatically redeploy your app.

## Conclusion

The Streamlit version provides a simpler deployment option compared to the Next.js + Flask architecture. It's ideal for:
- Quick prototypes
- Internal tools
- Teams familiar with Python
- Scenarios where a full web stack is overkill

For production deployments with high traffic, consider the original Next.js + Flask architecture.
