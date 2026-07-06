from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.conf import settings

import stripe

from store.models import Product
from .cart import Cart
from orders.forms import OrderCreateForm
from orders.models import Order, OrderItem

from django.core.mail import send_mail
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags

stripe.api_key = settings.STRIPE_SECRET_KEY


# ===============================
# Add Product To Cart
# ===============================

def cart_add(request, product_id):

    cart = Cart(request)

    product = get_object_or_404(Product, id=product_id)

    cart.add(product)

    return redirect("cart:cart_detail")


# ===============================
# Cart Detail
# ===============================

def cart_detail(request):

    cart = Cart(request)

    return render(
        request,
        "cart/cart_detail.html",
        {
            "cart": cart
        }
    )


# ===============================
# Remove Item
# ===============================

def cart_remove(request, product_id):

    cart = Cart(request)

    product = get_object_or_404(Product, id=product_id)

    cart.remove(product)

    return redirect("cart:cart_detail")


# ===============================
# Update Quantity
# ===============================

def cart_update(request, product_id, action):

    cart = Cart(request)

    product = get_object_or_404(Product, id=product_id)

    quantity = cart.cart[str(product.id)]["quantity"]

    if action == "increase":

        quantity += 1

    elif action == "decrease":

        quantity -= 1

    if quantity <= 0:

        cart.remove(product)

    else:

        cart.update(product, quantity)

    return redirect("cart:cart_detail")


# ===============================
# Checkout
# ===============================

def checkout(request):

    cart = Cart(request)

    if len(cart) == 0:

        return redirect("store:product_list")

    if request.method == "POST":

        form = OrderCreateForm(request.POST)

        if form.is_valid():

            order = form.save(commit=False)

            order.user = request.user

            order.save()

            for item in cart:

                OrderItem.objects.create(

                    order=order,

                    product=item["product"],

                    price=item["price"],

                    quantity=item["quantity"]

                )

# ===============================
# Payment Method
# ===============================

            if order.payment_method == "stripe":

                return redirect(
                    "payments:create_checkout_session",
                    order.id,
                )

            elif order.payment_method == "cod":

                order.paid = False

                order.status = "pending"

                order.save()

                cart.clear()

                return redirect(
                    "orders:order_success",
                    order.id,
                )

# Future SSLCommerz
            elif order.payment_method == "sslcommerz":

                return redirect(
                    "cart:create_checkout_session",
                    order.id,
                )

    else:

        form = OrderCreateForm()

    return render(

        request,

        "cart/checkout.html",

        {

            "cart": cart,

            "form": form,

        }

    )
