# News Parser Module

Модуль для парсинга новостей из различных источников.

## Структура

```
news_parser/
├── __init__.py           # Инициализация модуля
├── sites.py              # Базовый класс NewsParser и фабрика get_parser()
├── rbc_parser.py         # Парсер для RBC.ru (все рубрики)
└── habr_parser.py        # Парсер для Habr.com
```

## Базовый класс NewsParser

Находится в `sites.py`. Предоставляет общую функциональность:
- `fetch_page(url)` - получение HTML страницы
- `parse(url)` - абстрактный метод для парсинга (реализуется в подклассах)

## Парсеры

### RBC Parser

**Файл**: `rbc_parser.py`

**Поддерживаемые рубрики**:
- Политика: `/rubric/politics`
- Экономика: `/rubric/economics`
- Бизнес: `/rubric/business`
- Финансы: `/rubric/finances`
- Технологии и медиа: `/rubric/technology_and_media`
- Общество: `/rubric/society`
- Свое дело: `/rubric/own_business`
- Спорт: `/sport`
- Происшествия: `/rbcfreenews`

**Методы**:
- `parse(url)` - парсинг новостей со страницы
- `_parse_article(article, source_name)` - парсинг отдельной новости
- `_get_source_name_from_url(url)` - определение имени источника по URL
- `fetch_full_article(url)` - получение полного текста статьи

**Возвращаемые данные**:
```python
{
    'title': str,          # Заголовок новости
    'url': str,            # URL новости
    'summary': str,        # Краткое описание
    'source': str,         # Источник (например, "RBC-Politics")
    'published_at': datetime,  # Дата публикации
    'raw_text': str|None   # Полный текст (опционально)
}
```

### Habr Parser

**Файл**: `habr_parser.py`

**URL**: `https://habr.com/ru/news/`

**Особенности**:
- Парсит новостную ленту Habr.com
- Извлекает заголовок, ссылку и краткое описание
- Поддерживает парсинг даты публикации из атрибута `datetime`
- Может получать полный текст статьи (метод `fetch_full_article`)

**Методы**:
- `parse(url)` - парсинг новостей со страницы
- `_parse_article(article_tag)` - парсинг отдельной новости
- `fetch_full_article(url)` - получение полного текста статьи

**Пример использования**:
```python
from app.news_parser.habr_parser import HabrParser

parser = HabrParser()
news = await parser.parse('https://habr.com/ru/news/')
# Возвращает список из ~20 новостей
```

## Фабрика парсеров

**Функция**: `get_parser(source_type: str) -> NewsParser`

Возвращает соответствующий парсер по типу источника:

```python
from app.news_parser.sites import get_parser

# Для RBC (любая рубрика)
parser = get_parser('rbc_politics')  # RBCParser
parser = get_parser('rbc_economics') # RBCParser
parser = get_parser('rbc')           # RBCParser

# Для Habr
parser = get_parser('habr')          # HabrParser

# Для будущих парсеров
# parser = get_parser('vc')          # VCParser
# parser = get_parser('tproger')     # TprogerParser
```

## Добавление нового парсера

1. Создайте файл `your_parser.py` в директории `news_parser/`
2. Импортируйте `NewsParser` из `sites.py`
3. Создайте класс-наследник:

```python
from app.news_parser.sites import NewsParser

class YourParser(NewsParser):
    def __init__(self):
        super().__init__()
        self.base_url = "https://example.com"

    async def parse(self, url: str = None):
        html = await self.fetch_page(url)
        # Ваша логика парсинга
        return news_items
```

4. Зарегистрируйте парсер в `sites.py`:

```python
def get_parser(source_type: str):
    # ...
    if source_type_lower == 'your_site':
        from app.news_parser.your_parser import YourParser
        return YourParser()
```

## Пример использования

```python
import asyncio
from app.news_parser.sites import get_parser

async def main():
    # Получить парсер
    parser = get_parser('rbc_politics')

    # Парсить новости
    news = await parser.parse('https://www.rbc.ru/rubric/politics')

    # Обработать результаты
    for item in news:
        print(f"{item['title']}")
        print(f"  Source: {item['source']}")
        print(f"  URL: {item['url']}")

asyncio.run(main())
```

## Тестирование

Запустите тестовый скрипт:

```bash
# В контейнере
docker-compose exec app python test_refactored_parser.py

# Или локально
python test_refactored_parser.py
```
