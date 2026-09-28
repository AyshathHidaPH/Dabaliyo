from decimal import Decimal
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from .models import Address
from .models import Order, OrderItem, Address, ShippingAddress
from cart.models import Cart
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.models import User
# from django.db.models import Sum, Count, F, DecimalField, ExpressionWrapper
# from django.db.models.functions import TruncDate
# from datetime import timedelta
# from django.utils import timezone
# from products.models import Product



# =========================================================
# PLACE ORDER
# =========================================================
# Checkout page -> Select Address
# This function does NOT create the order.
# =========================================================
def staff_required(view_func):

    return user_passes_test(
        lambda user: user.is_authenticated and user.is_staff,
        login_url="admin_panel"
    )(view_func)

@login_required
@transaction.atomic
def place_order(request):

    # =========================================================
    # ONLY POST REQUEST
    # =========================================================

    if request.method != "POST":
        return redirect("select_address")


    # =========================================================
    # GET USER'S CART
    # =========================================================

    cart = get_object_or_404(
        Cart,
        user=request.user
    )

    cart_items = cart.items.select_related("product").all()


    # =========================================================
    # CHECK EMPTY CART
    # =========================================================

    if not cart_items.exists():

        messages.error(
            request,
            "Your cart is empty."
        )

        return redirect("cart")


    # =========================================================
    # GET SELECTED ADDRESS
    # =========================================================

    address_id = request.POST.get("address_id")


    if not address_id:

        messages.error(
            request,
            "Please select a delivery address."
        )

        return redirect("select_address")


    # =========================================================
    # GET ADDRESS
    # Only allow user's own address
    # =========================================================

    address = get_object_or_404(
        Address,
        id=address_id,
        user=request.user
    )


    # =========================================================
    # CALCULATE SUBTOTAL
    # =========================================================

    subtotal = Decimal("0.00")


    for item in cart_items:

        product = item.product

        # -----------------------------------------------------
        # Check product still exists
        # -----------------------------------------------------

        if not product:

            messages.error(
                request,
                "One of the products in your cart is no longer available."
            )

            return redirect("cart")


        # -----------------------------------------------------
        # CHECK STOCK
        # -----------------------------------------------------

        if item.quantity > product.stock:

            messages.error(
                request,
                f"Only {product.stock} units of "
                f"{product.name} are available."
            )

            return redirect("cart")


        # -----------------------------------------------------
        # PRODUCT PRICE
        # -----------------------------------------------------

        if (
            product.discount_price is not None
            and product.discount_price > 0
        ):

            price = product.discount_price

        else:

            price = product.price


        # -----------------------------------------------------
        # ITEM TOTAL
        # -----------------------------------------------------

        item_total = price * item.quantity

        subtotal += item_total


    # =========================================================
    # SHIPPING
    # =========================================================

    # Change this value if you want paid shipping.
    # Example:
    # shipping = Decimal("50.00")

    shipping = Decimal("0.00")


    # =========================================================
    # GRAND TOTAL
    # =========================================================

    grand_total = subtotal + shipping


    # =========================================================
    # CREATE ORDER
    # =========================================================

    order = Order.objects.create(

        user=request.user,

        address=address,

        subtotal=subtotal,

        shipping=shipping,

        grand_total=grand_total,

        status="Confirmed",
    )


    # =========================================================
    # CREATE SHIPPING ADDRESS
    #
    # We copy the address here so that even if the user later
    # edits/deletes their saved address, the order still keeps
    # the original delivery information.
    # =========================================================

    ShippingAddress.objects.create(

        order=order,

        name=address.name,

        phone=address.phone,

        email=address.email,

        address=address.address,

        landmark=address.landmark,

        city=address.city,

        state=address.state,

        pincode=address.pincode,

        address_type=address.address_type,
    )


    # =========================================================
    # CREATE ORDER ITEMS
    # =========================================================

    for item in cart_items:

        product = item.product


        # -----------------------------------------------------
        # PRICE
        # -----------------------------------------------------

        if (
            product.discount_price is not None
            and product.discount_price > 0
        ):

            price = product.discount_price

        else:

            price = product.price


        # -----------------------------------------------------
        # TOTAL
        # -----------------------------------------------------

        item_total = price * item.quantity


        # -----------------------------------------------------
        # CREATE ORDER ITEM
        # -----------------------------------------------------

        OrderItem.objects.create(

            order=order,

            product=product,

            product_name=product.name,

            price=price,

            quantity=item.quantity,

            total=item_total,
        )


        # -----------------------------------------------------
        # REDUCE STOCK
        # -----------------------------------------------------

        product.stock -= item.quantity

        product.save(update_fields=["stock"])


    # =========================================================
    # CLEAR CART
    # =========================================================

    cart.items.all().delete()


    # =========================================================
    # SUCCESS MESSAGE
    # =========================================================

    messages.success(
        request,
        "Your order has been placed successfully."
    )


    # =========================================================
    # REDIRECT TO ORDER SUCCESS PAGE
    # =========================================================

    return redirect(
        "order_success",
        order_id=order.id
    )
