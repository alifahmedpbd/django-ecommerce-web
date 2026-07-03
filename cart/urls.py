from django.urls import path
from . import views

app_name = "cart"

urlpatterns = [
    path("add/<int:product_id>/", views.cart_add, name="cart_add"),

    path("detail/", views.cart_detail, name="cart_detail"),

    path("remove/<int:product_id>/", views.cart_remove, name="cart_remove"),

    path("update/<int:product_id>/<str:action>/", views.cart_update, name="cart_update"),

    path("checkout/", views.checkout, name="checkout"),

    # Stripe Checkout
    path("create-checkout-session/<int:order_id>/", views.create_checkout_session, name="create_checkout_session"),
    path("payment-success/<int:order_id>/", views.payment_success, name="payment_success",
),
]