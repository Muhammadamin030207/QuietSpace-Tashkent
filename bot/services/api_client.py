"""QuietSpace bot — REST API client for backend. Bot never touches DB directly."""
import json
import logging

import httpx

logger = logging.getLogger(__name__)


class APIClient:
    def __init__(self, base_url: str, token_provider):
        self.base_url = base_url.rstrip("/")
        self._token_provider = token_provider
        self._client = httpx.AsyncClient(timeout=30)

    def _headers(self, auth: bool = True) -> dict:
        headers = {"Content-Type": "application/json"}
        if auth:
            token = self._token_provider()
            if token:
                headers["Authorization"] = f"Bearer {token}"
        return headers

    async def request(self, method: str, path: str, *, auth=True, **kwargs) -> httpx.Response:
        url = f"{self.base_url}/{path.lstrip('/')}"
        resp = await self._client.request(method, url, headers=self._headers(auth), **kwargs)
        if resp.status_code in (401, 403) and auth:
            logger.warning("Auth failed on %s (%s) — re-authenticating", path, resp.status_code)
            await self._token_provider(force=True)
            resp = await self._client.request(method, url, headers=self._headers(True), **kwargs)
        return resp

    async def telegram_login(self, telegram_id: int, username: str = "") -> dict:
        resp = await self.request(
            "POST", "api/auth/telegram-id/", auth=False,
            json={"telegram_id": telegram_id, "username": username},
        )
        resp.raise_for_status()
        data = resp.json()
        return {"access": data["access"], "refresh": data["refresh"], "user": data["user"]}

    async def nearby(self, lat: float, lng: float, radius_km: float = 5) -> list[dict]:
        resp = await self.request(
            "GET", "api/places/nearby/",
            params={"lat": lat, "lng": lng, "radius_km": radius_km, "page_size": 10},
        )
        resp.raise_for_status()
        return resp.json().get("results", [])

    async def search(self, params: dict) -> list[dict]:
        resp = await self.request("GET", "api/places/", params={**params, "page_size": 10})
        resp.raise_for_status()
        return resp.json().get("results", [])

    async def place_detail(self, place_id: int) -> dict:
        resp = await self.request("GET", f"api/places/{place_id}/")
        resp.raise_for_status()
        return resp.json()

    async def ai_chat(self, message: str, user_lat=None, user_lng=None, channel="bot") -> dict:
        payload = {"message": message, "channel": channel}
        if user_lat:
            payload["user_lat"] = user_lat
        if user_lng:
            payload["user_lng"] = user_lng
        resp = await self.request("POST", "api/ai/chat/", json=payload)
        resp.raise_for_status()
        return resp.json()

    async def ai_recommend(self, user_lat=None, user_lng=None) -> dict:
        payload = {}
        if user_lat:
            payload["user_lat"] = user_lat
        if user_lng:
            payload["user_lng"] = user_lng
        resp = await self.request("POST", "api/ai/recommend/", json=payload)
        resp.raise_for_status()
        return resp.json()

    async def report_occupancy(self, place_id: int, level: str) -> bool:
        resp = await self.request(
            "POST", f"api/places/{place_id}/occupancy/", json={"level": level}
        )
        return resp.status_code in (200, 201)

    async def add_favorite(self, place_id: int) -> bool:
        resp = await self.request("POST", "api/favorites/", json={"place_id": place_id})
        return resp.status_code == 201

    async def remove_favorite(self, place_id: int) -> bool:
        resp = await self.request("DELETE", f"api/favorites/{place_id}/")
        return resp.status_code == 204

    async def add_review(self, place_id: int, rating: int, text: str) -> dict:
        resp = await self.request(
            "POST", f"api/places/{place_id}/reviews/",
            json={"rating": rating, "text": text},
        )
        resp.raise_for_status()
        return resp.json()

    async def my_favorites(self) -> list[dict]:
        resp = await self.request("GET", "api/favorites/")
        resp.raise_for_status()
        return resp.json()

    async def ai_summary(self, place_id: int) -> dict:
        resp = await self.request("GET", f"api/places/{place_id}/ai-summary/")
        resp.raise_for_status()
        return resp.json()
