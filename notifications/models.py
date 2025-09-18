from django.conf import settings
from django.db import models
from .choices import Channel, AttemptStatus, NotificationStatus

# Профиль для хранения контактов
class UserProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="profile")
    phone = models.CharField("Телефон для SMS", max_length=32, blank=True, default="")
    telegram_chat_id = models.CharField("Telegram chat_id", max_length=64, blank=True, default="")

    def __str__(self):
        return f"Profile({self.user_id})"

class Notification(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    subject = models.CharField("Тема", max_length=255, blank=True, default="")
    message = models.TextField("Сообщение")
    # Порядок каналов, например ["email", "sms", "telegram"]
    channels_order = models.JSONField("Порядок каналов", default=list)
    status = models.CharField(max_length=16, choices=NotificationStatus.choices, default=NotificationStatus.PENDING)
    created_at = models.DateTimeField(auto_now_add=True)
    sent_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Notification<{self.id}> to {self.user_id} [{self.status}]"

class NotificationAttempt(models.Model):
    notification = models.ForeignKey(Notification, on_delete=models.CASCADE, related_name="attempts")
    channel = models.CharField(max_length=16, choices=Channel.choices)
    try_number = models.PositiveIntegerField(default=1)
    status = models.CharField(max_length=16, choices=AttemptStatus.choices, default=AttemptStatus.PENDING)
    error = models.TextField(blank=True, default="")
    provider_response = models.TextField(blank=True, default="")
    started_at = models.DateTimeField(auto_now_add=True)
    finished_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        indexes = [
            models.Index(fields=["notification", "channel"]),
        ]

    def __str__(self):
        return f"Attempt n={self.try_number} {self.channel} [{self.status}]"
