from django.core.cache import cache

from store.models import Wishlist
from dashboard.models import FeatureToggle


def global_data(request):

    wishlist_count = 0

    if request.user.is_authenticated:

        wishlist_count = (
            Wishlist.objects
            .filter(user=request.user)
            .count()
        )

    return {
        "wishlist_count": wishlist_count,
        "SHOP_NAME": "Shopora",
        "SHOP_TAGLINE": "Smart Shopping, Simplified.",
    }


def site_settings(request):

    features = cache.get(
        "shopora_feature_toggles"
    )

    if features is None:

        features = {
            item.key: item.enabled
            for item in FeatureToggle.objects.all()
        }

        cache.set(
            "shopora_feature_toggles",
            features,
            60,
        )

    return {
        "features": features,
    }


def announcement(request):

    return {
        "active_announcements": [],
    }