import os
from unittest.mock import patch

from django.test import SimpleTestCase

from .email_config import get_email_backend_config


class EmailConfigTests(SimpleTestCase):
    @patch.dict(os.environ, {}, clear=True)
    def test_defaults_to_console_backend_when_no_smtp_credentials_exist(self):
        backend, host, port, use_tls, use_ssl, username, password, default_from, owner_email = get_email_backend_config()

        self.assertEqual(backend, "django.core.mail.backends.console.EmailBackend")
        self.assertEqual(host, "")
        self.assertEqual(port, 25)
        self.assertFalse(use_tls)
        self.assertFalse(use_ssl)
        self.assertEqual(default_from, "noreply@shopora.local")
        self.assertEqual(owner_email, "noreply@shopora.local")

    @patch.dict(os.environ, {"SENDGRID_API_KEY": "test-key"}, clear=True)
    def test_sendgrid_credentials_enable_smtp_backend(self):
        backend, host, port, use_tls, use_ssl, username, password, default_from, owner_email = get_email_backend_config()

        self.assertEqual(backend, "django.core.mail.backends.smtp.EmailBackend")
        self.assertEqual(host, "smtp.sendgrid.net")
        self.assertEqual(port, 587)
        self.assertTrue(use_tls)
        self.assertFalse(use_ssl)
        self.assertEqual(username, "apikey")
        self.assertEqual(password, "test-key")
        self.assertEqual(default_from, "noreply@shopora.local")
        self.assertEqual(owner_email, "noreply@shopora.local")
