from django.urls import path
from . import views

app_name = "accounts"

urlpatterns = [

    # Authentication
    path(
        "register/",
        views.register_view,
        name="register",
    ),

    path(
        "verify-email/",
        views.verify_email_view,
        name="verify_email",
    ),

    path(
        "resend-otp/",
        views.resend_otp_view,
        name="resend_otp",
    ),

    path(
        "login/",
        views.login_view,
        name="login",
    ),

    path(
        "email-login/",
        views.email_login_view,
        name="email_login",
    ),

    path(
        "verify-login-otp/",
        views.verify_login_otp_view,
        name="verify_login_otp",
    ),

    path(
        "logout/",
        views.logout_view,
        name="logout",
    ),

    # Password Reset
    path(
        "forgot-password/",
        views.forgot_password_view,
        name="forgot_password",
    ),

    path(
        "verify-reset-otp/",
        views.verify_reset_otp_view,
        name="verify_reset_otp",
    ),

    path(
        "reset-password/",
        views.reset_password_view,
        name="reset_password",
    ),

    # Profile
    path(
        "profile/",
        views.profile_view,
        name="profile",
    ),

]