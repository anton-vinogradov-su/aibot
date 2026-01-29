"""Test parsing from all RBC rubrics"""
import asyncio
from app.models import SessionLocal, Source, NewsItem
from app.tasks import parse_news_from_source


async def test_all_rubrics():
    """Test parsing from all RBC rubrics"""
    db = SessionLocal()
    try:
        # Get all enabled sources
        sources = db.query(Source).filter(Source.enabled == True).all()

        print("=" * 80)
        print(f"Testing {len(sources)} sources")
        print("=" * 80)

        total_parsed = 0
        results = []

        for source in sources:
            print(f"\nParsing: {source.name}")
            print(f"URL: {source.url}")

            news_before = db.query(NewsItem).filter(NewsItem.source.like(f"%{source.name.split('_')[1] if '_' in source.name else 'RBC'}%")).count()

            # Parse news
            await parse_news_from_source(source, db)

            news_after = db.query(NewsItem).filter(NewsItem.source.like(f"%{source.name.split('_')[1] if '_' in source.name else 'RBC'}%")).count()

            new_items = news_after - news_before
            total_parsed += new_items

            results.append({
                'source': source.name,
                'parsed': new_items
            })

            print(f"  ✓ Parsed {new_items} new items")

        print("\n" + "=" * 80)
        print("SUMMARY:")
        print("=" * 80)
        for result in results:
            print(f"  {result['source']}: {result['parsed']} news")

        print(f"\nTotal new items parsed: {total_parsed}")
        print(f"Total news in database: {db.query(NewsItem).count()}")

    finally:
        db.close()


if __name__ == "__main__":
    asyncio.run(test_all_rubrics())
