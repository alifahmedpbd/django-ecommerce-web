from django.shortcuts import render
from store.models import Product, Category

# Create your views here.

def home(request):

    featured_products = (
        Product.objects
        .filter(available=True)
        .only(
            "id",
            "slug",
            "name",
            "price",
            "image",
            
        )
        .order_by("-created_at")[:8]
    )
    

    featured_categories = (
        Category.objects
        .only(
            "id",
            "name",
            "slug",
        )[:4]
    )
    
    context = {

        "featured_products": featured_products,

        "featured_categories": featured_categories
    }
    
    return render(request, 'core/home.html', context)

def about(request):

    return render(request, "core/about.html")

def contact(request):

    return render(request, "core/contact.html")

def faq(request):

    return render(request, "core/faq.html")

def privacy(request):

    return render(request, "core/privacy.html")

def terms(request):

    return render(request, "core/terms.html")