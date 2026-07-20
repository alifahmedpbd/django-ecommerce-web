import os


def str_to_bool(value):
    return str(value).strip().lower() in ("1", "true", "yes", "y")


def get_email_backend_config():
    backend = os.getenv(
        "EMAIL_BACKEND",
        "django.core.mail.backends.smtp.EmailBackend",
    )
    host = os.getenv("EMAIL_HOST", "smtp.gmail.com")
    port = int(os.getenv("EMAIL_PORT", 587))
    use_tls = str_to_bool(os.getenv("EMAIL_USE_TLS", "True"))
    use_ssl = str_to_bool(os.getenv("EMAIL_USE_SSL", "False"))

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

    if backend == "django.core.mail.backends.smtp.EmailBackend" and not (
        smtp_user and smtp_password
    ):
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

    return (
        backend,
        host,
        port,
        use_tls,
        use_ssl,
        smtp_user,
        smtp_password,
        default_from,
        owner_email,
    )
