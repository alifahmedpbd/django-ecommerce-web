from .helpers import get_feature_toggles
from dashboard.helpers import feature_enabled
from dashboard.models import Announcement, WebsiteSettings


def feature_toggles(request):

    return {

        "features": get_feature_toggles()

    }


def website_context(request):

    return {

        "website_features": {

            "announcement": feature_enabled("announcement"),
            "coming_soon": feature_enabled("coming_soon"),
            "emi": feature_enabled("emi"),

            "wishlist": feature_enabled("wishlist"),
            "reviews": feature_enabled("reviews"),
            "flash_sale": feature_enabled("flash_sale"),
            "free_delivery": feature_enabled("free_delivery"),
            "trending": feature_enabled("trending"),
            "new_arrival": feature_enabled("new_arrival"),
            "guest_checkout": feature_enabled("guest_checkout"),
            "coupon": feature_enabled("coupon"),
            "cod": feature_enabled("cod"),
        },

        "active_announcements": Announcement.objects.filter(
            is_active=True
        ),

        "website_settings": WebsiteSettings.load(),
    }