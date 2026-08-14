from django.shortcuts import get_object_or_404
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Favorite, Place
from .serializers import FavoriteSerializer, PlaceListSerializer


class FavoriteListCreateView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        qs = (
            Favorite.objects.filter(user=request.user)
            .select_related("place__category")
            .prefetch_related("place__photos", "place__occupancy_reports")
            .order_by("-created_at")
        )
        serializer = FavoriteSerializer(qs, many=True, context={"request": request})
        return Response(serializer.data)

    def post(self, request):
        place_id = request.data.get("place_id")
        if not place_id:
            return Response({"detail": "place_id is required"}, status=400)
        place = get_object_or_404(Place, id=place_id)
        favorite, created = Favorite.objects.get_or_create(
            user=request.user, place=place
        )
        if not created:
            return Response(
                {"detail": "Already in favorites"}, status=status.HTTP_200_OK
            )
        serializer = FavoriteSerializer(favorite, context={"request": request})
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class FavoriteDeleteView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request, place_id):
        deleted, _ = Favorite.objects.filter(
            user=request.user, place_id=place_id
        ).delete()
        if not deleted:
            return Response({"detail": "Not found"}, status=404)
        return Response(status=status.HTTP_204_NO_CONTENT)
