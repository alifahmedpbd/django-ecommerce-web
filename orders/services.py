from store.services import reduce_stock, restore_stock


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