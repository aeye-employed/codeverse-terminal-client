"""
CodeVerse CLI - AI-Powered Development Assistant

A production-ready command-line interface for the CodeVerse platform,
featuring 54 specialized AI agents for development tasks.
"""

__version__ = "1.0.0"
__author__ = "IBDA AI LTD"
__email__ = "support@ibda.me"
__license__ = "MIT"

from .client import CodeVerseClient
from .auth import AuthManager
from .config import Config

__all__ = ["CodeVerseClient", "AuthManager", "Config"]