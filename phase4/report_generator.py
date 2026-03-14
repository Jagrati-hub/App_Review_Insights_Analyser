"""Report Generator for creating weekly pulse reports from themes."""
import json
import random
from datetime import datetime, date
from typing import Optional
from groq import Groq

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from common.models import Theme, PulseReport, GenerationMetadata
from common.config import Config


class ReportGenerator:
    """Generates weekly pulse reports from analyzed themes."""
    
    def __init__(self, groq_api_key: Optional[str] = None):
        """Initialize report generator with Groq API client.
        
        Args:
            groq_api_key: Groq API key (defaults to Config.GROQ_API_KEY)
        """
        self.api_key = groq_api_key or Config.GROQ_API_KEY
        if not self.api_key:
            raise ValueError("Groq API key is required")
        
        self.client = Groq(api_key=self.api_key)
        self.model = Config.GROQ_MODEL
        self.timeout = Config.GROQ_TIMEOUT
        self.max_retries = Config.GROQ_MAX_RETRIES
        self.word_limit = Config.REPORT_WORD_LIMIT
        self.quote_count = Config.QUOTE_COUNT
        self.action_count = Config.ACTION_COUNT
    
    def generate_report(
        self,
        themes: list[Theme],
        date_range: tuple[date, date],
        total_review_count: int
    ) -> tuple[PulseReport, GenerationMetadata]:
        """Generate a weekly pulse report from themes.
        
        Args:
            themes: List of Theme objects (must have at least 2)
            date_range: Tuple of (start_date, end_date) for report coverage
            total_review_count: Total number of reviews analyzed
        
        Returns:
            Tuple of (PulseReport, GenerationMetadata)
        
        Raises:
            ValueError: If themes list has fewer than 2 themes
            Exception: If action idea generation fails after retries
        """
        if len(themes) < 2:
            raise ValueError(f"Need at least 2 themes to generate report, got {len(themes)}")
        
        # Step 1: Select top 3 themes by frequency
        top_themes = self._select_top_themes(themes)
        
        # Step 2: Calculate overall statistics from all reviews across themes
        all_reviews = []
        for theme in themes:
            all_reviews.extend(theme.reviews)
        
        # Remove duplicates (same review might be in multiple themes)
        unique_reviews = {r.review_id: r for r in all_reviews}.values()
        
        average_rating = sum(r.rating for r in unique_reviews) / len(unique_reviews) if unique_reviews else 0.0
        positive_count = sum(1 for r in unique_reviews if r.rating >= 4)
        negative_count = sum(1 for r in unique_reviews if r.rating <= 3)
        
        # Step 3: Select 3 quotes from different themes
        quotes = self._select_quotes(top_themes)
        
        # Step 4: Generate 3 action ideas using Groq LLM
        action_ideas = self._generate_action_ideas(top_themes)
        
        # Step 5: Calculate word count
        word_count = self._calculate_word_count(top_themes, quotes, action_ideas)
        
        # Step 6: If word count exceeds limit, trim action ideas
        if word_count > self.word_limit:
            # Try to trim action ideas to fit within limit
            words_over = word_count - self.word_limit
            action_ideas = self._trim_action_ideas(action_ideas, words_over + 5)  # Add buffer
            word_count = self._calculate_word_count(top_themes, quotes, action_ideas)
            
            # If still over limit, trim quotes
            if word_count > self.word_limit:
                words_over = word_count - self.word_limit
                quotes = self._trim_quotes(quotes, words_over + 5)  # Add buffer
                word_count = self._calculate_word_count(top_themes, quotes, action_ideas)
            
            # Final check: if still over, do aggressive trimming
            if word_count > self.word_limit:
                words_over = word_count - self.word_limit
                # Trim both quotes and action ideas more aggressively
                action_ideas = self._trim_action_ideas(action_ideas, words_over // 2 + 3)
                quotes = self._trim_quotes(quotes, words_over // 2 + 3)
                word_count = self._calculate_word_count(top_themes, quotes, action_ideas)
        
        # Step 7: Create PulseReport
        report = PulseReport(
            date_range=date_range,
            themes=top_themes,
            quotes=quotes,
            action_ideas=action_ideas,
            word_count=word_count,
            review_count=total_review_count,
            generation_timestamp=datetime.now(),
            average_rating=round(average_rating, 2),
            positive_count=positive_count,
            negative_count=negative_count
        )
        
        # Step 8: Create metadata
        metadata = GenerationMetadata(
            timestamp=datetime.now(),
            word_count=word_count,
            model_version=self.model
        )
        
        return report, metadata
    
    def _select_top_themes(self, themes: list[Theme]) -> list[Theme]:
        """Select top 3 themes by frequency.
        
        Args:
            themes: List of Theme objects sorted by rank
        
        Returns:
            List of top 3 themes (or fewer if less than 3 available)
        """
        # Sort by rank (ascending) to ensure we get top themes
        sorted_themes = sorted(themes, key=lambda t: t.rank)
        
        # Return top 3 (or all if fewer than 3)
        return sorted_themes[:3]
    
    def _select_quotes(self, themes: list[Theme]) -> list[str]:
        """Select 3 representative quotes from different themes.
        
        Strategy:
        - Select one quote from each of the top 3 themes (ensures diversity)
        - Prefer quotes that best represent the theme's sentiment
        - Avoid duplicates by tracking selected review texts
        - For negative themes: prefer lower ratings (1-3 stars)
        - For positive themes: prefer higher ratings (4-5 stars)
        - Prefer moderate length quotes (50-200 characters)
        
        Args:
            themes: List of top themes (2-3 themes)
        
        Returns:
            List of 3 unique quote strings
        """
        quotes = []
        selected_texts = set()  # Track selected quotes to prevent duplicates
        
        for theme in themes:
            if not theme.reviews:
                continue
            
            # Determine if theme is positive or negative based on description
            is_positive_theme = self._is_positive_theme(theme)
            
            # Score reviews for quote selection
            scored_reviews = []
            for review in theme.reviews:
                # Skip if already selected
                if review.text in selected_texts:
                    continue
                
                score = self._score_review_for_quote(review, is_positive_theme)
                scored_reviews.append((score, review))
            
            # Sort by score (descending) and select best
            scored_reviews.sort(key=lambda x: x[0], reverse=True)
            
            if scored_reviews:
                best_review = scored_reviews[0][1]
                quotes.append(best_review.text)
                selected_texts.add(best_review.text)
        
        # If we have fewer than 3 quotes (edge case with <3 themes or empty reviews)
        # Fill remaining slots with diverse quotes from available themes
        while len(quotes) < 3 and themes:
            for theme in themes:
                if len(quotes) >= 3:
                    break
                if theme.reviews:
                    # Pick the best available review not already selected
                    is_positive_theme = self._is_positive_theme(theme)
                    available = [
                        (self._score_review_for_quote(r, is_positive_theme), r)
                        for r in theme.reviews 
                        if r.text not in selected_texts
                    ]
                    if available:
                        available.sort(key=lambda x: x[0], reverse=True)
                        best_review = available[0][1]
                        quotes.append(best_review.text)
                        selected_texts.add(best_review.text)
        
        return quotes[:3]  # Ensure exactly 3 quotes
    
    def _is_positive_theme(self, theme: Theme) -> bool:
        """Determine if a theme is positive or negative based on keywords.
        
        Args:
            theme: Theme object
        
        Returns:
            True if theme is positive, False if negative
        """
        # Keywords indicating negative themes
        negative_keywords = [
            'issue', 'problem', 'bug', 'error', 'crash', 'slow', 'bad', 'poor',
            'worst', 'terrible', 'fail', 'broken', 'charge', 'expensive', 'high',
            'complaint', 'unhappy', 'disappointed', 'frustrat'
        ]
        
        # Keywords indicating positive themes
        positive_keywords = [
            'easy', 'good', 'great', 'excellent', 'best', 'love', 'like',
            'helpful', 'useful', 'simple', 'smooth', 'fast', 'convenient',
            'recommend', 'satisfied', 'happy', 'positive'
        ]
        
        theme_text = (theme.label + ' ' + theme.description).lower()
        
        # Count keyword matches
        negative_count = sum(1 for kw in negative_keywords if kw in theme_text)
        positive_count = sum(1 for kw in positive_keywords if kw in theme_text)
        
        # If more positive keywords, it's a positive theme
        return positive_count > negative_count
    
    def _score_review_for_quote(self, review, is_positive_theme: bool = True) -> float:
        """Score a review for quote selection based on theme sentiment.
        
        Scoring criteria:
        - Length: Prefer 50-200 characters (moderate length)
        - Rating alignment: 
          * For negative themes: prefer lower ratings (1-3 stars) for authenticity
          * For positive themes: prefer higher ratings (4-5 stars)
        - Avoid very short or very long reviews
        - Bonus for reviews that are clear and specific
        
        Args:
            review: Review object
            is_positive_theme: Whether the theme is positive or negative
        
        Returns:
            Score (higher is better)
        """
        score = 0.0
        text_len = len(review.text)
        
        # Length scoring (prefer moderate length)
        if 50 <= text_len <= 200:
            score += 10.0
        elif 30 <= text_len < 50 or 200 < text_len <= 300:
            score += 5.0
        elif text_len < 30:
            score += 1.0  # Too short
        else:
            score += 2.0  # Too long
        
        # Rating scoring based on theme sentiment
        if is_positive_theme:
            # For positive themes: prefer higher ratings (4-5 stars)
            if review.rating >= 4:
                score += 15.0
            elif review.rating == 3:
                score += 5.0
            else:
                score += 2.0
        else:
            # For negative themes: prefer lower ratings (1-3 stars) for authenticity
            if review.rating <= 2:
                score += 15.0
            elif review.rating == 3:
                score += 10.0
            else:
                score += 5.0
        
        # Bonus for reviews with specific details (contains numbers, specific words)
        if any(char.isdigit() for char in review.text):
            score += 3.0
        
        return score
    
    def _trim_action_ideas(self, action_ideas: list[str], words_to_remove: int) -> list[str]:
        """Trim action ideas to reduce word count.
        
        Strategy: Shorten each action idea proportionally
        
        Args:
            action_ideas: List of action idea strings
            words_to_remove: Number of words to remove
        
        Returns:
            Trimmed list of action ideas
        """
        if words_to_remove <= 0:
            return action_ideas
            
        trimmed = []
        words_per_idea = max(1, words_to_remove // len(action_ideas))
        
        for idea in action_ideas:
            words = idea.split()
            # Calculate how many words to keep (remove proportionally)
            words_to_keep = max(8, len(words) - words_per_idea)
            trimmed_idea = ' '.join(words[:words_to_keep])
            if len(words) > words_to_keep:
                trimmed_idea += '...'
            trimmed.append(trimmed_idea)
        return trimmed
    
    def _trim_quotes(self, quotes: list[str], words_to_remove: int) -> list[str]:
        """Trim quotes to reduce word count.
        
        Strategy: Shorten longer quotes first
        
        Args:
            quotes: List of quote strings
            words_to_remove: Number of words to remove
        
        Returns:
            Trimmed list of quotes
        """
        if words_to_remove <= 0:
            return quotes
            
        trimmed = []
        words_per_quote = max(1, words_to_remove // len(quotes))
        
        for quote in quotes:
            words = quote.split()
            # Calculate how many words to keep
            words_to_keep = max(12, len(words) - words_per_quote)
            trimmed_quote = ' '.join(words[:words_to_keep])
            if len(words) > words_to_keep:
                trimmed_quote += '...'
            trimmed.append(trimmed_quote)
        return trimmed
    
    def _generate_action_ideas(self, themes: list[Theme]) -> list[str]:
        """Generate 3 actionable ideas using Groq LLM.
        
        Args:
            themes: List of top themes
        
        Returns:
            List of 3 action idea strings
        
        Raises:
            Exception: If generation fails after max retries
        """
        # Prepare theme summaries for prompt
        theme_summaries = []
        for i, theme in enumerate(themes, 1):
            theme_summaries.append(
                f"{i}. {theme.label} ({theme.frequency} reviews): {theme.description}"
            )
        
        themes_text = "\n".join(theme_summaries)
        
        # Create prompt for action idea generation
        prompt = f"""Based on the following user feedback themes from Google Play Store reviews, generate exactly 3 specific, actionable items that the product team should implement.

THEMES:
{themes_text}

REQUIREMENTS:
- Format each item as: "Action Title → Step 1 → Step 2 → Expected Outcome"
- Every item MUST have all 4 parts separated by →
- Each part must be a complete phrase (NO truncation, NO ellipsis)
- Keep each full item under 40 words
- Make them practical and specific to the themes

EXAMPLE:
["Improve Onboarding → Simplify KYC flow → Add progress indicators → Reduce drop-off by 30%", "Fix Performance → Optimize API calls → Implement caching → Reduce load time to under 2 seconds", "Enhance Support → Add in-app chat → Train AI bot → Resolve 80 percent of queries instantly"]

Return ONLY a valid JSON array with exactly 3 strings. No other text."""
        
        # Call Groq API with retry logic
        for attempt in range(self.max_retries):
            try:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {
                            "role": "system",
                            "content": "You are a product manager expert at analyzing user feedback and generating actionable product improvements."
                        },
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    temperature=0.7,
                    max_tokens=800,
                    timeout=self.timeout
                )
                
                # Parse response
                content = response.choices[0].message.content.strip()
                
                # Try to extract JSON array
                action_ideas = self._parse_action_ideas(content)
                
                if len(action_ideas) == 3:
                    return action_ideas
                else:
                    print(f"Warning: Expected 3 action ideas, got {len(action_ideas)}. Retrying...")
                    continue
                
            except Exception as e:
                print(f"Attempt {attempt + 1}/{self.max_retries} failed: {str(e)}")
                if attempt == self.max_retries - 1:
                    raise Exception(
                        f"Failed to generate action ideas after {self.max_retries} attempts: {str(e)}"
                    )
        
        raise Exception("Failed to generate action ideas")
    
    def _parse_action_ideas(self, content: str) -> list[str]:
        """Parse action ideas from LLM response.
        
        Args:
            content: Raw response content from LLM
        
        Returns:
            List of action idea strings
        """
        try:
            # Try direct JSON parsing
            action_ideas = json.loads(content)
            if isinstance(action_ideas, list):
                return [str(idea).strip() for idea in action_ideas]
        except json.JSONDecodeError:
            pass
        
        # Fallback: Try to extract JSON array from text
        import re
        json_match = re.search(r'\[.*\]', content, re.DOTALL)
        if json_match:
            try:
                action_ideas = json.loads(json_match.group(0))
                if isinstance(action_ideas, list):
                    return [str(idea).strip() for idea in action_ideas]
            except json.JSONDecodeError:
                pass
        
        # Fallback: Parse numbered list
        lines = content.strip().split('\n')
        action_ideas = []
        for line in lines:
            line = line.strip()
            # Match patterns like "1. Action" or "1) Action" or "- Action"
            match = re.match(r'^[\d\-\*]+[\.\)]\s*(.+)$', line)
            if match:
                action_ideas.append(match.group(1).strip())
        
        return action_ideas
    
    def _calculate_word_count(
        self,
        themes: list[Theme],
        quotes: list[str],
        action_ideas: list[str]
    ) -> int:
        """Calculate total word count for report.
        
        Counts words in:
        - Theme labels and descriptions
        - Quotes
        - Action ideas
        
        Args:
            themes: List of themes
            quotes: List of quote strings
            action_ideas: List of action idea strings
        
        Returns:
            Total word count
        """
        word_count = 0
        
        # Count theme words
        for theme in themes:
            word_count += len(theme.label.split())
            word_count += len(theme.description.split())
        
        # Count quote words
        for quote in quotes:
            word_count += len(quote.split())
        
        # Count action idea words
        for idea in action_ideas:
            word_count += len(idea.split())
        
        return word_count
    
    def format_report(self, report: PulseReport) -> str:
        """Format PulseReport as human-readable text.
        
        Args:
            report: PulseReport object
        
        Returns:
            Formatted report string
        """
        lines = []
        
        # Header
        start_date = report.date_range[0].strftime("%B %d, %Y")
        end_date = report.date_range[1].strftime("%B %d, %Y")
        lines.append(f"PLAY STORE PULSE REPORT")
        lines.append(f"Week of {start_date} to {end_date}")
        lines.append(f"Based on {report.review_count} reviews")
        lines.append("")
        
        # Top Themes
        lines.append("=" * 60)
        lines.append("TOP THEMES")
        lines.append("=" * 60)
        for i, theme in enumerate(report.themes, 1):
            # Use actual_frequency if available, otherwise use frequency
            freq = getattr(theme, 'actual_frequency', theme.frequency)
            lines.append(f"\n{i}. {theme.label.upper()} ({freq} reviews)")
            lines.append(f"   {theme.description}")
        lines.append("")
        
        # User Voices
        lines.append("=" * 60)
        lines.append("USER VOICES")
        lines.append("=" * 60)
        for i, quote in enumerate(report.quotes, 1):
            lines.append(f"\n{i}. \"{quote}\"")
        lines.append("")
        
        # Action Ideas
        lines.append("=" * 60)
        lines.append("ACTION IDEAS")
        lines.append("=" * 60)
        for i, idea in enumerate(report.action_ideas, 1):
            lines.append(f"\n{i}. {idea}")
        lines.append("")
        
        # Footer
        lines.append("=" * 60)
        lines.append(f"Report generated: {report.generation_timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append(f"Word count: {report.word_count} / {self.word_limit}")
        lines.append("=" * 60)
        
        return "\n".join(lines)
