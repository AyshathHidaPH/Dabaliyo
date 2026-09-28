from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
import json
from products.models import Product
from .models import Cart, CartItem, Wishlist
from decimal import Decimal
from order.models import Address
from django.contrib.auth.decorators import login_required



@login_required
def add_to_cart(request, product_id):

    product = get_object_or_404(
        Product,
        id=product_id
    )

    # -----------------------------------------
    # GET QUANTITY
    # -----------------------------------------

    try:
        quantity = int(
            request.POST.get("quantity", 1)
        )
    except (TypeError, ValueError):
        quantity = 1


    # -----------------------------------------
    # CHECK QUANTITY
    # -----------------------------------------

    if quantity < 1:
        quantity = 1


    # Product out of stock
    if product.stock <= 0:

        if request.headers.get("X-Requested-With") == "XMLHttpRequest":

            return JsonResponse({
                "success": False,
                "message": "This product is out of stock."
            }, status=400)

        return redirect("cart")


    # Don't allow more than stock
    if quantity > product.stock:
        quantity = product.stock


    # -----------------------------------------
    # GET USER CART
    # -----------------------------------------

    cart, created = Cart.objects.get_or_create(
        user=request.user
    )


    # -----------------------------------------
    # GET OR CREATE CART ITEM
    # -----------------------------------------

    cart_item, item_created = CartItem.objects.get_or_create(
        cart=cart,
        product=product
    )


    if item_created:

        cart_item.quantity = quantity

    else:

        cart_item.quantity += quantity

        # Don't exceed available stock
        if cart_item.quantity > product.stock:

            cart_item.quantity = product.stock


    cart_item.save()


    # -----------------------------------------
    # TOTAL CART QUANTITY
    # -----------------------------------------

    cart_count = sum(
        item.quantity
        for item in cart.items.all()
    )


    # -----------------------------------------
    # AJAX RESPONSE
    # -----------------------------------------

    if request.headers.get("X-Requested-With") == "XMLHttpRequest":

        return JsonResponse({

            "success": True,

            "message": f"{product.name} added to cart successfully.",

            "cart_count": cart_count,

            "product_id": product.id

        })


    # -----------------------------------------
    # NORMAL REQUEST
    # -----------------------------------------

    return redirect("cart")

# @login_required
# def checkout(request):

#     cart_obj, created = Cart.objects.get_or_create(
#         user=request.user
#     )

#     cart_items = CartItem.objects.filter(
#         cart=cart_obj
#     ).select_related("product")

#     if not cart_items.exists():
#         messages.error(
#             request,
#             "Your cart is empty."
#         )
#         return redirect("cart")

#     subtotal = 0

#     for item in cart_items:
#         item.total = item.product.price * item.quantity
#         subtotal += item.total

#     shipping = 50 if subtotal > 0 else 0
#     grand_total = subtotal + shipping

#     return render(
#         request,
#         "cart/checkout.html",
#         {
#             "cart": cart_obj,
#             "cart_items": cart_items,
#             "subtotal": subtotal,
#             "shipping": shipping,
#             "grand_total": grand_total,
#         }
#     )
@login_required
def checkout(request):

    cart = get_object_or_404(
        Cart,
        user=request.user
    )

    cart_items = cart.items.select_related("product")

    subtotal = sum(
        (
            item.product.discount_price
            if item.product.discount_price
            else item.product.price
        ) * item.quantity
        for item in cart_items
    )

    shipping = 0 if subtotal >= 1000 else 50

    grand_total = subtotal + shipping

    # Get user's saved addresses
    addresses = Address.objects.filter(
        user=request.user
    ).order_by("-is_default", "-id")

    context = {
        "cart_items": cart_items,
        "subtotal": subtotal,
        "shipping": shipping,
        "grand_total": grand_total,
        "addresses": addresses,
    }

    return render(
        request,
        "user/checkout.html",
        context
    )
        


# @login_required
# def place_order(request):

#     if request.method != "POST":
#         return redirect("checkout")

#     cart_obj = get_object_or_404(
#         Cart,
#         user=request.user
#     )

#     cart_items = CartItem.objects.filter(
#         cart=cart_obj
#     ).select_related("product")

#     if not cart_items.exists():
#         messages.error(
#             request,
#             "Your cart is empty."
#         )
#         return redirect("cart")

#     # Get shipping details
#     name = request.POST.get("name")
#     phone = request.POST.get("phone")
#     email = request.POST.get("email")
#     address = request.POST.get("address")
#     city = request.POST.get("city")
#     state = request.POST.get("state")
#     pincode = request.POST.get("pincode")

#     # Check required fields
#     if not all([
#         name,
#         phone,
#         email,
#         address,
#         city,
#         state,
#         pincode
#     ]):
#         messages.error(
#             request,
#             "Please fill in all shipping details."
#         )
#         return redirect("checkout")

#     # Check stock
#     for item in cart_items:

#         if item.quantity > item.product.stock:

#             messages.error(
#                 request,
#                 f"Only {item.product.stock} "
#                 f"of {item.product.name} are available."
#             )

#             return redirect("checkout")

#     # Calculate total
#     subtotal = 0

#     for item in cart_items:
#         subtotal += (
#             item.product.price *
#             item.quantity
#         )

#     shipping = 50 if subtotal > 0 else 0
#     grand_total = subtotal + shipping

#     # Reduce stock
#     for item in cart_items:

#         item.product.stock -= item.quantity

#         item.product.save(
#             update_fields=["stock"]
#         )

#     # Save shipping details in session
#     request.session["shipping_details"] = {
#         "name": name,
#         "phone": phone,
#         "email": email,
#         "address": address,
#         "city": city,
#         "state": state,
#         "pincode": pincode,
#         "subtotal": subtotal,
#         "shipping": shipping,
#         "grand_total": grand_total,
#     }

