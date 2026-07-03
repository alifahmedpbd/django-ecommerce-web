from django.contrib import admin
from .models import Order, OrderItem
# Register your models here.

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "user",
        "paid",
        "payment_method",
        "status",
        "created_at",
    )

    list_filter = (
        "paid",
        "status",
        "payment_method",
    )

    search_fields = (
        "full_name",
        "email",
    )

    inlines = [
        OrderItemInline,
    ]

admin.site.register(OrderItem)