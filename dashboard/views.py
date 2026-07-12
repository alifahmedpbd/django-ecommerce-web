
from django.shortcuts import render, redirect, get_object_or_404

from accounts.decorators import owner_or_staff_required

from accounts.models import User
from orders.models import Order, Coupon
from django.contrib import messages

from store.models import Category, Product, Brand, ProductImage
from .forms import CategoryForm, ProductForm, BrandForm, ProductImageForm, CouponForm

from .decorators import owner_required
from django.core.paginator import Paginator

# Create your views here.


@owner_or_staff_required
def dashboard_home(request):

    total_orders = Order.objects.count()

    total_categories = Category.objects.count()

    total_customers = User.objects.filter(
        role="customer",
    ).count()

    total_products = Product.objects.count()

    revenue = sum(

        order.get_total_cost()

        for order in Order.objects.filter(

            status="delivered",

            paid=True,

        )

    )

    recent_orders = Order.objects.select_related(
        "user",
    ).order_by(
        "-created_at",
    )[:5]

    recent_customers = User.objects.filter(
        role="customer",
    ).order_by(
        "-date_joined",
    )[:5]

    low_stock_products = Product.objects.filter(

        stock__gt=0,

        stock__lte=5,

    )

    out_of_stock_products = Product.objects.filter(

        stock=0,

    )

    context = {

        "total_orders": total_orders,

        "total_categories": total_categories,

        "total_customers": total_customers,

        "total_products": total_products,

        "revenue": revenue,

        "recent_orders": recent_orders,

        "recent_customers": recent_customers,

        "low_stock_products": low_stock_products,

        "out_of_stock_products": out_of_stock_products,

        "low_stock_count": low_stock_products.count(),

        "out_of_stock_count": out_of_stock_products.count(),

    }

    if request.user.role == "owner":

        return render(
            request,
            "dashboard/owner_dashboard.html",
            context,
        )

    if request.user.role == "staff":

        return render(
            request,
            "dashboard/staff_dashboard.html",
            context,
        )

    return redirect("home")


@owner_required
def category_list(request):

    categories = Category.objects.all().order_by("name")

    return render(
        request,
        "dashboard/categories/list.html",
        {
            "categories": categories,
        },
    )


@owner_required
def category_create(request):

    if request.method == "POST":

        form = CategoryForm(request.POST, request.FILES)

        if form.is_valid():

            form.save()

            messages.success(
                request,
                "Category created successfully.",
            )

            return redirect("dashboard:category_list")

    else:

        form = CategoryForm()

    return render(
        request,
        "dashboard/categories/create.html",
        {
            "form": form,
        },
    )


@owner_required
def category_update(request, pk):

    category = get_object_or_404(
        Category,
        pk=pk,
    )

    if request.method == "POST":

        form = CategoryForm(
            request.POST,
            request.FILES,
            instance=category,
        )

        if form.is_valid():

            form.save()

            messages.success(
                request,
                "Category updated successfully.",
            )

            return redirect("dashboard:category_list")

    else:

        form = CategoryForm(instance=category)

    return render(
        request,
        "dashboard/categories/update.html",
        {
            "form": form,
            "category": category,
        },
    )


@owner_required
def category_delete(request, pk):

    category = get_object_or_404(
        Category,
        pk=pk,
    )

    category.delete()

    messages.success(
        request,
        "Category deleted successfully.",
    )

    return redirect("dashboard:category_list")


# ==========================================
# Brand List
# ==========================================

def brand_list(request):

    brands = Brand.objects.order_by("name")

    return render(
        request,
        "dashboard/brands/list.html",
        {
            "brands": brands,
        },
    )


# ==========================================
# Brand Create
# ==========================================

def brand_create(request):

    if request.method == "POST":

        form = BrandForm(
            request.POST,
            request.FILES,
        )

        if form.is_valid():

            form.save()

            messages.success(
                request,
                "Brand Added Successfully.",
            )

            return redirect("dashboard:brand_list")

    else:

        form = BrandForm()

    return render(
        request,
        "dashboard/brands/create.html",
        {
            "form": form,
        },
    )


# ==========================================
# Brand Update
# ==========================================

def brand_update(request, pk):

    brand = get_object_or_404(
        Brand,
        pk=pk,
    )

    if request.method == "POST":

        form = BrandForm(
            request.POST,
            request.FILES,
            instance=brand,
        )

        if form.is_valid():

            form.save()

            messages.success(
                request,
                "Brand Updated Successfully.",
            )

            return redirect("dashboard:brand_list")

    else:

        form = BrandForm(
            instance=brand,
        )

    return render(
        request,
        "dashboard/brands/update.html",
        {
            "form": form,
        },
    )


# ==========================================
# Brand Delete
# ==========================================

def brand_delete(request, pk):

    brand = get_object_or_404(Brand, pk=pk)

    if request.method == "POST":

        brand.delete()

        messages.success(
            request,
            "Brand Deleted Successfully.",
        )

        return redirect("dashboard:brand_list")

    return render(
        request,
        "dashboard/brands/delete.html",
        {
            "brand": brand,
        },
    )


