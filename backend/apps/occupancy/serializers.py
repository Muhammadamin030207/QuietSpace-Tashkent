from rest_framework import serializers

from .models import OccupancyReport


class OccupancyReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = OccupancyReport
        fields = ("id", "level", "reported_at", "place")
        read_only_fields = ("id", "reported_at", "place")

    def validate_level(self, value):
        if value not in OccupancyReport.Level.values:
            raise serializers.ValidationError("level must be empty|medium|full")
        return value