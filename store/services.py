from django.db import transaction


# ==========================================
# Reduce Product Stock
# ==========================================

@transaction.atomic
def reduce_stock(product, quantity):

    if quantity <= 0:

        return False

    if product.stock < quantity:

        return False

    product.stock -= quantity

    product.save(
        update_fields=[
            "stock",
        ]
    )

    return True


# ==========================================
# Restore Product Stock
# ==========================================

@transaction.atomic
def restore_stock(product, quantity):

    if quantity <= 0:

        return

    product.stock += quantity

    product.save(
        update_fields=[
            "stock",
        ]
    )


# ==========================================
# Product Out Of Stock
# ==========================================

def is_out_of_stock(product):

    return product.stock <= 0


# ==========================================
# Low Stock Warning
# ==========================================

def is_low_stock(product):

    return product.stock <= 5


# ==========================================
# Can Customer Buy?
# ==========================================

def can_purchase(product, quantity):

    return product.stock >= quantity