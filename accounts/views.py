from urllib import request
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from .forms import UserRegisterForm, UserUpdateForm
from django.contrib.auth.decorators import login_required
from orders.models import Order
from store.models import Wishlist, Review
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

@login_required
def profile_view(request):

    total_orders = Order.objects.filter(user=request.user).count()

    completed_orders = Order.objects.filter(user=request.user, status="delivered",).count()

    wishlist_count = Wishlist.objects.filter(user=request.user,).count()

    review_count = Review.objects.filter(user=request.user,).count()

    recent_orders = Order.objects.filter(user=request.user,).order_by("-created_at")[:5]

    recent_reviews = Review.objects.filter(user=request.user,).select_related(
        "product",
    ).order_by("-created_at")[:3]

    wishlist_items = Wishlist.objects.filter(user=request.user,).select_related(
        "product",
    ).order_by("-created_at")[:3]


    if request.method == "POST":

        form = UserUpdateForm(request.POST, request.FILES, instance=request.user)

        if form.is_valid():

            form.save()

            messages.success(request, "Profile Updated Successfully.")

            return redirect("accounts:profile")

    else:

        form = UserUpdateForm(instance=request.user)
    
    context = {
        "form": form,

        "total_orders": total_orders,

        "completed_orders": completed_orders,

        "wishlist_count": wishlist_count,

        "review_count": review_count,

        "recent_orders": recent_orders,

        "recent_reviews": recent_reviews,

        "wishlist_items": wishlist_items,
    }

    return render(request, "accounts/profile.html", context,)
