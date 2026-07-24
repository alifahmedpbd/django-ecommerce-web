from django.shortcuts import render, get_object_or_404, redirect
from .models import Order, ReturnRequest, OrderTimeline
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import (
    SimpleDocTemplate,
    Table,
    TableStyle,
    Paragraph,
    Spacer,
)
from django.contrib import messages
from .services import restore_order_stock
from django.db import transaction
from .forms import GuestOrderTrackingForm
# Create your views here.

def order_success(request, order_id):

    order = get_object_or_404(
        Order.objects.only(
            "id",
            "full_name",
            "payment_method",
            "final_total",
            "status",
        ),
        id=order_id,
    )

    return render(request, "orders/order_success.html", {"order": order })

@login_required
def order_list(request):

    orders = Order.objects.filter(
        user=request.user,
    ).order_by("-created_at")

    status = request.GET.get("status")

    payment = request.GET.get("payment")

    paid = request.GET.get("paid")

    q = request.GET.get("q")

    if status:
        orders = orders.filter(status=status)

    if payment:
        orders = orders.filter(payment_method=payment)

    if paid == "yes":
        orders = orders.filter(paid=True)

    elif paid == "no":
        orders = orders.filter(paid=False)

    if q:
        orders = orders.filter(id__icontains=q)

    context = {
        "orders": orders,
    }

    return render(
        request,
        "orders/order_list.html",
        context,
    )

def order_detail(request, order_id):

    order = get_object_or_404(

        Order.objects.prefetch_related(

            "items__product",

            "timeline",

        ),

        id=order_id,

    )

    if request.user.is_authenticated:

        if order.user:

            if order.user != request.user and not request.user.is_staff:

                messages.error(

                    request,

                    "You are not allowed to view this order.",

                )

                return redirect("orders:order_list")

    else:

        email = request.GET.get("email")

        if email != order.email:

            messages.error(

                request,

                "Invalid order access.",

            )

            return redirect("orders:track_order")

    timeline = order.timeline.all().order_by(

        "created_at"

    )

    context = {

        "order": order,

        "timeline": timeline,

    }

    return render(

        request,

        "orders/order_detail.html",

        context,

    )


@login_required
def invoice_pdf(request, order_id):

    # ==========================================
    # Get Order
    # ==========================================

    order = get_object_or_404(
        Order.objects.prefetch_related(
            "items__product",
        ),
        id=order_id,
        user=request.user,
    )

    # ==========================================
    # Create PDF Response
    # ==========================================

    response = HttpResponse(
        content_type="application/pdf"
    )

    response["Content-Disposition"] = (
        f'attachment; filename="invoice_{order.id}.pdf"'
    )

    # ==========================================
    # PDF Document
    # ==========================================

    doc = SimpleDocTemplate(response)

    styles = getSampleStyleSheet()

    title_style = styles["Title"]
    heading_style = styles["Heading2"]
    normal_style = styles["Normal"]
    italic_style = styles["Italic"]

    elements = []

    # ==========================================
    # Shopora Header
    # ==========================================

    elements.append(
        Paragraph(
            "<b>SHOPORA</b>",
            title_style,
        )
    )

    elements.append(
        Paragraph(
            "Shop More, Pay Less",
            heading_style,
        )
    )

    elements.append(Spacer(1, 10))

    elements.append(
        Paragraph(
            "Website : www.shopora.com",
            normal_style,
        )
    )

    elements.append(
        Paragraph(
            "Email : support@shopora.com",
            normal_style,
        )
    )

    elements.append(
        Paragraph(
            "Phone : +880 1700-000000",
            normal_style,
        )
    )

    elements.append(Spacer(1, 20))

    # ==========================================
    # Invoice Information
    # ==========================================

    elements.append(
        Paragraph(
            f"<b>Invoice ID :</b> #{order.id}",
            normal_style,
        )
    )

    elements.append(
        Paragraph(
            f"<b>Date :</b> {order.created_at.strftime('%d %B %Y')}",
            normal_style,
        )
    )

    elements.append(
        Paragraph(
            f"<b>Payment Method :</b> {order.payment_method.title()}",
            normal_style,
        )
    )

    elements.append(
        Paragraph(
            f"<b>Payment Status :</b> {'Paid' if order.paid else 'Unpaid'}",
            normal_style,
        )
    )

    elements.append(
        Paragraph(
            f"<b>Transaction ID :</b> {order.payment_id or 'N/A'}",
            normal_style,
        )
    )

    elements.append(Spacer(1, 20))

    # ==========================================
    # Customer Information
    # ==========================================

    elements.append(
        Paragraph(
            "<b>Customer Details</b>",
            styles["Heading3"],
        )
    )

    elements.append(
        Paragraph(
            f"Name : {order.full_name}",
            normal_style,
        )
    )

    elements.append(
        Paragraph(
            f"Email : {order.email}",
            normal_style,
        )
    )

    elements.append(
        Paragraph(
            f"Phone : {order.phone}",
            normal_style,
        )
    )

    elements.append(
        Paragraph(
            f"Address : {order.address}",
            normal_style,
        )
    )

    elements.append(Spacer(1, 25))

        # ==========================================
    # Products Table
    # ==========================================

    data = [

        [
            "Product",
            "Unit Price",
            "Quantity",
            "Subtotal",
        ]

    ]

    items = order.items.select_related("product")

    for item in items:

        data.append(

            [

                item.product.name,

                f"${item.price}",

                str(item.quantity),

                f"${item.get_total_price()}",

            ]

        )

    # ==========================================
    # Grand Total Row
    # ==========================================

    data.append(

        [

            "",

            "",

            "Grand Total",

            f"${order.final_total}"

        ]

    )

    table = Table(

        data,

        colWidths=[220, 90, 70, 100]

    )

    # ==========================================
    # Professional Table Style
    # ==========================================

    table.setStyle(

        TableStyle([

            # -----------------------------
            # Header
            # -----------------------------

            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0d6efd")),

            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),

            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),

            ("FONTSIZE", (0, 0), (-1, 0), 11),

            ("BOTTOMPADDING", (0, 0), (-1, 0), 12),

            ("ALIGN", (0, 0), (-1, -1), "CENTER"),

            # -----------------------------
            # Body
            # -----------------------------

            ("BACKGROUND", (0, 1), (-1, -2), colors.whitesmoke),

            ("FONTNAME", (0, 1), (-1, -2), "Helvetica"),

            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),

            # -----------------------------
            # Grand Total
            # -----------------------------

            ("BACKGROUND", (0, -1), (-1, -1), colors.HexColor("#dbeafe")),

            ("FONTNAME", (0, -1), (-1, -1), "Helvetica-Bold"),

            ("TEXTCOLOR", (0, -1), (-1, -1), colors.black),

            ("FONTSIZE", (0, -1), (-1, -1), 11),

            ("BOTTOMPADDING", (0, -1), (-1, -1), 10),

        ])

    )

    elements.append(table)

    # ==========================================
    # Footer
    # ==========================================

    elements.append(Spacer(1, 30))

    elements.append(

        Paragraph(

            "<b>Thank you for shopping with Shopora ❤️</b>",

            heading_style,

        )

    )

    elements.append(

        Paragraph(

            "We truly appreciate your purchase and hope to see you again.",

            italic_style,

        )

    )

    elements.append(Spacer(1, 10))

    elements.append(

        Paragraph(

            "This invoice was automatically generated by Shopora.",

            italic_style,

        )

    )

    # ==========================================
    # Build PDF
    # ==========================================

    doc.build(elements)

    return response

