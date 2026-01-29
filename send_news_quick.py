"""Quick send news with custom prompt"""
import asyncio
import sys
from app.models import SessionLocal, NewsItem, Post
from app.ai.openai_client import openai_client
from app.telegram.publisher import telegram_publisher


async def send_quick(news_index: int = 2, custom_prompt: str = None):
    """
    Send news to Telegram with custom prompt

    Args:
        news_index: Index of news item (1-based)
        custom_prompt: Custom prompt for OpenAI
    """
    db = SessionLocal()
    try:
        # Get news item
        news_items = db.query(NewsItem).order_by(NewsItem.created_at.desc()).all()

        if not news_items:
            print("No news items found!")
            return

        if news_index < 1 or news_index > len(news_items):
            print(f"Invalid index! Available: 1-{len(news_items)}")
            return

        selected_news = news_items[news_index - 1]

        print("=" * 80)
        print(f"Selected news #{news_index}:")
        print("=" * 80)
        print(f"Title: {selected_news.title}")
        print(f"URL: {selected_news.url}")
        print(f"Summary: {selected_news.summary}")
        print()

        # Default prompt if not provided
        if not custom_prompt:
            custom_prompt = """Создай короткий и привлекательный пост для Telegram канала на основе этой новости:

Заголовок: {title}
Описание: {summary}

Требования:
- Длина: 100-200 слов
- Добавь 1-2 релевантных эмодзи в начале
- Стиль: информативный и увлекательный
- В конце добавь ссылку: {url}
- Используй Markdown форматирование для Telegram"""

        # Format prompt
        prompt = custom_prompt.format(
            title=selected_news.title,
            summary=selected_news.summary or selected_news.title,
            url=selected_news.url
        )

        print("Prompt for OpenAI:")
        print("-" * 80)
        print(prompt)
        print("-" * 80)
        print()

        # Generate with OpenAI
        print("Generating post with OpenAI GPT-4...")
        generated_text = await openai_client.generate_completion(
            prompt=prompt,
            max_tokens=500,
            temperature=0.7
        )

        if not generated_text:
            print("❌ Failed to generate post!")
            return

        print()
        print("=" * 80)
        print("Generated post:")
        print("=" * 80)
        print(generated_text)
        print("=" * 80)
        print()

        # Create post record
        post = Post(
            news_id=selected_news.id,
            generated_text=generated_text,
            status="pending"
        )
        db.add(post)
        db.commit()
        db.refresh(post)

        print(f"Post created with ID: {post.id}")
        print()

        # Publish to Telegram
        print("Publishing to Telegram channel...")
        success = await telegram_publisher.publish_post(post, db)

        if success:
            print(f"✅ Successfully published to Telegram!")
            print(f"Post ID: {post.id}")
            print(f"Status: {post.status}")
            print(f"Published at: {post.published_at}")
        else:
            print(f"❌ Failed to publish")
            print(f"Error: {post.error_message}")

    finally:
        db.close()


if __name__ == "__main__":
    # Can pass news index as argument
    news_idx = int(sys.argv[1]) if len(sys.argv) > 1 else 2
    asyncio.run(send_quick(news_idx))
