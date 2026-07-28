from django.db import models

from django.conf import settings
# Create your models here.
class FeatureToggle(models.Model):

    CATEGORY_CHOICES = [

        ("marketing", "Marketing"),
        ("customer", "Customer"),
        ("payment", "Payment"),
        ("website", "Website"),
    ]

    FEATURE_CHOICES = [

        ("flash_sale", "Flash Sale"),
        ("free_delivery", "Free Delivery"),
        ("new_arrival", "New Arrival"),
        ("trending", "Trending"),
        ("guest_checkout", "Guest Checkout"),
        ("wishlist", "Wishlist"),
        ("reviews", "Reviews"),
        ("coupon", "Coupon"),
        ("cod", "Cash On Delivery"),
        ("emi", "EMI"),
        ("announcement", "Announcement Bar"),
        ("maintenance", "Maintenance Mode"),
        ("coming_soon", "Coming Soon"),

    ]

    key = models.CharField(max_length=50, choices=FEATURE_CHOICES, unique=True)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default="website",)
    icon = models.CharField(max_length=50, default="⚙️")
    description = models.CharField(max_length=255,blank=True)
    enabled = models.BooleanField(default=True,)
    updated_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:

        ordering = [
            "category",
            "key",
        ]

        verbose_name = "Feature Toggle"

        verbose_name_plural = "Feature Toggles"

    def __str__(self):

        return self.get_key_display()


class WebsiteSettings(models.Model):
    shop_name = models.CharField(max_length=100, default="Shopora")
    shop_tagline = models.CharField(max_length=255, blank=True, null=True, default="")

    announcement = models.TextField(blank=True, null=True, default="")

    phone = models.CharField(max_length=30, blank=True, null=True, default="")
    email = models.EmailField(blank=True, null=True, default="")
    address = models.TextField(blank=True, null=True, default="")

    facebook = models.URLField(blank=True, null=True, default="")
    instagram = models.URLField(blank=True, null=True, default="")
    youtube = models.URLField(blank=True, null=True, default="")
    linkedin = models.URLField(blank=True, null=True, default="")
    twitter = models.URLField(blank=True, null=True, default="")

    logo = models.ImageField(upload_to="website/", blank=True, null=True, default="")
    favicon = models.ImageField(upload_to="website/", blank=True, null=True, default="")

    footer_text = models.CharField(
        max_length=255,
        blank=True, null=True,
        default="Premium Electronics Store"
    )

    copyright = models.CharField(
        max_length=255,
        blank=True, null=True,
        default="© 2026"
    )

    class Meta:
        verbose_name = "Website Settings"
        verbose_name_plural = "Website Settings"

    def save(self, *args, **kwargs):
        self.pk = 1      # Singleton
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        pass

    @classmethod
    def load(cls):
        obj, created = cls.objects.get_or_create(pk=1)
        return obj

    def __str__(self):
        return self.shop_name

class Announcement(models.Model):

    text = models.CharField(max_length=300)
    background_color = models.CharField(max_length=20, default="#ff3d3d")
    text_color = models.CharField(max_length=20, default="#ffffff")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.text[:50]


class CustomerActivity(models.Model):

    ACTIONS = (

        ("cart_add", "Cart Add"),
        ("cart_remove", "Cart Remove"),
        ("wishlist_add", "Wishlist Add"),
        ("wishlist_remove", "Wishlist Remove"),
    )

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    product = models.ForeignKey("store.Product", on_delete=models.CASCADE,)
    action = models.CharField(max_length=30, choices=ACTIONS)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:

        ordering = [
            "-created_at",
        ]

    def __str__(self):

        return f"{self.user} - {self.action}"

    
class EmailCampaign(models.Model):

    TARGET_CHOICES = [

        ("all", "All Customers"),
        ("wishlist", "Wishlist Customers"),
        ("cart", "Cart Customers"),
        ("no_order", "Customers Without Orders"),
        ("selected", "Selected Customers"),
    ]

    STATUS_CHOICES = [

        ("draft", "Draft"),
        ("sending", "Sending"),
        ("completed", "Completed"),
        ("failed", "Failed"),
    ]

    title = models.CharField(max_length=200)
    subject = models.CharField(max_length=255)
    message = models.TextField()
    target = models.CharField(max_length=20, choices=TARGET_CHOICES, default="all")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="draft")
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name="email_campaigns")
    created_at = models.DateTimeField(auto_now_add=True)
    sent_at = models.DateTimeField(null=True,blank=True)

    def __str__(self):
        return self.title


class EmailCampaignLog(models.Model):

    STATUS_CHOICES = [

        ("success", "Success"),
        ("failed", "Failed"),
    ]

    campaign = models.ForeignKey(EmailCampaign, on_delete=models.CASCADE, related_name="logs")
    customer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    error = models.TextField(blank=True)
    sent_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.customer.email} - {self.status}"