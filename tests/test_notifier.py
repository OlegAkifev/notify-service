import json
import pytest
from django.core import mail
from django.utils import timezone
from notifications.services.notifier import Notifier
from notifications.choices import Channel, NotificationStatus, AttemptStatus
from notifications.models import Notification, NotificationAttempt
from .factories import UserFactory, UserProfileFactory

@pytest.mark.django_db
def test_email_success_first_channel():
    """
    Если email доступен и backend OK — уведомление отправляется по email,
    статус SENT, попыток по другим каналам нет.
    """
    user = UserFactory(email="u@example.com")
    UserProfileFactory(user=user)  # телефон/телега тоже есть, но не понадобятся

    notif = Notification.objects.create(
        user=user,
        subject="Hello",
        message="World",
        channels_order=[Channel.EMAIL, Channel.SMS, Channel.TELEGRAM],
    )

    result = Notifier().send_with_fallbacks(notif)

    notif.refresh_from_db()
    assert result["status"] == NotificationStatus.SENT
    assert result["via"] == Channel.EMAIL
    assert notif.status == NotificationStatus.SENT
    assert len(mail.outbox) == 1  # письмо реально попало в locmem
    # Попытки: только по email, success
    attempts = list(NotificationAttempt.objects.filter(notification=notif))
    assert len(attempts) == 1
    assert attempts[0].channel == Channel.EMAIL
    assert attempts[0].status == AttemptStatus.SUCCESS

@pytest.mark.django_db
def test_email_empty_then_fallback_to_sms_success(settings):
    """
    Если email пустой -> первый канал фейлится,
    затем успешная доставка по SMS.
    """
    user = UserFactory(email="")
    profile = UserProfileFactory(user=user, phone="+10000000001")

    notif = Notification.objects.create(
        user=user,
        subject="Subj",
        message="Msg",
        channels_order=[Channel.EMAIL, Channel.SMS],
    )

    result = Notifier().send_with_fallbacks(notif)
    notif.refresh_from_db()

    assert result["status"] == NotificationStatus.SENT
    assert result["via"] == Channel.SMS
    # Должно быть минимум 1 неуспешная попытка по email и 1 успешная по sms
    attempts = list(NotificationAttempt.objects.filter(notification=notif).order_by("id"))
    assert attempts[0].channel == Channel.EMAIL and attempts[0].status == AttemptStatus.FAILED
    assert any(a.channel == Channel.SMS and a.status == AttemptStatus.SUCCESS for a in attempts)

@pytest.mark.django_db
def test_sms_forced_fail_then_telegram_missing_token_fails_all(settings):
    """
    Включаем принудительный фейл SMS и не задаём токен телеги —
    все каналы проваливаются, уведомление FAILED.
    """
    settings.SMS_FAIL_ALWAYS = True
    settings.TELEGRAM_BOT_TOKEN = ""  # гарантируем провал телеги

    user = UserFactory(email="")  # email пустой -> email сразу провал
    profile = UserProfileFactory(user=user, phone="+10000000002", telegram_chat_id="12345")

    notif = Notification.objects.create(
        user=user,
        subject="S",
        message="M",
        channels_order=[Channel.EMAIL, Channel.SMS, Channel.TELEGRAM],
    )

    result = Notifier().send_with_fallbacks(notif)
    notif.refresh_from_db()

    assert result["status"] == NotificationStatus.FAILED
    assert result["via"] is None
    attempts = NotificationAttempt.objects.filter(notification=notif)
    # Будет до 3 попыток на каждый канал
    assert attempts.filter(channel=Channel.EMAIL).exists()
    assert attempts.filter(channel=Channel.SMS).exists()
    assert attempts.filter(channel=Channel.TELEGRAM).exists()
    assert all(a.status == AttemptStatus.FAILED for a in attempts)

@pytest.mark.django_db
def test_max_tries_per_channel_respected(monkeypatch):
    """
    Проверяем, что при ошибках по каналу делается не более MAX_TRIES_PER_CHANNEL попыток,
    после чего переходим к следующему каналу.
    """
    user = UserFactory(email="broken@example.com")
    UserProfileFactory(user=user, phone="")  # чтобы SMS не отвлекало в этом тесте

    notif = Notification.objects.create(
        user=user,
        subject="X",
        message="Y",
        channels_order=[Channel.EMAIL],  # только один канал
    )

    # Ломаем email-провайдер: send всегда False
    from notifications.services.providers.email_provider import EmailProvider
    def fake_send(*, to, subject, message):
        return False, "forced fail"

    monkeypatch.setattr(EmailProvider, "send", lambda self, **kw: fake_send(**kw))

    n = Notifier()
    result = n.send_with_fallbacks(notif)
    notif.refresh_from_db()

    assert result["status"] == NotificationStatus.FAILED
    attempts = NotificationAttempt.objects.filter(notification=notif, channel=Channel.EMAIL)
    assert attempts.count() == n.MAX_TRIES_PER_CHANNEL
