"""Send news to Telegram with custom OpenAI prompt"""
import asyncio
from app.models import SessionLocal, NewsItem, Post
from app.ai.openai_client import openai_client
from app.telegram.publisher import telegram_publisher


async def send_with_custom_prompt():
    db = SessionLocal()
    try:
        # Get all news items
        news_items = db.query(NewsItem).order_by(NewsItem.created_at.desc()).limit(10).all()

        if not news_items:
            print("No news items found in database!")
            return

        # Show available news
        print("=" * 80)
        print("Available news items:")
        print("=" * 80)
        for i, news in enumerate(news_items, 1):
            print(f"\n{i}. {news.title[:70]}")
            print(f"   Source: {news.source}")
            print(f"   URL: {news.url[:80]}...")

        # Select news
        print("\n" + "=" * 80)
        choice = input("Select news number (1-10): ").strip()

        try:
            choice = int(choice)
            if choice < 1 or choice > len(news_items):
                print("Invalid choice!")
                return
            selected_news = news_items[choice - 1]
        except ValueError:
            print("Invalid input!")
            return

        print("\n" + "=" * 80)
        print(f"Selected: {selected_news.title}")
        print("=" * 80)

        # Get custom prompt
        print("\nEnter your custom prompt for OpenAI:")
        print("(You can use {title}, {summary}, {url} as placeholders)")
        print("\nExample prompt:")
        print("Напиши короткий пост для Instagram на основе этой новости:")
        print("Заголовок: {title}")
        print("Описание: {summary}")
        print("Ссылка: {url}")
        print("\n" + "-" * 80)

        print("\nEnter your prompt (type 'END' on a new line when done):")
        lines = []
        while True:
            line = input()
            if line.strip() == 'END':
                break
            lines.append(line)

        custom_prompt = '\n'.join(lines)

        if not custom_prompt.strip():
            print("Prompt cannot be empty!")
            return

        # Replace placeholders
        prompt = custom_prompt.format(
            title=selected_news.title,
            summary=selected_news.summary or selected_news.title,
            url=selected_news.url
        )

        print("\n" + "=" * 80)
        print("Final prompt:")
        print("=" * 80)
        print(prompt)
        print("\n" + "=" * 80)

        # Generate with OpenAI
        print("\nGenerating post with OpenAI...")
        generated_text = await openai_client.generate_completion(
            prompt=prompt,
            max_tokens=500,
            temperature=0.7
        )

        if not generated_text:
            print("Failed to generate post!")
            return

        print("\n" + "=" * 80)
        print("Generated post:")
        print("=" * 80)
        print(generated_text)
        print("\n" + "=" * 80)

        # Ask for confirmation
        confirm = input("\nSend this post to Telegram? (yes/no): ").strip().lower()

        if confirm not in ['yes', 'y', 'да']:
            print("Cancelled.")
            return

        # Create post record
        post = Post(
            news_id=selected_news.id,
            generated_text=generated_text,
            status="pending"
        )
        db.add(post)
        db.commit()
        db.refresh(post)

        print(f"\nPost created with ID: {post.id}")

        # Publish to Telegram
        print("Publishing to Telegram channel...")
        success = await telegram_publisher.publish_post(post, db)

        if success:
            print(f"\n✅ Successfully published to Telegram!")
            print(f"Post ID: {post.id}")
            print(f"Post status: {post.status}")
        else:
            print(f"\n❌ Failed to publish to Telegram")
            print(f"Error: {post.error_message}")

    finally:
        db.close()


if __name__ == "__main__":
    asyncio.run(send_with_custom_prompt())
