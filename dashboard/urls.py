from django.urls import path
from . import views

app_name = "dashboard"

urlpatterns = [

    path("", views.dashboard_home, name="home"),

    path("reports/", views.reports, name="reports"),

    path("reports/pdf/", views.sales_report_pdf, name="sales_report_pdf"),

    path("reports/excel/", views.sales_report_excel, name="sales_report_excel"),

    # Categories
    path("categories/", views.category_list, name="category_list"),
    path("categories/add/", views.category_create, name="category_add"),
    path("categories/<int:pk>/edit/", views.category_update, name="category_edit"),
    path("categories/<int:pk>/delete/", views.category_delete, name="category_delete"),

    # ==========================================
    # Product
    # ==========================================
    path("products/", views.product_list, name="product_list"),
    path("products/create/", views.product_create, name="product_create"),
    path("products/<int:pk>/update/", views.product_update, name="product_update"),
    path("products/<int:pk>/delete/", views.product_delete, name="product_delete"),


    # ==========================================
    # Product Gallery
    # ==========================================

    path("products/<int:pk>/gallery/", views.product_gallery, name="product_gallery"),
    path("products/<int:pk>/gallery/add/", views.product_image_create, name="product_image_create"),
    path("gallery/<int:pk>/delete/", views.product_image_delete, name="product_image_delete"),


    # ==========================
    # Brand
    # ==========================
    path("brands/", views.brand_list, name="brand_list"),
    path("brands/create/", views.brand_create, name="brand_create"),
    path("brands/<int:pk>/update/", views.brand_update, name="brand_update"),
    path("brands/<int:pk>/delete/", views.brand_delete, name="brand_delete"),


    # ==========================
    # Coupon
    # ==========================
    path("coupons/", views.coupon_list, name="coupon_list"),
    path("coupons/add/", views.coupon_add, name="coupon_add"),
    path("coupons/<int:pk>/edit/", views.coupon_edit, name="coupon_edit"),
    path("coupons/<int:pk>/delete/", views.coupon_delete, name="coupon_delete"),

    path("orders/<int:order_id>/", views.dashboard_order_detail, name="dashboard_order_detail"),
    path("orders/", views.dashboard_orders, name="dashboard_orders"),

    path("reports/low-stock/", views.low_stock_report, name="low_stock_report"),

    path("reports/low-stock/pdf/", views.low_stock_report_pdf, name="low_stock_report_pdf"),

    path("reports/low-stock/excel/", views.low_stock_report_excel, name="low_stock_report_excel"),

    path("customers/", views.dashboard_customers, name="dashboard_customers"),
    path("customers/<int:user_id>/", views.dashboard_customer_detail, name="dashboard_customer_detail"),

]