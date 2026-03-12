"""Review scraper for Google Play Store using google-play-scraper library."""
import logging
import time
import re
from datetime import datetime, timedelta
from typing import Optional
from google_play_scraper import reviews, Sort
from langdetect import detect, LangDetectException

import sys
sys.path.append('..')
from common.models import Review, ScrapingSummary, ScraperConfig

logger = logging.getLogger(__name__)


class ScrapingError(Exception):
    """Exception raised when scraping fails."""
    pass


class ReviewScraper:
    """Scrapes Google Play Store reviews for the Groww app."""
    
    # Emoji pattern for removal
    EMOJI_PATTERN = re.compile(
        "["
        "\U0001F600-\U0001F64F"  # emoticons
        "\U0001F300-\U0001F5FF"  # symbols & pictographs
        "\U0001F680-\U0001F6FF"  # transport & map symbols
        "\U0001F1E0-\U0001F1FF"  # flags (iOS)
        "\U00002702-\U000027B0"
        "\U000024C2-\U0001F251"
        "\U0001F900-\U0001F9FF"  # Supplemental Symbols and Pictographs
        "\U0001FA00-\U0001FA6F"  # Chess Symbols
        "\U0001FA70-\U0001FAFF"  # Symbols and Pictographs Extended-A
        "\U00002600-\U000026FF"  # Miscellaneous Symbols
        "\U00002700-\U000027BF"  # Dingbats
        "]+",
        flags=re.UNICODE
    )
    
    def __init__(self, config: ScraperConfig):
        """Initialize scraper with configuration."""
        self.config = config
        self.app_id = config.app_id
        self.language = config.language
        self.country = config.country
        self.batch_size = config.batch_size
        self.delay = config.delay_between_batches
        self.max_reviews = config.max_reviews
        self.min_word_count = config.min_word_count
        self.filter_non_english = config.filter_non_english
        self.remove_emojis = config.remove_emojis
    
    def scrape_reviews(
        self, 
        weeks_back: int = 10
    ) -> tuple[list[Review], ScrapingSummary]:
        """
        Scrape reviews from Google Play Store for Groww app.
        
        Phase 1 Updates:
        - Fetches up to 5,000 reviews (not 200)
        - Filters out reviews with fewer than 5 words
        - Filters out non-English reviews
        - Removes emojis from review text
        - Does not include title field in Review objects
        
        Args:
            weeks_back: Number of weeks to fetch (8-12)
        
        Returns:
            - List of Review objects
            - ScrapingSummary with counts and metadata
        
        Raises:
            - ScrapingError: If Play Store is unavailable
            - ValidationError: If weeks_back is out of range
        """
        if not 8 <= weeks_back <= 12:
            raise ValueError(f"weeks_back must be 8-12, got {weeks_back}")
        
        cutoff_date = datetime.now() - timedelta(weeks=weeks_back)
        logger.info(f"Starting scrape for {self.app_id}, cutoff date: {cutoff_date}")
        
        all_reviews = []
        warnings = []
        total_fetched = 0
        skipped_count = 0
        continuation_token = None
        language_stats = {}
        
        try:
            while total_fetched < self.max_reviews:
                # Fetch batch with retry logic
                batch_reviews, continuation_token = self._fetch_reviews_batch(
                    count=min(self.batch_size, self.max_reviews - total_fetched),
                    continuation_token=continuation_token
                )
                
                if not batch_reviews:
                    logger.info("No more reviews available")
                    break
                
                total_fetched += len(batch_reviews)
                logger.info(f"Fetched {len(batch_reviews)} reviews (total: {total_fetched})")
                
                # Process each review in the batch
                for raw_review in batch_reviews:
                    try:
                        # Check if review is within date range
                        review_date = raw_review.get('at')
                        if review_date and review_date < cutoff_date:
                            logger.debug(f"Review older than cutoff date, stopping")
                            # Stop fetching if we've reached reviews older than cutoff
                            total_fetched = self.max_reviews  # Force exit
                            break
                        
                        # Parse review
                        review = self._parse_review(raw_review)
                        
                        # Phase 1: Remove emojis from text
                        if self.remove_emojis:
                            review.text = self._remove_emojis(review.text)
                        
                        # Phase 1: Detect language
                        detected_lang = self._detect_language(review.text)
                        review.language = detected_lang
                        
                        # Track language statistics
                        language_stats[detected_lang] = language_stats.get(detected_lang, 0) + 1
                        
                        # Phase 1: Filter non-English reviews
                        if self.filter_non_english and detected_lang != 'en':
                            logger.debug(f"Skipping non-English review (language: {detected_lang})")
                            skipped_count += 1
                            warnings.append(f"Review {review.review_id}: Non-English ({detected_lang})")
                            continue
                        
                        # Phase 1: Filter by word count (minimum 5 words)
                        word_count = len(review.text.split())
                        if word_count < self.min_word_count:
                            logger.debug(f"Skipping review with {word_count} words (< {self.min_word_count})")
                            skipped_count += 1
                            warnings.append(f"Review {review.review_id}: Too short ({word_count} words)")
                            continue
                        
                        all_reviews.append(review)
                        
                    except Exception as e:
                        logger.warning(f"Failed to parse review: {e}")
                        skipped_count += 1
                        warnings.append(f"Failed to parse review: {str(e)}")
                
                # Delay between batches to avoid rate limiting
                if continuation_token and total_fetched < self.max_reviews:
                    time.sleep(self.delay)
                else:
                    break
        
        except Exception as e:
            logger.error(f"Scraping failed: {e}")
            raise ScrapingError(f"Failed to scrape reviews: {str(e)}. Please check your internet connection and try again.")
        
        # Calculate date range
        if all_reviews:
            dates = [r.date for r in all_reviews]
            date_range = (min(dates).date(), max(dates).date())
        else:
            date_range = (cutoff_date.date(), datetime.now().date())
        
        summary = ScrapingSummary(
            total_reviews=total_fetched,
            valid_reviews=len(all_reviews),
            skipped_reviews=skipped_count,
            warnings=warnings,
            date_range=date_range,
            app_id=self.app_id,
            scrape_timestamp=datetime.now(),
            language_stats=language_stats
        )
        
        logger.info(f"Scraping complete: {len(all_reviews)} valid reviews, {skipped_count} skipped")
        logger.info(f"Language distribution: {language_stats}")
        return all_reviews, summary
    
    def _remove_emojis(self, text: str) -> str:
        """Remove emojis from text."""
        return self.EMOJI_PATTERN.sub('', text).strip()
    
    def _detect_language(self, text: str) -> str:
        """
        Detect language of review text.
        
        Returns:
            Language code (e.g., 'en', 'hi', 'es') or 'unknown'
        """
        try:
            # Remove extra whitespace
            clean_text = ' '.join(text.split())
            if len(clean_text) < 3:
                return 'unknown'
            return detect(clean_text)
        except LangDetectException:
            return 'unknown'
    
    def _fetch_reviews_batch(
        self, 
        count: int = 200,
        continuation_token: Optional[str] = None
    ) -> tuple[list[dict], Optional[str]]:
        """
        Fetch a batch of reviews from Play Store with retry logic.
        
        Returns:
            - List of raw review dictionaries
            - Continuation token for next batch
        """
        max_retries = 3
        for attempt in range(max_retries):
            try:
                result, token = reviews(
                    self.app_id,
                    lang=self.language,
                    country=self.country,
                    sort=Sort.NEWEST,
                    count=count,
                    continuation_token=continuation_token
                )
                return result, token
            
            except Exception as e:
                if attempt == max_retries - 1:
                    raise
                wait_time = 2 ** attempt
                logger.warning(f"Fetch attempt {attempt + 1} failed, retrying in {wait_time}s: {e}")
                time.sleep(wait_time)
        
        return [], None
    
    def _parse_review(self, raw_review: dict) -> Review:
        """
        Parse raw review data into Review object.
        
        Phase 1: Does not include title field.
        
        Args:
            raw_review: Dictionary from google-play-scraper
        
        Returns:
            Review object with validated fields
        """
        # Extract required fields
        rating = raw_review.get('score')
        text = raw_review.get('content', '')
        review_date = raw_review.get('at')
        review_id = raw_review.get('reviewId', '')
        
        # Validate required fields
        if not text:
            raise ValueError("Review content is missing")
        if not rating or not isinstance(rating, int):
            raise ValueError(f"Invalid rating: {rating}")
        if not 1 <= rating <= 5:
            raise ValueError(f"Rating must be 1-5, got {rating}")
        if not review_date:
            raise ValueError("Review date is missing")
        
        # Create Review object (no title field in Phase 1)
        return Review(
            rating=rating,
            text=text.strip(),
            date=review_date,
            review_id=review_id or f"review_{datetime.now().timestamp()}",
            is_sanitized=False,
            language=None  # Will be set later
        )
