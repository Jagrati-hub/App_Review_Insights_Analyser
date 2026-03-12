# Play Store Review Analyzer - Complete Setup Guide

This guide will help you set up and run the complete application with both the Flask backend and Next.js frontend.

## Architecture

```
┌─────────────────────┐         ┌──────────────────────┐
│   Next.js Frontend  │ ◄─────► │   Flask Backend API  │
│   (Port 3000)       │  HTTP   │   (Port 5000)        │
└─────────────────────┘         └──────────────────────┘
                                          │
                                          ▼
                                 ┌────────────────────┐
                                 │  Analysis Pipeline │
                                 │  - Phase 1: Scrape │
                                 │  - Phase 3: Analyze│
                                 │  - Phase 4: Report │
                                 │  - Phase 5: Email  │
                                 └────────────────────┘
```

## Prerequisites

### Backend Requirements
- Python 3.9+
- pip (Python package manager)
- Virtual environment (recommended)

### Frontend Requirements
- Node.js 18+
- npm or yarn

### API Keys
- Groq API key (for LLM analysis)

## Step 1: Backend Setup

### 1.1 Create Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

### 1.2 Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 1.3 Configure Environment Variables

Create a `.env` file in the root directory:

```env
# Groq API Configuration
GROQ_API_KEY=your_groq_api_key_here

# Flask Configuration
FLASK_SECRET_KEY=your_secret_key_here
FLASK_ENV=development

# Optional: Email Configuration
RECIPIENT_EMAIL=team@example.com
```

### 1.4 Start Flask Backend

**Option A: Using Batch Script (Recommended for Windows)**
```bash
start-backend.bat
```

**Option B: Manual Start**
```bash
python phase2/ui_controller.py
```

The API will be available at `http://localhost:5000`

**API Endpoints:**
- `POST /api/analyze` - Start analysis
- `GET /api/status/<id>` - Get pipeline status
- `GET /api/report/<id>` - Get generated report
- `GET /api/config` - Get configuration
- `GET /api/health` - Health check

## Step 2: Frontend Setup

### 2.1 Navigate to Frontend Directory

```bash
cd frontend
```

### 2.2 Install Node Dependencies

```bash
npm install
# or
yarn install
```

### 2.3 Start Next.js Development Server

**Option A: Using Batch Script (Recommended for Windows)**
```bash
start-frontend.bat
```

**Option B: Manual Start**
```bash
npm run dev
# or
yarn dev
```

The frontend will be available at `http://localhost:3000`

## Quick Start: Run Both Servers

**For Windows users, use the all-in-one script:**
```bash
start-all.bat
```

This will automatically:
1. Start the Flask backend on port 5000
2. Wait 3 seconds for backend initialization
3. Start the Next.js frontend on port 3000
4. Open both servers in separate command windows

## Step 3: Using the Application

### 3.1 Access the Web Interface

Open your browser and navigate to:
```
http://localhost:3000
```

### 3.2 Configure Analysis

1. **Weeks Back**: Select 8-12 weeks
2. **Recipient Email**: Enter email address
3. Click **"Generate Report"**

### 3.3 View Progress

The application will show real-time progress:
- Scraping reviews (10%)
- Analyzing themes (40%)
- Generating report (70%)
- Drafting email (90%)
- Complete (100%)

### 3.4 Review Results

Once complete, you'll see:
- 📊 Top 3 themes with review counts
- 💬 3 user quotes
- 💡 3 action ideas
- 📧 Email draft preview

## Step 4: Automated Scheduling (Optional)

### 4.1 Start the Weekly Scheduler

The scheduler automatically generates reports every week at 1:00 PM IST.

**Using Batch Script:**
```bash
start-scheduler.bat
```

**Manual Start:**
```bash
python phase6/scheduler.py
```

### 4.2 Test the Scheduler

To test without waiting for the scheduled time:

```bash
test-scheduler.bat
```

### 4.3 Scheduler Configuration

- **Schedule**: Every week at 1:00 PM IST
- **Recipient**: manshuc12@gmail.com (fixed)
- **Analysis Window**: 10 weeks
- **Output**: `phase6/reports/`
- **Logs**: `phase6/scheduler.log`

For detailed scheduler documentation, see [phase6/SCHEDULER_GUIDE.md](phase6/SCHEDULER_GUIDE.md)

## Project Structure

