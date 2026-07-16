from django.shortcuts import render, redirect, get_object_or_404
from orders.models import Order, OrderTimeline, CouponUsage
from .utils import clear_user_cart, send_order_confirmation_email, send_owner_new_order_email

from django.conf import settings

import stripe

stripe.api_key = settings.STRIPE_SECRET_KEY

from .services import (
    create_stripe_checkout_session,
    validate_stripe_payment,
)

from orders.services import reduce_order_stock
from django.db.models import F
from django.db import transaction


def create_checkout_session(request, order_id):

    order = get_object_or_404(
        Order.objects.select_related(
            "user",
            "coupon",
        ).prefetch_related(
            "items__product",
        ),
        id=order_id,
    )

    session = create_stripe_checkout_session(
        request,
        order,
    )

    return redirect(session.url)


def payment_success(request, order_id):

    order = get_object_or_404(
        Order.objects.select_related(
            "user",
            "coupon",
        ).prefetch_related(
            "items__product",
        ),
        id=order_id,
    )

    session_id = request.GET.get("session_id")

    if not session_id:

        return redirect(
            "payments:payment_cancel"
        )

    session = validate_stripe_payment(
        session_id
    )

    if session is None:

        return redirect(
            "payments:payment_cancel"
        )

    # ==========================================
    # Prevent duplicate payment
    # ==========================================

    if order.paid:

        return redirect(
            "orders:order_success",
            order.id,
        )

    # ==========================================
    # Save payment info
    # ==========================================

    with transaction.atomic():
        order.payment_id = (
            session.payment_intent
            or
            session.id
        )

        order.paid = True

        order.payment_status = "paid"

        order.status = "processing"

        order.save(
            update_fields=[
                "payment_id",
                "paid",
                "payment_status",
                "status",
            ]
        )
    

        OrderTimeline.objects.create(
            order=order, user=order.user, note="Stripe payment completed successfully."
        )

    # ==========================================
    # Reduce Stock
    # ==========================================


        reduce_order_stock(order)

    # ==========================================
    # Coupon Consume
    # ==========================================

        if order.coupon:

        

            CouponUsage.objects.create(

                coupon=order.coupon,

                user=order.user,

                order=order,

            )

            order.coupon.used_count = F("used_count") + 1
            order.coupon.save(update_fields=["used_count"])

    # ==========================================
    # Clear Coupon Session
    # ==========================================

    request.session.pop(
        "coupon_code",
        None,
    )

    # ==========================================
    # Clear Cart
    # ==========================================

    clear_user_cart(request)

    # ==========================================
    # Send Email
    # ==========================================

    send_order_confirmation_email(
        request,
        order,
    )

    send_owner_new_order_email(
        request,
        order,
    )

    return redirect(
        "orders:order_success",
        order.id,
    )


def payment_cancel(request):

    return render(
        request,
        "payments/cancel.html",
    )