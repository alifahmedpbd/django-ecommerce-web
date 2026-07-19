
from django.shortcuts import render, redirect, get_object_or_404

from accounts.decorators import owner_or_staff_required

from accounts.models import User
from orders.models import Order, Coupon, OrderTimeline
from django.contrib import messages

from store.models import Category, Product, Brand, ProductImage
from .forms import CategoryForm, ProductForm, BrandForm, ProductImageForm, CouponForm

from .decorators import owner_required
from django.core.paginator import Paginator

from django.db.models import Sum, Count, Q
from django.utils import timezone
from django.db.models.functions import TruncMonth

import json


from django.http import HttpResponse
from openpyxl import Workbook

from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph

# Create your views here.


@owner_or_staff_required
def dashboard_home(request):

    total_orders = Order.objects.count()

    total_categories = Category.objects.count()

    total_customers = User.objects.filter(
        role="customer",
    ).count()

    total_products = Product.objects.count()

    revenue = (
        Order.objects.filter(
            status="delivered",
            paid=True,
        ).aggregate(
            total=Sum("final_total")
        )["total"] or 0
    )

    today = timezone.now().date()

    today_orders = Order.objects.filter(
        created_at__date=today,
    ).count()

    today_revenue = (
        Order.objects.filter(
            created_at__date=today,
            paid=True,
            status="delivered",
        ).aggregate(
            total=Sum("final_total"),
        )["total"] or 0
    )

    monthly_revenue = (

        Order.objects.filter(

            paid=True,

            status="delivered",

        )

        .annotate(

            month=TruncMonth("created_at"),

        )

        .values(

            "month",

        )

        .annotate(

            revenue=Sum("final_total"),

        )

        .order_by(

            "month",

        )

    )

    monthly_orders = (

        Order.objects.annotate(

            month=TruncMonth(

                "created_at"

            )

        )

        .values(

            "month"

        )

        .annotate(

            total=Count("id")

        )

        .order_by(

            "month"

        )

    )

    top_products = (
        Product.objects.only(
            "id",
            "name",
        )
        .annotate(
            total_sold=Sum("orderitem__quantity")
        )
        .order_by("-total_sold")[:5]
    )

    top_categories = (
        Category.objects.only(
            "id",
            "name",
        )
        .annotate(
            total_sold=Sum("products__orderitem__quantity")
        )
        .order_by("-total_sold")[:5]
    )


    recent_orders = Order.objects.select_related(
        "user",
    ).order_by(
        "-created_at",
    )[:5]

    recent_customers = User.objects.filter(
        role="customer",
    ).only(
        "id",
        "username",
        "email",
        "date_joined",
    ).order_by("-date_joined")[:5]

    low_stock_products = Product.objects.filter(
        stock__gt=0,
        stock__lte=5,
    ).only(
        "id",
        "name",
        "stock",
    )

    out_of_stock_products = Product.objects.filter(
        stock=0,
    ).only(
        "id",
        "name",
        "stock",
    )


    monthly_labels = [
        item["month"].strftime("%b %Y")
        for item in monthly_revenue
    ]

    monthly_revenue_data = [
        float(item["revenue"] or 0)
        for item in monthly_revenue
    ]

    monthly_order_data = [
        item["total"]
        for item in monthly_orders
    ]

    top_product_labels = [
        product.name
        for product in top_products
    ]

    top_product_data = [
        product.total_sold or 0
        for product in top_products
    ] 

    top_category_labels = [
        category.name
        for category in top_categories
    ]

    top_category_data = [
        category.total_sold or 0
        for category in top_categories
    ]


    payment_methods = (
        Order.objects.filter(
            paid=True,
            status="delivered",
        )
        .values("payment_method")
        .annotate(
            total=Sum("final_total"),
        )
    )

    payment_labels = [
        item["payment_method"].upper()
        for item in payment_methods
    ]

    payment_data = [
        float(item["total"] or 0)
        for item in payment_methods
    ]

    payment_method_labels = [
        item["payment_method"].upper()
        for item in payment_methods
    ]

    payment_method_data = [
        float(item["total"] or 0)
        for item in payment_methods
    ]

    

    best_customers = (

        User.objects.filter(
            role="customer",
        )

        .annotate(

            total_spent=Sum(
                "orders__final_total",
                filter=Q(
                    orders__paid=True,
                    orders__status="delivered",
                ),
            ),

            total_orders=Count(
                "orders",
                filter=Q(
                    orders__paid=True,
                    orders__status="delivered",
                ),
            ),

        )

        .filter(
            total_spent__isnull=False,
        )

        .order_by(
            "-total_spent",
        )[:5]

    )

    context = {

        "total_orders": total_orders,

        "total_categories": total_categories,

        "total_customers": total_customers,

        "total_products": total_products,

        "revenue": revenue,

        "today_orders": today_orders,

        "today_revenue": today_revenue,

        "monthly_revenue": monthly_revenue,

        "monthly_orders": monthly_orders,

        "top_products": top_products,

        "top_categories": top_categories,

        "recent_orders": recent_orders,

        "recent_customers": recent_customers,

        "low_stock_products": low_stock_products,

        "out_of_stock_products": out_of_stock_products,

        "low_stock_count": low_stock_products.count(),

        "out_of_stock_count": out_of_stock_products.count(),

        "monthly_labels": json.dumps(monthly_labels),
        "monthly_revenue_data": json.dumps(monthly_revenue_data), 
        "monthly_order_data": json.dumps(monthly_order_data),

        "top_product_labels": json.dumps(top_product_labels),
        "top_product_data": json.dumps(top_product_data),

        "top_category_labels": json.dumps(top_category_labels),
        "top_category_data": json.dumps(top_category_data),

        "payment_labels": json.dumps(payment_labels),

        "payment_data": json.dumps(payment_data),

        "payment_method_labels": json.dumps(payment_method_labels),
        "payment_method_data": json.dumps(payment_method_data),

        "best_customers": best_customers,

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


@owner_or_staff_required
def reports(request):

    revenue_by_payment = (

        Order.objects.filter(

            paid=True,
            status="delivered",

        )

        .values("payment_method")

        .annotate(

            total=Sum("final_total"),

            orders=Count("id"),

        )

    )

    best_customers = (

        User.objects.filter(

            role="customer",

        )

        .annotate(

            total_spent=Sum("orders__final_total"),

            total_orders=Count("orders"),

        )

        .order_by(

            "-total_spent",

        )[:10]

    )

    low_stock = Product.objects.filter(
        stock__lte=5,
    ).select_related(
        "category",
    )

    return render(

        request,

        "dashboard/reports.html",

        {

            "revenue_by_payment": revenue_by_payment,

            "best_customers": best_customers,

            "low_stock": low_stock,

        },

    )


@owner_or_staff_required
def sales_report_pdf(request):

    orders = (
        Order.objects
        .select_related(
            "user",
            "coupon",
        )
        .order_by("-created_at")
    )

    response = HttpResponse(
        content_type="application/pdf"
    )

    response["Content-Disposition"] = (
        'attachment; filename="sales_report.pdf"'
    )

    doc = SimpleDocTemplate(response)

    data = [[
        "Order",
        "Customer",
        "Date",
        "Payment",
        "Status",
        "Coupon",
        "Discount",
        "Total",
    ]]

    for order in orders:

        data.append([

            f"#{order.id}",

            order.user.username,

            order.created_at.strftime("%d-%m-%Y"),

            order.payment_method.upper(),

            order.status.title(),

            order.coupon.code if order.coupon else "-",

            f"${order.discount}",

            f"${order.final_total}",

        ])

    table = Table(data)

    table.setStyle(TableStyle([

        ("BACKGROUND",(0,0),(-1,0),colors.darkblue),
        ("TEXTCOLOR",(0,0),(-1,0),colors.white),

        ("GRID",(0,0),(-1,-1),1,colors.grey),

        ("FONTNAME",(0,0),(-1,0),"Helvetica-Bold"),

        ("BACKGROUND",(0,1),(-1,-1),colors.whitesmoke),

    ]))

    doc.build([table])

    return response


@owner_or_staff_required
def sales_report_excel(request):

    workbook = openpyxl.Workbook()

    sheet = workbook.active

    sheet.title = "Sales Report"

    sheet.append([

        "Order ID",

        "Customer",

        "Date",

        "Payment",

        "Status",

        "Coupon",

        "Discount",

        "Total",

    ])

    orders = (
        Order.objects
        .select_related(
            "user",
            "coupon",
        )
        .order_by("-created_at")
    )

    for order in orders:

        sheet.append([

            order.id,

            order.user.username,

            order.created_at.strftime("%d-%m-%Y"),

            order.payment_method,

            order.status,

            order.coupon.code if order.coupon else "",

            float(order.discount),

            float(order.final_total),

        ])

    response = HttpResponse(

        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"

    )

    response["Content-Disposition"] = (

        'attachment; filename="sales_report.xlsx"'

    )

    workbook.save(response)

    return response


def low_stock_report_pdf(request):

    response = HttpResponse(
        content_type="application/pdf"
    )

    response[
        "Content-Disposition"
    ] = 'attachment; filename="low_stock_report.pdf"'

    doc = SimpleDocTemplate(response)

    styles = getSampleStyleSheet()

    data = [

        [

            "Product",

            "Category",

            "Stock",

        ]

    ]

    products = Product.objects.filter(

        stock__lte=5

    ).select_related(

        "category"

    )

    for product in products:

        data.append([

            product.name,

            product.category.name,

            str(product.stock),

        ])

    table = Table(data)

    table.setStyle(

        TableStyle([

            ("GRID",(0,0),(-1,-1),1,colors.grey),

            ("BACKGROUND",(0,0),(-1,0),colors.black),

            ("TEXTCOLOR",(0,0),(-1,0),colors.white),

            ("BOTTOMPADDING",(0,0),(-1,0),8),

        ])

    )

    elements = [

        Paragraph(

            "Low Stock Report",

            styles["Heading1"]

        ),

        table,

    ]

    doc.build(elements)

    return response


def low_stock_report_excel(request):

    wb = Workbook()

    ws = wb.active

    ws.title = "Low Stock"

    ws.append([

        "Product",

        "Category",

        "Stock",

    ])

    products = Product.objects.filter(

        stock__lte=5

    ).select_related(

        "category"

    )

    for product in products:

        ws.append([

            product.name,

            product.category.name,

            product.stock,

        ])

    response = HttpResponse(

        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"

    )

    response[
        "Content-Disposition"

    ] = 'attachment; filename="low_stock.xlsx"'

    wb.save(response)

    return response


@owner_required
def category_list(request):

    categories = Category.objects.only(
        "id",
        "name",
        "image",
    ).order_by("name")

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

    products = (
        Product.objects
        .select_related(
            "category",
            "brand",
        )
        .order_by("-created_at")
    )

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

    images = product.gallery.only(
        "id",
        "image",
    )

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

    coupons = Coupon.objects.only(
        "id",
        "code",
        "discount",
        "active",
        "valid_from",
        "valid_to",
    ).order_by("-id")

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

@owner_or_staff_required
def dashboard_order_detail(request, order_id):

    order = get_object_or_404(
        Order.objects.select_related(
            "user",
            "coupon",
        ).prefetch_related(
            "items__product",
            "timeline__user",
        ),
        id=order_id,
    )

    if request.method == "POST":

        # ==========================
        # Previous Status
        # ==========================

        old_status = order.status

        # ==========================
        # Payment Status
        # ==========================

        payment_status = request.POST.get(
            "payment_status"
        )

        if payment_status:

            order.payment_status = payment_status

            order.paid = payment_status in [
                "paid",
                "partial",
            ]

        # ==========================
        # Order Status
        # ==========================

        status = request.POST.get(
            "status"
        )

        if status:

            order.status = status

        # ==========================
        # Save Order
        # ==========================

        order.save()

        # ==========================
        # Timeline
        # ==========================

        note = request.POST.get(
            "note"
        )

        if note:

            OrderTimeline.objects.create(

                order=order,

                user=request.user,

                note=note,

            )

        # ==========================
        # Send Email ONLY if status changed
        # ==========================

        if old_status != order.status:

            from payments.utils import (
                send_shipping_email,
                send_delivered_email,
                send_cancelled_email,
            )

            if order.status == "shipped":
                send_shipping_email(request, order)

            elif order.status == "delivered":
                send_delivered_email(request, order)

            elif order.status == "cancelled":
                send_cancelled_email(request, order)

        # ==========================
        # Success Message
        # ==========================

        messages.success(

            request,

            "Order updated successfully."

        )

        return redirect(

            "dashboard:dashboard_order_detail",

            order.id,

        )

    return render(

        request,

        "dashboard/order_detail.html",

        {

            "order": order,

        },

    )

@owner_or_staff_required
def dashboard_orders(request):

    orders = (
        Order.objects
        .select_related("user")
        .order_by("-created_at")
    )

    return render(
        request,
        "dashboard/orders.html",
        {
            "orders": orders,
        },
    )

@owner_or_staff_required
def low_stock_report(request):

    products = Product.objects.filter(stock__lte=5)

    return render(
        request,
        "dashboard/low_stock_report.html",
        {
            "products": products,
        },
    )


@owner_or_staff_required
def dashboard_customers(request):

    customers = (
        User.objects.filter(
            role="customer",
        ).only(
            "id",
            "username",
            "email",
            "date_joined",
        )
        .annotate(
            total_orders=Count("orders"),
            total_spent=Sum("orders__final_total"),
        )
        .order_by("-date_joined")
    )

    return render(
        request,
        "dashboard/customers.html",
        {
            "customers": customers,
        },
    )


@owner_or_staff_required
def dashboard_customer_detail(request, user_id):

    customer = get_object_or_404(
        User,
        id=user_id,
        role="customer",
    )

    orders = customer.orders.select_related(
        "coupon",
    ).order_by(
        "-created_at",
    )

    total_spent = (
        orders.filter(
            paid=True,
            status="delivered",
        ).aggregate(
            total=Sum("final_total"),
        )["total"] or 0
    )

    context = {

        "customer": customer,

        "orders": orders,

        "total_spent": total_spent,

    }

    return render(
        request,
        "dashboard/customer_detail.html",
        context,
    )