"""
Configuration module for News Filter application.
Loads environment variables and provides configuration constants.
"""

import os
import json
from typing import Dict, List, Any
from dotenv import load_dotenv


class Config:
    """Configuration class to load and manage application settings."""
    
    def __init__(self, env_file: str = None):
        """
        Initialize configuration by loading environment variables.
        
        Args:
            env_file: Optional path to .env file
        """
        if env_file:
            load_dotenv(env_file)
        else:
            # Try to load from config/.env
            config_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config')
            env_path = os.path.join(config_dir, '.env')
            load_dotenv(env_path)
    
    @property
    def smtp_config(self) -> Dict[str, Any]:
        """Get SMTP configuration."""
        return {
            'host': os.getenv('SMTP_HOST', 'localhost'),
            'port': int(os.getenv('SMTP_PORT', '587')),
            'username': os.getenv('SMTP_USERNAME', ''),
            'password': os.getenv('SMTP_PASSWORD', '')
        }
    
    @property
    def email_recipients(self) -> List[str]:
        """Get email recipients list."""
        recipients_str = os.getenv('EMAIL_RECIPIENTS', '[]')
        try:
            return json.loads(recipients_str)
        except json.JSONDecodeError:
            return []
    
    @property
    def positive_keywords(self) -> Dict[str, List[str]]:
        """Get positive keywords categorized by topic."""
        keywords_str = os.getenv('POSITIVE_KEYWORDS', '{}')
        try:
            return json.loads(keywords_str)
        except json.JSONDecodeError:
            return {}
    
    @property
    def negative_keywords(self) -> List[str]:
        """Get negative keywords for exclusion."""
        keywords_str = os.getenv('NEGATIVE_KEYWORDS', '[]')
        try:
            return json.loads(keywords_str)
        except json.JSONDecodeError:
            return []
    
    @property
    def rss_sources(self) -> List[str]:
        """Get RSS source URLs."""
        sources_str = os.getenv('RSS_SOURCES', '[]')
        try:
            return json.loads(sources_str)
        except json.JSONDecodeError:
            return []
    
    @property
    def scraping_sources(self) -> Dict[str, Dict[str, str]]:
        """Get scraping source configuration."""
        sources_str = os.getenv('SCRAPING_SOURCES', '{}')
        try:
            return json.loads(sources_str)
        except json.JSONDecodeError:
            return {}
    
    @property
    def timezone(self) -> str:
        """Get timezone setting."""
        return os.getenv('TIMEZONE', 'Asia/Ho_Chi_Minh')


# Global config instance
config = Config()