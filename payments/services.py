import stripe

from django.conf import settings
from django.db import transaction
from django.db.models import F

from orders.models import Order, OrderTimeline, CouponUsage
from orders.services import reduce_order_stock
from store.models import AbandonedCart


stripe.api_key = settings.STRIPE_SECRET_KEY


def create_stripe_checkout_session(request, order):
    """
    Create a Stripe Checkout Session that is permanently
    linked to the Shopora order.
    """

    amount_cents = int(order.final_total * 100)

    session = stripe.checkout.Session.create(
        payment_method_types=["card"],

        line_items=[
            {
                "price_data": {
                    "currency": "usd",

                    "product_data": {
                        "name": f"Shopora Order #{order.id}",
                    },

                    "unit_amount": amount_cents,
                },

                "quantity": 1,
            }
        ],

        mode="payment",

        client_reference_id=str(order.id),

        metadata={
            "order_id": str(order.id),
        },

        success_url=(
            request.build_absolute_uri(
                f"/payments/success/{order.id}/"
            )
            + "?session_id={CHECKOUT_SESSION_ID}"
        ),

        cancel_url=request.build_absolute_uri(
            "/payments/cancel/"
        ),
    )

    return session


def validate_stripe_payment(session_id, order):
    """
    Validate that the Stripe session belongs to this exact order
    and that the amount/currency/payment status are correct.
    """

    try:
        session = stripe.checkout.Session.retrieve(
            session_id
        )
    except stripe.error.StripeError:
        return None

    # Must be a successful payment
    if session.payment_status != "paid":
        return None

    # Stripe session must belong to this order
    metadata = session.get("metadata") or {}

    if metadata.get("order_id") != str(order.id):
        return None

    if session.get("client_reference_id") != str(order.id):
        return None

    # Currency must match
    if session.get("currency") != "usd":
        return None

    # Amount must exactly match Shopora order total
    expected_amount = int(order.final_total * 100)

    if session.get("amount_total") != expected_amount:
        return None

    return session


def mark_order_as_paid(order, session):
    """
    Atomically mark an order as paid.

    select_for_update() prevents two simultaneous requests
    from processing the same payment twice.
    """

    with transaction.atomic():

        order = (
            Order.objects
            .select_for_update()
            .select_related("coupon", "user")
            .prefetch_related("items__product")
            .get(pk=order.pk)
        )

        # Already processed
        if order.paid:
            return order, False

        payment_id = (
            session.get("payment_intent")
            or session.get("id")
        )

        order.payment_id = payment_id
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
            order=order,
            user=order.user,
            created_by="Stripe",
            note="Stripe payment completed successfully.",
        )

        reduce_order_stock(order)

        if order.coupon and order.user:

            CouponUsage.objects.get_or_create(
                coupon=order.coupon,
                user=order.user,
                order=order,
            )

            order.coupon.used_count = F("used_count") + 1

            order.coupon.save(
                update_fields=["used_count"]
            )

        if order.user:

            AbandonedCart.objects.filter(
                user=order.user,
                recovered=False,
            ).update(
                recovered=True
            )

        return order, True