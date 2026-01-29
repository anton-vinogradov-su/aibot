"""Test bot connection and channel access"""
import asyncio
from app.telegram.bot import bot
from app.config import settings


async def test_bot():

    print("Testing Telegram Bot Connection...\n")

    # Get bot info
    try:
        me = await bot.get_me()
        print(f"✅ Bot connected successfully!")
        print(f"Bot username: @{me.username}")
        print(f"Bot name: {me.first_name}")
        print(f"Bot ID: {me.id}\n")
    except Exception as e:
        print(f"❌ Failed to connect bot: {e}")
        return

    # Test channel access
    print(f"Testing channel access: {settings.telegram_channel_id}")
    try:
        chat = await bot.get_chat(settings.telegram_channel_id)
        print(f"✅ Channel found!")
        print(f"Channel title: {chat.title}")
        print(f"Channel type: {chat.type}")
        print(f"Channel ID: {chat.id}\n")

        # Try to get chat administrators
        try:
            admins = await bot.get_chat_administrators(settings.telegram_channel_id)
            print(f"Channel administrators ({len(admins)}):")
            bot_is_admin = False
            for admin in admins:
                is_bot_marker = " ⭐ (THIS BOT)" if admin.user.id == me.id else ""
                print(f"  - @{admin.user.username or admin.user.first_name}{is_bot_marker}")
                if admin.user.id == me.id:
                    bot_is_admin = True

            if bot_is_admin:
                print(f"\n✅ Bot is an administrator of the channel!")
            else:
                print(f"\n❌ Bot is NOT an administrator of the channel!")
                print("Please add the bot to the channel as an administrator.")
        except Exception as e:
            print(f"Could not get administrators: {e}")

    except Exception as e:
        print(f"❌ Failed to access channel: {e}")
        print("\nPossible issues:")
        print("1. Channel username is incorrect")
        print("2. Channel is private and bot is not a member")
        print("3. Bot is not added to the channel as administrator")
        print("\nTo fix:")
        print(f"1. Go to your Telegram channel: {settings.telegram_channel_id}")
        print(f"2. Add @{me.username} as an administrator")
        print("3. Give it permission to 'Post messages'")

    await bot.session.close()


if __name__ == "__main__":
    asyncio.run(test_bot())
