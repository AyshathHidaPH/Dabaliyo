from django.urls import path
from . import views


urlpatterns = [
        path("",views.product_dashboard,name='product_dashboard'),
        path("product_add/",views.product_add,name='product_add'),
        path("brand_add/",views.brand_add,name='brand_add'),
        path("color_add",views.color_add,name='color_add'),
        path("storage_add/",views.storage_add,name='storage_add'),
        path("brand_page/",views.brand_page,name='brand_page'),
        path("color_page/",views.color_page,name='color_page'),
        path("storage_page/",views.storage_page,name='storage_page'),
        path("product_edit/<int:id>/",views.product_edit,name='product_edit'),
        path("product_delete/<int:id>/",views.product_delete,name='product_delete'),
        path("brand_edit/<int:id>/",views.brand_edit,name='brand_edit'),
        path("brand_delete/<int:id>/",views.brand_delete,name='brand_delete'),
        path("color_edit/<int:id>/",views.color_edit,name='color_edit'),
        path("color_delete/<int:id>/",views.color_delete,name='color_delete'),
        path("storage_edit/<int:id>/",views.storage_edit,name='storage_edit'),
        path("storage_delete/<int:id>/",views.storage_delete,name='storage_delete'),
        path("user_details/",views.user_details, name="user_details"),
        path("user_edit/<int:id>/",views.user_edit, name="user_edit"),
        path("user_delete/<int:id>/",views.user_delete, name="user_delete"),
        
]