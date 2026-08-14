"""JWT storage per telegram_id in Redis (with optional TTL)."""
import json
import logging

import redis.asyncio as aioredis

logger = logging.getLogger(__name__)

TOKEN_KEY = "qs:tg:{telegram_id}:token"


class TokenStore:
    def __init__(self, redis_url: str):
        self._redis = aioredis.from_url(redis_url, decode_responses=True)

    def _key(self, telegram_id: int) -> str:
        return TOKEN_KEY.format(telegram_id=telegram_id)

    async def save(self, telegram_id: int, tokens: dict):
        await self._redis.set(self._key(telegram_id), json.dumps(tokens), ex=30 * 24 * 3600)

    async def load(self, telegram_id: int) -> dict | None:
        raw = await self._redis.get(self._key(telegram_id))
        if raw:
            try:
                return json.loads(raw)
            except json.JSONDecodeError:
                return None
        return None
