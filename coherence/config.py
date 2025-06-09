"""Simple configuration management for Gemini API."""

import os
from dotenv import load_dotenv
from pathlib import Path
from logging_config import setup_logging


logger = setup_logging()

env_path = Path(__file__).parent.parent / '.env' 
load_dotenv(env_path)


def get_gemini_api_key() -> str:
    """Get the Gemini API key from environment variables."""
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        logger.warning("GEMINI_API_KEY environment variable not set. Coherence will be skipped. Please set it in your environment or .env file.")
        return None
    return api_key


def get_gemini_model() -> str:
    """Get the Gemini model name with a default fallback."""
    return os.getenv("GEMINI_MODEL", "gemini-2.0-flash-lite")
