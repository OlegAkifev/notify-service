import json
from django.http import JsonResponse, HttpRequest
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import get_user_model
from django.utils.timezone import now

from .models import Notification
from .tasks import send_notification_task
from .choices import Channel

User = get_user_model()

@csrf_exempt
def create_notification(request: HttpRequest):
    """
    Простейший JSON-эндпоинт:
    POST /api/notify/
    {
      "user_id": 1,
      "subject": "Тема",
      "message": "Текст",
      "channels": ["email","sms","telegram"]  # опционально
    }
    """
    if request.method != "POST":
        return JsonResponse({"detail": "Метод не поддерживается"}, status=405)

    try:
        payload = json.loads(request.body or "{}")
    except json.JSONDecodeError:
        return JsonResponse({"detail": "Некорректный JSON"}, status=400)

    user_id = payload.get("user_id")
    subject = payload.get("subject", "")
    message = payload.get("message", "")
    channels = payload.get("channels") or [Channel.EMAIL, Channel.SMS, Channel.TELEGRAM]

    if not user_id or not message:
        return JsonResponse({"detail": "user_id и message обязательны"}, status=400)

    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return JsonResponse({"detail": "Пользователь не найден"}, status=404)

    notif = Notification.objects.create(
        user=user,
        subject=subject,
        message=message,
        channels_order=channels,
    )

    # Кидаем задачу в Celery
    send_notification_task.delay(notif.id)

    return JsonResponse({"id": notif.id, "status": notif.status, "created_at": now().isoformat()})
