"""
Configuration Loader Module

Handles loading and validating environment variables and configuration settings
for the AI Trends Research Bot.
"""

import os
from dotenv import load_dotenv

def load_config() -> dict:
    """
    Load and validate environment variables from .env file and system environment.

    Returns:
        dict: A dictionary containing all configuration parameters.
    
    Raises:
        ValueError: If a required environment variable is not set.
    """
    load_dotenv()
    
    # Required environment variables
    required_vars = ['GEMINI_API_KEY']
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")
    
    # Load configuration with defaults
    config = {
        'gemini_api_key': os.getenv('GEMINI_API_KEY'),
        'gmail_credentials_path': os.getenv('GMAIL_CREDENTIALS_PATH', 'config/credentials.json'),
        'gmail_token_path': os.getenv('GMAIL_TOKEN_PATH', 'config/token.json'),
        'newsletter_lookback_days': int(os.getenv('NEWSLETTER_LOOKBACK_DAYS', '7')),
        'output_dir': os.getenv('OUTPUT_DIR', './outputs'),
        'log_level': os.getenv('LOG_LEVEL', 'INFO'),
        'log_file': os.getenv('LOG_FILE', './logs/ai_trends_bot.log'),
        'newsletter_whitelist': [x.strip() for x in os.getenv('NEWSLETTER_WHITELIST', '').split(',') if x.strip()],
        'newsletter_blacklist': [x.strip() for x in os.getenv('NEWSLETTER_BLACKLIST', '').split(',') if x.strip()],
        'newsletter_sender_blacklist': [x.strip() for x in os.getenv('NEWSLETTER_SENDER_BLACKLIST', '').split(',') if x.strip()],
        'newsletter_subject_blacklist': [x.strip() for x in os.getenv('NEWSLETTER_SUBJECT_BLACKLIST', '').split(',') if x.strip()],
    }
    
    return config

