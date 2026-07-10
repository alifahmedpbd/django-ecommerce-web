from django import forms
from store.models import Category, Product, Brand, ProductImage


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
            "slug",
            "image",
            "description",
            "price",
            "stock",
            "available",
            "featured",

        ]

        widgets = {

            "category": forms.Select(attrs={"class": "form-select"}),
            "brand": forms.Select(attrs={"class": "form-select"}),
            "name": forms.TextInput(attrs={"class": "form-control","placeholder": "Product Name"}),
            "description": forms.Textarea(attrs={"class": "form-control", "rows": 5, "placeholder": "Product Description"}),
            "price": forms.NumberInput(attrs={"class": "form-control", "placeholder": "Price"}),
            "stock": forms.NumberInput(attrs={"class": "form-control", "placeholder": "Stock Quantity"}),
            "image": forms.ClearableFileInput(attrs={"class": "form-control"}),
            "available": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "featured": forms.CheckboxInput(attrs={"class": "form-check-input"}),

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