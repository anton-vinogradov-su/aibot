"""Test full parsing process"""
import asyncio
from app.models import SessionLocal
from app.tasks import parse_news_from_source, Source


async def test_full_parsing():
    db = SessionLocal()
    try:
        # Get RBC source
        source = db.query(Source).filter(Source.name == "rbc").first()

        if not source:
            print("RBC source not found!")
            return

        print(f"Testing parsing from: {source.name}")
        print(f"URL: {source.url}")
        print(f"Enabled: {source.enabled}")
        print()

        # Parse news
        await parse_news_from_source(source, db)

        # Check results
        from app.models import NewsItem
        news_count = db.query(NewsItem).count()
        print(f"\nTotal news items in database: {news_count}")

        # Show latest news
        latest_news = db.query(NewsItem).order_by(NewsItem.created_at.desc()).limit(5).all()
        print(f"\nLatest {len(latest_news)} news items:")
        for i, news in enumerate(latest_news, 1):
            print(f"\n{i}. {news.title[:80]}")
            print(f"   Source: {news.source}")
            print(f"   URL: {news.url[:80]}...")

    finally:
        db.close()


if __name__ == "__main__":
    asyncio.run(test_full_parsing())
