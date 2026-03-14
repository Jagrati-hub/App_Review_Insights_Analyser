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

# Custom CSS for user-friendly theme
st.markdown("""
<style>
    /* User-Friendly Blue Gradient Theme */
    .main {
        background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%);
        color: #ffffff;
    }
    
    .stApp {
        background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%);
    }
    
    /* Header styling - Warm and inviting */
    h1 {
        color: #ffffff !important;
        font-weight: 800 !important;
        border-bottom: 4px solid #60a5fa;
        padding-bottom: 1.2rem;
        margin-bottom: 2rem;
        font-size: 2.8rem !important;
        letter-spacing: -0.5px;
        text-shadow: 0 3px 6px rgba(0, 0, 0, 0.3);
    }
    
    h2 {
        color: #ffffff !important;
        font-weight: 700 !important;
        margin-top: 2.5rem;
        margin-bottom: 1.2rem;
        font-size: 2rem !important;
        letter-spacing: -0.3px;
        text-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
    }
    
    h3 {
        color: #60a5fa !important;
        font-weight: 700 !important;
        font-size: 1.4rem !important;
        letter-spacing: -0.2px;
    }
    
    /* Text colors - White for readability on purple */
    p, span, div, label {
        color: #ffffff !important;
        font-weight: 500 !important;
    }
    
    /* Stronger text for better readability */
    .stMarkdown, .stText {
        color: #ffffff !important;
        font-weight: 500 !important;
    }
    
    /* List items - White and prominent */
    li {
        color: #ffffff !important;
        font-weight: 500 !important;
        line-height: 1.8 !important;
    }
    
    /* Button styling - Blue/Cyan rounded buttons */
    .stButton>button {
        background: linear-gradient(135deg, #3b82f6 0%, #06b6d4 100%) !important;
        color: #ffffff !important;
        border: none !important;
        padding: 1rem 2.5rem !important;
        font-size: 1.1rem !important;
        font-weight: 700 !important;
        border-radius: 25px !important;
        width: 100%;
        text-transform: uppercase;
        letter-spacing: 1.5px;
        box-shadow: 0 8px 20px rgba(59, 130, 246, 0.4);
        transition: all 0.3s ease;
    }
    
    .stButton>button:hover {
        background: linear-gradient(135deg, #06b6d4 0%, #3b82f6 100%) !important;
        box-shadow: 0 10px 25px rgba(6, 182, 212, 0.5);
        transform: translateY(-3px);
    }
    
    /* Input fields - Glass morphism effect */
    .stTextInput>div>div>input,
    .stNumberInput>div>div>input,
    .stSelectbox>div>div>select {
        background: rgba(255, 255, 255, 0.15) !important;
        color: #ffffff !important;
        border: 2px solid rgba(255, 255, 255, 0.3) !important;
        border-radius: 15px !important;
        font-weight: 500 !important;
        font-size: 1rem !important;
        padding: 0.5rem !important;
        backdrop-filter: blur(10px);
    }
    
    .stTextInput>div>div>input:focus,
    .stNumberInput>div>div>input:focus,
    .stSelectbox>div>div>select:focus {
        border-color: #60a5fa !important;
        box-shadow: 0 0 0 3px rgba(96, 165, 250, 0.3) !important;
    }
    
    /* Input labels - White and prominent */
    .stTextInput>label,
    .stNumberInput>label,
    .stSelectbox>label,
    .stSlider>label {
        color: #ffffff !important;
        font-weight: 700 !important;
        font-size: 1rem !important;
        margin-bottom: 0.5rem !important;
        letter-spacing: 0.3px;
        text-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
    }
    
    /* Slider - Blue accent */
    .stSlider>div>div>div>div {
        background: #60a5fa !important;
    }
    
    .stSlider>div>div>div {
        background: rgba(255, 255, 255, 0.3) !important;
    }
    
    /* Metrics - Colorful and appealing */
    [data-testid="stMetricValue"] {
        color: #60a5fa !important;
        font-size: 2.5rem !important;
        font-weight: 800 !important;
        text-shadow: 0 3px 6px rgba(0, 0, 0, 0.3);
    }
    
    [data-testid="stMetricLabel"] {
        color: #ffffff !important;
        font-weight: 700 !important;
        text-transform: uppercase;
        letter-spacing: 1px;
        font-size: 0.9rem !important;
        text-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
    }
    
    /* Metric container styling - Glass morphism */
    [data-testid="stMetric"] {
        background: rgba(255, 255, 255, 0.15);
        padding: 1.5rem;
        border-radius: 20px;
        border: 1px solid rgba(255, 255, 255, 0.3);
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
        backdrop-filter: blur(10px);
    }
    
    /* Cards/Containers - Glass morphism */
    .stAlert {
        background: rgba(255, 255, 255, 0.15) !important;
        border: 1px solid rgba(255, 255, 255, 0.3) !important;
        border-radius: 20px !important;
        color: #ffffff !important;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
        backdrop-filter: blur(10px);
    }
    
    /* Expander - Glass morphism styling */
    .streamlit-expanderHeader {
        background: rgba(255, 255, 255, 0.15) !important;
        border: 2px solid rgba(255, 255, 255, 0.3) !important;
        color: #ffffff !important;
        font-weight: 700 !important;
        border-radius: 20px !important;
        font-size: 1.1rem !important;
        padding: 1.2rem 1.5rem !important;
        margin: 0.5rem 0 !important;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
        backdrop-filter: blur(10px);
        transition: all 0.2s ease;
    }
    
    .streamlit-expanderHeader:hover {
        border-color: #60a5fa !important;
        box-shadow: 0 10px 40px rgba(96, 165, 250, 0.3);
    }
    
    .streamlit-expanderContent {
        background: rgba(255, 255, 255, 0.1) !important;
        border: 2px solid rgba(255, 255, 255, 0.2) !important;
        border-top: none !important;
        border-radius: 0 0 20px 20px !important;
        color: #ffffff !important;
        padding: 1.5rem !important;
        backdrop-filter: blur(10px);
    }
    
    .streamlit-expanderContent p,
    .streamlit-expanderContent div,
    .streamlit-expanderContent span {
        color: #ffffff !important;
        font-size: 1.05rem !important;
        line-height: 1.8 !important;
        font-weight: 500 !important;
    }
    
    /* Progress bar - Blue gradient */
    .stProgress>div>div>div>div {
        background: linear-gradient(90deg, #3b82f6 0%, #06b6d4 100%) !important;
    }
    
    .stProgress>div>div>div {
        background: rgba(255, 255, 255, 0.3) !important;
    }
    
    /* Info boxes - Glass morphism styling */
    .stInfo {
        background: rgba(255, 255, 255, 0.2) !important;
        border-left: 4px solid #60a5fa !important;
        border-radius: 20px !important;
        color: #ffffff !important;
        padding: 1.5rem !important;
        margin: 1rem 0 !important;
        backdrop-filter: blur(10px);
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
    }
    
    .stInfo p, .stInfo div, .stInfo span, .stInfo li {
        color: #ffffff !important;
        line-height: 1.7 !important;
    }
    
    .stSuccess {
        background: rgba(16, 185, 129, 0.2) !important;
        border-left: 4px solid #10b981 !important;
        border-radius: 20px !important;
        color: #ffffff !important;
        padding: 1rem !important;
        margin: 0.5rem 0 !important;
        backdrop-filter: blur(10px);
    }
    
    .stSuccess p, .stSuccess div, .stSuccess span {
        color: #ffffff !important;
    }
    
    .stError {
        background: rgba(239, 68, 68, 0.2) !important;
        border-left: 4px solid #ef4444 !important;
        border-radius: 20px !important;
        color: #ffffff !important;
        padding: 1rem !important;
        margin: 0.5rem 0 !important;
        backdrop-filter: blur(10px);
    }
    
    .stError p, .stError div, .stError span {
        color: #ffffff !important;
    }
    
    /* Text area - Glass morphism */
    .stTextArea>div>div>textarea {
        background: rgba(255, 255, 255, 0.15) !important;
        color: #ffffff !important;
        border: 2px solid rgba(255, 255, 255, 0.3) !important;
        font-family: 'Courier New', monospace !important;
        border-radius: 15px !important;
        backdrop-filter: blur(10px);
    }
    
    /* Download button - Cyan accent */
    .stDownloadButton>button {
        background: linear-gradient(135deg, #06b6d4 0%, #0891b2 100%) !important;
        color: #ffffff !important;
        border: none !important;
        font-weight: 600 !important;
        border-radius: 20px !important;
        padding: 0.75rem 1.5rem !important;
        box-shadow: 0 6px 20px rgba(6, 182, 212, 0.4);
    }
    
    /* Configuration section - Glass morphism card */
    .config-section {
        background: rgba(255, 255, 255, 0.15);
        border: 1px solid rgba(255, 255, 255, 0.3);
        padding: 2rem;
        margin: 2rem 0;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
        border-radius: 25px;
        backdrop-filter: blur(10px);
    }
    
    .config-section p,
    .config-section div,
    .config-section span,
    .config-section label {
        color: #ffffff !important;
    }
    
    /* Content containers - Glass morphism */
    .content-box {
        background: rgba(255, 255, 255, 0.15);
        border: 1px solid rgba(255, 255, 255, 0.3);
        padding: 1.5rem;
        margin: 1rem 0;
        border-radius: 20px;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
        backdrop-filter: blur(10px);
    }
    
    /* Section dividers */
    hr {
        border: none;
        border-top: 2px solid rgba(255, 255, 255, 0.3);
        margin: 2.5rem 0;
    }
    
    /* Hide sidebar */
    [data-testid="stSidebar"] {
        display: none;
    }
    
    /* Caption text */
    .stCaption {
        color: rgba(255, 255, 255, 0.8) !important;
        font-size: 0.875rem !important;
    }
    
    /* Ensure subheaders are visible and prominent */
    .stSubheader {
        color: #ffffff !important;
        font-size: 1.5rem !important;
        font-weight: 700 !important;
        letter-spacing: -0.3px;
        text-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
    }
    
    /* Help text */
    .stHelp {
        color: rgba(255, 255, 255, 0.8) !important;
    }
    
    /* Professional spacing */
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    
    /* Hide default Streamlit containers */
    .element-container {
        background: transparent !important;
    }
    
    /* Remove default Streamlit padding/margins that create blank spaces */
    .stMarkdown {
        background: transparent !important;
    }
    
    /* Fix any blank containers */
    div[data-testid="stVerticalBlock"] > div {
        background: transparent !important;
    }
    
    /* Remove any default white boxes */
    .stApp > div {
        background: transparent !important;
    }
    
    /* Ensure main content area has no extra containers */
    section[data-testid="stAppViewContainer"] {
        background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%) !important;
    }
    
    /* Remove any extra padding from columns */
    div[data-testid="column"] {
        background: transparent !important;
    }
    
    /* Target the specific container that might be showing as off-white */
    .stApp > header + div {
        background: transparent !important;
    }
    
    /* Remove background from all vertical blocks */
    div[data-testid="stVerticalBlock"] {
        background: transparent !important;
    }
    
    /* Ensure horizontal blocks are transparent */
    div[data-testid="stHorizontalBlock"] {
        background: transparent !important;
    }
    
    /* Fix container backgrounds */
    .main .block-container {
        background: transparent !important;
    }
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
        progress_bar.progress(10)
        
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
        
        reviews, scraping_summary = scraper.scrape_reviews(weeks_back=weeks_back)
        st.success(f"✅ Scraped {len(reviews)} reviews")
        progress_bar.progress(25)
        
        # PII Filtering
        status_text.text("🔒 Filtering PII from reviews...")
        pii_filter = PIIFilter()
        filtered_reviews, pii_summary = pii_filter.filter_reviews(reviews)
        
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
        st.success(f"✅ Identified {len(themes)} themes")
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
        st.success("✅ Report generated")
        progress_bar.progress(80)
        
        # Phase 5: Email Drafting
        status_text.text("✉️ Phase 5: Creating email draft...")
        drafter = EmailDrafter(send_email=False)  # Don't send in Streamlit
        email_content, draft_metadata = drafter.draft_email(
            report=report,
            recipient=recipient_email
        )
        st.success("✅ Email draft created")
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
    
    # Header with professional styling
    st.markdown("---")
    st.header("📊 Weekly Pulse Report")
    
    start_date = report.date_range[0].strftime("%B %d")
    end_date = report.date_range[1].strftime("%B %d, %Y")
    st.markdown(f"<p style='color: rgba(255, 255, 255, 0.9); font-size: 1.1rem; margin-bottom: 2rem;'>{start_date} to {end_date}</p>", unsafe_allow_html=True)
    
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
    st.subheader("📊 Top Themes")
    st.markdown("<p style='color: rgba(255, 255, 255, 0.9); margin-bottom: 1rem;'>Key insights from user feedback</p>", unsafe_allow_html=True)
    
    for i, theme in enumerate(report.themes, 1):
        freq = getattr(theme, 'actual_frequency', theme.frequency)
        avg_rating = theme.average_rating if theme.average_rating else 0.0
        stars = '⭐' * int(round(avg_rating))
        
        with st.expander(f"{i}. {theme.label} • {freq:,} reviews • {stars} {avg_rating:.1f}", expanded=(i==1)):
            st.markdown(f"<div style='padding: 0.5rem 0; line-height: 1.7; color: #ffffff;'>{theme.description}</div>", unsafe_allow_html=True)
    
    st.markdown("---")
    
    # User Voices
    st.subheader("💬 User Voices")
    st.markdown("<p style='color: rgba(255, 255, 255, 0.9); margin-bottom: 1rem;'>Representative feedback from users</p>", unsafe_allow_html=True)
    
    for i, quote in enumerate(report.quotes, 1):
        st.markdown(f"""
        <div style='background: rgba(255, 255, 255, 0.15); border-left: 4px solid #60a5fa; padding: 1.5rem; margin: 1rem 0; border-radius: 20px; box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1); backdrop-filter: blur(10px);'>
            <p style='color: #ffffff; font-size: 1.05rem; line-height: 1.7; margin: 0; font-style: italic;'>"{quote}"</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Action Roadmap
    st.subheader("💡 Action Roadmap")
    st.markdown("<p style='color: rgba(255, 255, 255, 0.9); margin-bottom: 1rem;'>Recommended next steps</p>", unsafe_allow_html=True)
    
    for i, idea in enumerate(report.action_ideas, 1):
        parts = [p.strip() for p in idea.split('→')]
        title = parts[0] if parts else idea
        steps = parts[1:] if len(parts) > 1 else []
        
        st.markdown(f"""
        <div style='background: rgba(255, 255, 255, 0.15); border: 1px solid rgba(255, 255, 255, 0.3); padding: 1.5rem; margin: 1rem 0; border-radius: 20px; box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1); backdrop-filter: blur(10px);'>
            <h4 style='color: #60a5fa; margin: 0 0 1rem 0; font-weight: 600;'>{i}. {title}</h4>
        """, unsafe_allow_html=True)
        
        if steps:
            for j, step in enumerate(steps, 1):
                st.markdown(f"<p style='color: #ffffff; margin: 0.5rem 0 0.5rem 1.5rem; line-height: 1.6;'>→ {step}</p>", unsafe_allow_html=True)
        
        st.markdown("</div>", unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Footer
    st.markdown("""
    <div style='margin-top: 2rem; padding: 1.5rem; background: rgba(255, 255, 255, 0.15); border-radius: 20px; border: 1px solid rgba(255, 255, 255, 0.3); backdrop-filter: blur(10px);'>
    """, unsafe_allow_html=True)
    st.caption(f"📅 Generated: {report.generation_timestamp.strftime('%B %d, %Y at %I:%M %p')}")
    st.caption(f"📝 Word count: {report.word_count}")
    st.markdown("</div>", unsafe_allow_html=True)

def main():
    """Main Streamlit app"""
    
    # Main content
    st.title("📊 Play Store Review Analyzer")
    st.markdown("<p style='color: rgba(255, 255, 255, 0.9); font-size: 1.1rem; margin-bottom: 2rem;'>Automated analysis of Google Play Store reviews for the Groww app</p>", unsafe_allow_html=True)
    
    # Configuration section at the top
    if not st.session_state.analysis_complete:
        # Use a container with custom styling
        with st.container():
            st.markdown("""
            <style>
            .config-container {
                background: #ffffff;
                border: 1px solid #e2e8f0;
                padding: 2rem;
                margin: 2rem 0;
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.07);
                border-radius: 16px;
            }
            </style>
            """, unsafe_allow_html=True)
            
            st.subheader("⚙️ Configuration")
            
            col1, col2 = st.columns([2, 1])
            
            with col1:
                weeks_back = st.slider(
                    "Weeks to analyze",
                    min_value=8,
                    max_value=12,
                    value=10,
                    help="Number of weeks of reviews to analyze"
                )
                
                recipient_email = st.text_input(
                    "Recipient Email",
                    value="manshuc12@gmail.com",
                    help="Email address for the report"
                )
            
            with col2:
                st.markdown("**System Configuration**")
                st.markdown(f"<p style='color: rgba(255, 255, 255, 0.9); font-size: 0.9rem; margin: 0.25rem 0;'>Model: {Config.GROQ_MODEL}</p>", unsafe_allow_html=True)
                st.markdown(f"<p style='color: rgba(255, 255, 255, 0.9); font-size: 0.9rem; margin: 0.25rem 0;'>Max Reviews: {Config.SCRAPER_MAX_REVIEWS:,}</p>", unsafe_allow_html=True)
                st.markdown(f"<p style='color: rgba(255, 255, 255, 0.9); font-size: 0.9rem; margin: 0.25rem 0;'>Max Themes: {Config.MAX_THEMES}</p>", unsafe_allow_html=True)
                st.markdown(f"<p style='color: rgba(255, 255, 255, 0.9); font-size: 0.9rem; margin: 0.25rem 0;'>Word Limit: {Config.REPORT_WORD_LIMIT}</p>", unsafe_allow_html=True)
        
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
        st.info("""
        ⚙️ Configure your analysis settings above and click **START ANALYSIS** to begin.
        
        **What this does:**
        • Scrapes reviews from Google Play Store (Groww app)
        • Filters non-English reviews and removes PII
        • Analyzes themes using Groq LLM
        • Generates a 250-word pulse report
        • Creates an email draft
        
        **Processing time:** ~45-60 seconds
        """)
        
        # Feature highlights
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("""
            <div style='background: rgba(255, 255, 255, 0.15); padding: 1.5rem; border-radius: 20px; border: 1px solid rgba(255, 255, 255, 0.3); box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1); backdrop-filter: blur(10px); height: 100%;'>
            <h3 style='color: #60a5fa !important; margin-bottom: 1rem;'>🔍 Smart Analysis</h3>
            <ul style='color: #ffffff; line-height: 1.7;'>
            <li>AI-powered theme detection</li>
            <li>Sentiment analysis</li>
            <li>Trend identification</li>
            </ul>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
            <div style='background: rgba(255, 255, 255, 0.15); padding: 1.5rem; border-radius: 20px; border: 1px solid rgba(255, 255, 255, 0.3); box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1); backdrop-filter: blur(10px); height: 100%;'>
            <h3 style='color: #60a5fa !important; margin-bottom: 1rem;'>📊 Comprehensive Reports</h3>
            <ul style='color: #ffffff; line-height: 1.7;'>
            <li>Top 3 themes</li>
            <li>User quotes</li>
            <li>Action recommendations</li>
            </ul>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown("""
            <div style='background: rgba(255, 255, 255, 0.15); padding: 1.5rem; border-radius: 20px; border: 1px solid rgba(255, 255, 255, 0.3); box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1); backdrop-filter: blur(10px); height: 100%;'>
            <h3 style='color: #60a5fa !important; margin-bottom: 1rem;'>✉️ Email Ready</h3>
            <ul style='color: #ffffff; line-height: 1.7;'>
            <li>Professional formatting</li>
            <li>Statistics included</li>
            <li>Ready to send</li>
            </ul>
            </div>
            """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
