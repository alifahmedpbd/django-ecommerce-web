from django.shortcuts import render, redirect, get_object_or_404
from django.db import transaction

from orders.models import Order

from .services import (
    create_stripe_checkout_session,
    validate_stripe_payment,
    mark_order_as_paid,
)

from .utils import (
    clear_user_cart,
    send_order_confirmation_email,
    send_owner_new_order_email,
)


def _can_access_order(request, order):
    """
    Allow:
    - Order owner
    - Owner/staff dashboard users
    - Guest checkout using the current session
    """

    if request.user.is_authenticated:

        if order.user_id == request.user.id:
            return True

        if (
            request.user.is_superuser
            or request.user.role in ("owner", "staff")
        ):
            return True

        return False

    # Guest checkout protection
    return (
        request.session.get("pending_order_id")
        == order.id
    )


def create_checkout_session(request, order_id):

    order = get_object_or_404(
        Order.objects.select_related(
            "user",
            "coupon",
        ),
        id=order_id,
    )

    if not _can_access_order(request, order):

        return redirect("home")

    if order.payment_method != "stripe":

        return redirect(
            "orders:order_detail",
            order.id,
        )

    if order.paid:

        return redirect(
            "orders:order_success",
            order.id,
        )

    session = create_stripe_checkout_session(
        request,
        order,
    )

    # Remember guest checkout order
    request.session["pending_order_id"] = order.id

    return redirect(session.url)


def payment_success(request, order_id):

    order = get_object_or_404(
        Order.objects.select_related(
            "user",
            "coupon",
        ),
        id=order_id,
    )

    if not _can_access_order(request, order):

        return redirect("home")

    session_id = request.GET.get("session_id")

    if not session_id:

        return redirect(
            "payments:payment_cancel"
        )

    session = validate_stripe_payment(
        session_id,
        order,
    )

    if session is None:

        return redirect(
            "payments:payment_cancel"
        )

    order, newly_paid = mark_order_as_paid(
        order,
        session,
    )

    # Only send emails once
    if newly_paid:

        try:
            send_order_confirmation_email(
                request,
                order,
            )

            send_owner_new_order_email(
                request,
                order,
            )

        except Exception:
            # Payment must remain successful
            # even if email fails.
            pass

    request.session.pop(
        "pending_order_id",
        None,
    )

    request.session.pop(
        "coupon_code",
        None,
    )

    clear_user_cart(request)

    return redirect(
        "orders:order_success",
        order.id,
    )


def payment_cancel(request):

    return render(
        request,
        "payments/cancel.html",
    )