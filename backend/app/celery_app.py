"""
NaviAid Celery App – background tasks (e.g. re-embedding).
"""
from celery import Celery
from app.config import settings

celery_app = Celery(
    "naviaid",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
    include=["app.tasks"],
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="Asia/Kolkata",
    enable_utc=True,
)
