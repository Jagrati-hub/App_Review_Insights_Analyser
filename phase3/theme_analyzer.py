"""Theme analysis using Groq LLM."""
import logging
from datetime import datetime
from typing import Optional

import sys
sys.path.append('..')
from common.models import Review, Theme, AnalysisMetadata, GroqConfig
from phase3.groq_client import GroqClient, GroqAPIError, AuthenticationError

logger = logging.getLogger(__name__)


class ThemeAnalyzer:
    """Analyzes reviews to identify common themes using Groq LLM."""
    
    def __init__(self, config: GroqConfig):
        """Initialize theme analyzer with Groq configuration."""
        self.config = config
        self.client = GroqClient(config)
        self.model = config.model
        logger.info("Theme analyzer initialized")
    
    def analyze_themes(
        self,
        reviews: list[Review],
        max_themes: int = 5,
        batch_size: int = 150  # Reduced from 200 to 150 for faster processing
    ) -> tuple[list[Theme], AnalysisMetadata]:
        """
        Identify themes across reviews using Groq LLM.
        
        Args:
            reviews: List of Review objects to analyze
            max_themes: Maximum number of themes to identify (default: 5)
            batch_size: Number of reviews to process at once (default: 200)
        
        Returns:
            - List of Theme objects (max 5) ranked by frequency
            - AnalysisMetadata with model info and timestamp
        
        Raises:
            GroqAPIError: If API call fails
            AuthenticationError: If API key is invalid
        """
        if not reviews:
            logger.warning("No reviews provided for theme analysis")
            return [], AnalysisMetadata(
                model_version=self.model,
                timestamp=datetime.now(),
                total_themes=0,
                total_reviews=0
            )
        
        logger.info(f"Analyzing {len(reviews)} reviews for themes (max: {max_themes})")
        
        # If reviews exceed batch size, sample them
        if len(reviews) > batch_size:
            logger.info(f"Sampling {batch_size} reviews from {len(reviews)} total reviews")
            import random
            sampled_reviews = random.sample(reviews, batch_size)
        else:
            sampled_reviews = reviews
        
        # Prepare reviews for LLM
        review_list = self._format_reviews_for_llm(sampled_reviews)
        
        # Create prompt for theme identification
        prompt = self._create_theme_identification_prompt(review_list, max_themes)
        
        # Call Groq API
        try:
            response = self.client.chat_completion(
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert at analyzing user feedback and identifying common themes. You provide structured JSON responses."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.3,  # Lower temperature for more consistent analysis
                max_tokens=2000
            )
            
            # Parse response
            themes_data = self.client.parse_json_response(response)
            
            # Create Theme objects (map back to original reviews)
            themes = self._create_theme_objects(themes_data, sampled_reviews, reviews)
            
            # Create metadata
            metadata = AnalysisMetadata(
                model_version=self.model,
                timestamp=datetime.now(),
                total_themes=len(themes),
                total_reviews=len(reviews)
            )
            
            logger.info(f"Theme analysis complete: {len(themes)} themes identified")
            return themes, metadata
        
        except (GroqAPIError, AuthenticationError) as e:
            logger.error(f"Theme analysis failed: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error during theme analysis: {e}")
            raise GroqAPIError(f"Theme analysis failed: {str(e)}")
    
    def _format_reviews_for_llm(self, reviews: list[Review]) -> str:
        """Format reviews as numbered list for LLM."""
        formatted = []
        for i, review in enumerate(reviews):
            formatted.append(f"{i}. [Rating: {review.rating}/5] {review.text}")
        return "\n".join(formatted)
    
    def _create_theme_identification_prompt(self, review_list: str, max_themes: int) -> str:
        """Create prompt for theme identification."""
        return f"""You are analyzing Google Play Store reviews for the Groww investment app to identify common themes.

Reviews:
{review_list}

Task: Identify up to {max_themes} distinct themes that appear across these reviews. For each theme:
1. Provide a concise label (2-4 words)
2. Provide a brief description (1-2 sentences)
3. List the review indices that belong to this theme
4. Count the frequency (number of reviews)
5. Rank themes by frequency (most common first)

Output format (JSON):
{{
  "themes": [
    {{
      "label": "Theme Label",
      "description": "Brief description of what this theme is about",
      "review_indices": [0, 3, 7],
      "frequency": 3,
      "rank": 1
    }}
  ]
}}

Requirements:
- Maximum {max_themes} themes
- Each review must be assigned to at least one theme (reviews can belong to multiple themes)
- Themes should be distinct and non-overlapping where possible
- Focus on actionable product/UX issues, features, and user sentiments
- Rank themes by frequency (rank 1 = most common)
- Ensure all review indices are valid (0 to {len(review_list.split(chr(10))) - 1})

Provide ONLY the JSON output, no additional text."""
    
    def _create_theme_objects(self, themes_data: dict, sampled_reviews: list[Review], all_reviews: list[Review]) -> list[Theme]:
        """Create Theme objects from LLM response and map to all reviews."""
        themes = []
        
        if 'themes' not in themes_data:
            logger.warning("No 'themes' key in LLM response")
            return themes
        
        for theme_data in themes_data['themes']:
            try:
                # Extract theme data
                label = theme_data.get('label', 'Unknown Theme')
                description = theme_data.get('description', '')
                review_indices = theme_data.get('review_indices', [])
                rank = theme_data.get('rank', len(themes) + 1)
                
                # Get sample reviews for this theme
                theme_sample_reviews = []
                for idx in review_indices:
                    if 0 <= idx < len(sampled_reviews):
                        theme_sample_reviews.append(sampled_reviews[idx])
                
                # Map theme to all reviews by matching text patterns
                theme_all_reviews = self._map_theme_to_all_reviews(
                    label, description, theme_sample_reviews, all_reviews
                )
                
                # Create Theme object
                if theme_all_reviews:  # Only create theme if it has reviews
                    theme = Theme(
                        label=label,
                        description=description,
                        reviews=theme_all_reviews,
                        frequency=len(theme_all_reviews),
                        rank=rank
                    )
                    themes.append(theme)
                    logger.debug(f"Created theme: {label} (frequency: {len(theme_all_reviews)})")
            
            except Exception as e:
                logger.warning(f"Failed to create theme from data: {e}")
                continue
        
        # Sort themes by frequency (descending) and update ranks
        themes.sort(key=lambda t: t.frequency, reverse=True)
        for i, theme in enumerate(themes):
            theme.rank = i + 1
        
        return themes
    
    def _map_theme_to_all_reviews(
        self, 
        label: str, 
        description: str, 
        sample_reviews: list[Review], 
        all_reviews: list[Review]
    ) -> list[Review]:
        """Map theme to all reviews by finding similar reviews."""
        # Extract keywords from sample reviews
        keywords = set()
        for review in sample_reviews:
            words = review.text.lower().split()
            keywords.update([w for w in words if len(w) > 4])  # Words longer than 4 chars
        
        # Find all reviews that match the theme
        matched_reviews = []
        for review in all_reviews:
            review_words = set(review.text.lower().split())
            # If review shares keywords with theme, include it
            if keywords & review_words:  # Intersection
                matched_reviews.append(review)
        
        return matched_reviews if matched_reviews else sample_reviews
