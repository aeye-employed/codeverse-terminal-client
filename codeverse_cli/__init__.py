"""CodeVerse CLI - Local client for CodeVerse Terminal cloud platform"""

__version__ = "1.0.0"
__author__ = "IBDA AI LTD"
__website__ = "https://codeverse.ibda.me"
__company__ = "IBDA AI LTD - https://ibda.me"

from .client import CodeVerseClient
from .config import Config
from .file_sync import FileSync

__all__ = ["CodeVerseClient", "Config", "FileSync"]