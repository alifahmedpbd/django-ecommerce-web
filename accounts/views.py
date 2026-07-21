from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from .forms import UserRegisterForm, UserUpdateForm
from django.contrib.auth.decorators import login_required
from orders.models import Order
from store.models import Wishlist, Review
from .models import EmailOTP, User
from .utils import  create_and_send_otp
from .forms import ForgotPasswordForm, OTPVerificationForm, ResetPasswordForm, EmailOTPLoginForm
from payments.utils import send_owner_new_customer_email
from django.conf import settings

# Create your views here.

def register_view(request):

    if request.method == "POST":

        form = UserRegisterForm(request.POST)

        if form.is_valid():

            user = form.save(commit=False)

            # Localhost -> OTP required
            if settings.DEBUG:
                user.is_active = False
            else:
                # Render demo
                user.is_active = True

            user.save()

            if settings.DEBUG:

                try:
                    create_and_send_otp(
                        user=user,
                        purpose="verify",
                    )
                except Exception as e:
                    print("OTP Error:", e)

                try:
                    send_owner_new_customer_email(request, user)
                except Exception as e:
                    print("Owner Mail Error:", e)

                request.session["verify_email"] = user.email

                messages.success(
                    request,
                    "Verification code has been sent to your email.",
                )

                return redirect("accounts:verify_email")

            # Render
            messages.success(
                request,
                "Registration completed successfully. Please login.",
            )

            return redirect("accounts:login")

    else:

        form = UserRegisterForm()

    return render(
        request,
        "accounts/register.html",
        {
            "form": form,
        },
    )

def verify_email_view(request):

    email = request.session.get("verify_email")

    if not email:
        messages.error(request, "Verification session expired.")
        return redirect("accounts:register")

    user = get_object_or_404(
        User.objects.only(
            "id",
            "email",
            "is_active",
        ),
        email=email,
    )

    if request.method == "POST":

        otp_code = request.POST.get("otp")

        try:

            otp = EmailOTP.objects.filter(
                user=user,
                purpose="verify",
                is_verified=False,
            ).latest("created_at")

        except EmailOTP.DoesNotExist:

            messages.error(request, "OTP not found.")
            return redirect("accounts:verify_email")

        if otp.is_expired():

            otp.delete()

            messages.error(request, "OTP expired.")

            return redirect("accounts:verify_email")

        if otp.otp != otp_code:

            messages.error(request, "Invalid OTP.")

            return redirect("accounts:verify_email")

        otp.is_verified = True
        otp.save(update_fields=["is_verified"])

        user.is_active = True
        user.save(update_fields=["is_active"])

        request.session.pop("verify_email", None)

        messages.success(
            request,
            "Email verified successfully. Please login.",
        )

        return redirect("accounts:login")

    return render(
        request,
        "accounts/verify_email.html",
    )
def resend_otp_view(request):

    email = request.session.get("verify_email")

    if not email:

        messages.error(request, "Verification session expired.")

        return redirect("accounts:register")

    user = get_object_or_404(
        User,
        email=email,
    )

    create_and_send_otp(
        user=user,
        purpose="verify",
    )

    messages.success(
        request,
        "New OTP sent successfully.",
    )

    return redirect("accounts:verify_email")


def email_login_view(request):

    if request.method == "POST":

        form = EmailOTPLoginForm(request.POST)

        if form.is_valid():

            email = form.cleaned_data["email"]

            try:

                user = User.objects.only(
                        "id",
                        "email",
                        "is_active",
                    ).get(email=email)

            except User.DoesNotExist:

                messages.error(request, "No account found.")

                return redirect("accounts:email_login")

            if not user.is_active:

                messages.error(
                    request,
                    "Please verify your account first.",
                )

                return redirect("accounts:login")

            create_and_send_otp(
                user=user,
                purpose="login",
            )

            request.session["login_user_id"] = user.id

            messages.success(
                request,
                "OTP sent to your email.",
            )

            return redirect("accounts:verify_login_otp")

    else:

        form = EmailOTPLoginForm()

    return render(
        request,
        "accounts/email_login.html",
        {
            "form": form,
        },
    )



def verify_login_otp_view(request):

    user_id = request.session.get("login_user_id")

    if not user_id:
        return redirect("accounts:email_login")

    user = get_object_or_404(
        User.objects.only(
            "id",
            "email",
            "password",
            "is_active",
        ),
        id=user_id,
    )

    if request.method == "POST":

        otp_code = request.POST.get("otp")

        try:

            email_otp = EmailOTP.objects.get(
                user=user,
                purpose="login",
                otp=otp_code,
                is_verified=False,
            )

        except EmailOTP.DoesNotExist:

            messages.error(request, "Invalid OTP.")

            return redirect("accounts:verify_login_otp")

        if email_otp.is_expired():

            email_otp.delete()

            messages.error(request, "OTP expired.")

            return redirect("accounts:email_login")

        email_otp.is_verified = True
        email_otp.save()

        login(request, user)

        EmailOTP.objects.filter(
            user=user,
            purpose="login",
        ).delete()

        request.session.pop("login_user_id", None)

        messages.success(
            request,
            "Login successful.",
        )

        return redirect("home")

    return render(
        request,
        "accounts/verify_login_otp.html",
    )

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



