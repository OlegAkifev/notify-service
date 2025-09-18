import json
import pytest
from django.urls import reverse
from notifications.models import Notification
from .factories import UserFactory, UserProfileFactory

@pytest.mark.django_db
def test_create_notification_endpoint(client):
    user = UserFactory()
    UserProfileFactory(user=user)

    url = "/api/notify/"
    payload = {
        "user_id": user.id,
        "subject": "Привет",
        "message": "Тест",
        "channels": ["email", "sms", "telegram"],
    }
    resp = client.post(url, data=json.dumps(payload), content_type="application/json")
    assert resp.status_code == 200
    data = resp.json()
    assert "id" in data
    notif = Notification.objects.get(id=data["id"])
    assert notif.message == "Тест"
    assert notif.channels_order == ["email", "sms", "telegram"]

@pytest.mark.django_db
def test_create_notification_validation(client):
    url = "/api/notify/"
    resp = client.post(url, data=json.dumps({}), content_type="application/json")
    assert resp.status_code == 400
    assert "detail" in resp.json()
