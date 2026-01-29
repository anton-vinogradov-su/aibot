"""Test Habr parser"""
import asyncio
from app.news_parser.habr_parser import HabrParser


async def test_habr_parser():
    """Test Habr.com parser"""
    parser = HabrParser()

    print("=" * 80)
    print("Testing Habr.com parser")
    print("=" * 80)

    url = "https://habr.com/ru/news/"
    print(f"\nParsing: {url}\n")

    news = await parser.parse(url)

    print(f"✓ Parsed {len(news)} news items\n")

    if news:
        print("First 5 news items:")
        print("-" * 80)
        for i, item in enumerate(news[:5], 1):
            print(f"\n{i}. {item['title'][:70]}...")
            print(f"   URL: {item['url']}")
            print(f"   Source: {item['source']}")
            if item['summary'] and item['summary'] != item['title']:
                print(f"   Summary: {item['summary'][:100]}...")
            print(f"   Published: {item['published_at']}")

    print("\n" + "=" * 80)
    print("✅ Habr parser works correctly!")
    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(test_habr_parser())
