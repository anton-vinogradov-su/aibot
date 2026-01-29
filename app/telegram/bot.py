"""Telegram bot setup"""
import logging

from aiogram import Bot
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from app.config import settings

logger = logging.getLogger(__name__)


# Initialize bot instance
bot = Bot(
    token=settings.telegram_bot_token,
    default=DefaultBotProperties(parse_mode=ParseMode.MARKDOWN)
)


async def send_message_to_channel(text: str) -> bool:
    """Send message to configured Telegram channel"""
    try:
        await bot.send_message(
            chat_id=settings.telegram_channel_id,
            text=text
        )
        logger.info(f"Message sent to channel {settings.telegram_channel_id}")
        return True
    except Exception as e:
        logger.error(f"Failed to send message to channel: {e}")
        return False


async def close_bot():
    """Close bot session"""
    await bot.session.close()
