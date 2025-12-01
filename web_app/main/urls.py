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
]
