from django.contrib.auth import get_user_model

User = get_user_model()


def get_or_create_telegram_user(tg_user: dict) -> User:
    """Create or fetch a user from Telegram user payload."""
    tg_id = int(tg_user.get("id"))
    username = tg_user.get("username") or ""
    user, created = User.objects.get_or_create(
        telegram_id=tg_id,
        defaults={
            "username": f"tg_{tg_id}",
            "telegram_username": username,
            "first_name": tg_user.get("first_name") or "",
            "last_name": tg_user.get("last_name") or "",
            "language": tg_user.get("language_code") or "uz",
        },
    )
    if not created:
        changed = False
        if tg_user.get("first_name"):
            user.first_name = tg_user.get("first_name")
            changed = True
        if username and user.telegram_username != username:
            user.telegram_username = username
            changed = True
        if changed:
            user.save(update_fields=["first_name", "telegram_username"])
    return user
