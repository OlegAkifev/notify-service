from celery import shared_task
from django.db import transaction
from .models import Notification
from .services.notifier import Notifier

@shared_task(bind=True, max_retries=3, autoretry_for=(Exception,), retry_backoff=5)
def send_notification_task(self, notification_id: int):
    """
    Celery-задача: достаёт уведомление из БД и запускает Notifier.
    Автоматический ретрай задачи на случай временных сбоёв (уровень выше попыток каналов).
    """
    notifier = Notifier()
    with transaction.atomic():
        notification = Notification.objects.select_for_update().get(id=notification_id)
        result = notifier.send_with_fallbacks(notification)
    return result
