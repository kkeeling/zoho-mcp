"""
Settings for the Zoho Books MCP Integration Server.

This module loads configuration from environment variables.
"""

import os
from pathlib import Path
from typing import Dict, Any
from dotenv import load_dotenv

# Load environment variables from .env file if it exists
env_path = Path(__file__).parent.parent.parent / "config" / ".env"
if env_path.exists():
    load_dotenv(dotenv_path=str(env_path))
else:
    # If no .env file exists, load from environment variables
    load_dotenv()


def _get_domain(region: str) -> str:
    """
    Get the domain for the Zoho region.
    
    Args:
        region: The region code (US, EU, IN, AU, etc.)
        
    Returns:
        The domain for the region (com, eu, in, com.au, etc.)
    """
    region_map = {
        "US": "com",
        "EU": "eu",
        "IN": "in",
        "AU": "com.au",
        "JP": "jp",
        "CN": "com.cn",
        "CA": "ca",
    }
    return region_map.get(region.upper(), "com")


class Settings:
    """
    Settings class to manage configuration for the MCP server.
    Pulls values from environment variables with defaults.
    """
    # Zoho API credentials
    ZOHO_CLIENT_ID: str = os.environ.get("ZOHO_CLIENT_ID", "")
    ZOHO_CLIENT_SECRET: str = os.environ.get("ZOHO_CLIENT_SECRET", "")
    ZOHO_REFRESH_TOKEN: str = os.environ.get("ZOHO_REFRESH_TOKEN", "")
    ZOHO_ORGANIZATION_ID: str = os.environ.get("ZOHO_ORGANIZATION_ID", "")
    
    # Zoho API URLs
    ZOHO_REGION: str = os.environ.get("ZOHO_REGION", "US")
    ZOHO_API_BASE_URL: str = os.environ.get(
        "ZOHO_API_BASE_URL", "https://www.zohoapis.com/books/v3"
    )
    domain = _get_domain(os.environ.get('ZOHO_REGION', 'US'))
    ZOHO_AUTH_BASE_URL: str = os.environ.get(
        "ZOHO_AUTH_BASE_URL", f"https://accounts.zoho.{domain}/oauth/v2"
    )
    
    # Token management
    TOKEN_CACHE_PATH: str = os.environ.get(
        "TOKEN_CACHE_PATH", 
        str(Path(__file__).parent.parent.parent / "config" / ".token_cache")
    )
    
    # Logging
    LOG_LEVEL: str = os.environ.get("LOG_LEVEL", "INFO")
    LOG_FORMAT: str = os.environ.get(
        "LOG_FORMAT", "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    
    # Server settings
    DEFAULT_PORT: int = int(os.environ.get("DEFAULT_PORT", "8000"))
    DEFAULT_HOST: str = os.environ.get("DEFAULT_HOST", "127.0.0.1")
    DEFAULT_WS_PORT: int = int(os.environ.get("DEFAULT_WS_PORT", "8765"))
    
    # Timeouts and retries
    REQUEST_TIMEOUT: int = int(os.environ.get("REQUEST_TIMEOUT", "60"))
    MAX_RETRIES: int = int(os.environ.get("MAX_RETRIES", "3"))
    
    def as_dict(self) -> Dict[str, Any]:
        """Return settings as a dictionary."""
        return {
            key: value for key, value in self.__dict__.items()
            if not key.startswith("_") and key.isupper()
        }
    
    def validate(self) -> None:
        """
        Validate required settings.
        
        Raises:
            ValueError: If any required setting is missing.
        """
        required_settings = [
            "ZOHO_CLIENT_ID",
            "ZOHO_CLIENT_SECRET",
            "ZOHO_REFRESH_TOKEN",
            "ZOHO_ORGANIZATION_ID",
        ]
        
        missing = [setting for setting in required_settings 
                  if not getattr(self, setting)]
        
        if missing:
            raise ValueError(
                f"Missing required settings: {', '.join(missing)}. "
                "Please add them to your .env file or environment variables."
            )


# Create a singleton instance
settings = Settings()