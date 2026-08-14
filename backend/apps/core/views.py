from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from apps.places.models import Category, Place
from apps.reviews.models import Review


@api_view(["GET"])
@permission_classes([AllowAny])
def stats(request):
    data = {
        "places_count": Place.objects.count(),
        "reviews_count": Review.objects.count(),
        "categories": list(Category.objects.values("key", "name_uz", "name_ru", "name_en")),
        "districts": list(
            Place.objects.values_list("district", flat=True).distinct().order_by("district")
        ),
    }
    return Response(data)
