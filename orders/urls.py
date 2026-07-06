from django.urls import path
from .import views

app_name = "orders"

urlpatterns = [
    path("success/<int:order_id>/", views.order_success, name="order_success"),
    path("my-orders/", views.order_list, name="order_list"),
    path("detail/<int:order_id>/", views.order_detail, name="order_detail"),
    path("invoice/<int:order_id>/", views.invoice_pdf, name="invoice_pdf"),
    path("cancel/<int:order_id>/", views.cancel_order, name="cancel_order"),

]