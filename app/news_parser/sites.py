"""Web site parsers for news sources - base classes and factory"""
import logging
from typing import List, Optional

import httpx

logger = logging.getLogger(__name__)


class NewsParser:
    """Base news parser class"""

    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }

    async def fetch_page(self, url: str) -> Optional[str]:
        """Fetch page content"""
        try:
            async with httpx.AsyncClient(follow_redirects=True) as client:
                response = await client.get(url, headers=self.headers, timeout=30.0)
                response.raise_for_status()
                return response.text
        except Exception as e:
            logger.error(f"Failed to fetch {url}: {e}")
            return None

    def parse(self, url: str) -> List[dict]:
        """Parse news from source - to be implemented by subclasses"""
        raise NotImplementedError


# Factory function to get parser by source type
def get_parser(source_type: str) -> Optional[NewsParser]:
    """Get parser instance by source type"""
    source_type_lower = source_type.lower()

    # Check if it's an RBC source (rbc, rbc_politics, rbc_economics, etc.)
    if source_type_lower == 'rbc' or source_type_lower.startswith('rbc_'):
        from app.news_parser.rbc_parser import RBCParser
        return RBCParser()

    # Add other parsers here in the future
    parsers = {
        # 'habr': HabrParser,
        # 'vc': VCParser,
        # 'tproger': TprogerParser,
    }

    parser_class = parsers.get(source_type_lower)
    if parser_class:
        return parser_class()

    logger.error(f"Unknown source type: {source_type}")
    return None
