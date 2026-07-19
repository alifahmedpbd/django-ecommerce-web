from unittest.mock import patch

from django.contrib.messages import get_messages
from django.test import TestCase, override_settings
from django.urls import reverse

from .models import User


class RegisterViewTests(TestCase):
    @override_settings(EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend")
    @patch("accounts.utils.send_mail", side_effect=OSError("Network is unreachable"))
    def test_register_view_handles_email_failure_gracefully(self, mock_send_mail):
        response = self.client.post(
            reverse("accounts:register"),
            {
                "username": "alifahmed",
                "email": "alifahmed@example.com",
                "phone": "01700000000",
                "password1": "StrongPass123!",
                "password2": "StrongPass123!",
            },
            follow=True,
        )

        self.assertRedirects(response, reverse("accounts:verify_email"))
        self.assertTrue(User.objects.filter(email="alifahmed@example.com").exists())

        messages = [message.message for message in get_messages(response.wsgi_request)]
        self.assertTrue(
            any("couldn't send" in message.lower() or "try again" in message.lower() for message in messages)
        )
