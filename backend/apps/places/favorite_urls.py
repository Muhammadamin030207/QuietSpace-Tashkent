from django.urls import path

from . import favorite_views

urlpatterns = [
    path("", favorite_views.FavoriteListCreateView.as_view(), name="favorites"),
    path(
        "<int:place_id>/", favorite_views.FavoriteDeleteView.as_view(),
        name="favorite-delete",
    ),
]