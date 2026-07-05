from django.contrib import admin
from .models import Category, Product, Wishlist
# Register your models here.

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "slug",
    )
    prepopulated_fields = {"slug": ("name",)}

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "price",
        "stock",
        "available",
        "created_at",
    )
    list_filter = (
        "available",
        "category",
    )
    search_fields = (
        "name",
        "description",
    )
    prepopulated_fields = {"slug": ("name",)}

@admin.register(Wishlist)
class WishlistAdmin(admin.ModelAdmin):

    list_display = (
        "user",
        "product",
        "created_at",
    )

    search_fields = (
        "user__username",
        "product__name",
    )