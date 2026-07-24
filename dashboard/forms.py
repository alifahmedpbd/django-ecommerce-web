from django import forms
from store.models import Category, Product, Brand, ProductImage
from orders.models import Coupon
from .models import Announcement

class CategoryForm(forms.ModelForm):

    class Meta:

        model = Category

        fields = [
            "name",
            "slug",
        ]

        widgets = {

            "name": forms.TextInput(attrs={"class": "form-control", "placeholder": "Category Name"}),
            "slug": forms.TextInput(attrs={"class": "form-control", "placeholder": "category-slug"}),

        }


class ProductForm(forms.ModelForm):

    class Meta:

        model = Product

        fields = [

            "category",

            "brand",

            "name",

            "image",

            "description",

            "price",

            "flash_price",

            "flash_end",

            "stock",

            "available",

            "featured",

            "is_flash_sale",

            "is_free_delivery",

            "is_trending",

            "is_new_arrival",

        ]

        widgets = {

            "description": forms.Textarea(

                attrs={

                    "rows": 5,

                }

            ),

            "flash_end": forms.DateTimeInput(

                attrs={

                    "type": "datetime-local",

                }

            ),

        }

# ==========================================
# Brand Form
# ==========================================

class BrandForm(forms.ModelForm):

    class Meta:

        model = Brand

        fields = [

            "name",

            "logo",

        ]

        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control", "placeholder": "Brand Name"}),
            "logo": forms.FileInput(attrs={"class": "form-control" }),

        }


# ==========================================
# Product Image Form
# ==========================================

class ProductImageForm(forms.ModelForm):

    class Meta:

        model = ProductImage

        fields = [

            "image",

        ]

        widgets = {
            "image": forms.FileInput(attrs={"class": "form-control"}),

        }



# ==========================================
# Coupon Form
# ==========================================

class CouponForm(forms.ModelForm):

    class Meta:

        model = Coupon

        fields = [

            "code",

            "discount_type",

            "discount",

            "minimum_purchase",

            "usage_limit",

            "active",

            "one_time_per_user",

            "valid_from",

            "valid_to",

        ]

        widgets = {

            "valid_from": forms.DateTimeInput(

                attrs={

                    "type": "datetime-local",

                    "class": "form-control",

                }

            ),

            "valid_to": forms.DateTimeInput(

                attrs={

                    "type": "datetime-local",

                    "class": "form-control",

                }

            ),

        }


class AnnouncementForm(forms.ModelForm):

    class Meta:

        model = Announcement

        fields = "__all__"