# AI News Bot - Генератор постов для Telegram

Автоматизированный сервис для сбора новостей, генерации AI-контента и публикации в Telegram-канале.

## Возможности

- Парсинг новостей с веб-сайтов (RBC.ru)
- Фильтрация новостей по ключевым словам
- AI-генерация привлекательных постов через OpenAI GPT-4
- Автоматическая публикация в Telegram-канал через aiogram
- Асинхронная обработка с помощью Celery и Redis
- REST API для управления источниками, ключевыми словами и мониторинга
- Автоматическая документация Swagger/OpenAPI

## Технологический стек

- **Python 3.12**
- **FastAPI** - веб-фреймворк и REST API
- **SQLAlchemy** - ORM для работы с PostgreSQL
- **PostgreSQL** - основная база данных
- **Redis** - брокер сообщений для Celery
- **Celery** - асинхронные задачи и планировщик
- **aiogram 3.x** - Telegram Bot API
- **OpenAI API** - генерация контента
- **BeautifulSoup4** - парсинг веб-страниц
- **Docker & Docker Compose** - контейнеризация

## Структура проекта

```
aibot/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI приложение
│   ├── config.py            # Конфигурация
│   ├── models.py            # SQLAlchemy модели
│   ├── tasks.py             # Celery задачи
│   ├── utils.py             # Утилиты
│   ├── api/
│   │   ├── endpoints.py     # API endpoints
│   │   └── schemas.py       # Pydantic схемы
│   ├── news_parser/
│   │   ├── sites.py         # Парсеры сайтов
│   │   └── telegram.py      # Парсер Telegram
│   ├── ai/
│   │   ├── openai_client.py # OpenAI клиент
│   │   └── generator.py     # Генератор постов
│   └── telegram/
│       ├── bot.py           # Telegram бот
│       └── publisher.py     # Публикация постов
├── celery_worker.py         # Celery worker
├── docker-compose.yml       # Docker Compose конфигурация
├── Dockerfile               # Docker образ
├── requirements.txt         # Python зависимости
├── .env.example             # Пример переменных окружения
└── README.md                # Документация
```

## Установка и запуск

### Предварительные требования

- Docker и Docker Compose
- API ключ OpenAI
- Telegram Bot Token (получить у @BotFather)
- Telegram канал (бот должен быть администратором)

### Шаг 1: Клонирование и настройка

```bash
# Перейти в директорию проекта
cd aibot

# Скопировать пример конфигурации
cp .env.example .env

# Отредактировать .env файл
nano .env
```

### Шаг 2: Настройка переменных окружения

Отредактируйте `.env` файл:

```env
# Database
DATABASE_URL=postgresql://aibot:aibot_password@db:5432/aibot_db

# Redis
REDIS_URL=redis://redis:6379/0

# OpenAI
OPENAI_API_KEY=your_openai_api_key_here

# Telegram
TELEGRAM_BOT_TOKEN=your_bot_token_here
TELEGRAM_CHANNEL_ID=@your_channel_name_or_id

# Celery
CELERY_BROKER_URL=redis://redis:6379/0
CELERY_RESULT_BACKEND=redis://redis:6379/0

# Parsing settings
PARSE_INTERVAL_MINUTES=30
```

### Шаг 3: Запуск через Docker Compose

```bash
# Сборка и запуск всех сервисов
docker-compose up --build

# Или в фоновом режиме
docker-compose up -d --build
```

Это запустит:
- PostgreSQL (порт 5432)
- Redis (порт 6379)
- FastAPI приложение (порт 8000)
- Celery Worker
- Celery Beat (планировщик)

### Шаг 4: Инициализация данных

После запуска нужно добавить источник новостей:

```bash
# Добавить RBC как источник
curl -X POST http://localhost:8000/api/sources \
  -H "Content-Type: application/json" \
  -d '{
    "type": "website",
    "name": "rbc",
    "url": "https://www.rbc.ru/politics/",
    "enabled": true
  }'
```

Опционально добавить ключевые слова для фильтрации:

```bash
curl -X POST http://localhost:8000/api/keywords \
  -H "Content-Type: application/json" \
  -d '{"word": "технологии"}'

curl -X POST http://localhost:8000/api/keywords \
  -H "Content-Type: application/json" \
  -d '{"word": "искусственный интеллект"}'
```

## Использование

### REST API

API доступен по адресу: `http://localhost:8000`

**Swagger документация**: `http://localhost:8000/docs`

#### Основные endpoints:

