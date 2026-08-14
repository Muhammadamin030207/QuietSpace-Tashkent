from django.contrib.auth import get_user_model
from django.utils.translation import gettext as _

from config import celery_app
from .models import Notification
from .services.telegram_push import send_message

User = get_user_model()


@celery_app.task
def notify_favorite_place_free(place_id):
    """When a place is reported, notify users who favorited it if free."""
    from apps.places.models import Favorite

    favorites = Favorite.objects.filter(place_id=place_id).select_related("place", "user")
    if not favorites.exists():
        return
    place = favorites.first().place
    for fav in favorites:
        user = fav.user
        Notification.objects.create(
            user=user,
            kind="favorite_free",
            payload={"place_id": place_id, "place_name": place.name},
        )
        if user.telegram_id:
            send_message(
                user.telegram_id,
                _(f"✅ {place.name} — hozir bandlik holati yangilandi! "
                  f"Tezda tekshirib ko'ring."),
            )


@celery_app.task
def notify_new_place(place_id):
    """Broadcast to admin/moderator users about a new place submission."""
    from apps.places.models import Place

    place = Place.objects.get(id=place_id)
    for user in User.objects.filter(role__in=["moderator", "admin"]):
        Notification.objects.create(
            user=user,
            kind="new_place",
            payload={"place_id": place_id, "place_name": place.name},
        )
