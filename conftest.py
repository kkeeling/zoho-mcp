"""
Pytest configuration file that loads environment variables before test collection.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file before any tests are collected
# This ensures that test_all_endpoints.py and other tests have access to env vars

# Try multiple locations for .env file
env_locations = [
    Path.home() / ".zoho-mcp" / ".env",  # Home directory location
    Path(__file__).parent / "config" / ".env",  # Project config directory
    Path(__file__).parent / ".env",  # Project root
]

for env_path in env_locations:
    if env_path.exists():
        load_dotenv(dotenv_path=str(env_path))
        break
else:
    # If no .env file found, try loading from system environment
    load_dotenv()