# ==========================================
# Product List
# ==========================================
@owner_required



def product_list(request):

    query = request.GET.get("q")

    products = Product.objects.select_related(
        "category"
    ).order_by("-created_at")

    if query:

        products = products.filter(
            name__icontains=query
        )

    paginator = Paginator(
        products,
        10,
    )

    page_number = request.GET.get("page")

    page_obj = paginator.get_page(page_number)

    context = {

        "page_obj": page_obj,

        "products": page_obj,

        "query": query,

        "total_products": Product.objects.count(),

        "available_products": Product.objects.filter(
            available=True
        ).count(),

        "featured_products": Product.objects.filter(
            featured=True
        ).count(),

        "out_of_stock": Product.objects.filter(
            stock=0
        ).count(),

    }

    return render(
        request,
        "dashboard/products/list.html",
        context,
    )

# ==========================================
# Product Create
# ==========================================
@owner_required
def product_create(request):

    if request.method == "POST":

        form = ProductForm(
            request.POST,
            request.FILES,
        )

        if form.is_valid():

            form.save()

            messages.success(
                request,
                "Product created successfully.",
            )

            return redirect("dashboard:product_list")

    else:

        form = ProductForm()

    return render(
        request,
        "dashboard/products/create.html",
        {

            "form": form,

        },
    )


# ==========================================
# Product Update
# ==========================================
@owner_required
def product_update(request, pk):

    product = get_object_or_404(
        Product,
        pk=pk,
    )

    if request.method == "POST":

        form = ProductForm(
            request.POST,
            request.FILES,
            instance=product,
        )

        if form.is_valid():

            form.save()

            messages.success(
                request,
                "Product updated successfully.",
            )

            return redirect("dashboard:product_list")

    else:

        form = ProductForm(
            instance=product,
        )

    return render(
        request,
        "dashboard/products/update.html",
        {

            "form": form,

            "product": product,

        },
    )


# ==========================================
# Product Delete
# ==========================================
@owner_required
def product_delete(request, pk):

    product = get_object_or_404(
        Product,
        pk=pk,
    )

    if request.method == "POST":

        product.delete()

        messages.success(
            request,
            "Product deleted successfully.",
        )

        return redirect("dashboard:product_list")

    return render(
        request,
        "dashboard/products/delete.html",
        {

            "product": product,

        },
    )



# ==========================================
# Product Gallery
# ==========================================

def product_gallery(request, pk):

    product = get_object_or_404(
        Product,
        pk=pk,
    )

    images = product.gallery.all()

    form = ProductImageForm()

    context = {

        "product": product,

        "images": images,

        "form": form,

    }

    return render(

        request,

        "dashboard/product_images/gallery.html",

        context,

    )



# ==========================================
# Upload Product Image
# ==========================================

def product_image_create(request, pk):

    product = get_object_or_404(

        Product,

        pk=pk,

    )

    if request.method == "POST":

        form = ProductImageForm(

            request.POST,

            request.FILES,

        )

        if form.is_valid():

            image = form.save(

                commit=False,

            )

            image.product = product

            image.save()

            messages.success(

                request,

                "Image Uploaded Successfully.",

            )

    return redirect(

        "dashboard:product_gallery",

        pk=pk,

    )


# ==========================================
# Delete Product Image
# ==========================================

def product_image_delete(request, pk):

    image = get_object_or_404(

        ProductImage,

        pk=pk,

    )

    product_id = image.product.id

    image.delete()

    messages.success(

        request,

        "Image Deleted Successfully.",

    )

    return redirect(

        "dashboard:product_gallery",

        pk=product_id,

    )


# ==========================================
# Coupon List
# ==========================================

def coupon_list(request):

    coupons = Coupon.objects.all().order_by("-id")

    return render(

        request,

        "dashboard/coupon/list.html",

        {

            "coupons": coupons,

        },

    )


# ==========================================
# Coupon Add
# ==========================================

def coupon_add(request):

    if request.method == "POST":

        form = CouponForm(request.POST)

        if form.is_valid():

            form.save()

            return redirect("dashboard:coupon_list")

    else:

        form = CouponForm()

    return render(

        request,

        "dashboard/coupon/form.html",

        {

            "form": form,

            "title": "Add Coupon",

        },

    )


# ==========================================
# Coupon Edit
# ==========================================

def coupon_edit(request, pk):

    coupon = get_object_or_404(

        Coupon,

        pk=pk,

    )

    if request.method == "POST":

        form = CouponForm(

            request.POST,

            instance=coupon,

        )

        if form.is_valid():

            form.save()

            return redirect(

                "dashboard:coupon_list"

            )

    else:

        form = CouponForm(

            instance=coupon,

        )

    return render(

        request,

        "dashboard/coupon/form.html",

        {

            "form": form,

            "title": "Edit Coupon",

        },

    )


# ==========================================
# Coupon Delete
# ==========================================

def coupon_delete(request, pk):

    coupon = get_object_or_404(

        Coupon,

        pk=pk,

    )

    coupon.delete()

    return redirect(

        "dashboard:coupon_list"

    )