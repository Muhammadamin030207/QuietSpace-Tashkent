from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    class Role(models.TextChoices):
        GUEST = "guest", "guest"
        USER = "user", "user"
        OWNER = "owner", "owner"
        MODERATOR = "moderator", "moderator"
        ADMIN = "admin", "admin"

    class Language(models.TextChoices):
        UZ = "uz", "uz"
        RU = "ru", "ru"
        EN = "en", "en"

    phone = models.CharField(max_length=20, blank=True, null=True, unique=True)
    telegram_id = models.BigIntegerField(unique=True, null=True, blank=True)
    telegram_username = models.CharField(max_length=64, blank=True)
    language = models.CharField(
        max_length=2, choices=Language.choices, default=Language.UZ
    )
    role = models.CharField(
        max_length=20, choices=Role.choices, default=Role.USER
    )

    def __str__(self):
        return self.username or f"user_{self.id}"