```
App_Review_Insights_Analyser/
├── phase1/                 # Review Scraping & PII Filtering
├── phase2/                 # Flask REST API
├── phase3/                 # Theme Analysis (Groq LLM)
├── phase4/                 # Report Generation
├── phase5/                 # Email Drafting
├── common/                 # Shared models and config
├── frontend/               # Next.js Frontend
│   ├── app/               # Next.js pages
│   ├── public/            # Static assets
│   └── package.json       # Frontend dependencies
├── .env                   # Environment variables
├── requirements.txt       # Python dependencies
└── SETUP_GUIDE.md        # This file
```

## Configuration

### Backend Configuration (`common/config.py`)

```python
# Groq LLM Settings
GROQ_MODEL = 'llama-3.3-70b-versatile'
GROQ_TIMEOUT = 30
GROQ_MAX_RETRIES = 3

# Scraper Settings
SCRAPER_MAX_REVIEWS = 5000
SCRAPER_MIN_WORD_COUNT = 5
SCRAPER_FILTER_NON_ENGLISH = True
SCRAPER_REMOVE_EMOJIS = True

# Analysis Settings
MIN_WEEKS = 8
MAX_WEEKS = 12
MAX_THEMES = 5
REPORT_WORD_LIMIT = 250
```

### Frontend Configuration

Edit `frontend/app/page.tsx` to change the API URL:

```typescript
const API_BASE_URL = 'http://localhost:5000/api';
```

## Troubleshooting

### Backend Issues

**Problem**: `ModuleNotFoundError`
```bash
# Solution: Install missing dependencies
pip install -r requirements.txt
```

**Problem**: `GROQ_API_KEY not found`
```bash
# Solution: Add API key to .env file
echo "GROQ_API_KEY=your_key_here" >> .env
```

**Problem**: Port 5000 already in use
```bash
# Solution: Change port in phase2/ui_controller.py
app.run(debug=True, host='0.0.0.0', port=5001)
```

### Frontend Issues

**Problem**: `Cannot connect to API`
```bash
# Solution: Verify backend is running
curl http://localhost:5000/api/health
```

**Problem**: CORS errors
```bash
# Solution: Verify CORS is enabled in Flask backend
# Check phase2/ui_controller.py for CORS configuration
```

**Problem**: `npm install` fails
```bash
# Solution: Clear cache and reinstall
rm -rf node_modules package-lock.json
npm install
```

## Running in Production

### Backend (Flask)

```bash
# Install production server
pip install gunicorn

# Run with gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 phase2.ui_controller:app
```

### Frontend (Next.js)

```bash
# Build for production
cd frontend
npm run build

# Start production server
npm start
```

## Testing

### Test Backend API

```bash
# Health check
curl http://localhost:5000/api/health

# Get configuration
curl http://localhost:5000/api/config

# Start analysis (POST)
curl -X POST http://localhost:5000/api/analyze \
  -H "Content-Type: application/json" \
  -d '{"weeks_back": 10, "recipient_email": "test@example.com"}'
```

### Test Frontend

1. Open `http://localhost:3000`
2. Fill the form
3. Submit and verify progress tracking
4. Check report display

## Performance

### Expected Processing Time

- **Scraping**: 2-5 minutes (5,000 reviews)
- **Theme Analysis**: 30-60 seconds
- **Report Generation**: 10-20 seconds
- **Email Drafting**: <5 seconds
- **Total**: ~3-7 minutes

### Optimization Tips

1. **Reduce review count** in `common/config.py`
2. **Use faster Groq model** (if available)
3. **Enable caching** for repeated analyses
4. **Add background task queue** (Celery)

## Security Considerations

1. **API Keys**: Never commit `.env` file to git
2. **CORS**: Restrict origins in production
3. **Rate Limiting**: Add rate limiting to API endpoints
4. **Authentication**: Add user authentication for production
5. **Input Validation**: Already implemented in backend

## Next Steps

1. **Add Authentication**: Implement user login
2. **Database**: Store results in PostgreSQL/MongoDB
3. **Background Tasks**: Use Celery for async processing
4. **Caching**: Add Redis for caching
5. **Monitoring**: Add logging and error tracking
6. **Testing**: Add unit and integration tests
7. **Deployment**: Deploy to cloud (AWS, GCP, Azure)

## Support

For issues or questions:
1. Check this guide
2. Review error messages
3. Check browser console (frontend)
4. Check Flask logs (backend)

## License

MIT
