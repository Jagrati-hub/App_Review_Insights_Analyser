# Play Store Review Analyzer

An automated system that scrapes Google Play Store reviews for the Groww app and generates weekly pulse reports using Groq LLM. Features a Next.js frontend and Flask REST API backend.

## 🚀 Quick Start

**New to this project? Start here:**

1. **First time setup**: See [QUICK_START.md](QUICK_START.md)
2. **Detailed setup**: See [SETUP_GUIDE.md](SETUP_GUIDE.md)
3. **Startup scripts**: See [STARTUP_SCRIPTS.md](STARTUP_SCRIPTS.md)
4. **GitHub Actions**: See [.github/GITHUB_ACTIONS_GUIDE.md](.github/GITHUB_ACTIONS_GUIDE.md)

**Already set up? Just run:**
```bash
start-all.bat
```
Then open http://localhost:3000

**Want automated reports? Use GitHub Actions:**
- See [.github/README.md](.github/README.md) for setup

## 📋 What This Does

1. **Scrapes** 5,000 reviews from Google Play Store (Groww app)
2. **Filters** non-English reviews, removes emojis and PII
3. **Analyzes** themes using Groq LLM (llama-3.3-70b-versatile)
4. **Generates** a 250-word pulse report with top 3 themes
5. **Creates** an email draft ready to send

**Processing time**: 3-7 minutes

## 🏗️ Architecture

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
                                          ▲
                                          │
                                 ┌────────────────────┐
                                 │  Weekly Scheduler  │
                                 │  (Phase 6)         │
                                 │  Every Week 1PM IST│
                                 │  → manshuc12@      │
                                 │     gmail.com      │
                                 └────────────────────┘
