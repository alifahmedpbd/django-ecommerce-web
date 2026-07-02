from django.db import models
from django.urls import reverse
# Create your models here.

class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)

    class Meta:
        ordering = ["name"]
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name

class Product(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    image = models.ImageField(upload_to="products/", blank=True, null=True)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField(default=0)
    available = models.BooleanField(default=True)
    featured = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        return reverse("store:product_detail", args=[self.slug])