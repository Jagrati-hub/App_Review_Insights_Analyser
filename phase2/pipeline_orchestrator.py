"""Pipeline Orchestrator for coordinating all analysis phases."""
import os
import sys
import json
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from common.models import AnalysisRequest, PipelineStatus, Review, Theme, PulseReport, ScraperConfig, GroqConfig
from common.config import Config

# Import phase components
from phase1.review_scraper import ReviewScraper
from phase1.pii_filter import PIIFilter
from phase3.theme_analyzer import ThemeAnalyzer
from phase4.report_generator import ReportGenerator
from phase5.email_drafter import EmailDrafter


class PipelineOrchestrator:
    """Orchestrates the full analysis pipeline across all phases."""
    
    def __init__(self):
        """Initialize pipeline orchestrator."""
        self.statuses: Dict[str, PipelineStatus] = {}
        self.results: Dict[str, dict] = {}
        
        # Initialize phase components with proper configuration
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
        
        groq_config = GroqConfig(
            api_key=Config.GROQ_API_KEY,
            model=Config.GROQ_MODEL,
            timeout=Config.GROQ_TIMEOUT,
            max_retries=Config.GROQ_MAX_RETRIES
        )
        
        self.scraper = ReviewScraper(scraper_config)
        self.pii_filter = PIIFilter()
        self.theme_analyzer = ThemeAnalyzer(groq_config)
        self.report_generator = ReportGenerator()
        self.email_drafter = EmailDrafter()
    
    def run_pipeline(self, request: AnalysisRequest) -> dict:
        """Run the complete analysis pipeline.
        
        Args:
            request: AnalysisRequest with configuration
        
        Returns:
            Dictionary with status and results
        """
        request_id = request.request_id
        
        # Initialize status
        self.statuses[request_id] = PipelineStatus(
            request_id=request_id,
            status='pending',
            current_step='Initializing',
            progress_percent=0,
            started_at=datetime.now()
        )
        
        try:
            # Phase 1: Scrape and filter reviews
            self._update_status(request_id, 'scraping', 'Scraping reviews from Play Store', 10)
            reviews, scraping_summary = self._run_phase1(request.weeks_back)
            
            if not reviews:
                raise Exception("No reviews found after scraping and filtering")
            
            # Phase 3: Analyze themes
            self._update_status(request_id, 'analyzing', 'Analyzing themes with Groq LLM', 40)
            themes, analysis_metadata = self._run_phase3(reviews)
            
            if not themes:
                raise Exception("No themes identified")
            
            # Phase 4: Generate report
            self._update_status(request_id, 'generating', 'Generating pulse report', 70)
            report, generation_metadata = self._run_phase4(
                themes,
                scraping_summary.date_range,
                len(reviews)
            )
            
            # Phase 5: Draft email
            self._update_status(request_id, 'generating', 'Drafting email', 90)
            email_content, draft_metadata = self._run_phase5(report, request.recipient_email)
            
            # Complete
            self._update_status(request_id, 'complete', 'Analysis complete', 100)
            
            # Store results
            self.results[request_id] = {
                'status': 'complete',
                'report': self._serialize_report(report),
                'email_draft': email_content,
                'metadata': {
                    'scraping': {
                        'total_reviews': scraping_summary.total_reviews,
                        'valid_reviews': scraping_summary.valid_reviews,
                        'date_range': [str(scraping_summary.date_range[0]), str(scraping_summary.date_range[1])]
                    },
                    'analysis': {
                        'model_version': analysis_metadata.model_version,
                        'total_themes': analysis_metadata.total_themes
                    },
                    'generation': {
                        'word_count': generation_metadata.word_count,
                        'model_version': generation_metadata.model_version
                    },
                    'draft': {
                        'recipient': draft_metadata.recipient,
                        'output_path': draft_metadata.output_path
                    }
                }
            }
            
            return self.results[request_id]
        
        except Exception as e:
            self._update_status(request_id, 'error', f'Error: {str(e)}', 0, str(e))
            self.results[request_id] = {
                'status': 'error',
                'error': str(e)
            }
            return self.results[request_id]
    
    def _run_phase1(self, weeks_back: int) -> tuple:
        """Run Phase 1: Review scraping and PII filtering."""
        # Scrape reviews (scraper handles date range internally based on weeks_back)
        reviews, scraping_summary = self.scraper.scrape_reviews(
            weeks_back=weeks_back
        )
        
        # Filter PII
        filtered_reviews, pii_summary = self.pii_filter.filter_reviews(reviews)
        
        return filtered_reviews, scraping_summary
    
    def _run_phase3(self, reviews: list[Review]) -> tuple:
        """Run Phase 3: Theme analysis."""
        themes, metadata = self.theme_analyzer.analyze_themes(reviews)
        return themes, metadata
    
    def _run_phase4(self, themes: list[Theme], date_range: tuple, review_count: int) -> tuple:
        """Run Phase 4: Report generation."""
        report, metadata = self.report_generator.generate_report(
            themes=themes,
            date_range=date_range,
            total_review_count=review_count
        )
        return report, metadata
    
    def _run_phase5(self, report: PulseReport, recipient: str) -> tuple:
        """Run Phase 5: Email drafting."""
        email_content, metadata = self.email_drafter.draft_email(
            report=report,
            recipient=recipient,
            sender_name="Groww Product Team"
        )
        return email_content, metadata
    
    def _update_status(
        self,
        request_id: str,
        status: str,
        current_step: str,
        progress: int,
        error: Optional[str] = None
    ):
        """Update pipeline status."""
        if request_id in self.statuses:
            self.statuses[request_id].status = status
            self.statuses[request_id].current_step = current_step
            self.statuses[request_id].progress_percent = progress
            self.statuses[request_id].error_message = error
            
            if status == 'complete':
                self.statuses[request_id].completed_at = datetime.now()
    
    def get_status(self, request_id: str) -> Optional[PipelineStatus]:
        """Get pipeline status for a request."""
        return self.statuses.get(request_id)
    
    def get_result(self, request_id: str) -> Optional[dict]:
        """Get pipeline result for a request."""
        return self.results.get(request_id)
    
    def _serialize_report(self, report: PulseReport) -> dict:
        """Serialize PulseReport to dictionary."""
        return {
            'date_range': [str(report.date_range[0]), str(report.date_range[1])],
            'themes': [
                {
                    'rank': theme.rank,
                    'label': theme.label,
                    'description': theme.description,
                    'frequency': getattr(theme, 'actual_frequency', theme.frequency)
                }
                for theme in report.themes
            ],
            'quotes': report.quotes,
            'action_ideas': report.action_ideas,
            'word_count': report.word_count,
            'review_count': report.review_count,
            'generation_timestamp': report.generation_timestamp.isoformat()
        }