@login_required
@transaction.atomic
def confirm_order(request):

    if request.method != "POST":
        return redirect("select_address")

    # -----------------------------------------------------
    # GET SELECTED ADDRESS
    # -----------------------------------------------------

    address_id = request.POST.get("address_id")

    if not address_id:
        messages.error(
            request,
            "Please select a delivery address."
        )
        return redirect("select_address")

    address = get_object_or_404(
        Address,
        id=address_id,
        user=request.user
    )

    # -----------------------------------------------------
    # GET CART
    # -----------------------------------------------------

    cart = get_object_or_404(
        Cart,
        user=request.user
    )

    cart_items = list(
        cart.items.select_related("product")
    )

    if not cart_items:
        messages.error(
            request,
            "Your cart is empty."
        )
        return redirect("cart")

    # -----------------------------------------------------
    # CHECK STOCK FIRST
    # -----------------------------------------------------
    # IMPORTANT:
    # Do this BEFORE creating the Order.
    # -----------------------------------------------------

    for item in cart_items:

        if item.quantity > item.product.stock:

            messages.error(
                request,
                f"Only {item.product.stock} unit(s) of "
                f"{item.product.name} are available."
            )

            return redirect("cart")

    # -----------------------------------------------------
    # CALCULATE SUBTOTAL
    # -----------------------------------------------------

    subtotal = Decimal("0.00")

    for item in cart_items:

        if item.product.discount_price:
            price = item.product.discount_price
        else:
            price = item.product.price

        subtotal += (
            Decimal(str(price)) * item.quantity
        )

    # -----------------------------------------------------
    # SHIPPING
    # -----------------------------------------------------

    shipping = Decimal("50.00")

    grand_total = subtotal + shipping

    # -----------------------------------------------------
    # CREATE ORDER
    # -----------------------------------------------------

    order = Order.objects.create(
        user=request.user,
        address=address,
        subtotal=subtotal,
        shipping=shipping,
        grand_total=grand_total,
        status="Confirmed"
    )

    # -----------------------------------------------------
    # CREATE ORDER ITEMS
    # -----------------------------------------------------

    for item in cart_items:

        if item.product.discount_price:
            price = item.product.discount_price
        else:
            price = item.product.price

        total = (
            Decimal(str(price)) * item.quantity
        )

        OrderItem.objects.create(
            order=order,
            product=item.product,
            product_name=item.product.name,
            price=price,
            quantity=item.quantity,
            total=total
        )

    # -----------------------------------------------------
    # REDUCE PRODUCT STOCK
    # -----------------------------------------------------

    for item in cart_items:

        item.product.stock -= item.quantity

        item.product.save(
            update_fields=["stock"]
        )

    # -----------------------------------------------------
    # CREATE SHIPPING ADDRESS SNAPSHOT
    # -----------------------------------------------------

    ShippingAddress.objects.create(
        order=order,
        name=address.name,
        phone=address.phone,
        email=address.email,
        address=address.address,
        landmark=address.landmark,
        city=address.city,
        state=address.state,
        pincode=address.pincode,
        address_type=address.address_type
    )

    # -----------------------------------------------------
    # CLEAR CART
    # -----------------------------------------------------

    cart.items.all().delete()

    # -----------------------------------------------------
    # ORDER SUCCESS
    # -----------------------------------------------------

    return redirect(
        "order_success",
        order_id=order.id
    )


# =========================================================
# ORDER SUCCESS
# =========================================================

@login_required
def order_success(request, order_id):

    order = get_object_or_404(
        Order,
        id=order_id,
        user=request.user
    )

    return render(
        request,
        "user/order_success.html",
        {
            "order": order,
            "total": order.grand_total,
        }
    )

# =========================================================
# CALCULATE SUBTOTAL
# =========================================================

def calculate_subtotal(cart_items):

    subtotal = Decimal("0.00")

    for item in cart_items:

        if item.product.discount_price:
            price = item.product.discount_price
        else:
            price = item.product.price

        subtotal += (
            Decimal(str(price)) * item.quantity
        )

    return subtotal


# =========================================================
# SELECT ADDRESS
# =========================================================

@login_required
def select_address(request):

    addresses = Address.objects.filter(
        user=request.user
    ).order_by("-is_default", "-id")

    # Get user's cart
    cart, created = Cart.objects.get_or_create(
        user=request.user
    )

    cart_items = cart.items.select_related("product").all()

    # Calculate subtotal
    subtotal = 0

    for item in cart_items:

        if item.product.discount_price:
            price = item.product.discount_price
        else:
            price = item.product.price

        subtotal += price * item.quantity

    # Shipping
    if subtotal > 0:
        shipping = 0
    else:
        shipping = 0

    grand_total = subtotal + shipping

    return render(
        request,
        "user/checkout.html",
        {
            "addresses": addresses,
            "cart_items": cart_items,
            "subtotal": subtotal,
            "shipping": shipping,
            "grand_total": grand_total,
        }
    )

