from django import forms
from store.models import Category, Product, Brand, ProductImage
from orders.models import Coupon
from .models import Announcement, EmailCampaign, EmailCampaignLog

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

        widgets = {"description": forms.Textarea(

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
# Product Gallery Form
# ==========================================

class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True


class ProductGalleryForm(forms.Form):

    images = forms.FileField(
        required=False,
        widget=MultipleFileInput(
            attrs={
                "multiple": True,
                "class": "form-control",
                "accept": "image/*",
            }
        ),
    )

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

class EmailCampaignForm(forms.ModelForm):

    class Meta:

        model = EmailCampaign

        fields = [
            "title",
            "subject",
            "target",
            "message",
        ]

        widgets = {

            "title": forms.TextInput(

                attrs={

                    "class": "form-control",

                    "placeholder": "Campaign Name",

                }

            ),

            "subject": forms.TextInput(

                attrs={

                    "class": "form-control",

                    "placeholder": "Email Subject",

                }

            ),

            "target": forms.Select(

                attrs={

                    "class": "form-select",

                }

            ),

            "message": forms.Textarea(

                attrs={

                    "class": "form-control",

                    "rows": 12,

                    "placeholder": "Write your email message...",

                }

            ),

        }

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)

        for name, field in self.fields.items():

            if name == "target":

                field.widget.attrs["class"] = "form-select"

            else:

                field.widget.attrs["class"] = "form-control"

        self.fields["message"].widget.attrs["rows"] = 12

