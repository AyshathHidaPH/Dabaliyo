from django.contrib import admin
from .models import Product, Brand, Color, Storage
# Register your models here.
admin.site.register(Product)
admin.site.register(Brand)
admin.site.register(Color)
admin.site.register(Storage)