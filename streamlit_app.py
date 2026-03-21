"""
Streamlit App for Play Store Review Analyzer
Combines frontend and backend in a single Streamlit application
"""

import streamlit as st
import sys
import os
from datetime import datetime, timedelta
import json
from pathlib import Path
import time

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from phase1.review_scraper import ReviewScraper
from phase1.pii_filter import PIIFilter
from phase3.theme_analyzer import ThemeAnalyzer
from phase4.report_generator import ReportGenerator
from phase5.email_drafter import EmailDrafter
from common.config import Config
from common.models import AnalysisRequest, ScraperConfig, GroqConfig

# Page configuration
st.set_page_config(
    page_title="Play Store Review Analyzer",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Modern dark SaaS theme CSS
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

    /* ── Base ── */
    html, body, .stApp {
        font-family: 'Inter', sans-serif !important;
        background: #0a0f1e !important;
        color: #e2e8f0 !important;
    }
    .main { background: #0a0f1e !important; }
    section[data-testid="stAppViewContainer"] { background: #0a0f1e !important; }
    .main .block-container {
        padding: 2rem 3rem !important;
        max-width: 1200px;
        background: transparent !important;
    }

    /* ── Transparent containers ── */
    .element-container, .stMarkdown,
    div[data-testid="stVerticalBlock"],
    div[data-testid="stVerticalBlock"] > div,
    div[data-testid="stHorizontalBlock"],
    div[data-testid="column"],
    .stApp > div,
    .stApp > header + div { background: transparent !important; }

    /* ── Hide sidebar ── */
    [data-testid="stSidebar"] { display: none; }

    /* ── Typography ── */
    h1 {
        color: #f8fafc !important;
        font-size: 2.4rem !important;
        font-weight: 800 !important;
        letter-spacing: -0.8px;
        line-height: 1.2;
        margin-bottom: 0.4rem !important;
        padding-bottom: 0 !important;
        border-bottom: none !important;
        text-shadow: none !important;
    }
    h2 {
        color: #f1f5f9 !important;
        font-size: 1.5rem !important;
        font-weight: 700 !important;
        letter-spacing: -0.4px;
        margin-top: 2rem !important;
        margin-bottom: 1rem !important;
        text-shadow: none !important;
    }
    h3 {
        color: #93c5fd !important;
        font-size: 1.1rem !important;
        font-weight: 600 !important;
        letter-spacing: -0.2px;
    }
    h4 { color: #93c5fd !important; font-weight: 600 !important; }
    p, span, div, label { color: #cbd5e1 !important; font-weight: 400 !important; }
    li { color: #94a3b8 !important; line-height: 1.8 !important; }
    .stMarkdown, .stText { color: #cbd5e1 !important; }

    /* ── Dividers ── */
    hr { border: none; border-top: 1px solid #1e293b; margin: 2rem 0; }

    /* ── Buttons ── */
    .stButton>button {
        background: #2563eb !important;
        color: #ffffff !important;
        border: none !important;
        padding: 0.75rem 2rem !important;
        font-size: 0.95rem !important;
        font-weight: 600 !important;
        border-radius: 8px !important;
        width: 100%;
        letter-spacing: 0.3px;
        box-shadow: 0 4px 14px rgba(37, 99, 235, 0.35);
        transition: all 0.2s ease;
        text-transform: none !important;
    }
    .stButton>button:hover {
        background: #1d4ed8 !important;
        box-shadow: 0 6px 20px rgba(37, 99, 235, 0.5);
        transform: translateY(-1px);
    }

    /* ── Inputs ── */
    .stTextInput>div>div>input,
    .stNumberInput>div>div>input,
    .stSelectbox>div>div>select {
        background: #111827 !important;
        color: #f1f5f9 !important;
        border: 1px solid #1e293b !important;
        border-radius: 8px !important;
        font-size: 0.95rem !important;
        font-weight: 400 !important;
    }
    .stTextInput>div>div>input:focus,
    .stNumberInput>div>div>input:focus {
        border-color: #3b82f6 !important;
        box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.15) !important;
    }
    .stTextInput>label, .stNumberInput>label,
    .stSelectbox>label, .stSlider>label {
        color: #94a3b8 !important;
        font-size: 0.85rem !important;
        font-weight: 500 !important;
        text-transform: uppercase;
        letter-spacing: 0.6px;
        text-shadow: none !important;
    }

    /* ── Slider ── */
    .stSlider>div>div>div>div { background: #3b82f6 !important; }
    .stSlider>div>div>div { background: #1e293b !important; }

    /* Slider value numbers - make them visible */
    .stSlider [data-testid="stTickBarMin"],
    .stSlider [data-testid="stTickBarMax"] {
        color: #94a3b8 !important;
        font-size: 0.82rem !important;
        font-weight: 500 !important;
    }
    .stSlider [data-testid="stThumbValue"],
    .stSlider output,
    .stSlider div[data-testid="stSlider"] p,
    .stSlider .st-emotion-cache-1dp5vir,
    .stSlider span {
        color: #f1f5f9 !important;
        font-weight: 600 !important;
        font-size: 0.9rem !important;
    }
    /* Current value bubble */
    .stSlider [role="slider"] {
        background: #3b82f6 !important;
        border: 2px solid #60a5fa !important;
    }
    /* Tick/range labels */
    .stSlider .st-emotion-cache-1inwz65,
    .stSlider .st-emotion-cache-13ln4jf {
        color: #94a3b8 !important;
        font-size: 0.82rem !important;
    }

    /* ── Metrics ── */
    [data-testid="stMetric"] {
        background: #111827;
        border: 1px solid #1e293b;
        border-radius: 12px;
        padding: 1.25rem 1.5rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.4);
        transition: border-color 0.2s;
    }
    [data-testid="stMetric"]:hover { border-color: #3b82f6; }
    [data-testid="stMetricValue"] {
        color: #60a5fa !important;
        font-size: 2rem !important;
        font-weight: 700 !important;
        text-shadow: none !important;
    }
    [data-testid="stMetricLabel"] {
        color: #64748b !important;
        font-size: 0.78rem !important;
        font-weight: 500 !important;
        text-transform: uppercase;
        letter-spacing: 0.8px;
        text-shadow: none !important;
    }

    /* ── Alerts / Info / Success / Error ── */
    .stAlert, .stInfo, .stSuccess, .stError, .stWarning {
        border-radius: 10px !important;
        backdrop-filter: none !important;
    }
    .stInfo {
        background: #0f172a !important;
        border: 1px solid #1e3a5f !important;
        border-left: 3px solid #3b82f6 !important;
    }
    .stInfo p, .stInfo div, .stInfo span, .stInfo li { color: #93c5fd !important; }
    .stSuccess {
        background: #052e16 !important;
        border: 1px solid #14532d !important;
        border-left: 3px solid #22c55e !important;
    }
    .stSuccess p, .stSuccess div, .stSuccess span { color: #86efac !important; }
    .stError {
        background: #1c0a0a !important;
        border: 1px solid #450a0a !important;
        border-left: 3px solid #ef4444 !important;
    }
    .stError p, .stError div, .stError span { color: #fca5a5 !important; }

    /* ── Expanders ── */
    .streamlit-expanderHeader {
        background: #111827 !important;
        border: 1px solid #1e293b !important;
        border-radius: 10px !important;
        color: #e2e8f0 !important;
        font-weight: 600 !important;
        font-size: 0.95rem !important;
        padding: 1rem 1.25rem !important;
        transition: border-color 0.2s, background 0.2s;
        box-shadow: none !important;
        backdrop-filter: none !important;
    }
    .streamlit-expanderHeader:hover {
        border-color: #3b82f6 !important;
        background: #0f172a !important;
        box-shadow: none !important;
    }
    .streamlit-expanderContent {
        background: #0d1424 !important;
        border: 1px solid #1e293b !important;
        border-top: none !important;
        border-radius: 0 0 10px 10px !important;
        padding: 1.25rem !important;
        backdrop-filter: none !important;
    }
    .streamlit-expanderContent p,
    .streamlit-expanderContent div,
    .streamlit-expanderContent span {
        color: #94a3b8 !important;
        font-size: 0.95rem !important;
        line-height: 1.75 !important;
    }

    /* ── Progress bar ── */
    .stProgress>div>div>div>div {
        background: linear-gradient(90deg, #2563eb, #38bdf8) !important;
        border-radius: 4px;
    }
    .stProgress>div>div>div { background: #1e293b !important; border-radius: 4px; }

    /* ── Text area ── */
    .stTextArea>div>div>textarea {
        background: #111827 !important;
        color: #e2e8f0 !important;
        border: 1px solid #1e293b !important;
        border-radius: 8px !important;
        font-family: 'JetBrains Mono', 'Courier New', monospace !important;
        font-size: 0.85rem !important;
        backdrop-filter: none !important;
    }

    /* ── Download button ── */
    .stDownloadButton>button {
        background: #0f766e !important;
        color: #ffffff !important;
        border: none !important;
        font-weight: 600 !important;
        border-radius: 8px !important;
        padding: 0.6rem 1.25rem !important;
        box-shadow: 0 4px 12px rgba(15, 118, 110, 0.3);
    }

    /* ── Caption ── */
    .stCaption { color: #475569 !important; font-size: 0.8rem !important; }

    /* ── Subheader ── */
    .stSubheader {
        color: #f1f5f9 !important;
        font-size: 1.2rem !important;
        font-weight: 700 !important;
        letter-spacing: -0.3px;
        text-shadow: none !important;
    }

    /* ── Spacing ── */
    .block-container { padding-top: 1.5rem; padding-bottom: 2rem; }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'analysis_complete' not in st.session_state:
    st.session_state.analysis_complete = False
if 'report_data' not in st.session_state:
    st.session_state.report_data = None
if 'email_content' not in st.session_state:
    st.session_state.email_content = None

def run_analysis(weeks_back: int, recipient_email: str):
    """Run the complete analysis pipeline"""
    
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    try:
        # Phase 1: Scrape Reviews
        status_text.text("📥 Phase 1: Scraping reviews from Google Play Store...")
        progress_bar.progress(5)
        
        # Create scraper config
        scraper_config = ScraperConfig(
            app_id=Config.APP_ID,
            language=Config.SCRAPER_LANGUAGE,
            country=Config.SCRAPER_COUNTRY,
            batch_size=Config.SCRAPER_BATCH_SIZE,
            delay_between_batches=Config.SCRAPER_DELAY,
            max_reviews=Config.SCRAPER_MAX_REVIEWS,
            min_word_count=Config.SCRAPER_MIN_WORD_COUNT,
            filter_non_english=Config.SCRAPER_FILTER_NON_ENGLISH,
            remove_emojis=Config.SCRAPER_REMOVE_EMOJIS
        )
        
        scraper = ReviewScraper(scraper_config)
        progress_bar.progress(10)
        
        # Quick connectivity check
        try:
            import urllib.request
            urllib.request.urlopen('https://play.google.com', timeout=5)
        except Exception as conn_err:
            st.error(f"❌ Cannot reach Google Play Store: {conn_err}")
            st.warning("Streamlit Cloud may be blocking outbound requests to play.google.com. The scheduler (GitHub Actions) will still work.")
            progress_bar.progress(0)
            status_text.text("")
            return None, None
        
        try:
            reviews, scraping_summary = scraper.scrape_reviews(weeks_back=weeks_back)
        except Exception as scrape_err:
            err_msg = str(scrape_err)
            st.error(f"❌ Phase 1 failed: {err_msg}")
            if 'connect' in err_msg.lower() or 'timeout' in err_msg.lower() or 'network' in err_msg.lower() or 'ssl' in err_msg.lower():
                st.warning("⚠️ Network issue detected. Streamlit Cloud may be blocking Google Play Store requests. Try running locally or check your network.")
            progress_bar.progress(0)
            status_text.text("")
            return None, None
        
        if not reviews:
            st.error("❌ Phase 1: No reviews scraped. The Play Store returned 0 results — this may be a network/IP block on Streamlit Cloud.")
            progress_bar.progress(0)
            status_text.text("")
            return None, None
        
        st.success(f"✅ Phase 1: Scraped {len(reviews)} reviews")
        progress_bar.progress(25)
        
        # Phase 2: PII Filtering
        status_text.text("🔒 Phase 2: Filtering PII from reviews...")
        pii_filter = PIIFilter()
        filtered_reviews, pii_summary = pii_filter.filter_reviews(reviews)
        st.success(f"✅ Phase 2: {len(filtered_reviews)} reviews after PII filtering")
        progress_bar.progress(35)
        
        # Phase 3: Theme Analysis
        status_text.text("🔍 Phase 3: Analyzing themes with Groq LLM...")
        
        # Create Groq config
        groq_config = GroqConfig(
            api_key=Config.GROQ_API_KEY,
            model=Config.GROQ_MODEL,
            timeout=Config.GROQ_TIMEOUT,
            max_retries=Config.GROQ_MAX_RETRIES
        )
        
        analyzer = ThemeAnalyzer(groq_config)
        themes, metadata = analyzer.analyze_themes(filtered_reviews, max_themes=Config.MAX_THEMES)
        st.success(f"✅ Phase 3: Identified {len(themes)} themes")
        progress_bar.progress(60)
        
        # Phase 4: Report Generation
        status_text.text("📝 Phase 4: Generating pulse report...")
        generator = ReportGenerator()
        
        # Calculate date range from scraping summary
        start_date, end_date = scraping_summary.date_range
        
        report, gen_metadata = generator.generate_report(
            themes=themes,
            date_range=(start_date, end_date),
            total_review_count=len(filtered_reviews)
        )
        st.success("✅ Phase 4: Report generated")
        progress_bar.progress(80)
        
        # Phase 5: Email Drafting + Sending
        status_text.text("✉️ Phase 5: Sending email report...")
        drafter = EmailDrafter(send_email=True)
        email_content, draft_metadata = drafter.draft_email(
            report=report,
            recipient=recipient_email
        )
        if draft_metadata.email_sent:
            st.success(f"✅ Email sent to {recipient_email}")
        else:
            st.error(f"❌ Email failed: {draft_metadata.error_message or 'Unknown SMTP error'}")
        progress_bar.progress(100)
        
        status_text.text("✅ Analysis complete!")
        
        # Store results in session state
        st.session_state.analysis_complete = True
        st.session_state.report_data = report
        st.session_state.email_content = email_content
        
        return report, email_content
        
    except Exception as e:
        st.error(f"❌ Error during analysis: {str(e)}")
        progress_bar.progress(0)
        status_text.text("")
        return None, None

def display_report(report):
    """Display the generated report"""
    
    if not report:
        return
    
    # Header with modern styling
    st.markdown("---")
    st.markdown(f"""
    <div style='display: flex; align-items: baseline; justify-content: space-between; margin-bottom: 1.5rem;'>
        <h2 style='margin: 0; color: #f1f5f9; font-size: 1.4rem; font-weight: 700;'>📊 Weekly Pulse Report</h2>
        <span style='background: #1e293b; color: #64748b; font-size: 0.78rem; padding: 0.3rem 0.75rem; border-radius: 20px; border: 1px solid #334155;'>
            {report.date_range[0].strftime("%b %d")} – {report.date_range[1].strftime("%b %d, %Y")}
        </span>
    </div>
    """, unsafe_allow_html=True)
    
    # Statistics with professional cards
    st.markdown("<div style='margin: 2rem 0;'>", unsafe_allow_html=True)
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Reviews", f"{report.review_count:,}")
    
    with col2:
        avg_rating = report.average_rating if report.average_rating else "N/A"
        st.metric("Avg Rating", f"{avg_rating:.1f}⭐" if avg_rating != "N/A" else avg_rating)
    
    with col3:
        positive = report.positive_count if report.positive_count else 0
        st.metric("Positive", f"{positive:,}")
    
    with col4:
        negative = report.negative_count if report.negative_count else 0
        st.metric("Negative", f"{negative:,}")
    
    st.markdown("</div>", unsafe_allow_html=True)
    st.markdown("---")
    
    # Top Themes
    st.markdown("<p style='color: #64748b; font-size: 0.78rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.8px; margin: 1.5rem 0 0.75rem 0;'>📌 Top Themes</p>", unsafe_allow_html=True)
    
    for i, theme in enumerate(report.themes, 1):
        freq = getattr(theme, 'actual_frequency', theme.frequency)
        avg_rating = theme.average_rating if theme.average_rating else 0.0
        stars = '⭐' * int(round(avg_rating))
        
        with st.expander(f"{i}. {theme.label} • {freq:,} reviews • {stars} {avg_rating:.1f}", expanded=(i==1)):
            st.markdown(f"<div style='padding: 0.5rem 0; line-height: 1.7; color: #ffffff;'>{theme.description}</div>", unsafe_allow_html=True)
    
    st.markdown("---")
    
    # User Voices
    st.markdown("<p style='color: #64748b; font-size: 0.78rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.8px; margin: 1.5rem 0 0.75rem 0;'>💬 User Voices</p>", unsafe_allow_html=True)

    for i, quote in enumerate(report.quotes, 1):
        st.markdown(f"""
        <div style='background: #111827; border: 1px solid #1e293b; border-left: 3px solid #3b82f6; padding: 1.25rem 1.5rem; margin: 0.75rem 0; border-radius: 10px;'>
            <p style='color: #94a3b8; font-size: 0.9rem; line-height: 1.75; margin: 0; font-style: italic;'>"{quote}"</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Action Items
    st.markdown("<p style='color: #64748b; font-size: 0.78rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.8px; margin: 1.5rem 0 0.75rem 0;'>💡 Action Items</p>", unsafe_allow_html=True)

    for i, idea in enumerate(report.action_ideas, 1):
        raw_parts = [p.strip() for p in idea.split('→')]
        parts = [p for p in raw_parts if p and p not in ('...', '…') and not p.endswith('...')]
        title = parts[0] if parts else idea
        steps = parts[1:] if len(parts) > 1 else []

        card_html = f"""
        <div style='background:#111827; border:1px solid #1e293b; border-left:3px solid #3b82f6;
                    padding:1.25rem 1.5rem; margin:0.75rem 0; border-radius:10px;'>
            <div style='display:flex; align-items:center; gap:0.75rem; margin-bottom:{"0.75rem" if steps else "0"};'>
                <span style='background:#1e3a5f; color:#60a5fa; font-size:0.75rem; font-weight:700;
                             padding:0.2rem 0.55rem; border-radius:5px;'>{i}</span>
                <span style='color:#e2e8f0; font-size:0.95rem; font-weight:600;'>{title}</span>
            </div>"""

        for step in steps:
            card_html += f"""
            <div style='display:flex; align-items:flex-start; gap:0.5rem; margin-top:0.5rem; padding-left:2.5rem;'>
                <span style='color:#3b82f6; font-weight:700; flex-shrink:0;'>→</span>
                <span style='color:#94a3b8; font-size:0.88rem; line-height:1.6;'>{step}</span>
            </div>"""

        card_html += "</div>"
        st.markdown(card_html, unsafe_allow_html=True)
    
    st.markdown("---")

    # Footer - timestamp in IST (UTC+5:30)
    from datetime import timezone, timedelta as td
    IST = timezone(td(hours=5, minutes=30))
    generated_ist = report.generation_timestamp.astimezone(IST)
    st.markdown(f"""
    <div style='display: flex; justify-content: space-between; align-items: center; padding: 0.75rem 0; margin-top: 0.5rem;'>
        <span style='color: #334155; font-size: 0.78rem;'>📅 Generated {generated_ist.strftime('%b %d, %Y at %I:%M %p')} IST</span>
        <span style='background: #1e293b; color: #475569; font-size: 0.75rem; padding: 0.2rem 0.6rem; border-radius: 6px;'>{report.word_count} words</span>
    </div>
    """, unsafe_allow_html=True)

def main():
    """Main Streamlit app"""
    
    # ── Hero header ──
    st.markdown("""
    <div style='padding: 2rem 0 1.5rem 0; border-bottom: 1px solid #1e293b; margin-bottom: 2rem;'>
        <div style='display: flex; align-items: center; gap: 0.75rem; margin-bottom: 0.5rem;'>
            <span style='font-size: 1.8rem;'>📊</span>
            <h1 style='margin: 0; font-size: 1.9rem; font-weight: 800; color: #f8fafc;'>Play Store Review Analyzer</h1>
        </div>
        <p style='color: #64748b; font-size: 0.95rem; margin: 0; font-weight: 400;'>
            AI-powered analysis of Google Play Store reviews &nbsp;·&nbsp; Groww App &nbsp;·&nbsp;
            <span style='color: #3b82f6;'>● Live</span>
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Configuration section at the top
    if not st.session_state.analysis_complete:
        with st.container():
            st.markdown("""
            <div style='background: #111827; border: 1px solid #1e293b; border-radius: 12px; padding: 1.75rem 2rem; margin-bottom: 1.5rem;'>
                <p style='color: #64748b; font-size: 0.78rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.8px; margin: 0 0 1rem 0;'>⚙️ Configuration</p>
            </div>
            """, unsafe_allow_html=True)

            col1, col2 = st.columns([2, 1])

            with col1:
                weeks_back = st.slider(
                    "Weeks to analyze",
                    min_value=8, max_value=12, value=10,
                    help="Number of weeks of reviews to analyze"
                )
                recipient_email = st.text_input(
                    "Recipient Email",
                    placeholder="Enter recipient email address",
                    help="Email address for the report"
                )

            with col2:
                st.markdown(f"""
                <div style='background: #0a0f1e; border: 1px solid #1e293b; border-radius: 10px; padding: 1.25rem; margin-top: 0.5rem;'>
                    <p style='color: #475569; font-size: 0.75rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.6px; margin: 0 0 0.75rem 0;'>System Info</p>
                    <div style='display: flex; flex-direction: column; gap: 0.5rem;'>
                        <div style='display: flex; justify-content: space-between;'>
                            <span style='color: #475569; font-size: 0.82rem;'>Model</span>
                            <span style='color: #93c5fd; font-size: 0.82rem; font-weight: 500;'>{Config.GROQ_MODEL.split('-')[0]}</span>
                        </div>
                        <div style='display: flex; justify-content: space-between;'>
                            <span style='color: #475569; font-size: 0.82rem;'>Max Reviews</span>
                            <span style='color: #93c5fd; font-size: 0.82rem; font-weight: 500;'>{Config.SCRAPER_MAX_REVIEWS:,}</span>
                        </div>
                        <div style='display: flex; justify-content: space-between;'>
                            <span style='color: #475569; font-size: 0.82rem;'>Max Themes</span>
                            <span style='color: #93c5fd; font-size: 0.82rem; font-weight: 500;'>{Config.MAX_THEMES}</span>
                        </div>
                        <div style='display: flex; justify-content: space-between;'>
                            <span style='color: #475569; font-size: 0.82rem;'>Word Limit</span>
                            <span style='color: #93c5fd; font-size: 0.82rem; font-weight: 500;'>{Config.REPORT_WORD_LIMIT}</span>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        
        # Start button (outside container to avoid spacing issues)
        st.markdown("<div style='margin-top: 1.5rem;'></div>", unsafe_allow_html=True)
        if st.button("🚀 START ANALYSIS", type="primary"):
            if not recipient_email or '@' not in recipient_email:
                st.error("Please enter a valid email address")
            else:
                st.session_state.analysis_complete = False
                st.session_state.report_data = None
                st.session_state.email_content = None
                with st.spinner("Running analysis..."):
                    report, email = run_analysis(weeks_back, recipient_email)
    
    # Display results if available
    if st.session_state.analysis_complete and st.session_state.report_data:
        display_report(st.session_state.report_data)
        
        # Email preview
        with st.expander("📧 Email Preview", expanded=False):
            st.text_area(
                "Email Content",
                value=st.session_state.email_content,
                height=400,
                disabled=True
            )
            
            if st.button("📥 Download Email Draft"):
                st.download_button(
                    label="Download as TXT",
                    data=st.session_state.email_content,
                    file_name=f"pulse_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                    mime="text/plain"
                )
    else:
        # Welcome message
        st.markdown("""
        <div style='background: #0f172a; border: 1px solid #1e3a5f; border-left: 3px solid #3b82f6; border-radius: 10px; padding: 1.25rem 1.5rem; margin: 1rem 0;'>
            <p style='color: #93c5fd; font-size: 0.9rem; margin: 0 0 0.75rem 0; font-weight: 600;'>⚙️ Ready to analyze</p>
            <p style='color: #64748b; font-size: 0.85rem; margin: 0 0 0.5rem 0;'>Configure settings above and click <strong style='color: #93c5fd;'>Run Analysis</strong> to begin.</p>
            <div style='display: flex; gap: 1.5rem; margin-top: 0.75rem; flex-wrap: wrap;'>
                <span style='color: #475569; font-size: 0.8rem;'>📥 Scrapes Play Store reviews</span>
                <span style='color: #475569; font-size: 0.8rem;'>🔒 PII filtering</span>
                <span style='color: #475569; font-size: 0.8rem;'>🤖 Groq LLM analysis</span>
                <span style='color: #475569; font-size: 0.8rem;'>⏱ ~45–60 seconds</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Feature cards
        col1, col2, col3 = st.columns(3)

        with col1:
            st.markdown("""
            <div style='background: #111827; border: 1px solid #1e293b; border-radius: 12px; padding: 1.5rem; margin-top: 1rem; transition: border-color 0.2s;'>
                <div style='font-size: 1.5rem; margin-bottom: 0.75rem;'>🔍</div>
                <p style='color: #e2e8f0; font-size: 0.95rem; font-weight: 600; margin: 0 0 0.5rem 0;'>Smart Analysis</p>
                <p style='color: #475569; font-size: 0.82rem; margin: 0; line-height: 1.6;'>AI-powered theme detection, sentiment analysis, and trend identification.</p>
            </div>
            """, unsafe_allow_html=True)

        with col2:
            st.markdown("""
            <div style='background: #111827; border: 1px solid #1e293b; border-radius: 12px; padding: 1.5rem; margin-top: 1rem;'>
                <div style='font-size: 1.5rem; margin-bottom: 0.75rem;'>📊</div>
                <p style='color: #e2e8f0; font-size: 0.95rem; font-weight: 600; margin: 0 0 0.5rem 0;'>Pulse Reports</p>
                <p style='color: #475569; font-size: 0.82rem; margin: 0; line-height: 1.6;'>Top themes, user quotes, and actionable product recommendations.</p>
            </div>
            """, unsafe_allow_html=True)

        with col3:
            st.markdown("""
            <div style='background: #111827; border: 1px solid #1e293b; border-radius: 12px; padding: 1.5rem; margin-top: 1rem;'>
                <div style='font-size: 1.5rem; margin-bottom: 0.75rem;'>✉️</div>
                <p style='color: #e2e8f0; font-size: 0.95rem; font-weight: 600; margin: 0 0 0.5rem 0;'>Email Ready</p>
                <p style='color: #475569; font-size: 0.82rem; margin: 0; line-height: 1.6;'>Professionally formatted email draft, ready to send to stakeholders.</p>
            </div>
            """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
