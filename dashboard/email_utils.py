from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string


def send_campaign_email(
    campaign,
    customer,
):
    """
    Send professional HTML campaign email.
    """

    context = {
        "customer": customer,
        "campaign": campaign,
        "subject": campaign.subject,
        "message": campaign.message,
        "shop_name": getattr(settings, "SHOP_NAME", "Shopora"),
        "shop_email": getattr(settings, "DEFAULT_FROM_EMAIL", ""),
        "shop_url": getattr(settings, "SHOP_URL", "http://127.0.0.1:8000"),
        "facebook": getattr(settings, "FACEBOOK_URL", ""),
        "instagram": getattr(settings, "INSTAGRAM_URL", ""),
        "youtube": getattr(settings, "YOUTUBE_URL", ""),
    }

    html_message = render_to_string(
        "dashboard/emails/campaign_email.html",
        context,
    )

    email = EmailMultiAlternatives(
        subject=campaign.subject,
        body=campaign.message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[customer.email],
    )

    email.attach_alternative(
        html_message,
        "text/html",
    )

    email.send(
        fail_silently=False,
    )