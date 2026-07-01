from django.shortcuts import render
from .models import Product, Category
# Create your views here.

def product_list(request):
    products = Product.objects.filter(available=True)
    
    context = {
        "products": products,
    }

    return render(request, "store/product_list.html", context)