```

## 📁 Project Structure

```
.
├── common/                 # Shared utilities and models
│   ├── models.py          # Data models used across all phases
│   ├── config.py          # Configuration management
│   └── __init__.py
│
├── phase1/                # Phase 1: Review Scraping & PII Filtering
│   ├── review_scraper.py  # Google Play Store scraper
│   ├── pii_filter.py      # PII detection and removal
│   ├── run_phase1.py      # Phase 1 execution script
│   └── phase1/output/     # Phase 1 output files
│
├── phase2/                # Phase 2: Flask REST API
│   ├── ui_controller.py   # Flask API endpoints
│   └── pipeline_orchestrator.py  # Pipeline coordinator
│
├── phase3/                # Phase 3: Groq LLM Integration
│   ├── groq_client.py     # Groq API client
│   ├── theme_analyzer.py  # Theme analysis with LLM
│   ├── run_phase3.py      # Phase 3 execution script
│   └── phase3/output/     # Theme analysis results
│
├── phase4/                # Phase 4: Report Generation
│   ├── report_generator.py  # Report generation logic
│   ├── run_phase4.py      # Phase 4 execution script
│   └── phase4/output/     # Generated reports
│
├── phase5/                # Phase 5: Email Drafting
│   ├── email_drafter.py   # Email formatting
│   ├── run_phase5.py      # Phase 5 execution script
│   └── drafts/            # Email drafts
│
├── phase6/                # Phase 6: Automated Scheduling
│   ├── scheduler.py       # Weekly pulse scheduler
│   └── reports/           # Scheduled report outputs
│
├── frontend/              # Next.js Frontend
│   ├── app/              # Next.js pages
│   │   ├── page.tsx      # Home/config page
│   │   └── report/[id]/page.tsx  # Report display
│   └── package.json      # Frontend dependencies
│
├── .env                   # Environment variables (API keys)
├── .env.example           # Environment variables template
├── requirements.txt       # Python dependencies
├── start-all.bat          # Start both servers (Windows)
├── start-backend.bat      # Start Flask backend
├── start-frontend.bat     # Start Next.js frontend
├── start-scheduler.bat    # Start weekly pulse scheduler
├── test-scheduler.bat     # Test scheduler immediately
├── test-connection.bat    # Test server connections
├── QUICK_START.md         # Quick start guide
├── SETUP_GUIDE.md         # Detailed setup guide
├── STARTUP_SCRIPTS.md     # Startup scripts documentation
└── README.md             # This file
```

## ✨ Features

### Phase 1: Review Scraping & PII Filtering
- ✅ Scrapes up to 5,000 reviews from Google Play Store (Groww app)
- ✅ Filters reviews with fewer than 5 words
- ✅ Removes non-English reviews (language detection)
- ✅ Removes emojis from review text
- ✅ Removes PII (emails, phone numbers, usernames, user IDs)

### Phase 2: Flask REST API
- ✅ RESTful API endpoints for analysis pipeline
- ✅ CORS support for Next.js frontend
- ✅ Real-time progress tracking
- ✅ Health check and configuration endpoints

### Phase 3: Groq LLM Integration
- ✅ Theme analysis using llama-3.3-70b-versatile
- ✅ Identifies top 5 themes from reviews
- ✅ Smart sampling strategy for large datasets
- ✅ Keyword-based mapping to all reviews

### Phase 4: Report Generation
- ✅ 250-word pulse reports
- ✅ Top 3 themes with review counts
- ✅ 3 diverse user quotes
- ✅ 3 AI-generated action ideas

### Phase 5: Email Drafting
- ✅ Professional email formatting
- ✅ Ready-to-send drafts
- ✅ Configurable recipients
- ✅ Email preview in UI
- ✅ Automatic SMTP email sending (Gmail)

### Phase 2: Web UI (Next.js)
- ✅ Modern, responsive interface
- ✅ Configuration form with validation
- ✅ Real-time progress tracking
- ✅ Report display with themes, quotes, and actions
- ✅ Email preview

### Phase 6: Automated Scheduling
- ✅ Weekly automated report generation
- ✅ Configurable schedule (default: every 5 minutes)
- ✅ Fixed recipient email (manshuc12@gmail.com)
- ✅ Automatic report archiving
- ✅ Logging and error handling
- ✅ GitHub Actions integration for cloud execution

## 🛠️ Technology Stack

**Backend:**
- Python 3.9+
- Flask (REST API)
- Groq LLM (llama-3.3-70b-versatile)
- google-play-scraper
- langdetect (language detection)

**Frontend:**
- Next.js 14
- TypeScript
- Tailwind CSS
- React

## 📖 Documentation

- **[QUICK_START.md](QUICK_START.md)** - Get started in 3 steps
- **[SETUP_GUIDE.md](SETUP_GUIDE.md)** - Detailed setup and configuration
- **[STARTUP_SCRIPTS.md](STARTUP_SCRIPTS.md)** - Batch script documentation
- **[.kiro/specs/play-store-review-analyzer/](.kiro/specs/play-store-review-analyzer/)** - Project specifications

## 🔧 Configuration

Key settings in `common/config.py`:

```python
# Groq LLM Settings
GROQ_MODEL = 'llama-3.3-70b-versatile'

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

## 🧪 Testing

Test the servers:
```bash
test-connection.bat
```

Test the API:
```bash
# Health check
curl http://localhost:5000/api/health

# Get configuration
curl http://localhost:5000/api/config
```

## 📊 Sample Output

**Themes Identified:**
1. High Brokerage Charges (783 reviews)
2. Technical Issues (767 reviews)
3. Ease of Use (717 reviews)

**User Quote Example:**
> "The app is very user-friendly and easy to navigate. Great for beginners!" - ⭐⭐⭐⭐⭐

**Action Idea Example:**
> Consider implementing a tiered pricing structure to address concerns about brokerage charges while maintaining profitability.

## 🚀 Deployment

For production deployment, see [SETUP_GUIDE.md](SETUP_GUIDE.md#running-in-production)

## 📝 License

MIT
