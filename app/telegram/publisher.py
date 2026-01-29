"""Telegram post publisher"""
import logging
from datetime import datetime
from typing import Optional

from sqlalchemy.orm import Session

from app.models import Post
from app.telegram.bot import send_message_to_channel

logger = logging.getLogger(__name__)


class TelegramPublisher:
    """Publisher for Telegram posts"""

    async def publish_post(self, post: Post, db: Session) -> bool:
        """Publish post to Telegram channel"""
        try:
            # Send message to channel
            success = await send_message_to_channel(post.generated_text)

            if success:
                # Update post status
                post.status = "published"
                post.published_at = datetime.utcnow()
                post.error_message = None
                logger.info(f"Post {post.id} published successfully")
            else:
                post.status = "failed"
                post.error_message = "Failed to send message to channel"
                logger.error(f"Post {post.id} publication failed")

            db.commit()
            return success

        except Exception as e:
            logger.error(f"Error publishing post {post.id}: {e}")
            post.status = "failed"
            post.error_message = str(e)
            db.commit()
            return False

    async def check_duplicate(self, text: str, db: Session) -> bool:
        """Check if similar post already exists"""
        # Simple duplicate check - you can implement more sophisticated logic
        existing = db.query(Post).filter(
            Post.generated_text == text,
            Post.status == "published"
        ).first()

        return existing is not None


# Global publisher instance
telegram_publisher = TelegramPublisher()
