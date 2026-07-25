from django.db import models
from accounts.models import User
from store.models import Product
from django.utils import timezone
import random
import string
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

class DeliveryCharge(models.Model):

    CITY_CHOICES = (
        ("dhaka", "Dhaka"),
        ("outside", "Outside Dhaka"),
    )

    city = models.CharField(
        max_length=20,
        choices=CITY_CHOICES,
        unique=True,
    )

    charge = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        help_text="USD Amount",
    )

    class Meta:
        ordering = ["city"]
        verbose_name = "Delivery Charge"
        verbose_name_plural = "Delivery Charges"

    def __str__(self):
        return f"{self.get_city_display()} - ${self.charge}"

class Order(models.Model):

    PAYMENT_METHODS = (
        ("cod", "Cash On Delivery"),
        ("sslcommerz", "SSSCommerz"),
        ("stripe", "Stripe"),
        ("emi", "EMI"),
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

    COURIER_CHOICES = (
        ("", "Select Courier"),
        ("Steadfast", "Steadfast"),
        ("RedX", "RedX"),
        ("Pathao", "Pathao"),
        ("Sundarban", "Sundarban Courier"),
        ("Paperfly", "Paperfly"),
        ("SA Paribahan", "SA Paribahan"),
        ("Others", "Others"),
    )

    EMI_MONTHS = (
        (3, "3 Months"),
        (6, "6 Months"),
        (9, "9 Months"),
        (12, "12 Months"),
    )

    CITY_CHOICES = (
        ("dhaka", "Dhaka"),
        ("outside", "Outside Dhaka"),
    )


    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="orders")
    full_name = models.CharField(max_length=200)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    address = models.TextField()
    city = models.CharField(max_length=20, choices=CITY_CHOICES, default="dhaka")
    created_at = models.DateTimeField(auto_now_add=True)
    paid = models.BooleanField(default=False)
    payment_method = models.CharField(max_length=200, choices=PAYMENT_METHODS, default="cod")
    payment_id = models.CharField(max_length=200, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    coupon = models.ForeignKey(Coupon, on_delete=models.SET_NULL, null=True, blank=True)
    discount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    final_total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default="pending")
    tracking_number = models.CharField(max_length=100, blank=True)
    courier_name = models.CharField(max_length=100, choices=COURIER_CHOICES, blank=True)
    estimated_delivery = models.DateField(null=True, blank=True)
    delivery_charge = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    admin_note = models.TextField(blank=True)
    cancel_reason = models.TextField(blank=True)
    return_reason = models.TextField(blank=True)
    emi_months = models.PositiveSmallIntegerField(choices=EMI_MONTHS, null=True, blank=True)


    def __str__(self):
        return f"Order #{self.id}"
    
    def get_total_cost(self):

        subtotal = sum(

            item.get_total_price()

            for item in self.items.all()

        )

        return subtotal - self.discount

    def generate_tracking_number(self):

        if self.tracking_number:
            return self.tracking_number

        while True:

            code = "SHP-" + "".join(
                random.choices(
                    string.ascii_uppercase + string.digits,
                    k=10,
                )
            )

            if not Order.objects.filter(
                tracking_number=code
            ).exists():

                self.tracking_number = code
                return code

    def get_tracking_url(self):

        if not self.tracking_number:
            return ""

        urls = {
            "Steadfast": f"https://steadfast.com.bd/t/{self.tracking_number}",
            "RedX": f"https://redx.com.bd/track?tracking={self.tracking_number}",
            "Pathao": f"https://merchant.pathao.com/tracking/{self.tracking_number}",
            "Sundarban": f"https://tracking.sundarbancourierltd.com/{self.tracking_number}",
            "Paperfly": f"https://paperfly.com.bd/track/{self.tracking_number}",
        }

        return urls.get(self.courier_name, "")
    
    
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
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    created_by = models.CharField(max_length=100, default="System")
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
    
class ReturnRequest(models.Model):

    STATUS_CHOICES = (

        ("pending", "Pending"),

        ("approved", "Approved"),

        ("rejected", "Rejected"),

        ("refunded", "Refunded"),

    )

    order = models.OneToOneField(
        Order,
        on_delete=models.CASCADE,
        related_name="return_request",
    )

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
    )

    reason = models.TextField()

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="pending",
    )

    admin_note = models.TextField(
        blank=True,
    )

    refund_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    def __str__(self):

        return f"Return #{self.order.id}"