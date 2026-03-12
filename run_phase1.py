"""Execute Phase 1: Scrape reviews and filter PII."""
import logging
import json
from datetime import datetime

from config import Config
from app.models import ScraperConfig
from app.review_scraper import ReviewScraper
from app.pii_filter import PIIFilter

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    """Run Phase 1 pipeline: Scrape and filter reviews."""
    logger.info("=" * 80)
    logger.info("PHASE 1: Review Scraping and PII Filtering")
    logger.info("=" * 80)
    
    # Initialize scraper configuration
    scraper_config = ScraperConfig(
        app_id=Config.APP_ID,
        language=Config.SCRAPER_LANGUAGE,
        country=Config.SCRAPER_COUNTRY,
        batch_size=Config.SCRAPER_BATCH_SIZE,
        delay_between_batches=Config.SCRAPER_DELAY,
        max_reviews=Config.SCRAPER_MAX_REVIEWS,  # 5000 reviews
        min_word_count=Config.SCRAPER_MIN_WORD_COUNT  # 5 words minimum
    )
    
    logger.info(f"Configuration:")
    logger.info(f"  App ID: {scraper_config.app_id}")
    logger.info(f"  Max Reviews: {scraper_config.max_reviews}")
    logger.info(f"  Min Word Count: {scraper_config.min_word_count}")
    logger.info(f"  Batch Size: {scraper_config.batch_size}")
    logger.info("")
    
    # Step 1: Scrape reviews
    logger.info("Step 1: Scraping reviews from Google Play Store...")
    scraper = ReviewScraper(scraper_config)
    
    try:
        reviews, scraping_summary = scraper.scrape_reviews(weeks_back=10)
        
        logger.info(f"Scraping complete!")
        logger.info(f"  Total fetched: {scraping_summary.total_reviews}")
        logger.info(f"  Valid reviews: {scraping_summary.valid_reviews}")
        logger.info(f"  Skipped reviews: {scraping_summary.skipped_reviews}")
        logger.info(f"  Date range: {scraping_summary.date_range[0]} to {scraping_summary.date_range[1]}")
        
        if scraping_summary.warnings:
            logger.warning(f"  Warnings: {len(scraping_summary.warnings)}")
            for warning in scraping_summary.warnings[:5]:  # Show first 5 warnings
                logger.warning(f"    - {warning}")
        
        logger.info("")
        
    except Exception as e:
        logger.error(f"Scraping failed: {e}")
        return
    
    # Step 2: Filter PII
    logger.info("Step 2: Filtering PII from reviews...")
    pii_filter = PIIFilter()
    
    try:
        sanitized_reviews, pii_summary = pii_filter.filter_reviews(reviews)
        
        logger.info(f"PII filtering complete!")
        logger.info(f"  Reviews processed: {pii_summary.reviews_processed}")
        logger.info(f"  PII instances found: {pii_summary.pii_instances_found}")
        logger.info(f"  PII by type:")
        for pii_type, count in pii_summary.pii_by_type.items():
            if count > 0:
                logger.info(f"    - {pii_type}: {count}")
        
        logger.info("")
        
    except Exception as e:
        logger.error(f"PII filtering failed: {e}")
        return
    
    # Step 3: Save results
    logger.info("Step 3: Saving results...")
    
    # Save sanitized reviews to JSON
    output_data = {
        'metadata': {
            'app_id': scraper_config.app_id,
            'scrape_timestamp': scraping_summary.scrape_timestamp.isoformat(),
            'date_range': [
                scraping_summary.date_range[0].isoformat(),
                scraping_summary.date_range[1].isoformat()
            ],
            'total_reviews': scraping_summary.valid_reviews,
            'pii_instances_removed': pii_summary.pii_instances_found,
            'pii_by_type': pii_summary.pii_by_type
        },
        'reviews': [
            {
                'review_id': review.review_id,
                'rating': review.rating,
                'text': review.text,
                'date': review.date.isoformat(),
                'is_sanitized': review.is_sanitized
            }
            for review in sanitized_reviews
        ]
    }
    
    output_file = f"phase1_output_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)
    
    logger.info(f"Results saved to: {output_file}")
    logger.info("")
    
    # Summary
    logger.info("=" * 80)
    logger.info("PHASE 1 COMPLETE")
    logger.info("=" * 80)
    logger.info(f"✓ Scraped {scraping_summary.valid_reviews} reviews from {scraper_config.app_id}")
    logger.info(f"✓ Filtered {pii_summary.pii_instances_found} PII instances")
    logger.info(f"✓ Output saved to {output_file}")
    logger.info("")
    logger.info("Phase 1 Updates Applied:")
    logger.info(f"  ✓ Scaled to {scraper_config.max_reviews} reviews (not 200)")
    logger.info(f"  ✓ Length filter: Discarded reviews with < {scraper_config.min_word_count} words")
    logger.info(f"  ✓ Title field removed from output (only review body and metadata)")
    logger.info("=" * 80)


if __name__ == '__main__':
    main()
