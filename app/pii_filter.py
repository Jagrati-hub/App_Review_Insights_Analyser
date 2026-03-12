"""PII filtering for review text."""
import re
import logging
from typing import Optional
from dataclasses import dataclass

from app.models import Review, PIISummary

logger = logging.getLogger(__name__)


@dataclass
class PIIMatch:
    """A detected PII instance."""
    pii_type: str  # 'email', 'phone', 'username', 'user_id'
    matched_text: str
    start_pos: int
    end_pos: int


class PIIFilter:
    """Removes personally identifiable information from review text."""
    
    # PII detection patterns
    EMAIL_PATTERN = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    PHONE_PATTERN = r'(\+\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b'
    USERNAME_PATTERN = r'@\w+'
    UUID_PATTERN = r'\b[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}\b'
    USER_ID_PATTERN = r'\b(?:user[_\s]?id|userid)[:\s]+\w+\b'
    
    # Replacement placeholders
    PLACEHOLDERS = {
        'email': '[EMAIL]',
        'phone': '[PHONE]',
        'username': '[USERNAME]',
        'user_id': '[USER_ID]'
    }
    
    def filter_reviews(
        self, 
        reviews: list[Review]
    ) -> tuple[list[Review], PIISummary]:
        """
        Remove PII from all review text fields.
        
        Returns:
            - List of Review objects with sanitized text
            - PIISummary with detection counts by type
        """
        sanitized_reviews = []
        total_pii_found = 0
        pii_by_type = {
            'email': 0,
            'phone': 0,
            'username': 0,
            'user_id': 0
        }
        
        for review in reviews:
            # Sanitize review text
            sanitized_text, matches = self.sanitize_text(review.text)
            
            # Count PII instances
            for match in matches:
                pii_by_type[match.pii_type] += 1
                total_pii_found += 1
            
            # Create sanitized review
            sanitized_review = Review(
                rating=review.rating,
                text=sanitized_text,
                date=review.date,
                review_id=review.review_id,
                is_sanitized=True
            )
            sanitized_reviews.append(sanitized_review)
        
        summary = PIISummary(
            reviews_processed=len(reviews),
            pii_instances_found=total_pii_found,
            pii_by_type=pii_by_type
        )
        
        logger.info(f"PII filtering complete: {total_pii_found} instances found in {len(reviews)} reviews")
        return sanitized_reviews, summary
    
    def sanitize_text(self, text: str) -> tuple[str, list[PIIMatch]]:
        """
        Remove PII from a single text string.
        
        Returns:
            - Sanitized text with placeholders
            - List of detected PII matches
        """
        matches = []
        sanitized = text
        
        # Detect and replace each PII type
        # Order matters: process longer patterns first to avoid partial replacements
        
        # 1. Email addresses
        for match in re.finditer(self.EMAIL_PATTERN, text, re.IGNORECASE):
            matches.append(PIIMatch(
                pii_type='email',
                matched_text=match.group(),
                start_pos=match.start(),
                end_pos=match.end()
            ))
        sanitized = re.sub(self.EMAIL_PATTERN, self.PLACEHOLDERS['email'], sanitized, flags=re.IGNORECASE)
        
        # 2. Phone numbers
        for match in re.finditer(self.PHONE_PATTERN, text):
            matches.append(PIIMatch(
                pii_type='phone',
                matched_text=match.group(),
                start_pos=match.start(),
                end_pos=match.end()
            ))
        sanitized = re.sub(self.PHONE_PATTERN, self.PLACEHOLDERS['phone'], sanitized)
        
        # 3. User IDs (before usernames to catch "user_id: 12345" patterns)
        for match in re.finditer(self.USER_ID_PATTERN, text, re.IGNORECASE):
            matches.append(PIIMatch(
                pii_type='user_id',
                matched_text=match.group(),
                start_pos=match.start(),
                end_pos=match.end()
            ))
        sanitized = re.sub(self.USER_ID_PATTERN, self.PLACEHOLDERS['user_id'], sanitized, flags=re.IGNORECASE)
        
        # 4. UUIDs
        for match in re.finditer(self.UUID_PATTERN, text, re.IGNORECASE):
            matches.append(PIIMatch(
                pii_type='user_id',
                matched_text=match.group(),
                start_pos=match.start(),
                end_pos=match.end()
            ))
        sanitized = re.sub(self.UUID_PATTERN, self.PLACEHOLDERS['user_id'], sanitized, flags=re.IGNORECASE)
        
        # 5. Usernames (@username)
        for match in re.finditer(self.USERNAME_PATTERN, text):
            matches.append(PIIMatch(
                pii_type='username',
                matched_text=match.group(),
                start_pos=match.start(),
                end_pos=match.end()
            ))
        sanitized = re.sub(self.USERNAME_PATTERN, self.PLACEHOLDERS['username'], sanitized)
        
        if matches:
            logger.debug(f"Found {len(matches)} PII instances in text")
        
        return sanitized, matches
