"""Bot-wide context: shared APIClient, TokenStore and per-user session access."""
import logging

from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from config import BACKEND_BASE_URL, REDIS_URL
from services.api_client import APIClient
from services.state import TokenStore

logger = logging.getLogger(__name__)

api = APIClient(BACKEND_BASE_URL, token_provider=None)
token_store = TokenStore(REDIS_URL)


def get_telegram_id(update) -> int:
    user = getattr(update, "from_user", None)
    return user.id if user else None


async def ensure_logged_in(update) -> tuple[int, dict] | None:
    """Make sure the user has a JWT; login via backend if missing."""
    tg_id = get_telegram_id(update)
    if not tg_id:
        return None
    tokens = await token_store.load(tg_id)
    if tokens and tokens.get("access"):
        return tg_id, tokens

    from_user = getattr(update, "from_user", None)
    username = from_user.username or "" if from_user else ""
    try:
        result = await api.telegram_login(tg_id, username)
    except Exception as exc:  # noqa: BLE001
        logger.error("Telegram login failed: %s", exc)
        return None
    await token_store.save(tg_id, result)
    return tg_id, result


class Session:
    """Holds user state (telegram_id, jwt) and exposes an authed APIClient."""

    def __init__(self, telegram_id: int, tokens: dict):
        self.telegram_id = telegram_id
        self.tokens = tokens

    def _get_token(self, force=False):
        if force:
            return None
        return self.tokens.get("access")

    @property
    def user(self) -> dict:
        return self.tokens.get("user", {})

    @property
    def client(self) -> APIClient:
        client = APIClient(BACKEND_BASE_URL, token_provider=self._get_token)
        client._token_provider = self._get_token
        return client


async def get_session(update) -> Session | None:
    resolved = await ensure_logged_in(update)
    if not resolved:
        return None
    tg_id, tokens = resolved
    return Session(tg_id, tokens)


async def store_user_location(state: FSMContext, message: Message):
    if message.location:
        await state.update_data(
            user_lat=message.location.latitude,
            user_lng=message.location.longitude,
        )