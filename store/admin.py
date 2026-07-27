from django.contrib import admin
from .models import Brand, Category, Product, Wishlist, Review, ProductImage


@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "slug",
        "created_at",
    )
    search_fields = (
        "name",
    )
    prepopulated_fields = {
        "slug": ("name",)
    }


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "slug",
    )
    search_fields = (
        "name",
    )
    prepopulated_fields = {
        "slug": ("name",)
    }


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "category",
        "brand",
        "price",
        "stock",
        "available",
        "featured",
        "created_at",
    )

    list_filter = (
        "available",
        "featured",
        "category",
        "brand",
    )

    search_fields = (
        "name",
        "description",
    )

    prepopulated_fields = {
        "slug": ("name",)
    }



class ProductImageInline(admin.TabularInline):

    model = ProductImage

    extra = 3



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


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = (
        "product",
        "user",
        "rating",
        "created_at",
    )

    list_filter = (
        "rating",
        "created_at",
    )

    search_fields = (
        "product__name",
        "user__username",
    )