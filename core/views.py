from django.shortcuts import render

from store.models import Product, Category

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

            "price",

            "image",

            "is_flash_sale",

            "is_trending",

            "is_new_arrival",

            "is_free_delivery",

        )

        .order_by("-created_at")[:8]

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

            .order_by("-updated_at")[:12]

        )

    context = {

        "featured_products": featured_products,

        "featured_categories": featured_categories,

        "flash_products": flash_products,

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