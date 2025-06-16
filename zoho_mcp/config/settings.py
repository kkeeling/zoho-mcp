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
    ZOHO_OAUTH_SCOPE: str = os.environ.get(
        "ZOHO_OAUTH_SCOPE",
        "ZohoBooks.fullaccess.all",
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
    LOG_FILE_PATH: str = os.environ.get("LOG_FILE_PATH", "")
    LOG_FORMAT_JSON: bool = os.environ.get("LOG_FORMAT_JSON", "False").lower() in ["true", "1", "yes"]
    LOG_MAX_BYTES: int = int(os.environ.get("LOG_MAX_BYTES", "10485760"))  # 10MB
    LOG_BACKUP_COUNT: int = int(os.environ.get("LOG_BACKUP_COUNT", "5"))
    LOG_SANITIZE_ENABLED: bool = os.environ.get("LOG_SANITIZE_ENABLED", "True").lower() in ["true", "1", "yes"]
    LOG_INCLUDE_REQUEST_BODY: bool = os.environ.get("LOG_INCLUDE_REQUEST_BODY", "False").lower() in ["true", "1", "yes"]
    LOG_INCLUDE_RESPONSE_BODY: bool = os.environ.get("LOG_INCLUDE_RESPONSE_BODY", "False").lower() in ["true", "1", "yes"]
    
    # Server settings
    DEFAULT_PORT: int = int(os.environ.get("DEFAULT_PORT", "8000"))
    DEFAULT_HOST: str = os.environ.get("DEFAULT_HOST", "127.0.0.1")
    DEFAULT_WS_PORT: int = int(os.environ.get("DEFAULT_WS_PORT", "8765"))
    
    # Transport-specific settings
    CORS_ORIGINS: list = os.environ.get("CORS_ORIGINS", "*").split(",")
    HTTP_KEEPALIVE: bool = os.environ.get("HTTP_KEEPALIVE", "True").lower() in ["true", "1", "yes"]
    HTTP_READ_TIMEOUT: int = int(os.environ.get("HTTP_READ_TIMEOUT", "30"))
    WS_PING_INTERVAL: int = int(os.environ.get("WS_PING_INTERVAL", "30"))
    WS_PING_TIMEOUT: int = int(os.environ.get("WS_PING_TIMEOUT", "60"))
    RATE_LIMIT_ENABLED: bool = os.environ.get("RATE_LIMIT_ENABLED", "True").lower() in ["true", "1", "yes"]
    RATE_LIMIT_REQUESTS: int = int(os.environ.get("RATE_LIMIT_REQUESTS", "100"))
    RATE_LIMIT_WINDOW: int = int(os.environ.get("RATE_LIMIT_WINDOW", "60"))  # in seconds
    
    # Security settings
    ENABLE_SECURE_TRANSPORT: bool = os.environ.get("ENABLE_SECURE_TRANSPORT", "False").lower() in ["true", "1", "yes"]
    SSL_CERT_PATH: str = os.environ.get("SSL_CERT_PATH", "")
    SSL_KEY_PATH: str = os.environ.get("SSL_KEY_PATH", "")
    
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