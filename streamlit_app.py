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
from common.models import AnalysisRequest

# Page configuration
st.set_page_config(
    page_title="Play Store Review Analyzer",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for corporate theme
st.markdown("""
<style>
    .main {
        background: linear-gradient(135deg, #f8fafc 0%, #e0e7ff 50%, #f1f5f9 100%);
    }
    .stButton>button {
        background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%);
        color: white;
        border: none;
        padding: 0.75rem 2rem;
        font-size: 1rem;
        font-weight: 600;
        border-radius: 0.5rem;
        width: 100%;
    }
    .stButton>button:hover {
        background: linear-gradient(135deg, #1d4ed8 0%, #1e40af 100%);
        box-shadow: 0 4px 12px rgba(37, 99, 235, 0.3);
    }
    h1 {
        color: #1e293b;
        font-weight: 800;
    }
    h2, h3 {
        color: #334155;
        font-weight: 700;
    }
    .stAlert {
        border-radius: 0.5rem;
    }
    .metric-card {
        background: white;
        padding: 1.5rem;
        border-radius: 0.75rem;
        box-shadow: 0 4px 12px rgba(0,0,0,0.08);
        border-left: 4px solid #2563eb;
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
        
        scraper = ReviewScraper()
        end_date = datetime.now().date()
        start_date = end_date - timedelta(weeks=weeks_back)
        
        reviews, scraping_summary = scraper.scrape_reviews(start_date, end_date)
        st.success(f"✅ Scraped {len(reviews)} reviews")
        progress_bar.progress(25)
        
        # PII Filtering
        status_text.text("🔒 Filtering PII from reviews...")
        pii_filter = PIIFilter()
        filtered_reviews = []
        for review in reviews:
            filtered_review, _ = pii_filter.filter_pii(review)
            filtered_reviews.append(filtered_review)
        
        progress_bar.progress(35)
        
        # Phase 3: Theme Analysis
        status_text.text("🔍 Phase 3: Analyzing themes with Groq LLM...")
        analyzer = ThemeAnalyzer()
        themes, metadata = analyzer.analyze_themes(filtered_reviews)
        st.success(f"✅ Identified {len(themes)} themes")
        progress_bar.progress(60)
        
        # Phase 4: Report Generation
        status_text.text("📝 Phase 4: Generating pulse report...")
        generator = ReportGenerator()
        report = generator.generate_report(
            themes=themes,
            all_reviews=filtered_reviews,
            date_range=(start_date, end_date)
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
    
    # Header
    st.markdown("---")
    st.header("📊 Weekly Pulse Report Of Groww")
    
    start_date = report.date_range[0].strftime("%B %d")
    end_date = report.date_range[1].strftime("%B %d, %Y")
    st.subheader(f"Week of {start_date} to {end_date}")
    
    # Statistics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Reviews", report.review_count)
    
    with col2:
        avg_rating = report.average_rating if report.average_rating else "N/A"
        st.metric("Avg Rating", f"{avg_rating}⭐" if avg_rating != "N/A" else avg_rating)
    
    with col3:
        positive = report.positive_count if report.positive_count else 0
        st.metric("Positive (4-5★)", positive)
    
    with col4:
        negative = report.negative_count if report.negative_count else 0
        st.metric("Negative (1-3★)", negative)
    
    st.markdown("---")
    
    # Top Themes
    st.subheader("📊 Top Themes")
    for i, theme in enumerate(report.themes, 1):
        freq = getattr(theme, 'actual_frequency', theme.frequency)
        avg_rating = theme.average_rating if theme.average_rating else 0.0
        stars = '⭐' * int(round(avg_rating))
        
        with st.expander(f"**{i}. {theme.label}** ({freq} reviews • {stars} {avg_rating:.1f})", expanded=True):
            st.write(theme.description)
    
    st.markdown("---")
    
    # User Voices
    st.subheader("💬 User Voices")
    for i, quote in enumerate(report.quotes, 1):
        st.info(f'"{quote}"')
    
    st.markdown("---")
    
    # Action Roadmap
    st.subheader("💡 Action Roadmap")
    for i, idea in enumerate(report.action_ideas, 1):
        parts = [p.strip() for p in idea.split('→')]
        title = parts[0] if parts else idea
        steps = parts[1:] if len(parts) > 1 else []
        
        with st.container():
            st.markdown(f"**{i}. {title}**")
            if steps:
                for j, step in enumerate(steps, 1):
                    st.write(f"   {j}. {step}")
            st.markdown("")
    
    st.markdown("---")
    
    # Footer
    st.caption(f"Report generated: {report.generation_timestamp.strftime('%B %d, %Y at %H:%M:%S')}")
    st.caption(f"Word count: {report.word_count}")

def main():
    """Main Streamlit app"""
    
    # Sidebar
    with st.sidebar:
        st.image("https://via.placeholder.com/150x50/2563eb/ffffff?text=Groww", use_container_width=True)
        st.title("Configuration")
        
        st.markdown("### Analysis Settings")
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
        
        st.markdown("---")
        
        st.markdown("### System Info")
        st.info(f"""
        **Model:** {Config.GROQ_MODEL}
        
        **Max Reviews:** {Config.SCRAPER_MAX_REVIEWS}
        
        **Max Themes:** {Config.MAX_THEMES}
        
        **Word Limit:** {Config.REPORT_WORD_LIMIT}
        """)
        
        st.markdown("---")
        
        if st.button("🚀 Start Analysis", type="primary"):
            if not recipient_email or '@' not in recipient_email:
                st.error("Please enter a valid email address")
            else:
                st.session_state.analysis_complete = False
                st.session_state.report_data = None
                st.session_state.email_content = None
                st.rerun()
    
    # Main content
    st.title("📊 Play Store Review Analyzer")
    st.markdown("Automated analysis of Google Play Store reviews for the Groww app")
    
    # Check if we should run analysis
    if not st.session_state.analysis_complete and st.sidebar.button("🚀 Start Analysis", key="hidden"):
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
        👈 Configure your analysis settings in the sidebar and click **Start Analysis** to begin.
        
        **What this does:**
        1. Scrapes reviews from Google Play Store (Groww app)
        2. Filters non-English reviews and removes PII
        3. Analyzes themes using Groq LLM
        4. Generates a 250-word pulse report
        5. Creates an email draft
        
        **Processing time:** 1.5-3 minutes
        """)
        
        # Feature highlights
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("""
            ### 🔍 Smart Analysis
            - AI-powered theme detection
            - Sentiment analysis
            - Trend identification
            """)
        
        with col2:
            st.markdown("""
            ### 📊 Comprehensive Reports
            - Top 3 themes
            - User quotes
            - Action recommendations
            """)
        
        with col3:
            st.markdown("""
            ### ✉️ Email Ready
            - Professional formatting
            - Statistics included
            - Ready to send
            """)

if __name__ == "__main__":
    main()
