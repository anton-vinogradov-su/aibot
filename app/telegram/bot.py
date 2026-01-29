"""Telegram bot setup"""
import logging

from aiogram import Bot
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from app.config import settings

logger = logging.getLogger(__name__)


async def send_message_to_channel(text: str) -> bool:
    """Send message to configured Telegram channel"""
    bot = None
    try:
        # Create new bot instance for each message to avoid event loop issues
        bot = Bot(
            token=settings.telegram_bot_token,
            default=DefaultBotProperties(parse_mode=ParseMode.MARKDOWN)
        )

        await bot.send_message(
            chat_id=settings.telegram_channel_id,
            text=text
        )
        logger.info(f"Message sent to channel {settings.telegram_channel_id}")
        return True
    except Exception as e:
        logger.error(f"Failed to send message to channel: {e}")
        return False
    finally:
        # Close bot session properly
        if bot:
            try:
                await bot.session.close()
            except Exception as e:
                logger.error(f"Error closing bot session: {e}")
