from django.core.cache import cache
from .models import FeatureToggle


CACHE_KEY = "website_feature_toggles"


def get_feature_toggles():

    features = cache.get(CACHE_KEY)

    if features is None:

        features = {

            item.key: item.enabled

            for item in FeatureToggle.objects.all()

        }

        cache.set(

            CACHE_KEY,

            features,

            60 * 30,

        )   # 30 minutes

    return features


def feature_enabled(key):

    return get_feature_toggles().get(

        key,

        False,

    )


def clear_feature_cache():

    cache.delete(CACHE_KEY)