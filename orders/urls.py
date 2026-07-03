from django.urls import path
from .import views

app_name = "orders"

urlpatterns = [
    path("success/<int:order_id>/", views.order_success, name="order_success"),
    path("orders/", views.order_list, name="order_list"),
    path("<int:order_id>/", views.order_detail, name="order_detail"),

]