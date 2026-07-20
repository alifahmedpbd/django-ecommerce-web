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