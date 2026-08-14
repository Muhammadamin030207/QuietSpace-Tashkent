from django.db import models
from django.utils import timezone

STALE_AFTER_MINUTES = 90


class OccupancyReport(models.Model):
    class Level(models.TextChoices):
        EMPTY = "empty", "empty"
        MEDIUM = "medium", "medium"
        FULL = "full", "full"

    place = models.ForeignKey(
        "places.Place",
        related_name="occupancy_reports",
        on_delete=models.CASCADE,
    )
    user = models.ForeignKey(
        "accounts.User", null=True, blank=True, on_delete=models.SET_NULL
    )
    level = models.CharField(max_length=10, choices=Level.choices)
    reported_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-reported_at"]
        indexes = [models.Index(fields=["place", "-reported_at"])]

    @property
    def is_stale(self):
        age = timezone.now() - self.reported_at
        return age.total_seconds() > STALE_AFTER_MINUTES * 60

    def __str__(self):
        return f"{self.place_id}:{self.level}"