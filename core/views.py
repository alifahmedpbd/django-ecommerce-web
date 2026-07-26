from django.shortcuts import render

from store.models import Product, Category, Wishlist

from dashboard.helpers import feature_enabled

# Create your views here.
# ==========================================
# Home
# ==========================================

def home(request):

    # Featured Products

    featured_products = (

        Product.objects

        .filter(

            available=True,

        )

        .only(

            "id",
            "slug",
            "name",
            "description",
            "image",

            "price",
            "flash_price",

            "stock",
            "available",

            "is_flash_sale",
            "is_trending",
            "is_new_arrival",
            "is_free_delivery",
            
            "display_order",
            "created_at",

            "category__id",
            "category__name",
            
        )

        .order_by(
            "display_order",
            "-created_at",
        )[:8]

    )

    # Featured Categories

    featured_categories = (

        Category.objects

        .only(

            "id",

            "name",

            "slug",

        )[:4]

    )

    # ==========================================
    # Flash Sale
    # ==========================================

    flash_products = Product.objects.none()

    if feature_enabled("flash_sale"):

        flash_products = (

            Product.objects

            .filter(

                available=True,

                is_flash_sale=True,

            )

            .only(

                "id",

                "slug",

                "name",

                "price",

                "image",

                "is_flash_sale",

            )

            .order_by(
                "display_order",
                "-updated_at",
            )[:12]

        )

    wishlist_products = set()

    if request.user.is_authenticated:
        wishlist_products = set(
            Wishlist.objects.filter(
                user=request.user
            ).values_list(
                "product_id",
                flat=True,
            )
        )

    context = {

        "featured_products": featured_products,

        "featured_categories": featured_categories,

        "flash_products": flash_products,

        "wishlist_products": wishlist_products,

    }

    return render(

        request,

        "core/home.html",

        context,

    )


# ==========================================
# Static Pages
# ==========================================

def about(request):

    return render(

        request,

        "core/about.html",

    )


def contact(request):

    return render(

        request,

        "core/contact.html",

    )


def faq(request):

    return render(

        request,

        "core/faq.html",

    )


def privacy(request):

    return render(

        request,

        "core/privacy.html",

    )


def terms(request):

    return render(

        request,

        "core/terms.html",

    )