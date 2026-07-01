from django.shortcuts import render, get_object_or_404
from .models import Product, Category
# Create your views here.

def product_list(request):
    products = Product.objects.filter(available=True)
    
    context = {
        "products": products,
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