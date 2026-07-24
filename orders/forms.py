from django import forms
from .models import Order

from dashboard.helpers import feature_enabled


class OrderCreateForm(forms.ModelForm):

    class Meta:

        model = Order

        fields = [

            "full_name",

            "email",

            "phone",

            "address",

            "payment_method",

            "emi_months",

        ]

        widgets = {

            "full_name": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Full Name",
                }
            ),

            "email": forms.EmailInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Email",
                }
            ),

            "phone": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Phone Number",
                }
            ),

            "address": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 4,
                    "placeholder": "Shipping Address",
                }
            ),

        }

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)

        payment = self.fields["payment_method"]

        choices = list(payment.choices)

        if not feature_enabled("cod"):

            choices = [

                c

                for c in choices

                if c[0] != "cod"

            ]

        if not feature_enabled("emi"):

            choices = [

                c

                for c in choices

                if c[0] != "emi"

            ]

        payment.choices = choices


class GuestOrderTrackingForm(forms.Form):

    order_id = forms.IntegerField(
        label="Order ID",
        widget=forms.NumberInput(
            attrs={
                "class": "form-control",
                "placeholder": "Enter Order ID",
            }
        ),
    )

    email = forms.EmailField(
        label="Email",
        widget=forms.EmailInput(
            attrs={
                "class": "form-control",
                "placeholder": "Enter Order Email",
            }
        ),
    )