from django.shortcuts import render, get_object_or_404, redirect
from django.conf import settings

import stripe

from store.models import Product
from .cart import Cart
from orders.forms import OrderCreateForm
from orders.models import OrderItem, OrderTimeline, CouponUsage

stripe.api_key = settings.STRIPE_SECRET_KEY
from store.services import can_purchase

from django.contrib import messages

from orders.services import reduce_order_stock, validate_coupon, calculate_discount
from payments.utils import send_order_confirmation_email, send_owner_new_order_email

from django.db.models import F
from django.db import transaction

# ===============================
# Add Product To Cart
# ===============================

def cart_add(request, product_id):

    cart = Cart(request)

    product = get_object_or_404(
        Product.objects.only(
            "id",
            "name",
            "price",
            "stock",
            "slug",
        ),
        id=product_id,
    )
    quantity = int(request.POST.get("quantity", 1))

    if not can_purchase(product, quantity):

        messages.error(
            request,
            f"Only {product.stock} item(s) available in stock."
        )

        return redirect(product.get_absolute_url())

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

    product = get_object_or_404(
        Product.objects.only(
            "id",
        ),
        id=product_id,
    )

    cart.remove(product)

    return redirect("cart:cart_detail")


# ===============================
# Update Quantity
# ===============================

def cart_update(request, product_id, action):

    cart = Cart(request)

    product = get_object_or_404(
        Product.objects.only(
            "id",
            "stock",
        ),
        id=product_id,
    )

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

    subtotal = cart.get_total_price()

    coupon = None
    discount = 0
    final_total = subtotal

    # ==========================================
    # Apply Coupon
    # ==========================================

    coupon_code = request.session.get("coupon_code")

    if coupon_code:

        coupon, error = validate_coupon(
            coupon_code,
            subtotal,
            request.user,
        )

        if coupon:

            discount = calculate_discount(
                coupon,
                subtotal,
            )

            final_total = subtotal - discount

        else:

            request.session.pop("coupon_code", None)

            messages.error(request, error)

    # ==========================================
    # Checkout Submit
    # ==========================================

    if request.method == "POST":

        form = OrderCreateForm(request.POST)

        if form.is_valid():

            # ==========================================
            # Final Stock Validation
            # ==========================================

            for item in cart:

                if not can_purchase(
                    item["product"],
                    item["quantity"],
                ):

                    messages.error(
                        request,
                        f"{item['product'].name} only has {item['product'].stock} item(s)."
                    )

                    return redirect("cart:cart_detail")

            # ==========================================
            # Database Transaction
            # ==========================================

            with transaction.atomic():

                # Create Order

                order = form.save(commit=False)

                order.user = request.user
                order.coupon = coupon
                order.discount = discount
                order.final_total = final_total

                order.save()

                # Order Items

                for item in cart:

                    OrderItem.objects.create(
                        order=order,
                        product=item["product"],
                        price=item["price"],
                        quantity=item["quantity"],
                    )

                # Cash On Delivery

                if order.payment_method == "cod":

                    order.status = "pending"
                    order.paid = False
                    order.payment_status = "pending"

                    order.save(
                        update_fields=[
                            "status",
                            "paid",
                            "payment_status",
                        ]
                    )

                    OrderTimeline.objects.create(
                        order=order,
                        user=request.user,
                        note="Cash On Delivery order placed.",
                    )

                    reduce_order_stock(order)

                    if coupon:

                        CouponUsage.objects.create(
                            coupon=coupon,
                            user=request.user,
                            order=order,
                        )

                        coupon.used_count = F("used_count") + 1
                        coupon.save(update_fields=["used_count"])

            # ==========================================
            # Stripe
            # ==========================================

            if order.payment_method == "stripe":

                return redirect(
                    "payments:create_checkout_session",
                    order.id,
                )

            # ==========================================
            # COD (Outside Transaction)
            # ==========================================

            if order.payment_method == "cod":

                send_order_confirmation_email(
                    request,
                    order,
                )

                send_owner_new_order_email(
                    request,
                    order,
                )

                cart.clear()

                request.session.pop(
                    "coupon_code",
                    None,
                )

                return redirect(
                    "orders:order_success",
                    order.id,
                )

            # ==========================================
            # SSL
            # ==========================================

            if order.payment_method == "sslcommerz":

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
            "coupon": coupon,
            "discount": discount,
            "subtotal": subtotal,
            "final_total": final_total,
        },
    )
# ==========================================
# Apply Coupon
# ==========================================

def apply_coupon(request):

    if request.method == "POST":

        code = request.POST.get(

            "coupon_code",

            "",

        ).strip()

        cart = Cart(request)

        subtotal = cart.get_total_price()

        coupon, error = validate_coupon(

            code,

            subtotal,

            request.user,

        )

        if coupon:

            request.session["coupon_code"] = coupon.code

            messages.success(

                request,

                "Coupon applied successfully."

            )

        else:

            messages.error(

                request,

                error,

            )

    return redirect(

        "cart:checkout",

    )


# ==========================================
# Remove Coupon
# ==========================================

def remove_coupon(request):

    request.session.pop(

        "coupon_code",

        None,

    )

    messages.success(

        request,

        "Coupon removed."

    )

    return redirect(

        "cart:checkout",

    )
