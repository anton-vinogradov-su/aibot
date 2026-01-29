"""Celery tasks for asynchronous processing"""
import asyncio
import logging
from datetime import datetime

from sqlalchemy import and_

from app.ai.generator import post_generator
from app.config import settings
from app.models import Keyword, NewsItem, Post, SessionLocal, Source
from app.news_parser.sites import get_parser
from app.telegram.publisher import telegram_publisher

logger = logging.getLogger(__name__)


def filter_news_by_keywords(news_item: NewsItem, keywords: list[str]) -> bool:
    """Filter news by keywords"""
    if not keywords:
        return True  # If no keywords, accept all news

    text = f"{news_item.title} {news_item.summary or ''}".lower()

    for keyword in keywords:
        if keyword.lower() in text:
            return True

    return False


def is_duplicate_news(url: str, db) -> bool:
    """Check if news already exists in database"""
    existing = db.query(NewsItem).filter(NewsItem.url == url).first()
    return existing is not None


async def parse_news_from_source(source: Source, db):
    """Parse news from a single source"""
    try:
        logger.info(f"Parsing news from {source.name}")

        # Get appropriate parser
        parser = get_parser(source.name.lower())
        if not parser:
            logger.error(f"No parser found for {source.name}")
            return

        # Parse news
        news_items = await parser.parse(source.url)

        # Get keywords for filtering
        keywords = [kw.word for kw in db.query(Keyword).all()]

        # Process each news item
        saved_count = 0
        for item in news_items:
            # Check for duplicates
            if is_duplicate_news(item['url'], db):
                logger.debug(f"Skipping duplicate: {item['url']}")
                continue

            # Create NewsItem object for filtering
            news_item = NewsItem(**item)

            # Filter by keywords
            if not filter_news_by_keywords(news_item, keywords):
                logger.debug(f"Filtered out by keywords: {item['title'][:50]}...")
                continue

            # Save to database
            db.add(news_item)
            saved_count += 1

        db.commit()
        logger.info(f"Saved {saved_count} new items from {source.name}")

    except Exception as e:
        logger.error(f"Error parsing news from {source.name}: {e}")
        db.rollback()


async def generate_and_publish_posts(db):
    """Generate AI posts and publish them"""
    try:
        # Find news items without posts
        news_without_posts = db.query(NewsItem).outerjoin(Post).filter(
            Post.id == None
        ).limit(5).all()  # Process 5 at a time

        for news_item in news_without_posts:
            try:
                # Generate post
                logger.info(f"Generating post for news {news_item.id}")
                generated_text = await post_generator.generate_post(
                    title=news_item.title,
                    summary=news_item.summary or news_item.title,
                    url=news_item.url
                )

                if not generated_text:
                    logger.warning(f"Failed to generate post for news {news_item.id}")
                    continue

                # Create post record
                post = Post(
                    news_id=news_item.id,
                    generated_text=generated_text,
                    status="pending"
                )
                db.add(post)
                db.commit()
                db.refresh(post)

                # Publish to Telegram
                logger.info(f"Publishing post {post.id}")
                await telegram_publisher.publish_post(post, db)

                # Add delay between posts to avoid rate limits
                await asyncio.sleep(2)

            except Exception as e:
                logger.error(f"Error processing news {news_item.id}: {e}")
                continue

    except Exception as e:
        logger.error(f"Error in generate_and_publish_posts: {e}")
        db.rollback()


# Main parsing task
def parse_all_sources_task():
    """Main task to parse all enabled sources"""
    db = SessionLocal()
    try:
        logger.info("Starting news parsing task")

        # Get all enabled sources
        sources = db.query(Source).filter(Source.enabled == True).all()

        if not sources:
            logger.warning("No enabled sources found")
            return

        # Parse each source
        for source in sources:
            asyncio.run(parse_news_from_source(source, db))

        logger.info("News parsing completed")

    except Exception as e:
        logger.error(f"Error in parse_all_sources_task: {e}")
    finally:
        db.close()


def generate_and_publish_task():
    """Task to generate and publish posts"""
    db = SessionLocal()
    try:
        logger.info("Starting post generation and publishing task")
        asyncio.run(generate_and_publish_posts(db))
        logger.info("Post generation and publishing completed")
    except Exception as e:
        logger.error(f"Error in generate_and_publish_task: {e}")
    finally:
        db.close()
