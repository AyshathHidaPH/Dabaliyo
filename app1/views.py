from django.shortcuts import render,redirect, get_object_or_404
from django.http import HttpResponse
from django.db.models import Q
from django.contrib.auth.models import User
from django.contrib.auth import authenticate,login as login_user,logout as auth_logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from products.models import Product, Brand
from cart.models import Wishlist, Cart, CartItem
from django.contrib.auth.decorators import user_passes_test
from .models import Profile
from decimal import Decimal
from datetime import timedelta
from django.db.models import Sum
from django.db.models.functions import TruncDate
from django.utils import timezone
from products.models import Product
from order.models import Order, OrderItem


def staff_required(view_func):

    return user_passes_test(
        lambda user: user.is_authenticated and user.is_staff,
        login_url="admin_panel"
    )(view_func)

def home(request):
    products = Product.objects.all().order_by('-id')[:4]
    featured_products = Product.objects.all().order_by('-id')[:4]
    wishlist_product_ids=[]
    if request.user.is_authenticated:
        wishlist_product_ids = list(
            Wishlist.objects.filter(
                user=request.user
            ).values_list('product_id', flat=True)
        )
    return render(request, 'user/home.html', {
        'products': products,
        'featured_products' : featured_products,
        'wishlist_product_ids':wishlist_product_ids,
            })



def productpage(request):

    products = Product.objects.all()


    search = request.GET.get('search', '').strip()

    if search:
        products = products.filter(
            Q(name__icontains=search) |
            Q(brand__name__icontains=search)
        )

  

    brand = request.GET.get('brand', '').strip()

    if brand:
        products = products.filter(
            brand__name__iexact=brand
        )



    available_brands = Brand.objects.all()

    context = {
        'products': products,
        'available_brands': available_brands,
        'search': search,
        'selected_brand': brand,
    }

    return render(
        request,
        'user/productpage.html',
        context
    )

def contact(request):
    return render(request, "user/contact.html")



def productdescription(request, id):

    product = get_object_or_404(
        Product,
        id=id
    )


    is_in_wishlist = False


    if request.user.is_authenticated:

        is_in_wishlist = Wishlist.objects.filter(
            user=request.user,
            product=product
        ).exists()


    context = {

        "product": product,

        "is_in_wishlist": is_in_wishlist,

    }


    return render(
        request,
        "user/productdescription.html",
        context
    )

def login(request):
    if request.method=='POST':
        username=request.POST.get('username')
        password=request.POST.get('password')
        # print(username,password)

        user = authenticate(username=username,password=password)
        # print(user)

        if user is not None:
            login_user(request,user)
            messages.success(request,"Login successful")
            return redirect('home')
        else:
            messages.error(request,"Invalid username or password")
        return redirect('login')
    return render(request, 'user/login.html')


def logout(request):

    if request.method == "POST":

        auth_logout(request)

        messages.success(
            request,
            "Logged out successfully!"
        )

    return redirect("home")


@login_required
def edit_profile(request):

    # Get existing profile or create one
    profile, created = Profile.objects.get_or_create(
        user=request.user
    )
    print(request.user,profile)

    if request.method == "POST":

       

        request.user.first_name = request.POST.get(
            "first_name", ""
        )

        request.user.last_name = request.POST.get(
            "last_name", ""
        )

        request.user.email = request.POST.get(
            "email", ""
        )

        request.user.save()




        profile.phone = request.POST.get(
            "phone", ""
        )

        profile.location = request.POST.get(
            "location", ""
        )

        profile.postal_code = request.POST.get(
            "postal_code", ""
        )



        if request.FILES.get("profile_image"):

            profile.profile_image = request.FILES[
                "profile_image"
            ]


        profile.save()


        return redirect("home")


    return render(
        request,
        "user/edit_profile.html"
    )
def register(request):
    if request.method=='POST':

        username=request.POST.get('username')
        email=request.POST.get('email')
        password=request.POST.get('password')

        if User.objects.filter(username=username).exists():
            messages.error(request,"username already exists")
            return redirect('login')

        print(username,email,password)

        User.objects.create_user(username=username,password=password,email=email)

        messages.success(request,"Account created successfully")
        return redirect('login')
    return render(request, 'user/login.html')


def admin_panel(request):

    if request.user.is_authenticated and request.user.is_staff:
        return redirect("admin_dashboard")

    if request.method == "POST":

        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user is not None and user.is_staff:

            login_user(request, user)

            return redirect("dashboard")

        messages.error(
            request,
            "Invalid username or password."
        )

    return render(
        request,
        "main/admin.html"
    )

# =========================================================
# ADMIN DASHBOARD
# =========================================================

@staff_required
def dashboard(request):
    total_orders = Order.objects.count()

    total_customers = User.objects.filter(is_staff=False).count()

    out_of_stock = Product.objects.filter(stock=0).count()

    low_stock = Product.objects.filter(
        stock__gt=0,
        stock__lte=5
    ).count()

    valid_orders = Order.objects.exclude(status="Cancelled")

    revenue = (
        valid_orders.aggregate(total=Sum("grand_total"))["total"]
        or Decimal("0.00")
    )

    profit = Decimal("0.00")

    order_items = (
        OrderItem.objects.filter(
            order__status__in=[
                "Pending",
                "Confirmed",
                "Shipped",
                "Delivered"
            ],
            product__isnull=False
        )
        .select_related("product")
    )

    for item in order_items:
        selling_amount = item.price * item.quantity
        cost_amount = item.product.cost_price * item.quantity
        profit += selling_amount - cost_amount

    recent_orders = (
        Order.objects
        .select_related("user", "address")
        .prefetch_related("items", "items__product")
        .order_by("-created_at")[:7]
    )

    inventory_alerts = (
        Product.objects
        .filter(stock__lte=5)
        .select_related("brand", "storage")
        .order_by("stock")[:8]
    )

    pending_orders = Order.objects.filter(status="Pending").count()
    confirmed_orders = Order.objects.filter(status="Confirmed").count()
    shipped_orders = Order.objects.filter(status="Shipped").count()
    delivered_orders = Order.objects.filter(status="Delivered").count()
    cancelled_orders = Order.objects.filter(status="Cancelled").count()

    # Last 7 days sales
    today = timezone.localdate()
    start_date = today - timedelta(days=6)

    daily_sales = (
        valid_orders
        .filter(
            created_at__date__gte=start_date,
            created_at__date__lte=today
        )
        .annotate(day=TruncDate("created_at"))
        .values("day")
        .annotate(total=Sum("grand_total"))
        .order_by("day")
    )

    sales_data = {
        item["day"].strftime("%d %b"): float(item["total"] or 0)
        for item in daily_sales
    }

    chart_labels = []
    chart_values = []

    for i in range(7):
        current_date = start_date + timedelta(days=i)

        label = current_date.strftime("%d %b")

        chart_labels.append(label)
        chart_values.append(
            sales_data.get(label, 0)
        )

    context = {
        "total_orders": total_orders,
        "total_customers": total_customers,
        "revenue": revenue,
        "profit": profit,
        "out_of_stock": out_of_stock,
        "low_stock": low_stock,

        "recent_orders": recent_orders,
        "inventory_alerts": inventory_alerts,

        "pending_orders": pending_orders,
        "confirmed_orders": confirmed_orders,
        "shipped_orders": shipped_orders,
        "delivered_orders": delivered_orders,
        "cancelled_orders": cancelled_orders,

        "chart_labels": chart_labels,
        "chart_values": chart_values,
    }

    return render(
        request,
        "main/dashboard.html",
        context
    )
