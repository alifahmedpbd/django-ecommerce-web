from store.services import reduce_stock, restore_stock
from decimal import Decimal
from django.utils import timezone
from .models import Coupon, CouponUsage

# ==========================================
# Reduce Order Stock
# ==========================================

def reduce_order_stock(order):

    for item in order.items.select_related("product"):

        reduce_stock(

            product=item.product,

            quantity=item.quantity,

        )


# ==========================================
# Restore Order Stock
# ==========================================

def restore_order_stock(order):

    for item in order.items.select_related("product"):

        restore_stock(

            product=item.product,

            quantity=item.quantity,

        )


# ==========================================
# Coupon Validation
# ==========================================

def validate_coupon(code, subtotal, user=None):

    try:

        coupon = Coupon.objects.get(

            code__iexact=code,

            active=True,

        )

    except Coupon.DoesNotExist:

        return None, "Invalid coupon."

    now = timezone.now()

    if now < coupon.valid_from:

        return None, "Coupon is not active yet."

    if now > coupon.valid_to:

        return None, "Coupon has expired."

    if coupon.usage_limit > 0:

        if coupon.used_count >= coupon.usage_limit:

            return None, "Coupon usage limit reached."

    if Decimal(subtotal) < coupon.minimum_purchase:

        return None, (

            f"Minimum purchase ${coupon.minimum_purchase} required."

        )

    if coupon.one_time_per_user and  user:

        already_used = CouponUsage.objects.filter(

            coupon=coupon,

            user=user,

        ).exists()

        if already_used:

            return None, (

                "You have already used this coupon."

            )

    return coupon, None


# ==========================================
# Calculate Discount
# ==========================================

def calculate_discount(coupon, subtotal):

    subtotal = Decimal(subtotal)

    if coupon.discount_type == "percentage":

        discount = (

            subtotal *

            coupon.discount

        ) / Decimal("100")

    else:

        discount = coupon.discount

    if discount > subtotal:

        discount = subtotal

    return discount