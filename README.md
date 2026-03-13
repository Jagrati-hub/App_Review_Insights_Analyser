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

1. **Scrapes** 2,000 reviews from Google Play Store (Groww app)
2. **Filters** non-English reviews, removes emojis and PII
3. **Analyzes** themes using Groq LLM (llama-3.3-70b-versatile)
4. **Generates** a 250-word pulse report with top 3 themes
5. **Creates** HTML email and sends via SMTP
6. **Saves** plain text draft locally

**Processing time**: 1.5-3 minutes (optimized for 2000 reviews)

## 🏗️ Architecture

```
┌─────────────────────┐         ┌──────────────────────┐
│   Next.js Frontend  │ ◄─────► │   Flask Backend API  │
│   (Port 3000)       │  HTTP   │   (Port 5000)        │
│   Corporate Theme   │         │   REST Endpoints     │
└─────────────────────┘         └──────────────────────┘
                                          │
                                          ▼
                                 ┌────────────────────┐
                                 │  Analysis Pipeline │
                                 │  - Phase 1: Scrape │
                                 │  - Phase 3: Analyze│
                                 │  - Phase 4: Report │
                                 │  - Phase 5: Email  │
                                 │    (HTML Template) │
                                 └────────────────────┘
                                          ▲
                                          │
                                 ┌────────────────────┐
                                 │  Scheduler (Phase6)│
                                 │  Every 180 min     │
                                 │  (00:00, 03:00,    │
                                 │   06:00, 09:00,    │
                                 │   12:00, 15:00,    │
                                 │   18:00, 21:00 IST)│
                                 │  → SMTP Email      │
                                 └────────────────────┘
                                          │
                                          ▼
                                 ┌────────────────────┐
                                 │  GitHub Actions    │
                                 │  - Scheduled       │
                                 │  - Manual Trigger  │
                                 │  - Test Pipeline   │
                                 └────────────────────┘
```

### Key Components

**Frontend (Next.js)**
- Corporate-friendly blue theme with high contrast
- Responsive design for mobile and desktop
- Real-time progress tracking
- Report visualization with statistics

**Backend (Flask API)**
- RESTful endpoints for pipeline orchestration
- CORS-enabled for frontend communication
- Health checks and configuration management
- Optimized for 2000 reviews (1.5-3 min processing)

**Email System (Phase 5)**
- HTML emails with inline styles for email client compatibility
- Table-based layout for maximum compatibility
- Colorful gradient header and themed sections
- Plain text drafts saved locally (.txt)
- SMTP integration for automatic sending

**Scheduler (Phase 6)**
- Runs every 180 minutes (8 times daily)
- Fixed schedule aligned with IST timezone
- Automatic error handling and logging
- Report archiving in phase6/reports/

**GitHub Actions**
- Scheduled workflow (configurable cron)
- Manual trigger workflow
- Test pipeline workflow
- Automated cloud execution

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
├── phase5/                # Phase 5: Email Drafting & SMTP
│   ├── email_drafter.py   # Email formatting and SMTP sending
│   ├── email_template_inline.py  # HTML email template (inline styles)
│   ├── run_phase5.py      # Phase 5 execution script
│   ├── test_email.py      # Email testing utility
│   └── drafts/            # Plain text email drafts (.txt)
│
├── phase6/                # Phase 6: Automated Scheduling
│   ├── scheduler.py       # Scheduler (every 180 min, 8x daily)
│   ├── logs/              # Scheduler logs
│   │   └── scheduler.log
│   └── reports/           # Scheduled report outputs
│
├── .github/               # GitHub Actions Workflows
│   ├── workflows/
│   │   ├── scheduled-pulse-report.yml  # Scheduled workflow
│   │   ├── manual-pulse-report.yml     # Manual trigger
│   │   └── test-pipeline.yml           # Test workflow
│   ├── GITHUB_ACTIONS_GUIDE.md  # GitHub Actions setup guide
│   └── README.md          # GitHub Actions overview
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
- ✅ Scrapes up to 2000 reviews from Google Play Store (Groww app)
- ✅ Optimized batch size (150) and delay (0.5s) for faster processing
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

### Phase 5: Email Drafting & SMTP
- ✅ Professional HTML email formatting with inline styles
- ✅ Table-based layout for email client compatibility
- ✅ Colorful gradient header and themed sections
- ✅ Plain text drafts saved locally (.txt files)
- ✅ Automatic SMTP email sending (Gmail)
- ✅ Mobile-responsive email design
- ✅ Statistics display (avg rating, positive/negative breakdown)
- ✅ Theme-level statistics with review counts
- ✅ Action roadmap visualization with step-by-step format

### Phase 2: Web UI (Next.js)
- ✅ Modern, responsive interface
- ✅ Corporate-friendly blue theme with high contrast
- ✅ Configuration form with validation
- ✅ Real-time progress tracking
- ✅ Report display with themes, quotes, and actions
- ✅ Email preview
- ✅ Mobile and desktop optimized

### Phase 6: Automated Scheduling
- ✅ Automated report generation every 180 minutes (8x daily)
- ✅ Fixed schedule: 00:00, 03:00, 06:00, 09:00, 12:00, 15:00, 18:00, 21:00 IST
- ✅ Configurable recipient email
- ✅ Automatic report archiving
- ✅ Comprehensive logging (phase6/logs/scheduler.log)
- ✅ Error handling and recovery
- ✅ GitHub Actions integration for cloud execution
- ✅ Manual trigger support
- ✅ Test pipeline for validation

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

# Scraper Settings (Optimized)
SCRAPER_MAX_REVIEWS = 2000  # Reduced from 5000 for faster processing
SCRAPER_BATCH_SIZE = 150    # Reduced from 200
SCRAPER_DELAY = 0.5         # Reduced from 1.0s
SCRAPER_MIN_WORD_COUNT = 5
SCRAPER_FILTER_NON_ENGLISH = True
SCRAPER_REMOVE_EMOJIS = True

# Analysis Settings
MIN_WEEKS = 8
MAX_WEEKS = 12
MAX_THEMES = 5
REPORT_WORD_LIMIT = 250

# Email Settings
SMTP_SERVER = 'smtp.gmail.com'
SMTP_PORT = 587
SENDER_EMAIL = 'your-email@gmail.com'
SENDER_NAME = 'Groww Product Team'

# Scheduler Settings
SCHEDULER_INTERVAL_MINUTES = 180  # Run every 3 hours
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
