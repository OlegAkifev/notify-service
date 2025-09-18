import requests
from typing import Tuple
from django.conf import settings
from .base import BaseProvider

class TelegramProvider(BaseProvider):
    """
    Простейшая отправка в Telegram через Bot API.
    Нужен токен бота, а получателю нужен chat_id.
    """
    def send(self, *, to: str, subject: str, message: str) -> Tuple[bool, str]:
        token = settings.TELEGRAM_BOT_TOKEN
        if not token:
            return False, "Не задан TELEGRAM_BOT_TOKEN"
        chat_id = to or settings.TELEGRAM_DEFAULT_CHAT_ID
        if not chat_id:
            return False, "Пустой telegram chat_id"

        text = f"*{subject or 'Уведомление'}*\n{message}"
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        payload = {"chat_id": chat_id, "text": text, "parse_mode": "Markdown"}
        resp = requests.post(url, json=payload, timeout=10)
        ok = resp.ok and resp.json().get("ok", False)
        return ok, resp.text
