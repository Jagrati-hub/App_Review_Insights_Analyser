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
    GROQ_MODEL = 'mixtral-8x7b-32768'
    GROQ_TIMEOUT = 30
    GROQ_MAX_RETRIES = 3
    
    # Scraper settings
    APP_ID = os.getenv('APP_ID', 'com.nextbillion.groww')
    SCRAPER_LANGUAGE = 'en'
    SCRAPER_COUNTRY = 'us'
    SCRAPER_BATCH_SIZE = 200
    SCRAPER_DELAY = 1.0  # seconds between batches
    SCRAPER_MAX_REVIEWS = 5000  # Phase 1: Scale to 5000 reviews
    SCRAPER_MIN_WORD_COUNT = 5  # Phase 1: Filter reviews with <5 words
    
    # Analysis settings
    MIN_WEEKS = int(os.getenv('MIN_WEEKS', 8))
    MAX_WEEKS = int(os.getenv('MAX_WEEKS', 12))
    MAX_THEMES = int(os.getenv('MAX_THEMES', 5))
    REPORT_WORD_LIMIT = int(os.getenv('REPORT_WORD_LIMIT', 250))
    QUOTE_COUNT = 3
    ACTION_COUNT = 3
