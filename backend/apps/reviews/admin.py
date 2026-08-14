from django.contrib import admin

from .models import Review, ReviewPhoto


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ("id", "place", "user", "rating", "ai_flagged", "ai_summary_tag", "created_at")
    list_filter = ("ai_flagged", "rating")
    search_fields = ("text",)


admin.site.register(ReviewPhoto)
