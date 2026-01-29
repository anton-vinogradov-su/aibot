"""Celery worker configuration"""
from celery import Celery
from celery.schedules import crontab

from app.config import settings
from app.tasks import generate_and_publish_task, parse_all_sources_task

# Create Celery app
celery_app = Celery(
    'aibot',
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend
)

# Celery configuration
celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 minutes
    task_soft_time_limit=25 * 60,  # 25 minutes
)


# Register tasks
@celery_app.task(name='parse_news')
def parse_news():
    """Parse news from all sources"""
    return parse_all_sources_task()


@celery_app.task(name='generate_and_publish')
def generate_and_publish():
    """Generate and publish posts"""
    return generate_and_publish_task()


# Celery Beat schedule
celery_app.conf.beat_schedule = {
    'parse-news-task': {
        'task': 'parse_news',
        'schedule': crontab(minute=f'*/{settings.parse_interval_minutes}'),
    },
    'generate-and-publish-posts': {
        'task': 'generate_and_publish',
        'schedule': crontab(minute=f'*/{settings.parse_interval_minutes}'),
    },
}
