from django.shortcuts import render, get_object_or_404
from .models import Product, Category
from django.core.paginator import Paginator
from django.db.models import Q
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

    #Featured Products
    featured_products = Product.objects.filter(featured=True, available=True)[:4]

    #Pagination
    paginator = Paginator(products, 4) # Show 4 peoducts per page

    page_number = request.GET.get("page")

    page_obj = paginator.get_page(page_number)

    context = {
        "category": category,
        "categories": categories,
        "products": page_obj,
        "page_obj": page_obj,
        "featured_products": featured_products,
        
    }

    return render(request, "store/product_list.html", context)

def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug, available=True)
    related_products = Product.objects.filter(category=product.category, available=True).exclude(id=product.id)[:4]

    context = {
        "product": product,
        "related_products": related_products,
    }

    return render(request, "store/product_detail.html", context)