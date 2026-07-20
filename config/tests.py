import os
from unittest.mock import patch

from django.test import SimpleTestCase

from .email_config import get_email_backend_config


class EmailConfigTests(SimpleTestCase):

    @patch.dict(os.environ, {}, clear=True)
    def test_console_backend(self):

        backend, host, port, tls, ssl, user, password, default_from, owner = get_email_backend_config()

        self.assertEqual(
            backend,
            "django.core.mail.backends.console.EmailBackend",
        )

    @patch.dict(
        os.environ,
        {
            "EMAIL_HOST_USER": "shopora@gmail.com",
            "EMAIL_HOST_PASSWORD": "password123",
        },
        clear=True,
    )
    def test_gmail_backend(self):

        backend, host, port, tls, ssl, user, password, default_from, owner = get_email_backend_config()

        self.assertEqual(
            backend,
            "django.core.mail.backends.smtp.EmailBackend",
        )

        self.assertEqual(
            host,
            "smtp.gmail.com",
        )

        self.assertEqual(
            port,
            587,
        )

        self.assertTrue(tls)

    @patch.dict(
        os.environ,
        {
            "EMAIL_BACKEND": "django.core.mail.backends.smtp.EmailBackend",
            "EMAIL_HOST": "smtp.gmail.com",
            "EMAIL_PORT": "587",
            "EMAIL_USE_TLS": "True",
            "EMAIL_USE_SSL": "False",
            "EMAIL_HOST_USER": "shopora@gmail.com",
            "EMAIL_HOST_PASSWORD": "password123",
            "DEFAULT_FROM_EMAIL": "Shopora <shopora@gmail.com>",
            "OWNER_EMAIL": "owner@example.com",
        },
        clear=True,
    )
    def test_explicit_smtp_environment_settings(self):

        backend, host, port, tls, ssl, user, password, default_from, owner = get_email_backend_config()

        self.assertEqual(
            backend,
            "django.core.mail.backends.smtp.EmailBackend",
        )

        self.assertEqual(
            host,
            "smtp.gmail.com",
        )

        self.assertEqual(
            port,
            587,
        )

        self.assertTrue(tls)
        self.assertFalse(ssl)

        self.assertEqual(
            user,
            "shopora@gmail.com",
        )

        self.assertEqual(
            password,
            "password123",
        )

        self.assertEqual(
            default_from,
            "Shopora <shopora@gmail.com>",
        )

        self.assertEqual(
            owner,
            "owner@example.com",
        )
