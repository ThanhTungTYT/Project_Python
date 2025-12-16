from django.contrib import admin
from django.urls import path
from . import views
from .views import order_views

urlpatterns = [
    path('', views.get_index, name='index'),
    path('catalog/', views.get_catalog, name='catalog'),
    path('cart/', views.get_cart, name='cart'),
    path('payment/', views.get_payment, name='payment'),
    path('login/', views.get_login, name='login'),
    path('forgotpassword/', views.get_forgotpassword, name='forgotpassword'),
    path('register/', views.get_register, name='register'),
    path('about/', views.get_about, name='aboutUs'),
    path('account/', views.get_account, name='account'),
    path('info/', views.get_info, name='info'),
    path('changepw/', views.get_changepw, name='changepw'),
    path('history/', views.get_history, name='history'),
    path('logout/', views.get_logout, name='logout'),
    path('product/<int:product_id>/', views.get_product, name='product'),
    path('add_to_cart/', views.add_to_cart, name='add_to_cart'),
    path('shippingPolicies/', views.get_shippingPolicies, name='shippingPolicies'),
    path('termOfUse/', views.get_termOfUse, name='termOfUse'),
    path('warrantyPolicies/', views.get_warrantyPolicies, name='warrantyPolicies'),
    path('help/', views.get_help, name='help'),
    path('adminPage1/', views.get_adminPage1, name='adminPage1'),
    path('adminPage2/', views.get_adminPage2, name='adminPage2'),
    path('adminPage3/', views.get_adminPage3, name='adminPage3'),
    path('adminPage4/', views.get_adminPage4, name='adminPage4'),
    path('adminPage5/', views.get_adminPage5, name='adminPage5'),
    path('adminPage6/', views.get_adminPage6, name='adminPage6'),
    path('adminPage7/', views.get_adminPage7, name='adminPage7'),
    path('adminPage8/', views.get_adminPage8, name='adminPage8'),
    path('cart/prepare/', order_views.prepare_checkout, name='prepare_checkout'),
    path('checkout/', order_views.checkout_view, name='checkout'),
    path('process/', order_views.process_checkout, name='process_checkout'),
    path('remove_cart_item/', views.remove_cart_item, name='remove_cart_item'),
    path('remove_all_cart_items/', views.remove_all_cart_items, name='remove_all_cart_items'),
]
