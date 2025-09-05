"""
Configuration settings for the AI Data Insights application.
"""

import os
from typing import Optional

# Load environment variables from secrets.env if it exists
def load_env_file(filepath: str):
    """Load environment variables from a file."""
    if os.path.exists(filepath):
        with open(filepath, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key.strip()] = value.strip()

# Try to load from secrets.env
load_env_file('secrets.env')

class Config:
    """Application configuration settings."""
    
    # OpenAI API Configuration
    OPENAI_API_KEY: Optional[str] = os.getenv("OPEN_AI_KEY")
    OPENAI_MODEL: str = "gpt-4o-mini"  # Default model to use
    OPENAI_MAX_RETRIES: int = 3
    OPENAI_BASE_DELAY: float = 1.0  # seconds
    
    # Rate Limiting
    RATE_LIMIT_ENABLED: bool = True
    MAX_REQUESTS_PER_MINUTE: int = 60
    
    # Error Handling
    SHOW_DETAILED_ERRORS: bool = False  # Set to True for debugging
    FALLBACK_MODE_ENABLED: bool = True
    
    # Application Settings
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"
    
    @classmethod
    def validate_openai_config(cls) -> tuple[bool, str]:
        """
        Validate OpenAI configuration.
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not cls.OPENAI_API_KEY:
            return False, "OpenAI API key not found. Please set the OPEN_AI_KEY environment variable."
        
        if not cls.OPENAI_API_KEY.startswith("sk-"):
            return False, "Invalid OpenAI API key format. API keys should start with 'sk-'."
        
        return True, ""
    
    @classmethod
    def get_status_message(cls) -> str:
        """Get current configuration status message."""
        is_valid, error = cls.validate_openai_config()
        
        if is_valid:
            return "✅ OpenAI API configuration is valid"
        else:
            return f"⚠️ OpenAI API configuration issue: {error}"

# Global config instance
config = Config()
