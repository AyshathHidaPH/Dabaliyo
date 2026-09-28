from django.urls import path
from . import views

urlpatterns =[
    path("",views.home, name='home'),
    path("productpage/",views.productpage, name='productpage'),
    path("contact/", views.contact, name="contact"),
    path("productdescription/<int:id>", views.productdescription, name='productdescription'),
    path("login/", views.login, name='login'),
    path("logout/", views.logout, name="logout"),
    path("edit_profile/", views.edit_profile, name="edit_profile"),
    path("register/", views.register, name='register'),
    path("admin_panel/", views.admin_panel, name='admin_panel'),
    path("dashboard/",views.dashboard,name='dashboard'),
    path("edit_profile/",views.dashboard, name='edit_profile'),
]