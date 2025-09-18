import os
from typing import Tuple
from .base import BaseProvider
from django.conf import settings

class SmsProvider(BaseProvider):
    """
    Пример заглушки: имитирует отправку SMS.
    Для реального провайдера (Twilio, Nexmo и т.п.) здесь будет API-запрос.
    """
    def send(self, *, to: str, subject: str, message: str) -> Tuple[bool, str]:
        if not to:
            return False, "Пустой номер телефона"
        # Флаг из настроек: принудительно падать (для демонстрации фоллбэка)
        if settings.SMS_FAIL_ALWAYS:
            return False, "Искусственная ошибка SMS"
        # Иначе считаем, что доставлено
        # Здесь мог бы быть реальный HTTP-запрос к SMS-провайдеру
        return True, f"SMS отправлено на {to}"