#     # Clear cart
#     cart_items.delete()

#     messages.success(
#         request,
#         "Your order has been placed successfully!"
#     )

#     return redirect("order_success")

@login_required
def buy_now(request, product_id):

    product = get_object_or_404(
        Product,
        id=product_id
    )

    # Get quantity
    quantity = int(
        request.POST.get("quantity", 1)
    )

    # Minimum quantity
    if quantity < 1:
        quantity = 1

    # Don't exceed stock
    if quantity > product.stock:
        quantity = product.stock

    # Get user's cart
    cart, created = Cart.objects.get_or_create(
        user=request.user
    )

    # Get or create cart item
    cart_item, created = CartItem.objects.get_or_create(
        cart=cart,
        product=product
    )

    if created:

        cart_item.quantity = quantity

    else:

        cart_item.quantity += quantity

        if cart_item.quantity > product.stock:
            cart_item.quantity = product.stock

    cart_item.save()

    # Go directly to checkout
    return redirect("checkout")


from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404

@login_required
def add_to_wishlist(request, product_id):

    product = get_object_or_404(Product, id=product_id)

    wishlist, created = Wishlist.objects.get_or_create(
        user=request.user,
        product=product
    )

    return JsonResponse({
        "success": True,
        "added": True
    })


@login_required
def remove_from_wishlist(request, product_id):

    Wishlist.objects.filter(
        user=request.user,
        product_id=product_id
    ).delete()

    return JsonResponse({
        "success": True,
        "added": False
    })

@login_required
def toggle_wishlist(request, product_id):

    product = get_object_or_404(Product, id=product_id)

    wishlist_item = Wishlist.objects.filter(
        user=request.user,
        product=product
    ).first()

    if wishlist_item:
        wishlist_item.delete()

        return JsonResponse({
            "success": True,
            "added": False,
        })

    Wishlist.objects.create(
        user=request.user,
        product=product
    )

    return JsonResponse({
        "success": True,
        "added": True,
    })

@login_required
def cart(request):

    cart_obj, created = Cart.objects.get_or_create(
        user=request.user
    )

    cart_items = CartItem.objects.filter(
        cart=cart_obj
    ).select_related("product")

    # Calculate individual item totals
    subtotal = 0

    for item in cart_items:
        item.total = item.product.price * item.quantity
        subtotal += item.total

    # Shipping
    shipping = 50 if subtotal > 0 else 0

    # Grand total
    grand_total = subtotal + shipping

    # Total number of products
    cart_count = sum(
        item.quantity for item in cart_items
    )

    return render(request, "user/cart.html", {
        "cart": cart_obj,
        "cart_items": cart_items,

        "cart_count": cart_count,

        "subtotal": subtotal,
        "shipping": shipping,
        "grand_total": grand_total,
    })


@login_required
def wishlist(request):
    wishlist_items = Wishlist.objects.filter(
        user=request.user
    ).select_related("product")

    return render(request, "user/wishlist.html", {
        "wishlist_items": wishlist_items
    })



@login_required
def remove_from_cart(request, product_id):

    cart_obj = get_object_or_404(
        Cart,
        user=request.user
    )

    cart_item = get_object_or_404(
        CartItem,
        cart=cart_obj,
        product_id=product_id
    )

    cart_item.delete()

    messages.success(
        request,
        "Product removed from cart!"
    )

    return redirect("cart")



@login_required
def update_cart(request, id):

    if request.method != "POST":
        return JsonResponse({
            "success": False,
            "message": "Invalid request method."
        }, status=400)

    cart_obj = get_object_or_404(
        Cart,
        user=request.user
    )

    cart_item = get_object_or_404(
        CartItem,
        id=id,
        cart=cart_obj
    )

    try:

        # JavaScript sends JSON
        data = json.loads(
            request.body
        )

        quantity = int(
            data.get("quantity", 1)
        )

    except (ValueError, TypeError, json.JSONDecodeError):

        return JsonResponse({
            "success": False,
            "message": "Invalid quantity."
        }, status=400)

    # Minimum quantity = 1
    if quantity < 1:
        quantity = 1

    cart_item.quantity = quantity
    cart_item.save()


    cart_items = CartItem.objects.filter(
        cart=cart_obj
    ).select_related("product")

    subtotal = 0

    for item in cart_items:
        subtotal += (
            item.product.price *
            item.quantity
        )

    shipping = 50 if subtotal > 0 else 0

    grand_total = subtotal + shipping

    cart_count = sum(
        item.quantity
        for item in cart_items
    )

    # Current item's total
    item_total = (
        cart_item.product.price *
        cart_item.quantity
    )

    return JsonResponse({
        "success": True,

        "quantity": cart_item.quantity,

        "item_total": str(item_total),

        "subtotal": str(subtotal),

        "shipping": str(shipping),

        "grand_total": str(grand_total),

        "cart_count": cart_count,
    })


@login_required
def order_success(request):

    shipping_details = request.session.get("shipping_details", {})

    return render(
        request,
        "user/order_success.html",
        {
            "shipping_details": shipping_details,
        }
    )

# @login_required
# def add_to_wishlist(request, product_id):

#     product = get_object_or_404(
#         Product,
#         id=product_id
#     )

#     wishlist_item, created = Wishlist.objects.get_or_create(
#         user=request.user,
#         product=product
#     )

#     if created:
#         messages.success(
#             request,
#             "Added to wishlist!"
#         )
#     else:
#         messages.info(
#             request,
#             "Product is already in wishlist."
#         )

#     return redirect(
#         request.META.get(
#             "HTTP_REFERER",
#             "home"
#         )
#     )



