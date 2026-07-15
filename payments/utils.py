from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.db.models import F
from cart.cart import Cart
from django.contrib.auth import get_user_model
User = get_user_model()



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

def send_shipping_email(request, order):

    html_message = render_to_string(

        "emails/shipped.html",

        {

            "order": order,

            "site_url": request.build_absolute_uri("/")[:-1],

        },

    )

    plain_message = strip_tags(html_message)

    email = EmailMultiAlternatives(

        subject=f"Your Order #{order.id} Has Been Shipped 🚚",

        body=plain_message,

        from_email=settings.DEFAULT_FROM_EMAIL,

        to=[order.email],

    )

    email.attach_alternative(

        html_message,

        "text/html",

    )

    email.send()

def send_delivered_email(request, order):

    html_message = render_to_string(

        "emails/delivered.html",

        {

            "order": order,

            "site_url": request.build_absolute_uri("/")[:-1],

        },

    )

    plain_message = strip_tags(html_message)

    email = EmailMultiAlternatives(

        subject=f"Order #{order.id} Delivered 🎉",

        body=plain_message,

        from_email=settings.DEFAULT_FROM_EMAIL,

        to=[order.email],

    )

    email.attach_alternative(

        html_message,

        "text/html",

    )

    email.send()


def send_cancelled_email(request, order):

    html_message = render_to_string(

        "emails/cancelled.html",

        {

            "order": order,

            "site_url": request.build_absolute_uri("/")[:-1],

        },

    )

    plain_message = strip_tags(html_message)

    email = EmailMultiAlternatives(

        subject=f"Order #{order.id} Cancelled",

        body=plain_message,

        from_email=settings.DEFAULT_FROM_EMAIL,

        to=[order.email],

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

        to=[settings.OWNER_EMAIL],

    )

    email.attach_alternative(

        html_message,

        "text/html",

    )

    email.send()


def send_low_stock_email(product):


    if product.stock > 5:
        return

    html_message = render_to_string(
        "emails/low_stock.html",
        {
            "product": product,
        },
    )

    plain_message = strip_tags(html_message)


    email = EmailMultiAlternatives(
        subject=f"⚠ Low Stock Alert - {product.name}",
        body=plain_message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[settings.OWNER_EMAIL],
    )

    email.attach_alternative(
        html_message,
        "text/html",
    )


    email.send(fail_silently=False)

 
def send_owner_new_customer_email(request, user):

    html_message = render_to_string(
        "emails/new_customer.html",
        {
            "user": user,
            "site_url": request.build_absolute_uri("/")[:-1],
        },
    )

    plain_message = strip_tags(html_message)

    email = EmailMultiAlternatives(
        subject=f"🎉 New Customer Registered - {user.get_full_name() or user.username}",
        body=plain_message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[settings.OWNER_EMAIL],
    )

    email.attach_alternative(
        html_message,
        "text/html",
    )

    email.send() 

