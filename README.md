# 🚀 Сервис уведомлений (Email → SMS → Telegram)

[![Python](https://img.shields.io/badge/Python-3.12-blue)]()
[![Django](https://img.shields.io/badge/Django-5.x-0C4B33)]()
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-336791)]()
[![Celery](https://img.shields.io/badge/Celery-5.x-37814A)]()
[![Redis](https://img.shields.io/badge/Redis-7-D82C20)]()
[![Docker Compose](https://img.shields.io/badge/Docker-Compose-2496ED)]()
[![Tests](https://img.shields.io/badge/pytest-passing-brightgreen)]()

Надёжная доставка уведомлений по нескольким каналам с фоллбэком: если текущий канал не сработал — пробуем следующий. Отправка асинхронная через Celery, все попытки логируются.

---

## 📚 Содержание

- [Возможности](#-возможности)
- [Архитектура](#-архитектура)
- [Стек](#-стек)
- [Структура проекта](#-структура-проекта)
- [Быстрый старт](#-быстрый-старт)
- [Переменные окружения](#-переменные-окружения-env)
- [API](#-api)
- [Примеры cURL и ответы](#-примеры-curl-и-ответы)
- [Тесты](#-тесты)
- [Траблшутинг](#-траблшутинг)
- [Лицензия](#-лицензия)

---

## ✅ Возможности

- API для постановки уведомления в очередь.
- Порядок каналов на запрос: `["email", "sms", "telegram"]`.
- До **3 попыток** на каждый канал; при неудаче — фоллбэк на следующий.
- Логирование всех попыток: канал, попытка, статус, ошибка, ответ провайдера, таймстемпы.
- Провайдеры каналов — отдельные классы (легко заменить на реальных).

---

## 🧩 Архитектура

```mermaid
flowchart LR
    A[HTTP POST /api/notify/] --> B[Create Notification (DB)]
    B --> C[Celery Task send_notification_task]
    C --> D{Email OK?}
    D -- Да --> E[Status: sent]
    D -- Нет --> F{SMS OK?}
    F -- Да --> E
    F -- Нет --> G{Telegram OK?}
    G -- Да --> E
    G -- Нет --> H[Status: failed]
    C -.-> I[(NotificationAttempt записи)]


🛠 Стек

Python 3.12 · Django 5 · PostgreSQL 16 · Celery 5 · Redis 7 · Docker · Docker Compose · Gunicorn · pytest


⚡ Быстрый старт

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


Админка: http://localhost:8000/admin/

📡 API
POST /api/notify/ — поставить уведомление в очередь

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

🧪 Примеры cURL и ответы

    1) Успешная постановка в очередь

        curl -X POST http://localhost:8000/api/notify/ \
            -H "Content-Type: application/json" \
            -d '{
                    "user_id": 1,
                    "subject": "Привет!",
                    "message": "Тестовое уведомление",
                    "channels": ["email", "sms", "telegram"]
                }'
    
        Ответ (200):
            { "id": 12, "status": "pending", "created_at": "2025-09-18T22:45:13.123456+00:00" }

🧫 Тесты

    docker compose exec web pytest -vv