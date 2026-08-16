import stripe

from django.conf import settings
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

from orders.models import Order

from .services import (
    validate_stripe_payment,
    mark_order_as_paid,
)


@csrf_exempt
def stripe_webhook(request):

    if request.method != "POST":

        return HttpResponse(
            status=405
        )

    payload = request.body

    signature = request.META.get(
        "HTTP_STRIPE_SIGNATURE"
    )

    if not signature:

        return HttpResponse(
            "Missing Stripe signature",
            status=400,
        )

    try:

        event = stripe.Webhook.construct_event(
            payload,
            signature,
            settings.STRIPE_WEBHOOK_SECRET,
        )

    except ValueError:

        return HttpResponse(
            "Invalid payload",
            status=400,
        )

    except stripe.error.SignatureVerificationError:

        return HttpResponse(
            "Invalid signature",
            status=400,
        )

    if event["type"] == "checkout.session.completed":

        session = event["data"]["object"]

        metadata = session.get(
            "metadata"
        ) or {}

        order_id = metadata.get(
            "order_id"
        )

        if not order_id:

            return HttpResponse(
                "Missing order ID",
                status=400,
            )

        try:

            order = Order.objects.get(
                id=order_id,
                payment_method="stripe",
            )

        except Order.DoesNotExist:

            return HttpResponse(
                "Order not found",
                status=404,
            )

        validated_session = (
            validate_stripe_payment(
                session["id"],
                order,
            )
        )

        if validated_session is None:

            return HttpResponse(
                "Payment validation failed",
                status=400,
            )

        mark_order_as_paid(
            order,
            validated_session,
        )

    return HttpResponse(
        status=200
    )