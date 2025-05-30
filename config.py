"""Application configuration module."""

import os
from dotenv import load_dotenv

# Load environment variables from a .env file if present
load_dotenv()

class Config:
    """Holds configuration values for the Flask app."""

    SECRET_KEY = os.environ.get("SECRET_KEY", "change-me")
    GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID", "")
    GOOGLE_CLIENT_SECRET = os.environ.get("GOOGLE_CLIENT_SECRET", "")
    GOOGLE_DISCOVERY_URL = "https://accounts.google.com/.well-known/openid-configuration"
    ALLOWED_DOMAIN = os.environ.get("ALLOWED_DOMAIN", "example.com")
