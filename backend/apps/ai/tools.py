"""search_places tool definition + PostGIS-backed executor."""

from django.contrib.gis.db.models.functions import Distance
from django.contrib.gis.geos import Point
from django.contrib.gis.measure import D

from apps.places.models import Place

SEARCH_PLACES_TOOL = {
    "name": "search_places",
    "description": (
        "Toshkentdagi tinch ish joylarini filtrlar bo'yicha qidiradi. "
        "Har doim ushbu tool orqali haqiqiy ma'lumot ol — joy nomlarini xotiradan to'qima."
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "category": {
                "type": "string",
                "enum": ["cafe", "library", "coworking", "free_zone"],
            },
            "max_noise": {
                "type": "string",
                "enum": ["very_quiet", "quiet", "moderate", "noisy"],
                "description": "Maksimal shovqin darajasi. very_quiet eng tinch.",
            },
            "min_wifi": {
                "type": "string",
                "enum": ["none", "slow", "medium", "fast"],
                "description": "Minimal Wi-Fi tezligi.",
            },
            "requires_outlets": {
                "type": "boolean",
                "description": "Rozetka kerakmi. true bo'lsa few yoki every_table.",
            },
            "max_price": {
                "type": "string",
                "enum": ["free", "$", "$$", "$$$"],
                "description": "Maksimal narx darajasi.",
            },
            "max_distance_km": {
                "type": "number",
                "description": "Maksimal masofa (km). Berilmasa 5 km.",
            },
            "district": {
                "type": "string",
                "description": "Tuman nomi, masalan 'Chilonzor'.",
            },
        },
    },
}


def execute_search_places(params: dict, user_point=None) -> list[dict]:
    """Run the actual PostGIS query for the tool call."""
    qs = Place.objects.select_related("category").prefetch_related("photos")

    category = params.get("category")
    if category:
        qs = qs.filter(category__key=category)

    max_noise = params.get("max_noise")
    if max_noise:
        order = {"very_quiet": 0, "quiet": 1, "moderate": 2, "noisy": 3}
        allowed = [k for k, v in order.items() if v <= order[max_noise]]
        qs = qs.filter(noise_level__in=allowed)

    min_wifi = params.get("min_wifi")
    if min_wifi:
        order = {"none": 0, "slow": 1, "medium": 2, "fast": 3}
        allowed = [k for k, v in order.items() if v >= order[min_wifi]]
        qs = qs.filter(wifi_speed__in=allowed)

    if params.get("requires_outlets"):
        qs = qs.filter(outlets_level__in=["few", "every_table"])

    max_price = params.get("max_price")
    if max_price:
        order = {"free": 0, "$": 1, "$$": 2, "$$$": 3}
        allowed = [k for k, v in order.items() if v <= order[max_price]]
        qs = qs.filter(price_level__in=allowed)

    district = params.get("district")
    if district:
        qs = qs.filter(district__iexact=district)

    if user_point is not None:
        radius_km = min(float(params.get("max_distance_km") or 5), 50)
        qs = qs.filter(location__distance_lte=(user_point, D(km=radius_km)))
        qs = qs.annotate(distance=Distance("location", user_point)).order_by("distance")
        qs = qs[:10]
    else:
        qs = qs[:10]

    results = []
    for place in qs:
        photo = place.photos.first()
        distance = getattr(place, "distance", None)
        results.append(
            {
                "id": place.id,
                "name": place.name,
                "category": place.category.key,
                "district": place.district,
                "address": place.address,
                "wifi": place.wifi_speed,
                "noise": place.noise_level,
                "outlets": place.outlets_level,
                "price": place.price_level,
                "rating": float(place.avg_rating),
                "distance_km": round(distance.km, 2) if distance else None,
                "verified": place.is_verified,
            }
        )
    return results