def forgot_password_view(request):

    if request.method == "POST":

        form = ForgotPasswordForm(request.POST)

        if form.is_valid():

            email = form.cleaned_data["email"]

            try:

                user = User.objects.only(
                    "id",
                    "email",
                ).get(email=email)

            except User.DoesNotExist:

                messages.error(
                    request,
                    "No account found with this email.",
                )

                return redirect("accounts:forgot_password")

            if settings.DEBUG:

                try:
                    create_and_send_otp(
                        user=user,
                        purpose="reset",
                    )
                except Exception as e:
                    print("OTP Error:", e)

                request.session["reset_user_id"] = user.id

                messages.success(
                    request,
                    "OTP has been sent to your email.",
                )

                return redirect("accounts:verify_reset_otp")

            # Render (OTP skip)
            request.session["reset_user_id"] = user.id

            messages.info(
                request,
                "OTP verification is disabled on demo server. Please set a new password.",
            )

            return redirect("accounts:reset_password")

    else:

        form = ForgotPasswordForm()

    return render(
        request,
        "accounts/forgot_password.html",
        {
            "form": form,
        },
    )


def verify_reset_otp_view(request):

    user_id = request.session.get("reset_user_id")

    if not user_id:
        return redirect("accounts:forgot_password")

    user = get_object_or_404(
        User.objects.only(
            "id",
            "email",
        ),
        id=user_id,
    )

    if request.method == "POST":

        form = OTPVerificationForm(request.POST)

        if form.is_valid():

            otp_code = form.cleaned_data["otp"]

            try:

                otp = EmailOTP.objects.filter(
                    user=user,
                    purpose="reset",
                    is_verified=False,
                ).latest("created_at")

            except EmailOTP.DoesNotExist:

                messages.error(
                    request,
                    "OTP not found.",
                )

                return redirect("accounts:forgot_password")

            if otp.is_expired():

                otp.delete()

                messages.error(
                    request,
                    "OTP expired.",
                )

                return redirect("accounts:forgot_password")

            if otp.otp != otp_code:

                messages.error(
                    request,
                    "Invalid OTP.",
                )

                return redirect("accounts:verify_reset_otp")

            otp.is_verified = True
            otp.save(update_fields=["is_verified"])

            request.session["reset_verified"] = True

            messages.success(
                request,
                "OTP verified successfully.",
            )

            return redirect("accounts:reset_password")

    else:

        form = OTPVerificationForm()

    return render(
        request,
        "accounts/verify_reset_otp.html",
        {
            "form": form,
        },
    )
def reset_password_view(request):

    user_id = request.session.get("reset_user_id")
    verified = request.session.get("reset_verified")

    if not user_id or not verified:
        return redirect("accounts:forgot_password")

    user = get_object_or_404(
        User.objects.only(
            "id",
            "password",
        ),
        id=user_id,
    )

    if request.method == "POST":

        form = ResetPasswordForm(user, request.POST)

        if form.is_valid():

            form.save()

            EmailOTP.objects.filter(
                user=user,
                purpose="reset",
            ).delete()

            request.session.pop("reset_user_id", None)
            request.session.pop("reset_verified", None)

            messages.success(
                request,
                "Password changed successfully. Please login.",
            )

            return redirect("accounts:login")

    else:

        form = ResetPasswordForm(user)

    return render(
        request,
        "accounts/reset_password.html",
        {
            "form": form,
        },
    )

    

@login_required
def profile_view(request):

    total_orders = Order.objects.filter(user=request.user).count()

    completed_orders = Order.objects.filter(user=request.user, status="delivered",).count()

    wishlist_count = Wishlist.objects.filter(user=request.user,).count()

    review_count = Review.objects.filter(user=request.user,).count()

    recent_orders = (
        Order.objects
        .filter(user=request.user)
        .only(
            "id",
            "status",
            "final_total",
            "created_at",
            "payment_method",
        )
        .order_by("-created_at")[:5]
    )

    recent_reviews = Review.objects.filter(user=request.user,).select_related("product").only(
        "rating",
        "comment",
        "created_at",
        "product__id",
        "product__name",
        "product__slug",
    ).order_by("-created_at")[:3]

    wishlist_items = Wishlist.objects.filter(user=request.user,).select_related("product").only(
        "created_at",
        "product__id",
        "product__name",
        "product__price",
        "product__slug",
        "product__image",
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
