from django.urls import path
from .views import create_notification

urlpatterns = [
    path("notify/", create_notification, name="create_notification"),
]
