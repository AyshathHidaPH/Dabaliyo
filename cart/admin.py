from django.contrib import admin
from.models import Wishlist, Cart, CartItem

# Register your models here.
admin.site.register(Wishlist)
admin.site.register(Cart)
admin.site.register(CartItem)