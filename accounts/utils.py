import requests
from django.conf import settings
from .models import EmailOTP


def send_brevo_email(to_email, subject, html):

    sender_email = settings.DEFAULT_FROM_EMAIL

    if "<" in sender_email:
        sender_name = sender_email.split("<")[0].strip()
        sender_email = sender_email.split("<")[1].replace(">", "").strip()
    else:
        sender_name = "Shopora"

    headers = {
        "accept": "application/json",
        "api-key": settings.BREVO_API_KEY,
        "content-type": "application/json",
    }

    payload = {
        "sender": {
            "name": sender_name,
            "email": sender_email,
        },
        "to": [
            {
                "email": to_email
            }
        ],
        "subject": subject,
        "htmlContent": html,
    }

    response = requests.post(
        "https://api.brevo.com/v3/smtp/email",
        json=payload,
        headers=headers,
        timeout=20,
    )

    response.raise_for_status()


def send_otp_email(user, otp):

    html = f"""
    <h2>Verify Your Email</h2>

    <p>Your OTP:</p>

    <h1>{otp}</h1>

    <p>Expires in 10 minutes.</p>
    """

    send_brevo_email(
        user.email,
        "Shopora Email Verification",
        html,
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