from rest_framework import serializers

from .models import Review


def _validate_rating(value):
    if value is not None and not 1 <= value <= 5:
        raise serializers.ValidationError("rating must be between 1 and 5")
    return value


class ReviewSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(source="user.id", read_only=True)
    username = serializers.CharField(source="user.username", read_only=True)
    photos = serializers.ListField(
        child=serializers.ImageField(), write_only=True, required=False
    )

    class Meta:
        model = Review
        fields = (
            "id", "place", "user_id", "username", "rating",
            "wifi_rating", "noise_rating", "comfort_rating", "text",
            "ai_flagged", "ai_summary_tag", "created_at", "photos",
        )
        read_only_fields = ("place", "ai_flagged", "ai_summary_tag", "created_at")

    def validate_rating(self, value):
        return _validate_rating(value)

    def validate(self, attrs):
        for name in ("wifi_rating", "noise_rating", "comfort_rating"):
            if name in attrs:
                attrs[name] = _validate_rating(attrs[name])
        return attrs

    def create(self, validated_data):
        photos = validated_data.pop("photos", None)
        review = Review.objects.create(**validated_data)
        if photos:
            from .models import ReviewPhoto

            ReviewPhoto.objects.bulk_create(
                [ReviewPhoto(review=review, image=p) for p in photos]
            )
        return review