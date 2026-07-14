from django.db import models
from accounts.models import User
from store.models import Product
from django.utils import timezone
# Create your models here.


# ==========================================
# Coupon Model
# ==========================================

class Coupon(models.Model):

    DISCOUNT_TYPE = (

        ("percentage", "Percentage"),

        ("fixed", "Fixed Amount"),

    )

    code = models.CharField(max_length=50, unique=True)
    discount_type = models.CharField(max_length=20, choices=DISCOUNT_TYPE)
    discount = models.DecimalField(max_digits=10, decimal_places=2)
    minimum_purchase = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    usage_limit = models.PositiveIntegerField(default=1)
    used_count = models.PositiveIntegerField(default=0)
    active = models.BooleanField(default=True)
    one_time_per_user = models.BooleanField(default=False)
    valid_from = models.DateTimeField(default=timezone.now)
    valid_to = models.DateTimeField()

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:

        ordering = [

            "-created_at",

        ]

    def __str__(self):

        return self.code

    @property
    def is_expired(self):

        return timezone.now() > self.valid_to

    @property
    def is_available(self):

        return (

            self.active

            and

            not self.is_expired

            and

            self.used_count < self.usage_limit

        )

class Order(models.Model):

    PAYMENT_METHODS = (
        ("cod", "Cash On Delivery"),
        ("sslcommerz", "SSSCommerz"),
        ("stripe", "Stripe"),
    )

    STATUS_CHOICES = (
        ("pending", "Pending"),
        ("processing", "Processing"),
        ("shipped", "Shipped"),
        ("delivered", "Delivered"),
        ("cancelled", "Cancelled"),
    )

    PAYMENT_STATUS_CHOICES = (

    ("pending", "Pending"),

    ("paid", "Paid"),

    ("partial", "Partial Paid"),

    ("failed", "Failed"),

    ("refunded", "Refunded"),

    ("cancelled", "Cancelled"),

    )

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="orders")
    full_name = models.CharField(max_length=200)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    address = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    paid = models.BooleanField(default=False)
    payment_method = models.CharField(max_length=200, choices=PAYMENT_METHODS, default="cod")
    payment_id = models.CharField(max_length=200, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    coupon = models.ForeignKey(Coupon, on_delete=models.SET_NULL, null=True, blank=True)
    discount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    final_total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default="pending")

    def __str__(self):
        return f"Order #{self.id}"
    
    def get_total_cost(self):

        subtotal = sum(

            item.get_total_price()

            for item in self.items.all()

        )

        return subtotal - self.discount
    
    
class OrderItem(models.Model):

    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)

    def get_total_price(self):
        return self.price * self.quantity
    
    def __str__(self):
        return self.product.name
    
# ==========================================
# Coupon Usage
# ==========================================

class CouponUsage(models.Model):

    coupon = models.ForeignKey(Coupon, on_delete=models.CASCADE, related_name="usages")
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    used_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):

        return f"{self.user.username} - {self.coupon.code}"


class OrderTimeline(models.Model):

    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="timeline")
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    note = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:

        ordering = ["-created_at"]

    def __str__(self):

        return f"Order #{self.order.id}"


class ExchangeRate(models.Model):

    currency = models.CharField(max_length=10, unique=True, default="USD")
    rate = models.DecimalField(max_digits=10, decimal_places=2, default=122.50,)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:

        verbose_name = "Exchange Rate"

        verbose_name_plural = "Exchange Rates"

    def __str__(self):

        return f"1 {self.currency} = ৳{self.rate}"