# =========================================================
# ADD ADDRESS
# =========================================================


@login_required
def add_address(request):

    if request.method == "POST":

        Address.objects.create(
            user=request.user,
            name=request.POST.get("name"),
            phone=request.POST.get("phone"),
            address=request.POST.get("address"),
            city=request.POST.get("city"),
            state=request.POST.get("state"),
            pincode=request.POST.get("pincode"),
            landmark=request.POST.get("landmark"),
        )

        return redirect("select_address")

    return render(
        request,
        "user/add_address.html"
    )
# =========================================================
# EDIT ADDRESS
# =========================================================

@login_required
def edit_address(request, address_id):

    address = get_object_or_404(
        Address,
        id=address_id,
        user=request.user
    )

    if request.method == "POST":

        address.name = request.POST.get("name")
        address.phone = request.POST.get("phone")
        address.email = request.POST.get("email")
        address.address = request.POST.get("address")
        address.landmark = request.POST.get("landmark")
        address.city = request.POST.get("city")
        address.state = request.POST.get("state")
        address.pincode = request.POST.get("pincode")
        address.address_type = request.POST.get(
            "address_type",
            "Home"
        )

        address.is_default = (
            request.POST.get("is_default") == "on"
        )

        address.save()

        return redirect("select_address")

    return render(
        request,
        "user/add_address.html",
        {
            "address": address,
            "edit_mode": True,
        }
    )

# =========================================================
# DELETE ADDRESS
# =========================================================

@login_required
def delete_address(request, address_id):

    # if request.method != "POST":
    #     return redirect("select_address")

    address = get_object_or_404(
        Address,
        id=address_id,
        user=request.user
    )

    address.delete()

    return redirect("checkout")



@login_required
def my_orders(request):

    orders = Order.objects.filter(
        user=request.user
    ).prefetch_related(
        "items",
        "items__product"
    ).order_by("-created_at")

    return render(
        request,
        "user/my_orders.html",
        {
            "orders": orders
        }
    )



@login_required
def order_details(request, order_id):

    order = get_object_or_404(
        Order.objects.prefetch_related("items__product"),
        id=order_id,
        user=request.user
    )

    return render(
        request,
        "user/order_details.html",
        {
            "order": order,
        }
    )

@login_required
def user_order_detail(request, order_id):

    order = get_object_or_404(
        Order.objects.prefetch_related(
            "items",
            "items__product"
        ),
        id=order_id,
        user=request.user
    )

    return render(
        request,
        "user/order_details.html",
        {
            "order": order
        }
    )

# =========================================================
# CANCEL ORDER
# =========================================================

@login_required
def cancel_order(request, order_id):

    # Only allow POST request
    if request.method != "POST":
        return redirect("my_orders")

    # Get only the logged-in user's order
    order = get_object_or_404(
        Order,
        id=order_id,
        user=request.user
    )

    # -----------------------------------------------------
    # CANNOT CANCEL AFTER DELIVERED
    # -----------------------------------------------------

    if order.status == "Delivered":

        messages.error(
            request,
            "This order cannot be cancelled because it has already been delivered."
        )

        return redirect("my_orders")

    # -----------------------------------------------------
    # ALREADY CANCELLED
    # -----------------------------------------------------

    if order.status == "Cancelled":

        messages.info(
            request,
            "This order has already been cancelled."
        )

        return redirect("my_orders")

    # -----------------------------------------------------
    # CANCEL ORDER
    # -----------------------------------------------------

    order.status = "Cancelled"

    order.save(
        update_fields=["status"]
    )

    messages.success(
        request,
        f"Order #{order.id} has been cancelled successfully."
    )

    return redirect("my_orders")

# =========================================================
# ADMIN ORDERS
# =========================================================

@staff_required
def admin_orders(request):

    orders = (
        Order.objects
        .select_related(
            "user",
            "address"
        )
        .prefetch_related(
            "items",
            "items__product"
        )
        .order_by("-created_at")
    )

    return render(
        request,
        "main/orders.html",
        {
            "orders": orders
        }
    )


# =========================================================
# ADMIN ORDER DETAIL
# =========================================================

@staff_required
def admin_order_detail(request, order_id):

    order = get_object_or_404(
        Order.objects
        .select_related(
            "user",
            "address"
        )
        .prefetch_related(
            "items",
            "items__product"
        ),
        id=order_id
    )

    return render(
        request,
        "main/order_details.html",
        {
            "order": order
        }
    )


