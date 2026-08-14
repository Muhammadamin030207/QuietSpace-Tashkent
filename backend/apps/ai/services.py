"""AI business logic: chat assistant with tool-use, personalized recommendations."""
import logging

from django.contrib.gis.geos import Point
from django.core.cache import cache

from apps.places.models import Favorite, Place

from .client import cached_or_run, parse_ai_json, run_tool_loop
from .models import AIConversation
from .tools import SEARCH_PLACES_TOOL, execute_search_places

logger = logging.getLogger(__name__)

MAX_HISTORY_MESSAGES = 40


def _system_prompt(language: str) -> str:
    return (
        "Sen — QuietSpace Tashkent yordamchisisiz. Bu platforma Toshkentdagi tinch, "
        "ishlash uchun qulay joylarni (kafelar, kutubxonalar, kovorkinglar, bepul zonalar) "
        "topish uchun mo'ljallangan.\n"
        f"JAVOB TILI: Foydalanuvchi bilan {language} tilida ('reply' maydonida) suhbatlash.\n"
        "QOIDALAR:\n"
        "1. Har doim search_places tool orqali haqiqiy ma'lumot ol. Hech qachon joy nomlarini "
        "o'zingdan to'qima — ular bazada yo'q bo'lishi mumkin.\n"
        "2. Tool chaqirish natijasi bo'lmagan savollarga (masalan salomlashuv) tool ishlatmasdan "
        "javob berishing mumkin.\n"
        "3. Javobing oxirida FAQAT JSON formatida: "
        '{"reply": "...", "place_ids": [1,2,3]}. reply — foydalanuvchiga ko\'rsatiladigan matn. '
        "Agar joylar tavsiya qilinsa, ularning nomlari va qisqa sabablarni reply ichida keltir.\n"
        "4. reply ichida Markdown ishlatma: **qalin** va emoji ruxsat.\n"
        "5. Agar hech qanday joy topilmasa, place_ids bo'sh bo'lsin va reply da sababini tushuntir."
    )


def _conversation_messages(conversation: AIConversation) -> list[dict]:
    return conversation.messages or []


def chat(user, message: str, conversation_id: str | None, user_lat, user_lng, channel="web") -> dict:
    user_point = None
    if user_lat and user_lng:
        try:
            user_point = Point(float(user_lng), float(user_lat), srid=4326)
        except (TypeError, ValueError):
            user_point = None

    if conversation_id:
        conversation = AIConversation.objects.filter(
            id=conversation_id, user=user
        ).first()
    else:
        conversation = None

    if conversation is None:
        conversation = AIConversation.objects.create(user=user, channel=channel)

    messages = _conversation_messages(conversation) + [
        {"role": "user", "content": message}
    ]

    def producer():
        final_text = run_tool_loop(
            messages=messages,
            system=_system_prompt(user.language),
            tools=[SEARCH_PLACES_TOOL],
            tool_executor=lambda name, params: (
                execute_search_places(params, user_point) if name == "search_places" else []
            ),
        )
        parsed = parse_ai_json(final_text)
        if parsed is None:
            # retry once with stricter instruction
            final_text = run_tool_loop(
                messages=messages + [
                    {
                        "role": "assistant",
                        "content": final_text,
                    },
                    {
                        "role": "user",
                        "content": (
                            "Iltimos, faqat JSON qaytar: "
                            '{"reply": "...", "place_ids": [...]}. Boshqa hech narsa yozma.'
                        ),
                    },
                ],
                system=_system_prompt(user.language) + "\nFAQAT JSON QAYTAR.",
                tools=[SEARCH_PLACES_TOOL],
                tool_executor=lambda name, params: (
                    execute_search_places(params, user_point) if name == "search_places" else []
                ),
            )
            parsed = parse_ai_json(final_text)
        return parsed or {"reply": final_text, "place_ids": []}

    cache_key = f"ai_chat:{user.id}:{hash(message)}:{user_lat}:{user_lng}"
    result = cached_or_run(cache_key, producer)

    conversation.add_message("user", message)
    conversation.add_message(
        "assistant", json_dump(result)
    )

    return _enrich_with_places(result, user)


