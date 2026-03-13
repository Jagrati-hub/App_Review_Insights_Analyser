"""Configuration management for Play Store Review Analyzer."""
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Application configuration."""
    
    # Flask settings
    SECRET_KEY = os.getenv('FLASK_SECRET_KEY', 'dev-secret-key-change-in-production')
    FLASK_ENV = os.getenv('FLASK_ENV', 'development')
    
    # Groq API settings
    GROQ_API_KEY = os.getenv('GROQ_API_KEY', '')
    GROQ_MODEL = 'llama-3.3-70b-versatile'  # Updated to newer model
    GROQ_TIMEOUT = 45  # Increased from 30 to 45 for better reliability
    GROQ_MAX_RETRIES = 2  # Reduced from 3 to 2 retries
    
    # Scraper settings
    APP_ID = os.getenv('APP_ID', 'com.nextbillion.groww')
    SCRAPER_LANGUAGE = 'en'
    SCRAPER_COUNTRY = 'us'
    SCRAPER_BATCH_SIZE = 200
    SCRAPER_DELAY = 0.5  # Reduced from 1.0 to 0.5 seconds between batches
    SCRAPER_MAX_REVIEWS = 2000  # Reduced from 5000 to 2000 for faster processing
    SCRAPER_MIN_WORD_COUNT = 5  # Phase 1: Filter reviews with <5 words
    SCRAPER_FILTER_NON_ENGLISH = True  # Phase 1: Filter non-English reviews
    SCRAPER_REMOVE_EMOJIS = True  # Phase 1: Remove emojis
    
    # Analysis settings
    MIN_WEEKS = int(os.getenv('MIN_WEEKS', 8))
    MAX_WEEKS = int(os.getenv('MAX_WEEKS', 12))
    MAX_THEMES = int(os.getenv('MAX_THEMES', 5))
    REPORT_WORD_LIMIT = int(os.getenv('REPORT_WORD_LIMIT', 250))
    QUOTE_COUNT = 3
    ACTION_COUNT = 3
    
    # SMTP Email settings
    SMTP_SERVER = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
    SMTP_PORT = int(os.getenv('SMTP_PORT', 587))  # 587 for TLS, 465 for SSL
    SMTP_USERNAME = os.getenv('SMTP_USERNAME', '')  # Gmail address
    SMTP_PASSWORD = os.getenv('SMTP_PASSWORD', '')  # Gmail app password
    SENDER_EMAIL = os.getenv('SENDER_EMAIL', os.getenv('SMTP_USERNAME', ''))
    SENDER_NAME = os.getenv('SENDER_NAME', 'Groww Product Team')
