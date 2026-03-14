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
                value = value[path_part]
            if value is not None and value != '':
                return str(value)
        except (KeyError, AttributeError, FileNotFoundError):
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
    GROQ_MODEL = 'llama-3.3-70b-versatile'  # Fast model
    GROQ_TIMEOUT = 30  # Reduced from 45 to 30 for faster processing
    GROQ_MAX_RETRIES = 1  # Reduced from 2 to 1 for speed
    
    # Scraper settings - Optimized for <1 minute processing
    APP_ID = os.getenv('APP_ID', 'com.nextbillion.groww')
    SCRAPER_LANGUAGE = 'en'
    SCRAPER_COUNTRY = 'us'
    SCRAPER_BATCH_SIZE = 100  # Reduced from 200 to 100
    SCRAPER_DELAY = 0.2  # Reduced from 0.5 to 0.2 seconds
    SCRAPER_MAX_REVIEWS = 500  # Reduced from 2000 to 500 for <1 min
    SCRAPER_MIN_WORD_COUNT = 5
    SCRAPER_FILTER_NON_ENGLISH = True
    SCRAPER_REMOVE_EMOJIS = True
    
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
