from .models import EmailOTP
from django.core.mail import send_mail
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


def send_otp_email(user, otp):
    try:
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
        return True

    except Exception as e:
        logger.exception(e)
        return False


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

    email_sent = send_otp_email(user, otp.otp)

    return otp, email_sent