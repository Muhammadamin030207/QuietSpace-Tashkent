from django.contrib.gis.db.models.functions import Distance
from django.contrib.gis.geos import Point
from rest_framework import serializers

from apps.occupancy.serializers import OccupancyReportSerializer
from apps.reviews.serializers import ReviewSerializer

from .models import Category, Favorite, Place, PlacePhoto


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ("key", "name_uz", "name_ru", "name_en", "icon")


class PlacePhotoSerializer(serializers.ModelSerializer):
    class Meta:
        model = PlacePhoto
        fields = ("id", "image")


class PlaceListSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    photo = serializers.SerializerMethodField()
    distance_km = serializers.SerializerMethodField()
    occupancy = serializers.SerializerMethodField()
    lat = serializers.SerializerMethodField()
    lng = serializers.SerializerMethodField()

    class Meta:
        model = Place
        fields = (
            "id", "name", "category", "photo", "district", "address",
            "lat", "lng", "wifi_speed", "noise_level", "price_level",
            "outlets_level", "avg_rating", "is_verified", "distance_km",
            "occupancy",
        )

    def get_lat(self, obj):
        return obj.location.y if obj.location else None

    def get_lng(self, obj):
        return obj.location.x if obj.location else None

    def get_photo(self, obj):
        photo = obj.photos.first()
        if photo:
            return self.context["request"].build_absolute_uri(photo.image.url)
        return None

    def get_distance_km(self, obj):
        distance = getattr(obj, "distance", None)
        if distance is not None:
            return round(distance.km, 2)
        return None

    def get_occupancy(self, obj):
        report = getattr(obj, "_latest_report", None)
        if report is None and hasattr(obj, "occupancy_reports"):
            report = obj.occupancy_reports.order_by("-reported_at").first()
        if report is None:
            return {"level": None, "reported_at": None, "is_stale": True}
        return {
            "level": report.level,
            "reported_at": report.reported_at,
            "is_stale": report.is_stale,
        }


class PlaceDetailSerializer(PlaceListSerializer):
    reviews = serializers.SerializerMethodField()
    photos = PlacePhotoSerializer(many=True, read_only=True)
    working_hours = serializers.JSONField()
    amenities = serializers.JSONField()
    is_favorite = serializers.SerializerMethodField()

    class Meta(PlaceListSerializer.Meta):
        fields = PlaceListSerializer.Meta.fields + (
            "description", "working_hours", "amenities", "owner",
            "photos", "reviews", "is_favorite", "created_at",
        )
        extra_kwargs = {"owner": {"read_only": True}}

    def get_reviews(self, obj):
        reviews = obj.reviews.select_related("user")[:5]
        return ReviewSerializer(reviews, many=True, context=self.context).data

    def get_is_favorite(self, obj):
        user = self.context["request"].user
        if not user.is_authenticated:
            return False
        return Favorite.objects.filter(user=user, place=obj).exists()


class PlaceWriteSerializer(serializers.ModelSerializer):
    lat = serializers.FloatField(write_only=True)
    lng = serializers.FloatField(write_only=True)
    category_key = serializers.SlugField(write_only=True)
    photo = serializers.ImageField(write_only=True, required=False)

    class Meta:
        model = Place
        fields = (
            "name", "description", "category_key", "address", "district",
            "lat", "lng", "wifi_speed", "outlets_level", "noise_level",
            "price_level", "working_hours", "amenities", "photo",
        )

    def validate_category_key(self, value):
        try:
            return Category.objects.get(key=value)
        except Category.DoesNotExist:
            raise serializers.ValidationError("Unknown category key")

    def create(self, validated_data):
        lat = validated_data.pop("lat")
        lng = validated_data.pop("lng")
        photo = validated_data.pop("photo", None)
        category = validated_data.pop("category_key")
        validated_data["location"] = Point(lng, lat, srid=4326)
        validated_data["category"] = category
        place = Place.objects.create(**validated_data)
        if photo:
            PlacePhoto.objects.create(place=place, image=photo)
        return place


class FavoriteSerializer(serializers.ModelSerializer):
    place = PlaceListSerializer(read_only=True)

    class Meta:
        model = Favorite
        fields = ("id", "place", "created_at")
