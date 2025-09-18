from django.db.models import TextChoices

class Channel(TextChoices):
    EMAIL = "email", "Email"
    SMS = "sms", "SMS"
    TELEGRAM = "telegram", "Telegram"

class AttemptStatus(TextChoices):
    PENDING = "pending", "В обработке"
    SUCCESS = "success", "Успешно"
    FAILED = "failed", "Ошибка"

class NotificationStatus(TextChoices):
    PENDING = "pending", "В очереди"
    SENT = "sent", "Отправлено"
    FAILED = "failed", "Не доставлено"
