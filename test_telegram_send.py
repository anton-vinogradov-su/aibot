"""Test generating and sending a post to Telegram"""
import asyncio
from app.models import SessionLocal, NewsItem, Post
from app.ai.generator import post_generator
from app.telegram.publisher import telegram_publisher


async def test_send_to_telegram():
    db = SessionLocal()
    try:
        # Get first news item
        news = db.query(NewsItem).first()

        if not news:
            print("No news items found in database!")
            return

        print(f"Selected news: {news.title}")
        print(f"URL: {news.url}")
        print(f"Summary: {news.summary}\n")

        # Generate post
        print("Generating post with OpenAI...")
        generated_text = await post_generator.generate_post(
            title=news.title,
            summary=news.summary or news.title,
            url=news.url
        )

        if not generated_text:
            print("Failed to generate post!")
            return

        print(f"\nGenerated post:\n{generated_text}\n")

        # Create post record
        post = Post(
            news_id=news.id,
            generated_text=generated_text,
            status="pending"
        )
        db.add(post)
        db.commit()
        db.refresh(post)

        print(f"Post created with ID: {post.id}")

        # Publish to Telegram
        print("\nPublishing to Telegram channel...")
        success = await telegram_publisher.publish_post(post, db)

        if success:
            print(f"✅ Successfully published to Telegram!")
            print(f"Post status: {post.status}")
        else:
            print(f"❌ Failed to publish to Telegram")
            print(f"Error: {post.error_message}")

    finally:
        db.close()


if __name__ == "__main__":
    asyncio.run(test_send_to_telegram())
