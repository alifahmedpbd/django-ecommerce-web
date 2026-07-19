import os


def get_email_backend_config():
    sendgrid_api_key = os.getenv("SENDGRID_API_KEY") or os.getenv("EMAIL_HOST_PASSWORD")
    smtp_user = os.getenv("EMAIL_HOST_USER") or os.getenv("SENDGRID_USERNAME") or ""
    smtp_password = sendgrid_api_key or ""
    default_from = os.getenv("DEFAULT_FROM_EMAIL") or os.getenv("EMAIL_FROM") or "noreply@shopora.local"
    owner_email = os.getenv("OWNER_EMAIL") or default_from

    if sendgrid_api_key:
        return (
            "django.core.mail.backends.smtp.EmailBackend",
            "smtp.sendgrid.net",
            587,
            True,
            False,
            "apikey",
            smtp_password,
            default_from,
            owner_email,
        )

    if smtp_user and smtp_password:
        return (
            "django.core.mail.backends.smtp.EmailBackend",
            os.getenv("EMAIL_HOST", "smtp.gmail.com"),
            int(os.getenv("EMAIL_PORT", "587")),
            os.getenv("EMAIL_USE_TLS", "True").lower() == "true",
            os.getenv("EMAIL_USE_SSL", "False").lower() == "true",
            smtp_user,
            smtp_password,
            default_from,
            owner_email,
        )

    return (
        "django.core.mail.backends.console.EmailBackend",
        "",
        25,
        False,
        False,
        "",
        "",
        default_from,
        owner_email,
    )
