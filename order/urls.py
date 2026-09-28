from django.urls import path
from . import views


urlpatterns = [
    path("place_order/",views.place_order,name="place_order"),
    path("order_success/<int:order_id>/",views.order_success,name="order_success"),
    path("select_address/",views.select_address,name="select_address"),
    path("add_address/",views.add_address, name="add_address"),
    path("edit_address/<int:address_id>/",views.edit_address,name="edit_address"),
    path("delete_address/<int:address_id>/",views.delete_address,name="delete_address"),
    path("confirm_order/",views.confirm_order,name="confirm_order"),
    path("my_orders/",views.my_orders,name="my_orders"),
    path("user_order_detail/<int:order_id>/",views.user_order_detail,name="user_order_detail"),
    path("order_details/<int:order_id>/",views.order_details,name="order_details"),
    path("admin_orders/",views.admin_orders,name="admin_orders"),
    path("admin_order_detail/<int:order_id>/",views.admin_order_detail,name="admin_order_detail"),
    path("update_order_status/<int:order_id>/update_order_status/",views.update_order_status,name="update_order_status"),
    path("cancel_order/<int:order_id>/",views.cancel_order,name="cancel_order"),
    # path("admin_dashboard/",views.admin_dashboard,name="admin_dashboard"),



]