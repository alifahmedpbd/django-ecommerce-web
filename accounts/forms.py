from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User
from django.forms import ModelForm

class UserRegisterForm(UserCreationForm):
    class Meta:
        model = User
        fields = [
            "username",
            "email",
            "phone",
            "password1",
            "password2"
        ]

class UserUpdateForm(ModelForm):
    class Meta:
        model = User
        fields = [
            "first_name",
            "last_name",
            "email",
            "phone",
            "profile_image",
        ]

        widgets = {

            "first_name": forms.TextInput(

                attrs={

                    "class": "form-control",

                }

            ),

            "last_name": forms.TextInput(

                attrs={

                    "class": "form-control",

                }

            ),

            "email": forms.EmailInput(

                attrs={

                    "class": "form-control",

                }

            ),

            "phone": forms.TextInput(

                attrs={

                    "class": "form-control",

                    "placeholder": "+8801XXXXXXXXX",

                }

            ),

        }