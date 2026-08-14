from django.contrib.gis.db.models.functions import Distance
from django.contrib.gis.geos import Point
from django.contrib.gis.measure import D
from django.db.models import Avg, Count
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.occupancy.models import OccupancyReport
from apps.occupancy.serializers import OccupancyReportSerializer
from apps.reviews.models import Review
from apps.reviews.serializers import ReviewSerializer

from .models import Category, Place
from .serializers import (
    CategorySerializer,
    PlaceDetailSerializer,
    PlaceListSerializer,
    PlaceWriteSerializer,
)

MAX_RADIUS_KM = 50
DEFAULT_RADIUS_KM = 5


class PlaceViewSet(viewsets.ReadOnlyModelViewSet):
    """Places: list (with filters), retrieve, nearby, reviews, occupancy."""

    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    http_method_names = ["get", "post", "patch", "head", "options"]

    def get_serializer_class(self):
        if self.action == "create":
            return PlaceWriteSerializer
        if self.action == "partial_update":
            return PlaceWriteSerializer
        if self.action == "retrieve":
            return PlaceDetailSerializer
        return PlaceListSerializer

    def get_queryset(self):
        qs = Place.objects.select_related("category").prefetch_related(
            "photos", "occupancy_reports"
        )
        params = self.request.query_params

        category = params.get("category")
        if category:
            qs = qs.filter(category__key=category)
        wifi = params.get("wifi")
        if wifi:
            qs = qs.filter(wifi_speed__in=wifi.split(","))
        noise = params.get("noise")
        if noise:
            qs = qs.filter(noise_level__in=noise.split(","))
        price = params.get("price")
        if price:
            qs = qs.filter(price_level__in=price.split(","))
        outlets = params.get("outlets")
        if outlets:
            qs = qs.filter(outlets_level__in=outlets.split(","))
        district = params.get("district")
        if district:
            qs = qs.filter(district__iexact=district)
        q = params.get("q")
        if q:
            qs = qs.filter(name__icontains=q)

        lat, lng = _parse_coords(params)
        if lat is not None and lng is not None:
            point = Point(lng, lat, srid=4326)
            radius_km = _parse_radius(params)
            qs = (
                qs.filter(location__distance_lte=(point, D(km=radius_km)))
                .annotate(distance=Distance("location", point))
                .order_by("distance")
            )
            self._annotate_occupancy(qs)
        return qs

    @staticmethod
    def _annotate_occupancy(qs):
        """Attach latest occupancy report per place (single query)."""
        latest_ids = (
            OccupancyReport.objects.filter(
                place_id__in=qs.values("id")
            )
            .order_by("place_id", "-reported_at")
            .distinct("place_id")
            .values_list("id", flat=True)
        )
        latest = {
            r.place_id: r
            for r in OccupancyReport.objects.filter(id__in=list(latest_ids))
        }
        for obj in qs:
            obj._latest_report = latest.get(obj.id)

    @action(detail=False, methods=["get"], url_path="nearby")
    def nearby(self, request):
        lat = request.query_params.get("lat")
        lng = request.query_params.get("lng")
        if not lat or not lng:
            return Response(
                {"detail": "lat and lng are required"}, status=status.HTTP_400_BAD_REQUEST
            )
        radius_km = _parse_radius(request.query_params)
        point = Point(float(lng), float(lat), srid=4326)
        qs = (
            self.get_queryset()
            .filter(location__distance_lte=(point, D(km=radius_km)))
            .annotate(distance=Distance("location", point))
            .order_by("distance")
        )
        self._annotate_occupancy(qs)
        page = self.paginate_queryset(qs)
        serializer = self.get_serializer(page or qs, many=True)
        if page is not None:
            return self.get_paginated_response(serializer.data)
        return Response(serializer.data)

    @action(detail=True, methods=["get", "post"], url_path="reviews")
    def reviews(self, request, pk=None):
        place = self.get_object()
        if request.method == "POST":
            if not request.user.is_authenticated:
                return Response(
                    {"detail": "Authentication required"}, status=401
                )
            serializer = ReviewSerializer(
                data=request.data,
                context={"request": request},
            )
            serializer.is_valid(raise_exception=True)
            review = serializer.save(place=place, user=request.user)
            place.update_avg_rating()
            from apps.ai.tasks import moderate_review

            moderate_review.delay(review.id)
            return Response(
                ReviewSerializer(review, context={"request": request}).data,
                status=status.HTTP_201_CREATED,
            )
        qs = (
            place.reviews.select_related("user")
            .order_by("-created_at")
        )
        page = self.paginate_queryset(qs)
        serializer = ReviewSerializer(page or qs, many=True, context={"request": request})
        if page is not None:
            return self.get_paginated_response(serializer.data)
        return Response(serializer.data)

    @action(detail=True, methods=["get", "post"], url_path="occupancy")
    def occupancy(self, request, pk=None):
        place = self.get_object()
        if request.method == "POST":
            serializer = OccupancyReportSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            report = serializer.save(
                place=place,
                user=request.user if request.user.is_authenticated else None,
            )
            from apps.notifications.tasks import notify_favorite_place_free

            notify_favorite_place_free.delay(place.id)
            return Response(OccupancyReportSerializer(report).data, status=201)
        report = (
            place.occupancy_reports.order_by("-reported_at").first()
        )
        if report is None:
            return Response({"level": None, "is_stale": True, "reported_at": None})
        return Response(
            {
                "level": report.level,
                "is_stale": report.is_stale,
                "reported_at": report.reported_at,
            }
        )

    @action(detail=True, methods=["get"], url_path="ai-summary")
    def ai_summary(self, request, pk=None):
        place = self.get_object()
        summary = getattr(place, "ai_summary", None)
        from apps.ai.tasks import summarize_place_reviews

        if summary is None or summary.is_stale:
            summarize_place_reviews.delay(place.id)
            return Response(
                {
                    "summary": summary.text if summary else None,
                    "status": "generating",
                }
            )
        return Response({"summary": summary.text, "status": "ready"})


def _parse_coords(params):
    try:
        return float(params.get("lat")), float(params.get("lng"))
    except (TypeError, ValueError):
        return None, None


def _parse_radius(params):
    try:
        radius = float(params.get("radius_km", DEFAULT_RADIUS_KM))
        return min(radius, MAX_RADIUS_KM)
    except (TypeError, ValueError):
        return DEFAULT_RADIUS_KM
