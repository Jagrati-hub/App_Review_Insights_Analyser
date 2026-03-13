"""Configuration management for Play Store Review Analyzer."""
import os
from dotenv import load_dotenv

load_dotenv()

# Try to import Streamlit for secrets support
try:
    import streamlit as st
    HAS_STREAMLIT = True
except ImportError:
    HAS_STREAMLIT = False

def get_config_value(key: str, default: str = '', streamlit_path: list = None):
    """Get configuration value from Streamlit secrets, env vars, or default.
    
    Priority:
    1. Streamlit secrets (if available)
    2. Environment variables
    3. Default value
    """
    # Try Streamlit secrets first
    if HAS_STREAMLIT and streamlit_path:
        try:
            value = st.secrets
            for path_part in streamlit_path:
                value = value.get(path_part, {})
            if value and value != {}:
                return value
        except (AttributeError, FileNotFoundError):
            pass
    
    # Fall back to environment variable
    env_value = os.getenv(key)
    if env_value:
        return env_value
    
    # Use default
    return default

class Config:
    """Application configuration."""
    
    # Flask settings
    SECRET_KEY = os.getenv('FLASK_SECRET_KEY', 'dev-secret-key-change-in-production')
    FLASK_ENV = os.getenv('FLASK_ENV', 'development')
    
    # Groq API settings
    GROQ_API_KEY = get_config_value('GROQ_API_KEY', '', ['groq', 'api_key'])
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
    SMTP_SERVER = get_config_value('SMTP_SERVER', 'smtp.gmail.com', ['email', 'smtp_server'])
    SMTP_PORT = int(get_config_value('SMTP_PORT', '587', ['email', 'smtp_port']))
    SMTP_USERNAME = get_config_value('SMTP_USERNAME', '', ['email', 'smtp_username'])
    SMTP_PASSWORD = get_config_value('SMTP_PASSWORD', '', ['email', 'smtp_password'])
    SENDER_EMAIL = get_config_value('SENDER_EMAIL', get_config_value('SMTP_USERNAME', '', ['email', 'smtp_username']), ['email', 'sender_email'])
    SENDER_NAME = get_config_value('SENDER_NAME', 'Groww Product Team', ['email', 'sender_name'])
