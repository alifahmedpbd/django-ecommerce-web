from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.conf import settings

import stripe

from store.models import Product
from .cart import Cart
from orders.forms import OrderCreateForm
from orders.models import Order, OrderItem

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

            # Stripe Checkout এ যাবে
            return redirect("cart:create_checkout_session", order.id)

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


# ===============================
# Stripe Checkout Session
# ===============================

def create_checkout_session(request, order_id):

    order = get_object_or_404(Order, id=order_id)

    session = stripe.checkout.Session.create(

        payment_method_types=["card"],

        line_items=[

            {

                "price_data": {

                    "currency": "usd",

                    "product_data": {

                        "name": f"Order #{order.id}",

                    },

                    "unit_amount": int(order.get_total_cost() * 100),

                },

                "quantity": 1,

            }

        ],

        mode="payment",

        success_url=request.build_absolute_uri(
            reverse("cart:payment_success", args=[order.id])
        ) + "?session_id={CHECKOUT_SESSION_ID}",

        cancel_url=request.build_absolute_uri(

            reverse("cart:checkout")

        ),

    )

    return redirect(session.url)


def payment_success(request, order_id):

    order = get_object_or_404(Order, id=order_id)

    session_id = request.GET.get("session_id")

    if session_id:

        session = stripe.checkout.Session.retrieve(session_id)

        order.payment_id = session.payment_intent or session.id

    order.paid = True
    order.payment_method = "stripe"
    order.status = "completed"

    order.save()

    cart = Cart(request)
    cart.clear()

    return redirect("orders:order_success", order.id)