from django.urls import path
from . import views

urlpatterns = [
    path("", views.cart, name="cart"),
    path("add_to_cart/<int:product_id>/", views.add_to_cart, name="add_to_cart"),
    path("remove_from_cart/<int:product_id>/", views.remove_from_cart, name="remove_from_cart"),
    path("update_cart/<int:id>/",views.update_cart, name="update_cart"),
    path("wishlist/",views.wishlist, name="wishlist"),
    path("add_to_wishlist/<int:product_id>/", views.add_to_wishlist, name="add_to_wishlist"),
    path("remove_from_wishlist/<int:product_id>/", views.remove_from_wishlist, name="remove_from_wishlist"),
    path("toggle_wishlist/<int:product_id>/",views.toggle_wishlist,name="toggle_wishlist"),
    path("buy_now/<int:product_id>/",views.buy_now, name='buy_now'),
    path("checkout/", views.checkout,name="checkout"),
]