**Источники новостей:**
- `GET /api/sources` - получить все источники
- `POST /api/sources` - создать источник
- `PATCH /api/sources/{id}` - обновить источник
- `DELETE /api/sources/{id}` - удалить источник

**Ключевые слова:**
- `GET /api/keywords` - получить все ключевые слова
- `POST /api/keywords` - создать ключевое слово
- `DELETE /api/keywords/{id}` - удалить ключевое слово

**Новости:**
- `GET /api/news` - получить список новостей
- `GET /api/news/{id}` - получить конкретную новость

**Посты:**
- `GET /api/posts` - получить список постов
- `GET /api/posts?status=published` - фильтр по статусу
- `GET /api/posts/{id}` - получить конкретный пост

**Статистика:**
- `GET /api/stats` - получить статистику системы

### Примеры запросов

**Получить статистику:**
```bash
curl http://localhost:8000/api/stats
```

**Получить последние посты:**
```bash
curl http://localhost:8000/api/posts?limit=10
```

**Получить опубликованные посты:**
```bash
curl http://localhost:8000/api/posts?status=published
```

## Автоматические задачи

Celery Beat выполняет следующие задачи:

1. **Парсинг новостей** - каждые 30 минут
   - Собирает новости из всех активных источников
   - Фильтрует по ключевым словам
   - Сохраняет в базу данных

2. **Генерация и публикация** - каждый час (в 5 минут)
   - Генерирует AI-посты для новых новостей
   - Публикует в Telegram-канал
   - Обновляет статусы

## Мониторинг

### Логи

```bash
# Логи всех сервисов
docker-compose logs -f

# Логи конкретного сервиса
docker-compose logs -f app
docker-compose logs -f celery_worker
docker-compose logs -f celery_beat
```

### Проверка состояния

```bash
# Health check
curl http://localhost:8000/health

# Статистика
curl http://localhost:8000/api/stats
```

## Разработка

### Локальный запуск без Docker

```bash
# Установить зависимости
pip install -r requirements.txt

# Запустить PostgreSQL и Redis отдельно
# Обновить DATABASE_URL и REDIS_URL в .env

# Запустить FastAPI
uvicorn app.main:app --reload

# В другом терминале запустить Celery Worker
celery -A celery_worker worker --loglevel=info

# В третьем терминале запустить Celery Beat
celery -A celery_worker beat --loglevel=info
```

## Тестирование

### Ручное тестирование парсера

```python
import asyncio
from app.news_parser.sites import RBCParser

async def test():
    parser = RBCParser()
    news = await parser.parse()
    for item in news[:3]:
        print(f"Title: {item['title']}")
        print(f"URL: {item['url']}")
        print("---")

asyncio.run(test())
```

### Тестирование AI генератора

```python
import asyncio
from app.ai.generator import post_generator

async def test():
    post = await post_generator.generate_post(
        title="Тестовая новость",
        summary="Описание новости для теста",
        url="https://example.com"
    )
    print(post)

asyncio.run(test())
```

## Troubleshooting

### База данных не инициализируется

```bash
# Пересоздать контейнеры
docker-compose down -v
docker-compose up --build
```

### Celery не подключается к Redis

Проверьте, что Redis запущен:
```bash
docker-compose ps
```

### Ошибки OpenAI API

- Проверьте правильность API ключа
- Убедитесь, что у вас есть доступ к GPT-4
- Проверьте лимиты использования API

### Telegram bot не публикует

- Убедитесь, что бот добавлен в канал как администратор
- Проверьте правильность TELEGRAM_CHANNEL_ID (должно начинаться с @ или быть числовым ID)
- Проверьте TELEGRAM_BOT_TOKEN

## Чек-лист функциональности

- [x] Сбор и хранение новостей
- [x] Celery и Redis брокер
- [x] Интеграция с Telegram через aiogram
- [x] AI-генерация постов через OpenAI
- [x] Фильтрация по ключевым словам
- [x] REST API для управления
- [x] FastAPI документация (Swagger)
- [x] Логирование
- [x] Docker Compose
- [x] README с инструкциями

## Возможные улучшения

- Добавить больше источников новостей (Habr, VC, Tproger)
- Реализовать парсинг Telegram каналов
- Добавить веб-интерфейс для управления
- Реализовать более сложную фильтрацию и дедупликацию
- Добавить метрики и мониторинг (Prometheus, Grafana)
- Добавить unit и integration тесты
- Реализовать retry механизм для failed постов
- Добавить поддержку изображений в постах

## Лицензия

MIT

## Автор

Проект разработан в рамках курса JavaRush Module 4
