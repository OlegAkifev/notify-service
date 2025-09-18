import os
from celery import Celery

# Указываем модуль настроек Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "project.settings")

app = Celery("project")

# Читаем настройки из Django с префиксом CELERY_
app.config_from_object("django.conf:settings", namespace="CELERY")

# Автоматически находим задачи во всех приложениях
app.autodiscover_tasks()
