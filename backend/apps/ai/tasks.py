import logging

from config import celery_app
from .client import complete, parse_ai_json

logger = logging.getLogger(__name__)


@celery_app.task
def moderate_review(review_id):
    """AI moderation of a newly created review (async)."""
    from apps.reviews.models import Review

    try:
        review = Review.objects.select_related("place").get(id=review_id)
    except Review.DoesNotExist:
        logger.warning("Review %s not found", review_id)
        return

    system = (
        "Sen sharhlar moderatorisisan. Sharhni spam, haqorat va mazmun bo'yicha bahola.\n"
        "Faqat JSON qaytar: "
        '{"is_spam": false, "is_abusive": false, "short_tag": "shovqinli kechqurun"}\n'
        "short_tag — sharh mazmunini 3-6 so'zda tasvirlaydigan qisqa teg (uzbek/rus tilida).\n"
        "Boshqa hech narsa yozma."
    )
    try:
        text = complete(
            system=system,
            max_tokens=200,
            messages=[
                {
                    "role": "user",
                    "content": f"Joy: {review.place.name}\nReyting: {review.rating}/5\nSharh: {review.text[:2000]}",
                }
            ],
        )
        result = parse_ai_json(text) or {}
        review.ai_flagged = bool(result.get("is_spam") or result.get("is_abusive"))
        review.ai_summary_tag = str(result.get("short_tag") or "")[:100]
        review.save(update_fields=["ai_flagged", "ai_summary_tag"])
    except Exception as exc:  # noqa: BLE001
        logger.error("moderate_review failed for %s: %s", review_id, exc)


@celery_app.task
def summarize_place_reviews(place_id):
    """AI-generated 2-3 sentence summary of a place's reviews (cached 24h)."""
    from apps.places.models import Place
    from .models import PlaceAISummary

    try:
        place = Place.objects.get(id=place_id)
    except Place.DoesNotExist:
        logger.warning("Place %s not found", place_id)
        return

    reviews = list(
        place.reviews.select_related("user").order_by("-created_at")[:30]
    )
    if not reviews:
        return

    lines = [
        f"- {r.user.username}: {r.rating}/5 — {r.text[:300]}" for r in reviews
    ]
    system = (
        "Sen joy sharhlarini umumlashtiruvchisan.\n"
        "Oxirgi 30 ta sharh asosida 2-3 jumlali xulosa yoz (uzbek tilida): "
        "joyning umumiy bahosi, kuchli tomonlari va kuzatilgan kamchiliklar.\n"
        "Faqat JSON qaytar: {\"summary\": \"...\"}. Boshqa hech narsa yozma."
    )
    try:
        text = complete(
            system=system,
            max_tokens=400,
            messages=[{"role": "user", "content": "\n".join(lines)}],
        )
        result = parse_ai_json(text) or {}
        summary = result.get("summary") or text.strip().strip('"')
        PlaceAISummary.objects.update_or_create(
            place=place, defaults={"text": summary[:2000]}
        )
    except Exception as exc:  # noqa: BLE001
        logger.error("summarize_place_reviews failed for %s: %s", place_id, exc)