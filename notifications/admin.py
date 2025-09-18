from django.contrib import admin
from .models import Notification, NotificationAttempt, UserProfile

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "status", "created_at", "sent_at")
    search_fields = ("user__username", "subject", "message")
    list_filter = ("status",)

@admin.register(NotificationAttempt)
class NotificationAttemptAdmin(admin.ModelAdmin):
    list_display = ("id", "notification", "channel", "try_number", "status", "started_at", "finished_at")
    list_filter = ("channel", "status")

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "phone", "telegram_chat_id")
