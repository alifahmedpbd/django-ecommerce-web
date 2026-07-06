import stripe
from django.conf import settings
from django.urls import reverse

stripe.api_key = settings.STRIPE_SECRET_KEY

def create_stripe_checkout_session(request, order):

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
            reverse(
                "payments:payment_success", args=[order.id],
            )
        ) +"?session_id={CHECKOUT_SESSION_ID}",
        cancel_url=request.build_absolute_uri(
            reverse("payments:payment_cancel")
        ),

    )
    return session

def validate_stripe_payment(session_id):

    session = stripe.checkout.Session.retrieve(session_id)

    if session.payment_status != "paid":

        return None
    
    return session