Сервис уведомлений (Email → SMS → Telegram)

Стек: Python 3.12 · Django 5 · PostgreSQL 16 · Celery 5 · Redis 7 · Docker · Docker Compose · Gunicorn · pytest

Надёжная доставка уведомлений по нескольким каналам с фоллбэком: если текущий канал не сработал — пробуем следующий. Отправка асинхронная через Celery, все попытки логируются.

Возможности

    API для постановки уведомления в очередь.

    Порядок каналов на запрос: ["email", "sms", "telegram"].

    До 3 попыток на каждый канал, затем фоллбэк на следующий.

    Логирование всех попыток: канал, попытка, статус, ошибка, ответ провайдера.

    Провайдеры каналов как отдельные классы (легко заменить на реальных).

Быстрый старт

# 1) Скопируй конфиг окружения
cp .env.example .env

# 2) Подними окружение
docker compose up --build

# 3) Создай миграции (один раз, если файлов миграций ещё нет)
docker compose exec web python manage.py makemigrations notifications

# 4) Применяй миграции
docker compose exec web python manage.py migrate

# 5) Создай суперпользователя (по желанию для админки)
docker compose exec web python manage.py createsuperuser

Открой админку: http://localhost:8000/admin/

API

POST /api/notify/

Ставит уведомление в очередь на отправку.

Body (JSON):

    {
    "user_id": 1,
    "subject": "Привет!",
    "message": "Тестовое уведомление",
    "channels": ["email", "sms", "telegram"]
    }
user_id — обязателен (пользователь должен существовать).

message — обязателен.

channels — опционально, по умолчанию ["email", "sms", "telegram"].

Response (200):

    {
    "id": 10,
    "status": "pending",
    "created_at": "2025-09-18T22:45:13.123456+00:00"
    }

Дальше Celery-воркер обработает уведомление, записи о попытках будут в notifications_notificationattempt, итоговый статус — в notifications_notification.
Пример curl:

    curl -X POST http://localhost:8000/api/notify/ \
    -H "Content-Type: application/json" \
    -d '{
            "user_id": 1,
            "subject": "Привет!",
            "message": "Тестовое уведомление",
            "channels": ["email", "sms", "telegram"]
        }'

Модель данных

    Notification — само уведомление, статус pending/sent/failed, порядок каналов.
    NotificationAttempt — отдельная попытка: канал, номер попытки, статус, ошибка, ответ провайдера, таймстемпы.
    UserProfile — контакты пользователя: phone, telegram_chat_id.
    Email берётся из User.email.

Провайдеры каналов

    Email — стандартный django.core.mail (SMTP).
    SMS — заглушка (можно принудительно «ронять» через SMS_FAIL_ALWAYS=TRUE).
    Для реального провайдера (Twilio/Nexmo/SMS Aero) — замените код в sms_provider.py.
    Telegram — Bot API (TELEGRAM_BOT_TOKEN обязателен, у пользователя должен быть telegram_chat_id).

Для запуска тестов 

    docker compose exec web pytest -vv