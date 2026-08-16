from django.conf import settings
from django.core.mail import send_mail

from .models import EmailOTP


def send_otp_email(user, otp):

    subject = "Shopora Verification Code"

    message = f"""
Hello {user.get_full_name() or user.username},

Your Shopora verification code is:

{otp}

This OTP will expire in 5 minutes.

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

    send_otp_email(
        user=user,
        otp=otp.otp,
    )

    return otp