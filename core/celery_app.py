from celery import Celery

from core.config import settings

celery_app = Celery(
    "src",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
)

celery_app.autodiscover_tasks(["src.tasks"])
