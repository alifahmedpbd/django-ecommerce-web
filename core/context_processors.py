from cart.cart import Cart
from store.models import Wishlist

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