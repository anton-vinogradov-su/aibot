"""Web site parsers for news sources"""
import logging
from datetime import datetime
from typing import List, Optional

import httpx
from bs4 import BeautifulSoup

from app.utils import clean_text

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
            async with httpx.AsyncClient() as client:
                response = await client.get(url, headers=self.headers, timeout=30.0)
                response.raise_for_status()
                return response.text
        except Exception as e:
            logger.error(f"Failed to fetch {url}: {e}")
            return None

    def parse(self, url: str) -> List[dict]:
        """Parse news from source - to be implemented by subclasses"""
        raise NotImplementedError


class RBCParser(NewsParser):
    """Parser for RBC.ru"""

    def __init__(self):
        super().__init__()
        self.base_url = "https://www.rbc.ru"
        self.source_name = "RBC"

    async def parse(self, url: str = None) -> List[dict]:
        """Parse news from RBC.ru"""
        if url is None:
            url = f"{self.base_url}/politics/"

        logger.info(f"Parsing RBC from {url}")
        html = await self.fetch_page(url)

        if not html:
            return []

        soup = BeautifulSoup(html, 'lxml')
        news_items = []

        # Find news items on the page
        # RBC uses different layouts, trying to find common news elements
        articles = soup.find_all('a', class_='news-feed__item')

        if not articles:
            # Try alternative selector
            articles = soup.find_all('div', class_='item')

        for article in articles[:20]:  # Limit to 20 items
            try:
                news_item = self._parse_article(article)
                if news_item:
                    news_items.append(news_item)
            except Exception as e:
                logger.error(f"Failed to parse article: {e}")
                continue

        logger.info(f"Parsed {len(news_items)} news items from RBC")
        return news_items

    def _parse_article(self, article) -> Optional[dict]:
        """Parse single article element"""
        try:
            # Try to find link
            link = article.get('href')
            if not link:
                link_tag = article.find('a')
                if link_tag:
                    link = link_tag.get('href')

            if not link:
                return None

            # Make absolute URL
            if link.startswith('/'):
                link = f"{self.base_url}{link}"

            # Try to find title
            title_tag = article.find('span', class_='news-feed__item__title')
            if not title_tag:
                title_tag = article.find('span', class_='item__title')
            if not title_tag:
                title_tag = article.find('h3')

            if not title_tag:
                return None

            title = clean_text(title_tag.get_text())

            # Try to find time
            time_tag = article.find('span', class_='news-feed__item__date-time')
            if not time_tag:
                time_tag = article.find('span', class_='item__category')

            # For now, use current time if we can't parse the date
            published_at = datetime.utcnow()

            # Try to find summary
            summary_tag = article.find('span', class_='news-feed__item__text')
            if not summary_tag:
                summary_tag = article.find('p')

            summary = clean_text(summary_tag.get_text()) if summary_tag else None

            return {
                'title': title,
                'url': link,
                'summary': summary or title,
                'source': self.source_name,
                'published_at': published_at,
                'raw_text': None  # Will be filled if we fetch full article
            }

        except Exception as e:
            logger.error(f"Error parsing article element: {e}")
            return None

    async def fetch_full_article(self, url: str) -> Optional[str]:
        """Fetch full article text"""
        html = await self.fetch_page(url)
        if not html:
            return None

        try:
            soup = BeautifulSoup(html, 'lxml')

            # Find article content
            article = soup.find('div', class_='article__text')
            if not article:
                article = soup.find('div', class_='article')

            if article:
                paragraphs = article.find_all('p')
                text = ' '.join([p.get_text() for p in paragraphs])
                return clean_text(text)

        except Exception as e:
            logger.error(f"Failed to fetch full article from {url}: {e}")

        return None


# Factory function to get parser by source type
def get_parser(source_type: str) -> Optional[NewsParser]:
    """Get parser instance by source type"""
    parsers = {
        'rbc': RBCParser,
    }

    parser_class = parsers.get(source_type.lower())
    if parser_class:
        return parser_class()

    logger.error(f"Unknown source type: {source_type}")
    return None
