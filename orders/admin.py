from django.contrib import admin
from .models import Order, OrderItem, Coupon, ExchangeRate, OrderTimeline
# Register your models here.

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "user",
        "status",
        "payment_status",
        "payment_method",
        "paid",
        "final_total",
        "courier_name",
        "created_at",
    )

    list_filter = (
        "status",
        "payment_status",
        "payment_method",
        "paid",
    )

    search_fields = (
        "id",
        "full_name",
        "email",
        "phone",
        "tracking_number",
    )

    readonly_fields = (
        "created_at",
    )

    fieldsets = (
        # ...
    )

    inlines = [
        OrderItemInline,
    ]

    def save_model(self, request, obj, form, change):

        if change:

            old = Order.objects.get(pk=obj.pk)

            if old.status != obj.status:

                OrderTimeline.objects.create(
                    order=obj,
                    user=obj.user,
                    created_by=request.user.username,
                    note=f"Order status changed from '{old.status}' to '{obj.status}'.",
                )

            if old.payment_status != obj.payment_status:

                OrderTimeline.objects.create(
                    order=obj,
                    user=obj.user,
                    created_by=request.user.username,
                    note=f"Payment status changed from '{old.payment_status}' to '{obj.payment_status}'.",
                )

        super().save_model(request, obj, form, change)

admin.site.register(OrderItem)
admin.site.register(Coupon)

@admin.register(ExchangeRate)
class ExchangeRateAdmin(admin.ModelAdmin):

    list_display = (

        "currency",

        "rate",

        "updated_at",

    )