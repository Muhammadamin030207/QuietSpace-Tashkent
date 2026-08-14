from django.contrib.gis.db import models as gis_models
from django.db import models


class Category(models.Model):
    key = models.SlugField(unique=True)  # cafe | library | coworking | free_zone
    name_uz = models.CharField(max_length=64)
    name_ru = models.CharField(max_length=64)
    name_en = models.CharField(max_length=64)
    icon = models.CharField(max_length=64)

    def __str__(self):
        return self.key


class Place(models.Model):
    class WifiSpeed(models.TextChoices):
        NONE = "none", "none"
        SLOW = "slow", "slow"
        MEDIUM = "medium", "medium"
        FAST = "fast", "fast"

    class OutletsLevel(models.TextChoices):
        NONE = "none", "none"
        FEW = "few", "few"
        EVERY_TABLE = "every_table", "every_table"

    class NoiseLevel(models.TextChoices):
        VERY_QUIET = "very_quiet", "very_quiet"
        QUIET = "quiet", "quiet"
        MODERATE = "moderate", "moderate"
        NOISY = "noisy", "noisy"

    class PriceLevel(models.TextChoices):
        FREE = "free", "free"
        USD1 = "$", "$"
        USD2 = "$$", "$$"
        USD3 = "$$$", "$$$"

    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    category = models.ForeignKey(Category, on_delete=models.PROTECT)
    owner = models.ForeignKey(
        "accounts.User", null=True, blank=True, on_delete=models.SET_NULL,
        related_name="owned_places",
    )
    location = gis_models.PointField(geography=True, srid=4326)
    address = models.CharField(max_length=300)
    district = models.CharField(max_length=100)
    wifi_speed = models.CharField(
        max_length=20, choices=WifiSpeed.choices, default=WifiSpeed.MEDIUM
    )
    outlets_level = models.CharField(
        max_length=20, choices=OutletsLevel.choices, default=OutletsLevel.FEW
    )
    noise_level = models.CharField(
        max_length=20, choices=NoiseLevel.choices, default=NoiseLevel.QUIET
    )
    price_level = models.CharField(
        max_length=10, choices=PriceLevel.choices, default=PriceLevel.FREE
    )
    working_hours = models.JSONField(default=dict)
    amenities = models.JSONField(default=list)
    is_verified = models.BooleanField(default=False)
    avg_rating = models.DecimalField(max_digits=3, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.name

    def update_avg_rating(self):
        from apps.reviews.models import Review

        avg = Review.objects.filter(place=self).aggregate(
            avg=models.Avg("rating")
        )["avg"]
        self.avg_rating = round(avg or 0, 2)
        self.save(update_fields=["avg_rating"])


class PlacePhoto(models.Model):
    place = models.ForeignKey(Place, related_name="photos", on_delete=models.CASCADE)
    image = models.ImageField(upload_to="places/")

    def __str__(self):
        return f"photo-{self.pk}"


class Favorite(models.Model):
    user = models.ForeignKey("accounts.User", on_delete=models.CASCADE, related_name="favorites")
    place = models.ForeignKey(Place, on_delete=models.CASCADE, related_name="favorited_by")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "place")
