from django.contrib import admin
from .models import FeatureToggle, Announcement, WebsiteSettings

# Register your models here.

@admin.register(FeatureToggle)
class FeatureToggleAdmin(admin.ModelAdmin):

    list_display = (
        "key",
        "enabled",
        "updated_at",
    )

    list_editable = (
        "enabled",
    )

    search_fields = (
        "key",
    )

@admin.register(WebsiteSettings)
class WebsiteSettingsAdmin(admin.ModelAdmin):
    pass

@admin.register(Announcement)
class AnnouncementAdmin(admin.ModelAdmin):

    list_display = (
        "text",
        "is_active",
        "created_at",
    )

    list_filter = (
        "is_active",
    )

    search_fields = (
        "text",
    )