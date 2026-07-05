from django.shortcuts import render, get_object_or_404, redirect
from .models import Product, Category, Wishlist, Review
from django.core.paginator import Paginator
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from .forms import ReviewForm
from django.db.models import Count
from django.contrib import messages
# Create your views here.

def product_list(request, category_slug=None):

    category = None

    categories = Category.objects.all()

    products = Product.objects.filter(available=True)

    #Category Filter
    if category_slug:

        category = get_object_or_404(Category, slug=category_slug)

        products = products.filter(category=category)

    #Search
    query = request.GET.get("q")

    if query:
        products = products.filter(
            Q(name__icontains=query) |
            Q(description__icontains=query)
        )
    
    #Sorting
    sort = request.GET.get("sort")

    if sort == "low":
        products = products.order_by("price")
    
    elif sort == "high":
        products = products.order_by("-price")

    # min and max price filter
    min_price = request.GET.get("min_price")
    max_price = request.GET.get("max_price")

    if min_price:
        products = products.filter(price__gte=min_price)

    if max_price:
        products = products.filter(price__lte=max_price)

    # Stock filter
    stock = request.GET.get("stock")

    if stock == "in":
        products = products.filter(stock__gt=0)

    elif stock == "out":
        products = products.filter(stock=0)

    # Latest Products
    latest_products = Product.objects.filter(available=True).order_by("-created_at")[:5]

    # Popular Products
    popular_products = Product.objects.filter(available=True).order_by("-views")[:5]

    #Featured Products
    featured_products = Product.objects.filter(featured=True, available=True)[:4]

    #Pagination
    paginator = Paginator(products, 6) # Show 6 products per page

    page_number = request.GET.get("page")

    page_obj = paginator.get_page(page_number)

    wishlist_products = []

    if request.user.is_authenticated:

        wishlist_products = Wishlist.objects.filter(
            user=request.user
        ).values_list(
            "product_id",
            flat=True
        )

    context = {
        "category": category,
        "categories": categories,
        "products": page_obj,
        "page_obj": page_obj,
        "featured_products": featured_products,
        "latest_products": latest_products,
        "popular_products": popular_products,
        "wishlist_products": wishlist_products,
    }

    return render(request, "store/product_list.html", context)

def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug, available=True)
    form = None
    related_products = Product.objects.filter(category=product.category, available=True).exclude(id=product.id)[:4]
    product.views += 1
    product.save()

    reviews = product.reviews.all()

    average_rating = product.average_rating()

    total_reviews = reviews.count()

    rating_summary = []

    for star in range(5, 0, -1):

        count = reviews.filter(
            rating=star
        ).count()

        percentage = 0

        if total_reviews:

            percentage = (count / total_reviews) * 100

        rating_summary.append({

            "star": star,

            "count": count,

            "percentage": percentage,

        })

    is_wishlisted = False

    if request.user.is_authenticated:

        is_wishlisted = Wishlist.objects.filter(
            user=request.user,
            product=product
        ).exists()

    # Review Form
    if request.user.is_authenticated:

        review = Review.objects.filter(
            product=product,
            user=request.user,
        ).first()

        if request.method == "POST":

            form = ReviewForm(
                request.POST,
                instance=review,
            )

            if form.is_valid():

                review = form.save(commit=False)

                review.user = request.user

                review.product = product

                review.save()

                messages.success(
                    request,
                    "Thank you for your review."
                )



                return redirect(
                    "store:product_detail",
                    slug=product.slug,
                )

        else:

            form = ReviewForm(
                instance=review,
            )

    else:

        form = None

    context = {
        "product": product,
        "related_products": related_products,
        "reviews": reviews,
        "rating_summary": rating_summary,
        "average_rating": average_rating,
        "total_reviews": total_reviews,
        "form": form,
        "is_wishlisted": is_wishlisted
    }

    return render(request, "store/product_detail.html", context)


from django.contrib import messages

@login_required
def delete_review(request, review_id):

    review = get_object_or_404(
        Review,
        id=review_id,
        user=request.user,
    )

    product_slug = review.product.slug

    review.delete()

    messages.success(
        request,
        "Review deleted successfully."
    )

    return redirect(
        "store:product_detail",
        slug=product_slug,
    )

# ==========================================
# Add Product To Wishlist
# ==========================================

@login_required
def add_to_wishlist(request, product_id):

    product = get_object_or_404(
        Product,
        id=product_id,
    )

    Wishlist.objects.get_or_create(
        user=request.user,
        product=product,
    )

    return redirect(request.META.get("HTTP_REFERER", "store:product_list"))

# ==========================================
# Remove Product From Wishlist
# ==========================================

@login_required
def remove_from_wishlist(request, product_id):

    product = get_object_or_404(
        Product,
        id=product_id,
    )

    Wishlist.objects.filter(
        user=request.user,
        product=product,
    ).delete()

    return redirect(request.META.get("HTTP_REFERER", "store:product_list"))

# ==========================================
# Wishlist Page
# ==========================================

@login_required
def wishlist(request):

    wishlist_items = Wishlist.objects.filter(
        user=request.user
    ).select_related("product")

    return render(request, "store/wishlist.html", {"wishlist_items": wishlist_items},)
