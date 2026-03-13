# Play Store Review Analyzer - Streamlit Version

A unified Streamlit application that combines frontend and backend for analyzing Google Play Store reviews.

## 🚀 Quick Start

### Local Development

1. **Install dependencies**:
   ```bash
   pip install -r requirements-streamlit.txt
   ```

2. **Configure secrets**:
   ```bash
   cp .streamlit/secrets.toml.example .streamlit/secrets.toml
   ```
   
   Edit `.streamlit/secrets.toml` with your credentials.

3. **Run the app**:
   ```bash
   streamlit run streamlit_app.py
   ```
   
   Or on Windows:
   ```bash
   run-streamlit.bat
   ```

4. **Open in browser**:
   Navigate to `http://localhost:8501`

## 🌐 Deploy to Streamlit Cloud

### Prerequisites
- GitHub account
- Groq API key
- Gmail account with App Password

### Steps

1. **Push to GitHub**:
   ```bash
   git add streamlit_app.py requirements-streamlit.txt .streamlit/
   git commit -m "Add Streamlit deployment"
   git push origin main
   ```

2. **Deploy on Streamlit Cloud**:
   - Go to [share.streamlit.io](https://share.streamlit.io)
   - Sign in with GitHub
   - Click "New app"
   - Select repository: `Jagrati-hub/App_Review_Insights_Analyser`
   - Main file: `streamlit_app.py`
   - Python version: `3.9`

3. **Add secrets**:
   In Streamlit Cloud app settings → Secrets:
   ```toml
   [groq]
   api_key = "your-groq-api-key"
   
   [email]
   smtp_server = "smtp.gmail.com"
   smtp_port = 587
   smtp_username = "your-email@gmail.com"
   smtp_password = "your-app-password"
   sender_email = "your-email@gmail.com"
   sender_name = "Groww Product Team"
   
   [app]
   recipient_email = "default@gmail.com"
   ```

4. **Deploy**: Click "Deploy" and wait for deployment to complete

## 📋 Features

- ✅ Interactive web interface
- ✅ Real-time progress tracking
- ✅ Review scraping from Google Play Store
- ✅ AI-powered theme analysis
- ✅ Automated report generation
- ✅ Email draft creation
- ✅ Statistics visualization
- ✅ Download reports

## 🎨 UI Features

- Corporate-friendly blue theme
- Responsive design
- Progress indicators
- Interactive charts
- Email preview
- Download functionality

## ⚙️ Configuration

### In Sidebar:
- **Weeks to analyze**: 8-12 weeks
- **Recipient email**: Email for reports

### In Code (`common/config.py`):
- Max reviews: 2000
- Groq model: llama-3.3-70b-versatile
- Report word limit: 250
- Max themes: 5

## 📊 How It Works

1. **Configure**: Set analysis parameters in sidebar
2. **Start**: Click "Start Analysis" button
3. **Wait**: Processing takes 1.5-3 minutes
4. **Review**: View generated report with themes, quotes, and actions
5. **Download**: Get email draft as text file

## 🔒 Security

- Secrets stored in `.streamlit/secrets.toml` (not committed)
- Streamlit Cloud secrets for deployment
- Gmail App Passwords for email
- No hardcoded credentials

## 📖 Documentation

- **[STREAMLIT_DEPLOYMENT_GUIDE.md](STREAMLIT_DEPLOYMENT_GUIDE.md)** - Complete deployment guide
- **[README.md](README.md)** - Original Next.js + Flask documentation

## 🆚 Streamlit vs Next.js+Flask

### Streamlit Version (This)
- ✅ Single Python file
- ✅ Easier deployment
- ✅ No separate frontend/backend
- ✅ Built-in UI components
- ❌ Less customizable UI
- ❌ Python-only

### Next.js + Flask Version (Original)
- ✅ Fully customizable UI
- ✅ Separate frontend/backend
- ✅ Production-ready architecture
- ✅ Better for high traffic
- ❌ More complex deployment
- ❌ Requires Node.js + Python

## 🐛 Troubleshooting

### "Module not found"
```bash
pip install -r requirements-streamlit.txt
```

### "Groq API key not found"
Add to `.streamlit/secrets.toml`:
```toml
[groq]
api_key = "your-key-here"
```

### Slow performance
Reduce `SCRAPER_MAX_REVIEWS` in `common/config.py`

## 📞 Support

- GitHub Issues: [Report bugs](https://github.com/Jagrati-hub/App_Review_Insights_Analyser/issues)
- Documentation: See `STREAMLIT_DEPLOYMENT_GUIDE.md`

## 📄 License

MIT

## 🙏 Acknowledgments

- Streamlit for the framework
- Groq for LLM API
- Google Play Scraper library
