from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Product, Brand, Color, Storage
from django.contrib.auth.models import User
from django.contrib.admin.views.decorators import staff_member_required
from django.urls import path
from .models import Product
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import user_passes_test
import json
from django.http import JsonResponse



def staff_required(view_func):

    return user_passes_test(
        lambda user: user.is_authenticated and user.is_staff,
        login_url="admin_panel"
    )(view_func)

@staff_required
def product_dashboard(request):
    products = Product.objects.all()
    return render(request, "main/product_dashboard.html", {
        "products": products
    })


def product_add(request):
    brands = Brand.objects.all()
    colors = Color.objects.all()
    storages = Storage.objects.all()
    if request.method == "POST":
        name = request.POST.get("name")
        price = request.POST.get("price")
        stock = request.POST.get("stock")
        description = request.POST.get("description")
        brand = request.POST.get("brand")
        color = request.POST.get("color")
        storage = request.POST.get("storage")
        image = request.FILES.get("photo")
        if not name:
            messages.error(request, "Please enter the product name.")
            return redirect("product_add")
        if not price:
            messages.error(request, "Please enter the price.")
            return redirect("product_add")
        if not stock:
            messages.error(request, "Please enter the stock.")
            return redirect("product_add")

        if not description:
            messages.error(request, "Please enter the description.")
            return redirect("product_add")

        if not image:
            messages.error(request, "Please upload a product image.")
            return redirect("product_add")

        if not brand:
            messages.error(request, "Please select a brand.")
            return redirect("product_add")

        if not color:
            messages.error(request, "Please select a color.")
            return redirect("product_add")

        if not storage:
            messages.error(request, "Please select storage.")
            return redirect("product_add")

        if Product.objects.filter(name__iexact=name).exists():
            messages.error(request, "Product already exists.")
            return redirect("product_add")

        brand = get_object_or_404(Brand, id=brand)
        color = get_object_or_404(Color, id=color)
        storage = get_object_or_404(Storage, id=storage)

        Product.objects.create(
            name=name,
            price=price,
            stock=stock,
            description=description,
            image=image,
            brand=brand,
            color=color,
            storage=storage,
        )

        messages.success(request, "Product added successfully.")
        return redirect("product_dashboard")

    return render(request, "main/product_add.html", {
        "brands": brands,
        "colors": colors,
        "storages": storages
    })


# @login_required
# def add_to_wishlist(request, product_id):

#     product = get_object_or_404(Product, id=product_id)

#     wishlist_item, created = Wishlist.objects.get_or_create(
#         user=request.user,
#         product=product
#     )

#     return redirect(request.META.get('HTTP_REFERER', 'home'))


# @login_required
# def remove_from_wishlist(request, product_id):

#     product = get_object_or_404(Product, id=product_id)

#     Wishlist.objects.filter(
#         user=request.user,
#         product=product
#     ).delete()

#     return redirect(request.META.get('HTTP_REFERER', 'home'))


# @login_required
# def wishlist(request):

#     wishlist_items = Wishlist.objects.filter(
#         user=request.user
#     ).select_related('product')

#     return render(request, 'user/wishlist.html', {
#         'wishlist_items': wishlist_items
#     })

def brand_add(request):
    if request.method == "POST":
        name = request.POST.get("name")
        logo = request.FILES.get("logo")

        if not name:
            messages.error(request, "Please enter a brand name.")
            return redirect("brand_add")

        if not logo:
            messages.error(request, "Please upload a brand logo.")
            return redirect("brand_add")

        if Brand.objects.filter(name__iexact=name).exists():
            messages.error(request, "Brand already exists.")
            return redirect("brand_add")

        Brand.objects.create(
            name=name,
            logo=logo
        )

        messages.success(request, "Brand added successfully.")
        return redirect("brand_page")

    return render(request, "main/brand_add.html")

# @login_required
# def toggle_wishlist(request, product_id):

#     product = get_object_or_404(Product, id=product_id)

#     wishlist_item = Wishlist.objects.filter(
#         user=request.user,
#         product=product
#     ).first()

#     if wishlist_item:
#         wishlist_item.delete()

#         return JsonResponse({
#             'status': 'removed',
#             'message': 'Removed from wishlist'
#         })

#     Wishlist.objects.create(
#         user=request.user,
#         product=product
#     )

#     return JsonResponse({
#         'status': 'added',
#         'message': 'Added to wishlist'
#     })


# @login_required
# def wishlist(request):

#     wishlist_items = Wishlist.objects.filter(
#         user=request.user
#     ).select_related('product')

#     return render(request, 'user/wishlist.html', {
#         'wishlist_items': wishlist_items
#     })

def color_add(request):
    if request.method == "POST":
        color = request.POST.get("color")
        color_code = request.POST.get("code")

        if not color:
            messages.error(request, "Please enter a color.")
            return redirect("color_add")

        if not color_code:
            messages.error(request, "Please enter the color code.")
            return redirect("color_add")

        Color.objects.create(
            color=color,
            color_code=color_code
        )

        messages.success(request, "Color added successfully.")
        return redirect("color_page")

    return render(request, "main/color_add.html")



