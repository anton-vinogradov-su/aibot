"""Utility functions"""
import hashlib
import logging
from datetime import datetime
from typing import Optional

logger = logging.getLogger(__name__)


def generate_hash(text: str) -> str:
    """Generate SHA256 hash from text"""
    return hashlib.sha256(text.encode()).hexdigest()


def is_duplicate(url: str, existing_urls: list[str]) -> bool:
    """Check if URL is duplicate"""
    return url in existing_urls


def parse_date(date_string: str) -> Optional[datetime]:
    """Parse date string to datetime object"""
    from dateutil import parser
    try:
        return parser.parse(date_string)
    except Exception as e:
        logger.error(f"Failed to parse date: {date_string}, error: {e}")
        return None


def clean_text(text: str) -> str:
    """Clean and normalize text"""
    if not text:
        return ""

    # Remove extra whitespace
    text = " ".join(text.split())

    # Remove special characters if needed
    # text = re.sub(r'[^\w\s\.,!?-]', '', text)

    return text.strip()


def setup_logging():
    """Setup logging configuration"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('app.log'),
            logging.StreamHandler()
        ]
    )
