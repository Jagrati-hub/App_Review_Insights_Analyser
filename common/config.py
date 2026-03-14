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
    
    # Groq API settings - supports multiple keys for rotation on rate limit
    GROQ_API_KEY = get_config_value('GROQ_API_KEY', '', ['groq', 'api_key'])
    GROQ_API_KEYS = [k for k in [
        get_config_value('GROQ_API_KEY', '', ['groq', 'api_key']),
        get_config_value('GROQ_API_KEY_2', '', ['groq', 'api_key_2']),
        get_config_value('GROQ_API_KEY_3', '', ['groq', 'api_key_3']),
        get_config_value('GROQ_API_KEY_4', '', ['groq', 'api_key_4']),
        get_config_value('GROQ_API_KEY_5', '', ['groq', 'api_key_5']),
    ] if k]
    GROQ_MODEL = 'llama-3.3-70b-versatile'  # Fast model
    GROQ_TIMEOUT = 30  # Reduced from 45 to 30 for faster processing
    GROQ_MAX_RETRIES = 2  # Retry once with fallback model on rate limit
    
    # Scraper settings - Optimized for <1 minute processing
    APP_ID = os.getenv('APP_ID', 'com.nextbillion.groww')
    SCRAPER_LANGUAGE = 'en'
    SCRAPER_COUNTRY = 'in'  # India - Groww is an Indian app, more reviews available
    SCRAPER_BATCH_SIZE = 100
    SCRAPER_DELAY = 0.1  # Reduced delay
    SCRAPER_MAX_REVIEWS = 1000  # Increased to 1000 for better coverage
    SCRAPER_MIN_WORD_COUNT = 3  # Lowered from 5 to capture more reviews
    SCRAPER_FILTER_NON_ENGLISH = False  # Disabled - Groww has many valid non-English reviews
    SCRAPER_REMOVE_EMOJIS = True
    
    # Gemini API keys (fallback when Groq is rate limited)
    GEMINI_API_KEYS = [k for k in [
        os.getenv('Gemini_api_key_1', ''),
        os.getenv('Gemini_api_key_2', ''),
        os.getenv('Gemini_api_key_3', ''),
    ] if k]
    GEMINI_MODEL = 'gemini-1.5-flash'
    MIN_WEEKS = int(os.getenv('MIN_WEEKS', 8))
    MAX_WEEKS = int(os.getenv('MAX_WEEKS', 12))
    MAX_THEMES = int(os.getenv('MAX_THEMES', 5))
    REPORT_WORD_LIMIT = int(os.getenv('REPORT_WORD_LIMIT', 250))
    QUOTE_COUNT = 3
    ACTION_COUNT = 3
    
    # SMTP Email settings
    SMTP_SERVER = get_config_value('SMTP_SERVER', 'smtp.gmail.com', ['email', 'smtp_server'])
    SMTP_PORT = int(get_config_value('SMTP_PORT', '587', ['email', 'smtp_port']))
    SMTP_USERNAME = get_config_value('SMTP_USERNAME', 'manshuc@gmail.com', ['email', 'smtp_username'])
    SMTP_PASSWORD = get_config_value('SMTP_PASSWORD', 'knakwswgklmlogcd', ['email', 'smtp_password'])
    SENDER_EMAIL = get_config_value('SENDER_EMAIL', 'manshuc@gmail.com', ['email', 'sender_email'])
    SENDER_NAME = get_config_value('SENDER_NAME', 'Groww Product Team', ['email', 'sender_name'])
