import datetime as dt
from typing import List, Dict, Any
from django.utils import timezone
from django.contrib.auth.models import AbstractBaseUser

from ..choices import Channel, NotificationStatus, AttemptStatus
from ..models import Notification, NotificationAttempt, UserProfile
from .providers.email_provider import EmailProvider
from .providers.sms_provider import SmsProvider
from .providers.telegram_provider import TelegramProvider


# Сопоставление каналов с провайдерами
PROVIDERS = {
    Channel.EMAIL: EmailProvider(),
    Channel.SMS: SmsProvider(),
    Channel.TELEGRAM: TelegramProvider(),
}

class Notifier:
    """
    Класс-оркестратор: перебирает каналы по порядку, делает до N попыток на канал,
    при успехе — завершает уведомление.
    """
    MAX_TRIES_PER_CHANNEL = 3

    def _resolve_recipient(self, user: AbstractBaseUser, channel: str) -> str:
        """Возвращает адрес/номер/чат по каналу для данного пользователя."""
        profile: UserProfile | None = getattr(user, "profile", None)
        if channel == Channel.EMAIL:
            return user.email
        if channel == Channel.SMS:
            return profile.phone if profile else ""
        if channel == Channel.TELEGRAM:
            return profile.telegram_chat_id if profile else ""
        return ""

    def send_with_fallbacks(self, notification: Notification) -> Dict[str, Any]:
        """
        Основная логика фоллбэков.
        Возвращает итог: {'status': 'sent'|'failed', 'via': <channel|None>}
        """
        user = notification.user
        subject = notification.subject
        message = notification.message

        order: List[str] = notification.channels_order or []
        if not order:
            order = [Channel.EMAIL, Channel.SMS, Channel.TELEGRAM]

        for channel in order:
            provider = PROVIDERS.get(channel)
            if not provider:
                continue

            to = self._resolve_recipient(user, channel)
            # Несколько попыток на каждый канал
            for try_num in range(1, self.MAX_TRIES_PER_CHANNEL + 1):
                attempt = NotificationAttempt.objects.create(
                    notification=notification,
                    channel=channel,
                    try_number=try_num,
                    status=AttemptStatus.PENDING,
                )
                try:
                    ok, response = provider.send(to=to, subject=subject, message=message)
                    if ok:
                        attempt.status = AttemptStatus.SUCCESS
                        attempt.provider_response = response
                        attempt.finished_at = timezone.now()
                        attempt.save(update_fields=["status", "provider_response", "finished_at"])

                        notification.status = NotificationStatus.SENT
                        notification.sent_at = timezone.now()
                        notification.save(update_fields=["status", "sent_at"])

                        return {"status": NotificationStatus.SENT, "via": channel}
                    else:
                        attempt.status = AttemptStatus.FAILED
                        attempt.error = response or "Неизвестная ошибка"
                        attempt.finished_at = timezone.now()
                        attempt.save(update_fields=["status", "error", "finished_at"])
                except Exception as e:
                    # Логируем исключение как провал попытки
                    attempt.status = AttemptStatus.FAILED
                    attempt.error = str(e)
                    attempt.finished_at = timezone.now()
                    attempt.save(update_fields=["status", "error", "finished_at"])
                # если не удалось — цикл попробует ещё раз (до MAX_TRIES_PER_CHANNEL)
            # если все попытки по каналу исчерпаны — переходим к следующему каналу

        # Если все каналы провалены
        notification.status = NotificationStatus.FAILED
        notification.save(update_fields=["status"])
        return {"status": NotificationStatus.FAILED, "via": None}
