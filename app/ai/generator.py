"""AI post generator"""
import logging
from typing import Optional

from app.ai.openai_client import openai_client

logger = logging.getLogger(__name__)


class PostGenerator:
    """Generate attractive Telegram posts from news"""

    def __init__(self):
        self.client = openai_client

    def _create_prompt(self, title: str, summary: str, url: str) -> str:
        """Create prompt for AI post generation"""
        prompt = f"""
Создай привлекательный пост для Telegram-канала на основе этой новости:

Заголовок: {title}
Описание: {summary}
Ссылка для подробностей: {url}

Требования:
- Длина 150-300 символов
- 1-2 эмодзи для привлечения внимания
- Краткое изложение сути новости
- Призыв к действию (прочитать, узнать больше и т.д.)
- Используй форматирование Markdown для ссылок

Важно: пост должен быть строго по теме этой новости, не выдумывай другие факты.
"""
        return prompt

    async def generate_post(
        self,
        title: str,
        summary: str,
        url: str
    ) -> Optional[str]:
        """Generate post from news item"""
        try:
            prompt = self._create_prompt(title, summary, url)
            post_text = await self.client.generate_completion(
                prompt=prompt,
                max_tokens=500,
                temperature=0.7
            )

            if post_text:
                logger.info(f"Generated post for: {title[:50]}...")
                return post_text.strip()

            logger.warning(f"Failed to generate post for: {title[:50]}...")
            return None

        except Exception as e:
            logger.error(f"Error generating post: {e}")
            return None

    async def test_generation(self, test_title: str = "Тестовая новость"):
        """Test post generation with sample data"""
        sample_summary = "Это тестовая новость для проверки работы AI-генератора."
        sample_url = "https://example.com/test"

        post = await self.generate_post(test_title, sample_summary, sample_url)
        return post


# Global generator instance
post_generator = PostGenerator()
