"""Data models for Play Store Review Analyzer."""
from dataclasses import dataclass, field
from datetime import datetime, date
from typing import Optional


@dataclass
class Review:
    """A Google Play Store review (Phase 1: No title field)."""
    
    rating: int  # 1-5 stars
    text: str  # Review body text
    date: datetime  # Review submission date
    review_id: str  # Unique identifier
    is_sanitized: bool = False  # PII removal flag
    language: Optional[str] = None  # Detected language code
    
    def __post_init__(self):
        """Validate review data."""
        if not 1 <= self.rating <= 5:
            raise ValueError(f"Rating must be 1-5, got {self.rating}")
        if not self.text:
            raise ValueError("Text is required")


@dataclass
class Theme:
    """A theme identified across reviews."""
    
    label: str  # Short descriptive label (2-4 words)
    description: str  # Brief explanation of theme
    reviews: list[Review]  # Reviews belonging to this theme
    frequency: int  # Number of reviews in theme
    rank: int  # Ranking by frequency (1 = most common)
    average_rating: Optional[float] = None  # Average rating for this theme
    
    def __post_init__(self):
        """Validate theme data."""
        if self.frequency != len(self.reviews):
            raise ValueError("Frequency must match review count")
        if self.rank < 1:
            raise ValueError("Rank must be positive")
        
        # Calculate average rating if not provided
        if self.average_rating is None and self.reviews:
            self.average_rating = sum(r.rating for r in self.reviews) / len(self.reviews)


@dataclass
class PulseReport:
    """Weekly pulse report containing themes, quotes, and actions."""
    
    date_range: tuple[date, date]  # Report coverage period
    themes: list[Theme]  # Top 3 themes
    quotes: list[str]  # 3 representative user quotes
    action_ideas: list[str]  # 3 actionable suggestions
    word_count: int  # Total word count
    review_count: int  # Total reviews analyzed
    generation_timestamp: datetime  # When report was created
    average_rating: Optional[float] = None  # Average rating across all reviews
    positive_count: Optional[int] = None  # Count of positive reviews (4-5 stars)
    negative_count: Optional[int] = None  # Count of negative reviews (1-3 stars)
    
    def __post_init__(self):
        """Validate report constraints."""
        if len(self.themes) != 3:
            raise ValueError("Report must contain exactly 3 themes")
        if len(self.quotes) != 3:
            raise ValueError("Report must contain exactly 3 quotes")
        if len(self.action_ideas) != 3:
            raise ValueError("Report must contain exactly 3 action ideas")
        if self.word_count > 250:
            raise ValueError(f"Report exceeds 250 word limit: {self.word_count}")


@dataclass
class ScrapingSummary:
    """Summary of review scraping operation."""
    total_reviews: int
    valid_reviews: int
    skipped_reviews: int
    warnings: list[str]
    date_range: tuple[date, date]
    app_id: str
    scrape_timestamp: datetime
    language_stats: Optional[dict[str, int]] = None  # Language distribution


@dataclass
class PIISummary:
    """Summary of PII detection and removal."""
    reviews_processed: int
    pii_instances_found: int
    pii_by_type: dict[str, int]  # e.g., {"email": 5, "phone": 2}


@dataclass
class AnalysisMetadata:
    """Metadata from theme analysis."""
    model_version: str
    timestamp: datetime
    total_themes: int
    total_reviews: int


@dataclass
class GenerationMetadata:
    """Metadata from report generation."""
    timestamp: datetime
    word_count: int
    model_version: str


@dataclass
class DraftMetadata:
    """Metadata from email draft creation."""
    recipient: str
    timestamp: datetime
    output_path: str
    email_sent: bool = False  # Whether email was sent via SMTP
    error_message: Optional[str] = None  # Error details if sending failed


@dataclass
class GroqConfig:
    """Configuration for Groq LLM integration."""
    api_key: str
    model: str = "mixtral-8x7b-32768"
    timeout: int = 30  # seconds
    max_retries: int = 3


@dataclass
class ScraperConfig:
    """Configuration for review scraping."""
    app_id: str = "com.nextbillion.groww"
    language: str = "en"
    country: str = "us"
    batch_size: int = 200
    delay_between_batches: float = 1.0  # seconds
    max_reviews: int = 5000  # Phase 1: Scale to 5000
    min_word_count: int = 5  # Phase 1: Filter reviews with <5 words
    filter_non_english: bool = True  # Phase 1: Filter non-English reviews
    remove_emojis: bool = True  # Phase 1: Remove emojis from text


@dataclass
class SystemConfig:
    """Overall system configuration."""
    groq: GroqConfig
    scraper: ScraperConfig
    min_weeks: int = 8
    max_weeks: int = 12
    max_themes: int = 5
    report_word_limit: int = 250
    quote_count: int = 3
    action_count: int = 3


@dataclass
class AnalysisRequest:
    """User request for analysis via UI."""
    weeks_back: int  # 8-12
    recipient_email: str
    request_timestamp: datetime
    request_id: str  # Unique identifier
    
    def __post_init__(self):
        """Validate request parameters."""
        if not 8 <= self.weeks_back <= 12:
            raise ValueError(f"weeks_back must be 8-12, got {self.weeks_back}")
        if not self.recipient_email or '@' not in self.recipient_email:
            raise ValueError("Invalid email address")


@dataclass
class PipelineStatus:
    """Current status of analysis pipeline."""
    request_id: str
    status: str  # 'pending', 'scraping', 'filtering', 'analyzing', 'generating', 'complete', 'error'
    current_step: str  # Human-readable current step
    progress_percent: int  # 0-100
    error_message: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    
    def __post_init__(self):
        """Validate status values."""
        valid_statuses = ['pending', 'scraping', 'filtering', 'analyzing', 'generating', 'complete', 'error']
        if self.status not in valid_statuses:
            raise ValueError(f"Invalid status: {self.status}")
        if not 0 <= self.progress_percent <= 100:
            raise ValueError(f"Progress must be 0-100, got {self.progress_percent}")


@dataclass
class ReportView:
    """Report data formatted for UI display."""
    report_id: str
    pulse_report: PulseReport
    email_draft: str
    recipient: str
    created_at: datetime
    is_sent: bool = False
    sent_at: Optional[datetime] = None
