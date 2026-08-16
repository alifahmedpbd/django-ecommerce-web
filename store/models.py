from django.db import models
from django.urls import reverse
from accounts.models import User
from django.db.models import Avg
from django.utils.text import slugify
from cloudinary.models import CloudinaryField


# Create your models here.

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

    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="products")
    brand = models.ForeignKey(Brand, on_delete=models.SET_NULL, null=True, blank=True, related_name="products")
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, blank=True)
    image = CloudinaryField("image", blank=True, null=True)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    flash_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, help_text="Discounted flash sale price")
    flash_end = models.DateTimeField(null=True, blank=True, help_text="Flash sale ending time")
    stock = models.PositiveIntegerField(default=0, help_text="Available Stock")
    available = models.BooleanField(default=True)
    featured = models.BooleanField(default=False)
    is_flash_sale = models.BooleanField(default=False)
    is_free_delivery = models.BooleanField(default=False)
    is_trending = models.BooleanField(default=False)
    is_new_arrival = models.BooleanField(default=False)
    views = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    display_order = models.PositiveIntegerField(default=9999, db_index=True, verbose_name="Display Order", help_text="Lower number shows first.")

    def save(self, *args, **kwargs):

        if not self.slug:

            self.slug = slugify(self.name)

        super().save(*args, **kwargs)
    class Meta:

        ordering = [
            "-created_at",
            "display_order",
        ]

        indexes = [
            models.Index(
                fields=["available", "stock"]
            ),
            models.Index(
                fields=["available", "featured"]
            ),
            models.Index(
                fields=["available", "is_flash_sale"]
            ),
            models.Index(
                fields=["views"]
            ),
        ]


    def __str__(self):

        return self.name


    def get_absolute_url(self):

        return reverse(

            "store:product_detail",

            args=[self.slug],

        )


    def average_rating(self):

        return (

            self.reviews.aggregate(

                average=Avg("rating")

            )["average"]

            or 0

        )

 

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

    def swap_display_order(self, new_order):

        from store.models import Product

        try:
            other = Product.objects.get(display_order=new_order)

        except Product.DoesNotExist:

            self.display_order = new_order

            self.save(
                update_fields=[
                    "display_order",
                ]
            )

            return

        old = self.display_order

        other.display_order = old

        other.save(
            update_fields=[
                "display_order",
            ]
        )

        self.display_order = new_order

        self.save(
            update_fields=[
                "display_order",
            ]
        )


class ProductImage(models.Model):

    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="gallery")
    image = CloudinaryField("image")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["id"]

    def __str__(self):
        return self.product.name


class Wishlist(models.Model):

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="wishlist",)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="wishlisted_by",)
    created_at = models.DateTimeField(auto_now_add=True)
    promotion_sent = models.BooleanField(default=False)
    last_promotion = models.DateTimeField(null=True, blank=True)
    class Meta:

        unique_together = ("user", "product")

        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user.username} ❤️ {self.product.name}"
    

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

class AbandonedCart(models.Model):

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="abandoned_carts")
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    recovered = models.BooleanField(default=False)
    reminder_sent = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:

        ordering = [
            "-created_at",
        ]