# ==========================================
# Cancel Order
# ==========================================

@login_required
def cancel_order(request, order_id):

    order = get_object_or_404(
        Order.objects.prefetch_related(
            "items__product",
        ),
        id=order_id,
        user=request.user,
    )

    if order.status in [

        "pending",

        "processing",

    ]:
        with transaction.atomic():

            restore_order_stock(order)

            order.status = "cancelled"

            order.save(update_fields=["status"])

            OrderTimeline.objects.create(
                order=order, user=request.user, note="Customer cancelled this order.")

        messages.success(

            request,

            "Your order has been cancelled successfully."

        )

    else:

        messages.error(

            request,

            "This order can no longer be cancelled."

        )

    return redirect(

        "orders:order_detail",

        order.id,

    )
def track_order(request):

    form = GuestOrderTrackingForm()

    order = None

    timeline = None

    current_step = 0

    status_steps = [

        "pending",

        "processing",

        "shipped",

        "delivered",

    ]

    if request.method == "POST":

        form = GuestOrderTrackingForm(request.POST)

        if form.is_valid():

            order_id = form.cleaned_data["order_id"]

            email = form.cleaned_data["email"]

            try:

                order = Order.objects.prefetch_related(
                    "timeline"
                ).get(

                    id=order_id,

                    email=email,

                )

                timeline = order.timeline.all().order_by("-created_at")

                if order.status in status_steps:

                    current_step = status_steps.index(order.status)

            except Order.DoesNotExist:

                messages.error(

                    request,

                    "Order not found.",

                )

    return render(

        request,

        "orders/track_order.html",

        {

            "form": form,

            "order": order,

            "timeline": timeline,

            "current_step": current_step,

            "status_steps": status_steps,

        },

    )

@login_required
def return_request(request, order_id):

    order = get_object_or_404(
        Order,
        id=order_id,
        user=request.user,
    )

    if order.status != "delivered":

        messages.error(
            request,
            "Only delivered orders can be returned.",
        )

        return redirect(
            "orders:order_detail",
            order.id,
        )

    if hasattr(order, "return_request"):

        messages.warning(
            request,
            "Return request already submitted.",
        )

        return redirect(
            "orders:order_detail",
            order.id,
        )

    if request.method == "POST":

        reason = request.POST.get("reason")

        if not reason:

            messages.error(
                request,
                "Return reason is required.",
            )

            return redirect(
                "orders:return_request",
                order.id,
            )

        ReturnRequest.objects.create(

            order=order,

            user=request.user,

            reason=reason,

            refund_amount=order.final_total,

        )

        OrderTimeline.objects.create(

            order=order,

            user=request.user,

            created_by=request.user.username,

            note="↩ Customer requested a return.",

        )

        messages.success(

            request,

            "Return request submitted successfully.",

        )

        return redirect(
            "orders:order_detail",
            order.id,
        )

    return render(

        request,

        "orders/return_request.html",

        {

            "order": order,

        },

    )