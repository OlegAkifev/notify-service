import pytest
from django.conf import settings
from django.core.mail.backends.locmem import EmailBackend

@pytest.fixture(autouse=True)
def _configure_test_settings(settings):
    """
    Общие настройки для тестов:
    - локальный email backend (письма в memory);
    - Celery — синхронно;
    - фолс для искусственного падения SMS (можно переопределить в конкретном тесте).
    """
    settings.EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"
    settings.DEFAULT_FROM_EMAIL = "test@example.com"

    # Celery синхронно, без брокера
    settings.CELERY_TASK_ALWAYS_EAGER = True

    # По умолчанию SMS не падает
    settings.SMS_FAIL_ALWAYS = False

    # Без реального телеграм токена по умолчанию
    settings.TELEGRAM_BOT_TOKEN = ""
    settings.TELEGRAM_DEFAULT_CHAT_ID = ""
    return settings