def storage_add(request):
    if request.method == "POST":
        size = request.POST.get("size")

        if not size:
            messages.error(request, "Please enter storage size.")
            return redirect("storage_add")

        Storage.objects.create(
            size=size
        )

        messages.success(request, "Storage added successfully.")
        return redirect("storage_page")

    return render(request, "main/storage_add.html")


@staff_required
def brand_page(request):
    brands = Brand.objects.all()
    return render(request, "main/brand_page.html", {
        "brands": brands
    })


@staff_required
def color_page(request):
    colors = Color.objects.all()
    return render(request, "main/color_page.html", {
        "colors": colors
    })

@staff_required
def storage_page(request):
    storages = Storage.objects.all()
    return render(request, "main/storage_page.html", {
        "storages": storages
    })



def product_edit(request, id):
    product = get_object_or_404(Product, id=id)


    brands = Brand.objects.all()
    colors = Color.objects.all()
    storages = Storage.objects.all()

    if request.method == "POST":
        product.name = request.POST.get("name")
        product.price = request.POST.get("price")
        product.stock = request.POST.get("stock")
        product.description = request.POST.get("description")

        brand = request.POST.get("brand")
        color = request.POST.get("color")
        storage = request.POST.get("storage")

        if brand:
            product.brand = get_object_or_404(Brand, id=brand)
        
        if color:
            product.color = get_object_or_404(Color, id=color)

        if storage:
            product.storage = get_object_or_404(Storage, id=storage)

        image = request.FILES.get("photo")
        if image:
            product.image = image

        product.save()

        messages.success(request, "Product updated successfully.")
        return redirect("product_dashboard")

    return render(request, "main/product_edit.html", {
        "product": product,
        "brands": brands,
        "colors": colors,
        "storages": storages,
    })
    
def product_delete(request, id):
    product = get_object_or_404(Product, id=id)
    product.delete()
    messages.success(request, "Product deleted successfully.")
    return redirect("product_dashboard")


def brand_edit(request, id):
    brand = get_object_or_404(Brand, id=id)

    if request.method == "POST":
        brand.name = request.POST.get("name")

        logo = request.FILES.get("logo")
        print("Uploaded logo:", logo)

        if logo:
            brand.logo = logo

        brand.save()

        messages.success(request, "Brand updated successfully.")
        return redirect("brand_page")

    return render(request, "main/brand_edit.html", {
        "brand": brand
    })


def brand_delete(request, id):
    brand = get_object_or_404(Brand, id=id)
    brand.delete()
    messages.success(request, "Brand deleted successfully.")
    return redirect("brand_page")



def color_edit(request, id):
    color = get_object_or_404(Color, id=id)

    if request.method == "POST":
        color_name = request.POST.get("color")
        color_code = request.POST.get("code")

        if not color_name:
            messages.error(request, "Please enter a color name.")
            return redirect("color_edit", id=id)

        if not color_code:
            messages.error(request, "Please enter a color code.")
            return redirect("color_edit", id=id)

        if Color.objects.filter(color__iexact=color_name).exclude(id=id).exists():
            messages.error(request, "Color already exists.")
            return redirect("color_edit", id=id)

        color.color = color_name
        color.color_code = color_code
        color.save()

        messages.success(request, "Color updated successfully.")
        return redirect("color_page")

    return render(request, "main/color_edit.html", {
        "color": color
    })
   


def color_delete(request, id):
    color = get_object_or_404(Color, id=id)
    color.delete()
    messages.success(request, "Color deleted successfully.")
    return redirect("color_page")



def storage_edit(request, id):
    storage = get_object_or_404(Storage, id=id)


    if request.method == "POST":
        size = request.POST.get("size")

        if not size:
            messages.error(request, "Please enter storage size.")
            return redirect("storage_edit", id=id)

        if Storage.objects.filter(size__iexact=size).exclude(id=id).exists():
            messages.error(request, "Storage already exists.")
            return redirect("storage_edit", id=id)

        storage.size = size
        storage.save()

        messages.success(request, "Storage updated successfully.")
        return redirect("storage_page")

    return render(request, "main/storage_edit.html", {
        "storage": storage
    })
  



def storage_delete(request, id):
    storage = get_object_or_404(Storage, id=id)
    storage.delete()
    messages.success(request, "Storage deleted successfully.")
    return redirect("storage_page")

@staff_required
def user_details(request):
    users = User.objects.filter(
        is_superuser=False
    ).order_by("-date_joined")

    return render(request, "main/user_details.html", {
        "users": users
    })

def user_edit(request, id):
    user = get_object_or_404(User, id=id)

    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")

        

        if not username:
            messages.error(request, "Please enter username.")
            return redirect("user_edit", id=id)

        if not email:
            messages.error(request, "Please enter email.")
            return redirect("user_edit", id=id)

        if User.objects.filter(
            username__iexact=username
        ).exclude(id=id).exists():

            messages.error(request, "Username already exists.")
            return redirect("user_edit", id=id)

        user.username = username
        user.email = email
        user.save()

        messages.success(request, "User updated successfully.")
        return redirect("user_details")

    return render(request, "main/user_edit.html", {
        "user": user
    })


def user_delete(request, id):
    user = get_object_or_404(User, id=id)

    user.delete()

    messages.success(request, "User deleted successfully.")
    return redirect("user_details")

