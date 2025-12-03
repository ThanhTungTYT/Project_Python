from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('', views.get_index, name='index'),
    path('catalog/', views.get_catalog, name='catalog'),
    path('cart/', views.get_cart, name='cart'),
    path('payment/', views.get_payment, name='payment'),
    path('login/', views.get_login, name='login'),
    path('register/', views.get_register, name='register'),
    path('about/', views.get_about, name='aboutUs'),
    path('account/', views.get_account, name='account'),
    path('info/', views.get_info, name='info'),
    path('changepw/', views.get_changepw, name='changepw'),
    path('history/', views.get_history, name='history'),
    path('logout/', views.get_logout, name='logout'),
    path('product/<int:product_id>/', views.get_product, name='product'),
    path('add_to_cart/', views.add_to_cart, name='add_to_cart'),
]
