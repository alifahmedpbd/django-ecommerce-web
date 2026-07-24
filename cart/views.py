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

from dashboard.helpers import feature_enabled

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

    cart.add(
        product,
        quantity=quantity,
    )

    messages.success(
        request,
        f'"{product.name}" added to cart successfully.'
    )

    # Go back to previous page (Home/Product page)
    return redirect(
        request.META.get(
            "HTTP_REFERER",
            product.get_absolute_url(),
        )
    )


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

    delivery_charge = 5

    if feature_enabled("free_delivery"):
        delivery_charge = 0

    final_total = subtotal + delivery_charge

    # ==========================================
    # Apply Coupon
    # ==========================================

    coupon_code = request.session.get(

        "coupon_code"

    )

    if coupon_code:

        if request.user.is_authenticated:

            coupon_user = request.user

        else:

            coupon_user = None

        coupon, error = validate_coupon(
            coupon_code,
            subtotal,
            coupon_user,
        )

        if coupon:

            discount = calculate_discount(

                coupon,

                subtotal,

            )

            final_total = subtotal - discount + delivery_charge

        else:

            request.session.pop(

                "coupon_code",

                None,

            )

            messages.error(

                request,

                error,

            )

    # ==========================================
    # Checkout Submit
    # ==========================================

    if request.method == "POST":

        form = OrderCreateForm(

            request.POST

        )

        if form.is_valid():

            # ==========================================
            # COD Feature Toggle
            # ==========================================

            payment_method = form.cleaned_data.get(

                "payment_method"

            )

            if (

                payment_method == "cod"

                and not feature_enabled("cod")

            ):

                messages.error(

                    request,

                    "Cash On Delivery is currently unavailable."

                )

                return redirect(

                    "cart:checkout"

                )
            
            if (
                payment_method == "emi"
                and not feature_enabled("emi")
                ):

                messages.error(
                    request,
                    "EMI payment is currently unavailable.",
                )

                return redirect(
                    "cart:checkout",
                )

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

                    return redirect(

                        "cart:cart_detail"

                    )

            # ==========================================
            # Database Transaction
            # ==========================================

            with transaction.atomic():
                # ==========================================
                # Create Order
                # ==========================================

                order = form.save(commit=False)

                if request.user.is_authenticated:

                    order.user = request.user

                else:

                    order.user = None

                order.coupon = coupon
                order.discount = discount
                order.delivery_charge = delivery_charge
                order.final_total = final_total

                order.save()

                # ==========================================
                # Order Items
                # ==========================================

                for item in cart:

                    OrderItem.objects.create(

                        order=order,

                        product=item["product"],

                        price=item["price"],

                        quantity=item["quantity"],

                    )

                # ==========================================
                # Cash On Delivery
                # ==========================================

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
                        user=request.user if request.user.is_authenticated else None,
                        note="Cash On Delivery order placed.",
                    )

                    reduce_order_stock(order)

                    if coupon:

                        if request.user.is_authenticated:

                            CouponUsage.objects.create(
                                coupon=coupon,
                                user=request.user,
                                order=order,
                            )

                        coupon.used_count = F("used_count") + 1

                        coupon.save(

                            update_fields=[

                                "used_count",

                            ]

                        )

            # ==========================================
            # Stripe
            # ==========================================

            if order.payment_method == "stripe":

                return redirect(

                    "payments:create_checkout_session",

                    order.id,

                )

            # ==========================================
            # COD
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
            # SSLCommerz
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
            "delivery_charge": delivery_charge,
            "final_total": final_total,

            "feature_enabled": {
                "coupon": feature_enabled("coupon"),
                "free_delivery": feature_enabled("free_delivery"),
                "cod": feature_enabled("cod"),
                "emi": feature_enabled("emi"),
            },
        },
    )


# ==========================================
# Apply Coupon
# ==========================================

def apply_coupon(request):

    if not feature_enabled("coupon"):

        messages.error(

            request,

            "Coupon system is currently disabled."

        )

        return redirect(

            "cart:checkout",

        )

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

    if not feature_enabled("coupon"):

        messages.error(

            request,

            "Coupon system is currently disabled."

        )

        return redirect(

            "cart:checkout",

        )

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

# ==========================================
# Buy Now
# ==========================================

def buy_now(request, product_id):

    cart = Cart(request)

    cart.clear()

    product = get_object_or_404(Product, id=product_id)

    if not can_purchase(product, 1):

        messages.error(
            request,
            f"{product.name} is out of stock."
        )

        return redirect(product.get_absolute_url())

    cart.add(product, quantity=1)

    return redirect("cart:checkout")