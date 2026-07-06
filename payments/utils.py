from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags

from cart.cart import Cart

def clear_user_cart(request):
    cart = Cart(request)
    cart.clear()

def send_order_confirmation_email(request, order):

    html_message = render_to_string(
        "emails/order_confirmation.html",

        {
            "order": order,
            "site_url": request.build_absolute_uri("/")[:-1],
        },
    )

    plain_message = strip_tags(html_message)

    email = EmailMultiAlternatives(

        subject=f"Order #{order.id} Confirmed - Shopora",

        body=plain_message,

        from_email=settings.DEFAULT_FROM_EMAIL,

        to=[order.email],
    )

    email.attach_alternative(

        html_message,

        "text/html",

    )

    email.send()

        