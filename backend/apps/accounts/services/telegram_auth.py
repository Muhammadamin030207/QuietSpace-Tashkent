"""Telegram initData validation via HMAC-SHA256 (official scheme)."""
import hashlib
import hmac
import json
from urllib.parse import parse_qsl

from django.conf import settings

TELEGRAM_BOT_TOKEN = settings.TELEGRAM_BOT_TOKEN


def _extract_init_data(raw_init_data: str) -> dict:
    pairs = parse_qsl(raw_init_data, keep_blank_values=True)
    return {k: v for k, v in pairs}


def validate_init_data(raw_init_data: str) -> dict | None:
    """Returns parsed user dict from initData, or None if invalid.

    Supports both 'user=...&auth_date=...&hash=...' raw string and already
    JSON-parsed initData ({'user': '{"id":123,...}', 'hash': '...'}).
    """
    if not TELEGRAM_BOT_TOKEN:
        return None
    data = raw_init_data
    if isinstance(data, str):
        try:
            data = json.loads(data)
        except (json.JSONDecodeError, TypeError):
            try:
                data = _extract_init_data(data)
            except Exception:
                return None
    if not isinstance(data, dict):
        return None
    received_hash = data.get("hash")
    if not received_hash:
        return None
    data_check_string = "\n".join(
        f"{k}={v}" for k, v in sorted(data.items()) if k != "hash"
    )
    secret_key = hmac.new(
        b"WebAppData", TELEGRAM_BOT_TOKEN.encode(), hashlib.sha256
    ).digest()
    computed = hmac.new(secret_key, data_check_string.encode(), hashlib.sha256).hexdigest()
    if computed != received_hash:
        return None
    try:
        user = json.loads(data.get("user", "{}"))
    except json.JSONDecodeError:
        return None
    return user or None


def telegram_user_to_username(user: dict) -> str:
    first = user.get("first_name") or ""
    last = user.get("last_name") or ""
    username = user.get("username") or ""
    return f"tg_{user.get('id')}" if username == "" else username
