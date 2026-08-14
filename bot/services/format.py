"""Common text/format helpers for place cards."""
CATEGORY_ICON = {
    "cafe": "☕", "library": "📚", "coworking": "💼", "free_zone": "🆓",
}
NOISE_LABEL = {
    "very_quiet": "🤫 juda tinch", "quiet": "😌 tinch",
    "moderate": "🎵 o'rtacha", "noisy": "📢 shovqinli",
}
WIFI_LABEL = {
    "none": "🚫 yo'q", "slow": "🐢 sekin",
    "medium": "🫡 o'rtacha", "fast": "⚡ tez",
}
OUTLET_LABEL = {
    "none": "🚫 yo'q", "few": "🔌 kam", "every_table": "🔌 har stolda",
}
PRICE_LABEL = {
    "free": "🆓 Bepul", "$": "$", "$$": "$$", "$$$": "$$$",
}
OCCUPANCY_LABEL = {
    "empty": "🟢 Bo'sh", "medium": "🟡 O'rtacha", "full": "🔴 To'la",
}


def fmt_rating(rating):
    try:
        return f"{float(rating):.1f}"
    except (TypeError, ValueError):
        return "—"


def place_card_text(place: dict) -> str:
    lines = [
        f"<b>{place.get('name', '—')}</b> {CATEGORY_ICON.get(place.get('category', {}).get('key') or '', '')}",
        f"🏷 {place.get('category', {}).get('name_uz', '')}",
        f"📍 {place.get('district', '')}, {place.get('address', '')}",
        f"⭐ Reyting: {fmt_rating(place.get('avg_rating'))}",
    ]
    if place.get("distance_km") is not None:
        lines.append(f"📏 Masofa: {place['distance_km']} km")
    occ = place.get("occupancy") or {}
    if occ.get("level") and not occ.get("is_stale"):
        lines.append(f"🧍 Bandlik: {OCCUPANCY_LABEL.get(occ['level'], occ['level'])}")
    lines.append(
        f"🌐 Wi-Fi: {WIFI_LABEL.get(place.get('wifi_speed'), '')} | "
        f"🔊 Shovqin: {NOISE_LABEL.get(place.get('noise_level'), '')}\n"
        f"🔌 Rozetka: {OUTLET_LABEL.get(place.get('outlets_level'), '')} | "
        f"💵 Narx: {PRICE_LABEL.get(place.get('price_level'), '')}"
    )
    return "\n".join(lines)
