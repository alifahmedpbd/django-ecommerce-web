import os


def get_email_backend_config():
    smtp_user = os.getenv("EMAIL_HOST_USER", "")
    smtp_password = os.getenv("EMAIL_HOST_PASSWORD", "")

    default_from = os.getenv(
        "DEFAULT_FROM_EMAIL",
        f"Shopora <{smtp_user}>",
    )

    owner_email = os.getenv(
        "OWNER_EMAIL",
        smtp_user,
    )

    if smtp_user and smtp_password:
        return (
            "django.core.mail.backends.smtp.EmailBackend",
            "smtp.gmail.com",
            587,
            True,
            False,
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