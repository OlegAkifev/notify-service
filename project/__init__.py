# Инициализация Celery при импорте Django
from .celery import app as celery_app

__all__ = ("celery_app",)
