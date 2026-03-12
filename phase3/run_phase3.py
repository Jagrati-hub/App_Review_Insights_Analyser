"""Execute Phase 3: Theme Analysis using Groq LLM."""
import logging
import json
from datetime import datetime
import sys
sys.path.append('..')

from common.config import Config
from common.models import Review, GroqConfig
from phase3.theme_analyzer import ThemeAnalyzer
from phase3.groq_client import GroqAPIError, AuthenticationError

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def load_phase1_reviews(phase1_output_file: str) -> list[Review]:
    """Load reviews from Phase 1 output file."""
    logger.info(f"Loading reviews from: {phase1_output_file}")
    
    with open(phase1_output_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    reviews = []
    for review_data in data['reviews']:
        review = Review(
            rating=review_data['rating'],
            text=review_data['text'],
            date=datetime.fromisoformat(review_data['date']),
            review_id=review_data['review_id'],
            is_sanitized=review_data['is_sanitized'],
            language=review_data.get('language', 'en')
        )
        reviews.append(review)
    
    logger.info(f"Loaded {len(reviews)} reviews from Phase 1")
    return reviews


def main():
    """Run Phase 3 pipeline: Theme Analysis."""
    logger.info("=" * 80)
    logger.info("PHASE 3: Theme Analysis using Groq LLM")
    logger.info("=" * 80)
    
    # Configuration
    groq_config = GroqConfig(
        api_key=Config.GROQ_API_KEY,
        model=Config.GROQ_MODEL,
        timeout=Config.GROQ_TIMEOUT,
        max_retries=Config.GROQ_MAX_RETRIES
    )
    
    logger.info(f"Configuration:")
    logger.info(f"  Groq Model: {groq_config.model}")
    logger.info(f"  Max Themes: {Config.MAX_THEMES}")
    logger.info(f"  Timeout: {groq_config.timeout}s")
    logger.info("")
    
    # Step 1: Load Phase 1 reviews
    logger.info("Step 1: Loading filtered reviews from Phase 1...")
    
    # Find the latest Phase 1 output file
    import os
    import glob
    
    phase1_output_dir = '../phase1/phase1/output'
    if not os.path.exists(phase1_output_dir):
        logger.error(f"Phase 1 output directory not found: {phase1_output_dir}")
        logger.error("Please run Phase 1 first to generate filtered reviews.")
        return
    
    # Get the latest output file
    output_files = glob.glob(f"{phase1_output_dir}/phase1_output_*.json")
    if not output_files:
        logger.error("No Phase 1 output files found.")
        logger.error("Please run Phase 1 first to generate filtered reviews.")
        return
    
    latest_file = max(output_files, key=os.path.getctime)
    logger.info(f"Using Phase 1 output: {latest_file}")
    
    try:
        reviews = load_phase1_reviews(latest_file)
        logger.info(f"✓ Loaded {len(reviews)} reviews")
        logger.info("")
    except Exception as e:
        logger.error(f"Failed to load Phase 1 reviews: {e}")
        return
    
    # Step 2: Analyze themes
    logger.info("Step 2: Analyzing themes with Groq LLM...")
    logger.info("This may take a minute...")
    
    analyzer = ThemeAnalyzer(groq_config)
    
    try:
        themes, metadata = analyzer.analyze_themes(
            reviews=reviews,
            max_themes=Config.MAX_THEMES
        )
        
        logger.info(f"Theme analysis complete!")
        logger.info(f"  Themes identified: {len(themes)}")
        logger.info(f"  Model used: {metadata.model_version}")
        logger.info(f"  Analysis timestamp: {metadata.timestamp}")
        logger.info("")
        
        # Display themes
        logger.info("Identified Themes:")
        for theme in themes:
            logger.info(f"  {theme.rank}. {theme.label} (frequency: {theme.frequency})")
            logger.info(f"     {theme.description}")
            logger.info("")
        
    except AuthenticationError as e:
        logger.error(f"Authentication failed: {e}")
        logger.error("Please set your GROQ_API_KEY in the .env file")
        return
    except GroqAPIError as e:
        logger.error(f"Theme analysis failed: {e}")
        return
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return
    
    # Step 3: Save results
    logger.info("Step 3: Saving results...")
    
    # Prepare output data
    output_data = {
        'metadata': {
            'model_version': metadata.model_version,
            'analysis_timestamp': metadata.timestamp.isoformat(),
            'total_themes': metadata.total_themes,
            'total_reviews': metadata.total_reviews,
            'max_themes': Config.MAX_THEMES
        },
        'themes': [
            {
                'rank': theme.rank,
                'label': theme.label,
                'description': theme.description,
                'frequency': theme.frequency,
                'review_count': len(theme.reviews),
                'sample_reviews': [
                    {
                        'review_id': review.review_id,
                        'rating': review.rating,
                        'text': review.text[:200] + '...' if len(review.text) > 200 else review.text
                    }
                    for review in theme.reviews[:5]  # Include first 5 reviews as samples
                ]
            }
            for theme in themes
        ]
    }
    
    # Create output directory
    os.makedirs('phase3/output', exist_ok=True)
    
    output_file = f"phase3/output/phase3_output_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)
    
    logger.info(f"Results saved to: {output_file}")
    logger.info("")
    
    # Summary
    logger.info("=" * 80)
    logger.info("PHASE 3 COMPLETE")
    logger.info("=" * 80)
    logger.info(f"✓ Analyzed {len(reviews)} reviews")
    logger.info(f"✓ Identified {len(themes)} themes")
    logger.info(f"✓ Output saved to {output_file}")
    logger.info("")
    logger.info("Top 3 Themes:")
    for theme in themes[:3]:
        logger.info(f"  {theme.rank}. {theme.label} ({theme.frequency} reviews)")
    logger.info("=" * 80)


if __name__ == '__main__':
    main()