# =========================================================
# UPDATE ORDER STATUS
# =========================================================

@staff_required
def update_order_status(request, order_id):

    order = get_object_or_404(
        Order,
        id=order_id
    )

    if request.method == "POST":

        status = request.POST.get("status")

        valid_statuses = [
            choice[0]
            for choice in Order.STATUS_CHOICES
        ]

        if status in valid_statuses:

            order.status = status
            order.save(update_fields=["status"])

    return redirect(
        "admin_order_detail",
        order_id=order.id
    )
# =========================================================
# ADMIN DASHBOARD
# =========================================================

# @staff_required
# def admin_dashboard(request):

#     # =====================================================
#     # BASIC COUNTS
#     # =====================================================

#     total_orders = Order.objects.count()

#     total_customers = User.objects.filter(
#         is_staff=False
#     ).count()

#     out_of_stock = Product.objects.filter(
#         stock=0
#     ).count()

#     low_stock = Product.objects.filter(
#         stock__gt=0,
#         stock__lte=5
#     ).count()


#     # =====================================================
#     # REVENUE
#     # Cancelled orders are not included
#     # =====================================================

#     valid_orders = Order.objects.exclude(
#         status="Cancelled"
#     )

#     revenue = valid_orders.aggregate(
#         total=Sum("grand_total")
#     )["total"] or Decimal("0.00")


#     # =====================================================
#     # PROFIT
#     #
#     # Selling price - cost price
#     # =====================================================

#     profit = Decimal("0.00")

#     order_items = OrderItem.objects.filter(
#         order__status__in=[
#             "Pending",
#             "Confirmed",
#             "Shipped",
#             "Delivered"
#         ],
#         product__isnull=False
#     ).select_related("product")


#     for item in order_items:

#         selling_total = (
#             item.price * item.quantity
#         )

#         cost_total = (
#             item.product.cost_price *
#             item.quantity
#         )

#         profit += (
#             selling_total - cost_total
#         )


#     # =====================================================
#     # RECENT ORDERS
#     # =====================================================

#     recent_orders = (
#         Order.objects
#         .select_related(
#             "user",
#             "address"
#         )
#         .prefetch_related(
#             "items",
#             "items__product"
#         )
#         .order_by("-created_at")[:7]
#     )


#     # =====================================================
#     # INVENTORY ALERTS
#     # =====================================================

#     inventory_alerts = (
#         Product.objects
#         .select_related(
#             "brand",
#             "storage"
#         )
#         .filter(stock__lte=5)
#         .order_by("stock")[:8]
#     )


#     # =====================================================
#     # SALES CHART - LAST 7 DAYS
#     # =====================================================

#     today = timezone.localdate()

#     start_date = today - timedelta(days=6)


#     daily_sales = (
#         valid_orders
#         .filter(
#             created_at__date__gte=start_date,
#             created_at__date__lte=today
#         )
#         .annotate(
#             day=TruncDate("created_at")
#         )
#         .values("day")
#         .annotate(
#             total=Sum("grand_total")
#         )
#         .order_by("day")
#     )


#     sales_data = {
#         item["day"].strftime("%d %b"): float(
#             item["total"] or 0
#         )
#         for item in daily_sales
#     }


#     chart_labels = []

#     chart_values = []


#     for i in range(7):

#         current_date = (
#             start_date +
#             timedelta(days=i)
#         )

#         label = current_date.strftime("%d %b")

#         chart_labels.append(label)

#         chart_values.append(
#             sales_data.get(label, 0)
#         )


#     # =====================================================
#     # ORDER STATUS COUNTS
#     # =====================================================

#     pending_orders = Order.objects.filter(
#         status="Pending"
#     ).count()

#     confirmed_orders = Order.objects.filter(
#         status="Confirmed"
#     ).count()

#     shipped_orders = Order.objects.filter(
#         status="Shipped"
#     ).count()

#     delivered_orders = Order.objects.filter(
#         status="Delivered"
#     ).count()

#     cancelled_orders = Order.objects.filter(
#         status="Cancelled"
#     ).count()


#     # =====================================================
#     # CONTEXT
#     # =====================================================

#     context = {

#         "total_orders": total_orders,

#         "total_customers": total_customers,

#         "revenue": revenue,

#         "profit": profit,

#         "out_of_stock": out_of_stock,

#         "low_stock": low_stock,

#         "recent_orders": recent_orders,

#         "inventory_alerts": inventory_alerts,

#         "pending_orders": pending_orders,

#         "confirmed_orders": confirmed_orders,

#         "shipped_orders": shipped_orders,

#         "delivered_orders": delivered_orders,

#         "cancelled_orders": cancelled_orders,

#         "chart_labels": chart_labels,

#         "chart_values": chart_values,
#     }


#     return render(
#         request,
#         "main/dashboard.html",
#         context
#     )