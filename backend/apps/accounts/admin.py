from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ("id", "username", "phone", "telegram_id", "role", "language")
    list_filter = ("role", "language")
    fieldsets = UserAdmin.fieldsets + (
        ("QuietSpace", {"fields": ("phone", "telegram_id", "telegram_username", "language", "role")}),
    )
