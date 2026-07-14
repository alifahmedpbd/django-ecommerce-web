from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags

from cart.cart import Cart

def clear_user_cart(request):
    cart = Cart(request)
    cart.clear()

def send_order_confirmation_email(request, order):

    if order.payment_method == "cod":

        template = "emails/cod_order_confirmation.html"

        subject = f"Cash on Delivery Order #{order.id} - Shopora"

    else:

        template = "emails/order_confirmation.html"

        subject = f"Order #{order.id} Confirmed - Shopora"

    html_message = render_to_string(

        template,

        {
            "order": order,
            "site_url": request.build_absolute_uri("/")[:-1],
        },

    )

    plain_message = strip_tags(html_message)

    email = EmailMultiAlternatives(

        subject=subject,

        body=plain_message,

        from_email=settings.DEFAULT_FROM_EMAIL,

        to=[order.email],

    )

    email.attach_alternative(

        html_message,

        "text/html",

    )

    email.send()


def send_order_status_email(request, order):

    templates = {

        "shipped": (

            "emails/shipped.html",

            f"Your Order #{order.id} Has Been Shipped",

        ),

        "delivered": (

            "emails/delivered.html",

            f"Order #{order.id} Delivered",

        ),

        "cancelled": (

            "emails/cancelled.html",

            f"Order #{order.id} Cancelled",

        ),

    }

    if order.status not in templates:

        return

    template, subject = templates[order.status]

    html_message = render_to_string(

        template,

        {

            "order": order,

            "site_url": request.build_absolute_uri("/")[:-1],

        },

    )

    plain = strip_tags(html_message)

    email = EmailMultiAlternatives(

        subject,

        plain,

        settings.DEFAULT_FROM_EMAIL,

        [order.email],

    )

    email.attach_alternative(

        html_message,

        "text/html",

    )

    email.send()       

def send_owner_new_order_email(request, order):

    html_message = render_to_string(
        "emails/new_order_owner.html",
        {
            "order": order,
            "site_url": request.build_absolute_uri("/")[:-1],
        },
    )

    plain_message = strip_tags(html_message)

    email = EmailMultiAlternatives(

        subject=f"🛒 New Order Received #{order.id}",

        body=plain_message,

        from_email=settings.DEFAULT_FROM_EMAIL,

        to=[settings.DEFAULT_FROM_EMAIL],

    )

    email.attach_alternative(

        html_message,

        "text/html",

    )

    email.send()