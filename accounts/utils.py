from .models import EmailOTP
from django.core.mail import send_mail
from django.conf import settings


def send_otp_email(user, otp):

    send_mail(
        subject="Shopora Verification Code",
        message=f"""
Hello {user.username},

Your OTP is:

{otp}

It expires in 5 minutes.

Shopora
Smart Shopping, Simplified.
""",
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

    send_otp_email(user, otp.otp)

    return otp