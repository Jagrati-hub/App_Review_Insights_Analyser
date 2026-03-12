# Quick Start Guide

Get the Play Store Review Analyzer running in 3 simple steps!

## Prerequisites Check

Before starting, ensure you have:
- ✅ Python 3.9+ installed
- ✅ Node.js 18+ installed
- ✅ Groq API key (get one at https://console.groq.com/)

## Step 1: First Time Setup (5 minutes)

Run these commands once:

```bash
# 1. Install Python dependencies
pip install -r requirements.txt

# 2. Install Node.js dependencies
cd frontend
npm install
cd ..

# 3. Configure API key
# Copy .env.example to .env and add your GROQ_API_KEY
copy .env.example .env
# Then edit .env and add: GROQ_API_KEY=your_key_here
```

## Step 2: Start the Application

**Option A: One-Click Start (Recommended)**
```bash
start-all.bat
```

**Option B: Manual Start**

Terminal 1 (Backend):
```bash
start-backend.bat
```

Terminal 2 (Frontend):
```bash
start-frontend.bat
```

## Step 3: Use the Application

1. Open your browser to: **http://localhost:3000**
2. Configure the analysis:
   - Select weeks back (8-12)
   - Enter recipient email
3. Click **"Generate Report"**
4. Wait 3-7 minutes for analysis
5. View results and email draft

## Optional: Automated Weekly Reports

Start the scheduler to automatically generate reports every week at 1:00 PM IST:

```bash
start-scheduler.bat
```

Reports will be sent to: manshuc12@gmail.com

Test the scheduler immediately:
```bash
test-scheduler.bat
```

## What You'll Get

📊 **Top 3 Themes** - Most discussed topics in reviews
💬 **User Quotes** - Real user feedback examples
💡 **Action Ideas** - AI-generated recommendations
📧 **Email Draft** - Ready-to-send summary

## Troubleshooting

### Servers Not Starting?

**Test the connection:**
```bash
test-connection.bat
```

**Check if ports are in use:**
```bash
netstat -ano | findstr :5000
netstat -ano | findstr :3000
```

### API Key Issues?

Make sure your `.env` file contains:
```
GROQ_API_KEY=your_actual_key_here
```

### Still Having Issues?

1. Check `SETUP_GUIDE.md` for detailed instructions
2. Check `STARTUP_SCRIPTS.md` for script documentation
3. Review error messages in the command windows

## Stopping the Application

Press `Ctrl+C` in each command window, or close the windows.

## Next Steps

- Read `SETUP_GUIDE.md` for detailed configuration
- Read `STARTUP_SCRIPTS.md` for script documentation
- Check `.kiro/specs/play-store-review-analyzer/` for project specs

## Support

For detailed documentation:
- **Setup**: `SETUP_GUIDE.md`
- **Scripts**: `STARTUP_SCRIPTS.md`
- **Project Specs**: `.kiro/specs/play-store-review-analyzer/`

---

**Ready to analyze reviews? Run `start-all.bat` and open http://localhost:3000**
