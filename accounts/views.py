from urllib import request

from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from .forms import UserRegisterForm
# Create your views here.

def register_view(request):
    if request.method == "POST":
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)

            messages.success(request, "Account Created Successfully!")
            return redirect("home")
    else:
        form = UserRegisterForm()
    return render(request, "accounts/register.html", {"form": form})

def login_view(request):

    if request.method == "POST":

        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)

        if user:
            login(request, user)

            return redirect("home")
        
        messages.error(request, "Invalid username or password.")

    return render(request, "accounts/login.html")

def logout_view(request):

    logout(request)
    return redirect("home")

