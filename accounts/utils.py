from django.conf import settings
from django.core.mail import send_mail
from .models import EmailOTP


def send_otp_email(user, otp):
    """
    Localhost (DEBUG=True) -> Gmail SMTP
    Render (DEBUG=False) -> Skip email
    """

    # Production (Render) এ কোনো email পাঠাবে না
    if not settings.DEBUG:
        print("Email sending skipped (Production).")
        return

    subject = "Shopora Email Verification"

    message = f"""
Hello {user.get_full_name() or user.username},

Your verification code is:

{otp}

This OTP will expire in 10 minutes.

Thanks,
Shopora
"""

    send_mail(
        subject=subject,
        message=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        fail_silently=False,
    )


def create_and_send_otp(user, purpose):

    EmailOTP.objects.filter(
        user=user,
        purpose=purpose,
        is_verified=False,
    ).delete()

    otp = EmailOTP.objects.create(
        user=user,
        purpose=purpose,
    )

    otp.generate_otp()

    try:
        send_otp_email(
            user=user,
            otp=otp.otp,
        )
    except Exception as e:
        print("OTP Email Error:", e)

    return otp