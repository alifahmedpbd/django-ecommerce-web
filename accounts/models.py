from datetime import timedelta
import random

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone

# Create your models here.

class User(AbstractUser):

    ROLE_CHOICES = (
        ("customer", "Customer"),
        ("staff", "Staff"),
        ("owner", "Owner"),
    )

    email = models.EmailField(
        unique=True,
    )

    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default="customer",
    )

    phone = models.CharField(
        max_length=15,
        blank=True,
    )

    profile_image = models.ImageField(
        upload_to="profile_images/",
        blank=True,
        null=True,
    )

    def __str__(self):
        return self.username


class EmailOTP(models.Model):

    PURPOSE_VERIFY = "verify"
    PURPOSE_RESET = "reset"
    PURPOSE_LOGIN = "login"

    PURPOSE_CHOICES = (
        (PURPOSE_VERIFY, "Verify Email"),
        (PURPOSE_RESET, "Reset Password"),
        (PURPOSE_LOGIN, "Login"),
    )

    OTP_LENGTH = 6

    OTP_EXPIRE_MINUTES = 5

    RESEND_INTERVAL_SECONDS = 30

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="email_otps",
    )

    purpose = models.CharField(
        max_length=20,
        choices=PURPOSE_CHOICES,
    )

    otp = models.CharField(
        max_length=OTP_LENGTH,
    )

    is_verified = models.BooleanField(
        default=False,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:

        ordering = ["-created_at"]

        indexes = [
            models.Index(fields=["user", "purpose"]),
            models.Index(fields=["otp"]),
        ]

    def generate_otp(self):

        self.otp = str(
            random.randint(100000, 999999)
        )

        self.save(update_fields=["otp"])

    def is_expired(self):

        return timezone.now() > (
            self.created_at
            + timedelta(minutes=self.OTP_EXPIRE_MINUTES)
        )

    def can_resend(self):

        return timezone.now() > (
            self.updated_at
            + timedelta(seconds=self.RESEND_INTERVAL_SECONDS)
        )

    def mark_verified(self):

        self.is_verified = True

        self.save(update_fields=["is_verified"])

    def __str__(self):

        return f"{self.user.email} - {self.purpose}"