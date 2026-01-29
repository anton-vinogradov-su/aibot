"""Habr.com news parser"""
import logging
from datetime import datetime
from typing import List, Optional

from bs4 import BeautifulSoup

from app.news_parser.sites import NewsParser
from app.utils import clean_text

logger = logging.getLogger(__name__)


class HabrParser(NewsParser):
    """Parser for Habr.com"""

    def __init__(self):
        super().__init__()
        self.base_url = "https://habr.com"
        self.source_name = "Habr"

    async def parse(self, url: str = None) -> List[dict]:
        """Parse news from Habr.com"""
        if url is None:
            url = f"{self.base_url}/ru/news/"

        logger.info(f"Parsing Habr from {url}")

        html = await self.fetch_page(url)

        if not html:
            return []

        soup = BeautifulSoup(html, 'html.parser')
        news_items = []

        # Find all article elements
        article_tags = soup.select("article")

        for article_tag in article_tags[:20]:  # Limit to 20 items
            try:
                news_item = self._parse_article(article_tag)
                if news_item:
                    news_items.append(news_item)
            except Exception as e:
                logger.error(f"Failed to parse article: {e}")
                continue

        logger.info(f"Parsed {len(news_items)} news items from Habr")
        return news_items

    def _parse_article(self, article_tag) -> Optional[dict]:
        """Parse single article element"""
        try:
            # Find title and link
            title_link = article_tag.find('a', class_="tm-title__link")
            if title_link is None:
                return None

            title_text = clean_text(title_link.get_text(strip=True))
            relative_url = title_link.get('href', '')

            if not relative_url:
                return None

            # Make absolute URL
            if relative_url.startswith("http"):
                full_url = relative_url
            else:
                full_url = f"{self.base_url}{relative_url}"

            # Try to find summary/description
            summary = None

            # Try article snippet
            snippet_tag = article_tag.find('div', class_='tm-article-snippet')
            if snippet_tag:
                snippet_text = snippet_tag.get_text(strip=True)
                summary = clean_text(snippet_text)

            # Alternative: try article body
            if not summary:
                body_tag = article_tag.find('div', class_='article-formatted-body')
                if body_tag:
                    # Get first paragraph
                    first_p = body_tag.find('p')
                    if first_p:
                        summary = clean_text(first_p.get_text(strip=True))

            # Try to find publication time
            published_at = datetime.utcnow()
            time_tag = article_tag.find('time')
            if time_tag and time_tag.get('datetime'):
                try:
                    from dateutil import parser as date_parser
                    published_at = date_parser.parse(time_tag['datetime'])
                except Exception as e:
                    logger.debug(f"Could not parse date: {e}")

            return {
                'title': title_text,
                'url': full_url,
                'summary': summary or title_text,
                'source': self.source_name,
                'published_at': published_at,
                'raw_text': None
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
            soup = BeautifulSoup(html, 'html.parser')

            # Find article content
            article = soup.find('div', class_='article-formatted-body')
            if not article:
                article = soup.find('div', class_='tm-article-body')

            if article:
                # Remove code blocks and other non-text elements
                for tag in article.find_all(['pre', 'code', 'script']):
                    tag.decompose()

                paragraphs = article.find_all('p')
                text = ' '.join([p.get_text() for p in paragraphs])
                return clean_text(text)

        except Exception as e:
            logger.error(f"Failed to fetch full article from {url}: {e}")

        return None
