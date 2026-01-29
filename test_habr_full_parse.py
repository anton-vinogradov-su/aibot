"""Test full Habr parsing and saving to database"""
import asyncio
from app.models import SessionLocal, Source, NewsItem
from app.tasks import parse_news_from_source


async def test_habr_full_parse():
    """Test parsing Habr and saving to database"""
    db = SessionLocal()
    try:
        # Get Habr source
        source = db.query(Source).filter(Source.name == "habr").first()

        if not source:
            print("❌ Habr source not found!")
            return

        print("=" * 80)
        print("Testing full Habr parsing cycle")
        print("=" * 80)
        print(f"Source: {source.name}")
        print(f"URL: {source.url}")
        print()

        # Count news before
        news_before = db.query(NewsItem).filter(NewsItem.source == "Habr").count()
        print(f"News in DB before: {news_before}")

        # Parse news
        print("\nParsing news from Habr...")
        await parse_news_from_source(source, db)

        # Count news after
        news_after = db.query(NewsItem).filter(NewsItem.source == "Habr").count()
        new_items = news_after - news_before

        print(f"News in DB after: {news_after}")
        print(f"New items added: {new_items}")

        # Show latest Habr news
        if new_items > 0:
            latest_news = db.query(NewsItem).filter(
                NewsItem.source == "Habr"
            ).order_by(NewsItem.created_at.desc()).limit(5).all()

            print("\n" + "=" * 80)
            print("Latest Habr news in database:")
            print("=" * 80)
            for i, news in enumerate(latest_news, 1):
                print(f"\n{i}. {news.title[:70]}...")
                print(f"   URL: {news.url}")
                print(f"   Source: {news.source}")

        print("\n" + "=" * 80)
        print("✅ Habr parsing test completed!")
        print("=" * 80)

    finally:
        db.close()


if __name__ == "__main__":
    asyncio.run(test_habr_full_parse())
