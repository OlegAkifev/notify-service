from typing import Tuple
from django.core.mail import send_mail
from django.conf import settings
from .base import BaseProvider

class EmailProvider(BaseProvider):
    """
    Отправка письма через стандартный SMTP бэкенд Django.
    """
    def send(self, *, to: str, subject: str, message: str) -> Tuple[bool, str]:
        # Если email не указан — считаем как ошибка
        if not to:
            return False, "Пустой email получателя"
        # Django вернёт число успешно отправленных писем
        sent = send_mail(
            subject=subject or "(без темы)",
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[to],
            fail_silently=False,  # хотим видеть исключения
        )
        return (sent > 0), f"send_mail_sent={sent}"
