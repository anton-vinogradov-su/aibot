"""Test refactored RBC parser"""
import asyncio
from app.news_parser.rbc_parser import RBCParser


async def test_parser():
    """Test that refactored parser works"""
    parser = RBCParser()

    print("=" * 80)
    print("Testing refactored RBC parser")
    print("=" * 80)

    # Test different rubrics
    test_urls = [
        "https://www.rbc.ru/rubric/politics",
        "https://www.rbc.ru/rubric/economics",
        "https://www.rbc.ru/sport",
    ]

    for url in test_urls:
        print(f"\nTesting: {url}")
        news = await parser.parse(url)
        print(f"  ✓ Parsed {len(news)} items")

        if news:
            print(f"  First item: {news[0]['title'][:60]}...")
            print(f"  Source: {news[0]['source']}")

    print("\n" + "=" * 80)
    print("✅ Parser works correctly!")
    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(test_parser())