def json_dump(obj) -> str:
    import json

    return json.dumps(obj, ensure_ascii=False)


def _enrich_with_places(result: dict, user) -> dict:
    place_ids = result.get("place_ids") or []
    places = Place.objects.select_related("category").prefetch_related("photos").filter(
        id__in=place_ids[:10]
    )
    place_map = {p.id: p for p in places}
    ordered = [place_map[i] for i in place_ids if i in place_map]
    favorites = set(
        Favorite.objects.filter(user=user, place_id__in=[p.id for p in ordered]).values_list(
            "place_id", flat=True
        )
    )
    return {
        "reply": result.get("reply", ""),
        "place_ids": [p.id for p in ordered],
        "places": [
            {
                "id": p.id,
                "name": p.name,
                "category": p.category.key,
                "district": p.district,
                "address": p.address,
                "wifi": p.wifi_speed,
                "noise": p.noise_level,
                "outlets": p.outlets_level,
                "price": p.price_level,
                "rating": float(p.avg_rating),
                "is_favorite": p.id in favorites,
                "photo": (
                    request_absolute_photo(p) 
                ),
            }
            for p in ordered
        ],
        "conversation_id": None,
    }


def request_absolute_photo(place) -> str | None:
    from django.conf import settings

    photo = place.photos.first()
    if not photo:
        return None
    return f"{settings.BACKEND_BASE_URL}{photo.image.url}"


def recommend(user, user_lat, user_lng, limit=5) -> dict:
    """Personalized recommendations from user's last 20 reviews/favorites + location."""
    from apps.reviews.models import Review

    user_point = None
    if user_lat and user_lng:
        try:
            user_point = Point(float(user_lng), float(user_lat), srid=4326)
        except (TypeError, ValueError):
            pass

    reviews = list(
        Review.objects.filter(user=user)
        .select_related("place__category")
        .order_by("-created_at")[:20]
    )
    favorites = list(
        Favorite.objects.filter(user=user)
        .select_related("place__category")
        .order_by("-created_at")[:20]
    )

    context_lines = ["Foydalanuvchi profili (o'tmishdagi faollik):"]
    for r in reviews:
        context_lines.append(
            f"- sharh: {r.place.name} ({r.place.category.key}), reyting {r.rating}/5, "
            f"wifi={r.place.wifi_speed}, shovqin={r.place.noise_level}"
        )
    for f in favorites:
        context_lines.append(f"- sevimli: {f.place.name} ({f.place.category.key})")
    if user_point is not None:
        context_lines.append(
            f"- foydalanuvchi joylashuvi: lat={user_lat}, lng={user_lng}"
        )

    system = (
        "Sen — QuietSpace Tashkent shaxsiy tavsiya tizimisisan.\n"
        "Foydalanuvchi profiliga qarab 3-5 ta joy tavsiya qil.\n"
        "search_places tool orqali haqiqiy joylarni qidir, nom to'qima.\n"
        "Faqat JSON qaytar: "
        '{"places": [{"id": 1, "reason": "Chunki siz odatda jim va Wi-Fi tez joylarni tanlaysiz"}]}'
    )
    messages = [{"role": "user", "content": "\n".join(context_lines)}]

    final_text = run_tool_loop(
        messages=messages,
        system=system,
        tools=[SEARCH_PLACES_TOOL],
        tool_executor=lambda name, params: (
            execute_search_places(params, user_point) if name == "search_places" else []
        ),
    )
    parsed = parse_ai_json(final_text) or {"places": []}

    items = parsed.get("places", [])[:limit]
    ids = [i.get("id") for i in items if i.get("id")]
    places = {
        p.id: p
        for p in Place.objects.select_related("category")
        .prefetch_related("photos")
        .filter(id__in=ids)
    }
    result = []
    for item in items:
        place = places.get(item.get("id"))
        if place is None:
            continue
        result.append(
            {
                "id": place.id,
                "name": place.name,
                "category": place.category.key,
                "district": place.district,
                "address": place.address,
                "rating": float(place.avg_rating),
                "photo": request_absolute_photo(place),
                "reason": item.get("reason", ""),
            }
        )
    return {"places": result}