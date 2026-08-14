from django.contrib import admin

from .models import Category, Favorite, Place, PlacePhoto


class PlacePhotoInline(admin.TabularInline):
    model = PlacePhoto
    extra = 0


@admin.register(Place)
class PlaceAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "category", "district", "noise_level", "avg_rating", "is_verified")
    list_filter = ("category", "district", "noise_level", "is_verified")
    search_fields = ("name", "address")
    inlines = [PlacePhotoInline]


admin.site.register(Category)
admin.site.register(Favorite)
