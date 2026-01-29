"""Get Telegram channel ID"""
import asyncio
from aiogram import Bot
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from app.config import settings


async def get_channel_id():
    bot = Bot(
        token=settings.telegram_bot_token,
        default=DefaultBotProperties(parse_mode=ParseMode.MARKDOWN)
    )

    print("=" * 60)
    print("Telegram Channel ID Finder")
    print("=" * 60)

    me = await bot.get_me()
    print(f"\n✅ Bot: @{me.username} (ID: {me.id})\n")

    print("Method 1: If you know the channel username")
    print("-" * 60)
    channel_username = input("Enter channel username (e.g. @mychannel or mychannel): ").strip()

    if channel_username:
        if not channel_username.startswith('@'):
            channel_username = '@' + channel_username

        try:
            chat = await bot.get_chat(channel_username)
            print(f"\n✅ Channel found!")
            print(f"Title: {chat.title}")
            print(f"Username: @{chat.username}")
            print(f"Numeric ID: {chat.id}")
            print(f"\nUse this in .env file:")
            print(f"TELEGRAM_CHANNEL_ID={chat.id}")
            await bot.session.close()
            return
        except Exception as e:
            print(f"\n❌ Channel not found: {e}")
            print("\nTrying alternative methods...\n")

    print("\nMethod 2: Forward a message from your channel")
    print("-" * 60)
    print("1. Forward ANY message from your channel to this bot:")
    print(f"   @{me.username}")
    print("2. Then run this script again with --updates flag")
    print(f"\n   docker-compose exec app python get_channel_id.py --updates")

    print("\nMethod 3: Add bot to channel and post")
    print("-" * 60)
    print(f"1. Add @{me.username} to your channel as administrator")
    print("2. Post any message to the channel")
    print("3. Run this script with --updates flag:")
    print(f"\n   docker-compose exec app python get_channel_id.py --updates")

    await bot.session.close()


async def get_updates():
    """Get recent updates to find channel ID"""
    bot = Bot(
        token=settings.telegram_bot_token,
        default=DefaultBotProperties(parse_mode=ParseMode.MARKDOWN)
    )

    print("Fetching recent updates...\n")

    try:
        updates = await bot.get_updates(limit=20)

        if not updates:
            print("No recent updates found.")
            print("\nPlease:")
            print("1. Forward a message from your channel to the bot, OR")
            print("2. Post a message in the channel where bot is admin")
            print("\nThen run this command again.")
            await bot.session.close()
            return

        print(f"Found {len(updates)} recent updates:\n")

        channels_found = set()

        for update in updates:
            # Check for forwarded messages
            if update.message and update.message.forward_from_chat:
                chat = update.message.forward_from_chat
                if chat.type in ['channel', 'supergroup']:
                    channels_found.add((chat.id, chat.title, chat.username))
                    print(f"📢 Channel from forwarded message:")
                    print(f"   Title: {chat.title}")
                    print(f"   Username: @{chat.username if chat.username else 'N/A'}")
                    print(f"   ID: {chat.id}")
                    print()

            # Check for channel posts
            if update.channel_post:
                chat = update.channel_post.chat
                channels_found.add((chat.id, chat.title, chat.username))
                print(f"📢 Channel from post:")
                print(f"   Title: {chat.title}")
                print(f"   Username: @{chat.username if chat.username else 'N/A'}")
                print(f"   ID: {chat.id}")
                print()

        if channels_found:
            print("\n" + "=" * 60)
            print("Use one of these IDs in your .env file:")
            print("=" * 60)
            for chat_id, title, username in channels_found:
                print(f"TELEGRAM_CHANNEL_ID={chat_id}  # {title}")
        else:
            print("No channels found in recent updates.")
            print("\nPlease forward a message from your channel to the bot")
            print("or post a message in a channel where the bot is admin.")

    except Exception as e:
        print(f"Error: {e}")

    await bot.session.close()


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == '--updates':
        asyncio.run(get_updates())
    else:
        asyncio.run(get_channel_id())
