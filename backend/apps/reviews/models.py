from django.db import models


class Review(models.Model):
    place = models.ForeignKey(
        "places.Place", related_name="reviews", on_delete=models.CASCADE
    )
    user = models.ForeignKey("accounts.User", on_delete=models.CASCADE)
    rating = models.PositiveSmallIntegerField()
    wifi_rating = models.PositiveSmallIntegerField(null=True, blank=True)
    noise_rating = models.PositiveSmallIntegerField(null=True, blank=True)
    comfort_rating = models.PositiveSmallIntegerField(null=True, blank=True)
    text = models.TextField(blank=True)
    ai_flagged = models.BooleanField(default=False)
    ai_summary_tag = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def clean(self):
        if not 1 <= self.rating <= 5:
            raise ValueError("rating must be 1-5")


class ReviewPhoto(models.Model):
    review = models.ForeignKey(
        Review, related_name="photos", on_delete=models.CASCADE
    )
    image = models.ImageField(upload_to="reviews/")

    def __str__(self):
        return f"review-photo-{self.pk}"