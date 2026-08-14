"""Send Telegram messages directly from backend via Bot API."""
import logging

from django.conf import settings

import httpx

logger = logging.getLogger(__name__)

BOT_API = f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}"


def send_message(telegram_id: int, text: str, **kwargs) -> bool:
    if not settings.TELEGRAM_BOT_TOKEN:
        logger.warning("TELEGRAM_BOT_TOKEN not set, skip push")
        return False
    try:
        resp = httpx.post(
            f"{BOT_API}/sendMessage",
            json={"chat_id": telegram_id, "text": text, **kwargs},
            timeout=10,
        )
        resp.raise_for_status()
        return True
    except Exception as exc:  # noqa: BLE001
        logger.error("Telegram push failed for %s: %s", telegram_id, exc)
        return False
