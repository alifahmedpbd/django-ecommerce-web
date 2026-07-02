from django.shortcuts import render, get_object_or_404, redirect
from store.models import Product
from .cart import Cart

# Create your views here.

def cart_add(request, product_id):

    cart = Cart(request)

    product = get_object_or_404(Product, id=product_id)

    cart.add(product)
    return redirect("cart:cart_detail")

def cart_detail(request):

    cart = Cart(request)

    return render(request, "cart/cart_detail.html", {"cart": cart})

def cart_remove(request, product_id):

    cart = Cart(request)

    product = get_object_or_404(Product, id=product_id)

    cart.remove(product)

    return redirect("cart:cart_detail")
