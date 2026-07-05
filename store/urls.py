from django.urls import path

from . import views


app_name = "store"

urlpatterns = [

    path("products/", views.product_list, name="product_list"),
    path("category/<slug:category_slug>/", views.product_list, name="products_by_category"),
    path("products/<slug:slug>/", views.product_detail, name="product_detail"),
    path("wishlist/add/<int:product_id>/", views.add_to_wishlist, name="add_to_wishlist"),
    path("wishlist/remove/<int:product_id>/", views.remove_from_wishlist, name="remove_from_wishlist"),
    path("wishlist/", views.wishlist, name="wishlist"),
]