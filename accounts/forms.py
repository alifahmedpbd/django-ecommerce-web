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
            "username",
            "email",
            "phone",
            "profile_image",
        ]