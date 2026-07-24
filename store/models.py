from django.db import models
from django.urls import reverse
from accounts.models import User
from django.db.models import Avg
from django.utils.text import slugify
from cloudinary.models import CloudinaryField


# Create your models here.



# ==========================================
# Brand Model
# ==========================================

class Brand(models.Model):

    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(unique=True, blank=True)
    logo = models.ImageField(upload_to="brands/", blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:

        ordering = [
            "name"
        ]

    def save(self, *args, **kwargs):

        if not self.slug:

            self.slug = slugify(self.name)

        super().save(*args, **kwargs)

    def __str__(self):

        return self.name

class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, blank=True)

    def save(self, *args, **kwargs):

        if not self.slug:

            self.slug = slugify(self.name)

        super().save(*args, **kwargs)

    class Meta:
        ordering = ["name"]
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name

class Product(models.Model):

    # ==========================================
    # Basic
    # ==========================================

    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name="products",
    )

    brand = models.ForeignKey(
        Brand,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="products",
    )

    name = models.CharField(
        max_length=200,
    )

    slug = models.SlugField(
        unique=True,
        blank=True,
    )

    image = CloudinaryField(
        "image",
        blank=True,
        null=True,
    )

    description = models.TextField(
        blank=True,
    )

    # ==========================================
    # Price
    # ==========================================

    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
    )

    flash_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Discounted flash sale price",
    )

    flash_end = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Flash sale ending time",
    )

    # ==========================================
    # Stock
    # ==========================================

    stock = models.PositiveIntegerField(
        default=0,
        help_text="Available Stock",
    )

    available = models.BooleanField(
        default=True,
    )

    featured = models.BooleanField(
        default=False,
    )

    # ==========================================
    # Marketing Flags
    # ==========================================

    is_flash_sale = models.BooleanField(
        default=False,
    )

    is_free_delivery = models.BooleanField(
        default=False,
    )

    is_trending = models.BooleanField(
        default=False,
    )

    is_new_arrival = models.BooleanField(
        default=False,
    )

    # ==========================================
    # Analytics
    # ==========================================

    views = models.PositiveIntegerField(
        default=0,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    # ==========================================
    # Save
    # ==========================================

    def save(self, *args, **kwargs):

        if not self.slug:

            self.slug = slugify(self.name)

        super().save(*args, **kwargs)

    # ==========================================
    # Meta
    # ==========================================

    class Meta:

        ordering = [

            "-created_at",

        ]

    # ==========================================
    # String
    # ==========================================

    def __str__(self):

        return self.name

    # ==========================================
    # URL
    # ==========================================

    def get_absolute_url(self):

        return reverse(

            "store:product_detail",

            args=[self.slug],

        )

    # ==========================================
    # Rating
    # ==========================================

    def average_rating(self):

        return (

            self.reviews.aggregate(

                average=Avg("rating")

            )["average"]

            or 0

        )

    # ==========================================
    # Stock Helpers
    # ==========================================

    @property
    def in_stock(self):

        return self.stock > 0

    @property
    def low_stock(self):

        return self.stock <= 5

    @property
    def stock_status(self):

        if self.stock <= 0:

            return "Out Of Stock"

        if self.stock <= 5:

            return "Low Stock"

        return "In Stock"

    # ==========================================
    # Flash Sale
    # ==========================================

    @property
    def has_flash_sale(self):

        return (

            self.is_flash_sale

            and self.flash_price

            and self.flash_price < self.price

        )

    @property
    def current_price(self):

        if self.has_flash_sale:

            return self.flash_price

        return self.price

    @property
    def discount_percent(self):

        if self.has_flash_sale:

            return round(

                (

                    (self.price - self.flash_price)

                    / self.price

                ) * 100

            )

        return 0
    
# ==========================================
# Product Images
# ==========================================

class ProductImage(models.Model):

    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="gallery")
    image = models.ImageField(upload_to="products/gallery/")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:

        ordering = [

            "id",

        ]

    def __str__(self):

        return self.product.name

    
# ==========================================
# Wishlist Model
# ==========================================

class Wishlist(models.Model):

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="wishlist",)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="wishlisted_by",)
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:

        unique_together = ("user", "product")

        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user.username} ❤️ {self.product.name}"
    
# ==========================================
# Product Review Model
# ==========================================

class Review(models.Model):
    RATING_CHOICES = (
        (1, "⭐"),

        (2, "⭐⭐"),

        (3, "⭐⭐⭐"),

        (4, "⭐⭐⭐⭐"),

        (5, "⭐⭐⭐⭐⭐"),

    )

    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="reviews")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="reviews")
    rating = models.PositiveSmallIntegerField(choices=RATING_CHOICES)
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = (
            "product",
            "user",
        )

        ordering = [
            "-created_at"
        ]

    def __str__(self):
        return f"{self.product.name} - {self.user.username}"