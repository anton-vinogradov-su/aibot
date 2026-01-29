"""Test RBC parser"""
import asyncio
from app.news_parser.sites import RBCParser


async def test_parser():
    parser = RBCParser()
    url = "https://www.rbc.ru/rubric/politics"

    print(f"Testing parser for: {url}")
    news = await parser.parse(url)

    print(f"\nFound {len(news)} news items:")
    for i, item in enumerate(news[:5], 1):
        print(f"\n{i}. {item['title'][:100]}")
        print(f"   URL: {item['url']}")
        print(f"   Summary: {item['summary'][:100] if item['summary'] else 'N/A'}")


if __name__ == "__main__":
    asyncio.run(test_parser())
