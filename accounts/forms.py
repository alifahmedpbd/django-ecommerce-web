from django import forms
from django.contrib.auth.forms import UserCreationForm, SetPasswordForm
from django.forms import ModelForm

from .models import User


class UserRegisterForm(UserCreationForm):

    class Meta:
        model = User
        fields = [
            "username",
            "email",
            "phone",
            "password1",
            "password2",
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


class ForgotPasswordForm(forms.Form):

    email = forms.EmailField(

        widget=forms.EmailInput(

            attrs={
                "class": "form-control",
                "placeholder": "Enter your email",
            }

        )

    )


class OTPVerificationForm(forms.Form):

    otp = forms.CharField(

        max_length=6,

        widget=forms.TextInput(

            attrs={
                "class": "form-control",
                "placeholder": "Enter 6 digit OTP",
            }

        )

    )


class ResetPasswordForm(SetPasswordForm):

    new_password1 = forms.CharField(

        widget=forms.PasswordInput(

            attrs={
                "class": "form-control",
                "placeholder": "New Password",
            }

        )

    )

    new_password2 = forms.CharField(

        widget=forms.PasswordInput(

            attrs={
                "class": "form-control",
                "placeholder": "Confirm Password",
            }

        )

    )


class EmailOTPLoginForm(forms.Form):

    email = forms.EmailField(

        widget=forms.EmailInput(

            attrs={
                "class": "form-control",
                "placeholder": "Enter your email",
            }

        )

    )