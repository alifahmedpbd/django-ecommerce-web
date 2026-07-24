from cart.cart import Cart
from store.models import Wishlist
from dashboard.models import FeatureToggle, Announcement, WebsiteSettings

def global_data(request):

    wishlist_count = 0

    if request.user.is_authenticated:

        wishlist_count = Wishlist.objects.filter(user=request.user).count()

    return {
        "cart": Cart(request),

        "wishlist_count": wishlist_count,

        "SHOP_NAME": "Shopora",

        "SHOP_TAGLINE": "Smart Shopping, Simplified.",
    }




def site_settings(request):

    features = {
        item.key: item.enabled
        for item in FeatureToggle.objects.all()
    }

    return {
        "features": features,
        "settings": WebsiteSettings.load(),
    }

   
def announcement(request):

    active_announcements = Announcement.objects.filter(is_active=True)


    return {
        "active_announcements": active_announcements,
    }