"""RBC.ru news parser"""
import logging
from datetime import datetime
from typing import List, Optional

from bs4 import BeautifulSoup

from app.news_parser.sites import NewsParser
from app.utils import clean_text

logger = logging.getLogger(__name__)


class RBCParser(NewsParser):
    """Parser for RBC.ru (all rubrics)"""

    def __init__(self):
        super().__init__()
        self.base_url = "https://www.rbc.ru"
        self.source_name = "RBC"

    def _get_source_name_from_url(self, url: str) -> str:
        """Extract source name from URL"""
        # Extract rubric name from URL
        if '/rubric/' in url:
            rubric = url.split('/rubric/')[1].split('?')[0].strip('/')
            return f"RBC-{rubric.title()}"
        elif '/sport' in url:
            return "RBC-Sport"
        elif '/rbcfreenews' in url:
            return "RBC-News"
        return "RBC"

    async def parse(self, url: str = None) -> List[dict]:
        """Parse news from RBC.ru"""
        if url is None:
            url = f"{self.base_url}/rubric/politics"

        logger.info(f"Parsing RBC from {url}")

        # Get source name from URL
        source_name = self._get_source_name_from_url(url)

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
                news_item = self._parse_article(article, source_name)
                if news_item:
                    news_items.append(news_item)
            except Exception as e:
                logger.error(f"Failed to parse article: {e}")
                continue

        logger.info(f"Parsed {len(news_items)} news items from {source_name}")
        return news_items

    def _parse_article(self, article, source_name: str) -> Optional[dict]:
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
                'source': source_name,
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
