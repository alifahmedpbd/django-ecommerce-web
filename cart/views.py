from django.shortcuts import render, get_object_or_404, redirect
from store.models import Product
from .cart import Cart
from orders.forms import OrderCreateForm
from orders.models import OrderItem
# Create your views here.

def cart_add(request, product_id):

    cart = Cart(request)

    product = get_object_or_404(Product, id=product_id)

    cart.add(product)
    return redirect("cart:cart_detail")

def cart_detail(request):

    cart = Cart(request)

    return render(request, "cart/cart_detail.html", {"cart": cart})

def cart_remove(request, product_id):

    cart = Cart(request)

    product = get_object_or_404(Product, id=product_id)

    cart.remove(product)

    return redirect("cart:cart_detail")

def cart_update(request, product_id, action):

    cart = Cart(request)

    product = get_object_or_404(Product, id=product_id)

    quantity = cart.cart[str(product.id)]["quantity"]

    if action == "increase":

        quantity += 1
    
    elif action == "decrease":

        quantity -= 1

    if quantity <= 0:

        cart.remove(product)
    
    else:

        cart.update(product, quantity)

    return redirect("cart:cart_detail")

def checkout(request):

    cart = Cart(request)

    if len(cart) == 0:

        return redirect("store:product_list")

    if request.method == "POST":

        form = OrderCreateForm(request.POST)

        if form.is_valid():

            order = form.save(commit=False)

            order.user = request.user

            order.save()

            for item in cart:

                OrderItem.objects.create(
                    order=order,
                    product=item["product"],
                    price=item["price"],
                    quantity=item["quantity"]
                )
                
            cart.clear()

            return redirect("orders:order_success", order.id)
        
    else:

        form = OrderCreateForm()

    return render(request, "cart/checkout.html", {"cart": cart, "form": form, })